# Build Summary — Environmental Geophysics Course Site

Date: 2026-07-13
Target repo: `geohang/environmental-geophysics` → https://geohang.github.io/environmental-geophysics/
Local path: `Documents/GitHub/environmental-geophysics`

## What was created

**Migration from Google Sites.** `scripts/extract_site.py` fetched all 24 pages of the
original Google Site and pulled the interactive HTML apps out of the Google Sites embed
widgets. 23 self-contained lecture/activity apps were recovered (2 pages, the Lecture and
Seismic Methods index pages, were empty shells on the source and became module landing
pages instead). Verbatim copies and `inventory.json` are in `archive/` for provenance.

**MkDocs Material site.** Home page, a Lectures overview, and nine module pages
(introduction, gravity, magnetic, seismic, electrical, electromagnetic, GPR,
magnetotellurics, borehole). Light/dark toggle, search, and top-tab navigation. The
site name fixes the "Enviromental" typo from the source.

**Ten new interactive demos** (`docs/lecture/*/apps/demo-*.html`), one per module, in the
same dark visual language as the migrated apps. All physics was verified in-browser:

| Demo | Verified result |
|---|---|
| Gravity buried-body modeler | sphere peak 0.0124 mGal; half-width depth rules exact |
| Depth vs. resolution explorer | method ranges correct (at 2 km, only gravity/mag/MT) |
| Magnetic dipole vs. inclination | equator→pole anomaly transition, no errors |
| Seismic refraction builder | intercept 18.9 ms, depth recovery 8.0 m exact |
| ERT pseudosection builder | 154 measurements, ρa 21–100 Ω·m over conductive block |
| EM skin depth | 159.1 m at 1 kHz / 100 Ω·m (exact) |
| GPR hyperbola estimator | εr 6.3 at true velocity, match feedback works |
| MT 1D sounding | uniform half-space → ρa 100 Ω·m, phase 45° (exact) |
| Borehole log response | 5-layer builder, live GR/Res/NPHI/RHOB curves |

**Notebooks and data.** Four Colab-ready notebooks (`docs/notebooks/`) with badges, and
four synthetic teaching datasets (`docs/data/`) matching the activities.

**CI/CD.** `.github/workflows/deploy.yml` builds with `mkdocs build --strict` and deploys
to GitHub Pages using Node.js-24 action majors (checkout@v5, setup-python@v6).

## QA passed

- `mkdocs build --strict`: clean (no broken links, no missing files).
- All 10 demos: correct physics, canvas rendering, zero console errors.
- Extracted apps: content preserved, MathJax renders, injected back-links resolve.
- Search index: 51 documents. Mobile (375px): no horizontal overflow.

## Not yet done (needs your approval / input)

1. **git commit + GitHub repo create + push + Pages enablement** — staged locally, waiting
   on approval (per Git Safety rule).
2. **Real field datasets** — the four CSVs are synthetic placeholders you can replace.
3. **Cutover** — add a link on the Google Sites home pointing to the new URL once live.
