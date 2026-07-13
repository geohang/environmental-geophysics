# Data

Datasets for the course activities and notebooks are collected here. Each file is small enough to download directly or load straight into a Colab notebook.

!!! note "These are synthetic teaching datasets"
    The files below are clean synthetic examples that match the activities and notebooks, so every exercise works out of the box. Field datasets from the course will replace them as they are prepared.

## By Module

| Module | Dataset | Download | Used In |
|---|---|---|---|
| Gravity | Base-station drift readings | [`drift_readings.csv`](gravity/drift_readings.csv) | [Activity 1 · Drift Correction](../lecture/gravity/apps/activity-1.html) |
| Gravity | Sphere anomaly profile | [`anomaly_profile.csv`](gravity/anomaly_profile.csv) | [Activity 3 · Depth Detective](../lecture/gravity/apps/activity-3.html) |
| Seismic | First-break travel times | [`first_breaks.csv`](seismic/first_breaks.csv) | [Seismic Refraction Lab](../lecture/seismic/apps/seismic-refraction.html) |
| Electrical | VES Schlumberger sounding | [`ves_sounding.csv`](electrical/ves_sounding.csv) | [3-Layer VES Forward Modeling](../lecture/electrical/apps/ert-2.html) |

## Using a Dataset

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
