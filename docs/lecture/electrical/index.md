# Electrical Methods

Electrical resistivity spans more orders of magnitude than any other rock property, which makes current-based methods the workhorses of environmental geophysics. This module covers galvanic resistivity surveying (VES and ERT), the passive self-potential (SP) method, and induced polarization (IP).

## Learning Objectives

**Undergraduate Core:** By the end of this module, you will be able to:

- Explain electrolytic conduction and the roles of saturation, salinity, porosity, clay, and temperature.
- Calculate geometric factors and distinguish true, apparent, and inverted resistivity.
- Compare Wenner, Schlumberger, and dipole–dipole survey behavior.
- Distinguish ERT, SP, and IP mechanisms and avoid treating any response as a unique hydrologic property.

??? abstract "Graduate Extension"
    Examine sensitivity functions, regularization, equivalence, Cole–Cole conventions, and uncertainty in petrophysical conversion from resistivity to water content.

[Practice this module](../../apps/practice-lab.html#electrical){ .md-button }
[Teach with active-learning slides](../../apps/lecture-frameworks.html#electrical){ .md-button }

## Interactive Lecture

<div class="grid cards" markdown>

-   🖥️ **[How Do Rocks Conduct Electricity?](apps/electrical-methods.html)**

    ---

    Electrolytic conduction, Archie's law, and what controls formation resistivity.

</div>

## Topic Apps

<div class="grid cards" markdown>

-   🖥️ **[ERT · Geometric Factor K for Common Arrays](apps/ert.html)**

    ---

    Wenner, Schlumberger, and dipole-dipole geometries and their sensitivity.

-   🖥️ **[ERT · 3-Layer VES Forward Modeling](apps/ert-2.html)**

    ---

    Build layered models and generate vertical electric sounding curves.

-   🖥️ **[SP · Signal Mechanisms](apps/sp.html)**

    ---

    Streaming, diffusion, and mineral potentials behind self-potential signals.

-   🖥️ **[SP · Method Applications](apps/sp-2.html)**

    ---

    Seepage detection, contaminant plumes, and other SP use cases.

-   🖥️ **[IP · Signal Mechanisms](apps/ip.html)**

    ---

    Membrane and electrode polarization, chargeability, and time- vs. frequency-domain IP.

-   🖥️ **[IP · Cole-Cole Model Interactive](apps/ip-2.html)**

    ---

    Explore how Cole-Cole parameters shape the complex-resistivity spectrum.

</div>

## Demo

<div class="grid cards" markdown>

-   ⚡ **[Apparent-Resistivity Pseudosection Builder](apps/demo-pseudosection.html)**

    ---

    Place a conductive or resistive body in the subsurface, pick an array, and build the pseudosection measurement by measurement.

</div>

## Classroom Lab

🧰 **[Three-layer VES group investigation](../../apps/classroom-labs.html#electrical)** — divide into curve-type, suppression, and equivalence teams, then explain why apparent resistivity and electrode spacing are not a literal depth section.

## Research Code: PyHydroGeophysX

!!! tip "From resistivity to water content"
    The petrophysics in this module (Archie's law, and its clay-corrected cousin the Waxman-Smits model) is exactly how field ERT becomes hydrology. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, implements these transforms together with full 2D and 3D ERT forward modeling and inversion, including time-lapse and structure-constrained inversion for watershed monitoring.

    - [Full ERT workflow](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_ERT_workflow.ipynb): mesh, forward model, invert.
    - [Time-lapse ERT inversion](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_TL_inversion.ipynb): track moisture change over time.
    - [Structure-constrained inversion](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_Structure_resinv.ipynb): sharpen boundaries using seismic structure.

    Background reading: Archie (1942), Loke et al. (2013), and Binley & Slater (2020) on the [References](../../references.md) page.

## Data and Notebooks

- 📊 Datasets live in the [Data area](../../data/index.md).
- 🚀 Python exercises (including pyGIMLi-based forward modeling) are in [Notebooks](../../notebooks/index.md).
