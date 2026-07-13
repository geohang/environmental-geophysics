# Notebooks

These Python notebooks run in [Google Colab](https://colab.research.google.com/) with no local installation. Click a **Open in Colab** badge to launch, then run the cells top to bottom. Each notebook mirrors an interactive activity on the site and lets you take the analysis further with real code.

!!! tip "Getting started with Colab"
    A free Google account is all you need. Colab gives you a Python environment in the browser; the first cell of each notebook installs any geophysics packages it needs (for example `pygimli` or `pyhydrogeophysX`).

## Available Notebooks

| Notebook | Topic | Launch |
|---|---|---|
| `gravity_drift_correction.ipynb` | Build a drift curve and correct a gravity loop | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/environmental-geophysics/blob/main/docs/notebooks/gravity_drift_correction.ipynb) |
| `gravity_forward_model.ipynb` | Forward-model the anomaly of a buried sphere | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/environmental-geophysics/blob/main/docs/notebooks/gravity_forward_model.ipynb) |
| `seismic_refraction.ipynb` | Pick first breaks and invert a two-layer model | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/environmental-geophysics/blob/main/docs/notebooks/seismic_refraction.ipynb) |
| `ert_forward_model.ipynb` | Forward-model an ERT pseudosection with pyGIMLi | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/environmental-geophysics/blob/main/docs/notebooks/ert_forward_model.ipynb) |

!!! note "More notebooks are on the way"
    Additional exercises for magnetics, EM, GPR, MT, and borehole logs are being added. The badges above will go live as each notebook lands in the repository.

## Related Software

The notebooks build on open-source tools developed and used in the [SHIP Lab](https://github.com/geohang):

- **[PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX)** integrates hydrological model outputs with geophysical forward modeling.
- **[pyGIMLi](https://www.pygimli.org/)** provides forward modeling and inversion for ERT, seismics, and more.
