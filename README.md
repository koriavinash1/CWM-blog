# What Makes a World Model Causal? — ICLR 2027 blog draft

Repository-compatible content for the [ICLR 2027 blog-post template](https://github.com/iclr-blogposts/2027).

## Files

- `_posts/2027-04-30-what-makes-a-world-model-causal.md`: anonymised Distill-format post, with table of contents, comparison table, equations, footnotes, and `<d-cite>` citations.
- `assets/bibliography/2027-04-30-what-makes-a-world-model-causal.bib`: bibliography.
- `assets/img/2027-04-30-what-makes-a-world-model-causal/`:
  - `tabletop-example.png`: tabletop manipulation task and entity-centric causal pipeline (web-optimised from `Foundations-and-Trends-Causal-World-Models/nowfnt/figures/Table-top-example.png`).
  - `cwm-cid.svg`: vector causal influence diagram of CWM component interfaces and omitted-factor confounding (adapted from `fig:WM-CID` in `nowfnt/main.tex`).
  - `causal-ladder.png`: conceptual causal ladder of a CWM (web-optimised from `Foundations-and-Trends-Causal-World-Models/nowfnt/figures/Causal_Ladder_of_World_Models.png`).

## Installation in the official template

Copy `_posts/` and `assets/` into a fork of the official ICLR 2027 repository, preserving paths. The article uses root-relative image paths, so the figures must be copied along with the Markdown and bibliography. Do not copy this README or `.git/` into the official submission unless desired.

## Pre-submission checks

- **Double-blind anonymity:** Verify whether `tabletop-example.png` or `causal-ladder.png` already appear in any public preprint carrying author names before submitting under an anonymous track.
- **Artwork polish (optional):** `causal-ladder.png` still labels *Interpreting* as "RUNG 1-2" and places *Prediction Model* in the top band; the blog caption clarifies both points explicitly (matching `nowfnt/main.tex`), or the source graphic can be edited directly.
- **Citation verification:** Double-check `balestriero2026counterfactual` (arXiv:2611.24778) and `namcausal` publication details, and run a full Jekyll/Distill local build to verify math, `<d-footnote>`, and SVG rendering.
