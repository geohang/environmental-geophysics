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

## Learning Path

Work through the apps in order. Each one opens full screen; the bar at its top shows this path and has Prev and Next buttons.

<div class="learning-path" markdown>

1.  **[Gravity Exploration & Data Reduction](apps/gravity-methods.html)** <span class="lp-type">Interactive lecture</span>

    The geoid, the latitude effect, and the corrections that turn gravimeter readings into a Bouguer anomaly, with a calculator for each step.

2.  **[Activity 1 · Drift Correction Loop](apps/activity-1.html)** <span class="lp-type">Activity</span>

    Build a drift curve from repeated base-station readings and correct a field loop.

3.  **[Activity 2 · Cross-Section Challenge](apps/activity-2.html)** <span class="lp-type">Activity</span>

    Reduce the readings at four stations (latitude, free-air, and Bouguer corrections) to reveal a hidden structure.

4.  **[Buried-Body Gravity Anomaly Modeler](apps/demo-anomaly-modeler.html)** <span class="lp-type">Demo</span>

    Drag a sphere or horizontal cylinder in the subsurface, set its density contrast, and watch the surface anomaly respond in real time.

5.  **[Activity 3 · Depth Detective](apps/activity-3.html)** <span class="lp-type">Activity</span>

    Use anomaly shape rules (half-width, amplitude) to estimate source depth and geometry.

</div>

**How the depth apps connect.** The half-width depth rule appears three times in this module, each with a different job. The Depth Estimator at the end of app 1 introduces the rule, the Anomaly Modeler (app 4) shows the half-width growing as a body moves deeper, and Activity 3 asks you to apply it to an unknown target. [Magnetic Interpretation Methods](../magnetic/apps/depth-estimation.html) in the next module uses the same idea for dipole sources, where the depth factors differ.

**After the path:** [practice questions](../../apps/practice-lab.html#gravity) · [classroom lab](#classroom-lab) · [data and notebooks](#data-and-notebooks).

## Classroom Lab

🧰 **[Microgravity search for a limestone cavity](../../apps/classroom-labs.html#gravity)** — reduce a full base-loop dataset, document correction signs, estimate an idealized source depth, and write a qualified engineering recommendation.

## Research Code: PyHydroGeophysX

!!! tip "Potential-field inversion"
    Gravity and magnetic data can be inverted together for subsurface density and susceptibility structure. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, includes a [gravity and magnetics inversion example (source)](https://github.com/geohang/PyHydroGeophysX/blob/main/examples/Ex_gravity_magnetics_inversion.py) alongside its electrical, seismic, and EM tools.

## Data and Notebooks

- 📊 Activity datasets live in the [Data area](../../data/index.md).
- 🚀 A Colab notebook version of the drift-correction exercise is in [Notebooks](../../notebooks/index.md).
