# Environmental Geophysics

Open, interactive course materials for upper-level undergraduate environmental geophysics at the University of Iowa, taught by Dr. Hang Chen. Optional **Graduate Extension** cards add derivation, inversion, sensitivity, non-uniqueness, and uncertainty topics without interrupting the core learning path.

🌐 **Live site:** https://geohang.github.io/environmental-geophysics/

## What is here

- **8 chapter groups** covering foundations, gravity, magnetics, seismic, electrical/SP/IP, electromagnetic methods (including MT/CSEM), GPR, and borehole geophysics.
- **35 original interactive lecture and demonstration pages**, with shared navigation, responsive layouts, keyboard support, accessible controls, and explicit scientific assumptions.
- **Classroom Lab Studio**, with six course-tested workflows, five downloadable synthetic datasets, and a public processing-pipeline review challenge.
- **Active-Learning Lessons**, with short foundation slides, prediction, linked app exploration, formative practice, discussion, and exit tickets for every module.
- **Field Missions**, with four lightweight, explicitly synthetic environmental case studies.
- **Practice Lab**, with 45 formative questions tagged for Undergraduate, Graduate, or Both levels and immediate explanatory feedback.
- **4 notebooks** for gravity processing/modeling, seismic refraction, and ERT forward modeling, plus sample datasets.

The interactive lecture apps were migrated from the original Google Sites course site; the extraction script and verbatim copies are retained in `archive/` for provenance. Public activities use synthetic or instructional data unless a source is explicitly stated.

## Local development

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows; source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python scripts/audit_course.py
mkdocs serve
mkdocs build --strict
```

## Deployment

Every push to `main` runs the static course audit and a strict MkDocs build before publishing to GitHub Pages. In repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

## Repository layout

```text
docs/                      MkDocs content root
  index.md                 course home
  apps/                    course guide, classroom labs, missions, and practice lab
  lecture/<module>/        module page and interactive apps
  data/                    instructional datasets
  notebooks/               Colab-ready notebooks
scripts/audit_course.py    static accessibility and link audit
archive/                   source-site provenance materials
mkdocs.yml                 site configuration
```

The `instructor/` directory is intentionally excluded by `.gitignore`. It contains answer keys and formal examinations and must not be published.

## Citation

Use the repository’s `CITATION.cff` file or GitHub’s **Cite this repository** control. Suggested short citation:

> Chen, H. (2026). *Environmental Geophysics: Open Course Materials and Interactive Labs*. University of Iowa. https://github.com/geohang/environmental-geophysics

## Dual license

- Source code—including HTML/JavaScript applications, styles, scripts, and notebook code—is licensed under the **MIT License** (`LICENSE`).
- Original course text, figures, and educational data are licensed under **Creative Commons Attribution 4.0 International** (`LICENSE-CONTENT`).

Third-party assets and archived source material retain their original licenses and attribution requirements.
