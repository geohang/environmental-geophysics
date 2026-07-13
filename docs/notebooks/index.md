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

## Research Code: PyHydroGeophysX

The course tools are teaching versions of a real research package. [**PyHydroGeophysX**](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, integrates hydrological model outputs (MODFLOW, ParFlow) with geophysical forward modeling and inversion across ERT, seismic, and EM methods. Its example notebooks run in Colab, and its documentation is at [geohang.github.io/PyHydroGeophysX](https://geohang.github.io/PyHydroGeophysX/).

!!! warning "These examples need the geophysics dependencies"
    Unlike the teaching notebooks above, the PyHydroGeophysX examples install heavier libraries (pyGIMLi, SimPEG). In the first Colab cell run:
    ```bash
    !pip install "pyhydrogeophysx[geophysics]"
    ```

| Example | Method | Launch |
|---|---|---|
| `Ex_hydro_to_multigeophys` | Hydrology → ERT/seismic/EM | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_hydro_to_multigeophys.ipynb) |
| `Ex_ERT_workflow` | ERT forward + inversion | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_ERT_workflow.ipynb) |
| `Ex_TL_inversion` | Time-lapse ERT | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_TL_inversion.ipynb) |
| `Ex_SRT_inv` | Seismic refraction tomography | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_SRT_inv.ipynb) |
| `Ex_joint_inversion` | Joint ERT + seismic | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_joint_inversion.ipynb) |
| `Ex_TDEM_workflow` | Time-domain EM | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_TDEM_workflow.ipynb) |

To cite the package, see the [References](../references.md) page. It also builds on [pyGIMLi](https://www.pygimli.org/) (Rücker et al., 2017) for mesh generation, forward modeling, and inversion.
