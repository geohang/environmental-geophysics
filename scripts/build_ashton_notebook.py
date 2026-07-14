"""Build the reproducible Ashton Prairie field-data teaching notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "notebooks" / "ashton_field_data.ipynb"


def code(source: str) -> nbf.NotebookNode:
    """Return a code cell with concise execution metadata."""

    return nbf.v4.new_code_cell(source.strip())


def markdown(source: str) -> nbf.NotebookNode:
    """Return a Markdown cell."""

    return nbf.v4.new_markdown_cell(source.strip())


def build_notebook() -> nbf.NotebookNode:
    """Assemble the Ashton notebook from auditable source cells."""

    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
        "colab": {"name": "ashton_field_data.ipynb", "provenance": []},
    }
    notebook["cells"] = [
        markdown(
            """
# Ashton Prairie field-data quality control and exploration

This notebook works with **real field data** collected at the University of Iowa's
[Ashton Prairie Living Laboratory](https://sees.uiowa.edu/research/ashton-prairie).
It uses the public `PyHydroGeophysX` API for seismic reading and preprocessing,
and PyGIMLi for the two approved positive-only ERT teaching datasets.

**Data boundary.** Raw files are unchanged. Derived values carry provenance and
quality flags. The optional synthetic overlays are teaching hypotheses, never
observations. Data are released under CC BY 4.0; cite *Chen, Hang, and the
University of Iowa Environmental Geophysics course/research team (2026).*
"""
        ),
        markdown(
            """
## 1. Environment and data access

Run the cells from top to bottom. In Colab, the setup cell installs pinned major
versions only when a dependency is missing. In a repository checkout, files are
read locally; Colab downloads only the files used in this notebook.
"""
        ),
        code(
            r'''
import importlib.util
import subprocess
import sys

required = {
    "PyHydroGeophysX": "PyHydroGeophysX==0.3.0",
    "pygimli": "pygimli>=1.5,<2",
    "pyproj": "pyproj>=3.6,<4",
    "openpyxl": "openpyxl>=3.1,<4",
}
missing = [spec for module, spec in required.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlretrieve

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from PyHydroGeophysX.data_processing import normalize_traces, read_segy

REPOSITORY = "https://raw.githubusercontent.com/geohang/environmental-geophysics/main/docs/data/ashton"
LOCAL_ROOT = next(
    (candidate / "docs" / "data" / "ashton" for candidate in [Path.cwd(), *Path.cwd().parents]
     if (candidate / "docs" / "data" / "ashton").exists()),
    None,
)
CACHE = Path("/content/ashton-data") if Path("/content").exists() else Path(".ashton-data-cache")

def data_file(relative_path: str) -> Path:
    """Return a local Ashton file, downloading it from GitHub when necessary."""
    if LOCAL_ROOT is not None:
        return LOCAL_ROOT / relative_path
    target = CACHE / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        urlretrieve(f"{REPOSITORY}/{quote(relative_path, safe='/')}", target)
    return target

print("Data source:", LOCAL_ROOT or REPOSITORY)
print("PyHydroGeophysX import: OK")
'''
        ),
        markdown(
            """
## 2. Survey inventory and elevation provenance

The curated table contains the 367 surveyed positions. The 13 zero elevations
on 2026-05-02 EM line 4 are treated as missing and replaced by inverse-distance
weighted (IDW) estimates from eight neighboring, valid EM elevations in UTM zone
15N. These are estimates, not field measurements.
"""
        ),
        code(
            r'''
locations = pd.read_csv(data_file("web/survey_locations_curated.csv"))
summary = locations.groupby(["date", "instrument"]).size().rename("points").to_frame()
display(summary)

line4 = locations[(locations["date"] == "2026-05-02") & (locations["group"] == "EM line 4")]
display(line4[["display_name", "elevation_m", "elevation_source", "quality_flags"]])

assert len(locations) == 367
assert (line4["elevation_source"] == "interpolated_from_neighboring_em_points").sum() == 13
'''
        ),
        code(
            r'''
em_lines = []
for line_number in range(1, 10):
    frame = pd.read_csv(data_file(f"raw/2026-05-02/em/location_line {line_number}.txt"))
    frame["line_number"] = line_number
    frame["line_index"] = np.arange(1, len(frame) + 1)
    em_lines.append(frame)
em_locations = pd.concat(em_lines, ignore_index=True)

valid = em_locations[em_locations["Z"] > 0].copy()
missing_line4 = em_locations[(em_locations["line_number"] == 4) & (em_locations["Z"] == 0)].copy()
tree = cKDTree(valid[["X", "Y"]])
distance, neighbor = tree.query(missing_line4[["X", "Y"]], k=8)
weights = 1.0 / np.maximum(distance, 0.25) ** 2
idw = (weights * valid["Z"].to_numpy()[neighbor]).sum(axis=1) / weights.sum(axis=1)

published = line4[line4["elevation_source"].str.startswith("interpolated")]["elevation_m"].to_numpy()
np.testing.assert_allclose(idw, published, rtol=0, atol=1e-6)
print(f"Reproduced {len(idw)} interpolated elevations: {idw.min():.2f}–{idw.max():.2f} m")
print("Independent leave-one-out check reported by the audit: RMSE 0.88 m; MAE 0.61 m.")
'''
        ),
        markdown(
            """
## 3. ERT quality-controlled teaching dataset

For instruction, we load only the positive-only PyGIMLi files: the April 11
Wenner dataset and the May 2 dipole–dipole dataset. Both are already formatted
as PyGIMLi `DataContainerERT` objects. The problematic raw exports remain in the
external source archive but are **not published, read, or analyzed in this
notebook**. Apparent resistivity is not true resistivity or an inversion model.
"""
        ),
        code(
            r'''
from pygimli.physics import ert

ert_files = {
    "2026-04-11 Wenner": "raw/2026-04-11/ert/inversion_2026-04-11_Wenner_48elec_2m_flat_positive_only_pygimli.txt",
    "2026-05-02 dipole–dipole": "raw/2026-05-02/ert/inversion_2026-05-02_May2_dipole_dipole_positive_only_pygimli.txt",
}
ert_datasets = {name: ert.load(str(data_file(relative))) for name, relative in ert_files.items()}
summary_rows = []
for name, dataset in ert_datasets.items():
    rhoa = np.asarray(dataset["rhoa"], dtype=float)
    summary_rows.append({
        "survey": name, "electrodes": dataset.sensorCount(), "measurements": dataset.size(),
        "minimum_rhoa_ohm_m": rhoa.min(), "median_rhoa_ohm_m": np.median(rhoa),
        "maximum_rhoa_ohm_m": rhoa.max(), "nonpositive_values": int((rhoa <= 0).sum()),
    })
    assert dataset.sensorCount() == 48 and np.all(rhoa > 0)
display(pd.DataFrame(summary_rows).set_index("survey"))
assert ert_datasets["2026-04-11 Wenner"].size() == 178
assert ert_datasets["2026-05-02 dipole–dipole"].size() == 106

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, (name, dataset), color in zip(axes, ert_datasets.items(), ["#1565c0", "#b85c00"]):
    ax.hist(np.log10(np.asarray(dataset["rhoa"], dtype=float)), bins=20, color=color)
    ax.set(xlabel="log10 apparent resistivity (Ω·m)", ylabel="Count", title=name)
fig.tight_layout()
'''
        ),
        markdown(
            """
## 4. Processed EM data: fit error and inversion bounds

The EM file is a processed layered inversion product, so it is **derived real
data**, not a direct resistivity measurement. Cells shown on the Web GIS require
fit error ≤30%. Values at the 2000 Ω·m upper bound are treated as bound hits,
not precise estimates.
"""
        ),
        code(
            r'''
em_model = pd.read_csv(data_file("raw/2026-05-02/em/processed_valid_inversion.csv"))
em_qc = em_model[em_model["FitError(%)"] <= 30].copy()
bound_hits = em_qc["ResLayer_1"] >= 1999.9
display(pd.Series({
    "all_rows": len(em_model), "fit_error_gt_30pct": int((em_model["FitError(%)"] > 30).sum()),
    "retained_rows": len(em_qc), "layer1_upper_bound_hits": int(bound_hits.sum()),
}))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(em_model["FitError(%)"].clip(upper=100), bins=35, color="#1565c0")
axes[0].axvline(30, color="#b42318", linestyle="--", label="Web GIS threshold")
axes[0].set(xlabel="Fit error (%)", ylabel="Count", title="Layered inversion fit")
axes[0].legend()
plot_values = em_qc["ResLayer_1"].clip(upper=1999.9)
scatter = axes[1].scatter(em_qc.X, em_qc.Y, c=plot_values, s=3, cmap="viridis")
axes[1].set(xlabel="UTM easting (m)", ylabel="UTM northing (m)", title="Shallow-layer resistivity")
fig.colorbar(scatter, ax=axes[1], label="Ω·m (bound hits clipped)")
fig.tight_layout()
'''
        ),
        markdown(
            """
## 5. Seismic data with PyHydroGeophysX

`read_segy` preserves the field-record structure; `normalize_traces` scales each
trace for display only. The normalized gather must not be used to compare true
amplitudes. First-break picks also carry picking uncertainty and do not uniquely
determine a velocity model when low-velocity layers or reversals are present.
"""
        ),
        code(
            r'''
segy_path = data_file("raw/2026-05-02/seismic/1000.sgy")
seismic = read_segy(str(segy_path))
traces = np.asarray(seismic.traces)
dt_s = seismic.metadata.sample_interval_us * 1e-6
print(f"SEG-Y shape: {traces.shape[0]} samples × {traces.shape[1]} traces")
print(f"Sample interval: {seismic.metadata.sample_interval_us} µs; field records: {len(seismic.field_records)}")
assert traces.shape == (8000, 672) and len(seismic.field_records) == 28

gather = normalize_traces(traces[:, :24])
time_ms = np.arange(gather.shape[0]) * dt_s * 1000
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(gather[:800], aspect="auto", cmap="gray", vmin=-0.5, vmax=0.5,
          extent=[0.5, 24.5, time_ms[799], time_ms[0]])
ax.set(xlabel="Trace in first field record", ylabel="Time (ms)", title="Normalized seismic gather")
'''
        ),
        code(
            r'''
picks = pd.read_csv(data_file("raw/2026-05-02/seismic/1000_first_break_picks.csv"))
first_record = picks[picks["field_record"] == picks["field_record"].min()].copy()
offset = np.abs(first_record["receiver_x"] - first_record["source_x"])
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(offset, first_record["time_s"] * 1000, color="#b85c00")
ax.set(xlabel="Absolute source–receiver offset (m)", ylabel="Picked time (ms)",
       title="First-arrival picks: first field record")
ax.grid(alpha=0.25)
print(f"Pick table: {len(picks)} rows; plotted field record: {len(first_record)} picks")
'''
        ),
        markdown(
            """
## 6. Interpretation checklist

Before using these data in a report, answer:

1. Which values are raw observations, processed inversion results, interpolated
   coordinates, or synthetic teaching hypotheses?
2. Which selection rule created the positive-only ERT teaching subset, and how
   might that selection affect an inversion or interpretation?
3. What does an EM model value at the inversion upper bound actually constrain?
4. Which reciprocal shots or independent information would test the seismic
   velocity interpretation?
5. Is the 0.88 m interpolation RMSE acceptable for your scientific question?

The complete machine-readable audit is in `web/quality_report.json`; the
interactive map is the course site's **Ashton Field Data Explorer**.
"""
        ),
    ]
    return notebook


def main() -> None:
    """Write the notebook deterministically."""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(nbf.writes(build_notebook()), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
