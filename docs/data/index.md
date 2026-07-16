# Field Data and Teaching Datasets

Course datasets are separated by provenance so students can see what was measured, what was derived, and what was generated for teaching. Two paths are kept distinct: real observations from the **[Ashton Prairie Living Laboratory (APLL)](../apps/field-data.html)** data hub and the explicitly synthetic **[Field Missions](../apps/field-missions.html)** and teaching CSVs below.

## Ashton Prairie Living Laboratory (APLL)

The **[Ashton Prairie Living Laboratory (APLL)](../apps/field-data.html)** data hub maps retained survey lines from the University of Iowa's [field site](https://sees.uiowa.edu/research/ashton-prairie). Individual survey points, synthetic map overlays, and the non-straight June 25 pre-processing ERT track are omitted. It includes layer controls, popups, a downloadable file catalog, and a companion [PyHydroGeophysX processing notebook](../notebooks/ashton_field_data.ipynb).

All 60 source files were checked. The public catalog contains 29 retained source files, 13 organized EM files, and 2 curated map products; redundant EM mirrors/intermediates and six problematic ERT measurement files are not published. The EM package keeps the full 24,212-row averaged in-phase/quadrature table as its processing input, provides separately named location tables for Profile 01–09, and places the valid layered inversion under `models/` as a derived result. The ERT teaching workflow uses only the positive-only April 11 Wenner and May 2 dipole–dipole PyGIMLi datasets. Thirteen zero-placeholder elevations on EM Profile 04 are replaced in the organized profile geometry and Web GIS by flagged IDW estimates; the external source archive remains unchanged.

!!! info "Map layers remain explicit"
    Survey lines show retained acquisition geometry, while processed EM resistivity and the survey footprint are labeled as derived products. Synthetic cases remain in the separate Field Missions activity rather than overlapping the real-data map. See the [data license](ashton/DATA_LICENSE.txt) and [machine-readable quality report](ashton/web/quality_report.json).

## Synthetic Field Data: Field Missions

The **[Field Missions](../apps/field-missions.html)** provide four guided, physically plausible investigations. Every mission is explicitly synthetic and is designed for method selection, signal prediction, interpretation, and discussion of limitations.

### Supporting Synthetic Teaching Data

The files below are clean synthetic examples that match the activities and notebooks, so every exercise works out of the box. They are not observations from Ashton Prairie.

#### By Module

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

#### Using a Synthetic Dataset

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
