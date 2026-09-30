# Magnetic Methods

Rocks acquire magnetization from magnetic minerals, magnetite above all, and that magnetization perturbs the geomagnetic field measured at the surface. Because the inducing field is inclined, magnetic anomalies change shape with latitude, which makes interpretation richer than gravity even though the survey practice is faster.

## Learning Objectives

**Undergraduate Core:** By the end of this module, you will be able to:

- Distinguish induced magnetization, remanent magnetization, and magnetic susceptibility.
- Predict how inclination, source depth, and observation height affect anomaly shape.
- Explain upward continuation, simple depth rules, and reduction to the pole (RTP).
- Identify when cultural noise or remanence makes a simple interpretation unreliable.

??? abstract "Graduate Extension"
    Assess the assumptions and instability of continuation, RTP, and source-depth estimators, especially at low inclination and for remanently magnetized bodies.

[Practice this module](../../apps/practice-lab.html#magnetic){ .md-button }
[Teach with active-learning slides](../../apps/lecture-frameworks.html#magnetic){ .md-button }

## Learning Path

Work through the apps in order. Each one opens full screen; the bar at its top shows this path and has Prev and Next buttons.

<div class="learning-path" markdown>

1.  **[GeoMag Lab: Rock Magnetism](apps/magnetic-methods.html)** <span class="lp-type">Activity</span>

    Induced and remanent magnetization as vectors, the Königsberger ratio, and five guided tasks.

2.  **[Dipole Anomaly vs. Inclination](apps/demo-dipole-inclination.html)** <span class="lp-type">Demo</span>

    Move the same buried dipole from the magnetic equator to the pole and watch the anomaly change from asymmetric to symmetric.

3.  **[Geomagnetic Anomaly Simulator](apps/magnetic-signal.html)** <span class="lp-type">Interactive lecture</span>

    How buried magnetic bodies express themselves in total-field data.

4.  **[Continuation Simulator](apps/continuation.html)** <span class="lp-type">Interactive lecture</span>

    Upward and downward continuation as wavelength filtering of a magnetic profile.

5.  **[Magnetic Interpretation Methods](apps/depth-estimation.html)** <span class="lp-type">Interactive lecture</span>

    Half-width depth rules, Peters' half-slope method, and reduction to the pole.

</div>

**After the path:** [practice questions](../../apps/practice-lab.html#magnetic) · [classroom lab](#classroom-lab) · [data and notebooks](#data-and-notebooks).

## Classroom Lab

🧰 **[Concealed dyke and buried-vessel profiles](../../apps/classroom-labs.html#magnetic)** — interpolate a base station, remove diurnal and regional fields, compare total-field and gradient data, and frame a safe target recommendation.

## Data and Notebooks

- 📊 Datasets live in the [Data area](../../data/index.md).
- 🚀 Python exercises are in [Notebooks](../../notebooks/index.md).

??? info "PyHydroGeophysX Research Code"
    Gravity and magnetic observations can be inverted together for subsurface density and susceptibility structure. [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX), developed in Dr. Chen's group, includes a [gravity and magnetics inversion example (source)](https://github.com/geohang/PyHydroGeophysX/blob/main/examples/Ex_gravity_magnetics_inversion.py) alongside its electrical, seismic, and electromagnetic workflows.
