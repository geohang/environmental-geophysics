# Electromagnetic Methods

Electromagnetic induction lets us sense subsurface conductivity without ground contact: a transmitter coil drives currents in the earth, and a receiver measures the secondary field those currents produce. Frequency-domain (FDEM) and time-domain (TEM) systems trade depth, resolution, and productivity in different ways.

## Learning Objectives

**Undergraduate Core:** By the end of this module, you will be able to:

- Explain primary-field induction, secondary currents, and receiver response.
- Relate frequency, conductivity, time gate, and skin or diffusion depth qualitatively.
- Compare FDEM and TEM acquisition and select an appropriate system for a target.
- Identify coupling, cultural noise, and limits of apparent-conductivity interpretation.

??? abstract "Graduate Extension"
    Distinguish qualitative diffusion-depth proxies from Maxwell-equation forward models and evaluate sensitivity, equivalence, and inversion regularization.

[Practice this module](../../apps/practice-lab.html#em){ .md-button }
[Teach with active-learning slides](../../apps/lecture-frameworks.html#em){ .md-button }

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

## Classroom Lab

🧰 **[FDEM plume triage and TEM bedrock comparison](../../apps/classroom-labs.html#em)** — use diffusion-depth teaching proxies to make survey decisions, then identify the assumptions that require a full forward model.

## Deep EM Extension

<div class="grid cards" markdown>

-   🌍 **[Magnetotellurics and Deep EM](../mt/index.md)**

    ---

    Continue from controlled-source FDEM/TEM to natural-source MT, tensor impedance, apparent resistivity, phase, static shift, dimensionality, and deep-crustal interpretation.

</div>

## Research Code: PyHydroGeophysX

!!! tip "FDEM and TEM forward modeling and inversion"
    The induction principles here carry directly into quantitative EM modeling. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX) wraps SimPEG to run frequency-domain (FDEM) and time-domain (TDEM) forward modeling and inversion over layered and 2D conductivity structures.

    - [TDEM workflow](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_TDEM_workflow.ipynb): transient decay and inversion (runs in Colab).
    - [FDEM workflow (source)](https://github.com/geohang/PyHydroGeophysX/blob/main/examples/Ex_FDEM_workflow.py): frequency-domain response and inversion.

## Data and Notebooks

- 📊 Datasets live in the [Data area](../../data/index.md).
- 🚀 Python exercises are in [Notebooks](../../notebooks/index.md).
