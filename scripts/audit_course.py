"""Static release checks for the Environmental Geophysics course site."""

from __future__ import annotations

import csv
import math
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
APP_PATTERN = re.compile(r"(?:^|/)apps/[^/]+\.html$")


class CourseHTMLParser(HTMLParser):
    """Collect the small set of HTML facts needed by the release audit."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.resources: list[tuple[str, str]] = []
        self.has_title = False
        self.has_viewport = False
        self.controls: list[dict[str, str]] = []
        self.label_fors: set[str] = set()
        self.canvases: list[dict[str, str]] = []
        self._label_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "title":
            self.has_title = True
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "label":
            self._label_depth += 1
            if values.get("for"):
                self.label_fors.add(values["for"])
        if tag in {"input", "select", "textarea"}:
            values["nested-label"] = str(self._label_depth > 0)
            self.controls.append(values)
        if tag == "canvas":
            self.canvases.append(values)
        for attr in ("href", "src"):
            if values.get(attr):
                self.resources.append((attr, values[attr]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._label_depth:
            self._label_depth -= 1


def source_target_exists(source: Path, raw_url: str) -> bool:
    """Return whether a local source link has a corresponding docs artifact."""
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc or raw_url.startswith(("#", "data:", "mailto:", "tel:")):
        return True
    path_text = unquote(parsed.path)
    if not path_text:
        return True
    target = (source.parent / path_text).resolve()
    try:
        target.relative_to(DOCS.resolve())
    except ValueError:
        return target.exists()
    if target.exists():
        return True
    if target.suffix.lower() == ".html" and target.with_suffix(".md").exists():
        return True
    if not target.suffix and target.with_suffix(".md").exists():
        return True
    if not target.suffix and (target / "index.md").exists():
        return True
    return False


def audit_html() -> list[str]:
    """Audit HTML metadata, IDs, local resources, and progressive accessibility."""
    errors: list[str] = []
    files = sorted(DOCS.rglob("*.html"))
    canvas_total = 0
    forbidden_dependencies = {
        "react.development": "development React build",
        "@babel/standalone": "runtime Babel",
        'type="text/babel"': "runtime JSX",
        'cdn.jsdelivr.net/npm/chart.js"': "unversioned Chart.js",
        'cdn.tailwindcss.com"': "unversioned Tailwind browser build",
        "mathjax@3/es5": "unversioned MathJax",
        "polyfill.io": "uncontrolled polyfill service",
    }
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        parser = CourseHTMLParser()
        try:
            parser.feed(text)
        except Exception as exc:  # HTMLParser is permissive, so any failure matters.
            errors.append(f"{relative}: HTML parsing failed: {exc}")
            continue
        canvas_total += len(parser.canvases)
        for token, description in forbidden_dependencies.items():
            if token in text:
                errors.append(f"{relative}: contains {description}")
        if not parser.has_title:
            errors.append(f"{relative}: missing <title>")
        if not parser.has_viewport:
            errors.append(f"{relative}: missing viewport meta tag")
        duplicates = sorted(item for item, count in Counter(parser.ids).items() if count > 1)
        if duplicates:
            errors.append(f"{relative}: duplicate IDs: {', '.join(duplicates)}")
        for attr, url in parser.resources:
            if not source_target_exists(path, url):
                errors.append(f"{relative}: missing local {attr} target: {url}")

        progressive = "assets/javascripts/course-app.js" in text
        for control in parser.controls:
            control_type = control.get("type", "").lower()
            if control_type == "hidden":
                continue
            control_id = control.get("id", "")
            labelled = (
                control.get("nested-label") == "True"
                or bool(control.get("aria-label"))
                or bool(control.get("aria-labelledby"))
                or bool(control_id and control_id in parser.label_fors)
            )
            if not labelled and not progressive:
                errors.append(f"{relative}: unlabelled {control.get('type', 'control')} control")
        for canvas in parser.canvases:
            named = bool(canvas.get("aria-label") or canvas.get("aria-labelledby") or canvas.get("title"))
            if not named and not progressive:
                errors.append(f"{relative}: canvas lacks an accessible name")

        docs_relative = path.relative_to(DOCS).as_posix()
        if APP_PATTERN.search(docs_relative):
            if "assets/stylesheets/course-app.css" not in text:
                errors.append(f"{relative}: standalone app missing course-app.css")
            if not progressive:
                errors.append(f"{relative}: standalone app missing course-app.js")
    if canvas_total != 46:
        errors.append(f"Expected 46 parsed canvas elements, found {canvas_total}")
    return errors


def audit_assessments() -> list[str]:
    """Check public question count/levels and private-public separation."""
    errors: list[str] = []
    practice = (DOCS / "apps" / "practice-lab.html").read_text(encoding="utf-8")
    ids = re.findall(r"\{id:'([^']+)',m:'([^']+)',l:'([^']+)'", practice)
    if len(ids) != 45:
        errors.append(f"Practice Lab: expected 45 questions, found {len(ids)}")
    module_counts = Counter(module for _, module, _ in ids)
    for module in ("intro", "gravity", "magnetic", "seismic", "electrical", "em", "gpr", "mt", "borehole"):
        if module_counts[module] != 5:
            errors.append(f"Practice Lab: {module} has {module_counts[module]} questions, expected 5")
    allowed_levels = {"Undergraduate", "Graduate", "Both"}
    invalid_levels = sorted({level for _, _, level in ids} - allowed_levels)
    if invalid_levels:
        errors.append(f"Practice Lab: invalid levels: {', '.join(invalid_levels)}")
    if (DOCS / "instructor").exists():
        errors.append("Private instructor materials must not exist inside docs/")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "instructor/" not in gitignore:
        errors.append(".gitignore does not exclude instructor/")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    if "mkdocs-material==" not in requirements:
        errors.append("requirements.txt must pin MkDocs Material exactly")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for field in ("cff-version:", "title:", "authors:", "repository-code:", "license:"):
        if field not in citation:
            errors.append(f"CITATION.cff missing {field}")

    lesson_path = DOCS / "apps" / "lecture-frameworks.html"
    lesson_text = lesson_path.read_text(encoding="utf-8")
    lesson_names = re.findall(r"\n  ([a-z]+):\{\n    nav:'", lesson_text)
    if len(lesson_names) != 9:
        errors.append(f"Active-learning lessons: expected 9 lessons, found {len(lesson_names)}")
    for link in re.findall(r"(?:url|practice|activity|next):'([^']+)'", lesson_text):
        if not source_target_exists(lesson_path, link):
            errors.append(f"Active-learning lessons: missing local target {link}")
    for required in (
        "Predict before clicking",
        "Play the demo or activity",
        "Guided exploration",
        "Formative practice",
        "Discussion & exit ticket",
    ):
        if required not in lesson_text:
            errors.append(f"Active-learning lessons: missing slide role {required}")
    if "How to use and cite these frameworks" in lesson_text:
        errors.append("Active-learning lessons still contain the old framework preamble")
    for forbidden in (
        "Undergraduate Core",
        "Graduate Extension",
        "Instructor role",
        "teacher mini-lesson",
    ):
        if forbidden in lesson_text:
            errors.append(f"Active-learning lessons expose presentation meta-text: {forbidden}")
    return errors


def audit_numerical_benchmarks() -> list[str]:
    """Verify reference calculations used throughout the teaching apps."""
    errors: list[str] = []

    def check(name: str, value: float, expected: float, tolerance: float) -> None:
        if not math.isfinite(value) or abs(value - expected) > tolerance:
            errors.append(f"Benchmark {name}: got {value}, expected {expected} ± {tolerance}")

    # Archie: rho_b = a*rho_w*phi^-m*Sw^-n.
    check("Archie", 1.0 * 1.0 * 0.1**-2.0 * 1.0**-2.0, 100.0, 1e-10)
    # Ideal sphere half-amplitude occurs at x/z = sqrt(2^(2/3)-1).
    sphere_depth_factor = 1.0 / math.sqrt(2.0 ** (2.0 / 3.0) - 1.0)
    check("gravity sphere half-width", sphere_depth_factor, 1.305, 0.001)
    # Two horizontal layers: t_i = 2h*cos(theta_c)/v1.
    v1, v2, thickness = 500.0, 1500.0, 10.0
    intercept = 2.0 * thickness * math.cos(math.asin(v1 / v2)) / v1
    check("two-layer refraction intercept", intercept, 0.037712, 1e-6)
    check("skin depth", 503.0 * math.sqrt(100.0 / 1000.0), 159.061, 0.01)
    # Zero-offset GPR two-way time for 2 m depth at 0.1 m/ns.
    check("GPR two-way time", 2.0 * 2.0 / 0.1, 40.0, 1e-12)
    check("Wenner geometric factor", 2.0 * math.pi * 5.0, 31.4159, 1e-4)
    # Uniform half-space MT: Z=sqrt(i*w*mu*rho), rho_a=rho and phase=45 degrees.
    rho, frequency, mu0 = 100.0, 1.0, 4.0e-7 * math.pi
    omega = 2.0 * math.pi * frequency
    impedance = complex(0.0, omega * mu0 * rho) ** 0.5
    apparent = abs(impedance) ** 2 / (mu0 * omega)
    check("uniform half-space MT resistivity", apparent, rho, 1e-10)
    check("uniform half-space MT phase", math.degrees(math.atan2(impedance.imag, impedance.real)), 45.0, 1e-10)
    return errors


def audit_classroom_datasets() -> list[str]:
    """Check the units, structure, and expected physics of public lab datasets."""
    errors: list[str] = []

    def rows(relative: str) -> list[dict[str, str]]:
        with (DOCS / "data" / relative).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def minutes(value: str) -> int:
        hour, minute = (int(part) for part in value.split(":"))
        return 60 * hour + minute

    def linear_fit(points: list[tuple[float, float]]) -> tuple[float, float]:
        count = len(points)
        mean_x = sum(point[0] for point in points) / count
        mean_y = sum(point[1] for point in points) / count
        variance = sum((point[0] - mean_x) ** 2 for point in points)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / variance
        return slope, mean_y - slope * mean_x

    # Gravity: reverse the published reduction workflow and require a localized low.
    gravity = rows("gravity/cavity_survey.csv")
    expected_gravity_fields = {"station", "time", "dial_reading", "elevation_m", "north_offset_m"}
    if len(gravity) != 23 or (gravity and set(gravity[0]) != expected_gravity_fields):
        errors.append("Gravity classroom dataset must contain 23 rows and the documented five fields")
    else:
        calibration = 1.053
        base_start = float(gravity[0]["dial_reading"]) * calibration
        base_end = float(gravity[-1]["dial_reading"]) * calibration
        start_time = minutes(gravity[0]["time"])
        drift_rate = (base_end - base_start) / (minutes(gravity[-1]["time"]) - start_time)
        anomaly: list[tuple[float, float]] = []
        for item in gravity[1:-1]:
            offset = float(item["north_offset_m"])
            elevation_difference = float(item["elevation_m"]) - 250.0
            relative_observed = float(item["dial_reading"]) * calibration - base_start
            drift = drift_rate * (minutes(item["time"]) - start_time)
            bouguer = (
                relative_observed
                - drift
                - 0.000812 * offset
                + 0.3086 * elevation_difference
                - 0.04191 * 2.60 * elevation_difference
            )
            anomaly.append((offset, bouguer))
        station_zero = anomaly[0][1]
        anomaly = [(offset, value - station_zero) for offset, value in anomaly]
        minimum = min(anomaly, key=lambda point: point[1])
        if minimum[0] != 100.0 or not -0.185 <= minimum[1] <= -0.175:
            errors.append(f"Gravity cavity response is not the expected midpoint low: {minimum}")
        if abs(anomaly[-1][1]) > 0.002:
            errors.append(f"Gravity profile does not close to baseline: {anomaly[-1][1]:.4g} mGal")
        half_value = minimum[1] / 2.0
        crossings: list[float] = []
        for left, right in zip(anomaly[:-1], anomaly[1:]):
            if (left[1] - half_value) * (right[1] - half_value) <= 0.0:
                fraction = (half_value - left[1]) / (right[1] - left[1])
                crossings.append(left[0] + fraction * (right[0] - left[0]))
        if len(crossings) != 2:
            errors.append(f"Gravity cavity response has {len(crossings)} half-amplitude crossings")
        else:
            estimated_depth = 1.305 * (crossings[1] - crossings[0]) / 2.0
            if not 17.0 <= estimated_depth <= 20.0:
                errors.append(f"Gravity half-width depth is inconsistent: {estimated_depth:.3f} m")

    # Magnetics: reproduce base interpolation and verify the intentionally centered dyke response.
    base = rows("magnetic/base_station.csv")
    traverse = rows("magnetic/raw_dyke_profile.csv")
    if len(base) != 13 or len(traverse) != 61:
        errors.append("Magnetic datasets must contain 13 base and 61 traverse readings")
    else:
        base_minutes = [minutes(item["time"]) for item in base]
        base_values = [float(item["base_field_nT"]) for item in base]

        def interpolate_base(target: int) -> float:
            for index in range(len(base_minutes) - 1):
                left, right = base_minutes[index : index + 2]
                if left <= target <= right:
                    fraction = (target - left) / (right - left)
                    return base_values[index] + fraction * (base_values[index + 1] - base_values[index])
            raise ValueError(f"Magnetic survey time {target} falls outside the base record")

        residual: list[tuple[float, float]] = []
        for item in traverse:
            position = float(item["position_m"])
            diurnal_change = interpolate_base(minutes(item["time"])) - base_values[0]
            value = float(item["raw_field_nT"]) - diurnal_change - (52000.0 + 0.5 * position)
            residual.append((position, value))
        peak = max(residual, key=lambda point: point[1])
        if peak[0] != 62.0 or not 688.0 <= peak[1] <= 689.0:
            errors.append(f"Magnetic corrected dyke peak is inconsistent: {peak}")

    gradiometer = rows("magnetic/gradiometer_profile.csv")
    if not gradiometer or set(gradiometer[0]) != {"position_m", "sensor_difference_nT"}:
        errors.append("Gradiometer data must be labelled as a two-sensor difference in nT")
    else:
        gradient_points = [
            (float(item["position_m"]), float(item["sensor_difference_nT"])) for item in gradiometer
        ]
        if max(gradient_points, key=lambda point: point[1]) != (14.0, 1450.0):
            errors.append("Gradiometer positive extremum has changed")
        if min(gradient_points, key=lambda point: point[1]) != (18.5, -1050.0):
            errors.append("Gradiometer negative extremum has changed")

    # Seismic: verify the three deliberately idealized first-arrival branches.
    seismic = rows("seismic/three_layer_first_arrivals.csv")
    seismic_points = [
        (float(item["position_m"]), float(item["arrival_time_ms"])) for item in seismic
    ]
    for name, lower, upper, expected_velocity in (
        ("direct", 5.0, 15.0, 500.0),
        ("first refractor", 20.0, 90.0, 1500.0),
        ("second refractor", 95.0, 120.0, 3000.0),
    ):
        branch = [point for point in seismic_points if lower <= point[0] <= upper]
        slope, _ = linear_fit(branch)
        velocity = 1000.0 / slope
        if abs(velocity - expected_velocity) > 15.0:
            errors.append(f"Seismic {name} branch gives {velocity:.2f} m/s")

    # Electrical: the public VES curve must retain its stated H-type ordering.
    ves = rows("electrical/ves_sounding.csv")
    apparent = [float(item["apparent_resistivity_ohm_m"]) for item in ves]
    minimum_index = apparent.index(min(apparent)) if apparent else -1
    if not apparent or minimum_index in {0, len(apparent) - 1} or not (
        apparent[0] > apparent[minimum_index] < apparent[-1]
    ):
        errors.append("VES sounding no longer expresses an H-type minimum")
    return errors


def main() -> int:
    """Run all checks and return a process exit status."""
    errors = (
        audit_html()
        + audit_assessments()
        + audit_numerical_benchmarks()
        + audit_classroom_datasets()
    )
    if errors:
        print(f"Course audit failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    html_count = sum(1 for _ in DOCS.rglob("*.html"))
    print(
        f"Course audit passed: {html_count} source HTML apps/pages, 45 practice questions, "
        "9 active-learning lessons, 7 numerical benchmarks, and 5 classroom dataset suites."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
