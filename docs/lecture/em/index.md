# Electromagnetic Methods

Electromagnetic induction lets us sense subsurface conductivity without ground contact: a transmitter coil drives currents in the earth, and a receiver measures the secondary field those currents produce. Frequency-domain (FDEM) and time-domain (TEM) systems trade depth, resolution, and productivity in different ways.

## Interactive Lecture

<div class="grid cards" markdown>

-   🖥️ **[EM System Animation Activity](apps/electromagnetic-methods.html)**

    ---

    How transmitter, ground response, and receiver interact in an EM system.

-   🖥️ **[EM Waveforms Animation Activity](apps/electromagnetic-methods-2.html)**

    ---

    Primary and secondary fields, in-phase and quadrature components, and TEM decay.

</div>

## Topic Apps

<div class="grid cards" markdown>

-   🖥️ **[Interactive 1D EM Forward Modeling](apps/fdem-tem.html)**

    ---

    Model FDEM and TEM responses over layered conductivity structures.

</div>

## Demo

<div class="grid cards" markdown>

-   ⚡ **[Skin Depth Calculator & Visualizer](apps/demo-skin-depth.html)**

    ---

    See how frequency and ground conductivity set the penetration of EM fields, with the classic skin-depth formula evaluated live.

</div>

## Research Code: PyHydroGeophysX

!!! tip "FDEM and TEM forward modeling and inversion"
    The induction principles here carry directly into quantitative EM modeling. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX) wraps SimPEG to run frequency-domain (FDEM) and time-domain (TDEM) forward modeling and inversion over layered and 2D conductivity structures.

    - [TDEM workflow](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_TDEM_workflow.ipynb): transient decay and inversion (runs in Colab).
    - [FDEM workflow (source)](https://github.com/geohang/PyHydroGeophysX/blob/main/examples/Ex_FDEM_workflow.py): frequency-domain response and inversion.

## Data and Notebooks

- 📊 Datasets live in the [Data area](../../data/index.md).
- 🚀 Python exercises are in [Notebooks](../../notebooks/index.md).
