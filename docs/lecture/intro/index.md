# Introduction to Environmental Geophysics

Geophysics lets us image the subsurface without digging: every method measures a physical field at the surface and infers what property contrasts below could produce it. The central skill of this module is matching the right method to the right problem, because target depth, target size, and property contrast decide what is detectable.

## Interactive Lecture

<div class="grid cards" markdown>

-   🖥️ **[Geophysical Method & Spacing Simulator](apps/introduction.html)**

    ---

    Explore how survey geometry and method choice control what you can resolve at depth.

</div>

## Demo

<div class="grid cards" markdown>

-   ⚡ **[Depth of Investigation vs. Resolution Explorer](apps/demo-depth-resolution.html)**

    ---

    Compare the depth ranges and resolving power of gravity, magnetics, seismic, ERT, EM, and GPR side by side.

</div>

## Why This Matters: Hydrogeophysics

!!! tip "Turning geophysical images into hydrology"
    A resistivity or velocity image is only a means to an end. The goal in much of modern near-surface work is to watch water move through the subsurface: soil moisture, groundwater, and the weathered "critical zone" where rock becomes soil. Doing that means combining several methods and linking them to hydrological models.

    [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, is built for exactly this. It converts hydrological model outputs (MODFLOW, ParFlow) into ERT, seismic, and EM responses, and inverts field data back to water content.

    - [Hydrology to multi-method geophysics](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_hydro_to_multigeophys.ipynb): one workflow, several methods.

    Orientation reading: Binley et al. (2015) and Parsekian et al. (2015) on the [References](../../references.md) page.

## Keep Going

- 📚 Continue with [Gravity Methods](../gravity/index.md), the first method module.
- 🚀 Set up [Google Colab](../../notebooks/index.md) so you are ready for the notebook exercises.
