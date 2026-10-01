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

## Learning Path

Work through the apps in order. Each one opens full screen; the bar at its top shows this path and has Prev and Next buttons.

<div class="learning-path" markdown>

1.  **[How Do Rocks Conduct Electricity?](apps/electrical-methods.html)** <span class="lp-type">Interactive lecture</span>

    Electrolytic and electronic conduction, and dielectric polarization: how charges move or polarize in earth materials.

2.  **[ERT · Geometric Factor K](apps/ert.html)** <span class="lp-type">Interactive lecture</span>

    Geometric factors of the Wenner, Schlumberger, and dipole–dipole arrays, and why a larger K means a smaller measured voltage.

3.  **[VES · 3-Layer Forward Model](apps/ert-2.html)** <span class="lp-type">Interactive lecture</span>

    Build layered models and generate vertical electrical sounding curves.

4.  **[Apparent-Resistivity Pseudosection Builder](apps/demo-pseudosection.html)** <span class="lp-type">Demo</span>

    Place a conductive or resistive body in the subsurface, pick an array, and build the pseudosection measurement by measurement.

5.  **[SP · Signal Mechanisms](apps/sp.html)** <span class="lp-type">Interactive lecture</span>

    Streaming, mineralization (redox), and thermoelectric sources of self-potential signals.

6.  **[SP · Field Applications](apps/sp-2.html)** <span class="lp-type">Activity</span>

    Survey a sulfide ore body, a leaking dam, and a geothermal upflow with a virtual SP sensor.

7.  **[IP · Signal Mechanisms](apps/ip.html)** <span class="lp-type">Interactive lecture</span>

    Membrane and electrode polarization at the pore scale, and the decaying voltage they leave when the current switches off.

8.  **[IP · Cole-Cole Model](apps/ip-2.html)** <span class="lp-type">Interactive lecture</span>

    Explore how Cole-Cole parameters shape the complex-resistivity spectrum.

</div>

**After the path:** [practice questions](../../apps/practice-lab.html#electrical) · [classroom lab](#classroom-lab) · [data and notebooks](#data-and-notebooks).

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
