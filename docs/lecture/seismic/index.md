# Seismic Methods

Seismic waves travel at speeds set by the elastic moduli and density of the material they cross, so travel times carry structural information. Near-surface work leans on the refraction method: head waves from faster layers below overtake direct arrivals and reveal layer depths and velocities.

## Learning Objectives

**Undergraduate Core:** By the end of this module, you will be able to:

- Relate stress, strain, elastic moduli, density, and P- and S-wave velocity.
- Read slopes, intercept time, and crossover distance from a refraction travel-time plot.
- Recover a two-layer velocity model and interface depth under the planar-layer assumption.
- Recognize low-velocity-layer blindness, lateral variation, and first-break picking uncertainty.

??? abstract "Graduate Extension"
    Compare intercept-time interpretation with refraction tomography, reciprocal acquisition, regularization, resolution, and uncertainty analysis.

[Practice this module](../../apps/practice-lab.html#seismic){ .md-button }

## Topic Apps

<div class="grid cards" markdown>

-   🖥️ **[Elasticity: The Basis of Seismic Waves](apps/stress-and-strain.html)**

    ---

    Stress, strain, and the elastic moduli that set P- and S-wave velocities.

-   🖥️ **[Seismic Refraction Lab](apps/seismic-refraction.html)**

    ---

    Acquire and interpret a refraction survey over a layered subsurface.

</div>

## Demo

<div class="grid cards" markdown>

-   ⚡ **[Refraction Travel-Time Curve Builder](apps/demo-refraction-traveltime.html)**

    ---

    Adjust layer velocities and thickness in a two-layer earth and see the direct wave, head wave, crossover distance, and intercept time update live.

</div>

## Research Code: PyHydroGeophysX

!!! tip "Seismic refraction and joint inversion"
    The travel-time picking and interpretation you practice here scale up to full seismic refraction tomography (SRT). [PyHydroGeophysX](https://github.com/geohang/PyHydroGeophysX) provides SRT forward modeling and inversion, rock-physics velocity models (Hertz-Mindlin, differential effective medium), and joint ERT plus seismic inversion so the two methods constrain one shared subsurface model.

    - [SRT forward modeling](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/EX_SRT_forward.ipynb): build travel times from a velocity model.
    - [SRT inversion](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_SRT_inv.ipynb): recover velocity structure from picks.
    - [Joint ERT + seismic inversion](https://colab.research.google.com/github/geohang/PyHydroGeophysX/blob/main/examples/Ex_joint_inversion.ipynb): couple resistivity and velocity.

## Data and Notebooks

- 📊 Datasets live in the [Data area](../../data/index.md).
- 🚀 Python exercises are in [Notebooks](../../notebooks/index.md).
