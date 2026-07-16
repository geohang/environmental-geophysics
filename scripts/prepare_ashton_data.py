"""Audit Ashton Prairie field files and build browser-ready teaching products.

The source directory is never modified. Published map products distinguish
real acquisition lines from derived geophysical products through explicit
``data_class`` and quality fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import ConvexHull, cKDTree


OFFICIAL_SITE = "https://sees.uiowa.edu/research/ashton-prairie"
PACKAGE_REPOSITORY = "https://github.com/geohang/PyHydroGeophysX"
DATA_EXTENSIONS = {".csv", ".dat", ".kml", ".sgy", ".txt", ".xlsx"}
NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
PUBLIC_ERT_DATASETS = {
    "2026-04-11/ert/inversion_2026-04-11_Wenner_48elec_2m_flat_positive_only_pygimli.txt",
    "2026-05-02/ert/inversion_2026-05-02_May2_dipole_dipole_positive_only_pygimli.txt",
}
EM_SOURCE_FILES = {
    *{f"2026-05-02/em/location_line {number}.txt" for number in range(1, 10)},
    "2026-05-02/em/location_Line_information.txt",
    "2026-05-02/em/processed_22-xg-12se-294_gem_averaged_inverted.csv",
    "2026-05-02/em/processed_22-xg-12se-294_gem_averaged_processed.csv",
    "2026-05-02/em/processed_All_Lines_Corr_EM.xlsx",
    "2026-05-02/em/processed_corr.csv",
    "2026-05-02/em/processed_valid_inversion.csv",
    "2026-05-02/em/raw_22-xg-12se-294_gem_averaged_original_copy.csv",
}
PUBLIC_EXCLUSIONS = {
    # Subset KML files duplicate the consolidated all-date KML.
    "2026-04-11/2026-04-11_locations.kml",
    "2026-04-11/ert/2026-04-11_ERT_48electrodes_2m_interpolated_extrapolated.kml",
    "2026-04-11/seismic/2026-04-11_seismic_GPS_points.kml",
    "2026-05-02/2026-05-02_locations.kml",
    "2026-06-25/2026-06-25_locations.kml",
    "2026-06-25/ert/2026-06-25_ERT_electrodes_267-314.kml",
    # The master survey table already contains these WGS84 source positions.
    "2026-04-11/seismic/location_2026-04-11_seismic_GPS_points.csv",
    # EM files are republished under stable, role-based names in organized/em.
    # The averaged processed table remains the canonical I/Q input; only its
    # confusing source filename is removed from the raw download tree.
    *EM_SOURCE_FILES,
    # The CSV pick tables retain more metadata than these PyGIMLi text mirrors.
    "2026-05-02/seismic/1000_output_picks.txt",
    "2026-05-02/seismic/2000_output_picks.txt",
}


def sha256(path: Path) -> str:
    """Return the SHA-256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    """Summarize finite numeric values in a JSON-friendly dictionary."""

    array = np.asarray(list(values), dtype=float)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {"count": 0, "minimum": None, "median": None, "maximum": None}
    return {
        "count": int(finite.size),
        "minimum": float(np.min(finite)),
        "median": float(np.median(finite)),
        "maximum": float(np.max(finite)),
    }


def parse_syscal_export(path: Path) -> pd.DataFrame:
    """Parse whitespace Syscal exports whose array name contains spaces."""

    records: list[list[float]] = []
    arrays: list[str] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[1:]:
        matches = list(NUMBER_RE.finditer(line))
        if len(matches) < 10:
            continue
        values = [float(match.group()) for match in matches[-10:]]
        records.append(values)
        arrays.append(line[: matches[-10].start()].strip())
    columns = ["a", "b", "m", "n", "rho_ohm_m", "dev_percent", "ip", "sp", "vp", "current"]
    frame = pd.DataFrame(records, columns=columns)
    frame.insert(0, "array", arrays)
    return frame


def parse_res2dinv_export(path: Path) -> pd.DataFrame:
    """Parse general-array Res2DInv rows into ABMN geometry and resistance."""

    records: list[list[float]] = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        values = [float(value) for value in NUMBER_RE.findall(line)]
        if len(values) == 10 and int(values[0]) == 4:
            records.append(values)
    columns = ["type", "a", "ya", "b", "yb", "m", "ym", "n", "yn", "resistance_ohm"]
    return pd.DataFrame(records, columns=columns)


def audit_kml(path: Path) -> dict[str, Any]:
    """Parse KML geometry counts and coordinate bounds."""

    root = ET.parse(path).getroot()
    namespace = {"k": "http://www.opengis.net/kml/2.2"}
    geometry_counts = {
        name: len(root.findall(f".//k:{name}", namespace))
        for name in ("Point", "LineString", "Polygon")
    }
    coordinates: list[tuple[float, float, float | None]] = []
    for node in root.findall(".//k:coordinates", namespace):
        for token in (node.text or "").split():
            parts = token.split(",")
            if len(parts) >= 2:
                coordinates.append(
                    (float(parts[0]), float(parts[1]), float(parts[2]) if len(parts) > 2 else None)
                )
    return {
        "geometry_counts": geometry_counts,
        "coordinate_count": len(coordinates),
        "longitude": finite_summary(item[0] for item in coordinates),
        "latitude": finite_summary(item[1] for item in coordinates),
        "zero_elevations": sum(item[2] == 0 for item in coordinates if item[2] is not None),
    }


def audit_seismic(path: Path) -> dict[str, Any]:
    """Read DAT or SEG-Y using the PyHydroGeophysX public API."""

    from PyHydroGeophysX.data_processing import read_geometrics_dat, read_segy

    dataset = read_geometrics_dat(str(path)) if path.suffix.lower() == ".dat" else read_segy(str(path))
    traces = np.asarray(dataset.traces)
    zero_traces = int(np.all(traces == 0, axis=0).sum()) if traces.size else 0
    metrics: dict[str, Any] = {
        "shape_samples_by_traces": [int(value) for value in traces.shape],
        "sample_interval_us": int(dataset.metadata.sample_interval_us),
        "field_records": [int(value) for value in dataset.field_records],
        "finite_fraction": float(np.isfinite(traces).mean()) if traces.size else None,
        "zero_trace_count": zero_traces,
        "amplitude": finite_summary(traces.ravel()),
    }
    if path.suffix.lower() == ".sgy":
        picks_path = path.with_name(f"{path.stem}_first_break_picks.csv")
        if picks_path.exists():
            picks = pd.read_csv(picks_path)
            sample_indices = np.rint(
                picks["time_s"].to_numpy(float) / (dataset.metadata.sample_interval_us * 1e-6)
            ).astype(int)
            trace_indices = picks["trace_index"].to_numpy(int)
            valid = (
                (sample_indices >= 0)
                & (sample_indices < traces.shape[0])
                & (trace_indices >= 0)
                & (trace_indices < traces.shape[1])
            )
            sampled = traces[sample_indices[valid], trace_indices[valid]]
            reported = picks.loc[valid, "amplitude"].to_numpy(float)
            metrics["first_break_rows"] = int(len(picks))
            metrics["first_break_index_valid"] = int(valid.sum())
            metrics["first_break_amplitude_max_abs_difference"] = float(
                np.max(np.abs(sampled - reported)) if sampled.size else math.nan
            )
    return metrics


def audit_pygimli_ert(path: Path) -> dict[str, Any]:
    """Load a PyGIMLi-format ERT container without leaving sidecar files."""

    from pygimli.physics import ert

    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="ashton_pygimli_") as temporary:
        try:
            os.chdir(temporary)
            container = ert.load(str(path.resolve()))
        finally:
            os.chdir(original_cwd)
    tokens = str(container.tokenList()).split()
    metrics: dict[str, Any] = {
        "format": "PyGIMLi DataContainerERT",
        "sensors": int(container.sensorCount()),
        "rows_after_validity_check": int(container.size()),
        "tokens": tokens,
    }
    for token in ("rhoa", "r", "err", "valid"):
        if container.haveData(token):
            values = np.asarray(container[token], dtype=float)
            metrics[token] = finite_summary(values)
            metrics[f"{token}_nonpositive"] = int((values <= 0).sum())
    return metrics


def audit_output_picks(path: Path) -> dict[str, Any]:
    """Parse a PyGIMLi seismic travel-time data container."""

    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()]
    sensor_count = int(lines[0])
    sensor_rows = [line for line in lines[2 : 2 + sensor_count] if line and not line.startswith("#")]
    cursor = 2 + sensor_count
    while cursor < len(lines) and not lines[cursor]:
        cursor += 1
    declared_rows = int(lines[cursor])
    cursor += 1
    while cursor < len(lines) and (not lines[cursor] or lines[cursor].startswith("#")):
        cursor += 1
    data_rows = []
    for line in lines[cursor:]:
        values = NUMBER_RE.findall(line)
        if len(values) >= 3:
            data_rows.append([float(value) for value in values[:3]])
    frame = pd.DataFrame(data_rows, columns=["source", "geophone", "time_s"])
    return {
        "format": "PyGIMLi travel-time container",
        "declared_sensors": sensor_count,
        "parsed_sensor_rows": len(sensor_rows),
        "declared_data_rows": declared_rows,
        "parsed_data_rows": int(len(frame)),
        "positive_travel_times": int((frame["time_s"] > 0).sum()),
        "travel_time_s": finite_summary(frame["time_s"]),
    }


def audit_file(path: Path, root: Path) -> dict[str, Any]:
    """Read one source file and return format-specific metrics."""

    relative = path.relative_to(root).as_posix()
    result: dict[str, Any] = {
        "path": relative,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "status": "reviewed",
        "metrics": {},
    }
    try:
        lower_name = path.name.lower()
        if path.suffix.lower() in {".dat", ".sgy"}:
            result["metrics"] = audit_seismic(path)
        elif path.suffix.lower() == ".kml":
            result["metrics"] = audit_kml(path)
        elif path.suffix.lower() == ".xlsx":
            workbook = pd.ExcelFile(path)
            result["metrics"] = {
                "sheets": {
                    sheet: {
                        "rows": int(frame.shape[0]),
                        "columns": int(frame.shape[1]),
                        "missing_cells": int(frame.isna().sum().sum()),
                    }
                    for sheet in workbook.sheet_names
                    for frame in [pd.read_excel(path, sheet_name=sheet)]
                }
            }
        elif "ert_raw_wenner" in lower_name or "ert_raw_may2" in lower_name:
            frame = parse_syscal_export(path)
            result["metrics"] = {
                "format": "Syscal whitespace export",
                "rows": int(len(frame)),
                "positive_resistivity": int((frame["rho_ohm_m"] > 0).sum()),
                "zero_resistivity": int((frame["rho_ohm_m"] == 0).sum()),
                "negative_resistivity": int((frame["rho_ohm_m"] < 0).sum()),
                "deviation_gt_20_percent": int((frame["dev_percent"] > 20).sum()),
                "zero_voltage": int((frame["vp"] == 0).sum()),
                "qc_positive_dev20_nonzero_voltage": int(
                    ((frame["rho_ohm_m"] > 0) & (frame["dev_percent"] <= 20) & (frame["vp"] != 0)).sum()
                ),
            }
        elif "ert_raw_ashton" in lower_name:
            frame = parse_res2dinv_export(path)
            resistance = frame["resistance_ohm"]
            result["metrics"] = {
                "format": "Res2DInv general array resistance",
                "rows": int(len(frame)),
                "positive_resistance": int((resistance > 0).sum()),
                "zero_resistance": int((resistance == 0).sum()),
                "negative_resistance": int((resistance < 0).sum()),
                "resistance_ohm": finite_summary(resistance),
            }
        elif lower_name.startswith("inversion_"):
            result["metrics"] = audit_pygimli_ert(path)
        elif lower_name.endswith("_output_picks.txt"):
            result["metrics"] = audit_output_picks(path)
        elif lower_name.startswith("location_line "):
            frame = pd.read_csv(path)
            result["metrics"] = {
                "format": "EM surveyed line locations",
                "rows": int(len(frame)),
                "zero_elevations": int((frame["Z"] == 0).sum()),
                "duplicate_xyz_rows": int(frame.duplicated(["X", "Y", "Z"]).sum()),
                "x_utm_m": finite_summary(frame["X"]),
                "y_utm_m": finite_summary(frame["Y"]),
                "elevation_m": finite_summary(frame.loc[frame["Z"] > 0, "Z"]),
            }
        elif path.suffix.lower() == ".txt" and (
            lower_name.startswith("location_") or lower_name.endswith("_28pts.txt")
        ):
            frame = pd.read_csv(path, sep=r"\s+")
            result["metrics"] = {
                "format": "survey location table",
                "rows": int(frame.shape[0]),
                "columns": int(frame.shape[1]),
                "column_names": [str(value) for value in frame.columns],
                "missing_cells": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
            }
        elif path.suffix.lower() == ".csv":
            frame = pd.read_csv(path, skipinitialspace=True)
            numeric = frame.select_dtypes(include=[np.number])
            result["metrics"] = {
                "rows": int(frame.shape[0]),
                "columns": int(frame.shape[1]),
                "column_names": [str(value).strip() for value in frame.columns],
                "missing_cells": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
                "nonfinite_numeric_cells": int((~np.isfinite(numeric.to_numpy(float))).sum()) if not numeric.empty else 0,
            }
        else:
            lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            result["metrics"] = {
                "line_count": len(lines),
                "replacement_character_count": sum(line.count("�") for line in lines),
                "nonempty_lines": sum(bool(line.strip()) for line in lines),
            }
    except Exception as exc:  # report each failed source without hiding the rest
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def idw_interpolation(location_frames: list[pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, float]]:
    """Interpolate missing EM elevations from neighboring valid survey points."""

    locations = pd.concat(location_frames, ignore_index=True)
    valid = locations[locations["Z"] > 0].copy()
    missing = locations[locations["Z"] <= 0].copy()
    xy = valid[["X", "Y"]].to_numpy(float)
    z = valid["Z"].to_numpy(float)
    tree = cKDTree(xy)

    def estimate(query: np.ndarray, tree_obj: cKDTree, values: np.ndarray, k: int = 8) -> float:
        distances, indices = tree_obj.query(query, k=min(k, len(values)))
        distances = np.atleast_1d(distances)
        indices = np.atleast_1d(indices)
        weights = 1.0 / np.maximum(distances, 0.5) ** 2
        return float(np.dot(weights, values[indices]) / weights.sum())

    missing["Z_interpolated"] = [estimate(query, tree, z) for query in missing[["X", "Y"]].to_numpy(float)]
    errors: list[float] = []
    for index, query in enumerate(xy):
        reduced_xy = np.delete(xy, index, axis=0)
        reduced_z = np.delete(z, index)
        prediction = estimate(query, cKDTree(reduced_xy), reduced_z)
        errors.append(prediction - z[index])
    error_array = np.asarray(errors)
    metrics = {
        "method": "8-neighbor inverse-distance weighting in EPSG:26915",
        "cross_validation_rmse_m": float(np.sqrt(np.mean(error_array**2))),
        "cross_validation_mae_m": float(np.mean(np.abs(error_array))),
        "cross_validation_abs_error_p95_m": float(np.percentile(np.abs(error_array), 95)),
    }
    return missing, metrics


def geojson_feature(geometry: dict[str, Any], properties: dict[str, Any]) -> dict[str, Any]:
    """Create one RFC 7946 feature."""

    return {"type": "Feature", "geometry": geometry, "properties": properties}


def write_json(path: Path, payload: Any, compact: bool = False) -> None:
    """Write deterministic UTF-8 JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(
            payload,
            stream,
            ensure_ascii=False,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        )
        stream.write("\n")


def build_organized_em_products(root: Path, organized_root: Path) -> list[dict[str, Any]]:
    """Publish EM measurements, per-profile geometry, metadata, and models.

    The five-frequency in-phase/quadrature table is copied without changing its
    columns or values so it remains compatible with existing processing code.
    Sparse acquisition geometry is published as one clearly named file per
    profile. Zero elevation placeholders are replaced with the same audited IDW
    estimates used by the Web GIS and remain explicitly flagged as interpolated.
    """

    source = root / "2026-05-02" / "em"
    em_root = organized_root / "em"
    measurement_dir = em_root / "measurements"
    profile_dir = em_root / "profiles"
    metadata_dir = em_root / "metadata"
    model_dir = em_root / "models"
    for directory in (measurement_dir, profile_dir, metadata_dir, model_dir):
        directory.mkdir(parents=True, exist_ok=True)

    measurement_name = "2026-05-02_gem2_averaged_inphase_quadrature.csv"
    model_name = "2026-05-02_gem2_valid_layered_inversion.csv"
    measurement_source = source / "processed_22-xg-12se-294_gem_averaged_processed.csv"
    model_source = source / "processed_valid_inversion.csv"
    shutil.copyfile(measurement_source, measurement_dir / measurement_name)
    shutil.copyfile(model_source, model_dir / model_name)

    location_frames: list[pd.DataFrame] = []
    for profile_number in range(1, 10):
        path = source / f"location_line {profile_number}.txt"
        frame = pd.read_csv(path)
        frame["profile_number"] = profile_number
        frame["point_number"] = np.arange(1, len(frame) + 1)
        frame["source_file"] = path.name
        location_frames.append(frame)
    missing, interpolation = idw_interpolation(location_frames)
    estimates = {
        (int(row.profile_number), int(row.point_number)): float(row.Z_interpolated)
        for row in missing.itertuples()
    }

    profile_specs: list[dict[str, Any]] = []
    for frame in location_frames:
        profile_number = int(frame["profile_number"].iloc[0])
        profile_id = f"profile_{profile_number:02d}"
        published = pd.DataFrame(
            {
                "profile_id": profile_id,
                "point_id": [f"{profile_id}_point_{value:02d}" for value in frame["point_number"]],
                "x_utm_m": frame["X"].astype(float),
                "y_utm_m": frame["Y"].astype(float),
                "source_elevation_m": frame["Z"].astype(float),
            }
        )
        published["elevation_m"] = [
            estimates.get((profile_number, int(point_number)), float(source_z))
            for point_number, source_z in zip(frame["point_number"], frame["Z"])
        ]
        published["elevation_source"] = np.where(
            published["source_elevation_m"] > 0,
            "provided_in_source",
            "interpolated_8_neighbor_idw",
        )
        published["crs"] = "EPSG:26915"
        published["source_file"] = frame["source_file"].astype(str).to_numpy()
        filename = f"{profile_id}_locations.csv"
        published.to_csv(profile_dir / filename, index=False, float_format="%.6f")
        profile_specs.append(
            {
                "profile_id": profile_id,
                "profile_number": profile_number,
                "location_file": f"profiles/{filename}",
                "location_count": int(len(published)),
                "interpolated_elevation_count": int(
                    (published["elevation_source"] == "interpolated_8_neighbor_idw").sum()
                ),
            }
        )

    mark_starts = [3, 18, 34, 50, 65, 81, 98, 117, 146]
    mark_ranges = pd.DataFrame(
        {
            "profile_id": [f"profile_{number:02d}" for number in range(1, 10)],
            "profile_number": range(1, 10),
            "start_mark_inclusive": mark_starts,
            "end_mark_exclusive": mark_starts[1:] + [np.nan],
        }
    )
    mark_ranges.to_csv(metadata_dir / "profile_mark_ranges.csv", index=False)

    measurement = pd.read_csv(measurement_dir / measurement_name, skipinitialspace=True)
    iq_columns = [column for column in measurement.columns if column.startswith(("I_", "Q_")) and column != "QSum"]
    expected_iq = [
        f"{component}_{frequency}Hz"
        for frequency in (450, 1410, 4350, 13530, 42150)
        for component in ("I", "Q")
    ]
    if iq_columns != expected_iq:
        raise ValueError(f"Unexpected GEM-2 I/Q columns: {iq_columns}")

    manifest = {
        "dataset": "Ashton Prairie GEM-2 frequency-domain EM survey",
        "data_class": "real field data",
        "acquisition_date": "2026-05-02",
        "instrument": "GEM-2 FDEM",
        "coordinate_reference_system": "EPSG:26915",
        "measurement_input": {
            "path": f"measurements/{measurement_name}",
            "rows": int(len(measurement)),
            "role": "canonical processing input",
            "frequencies_hz": [450, 1410, 4350, 13530, 42150],
            "response_components": ["in-phase", "quadrature"],
            "source_columns_preserved": True,
            "note": "Averaged processed observations; not an inversion result.",
        },
        "profile_mapping": {
            "path": "metadata/profile_mark_ranges.csv",
            "rule": "Assign rows where start_mark_inclusive <= Mark < end_mark_exclusive; Mark values below 3 are unassigned setup records.",
            "profiles": profile_specs,
        },
        "derived_model": {
            "path": f"models/{model_name}",
            "rows": int(pd.read_csv(model_dir / model_name, skipinitialspace=True).shape[0]),
            "role": "derived layered inversion result",
            "note": "Do not substitute this model table for the original I/Q observations.",
        },
        "elevation_processing": interpolation,
        "license": "CC BY 4.0",
    }
    write_json(em_root / "manifest.json", manifest)

    products = [
        {
            "path": f"organized/em/measurements/{measurement_name}",
            "filename": measurement_dir / measurement_name,
            "display_name": "May 2 GEM-2 — averaged in-phase and quadrature observations",
            "processing_level": "averaged observations",
            "description": "Canonical processing input with original I/Q responses at five frequencies (24,212 rows).",
            "recommended": True,
            "source_class": "source measurement",
        },
        {
            "path": "organized/em/metadata/profile_mark_ranges.csv",
            "filename": metadata_dir / "profile_mark_ranges.csv",
            "display_name": "May 2 GEM-2 — Profile-to-Mark mapping",
            "processing_level": "acquisition metadata",
            "description": "Maps measurement Mark ranges to Profile 01–09 for profile-aware processing.",
            "recommended": True,
            "source_class": "source metadata",
        },
        {
            "path": "organized/em/manifest.json",
            "filename": em_root / "manifest.json",
            "display_name": "May 2 GEM-2 — organized package manifest",
            "processing_level": "package metadata",
            "description": "Machine-readable roles, paths, frequencies, profile mapping, and elevation provenance.",
            "recommended": True,
            "source_class": "metadata",
        },
        {
            "path": f"organized/em/models/{model_name}",
            "filename": model_dir / model_name,
            "display_name": "May 2 GEM-2 — valid layered inversion",
            "processing_level": "derived inversion model",
            "description": "A 10,538-row derived model supplied for comparison; it is not the measurement input.",
            "recommended": False,
            "source_class": "derived",
        },
    ]
    for spec in profile_specs:
        filename = profile_dir / Path(spec["location_file"]).name
        products.append(
            {
                "path": f"organized/em/{spec['location_file']}",
                "filename": filename,
                "display_name": f"May 2 GEM-2 — Profile {spec['profile_number']:02d} locations",
                "processing_level": "profile geometry",
                "description": (
                    f"{spec['location_count']} ordered UTM locations for Profile {spec['profile_number']:02d}; "
                    f"{spec['interpolated_elevation_count']} interpolated elevations are flagged."
                ),
                "recommended": False,
                "source_class": "quality-controlled geometry",
            }
        )
    return products


def _copy_package_file(source: Path, destination: Path) -> dict[str, Any]:
    """Copy one approved source into a package and return file metadata."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return {
        "path": destination.as_posix(),
        "extension": destination.suffix.lower(),
        "size_bytes": destination.stat().st_size,
        "sha256": sha256(destination),
    }


def _write_package_readme(path: Path, text: str) -> dict[str, Any]:
    """Write a plain-text package guide and return file metadata."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    return {
        "path": path.as_posix(),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def build_data_packages(root: Path, packages_root: Path) -> list[dict[str, Any]]:
    """Build acquisition-unit packages for the approved APLL release."""

    # Overwrite the deterministic package paths in place. Recursive deletion is
    # unreliable in synced OneDrive workspaces where a recently read directory
    # may remain briefly locked by the sync client.
    packages_root.mkdir(parents=True, exist_ok=True)
    packages: list[dict[str, Any]] = []

    def add_package(
        package_id: str,
        method: str,
        date: str,
        display_name: str,
        instrument: str,
        summary: str,
        readme: str,
        copies: list[tuple[Path, str, str]],
    ) -> None:
        package_dir = packages_root / Path(package_id)
        files: list[dict[str, Any]] = []
        for source, relative_destination, role in copies:
            metadata_item = _copy_package_file(source, package_dir / relative_destination)
            metadata_item["role"] = role
            files.append(metadata_item)
        readme_item = _write_package_readme(package_dir / "README.txt", readme)
        readme_item["role"] = "package guide"
        files.insert(0, readme_item)
        packages.append(
            {
                "id": package_id.replace("/", "__"),
                "directory": package_id,
                "method": method,
                "date": date,
                "display_name": display_name,
                "instrument": instrument,
                "summary": summary,
                "readme": f"{package_id}/README.txt",
                "files": files,
            }
        )

    april_ert = root / "2026-04-11" / "ert"
    add_package(
        "ert/2026-04-11_wenner_2m",
        "ERT",
        "2026-04-11",
        "ERT | 2026-04-11 Wenner line",
        "Not recorded in the retained files",
        "One 48-electrode Wenner profile with 2 m electrode spacing.",
        """
APLL ERT PACKAGE: 2026-04-11 WENNER LINE

Data class: Real field data
Acquisition date: 2026-04-11
Method: Electrical resistivity tomography (ERT)
Array: Wenner
Instrument: Not recorded in the retained files
Geometry: 48 electrodes at 2 m spacing; profile coordinates run from 0 to 94 m.

CONTENTS
data/inversion_2026-04-11_Wenner_48elec_2m_flat_positive_only_pygimli.txt
  Approved PyGIMLi-format apparent-resistivity dataset. Only positive apparent
  resistivity values are retained. The inversion geometry is flat.
location/location_2026-04-11_ERT_electrodes_2m_derived.csv
  Electrode distance, UTM/WGS84 coordinates, and estimated elevations. The
  location_basis field records that positions were derived from seismic GPS.

USE NOTES
Use the data and location files together. The location elevations are derived,
whereas the PyGIMLi data file uses flat z coordinates. Do not substitute the
withheld unfiltered or estimated-topography ERT files for this reviewed release.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
""",
        [
            (
                april_ert / "inversion_2026-04-11_Wenner_48elec_2m_flat_positive_only_pygimli.txt",
                "data/inversion_2026-04-11_Wenner_48elec_2m_flat_positive_only_pygimli.txt",
                "quality-controlled PyGIMLi data",
            ),
            (
                april_ert / "location_2026-04-11_ERT_electrodes_2m_derived.csv",
                "location/location_2026-04-11_ERT_electrodes_2m_derived.csv",
                "electrode locations",
            ),
        ],
    )

    may_ert = root / "2026-05-02" / "ert"
    add_package(
        "ert/2026-05-02_dipole_dipole_1p5m",
        "ERT",
        "2026-05-02",
        "ERT | 2026-05-02 dipole-dipole line",
        "IRIS SYSCAL Pro",
        "One 48-electrode dipole-dipole profile with nominal 1.5 m spacing.",
        """
APLL ERT PACKAGE: 2026-05-02 DIPOLE-DIPOLE LINE

Data class: Real field data
Acquisition date: 2026-05-02
Method: Electrical resistivity tomography (ERT)
Array: Dipole-dipole
Instrument: IRIS SYSCAL Pro
Geometry: 48 stainless-steel electrodes at nominal 1.5 m spacing. Field notes
report an approximately 72 m survey line and approximately 0.30 m electrode
insertion depth. The coordinate files span 0 to 70.5 m between end electrodes.

CONTENTS
data/inversion_2026-05-02_May2_dipole_dipole_positive_only_pygimli.txt
  Approved topographic PyGIMLi-format apparent-resistivity dataset. Only
  positive apparent resistivity values are retained.
location/location_2026-05-02_ert_electrodes_UTM_1p5m.txt
  Electrode distance, UTM coordinates, and elevation.
location/location_2026-05-02_ert_electrodes_wgs84.csv
  Matching UTM and WGS84 electrode coordinates.

USE NOTES
Use one of the two location files according to the required coordinate system.
Do not use the withheld unfiltered version of this ERT dataset.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
""",
        [
            (
                may_ert / "inversion_2026-05-02_May2_dipole_dipole_positive_only_pygimli.txt",
                "data/inversion_2026-05-02_May2_dipole_dipole_positive_only_pygimli.txt",
                "quality-controlled PyGIMLi data",
            ),
            (
                may_ert / "location_2026-05-02_ert_electrodes_UTM_1p5m.txt",
                "location/location_2026-05-02_ert_electrodes_UTM_1p5m.txt",
                "electrode locations (UTM)",
            ),
            (
                may_ert / "location_2026-05-02_ert_electrodes_wgs84.csv",
                "location/location_2026-05-02_ert_electrodes_wgs84.csv",
                "electrode locations (UTM and WGS84)",
            ),
        ],
    )

    april_seismic = root / "2026-04-11" / "seismic"
    april_shots = sorted(april_seismic.glob("*.dat"), key=lambda path: int(path.stem))
    add_package(
        "srt/2026-04-11_line",
        "SRT",
        "2026-04-11",
        "SRT | 2026-04-11 line",
        "Geometrics acquisition system (model not recorded)",
        "One seismic-refraction line with 15 Geometrics DAT shot records.",
        """
APLL SRT PACKAGE: 2026-04-11 LINE

Data class: Real field data
Acquisition date: 2026-04-11
Method: Seismic refraction tomography (SRT)
Instrument: Geometrics acquisition system; model not recorded in retained files
Acquisition unit: One line with 15 raw DAT shot records and 15 GPS positions.

CONTENTS
data/shot_01.dat through data/shot_15.dat
  Raw Geometrics shot records, renamed only to preserve numeric sort order.
location/location_2026-04-11_seismic_GPS_points.csv
  WGS84 longitude, latitude, and elevation for the 15 recorded positions.

USE NOTES
The supplied metadata do not document receiver spacing, source offsets, or the
mapping between every DAT record and every GPS row. Preserve record order and
verify geometry before inversion.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
""",
        [
            *[(path, f"data/shot_{int(path.stem):02d}.dat", "raw shot record") for path in april_shots],
            (
                april_seismic / "location_2026-04-11_seismic_GPS_points.csv",
                "location/location_2026-04-11_seismic_GPS_points.csv",
                "line locations",
            ),
        ],
    )

    may_seismic = root / "2026-05-02" / "seismic"
    may_locations = pd.read_csv(may_seismic / "location_2026-05-02_seismic_positions_wgs84.csv")
    for line_number in (1000, 2000):
        package_id = f"srt/2026-05-02_line_{line_number}"
        package_dir = packages_root / package_id
        line_locations = may_locations.loc[may_locations["line"] == line_number].copy()
        line_location_path = package_dir / "location" / f"line_{line_number}_positions_wgs84.csv"
        line_location_path.parent.mkdir(parents=True, exist_ok=True)
        line_locations.to_csv(line_location_path, index=False, float_format="%.6f")
        copies = [
            (may_seismic / f"{line_number}.sgy", f"data/line_{line_number}.sgy", "raw SEG-Y waveforms"),
            (
                may_seismic / f"{line_number}_28pts.txt",
                f"location/line_{line_number}_positions_utm.txt",
                "source/receiver positions (UTM)",
            ),
            (
                may_seismic / f"{line_number}_first_break_picks.csv",
                f"processed/line_{line_number}_first_break_picks.csv",
                "interpreted first-break picks",
            ),
        ]
        add_package(
            package_id,
            "SRT",
            "2026-05-02",
            f"SRT | 2026-05-02 line {line_number}",
            "24-channel seismic acquisition system; sledgehammer source",
            f"One 24-channel seismic-refraction line with 28 source positions and first-break picks.",
            f"""
APLL SRT PACKAGE: 2026-05-02 LINE {line_number}

Data class: Real field data
Acquisition date: 2026-05-02
Method: Seismic refraction tomography (SRT)
Receiver setup: 24 geophones at nominal 2 m spacing
Source: Sledgehammer impact on an aluminum plate
Acquisition: Three impacts were collected at each source station for stacking
and noise reduction. Source stations extend 4 m beyond both ends of the receiver
spread. The supplied geometry contains 28 positions at 2 m spacing (0 to 54 m).

CONTENTS
data/line_{line_number}.sgy
  Raw SEG-Y waveform data for this line.
location/line_{line_number}_positions_utm.txt
  Ordered source/receiver geometry in UTM coordinates with elevations.
location/line_{line_number}_positions_wgs84.csv
  The same 28 positions with UTM and WGS84 coordinates.
processed/line_{line_number}_first_break_picks.csv
  Interpreted first-arrival picks with trace and geometry metadata.

USE NOTES
The first-break table is interpreted data, not raw acquisition. Keep it separate
from the SEG-Y waveforms when testing picking or uncertainty workflows.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
""",
            copies,
        )
        package = packages[-1]
        generated_item = {
            "path": line_location_path.as_posix(),
            "extension": line_location_path.suffix.lower(),
            "size_bytes": line_location_path.stat().st_size,
            "sha256": sha256(line_location_path),
            "role": "line locations (UTM and WGS84)",
        }
        package["files"].insert(-1, generated_item)

    # Reuse the audited profile/elevation workflow, then place all EM products
    # in one acquisition package with clear raw/processed/inversion roles.
    with tempfile.TemporaryDirectory() as temporary_directory:
        stage_root = Path(temporary_directory)
        build_organized_em_products(root, stage_root)
        staged_em = stage_root / "em"
        em_source = root / "2026-05-02" / "em"
        em_package_id = "em/2026-05-02_gem2_survey"
        em_dir = packages_root / em_package_id
        em_copies: list[tuple[Path, str, str]] = [
            (
                em_source / "raw_22-xg-12se-294_gem_averaged_original_copy.csv",
                "raw/2026-05-02_gem2_raw_averaged_instrument_export.csv",
                "raw averaged instrument export",
            ),
            (
                staged_em / "measurements" / "2026-05-02_gem2_averaged_inphase_quadrature.csv",
                "processed/2026-05-02_gem2_averaged_inphase_quadrature.csv",
                "processed averaged I/Q observations",
            ),
            (
                staged_em / "metadata" / "profile_mark_ranges.csv",
                "metadata/profile_mark_ranges.csv",
                "profile-to-Mark mapping",
            ),
            (
                staged_em / "models" / "2026-05-02_gem2_valid_layered_inversion.csv",
                "inversion/2026-05-02_gem2_valid_layered_inversion.csv",
                "derived layered inversion",
            ),
            *[
                (
                    staged_em / "profiles" / f"profile_{number:02d}_locations.csv",
                    f"location/profile_{number:02d}_locations.csv",
                    f"Profile {number:02d} locations",
                )
                for number in range(1, 10)
            ],
        ]
        add_package(
            em_package_id,
            "EM",
            "2026-05-02",
            "EM | 2026-05-02 GEM-2 survey (Profiles 01-09)",
            "Geophex GEM-2 Ski, hand-held frequency-domain EM system",
            "One GEM-2 acquisition containing Profiles 01-09, raw averaged I/Q, processed I/Q, locations, and inversion results.",
            """
APLL EM PACKAGE: 2026-05-02 GEM-2 SURVEY

Data class: Real field data
Acquisition date: 2026-05-02
Method: Frequency-domain electromagnetic induction (FDEM)
Instrument: Geophex GEM-2 Ski, hand-held system
Survey organization: Nine survey profiles acquired in one field campaign
Frequencies: 450, 1410, 4350, 13530, and 42150 Hz
Response components: In-phase (I) and quadrature (Q)
Coordinate reference system: NAD83 / UTM zone 15N (EPSG:26915)

CONTENTS
raw/2026-05-02_gem2_raw_averaged_instrument_export.csv
  Original-copy averaged instrument export. This is the earliest retained GEM-2
  table, but it is already averaged and must not be described as unaveraged raw
  time-series data.
processed/2026-05-02_gem2_averaged_inphase_quadrature.csv
  Canonical processed input with the original five-frequency I/Q columns.
location/profile_01_locations.csv through profile_09_locations.csv
  Ordered profile-specific UTM coordinates and elevations. Estimated elevations
  are explicitly identified by the elevation_source field.
metadata/profile_mark_ranges.csv
  Mapping from measurement Mark ranges to Profiles 01-09.
inversion/2026-05-02_gem2_valid_layered_inversion.csv
  Quality-screened layered inversion results. This is a derived product and must
  not be substituted for the I/Q observations in processing workflows.
manifest.json
  Machine-readable package structure, roles, checksums, and acquisition metadata.

USE NOTES
Use metadata/profile_mark_ranges.csv to assign observations to profiles. Join a
profile to its matching location file; do not apply one shared position file to
all profiles. Start processing from the processed I/Q table when reproducing the
PyHydroGeophysX workflow, and use the raw averaged export for lower-level QA.

License: CC BY 4.0. See ../../../DATA_LICENSE.txt.
""",
            em_copies,
        )
        em_package = packages[-1]
        manifest = {
            "dataset": "Ashton Prairie GEM-2 frequency-domain EM survey",
            "data_class": "real field data",
            "acquisition_date": "2026-05-02",
            "instrument": "Geophex GEM-2 Ski",
            "frequencies_hz": [450, 1410, 4350, 13530, 42150],
            "response_components": ["in-phase", "quadrature"],
            "coordinate_reference_system": "EPSG:26915",
            "profiles": [f"profile_{number:02d}" for number in range(1, 10)],
            "files": [
                {
                    "path": Path(item["path"]).relative_to(em_dir).as_posix(),
                    "role": item["role"],
                    "size_bytes": item["size_bytes"],
                    "sha256": item["sha256"],
                }
                for item in em_package["files"]
                if item["role"] != "package guide"
            ],
            "license": "CC BY 4.0",
        }
        manifest_path = em_dir / "manifest.json"
        write_json(manifest_path, manifest)
        em_package["files"].append(
            {
                "path": manifest_path.as_posix(),
                "extension": ".json",
                "size_bytes": manifest_path.stat().st_size,
                "sha256": sha256(manifest_path),
                "role": "machine-readable package manifest",
            }
        )

    # Store catalog-facing paths relative to the package root.
    for package in packages:
        for item in package["files"]:
            item["path"] = Path(item["path"]).relative_to(packages_root).as_posix()
            item["url"] = f"../data/ashton/packages/{item['path']}"

    downloads_root = packages_root.parent / "downloads"
    downloads_root.mkdir(parents=True, exist_ok=True)
    for package in packages:
        archive_name = f"apll_{package['id'].replace('__', '_')}.zip"
        archive_path = downloads_root / archive_name
        top_level = f"apll_{Path(package['directory']).name}"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in package["files"]:
                source_path = packages_root / item["path"]
                within_package = Path(item["path"]).relative_to(package["directory"])
                archive.write(source_path, (Path(top_level) / within_package).as_posix())
        package["archive"] = archive_name
        package["archive_url"] = f"../data/ashton/downloads/{archive_name}"
        package["archive_size_bytes"] = archive_path.stat().st_size
        package["archive_sha256"] = sha256(archive_path)
    return packages


def build_web_products(root: Path, output: Path) -> dict[str, Any]:
    """Build curated survey-line and processed-data layers for the Web GIS."""

    master_path = root / "Ashton_all_dates_all_points.csv"
    master = pd.read_csv(master_path, dtype={"point_id": str})
    em_location_frames: list[pd.DataFrame] = []
    for path in sorted((root / "2026-05-02" / "em").glob("location_line *.txt")):
        frame = pd.read_csv(path)
        line_number = int(re.search(r"(\d+)", path.stem).group(1))
        frame["line_number"] = line_number
        frame["line_index"] = np.arange(1, len(frame) + 1)
        frame["source_file"] = path.name
        em_location_frames.append(frame)
    em_source_locations = pd.concat(em_location_frames, ignore_index=True)
    em_source_locations["elevation_status"] = np.where(
        em_source_locations["Z"] > 0,
        "provided_in_source",
        "zero_placeholder_missing_elevation",
    )
    missing, interpolation = idw_interpolation(em_location_frames)
    estimates = {
        (int(row.line_number), int(row.line_index)): float(row.Z_interpolated)
        for row in missing.itertuples()
    }

    master["data_class"] = "real"
    master["elevation_source"] = "provided_in_source"
    master["quality_flags"] = ""
    for index, row in master.iterrows():
        if row["group"] == "EM line 4" and float(row["elevation_m"]) == 0:
            point_number = int(str(row["point_id"]).split("-")[-1])
            master.at[index, "elevation_m"] = estimates[(4, point_number)]
            master.at[index, "elevation_source"] = "interpolated_from_neighboring_em_points"
            master.at[index, "quality_flags"] = "interpolated_elevation"
        elif row["display_name"] == "0502-EM4-01":
            master.at[index, "quality_flags"] = "elevation_differs_from_neighboring_line_interpolation"

    grouped_coordinates: defaultdict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in master.iterrows():
        key = (f"{float(row['longitude_WGS84']):.10f}", f"{float(row['latitude_WGS84']):.10f}")
        grouped_coordinates[key].append(index)
    for indices in grouped_coordinates.values():
        same_group = defaultdict(list)
        for index in indices:
            same_group[str(master.at[index, "group"])].append(index)
        for group_indices in same_group.values():
            if len(group_indices) > 1:
                for index in group_indices:
                    current = str(master.at[index, "quality_flags"]).strip(";")
                    master.at[index, "quality_flags"] = ";".join(filter(None, [current, "duplicate_position"]))

    output.mkdir(parents=True, exist_ok=True)
    master.to_csv(output / "survey_locations_curated.csv", index=False, float_format="%.10g")

    line_features = []
    excluded_preprocessing_lines = {
        ("2026-06-25", "ERT", "ERT electrodes 267-314"),
    }
    for (date, instrument, group), frame in master.groupby(["date", "instrument", "group"], sort=False):
        if (date, instrument, group) in excluded_preprocessing_lines:
            continue
        coordinates = frame[["longitude_WGS84", "latitude_WGS84"]].astype(float).values.tolist()
        line_features.append(
            geojson_feature(
                {"type": "LineString", "coordinates": coordinates},
                {
                    "data_class": "real",
                    "date": date,
                    "instrument": instrument,
                    "group": group,
                    "point_count": int(len(frame)),
                    "geometry_note": "Line connects survey points in source-file order.",
                },
            )
        )
    write_json(output / "survey_lines.geojson", {"type": "FeatureCollection", "features": line_features}, True)

    xy = master[["longitude_WGS84", "latitude_WGS84"]].to_numpy(float)
    hull = ConvexHull(xy)
    polygon = xy[hull.vertices].tolist()
    polygon.append(polygon[0])
    extent_feature = geojson_feature(
        {"type": "Polygon", "coordinates": [polygon]},
        {
            "data_class": "derived_from_real",
            "name": "Survey footprint",
            "geometry_note": "Convex hull of the curated survey-location table; not the official prairie boundary.",
        },
    )
    write_json(output / "survey_extent.geojson", {"type": "FeatureCollection", "features": [extent_feature]}, True)

    em = pd.read_csv(root / "2026-05-02" / "em" / "processed_valid_inversion.csv", skipinitialspace=True)
    em = em[(em["FitError(%)"] <= 30) & (em["GPSStat"] > 0)].copy()
    em["x_grid"] = em["X"].round()
    em["y_grid"] = em["Y"].round()
    aggregated = (
        em.groupby(["x_grid", "y_grid"], as_index=False)
        .agg(
            shallow_resistivity_ohm_m=("ResLayer_1", "median"),
            fit_error_percent=("FitError(%)", "median"),
            sample_count=("Sample", "count"),
            line=("Line", "first"),
        )
    )
    transformer = Transformer.from_crs("EPSG:26915", "EPSG:4326", always_xy=True)
    longitudes, latitudes = transformer.transform(aggregated["x_grid"], aggregated["y_grid"])
    em_features = []
    for row, longitude, latitude in zip(aggregated.itertuples(index=False), longitudes, latitudes):
        em_features.append(
            geojson_feature(
                {"type": "Point", "coordinates": [float(longitude), float(latitude)]},
                {
                    "data_class": "real_processed",
                    "date": "2026-05-02",
                    "instrument": "GEM-2 FDEM",
                    "line": int(row.line),
                    "shallow_resistivity_ohm_m": round(float(row.shallow_resistivity_ohm_m), 2),
                    "fit_error_percent": round(float(row.fit_error_percent), 2),
                    "sample_count": int(row.sample_count),
                    "processing_note": "Median in 1 m cell; inversion fit error <= 30%.",
                },
            )
        )
    write_json(output / "em_shallow_resistivity.geojson", {"type": "FeatureCollection", "features": em_features}, True)

    return {
        "real_survey_lines": len(line_features),
        "excluded_preprocessing_survey_lines": len(excluded_preprocessing_lines),
        "real_em_source_locations": int(len(em_source_locations)),
        "real_em_map_cells": len(em_features),
        "elevation_interpolation": interpolation,
        "interpolated_elevation_count": int(len(missing)),
    }


def build_report(root: Path, output: Path) -> dict[str, Any]:
    """Audit every publishable source file and assemble the quality report."""

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in DATA_EXTENSIONS and path.name.lower() != "desktop.ini"
    )
    reports = [audit_file(path, root) for path in files]
    issues: list[dict[str, str]] = []

    def issue(severity: str, code: str, file: str, finding: str, action: str) -> None:
        issues.append({"severity": severity, "code": code, "file": file, "finding": finding, "publication_action": action})

    report_by_path = {item["path"]: item for item in reports}
    for item in reports:
        if item["status"] == "error":
            issue("error", "unreadable_file", item["path"], item["error"], "Do not publish until readable.")

    issue(
        "warning", "em_line4_missing_elevation", "2026-05-02/em/location_line 4.txt",
        "13 of 14 elevations are stored as 0.0 m.",
        "Replace zero placeholders in curated products with 8-neighbor IDW estimates and retain source flags.",
    )
    issue(
        "warning", "em_line4_anchor_outlier", "2026-05-02/em/location_line 4.txt",
        "The one nonzero line-4 elevation differs by about 5.4 m from a neighboring-line IDW estimate.",
        "Retain the measured value but flag it for field-metadata review.",
    )
    issue(
        "warning", "em_line9_duplicate_position", "2026-05-02/em/location_line 9.txt",
        "The first two records have identical X/Y/Z coordinates.",
        "Retain both records and mark duplicate_position in curated point data.",
    )
    for relative in (
        "2026-04-11/ert/2026-04-11_ert_raw_Wenner_test.txt",
        "2026-05-02/ert/2026-05-02_ert_raw_May2.csv",
        "2026-06-25/ert/2026-06-25_ERT_raw_Ashton_1p5m.csv",
    ):
        metrics = report_by_path[relative]["metrics"]
        issue(
            "warning", "ert_raw_requires_qc", relative,
            f"Raw ERT contains many nonpositive/zero or high-deviation records: {metrics}.",
            "Do not publish or analyze this file; retain only in the external source archive.",
        )
    em_path = "2026-05-02/em/processed_valid_inversion.csv"
    em = pd.read_csv(root / em_path, skipinitialspace=True)
    issue(
        "warning", "em_inversion_fit_filter", em_path,
        f"{int((em['FitError(%)'] > 30).sum())} of {len(em)} inversions exceed 30% fit error.",
        "Exclude those rows from the Web GIS resistivity layer; keep them in the raw download.",
    )
    issue(
        "warning", "em_inversion_bound_hits", em_path,
        f"Layer-1 resistivity equals the 2000 ohm m upper bound in {int(np.isclose(em['ResLayer_1'], 2000).sum())} rows.",
        "Treat 2000 ohm m as a bound hit, not a resolved exact value.",
    )

    workbook = pd.read_excel(root / "2026-05-02/em/processed_All_Lines_Corr_EM.xlsx")
    csv_copy = pd.read_csv(root / "2026-05-02/em/processed_corr.csv", skipinitialspace=True)
    numeric_difference = float(
        np.nanmax(
            np.abs(
                workbook.select_dtypes(include=[np.number]).to_numpy(float)
                - csv_copy.select_dtypes(include=[np.number]).to_numpy(float)
            )
        )
    )
    cross_checks = {
        "xlsx_matches_processed_corr_shape": list(workbook.shape) == list(csv_copy.shape),
        "xlsx_processed_corr_max_numeric_difference": numeric_difference,
        "master_csv_rows": int(pd.read_csv(root / "Ashton_all_dates_all_points.csv").shape[0]),
        "master_kml_points": audit_kml(root / "Ashton_all_dates_all_points.kml")["geometry_counts"]["Point"],
    }
    products = build_web_products(root, output)
    package_versions: dict[str, str] = {}
    for package in ("PyHydroGeophysX", "numpy", "pandas", "scipy", "pyproj", "openpyxl"):
        try:
            package_versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            package_versions[package] = "not installed"
    report = {
        "dataset": "Ashton Prairie Environmental Geophysics Field Data",
        "data_class": "real field data and derived products",
        "official_site": OFFICIAL_SITE,
        "package_repository": PACKAGE_REPOSITORY,
        "license": "CC BY 4.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_file_count": len(files),
        "source_size_bytes": int(sum(path.stat().st_size for path in files)),
        "extension_counts": dict(sorted(Counter(path.suffix.lower() for path in files).items())),
        "overall_status": "pass_with_warnings" if not any(item["severity"] == "error" for item in issues) else "error",
        "package_versions": package_versions,
        "cross_checks": cross_checks,
        "web_products": products,
        "issues": issues,
        "files": reports,
    }
    return report


def is_public_file(relative_path: str, public_root: Path) -> bool:
    """Return whether an audited source is approved and present for download."""

    normalized = relative_path.replace("\\", "/")
    if normalized in PUBLIC_EXCLUSIONS:
        return False
    parts = normalized.lower().split("/")
    is_ert_measurement = (
        "ert" in parts
        and not Path(normalized).name.lower().startswith("location_")
        and Path(normalized).suffix.lower() != ".kml"
    )
    if is_ert_measurement and normalized not in PUBLIC_ERT_DATASETS:
        return False
    return (public_root / Path(normalized)).is_file()


def describe_public_file(relative_path: str) -> dict[str, Any]:
    """Return student-facing category, processing level, and role metadata."""

    normalized = relative_path.replace("\\", "/")
    name = Path(normalized).name
    lower = normalized.lower()
    category = "Survey geometry"
    level = "source geometry"
    recommended = False
    display_name = name
    description = "Survey geometry or acquisition metadata retained for provenance."

    if "/ert/" in lower:
        category = "ERT"
        if "positive_only" in lower:
            level = "quality-controlled"
            recommended = True
            array = "Wenner" if "wenner" in lower else "dipole–dipole"
            date = "April 11" if "2026-04-11" in lower else "May 2"
            display_name = f"{date} ERT — {array}, positive-only PyGIMLi"
            description = "Approved 48-electrode apparent-resistivity dataset used by the notebook."
        else:
            display_name = f"ERT geometry — {name}"
            description = "Electrode coordinates and elevations; no resistivity measurements."
    elif "/em/" in lower:
        category = "EM"
        if name == "raw_22-xg-12se-294_gem_averaged_original_copy.csv":
            level = "raw measurements"
            display_name = "May 2 GEM-2 — raw averaged responses"
            description = "Original averaged in-phase and quadrature responses at five frequencies."
        elif name == "processed_valid_inversion.csv":
            level = "quality-controlled model"
            recommended = True
            display_name = "May 2 GEM-2 — valid layered inversion"
            description = "Canonical 10,538-row inversion table with reconstructed line and sample keys."
        else:
            level = "acquisition metadata"
            display_name = "May 2 GEM-2 — line/mark metadata"
            description = "Source notes used to reconstruct EM survey lines."
    elif "/seismic/" in lower:
        category = "Seismic"
        if name.lower().endswith(".sgy"):
            level = "raw waveforms"
            recommended = True
            display_name = f"May 2 seismic line {Path(name).stem} — SEG-Y"
            description = "Raw 28-field-record seismic line read directly by PyHydroGeophysX."
        elif name.lower().endswith("_first_break_picks.csv"):
            level = "interpreted picks"
            recommended = True
            display_name = f"May 2 seismic line {name.split('_')[0]} — first-break picks"
            description = "First-arrival picks with trace, geometry, time, and amplitude metadata."
        elif name.lower().endswith(".dat"):
            level = "raw waveforms"
            display_name = f"April 11 seismic shot {Path(name).stem} — Geometrics DAT"
            description = "One raw 24-channel Geometrics shot record."
        elif name.lower().endswith("_28pts.txt"):
            level = "source geometry"
            display_name = f"May 2 seismic line {name.split('_')[0]} — source/geophone positions"
            description = "UTM source positions, elevations, and geophone mapping for the SEG-Y line."
        else:
            display_name = "May 2 seismic — consolidated WGS84 geometry"
            description = "UTM/WGS84 positions for both May 2 seismic lines."
    elif name == "Ashton_all_dates_all_points.csv":
        level = "source inventory"
        recommended = True
        display_name = "All dates and methods — source survey inventory"
        description = "Canonical 367-row source table before derived elevation interpolation."
    elif name == "Ashton_all_dates_all_points.kml":
        level = "GIS geometry"
        display_name = "All dates and methods — consolidated KML"
        description = "GIS representation of the complete source survey inventory."

    return {
        "display_name": display_name,
        "category": category,
        "processing_level": level,
        "recommended": recommended,
        "description": description,
        "source_class": "source",
    }


def build_catalog(
    report: dict[str, Any],
    output: Path,
    public_root: Path,
    organized_products: list[dict[str, Any]],
) -> None:
    """Create the browser catalog from approved public files in the audit report."""

    notes_by_file: defaultdict[str, list[str]] = defaultdict(list)
    for issue in report["issues"]:
        notes_by_file[issue["file"]].append(issue["finding"])
    source_files = []
    for item in report["files"]:
        if not is_public_file(item["path"], public_root):
            continue
        source_files.append(
            {
                "path": item["path"],
                "url": f"../data/ashton/raw/{item['path']}",
                "extension": item["extension"],
                "size_bytes": item["size_bytes"],
                "status": item["status"],
                "quality_notes": notes_by_file[item["path"]],
                **describe_public_file(item["path"]),
            }
        )

    curated_specs = [
        (
            "derived/survey_locations_curated.csv",
            "survey_locations_curated.csv",
            "Survey geometry",
            "quality-controlled",
            "All dates and methods — curated survey locations",
            "Recommended 367-row location table with elevation provenance and quality flags.",
            True,
        ),
        (
            "derived/em_shallow_resistivity.geojson",
            "em_shallow_resistivity.geojson",
            "EM",
            "mapped derived product",
            "May 2 GEM-2 — shallow-resistivity map cells",
            "Recommended 1 m GeoJSON cells after fit-error screening and spatial aggregation.",
            True,
        ),
    ]
    curated_files = []
    for catalog_path, filename, category, level, display_name, description, recommended in curated_specs:
        path = output / filename
        curated_files.append(
            {
                "path": catalog_path,
                "url": f"../data/ashton/web/{filename}",
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "status": "reviewed",
                "quality_notes": [],
                "display_name": display_name,
                "category": category,
                "processing_level": level,
                "recommended": recommended,
                "description": description,
                "source_class": "derived",
            }
        )

    organized_files = []
    for product in organized_products:
        path = Path(product["filename"])
        quality_notes = []
        if "profile_04_locations" in product["path"]:
            quality_notes.append("13 source elevation placeholders were replaced by flagged IDW estimates.")
        if "/models/" in product["path"]:
            quality_notes.append("Derived inversion result; use the averaged I/Q table as the processing input.")
        organized_files.append(
            {
                "path": product["path"],
                "url": f"../data/ashton/{product['path']}",
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "status": "reviewed",
                "quality_notes": quality_notes,
                "display_name": product["display_name"],
                "category": "EM",
                "processing_level": product["processing_level"],
                "recommended": product["recommended"],
                "description": product["description"],
                "source_class": product["source_class"],
            }
        )

    catalog = {
        "dataset": report["dataset"],
        "data_class": "real",
        "license": report["license"],
        "official_site": report["official_site"],
        "publication_summary": {
            "audited_source_files": report["source_file_count"],
            "published_source_files": len(source_files),
            "curated_products": len(curated_files),
            "organized_em_files": len(organized_files),
            "withheld_problem_ert_files": 6,
            "removed_redundant_or_intermediate_files": len(PUBLIC_EXCLUSIONS),
        },
        "files": organized_files + curated_files + source_files,
    }
    write_json(output / "data_catalog.json", catalog)


def build_package_catalog(
    report: dict[str, Any],
    output: Path,
    packages: list[dict[str, Any]],
) -> None:
    """Create a package-level browser catalog and a flat notebook index."""

    public_packages: list[dict[str, Any]] = []
    flat_files: list[dict[str, Any]] = []
    for package in packages:
        package_files = []
        for item in package["files"]:
            file_item = {
                **item,
                "package_id": package["id"],
                "category": package["method"],
                "dataset": package["display_name"],
                "display_name": Path(item["path"]).name,
                "processing_level": item["role"],
                "description": package["summary"],
                "status": "reviewed",
                "quality_notes": [],
                "recommended": item["role"] in {
                    "package guide",
                    "quality-controlled PyGIMLi data",
                    "raw SEG-Y waveforms",
                    "processed averaged I/Q observations",
                },
                "source_class": "real field data",
            }
            package_files.append(file_item)
            flat_files.append(file_item)
        package_summary = {
            key: package[key]
            for key in (
                "id",
                "directory",
                "method",
                "date",
                "display_name",
                "instrument",
                "summary",
                "readme",
            )
        }
        package_summary.update(
            {
                "readme_url": f"../data/ashton/packages/{package['readme']}",
                "archive": package["archive"],
                "archive_url": package["archive_url"],
                "archive_size_bytes": package["archive_size_bytes"],
                "archive_sha256": package["archive_sha256"],
                "file_count": len(package_files),
                "size_bytes": sum(item["size_bytes"] for item in package_files),
                "files": package_files,
            }
        )
        public_packages.append(package_summary)

    catalog = {
        "dataset": report["dataset"],
        "data_class": "real",
        "license": report["license"],
        "official_site": report["official_site"],
        "publication_summary": {
            "audited_source_files": report["source_file_count"],
            "published_packages": len(public_packages),
            "published_package_files": len(flat_files),
            "download_archives": len(public_packages),
            "withheld_problem_ert_files": 6,
            "removed_redundant_or_intermediate_files": len(PUBLIC_EXCLUSIONS),
        },
        "packages": public_packages,
        "files": flat_files,
    }
    write_json(output / "data_catalog.json", catalog)


def main() -> int:
    """Run the complete audit and Web GIS preparation workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Root directory containing the Ashton source files.")
    parser.add_argument("output", type=Path, help="Directory for curated Web GIS products and reports.")
    parser.add_argument(
        "--packages-root",
        type=Path,
        default=None,
        help="Published acquisition-package directory; defaults to a sibling of the Web output directory.",
    )
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    packages_root = args.packages_root.resolve() if args.packages_root else output.parent / "packages"
    if not source.exists():
        parser.error(f"Source directory does not exist: {source}")
    report = build_report(source, output)
    packages = build_data_packages(source, packages_root)
    write_json(output / "quality_report.json", report)
    build_package_catalog(report, output, packages)
    print(
        f"Reviewed {report['source_file_count']} Ashton files; "
        f"status={report['overall_status']}; "
        f"lines={report['web_products']['real_survey_lines']}; "
        f"EM cells={report['web_products']['real_em_map_cells']}."
    )
    return 1 if report["overall_status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
