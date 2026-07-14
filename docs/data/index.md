# Data

Course datasets are separated by provenance so students can see what was measured, what was derived, and what was generated for teaching.

## Real Field Data: Ashton Prairie

The **[Ashton Field Data Explorer](../apps/field-data.html)** maps survey points and lines from the University of Iowa's [Ashton Prairie Living Laboratory](https://sees.uiowa.edu/research/ashton-prairie). It includes layer controls, popups, a downloadable file catalog, and a companion [PyHydroGeophysX processing notebook](../notebooks/ashton_field_data.ipynb).

The public archive contains 54 approved files. All 60 source files were checked, but six problematic ERT measurement files are not published. The ERT teaching workflow uses only the positive-only April 11 Wenner and May 2 dipole–dipole PyGIMLi datasets. Thirteen zero-placeholder elevations on EM line 4 are replaced in **derived products only** by IDW interpolation and retain an `interpolated_elevation` flag; raw source files are unchanged.

!!! info "Real, derived, and synthetic remain distinct"
    Green layers are real field observations, amber layers are derived from real data, and magenta overlays are explicitly synthetic and hidden by default. See the [data license](ashton/DATA_LICENSE.txt) and [machine-readable quality report](ashton/web/quality_report.json).

## Synthetic Teaching Data

The files below are clean synthetic examples that match the activities and notebooks, so every exercise works out of the box. They are not observations from Ashton Prairie.

### By Module

| Module | Dataset | Download | Used In |
|---|---|---|---|
| Gravity | Base-station drift readings | [`drift_readings.csv`](gravity/drift_readings.csv) | [Activity 1 · Drift Correction](../lecture/gravity/apps/activity-1.html) |
| Gravity | Sphere anomaly profile | [`anomaly_profile.csv`](gravity/anomaly_profile.csv) | [Activity 3 · Depth Detective](../lecture/gravity/apps/activity-3.html) |
| Gravity | Revised, forward-constructed cavity-survey loop | [`cavity_survey.csv`](gravity/cavity_survey.csv) | [Classroom Labs · Gravity](../apps/classroom-labs.html#gravity) |
| Magnetics | Base-station time series | [`base_station.csv`](magnetic/base_station.csv) | [Classroom Labs · Magnetics](../apps/classroom-labs.html#magnetic) |
| Magnetics | Raw concealed-dyke profile | [`raw_dyke_profile.csv`](magnetic/raw_dyke_profile.csv) | [Classroom Labs · Magnetics](../apps/classroom-labs.html#magnetic) |
| Magnetics | Buried-vessel two-sensor difference profile (nT) | [`gradiometer_profile.csv`](magnetic/gradiometer_profile.csv) | [Classroom Labs · Magnetics](../apps/classroom-labs.html#magnetic) |
| Seismic | First-break travel times | [`first_breaks.csv`](seismic/first_breaks.csv) | [Seismic Refraction Lab](../lecture/seismic/apps/seismic-refraction.html) |
| Seismic | Three-layer first arrivals | [`three_layer_first_arrivals.csv`](seismic/three_layer_first_arrivals.csv) | [Classroom Labs · Seismic](../apps/classroom-labs.html#seismic) |
| Electrical | VES Schlumberger sounding | [`ves_sounding.csv`](electrical/ves_sounding.csv) | [3-Layer VES Forward Modeling](../lecture/electrical/apps/ert-2.html) |

### Using a Synthetic Dataset

=== "Download directly"

    Click the link in the table, then save the file. Open it in a spreadsheet or load it into the matching interactive tool.

=== "Load in Colab"

    ```python
    import pandas as pd
    url = "https://raw.githubusercontent.com/geohang/environmental-geophysics/main/docs/data/gravity/drift_readings.csv"
    df = pd.read_csv(url)
    df.head()
    ```

See the [Notebooks](../notebooks/index.md) page for ready-made Colab exercises that use these files.
