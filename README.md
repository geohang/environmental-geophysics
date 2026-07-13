# SEES:4800 · Environmental Geophysics

Interactive course website for **SEES:4800 Environmental Geophysics** at the University of Iowa, taught by Dr. Hang Chen. Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and deployed to GitHub Pages.

🌐 **Live site:** https://geohang.github.io/environmental-geophysics/

## What is here

- **9 method modules** (introduction, gravity, magnetic, seismic, electrical, electromagnetic, GPR, magnetotellurics, borehole), each with interactive browser lectures, activities, and a hands-on demo.
- **10 original interactive demos** (`docs/lecture/*/apps/demo-*.html`): self-contained HTML/JS tools such as a gravity anomaly modeler, a seismic refraction travel-time builder, a 1D magnetotelluric sounding explorer, and an apparent-resistivity pseudosection builder.
- **Colab notebooks** (`docs/notebooks/`) for drift correction, gravity and ERT forward modeling, and refraction interpretation.
- **Sample datasets** (`docs/data/`) that match the activities and notebooks.

The interactive lecture apps were migrated from the original Google Sites course site; the extraction script and verbatim copies are kept in `archive/` for provenance.

## Local development

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
mkdocs serve                # preview at http://127.0.0.1:8000
mkdocs build --strict       # production build into site/
```

## Deployment

Every push to `main` triggers `.github/workflows/deploy.yml`, which builds the site with `mkdocs build --strict` and publishes it to GitHub Pages. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

## Repository layout

```
docs/                      MkDocs content root
  index.md                 course home
  lecture/<module>/        module page + apps/ (interactive lectures + demos)
  data/                    sample datasets
  notebooks/               Colab-ready notebooks
scripts/extract_site.py    one-time Google Sites extraction
archive/                   verbatim extracted apps + inventory.json
mkdocs.yml                 site configuration
```

## License

Course materials © 2026 Hang Chen. Interactive tools may be reused for teaching with attribution.
