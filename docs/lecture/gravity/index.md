# Gravity Methods

Lateral density contrasts in the subsurface produce tiny variations in gravitational acceleration, on the order of parts per million of \(g\). Gravity surveying measures those variations, strips away every predictable effect (instrument drift, tides, latitude, elevation, terrain), and interprets what remains as geology.

## Learning Objectives

**Undergraduate Core:** By the end of this module, you will be able to:

- Relate anomaly sign and amplitude to density contrast and source geometry.
- Apply drift, latitude, free-air, Bouguer, and terrain corrections with consistent units and signs.
- Estimate idealized source depth from a half-width measurement.
- Explain why multiple density models can fit the same gravity anomaly.

??? abstract "Graduate Extension"
    Evaluate regional–residual separation, parameter trade-offs, equivalent-source behavior, and uncertainty in density-contrast inversion.

[Practice this module](../../apps/practice-lab.html#gravity){ .md-button }
[Teach with active-learning slides](../../apps/lecture-frameworks.html#gravity){ .md-button }

## Interactive Lecture

<div class="grid cards" markdown>

-   🖥️ **[Complete Gravity Exploration & Data Reduction](apps/gravity-methods.html)**

    ---

    The full workflow from raw gravimeter readings to a Bouguer anomaly map, with each correction explained.

</div>

## Activities

<div class="grid cards" markdown>

-   🧪 **[Activity 1 · Advanced Gravity Drift Correction](apps/activity-1.html)**

    ---

    Build a drift curve from repeated base-station readings and correct a field loop.

-   🧪 **[Activity 2 · Gravity Lab: The Cross-Section Challenge](apps/activity-2.html)**

    ---

    Match observed anomaly profiles to candidate subsurface cross sections.

-   🧪 **[Activity 3 · Gravity Geometry: Subsurface Depth Detective](apps/activity-3.html)**

    ---

    Use anomaly shape rules (half-width, amplitude) to estimate source depth and geometry.

</div>

## Demo

<div class="grid cards" markdown>

-   ⚡ **[Buried-Body Anomaly Modeler](apps/demo-anomaly-modeler.html)**

    ---

    Drag a sphere or horizontal cylinder in the subsurface, set its density contrast, and watch the surface anomaly respond in real time.

</div>

## Classroom Lab

🧰 **[Microgravity search for a limestone cavity](../../apps/classroom-labs.html#gravity)** — reduce a full base-loop dataset, document correction signs, estimate an idealized source depth, and write a qualified engineering recommendation.

## Research Code: PyHydroGeophysX

!!! tip "Potential-field inversion"
    Gravity and magnetic data can be inverted together for subsurface density and susceptibility structure. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, includes a [gravity and magnetics inversion example (source)](https://github.com/geohang/PyHydroGeophysX/blob/main/examples/Ex_gravity_magnetics_inversion.py) alongside its electrical, seismic, and EM tools.

## Data and Notebooks

- 📊 Activity datasets live in the [Data area](../../data/index.md).
- 🚀 A Colab notebook version of the drift-correction exercise is in [Notebooks](../../notebooks/index.md).
