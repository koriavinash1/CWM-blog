#!/usr/bin/env python3
"""Render the Distill-format ICLR 2027 markdown post into _preview/ using the
vendored ICLR 2027 al-folio Distill theme (zero external Python dependencies)."""

from __future__ import annotations

import argparse
from datetime import datetime
import html
import json
import os
from pathlib import Path
import re
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POST = REPO_ROOT / "_posts" / "2027-04-30-what-makes-a-world-model-causal.md"
DEFAULT_OUT = REPO_ROOT / "_preview"
THEME_DIR = REPO_ROOT / "scripts" / "theme"


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9\s-]", "", text.lower()).strip()
    return re.sub(r"[\s-]+", "-", s)


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Markdown file is missing YAML frontmatter delimited by '---'.")
    fm_text, body = parts[1].strip(), parts[2].strip()
    meta: dict = {"toc": [], "authors": []}
    section = None
    for line in fm_text.splitlines():
        if re.match(r"^(title|description|date|bibliography):\s*", line):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
            section = None
        elif line.startswith("authors:"):
            section = "authors"
        elif line.startswith("toc:"):
            section = "toc"
        elif section == "authors" and "- name:" in line:
            meta["authors"].append(
                {
                    "author": line.split(":", 1)[1].strip(),
                    "authorURL": "",
                    "affiliations": [{"name": "", "url": ""}],
                }
            )
        elif section == "toc" and "- name:" in line:
            meta["toc"].append(line.split(":", 1)[1].strip())
    return meta, body


def format_published_date(raw_date: str) -> str:
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        return raw_date


def format_inline(text: str) -> str:
    placeholders: list[str] = []

    def stash_raw(val: str) -> str:
        idx = len(placeholders)
        placeholders.append(val)
        return f"\x00PH{idx}\x00"

    def stash_inline_math(m: re.Match) -> str:
        inner = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return stash_raw(f"\\({inner}\\)")

    # Kramdown inline math $$...$$, \(...\), or fallback $...$
    text = re.sub(r"\$\$([^\n]+?)\$\$", stash_inline_math, text)
    text = re.sub(r"\\\((.+?)\\\)", stash_inline_math, text)
    text = re.sub(r"(?<!\$)\$(?!\$)([^\n$]+?)(?<!\$)\$(?!\$)", stash_inline_math, text)
    # Protect inline HTML tags (<d-cite>, <d-footnote>, <em>, etc.)
    text = re.sub(r"<[^>]+>", lambda m: stash_raw(m.group(0)), text)

    text = re.sub(
        r"`([^`]+)`",
        lambda m: f'<code class="language-plaintext highlighter-rouge">{html.escape(m.group(1))}</code>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    for idx, val in enumerate(placeholders):
        text = text.replace(f"\x00PH{idx}\x00", val)
    return text


def md_to_html(body: str) -> str:
    # Resolve Liquid relative_url filter to site-root /assets/...
    body = re.sub(
        r"\{\{\s*'(/assets/[^']+)'\s*\|\s*relative_url\s*\}\}",
        r"\1",
        body,
    )

    lines = body.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # HTML comment block
        if stripped.startswith("<!--"):
            buf = [line]
            while i < n and "-->" not in lines[i]:
                i += 1
                if i < n:
                    buf.append(lines[i])
            i += 1
            out.append("\n".join(buf))
            continue

        # Multi-line display math $$ ... $$
        if stripped == "$$":
            buf = []
            i += 1
            while i < n and lines[i].strip() != "$$":
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1
            math_body = "\n".join(buf).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f"\\[{math_body}\\]")
            continue

        # Single-line display math $$...$$ on its own paragraph
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            math_body = stripped[2:-2].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f"\\[{math_body}\\]")
            i += 1
            continue

        # Raw HTML block (<div ...>...</div>)
        if stripped.startswith("<div"):
            buf = [line]
            depth = line.count("<div") - line.count("</div>")
            i += 1
            while i < n and depth > 0:
                buf.append(lines[i])
                depth += lines[i].count("<div") - lines[i].count("</div>")
                i += 1
            out.append("\n".join(buf))
            continue

        # Headings
        if stripped.startswith("## "):
            title = stripped[3:].strip()
            out.append(f'<h2 id="{slugify(title)}">{format_inline(title)}</h2>')
            i += 1
            continue
        if stripped.startswith("### "):
            title = stripped[4:].strip()
            out.append(f'<h3 id="{slugify(title)}">{format_inline(title)}</h3>')
            i += 1
            continue

        # GFM Table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tbl = ["<table>", "  <thead>", "    <tr>"]
            for h in headers:
                tbl.append(f"      <th>{format_inline(h.replace('&', '&amp;'))}</th>")
            tbl.extend(["    </tr>", "  </thead>", "  <tbody>"])
            for r in rows:
                tbl.append("    <tr>")
                for c in r:
                    tbl.append(f"      <td>{format_inline(c)}</td>")
                tbl.append("    </tr>")
            tbl.extend(["  </tbody>", "</table>"])
            out.append("\n".join(tbl))
            continue

        # Blockquote
        if stripped.startswith(">"):
            bq_lines = []
            while i < n and lines[i].strip().startswith(">"):
                bq_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            inner_html = md_to_html("\n".join(bq_lines))
            out.append(f"<blockquote>\n{inner_html}\n</blockquote>")
            continue

        # Unordered list
        if re.match(r"^-\s+", stripped):
            items = []
            while i < n and re.match(r"^-\s+", lines[i].strip()):
                items.append(re.sub(r"^-\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>\n" + "\n".join(f"  <li>{format_inline(it)}</li>" for it in items) + "\n</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>\n" + "\n".join(f"  <li>{format_inline(it)}</li>" for it in items) + "\n</ol>")
            continue

        # Paragraph
        para = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt == "$$"
                or (nxt.startswith("$$") and nxt.endswith("$$") and len(nxt) > 4)
                or nxt.startswith(("<div", "## ", "### ", ">", "|", "<!--"))
                or re.match(r"^(-\s+|\d+\.\s+)", nxt)
            ):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{format_inline(' '.join(para))}</p>")

    return "\n\n".join(out)


def link_or_copy(src: Path, dst: Path) -> None:
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.is_dir():
        shutil.rmtree(dst)
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copytree(src, dst)


def validate_citations(article_html: str, bib_path: Path) -> tuple[int, list[str], list[str]]:
    cited = {
        k.strip()
        for m in re.finditer(r'<d-cite\s+key="([^"]+)"', article_html)
        for k in m.group(1).split(",")
        if k.strip()
    }
    bib_text = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    bib_keys = set(re.findall(r"@\w+\{([^,\s]+),", bib_text))
    return len(cited), sorted(cited - bib_keys), sorted(bib_keys - cited)


def build(post_path: Path = DEFAULT_POST, out_dir: Path = DEFAULT_OUT) -> Path:
    raw_md = post_path.read_text(encoding="utf-8")
    meta, body_md = parse_frontmatter(raw_md)
    article_html = md_to_html(body_md)

    title = meta.get("title", "Blog Post Preview")
    description = meta.get("description", "")
    published = format_published_date(meta.get("date", "2027-04-30"))
    authors = meta.get("authors") or [
        {"author": "Anonymous", "authorURL": "", "affiliations": [{"name": "", "url": ""}]}
    ]
    bib_name = meta.get("bibliography", "2027-04-30-what-makes-a-world-model-causal.bib")
    bib_path = REPO_ROOT / "assets" / "bibliography" / bib_name

    toc_html = "\n".join(
        f'              <div>\n                <a href="#{slugify(item)}">{html.escape(item)}</a>\n              </div>'
        for item in meta.get("toc", [])
    )

    front_matter_json = json.dumps(
        {
            "title": title,
            "description": description,
            "published": published,
            "authors": authors,
            "katex": {
                "delimiters": [
                    {"left": "$", "right": "$", "display": False},
                    {"left": "$$", "right": "$$", "display": True},
                ]
            },
        },
        indent=2,
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{html.escape(title)} | ICLR Blogposts 2027</title>
    <meta name="description" content="{html.escape(description)}">

    <style>
      :root {{
        --max-content-width: 930px;
      }}
    </style>

    <!-- ICLR 2027 / al-folio Distill styles -->
    <link rel="stylesheet" href="/theme/css/tailwind.css">
    <link defer rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.2.0/css/all.min.css" crossorigin="anonymous">
    <link defer rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Roboto+Slab:100,300,400,500,700|Material+Icons&amp;display=swap">
    <link rel="stylesheet" href="/theme/css/main.css">
    <link rel="stylesheet" href="/theme/css/al-folio-distill.css">

    <!-- Dark Mode -->
    <script src="/theme/js/theme.js"></script>
    <script>
      initTheme();
    </script>

    <!-- Vendored Distill v2 runtime -->
    <script>
      window.alFolioDistill = window.alFolioDistill || {{}};
      window.alFolioDistill.templateLoader = {{"url": "/theme/js/distillpub/template.v2.js", "remote": false}};
    </script>
    <script src="/theme/js/distillpub/template.v2.js"></script>
    <script src="/theme/js/distillpub/transforms.v2.js"></script>
  </head>

  <body>
    <d-front-matter>
      <script async type="text/json">
{front_matter_json}
      </script>
    </d-front-matter>

    <!-- Header -->
    <header>
      <nav id="navbar" class="navbar navbar-light navbar-expand-sm fixed-top" role="navigation">
        <div class="container">
          <a class="navbar-brand title font-weight-lighter" href="/">ICLR Blogposts 2027</a>
          <div class="collapse navbar-collapse navbar-collapse-main" id="navbarNav">
            <ul class="navbar-nav navbar-menu-list flex-nowrap">
              <li class="toggle-container">
                <button id="light-toggle" type="button" title="Change theme" aria-label="Change color theme">
                  <i class="fa-half-sun-moon" id="light-toggle-system"></i>
                  <i class="fa-solid fa-moon" id="light-toggle-dark"></i>
                  <i class="fa-solid fa-sun" id="light-toggle-light"></i>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <progress id="progress" value="0">
        <div class="progress-container">
          <span class="progress-bar"></span>
        </div>
      </progress>
    </header>

    <!-- Content -->
    <div class="post distill">
      <d-title>
        <h1>{html.escape(title)}</h1>
        <p>{html.escape(description)}</p>
      </d-title>

      <d-byline></d-byline>

      <d-article>
        <d-contents>
          <nav class="l-text figcaption">
            <h3>Contents</h3>
{toc_html}
          </nav>
        </d-contents>

{article_html}

      </d-article>

      <d-appendix>
        <d-footnote-list></d-footnote-list>
        <d-citation-list></d-citation-list>
      </d-appendix>

      <d-bibliography src="/assets/bibliography/{html.escape(bib_name)}"></d-bibliography>
    </div>

    <!-- Distill theme overrides & MathJax 3 -->
    <script src="/theme/js/distillpub/overrides.js"></script>
    <script defer type="text/javascript" id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js" crossorigin="anonymous"></script>
    <script src="/theme/js/mathjax-setup.js"></script>
    <script defer src="/theme/js/progress-bar.js"></script>
  </body>
</html>
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    link_or_copy(REPO_ROOT / "assets", out_dir / "assets")
    link_or_copy(THEME_DIR, out_dir / "theme")

    out_html = out_dir / "index.html"
    out_html.write_text(page, encoding="utf-8")

    n_cited, missing, unused = validate_citations(article_html, bib_path)
    print(f"Rendered {post_path.relative_to(REPO_ROOT)} -> {out_html.relative_to(REPO_ROOT)} ({len(page):,} bytes)")
    print(f"Citations: {n_cited} cited | missing: {len(missing)} | unused: {len(unused)}")
    if missing:
        print(f"WARNING: Missing bib keys: {missing}")
    if unused:
        print(f"NOTE: Unused bib keys: {unused}")
    return out_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Distill blog post into _preview/.")
    parser.add_argument("--post", type=Path, default=DEFAULT_POST, help="Path to markdown post.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory (default: _preview).")
    args = parser.parse_args()
    build(args.post.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
