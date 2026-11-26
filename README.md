# What Makes a World Model Causal? — ICLR 2027 blog draft

Repository-compatible content for the [ICLR 2027 blog-post template](https://github.com/iclr-blogposts/2027), plus lightweight zero-dependency preview scripts using the vendored ICLR 2027 `al-folio` Distill theme.

## Files

- `_posts/2027-04-30-what-makes-a-world-model-causal.md`: anonymised Distill-format post with table of contents, comparison table, Kramdown-safe `$$...$$` equations, `<d-footnote>`s, and `<d-cite>` citations.
- `assets/bibliography/2027-04-30-what-makes-a-world-model-causal.bib`: UTF-8 BibTeX bibliography.
- `assets/img/2027-04-30-what-makes-a-world-model-causal/`:
  - `tabletop-example.png`: tabletop manipulation task and entity-centric causal pipeline (downscaled from `Foundations-and-Trends-Causal-World-Models/nowfnt/figures/Table-top-example.png`).
  - `cwm-cid.svg`: vector causal influence diagram of CWM component interfaces and omitted-factor confounding (adapted from `fig:WM-CID` in `nowfnt/main.tex`).
  - `causal-ladder.png`: conceptual causal ladder of a CWM (downscaled from `Foundations-and-Trends-Causal-World-Models/nowfnt/figures/Causal_Ladder_of_World_Models.png`).
- `scripts/`: local rendering & preview server utilities (not needed for the ICLR submission fork):
  - `scripts/render.py`: compiles `_posts/*.md` into `_preview/index.html` using the vendored ICLR 2027 Distill CSS/JS and validates `<d-cite>` keys against the `.bib` file.
  - `scripts/serve.py`: builds `_preview/` and starts a local HTTP preview server (with optional `--watch` auto-rebuild).
  - `scripts/theme/`: minimal vendored ICLR 2027 `al-folio` Distill CSS and JS (`template.v2.js`, `transforms.v2.js`, `overrides.js`, `al-folio-distill.css`, `main.css`, `tailwind.css`, dark-mode toggle, MathJax setup).

## Local preview (render and start the server)

Requires only **Python 3** (standard library only; no Ruby/Jekyll installation needed).

1. **Render only** (writes `_preview/index.html`, gitignored):
   ```bash
   python3 scripts/render.py
   ```

2. **Render and start the local preview server**:
   ```bash
   python3 scripts/serve.py
   ```
   Then open **http://127.0.0.1:4173/** in your browser.

3. **Live-edit mode (auto-rebuild on save)**:
   ```bash
   python3 scripts/serve.py --watch
   ```
   Edit `_posts/2027-04-30-what-makes-a-world-model-causal.md` or the `.bib` file in your editor (`nano`, `vim`, etc.), save, and refresh the browser.

4. **Optional flags**:
   ```bash
   python3 scripts/serve.py --port 8000 --host 127.0.0.1
   python3 scripts/serve.py --no-build   # serve existing _preview/ without rebuilding
   ```

## Installation in the official ICLR 2027 template

Copy **only** `_posts/` and `assets/` into a fork of [iclr-blogposts/2027](https://github.com/iclr-blogposts/2027), preserving directory paths. The post uses Jekyll's `relative_url` filter for images and Kramdown-safe `$$...$$` for inline and display math. Do **not** copy `scripts/`, `_preview/`, `README.md`, or `.git/` into the official submission unless desired.

## Pre-submission checks

- **Double-blind anonymity:** Verify whether `tabletop-example.png` or `causal-ladder.png` already appear in any public preprint carrying author names before submitting under an anonymous track. `cwm-cid.svg` is a fresh vector adaptation.
- **Artwork polish (optional):** `causal-ladder.png` still labels *Interpreting* as "RUNG 1-2" and places *Prediction Model* in the top band; the blog caption clarifies both points explicitly (matching `nowfnt/main.tex`), or the source graphic can be edited directly.
- **Citation verification:** Double-check `balestriero2026counterfactual` (arXiv:2611.24778) and `namcausal` publication details, and run a final Jekyll build in your `iclr-blogposts/2027` fork before submitting.
