#!/usr/bin/env python3

from __future__ import annotations

import html
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs"
ASSET_DIR = OUTPUT / "assets"
STYLE_NOTE = Path(
    "/Users/breno/Documents/Obsidian Vault/Zettelkasten/Medieval manuscript CSS style.md"
)

CSS_BLOCK_RE = re.compile(r"```css\s*(.*?)```", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
MD_LINK_RE = re.compile(r'href="([^":?#"]+?)\.md((?:[#?][^"]*)?)"')

SITE_SHELL_CSS = """
:root {
  color-scheme: light;
}

* {
  box-sizing: border-box;
}

html {
  background: #eadfc8;
}

body {
  margin: 0;
  min-height: 100vh;
  padding: 18px 10px 36px;
  background:
    radial-gradient(circle at top, rgba(159, 122, 51, 0.18), rgba(159, 122, 51, 0) 34%),
    linear-gradient(180deg, #f2e7cf 0%, #eadfc8 100%);
}

a {
  transition:
    color 160ms ease,
    border-color 160ms ease,
    transform 160ms ease,
    background-color 160ms ease;
}

.page-shell,
.index-shell {
  max-width: 980px;
  margin: 0 auto;
}

.site-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin: 0 auto 16px;
  padding: 4px;
  position: sticky;
  top: 8px;
  z-index: 10;
}

.site-nav a {
  color: #4a3d31;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.72rem;
  padding: 0.56rem 0.9rem;
  border: 1px solid rgba(99, 70, 31, 0.24);
  border-radius: 999px;
  background: rgba(248, 239, 220, 0.82);
  box-shadow: 0 8px 18px rgba(54, 35, 14, 0.09);
  backdrop-filter: blur(8px);
}

.site-nav a:hover {
  color: #983334;
  border-color: rgba(152, 51, 52, 0.4);
  background: rgba(248, 239, 220, 0.96);
  transform: translateY(-1px);
}

.page-meta {
  margin: 0 0 1.2rem;
  text-align: center;
  color: #6a5a49;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
}

.index-shell {
  padding: 18px 0 28px;
}

.index-header {
  max-width: 780px;
  margin: 0 auto 18px;
  text-align: center;
  color: #3f3225;
  padding: 26px 14px 14px;
}

.eyebrow {
  margin: 0 0 0.5rem;
  color: #7f4b3f;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.74rem;
}

.index-header h1 {
  margin: 0;
  font-family: "Baskerville", "Times New Roman", serif;
  font-size: clamp(2.1rem, 5vw, 3.4rem);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.index-header p {
  margin: 0.9rem auto 0;
  max-width: 50rem;
  color: #5a4a38;
  line-height: 1.6;
}

.index-list {
  display: grid;
  gap: 14px;
}

.index-card {
  display: block;
  text-decoration: none;
  color: inherit;
  max-width: 860px;
  margin: 0 auto;
  padding: 18px 18px 16px;
  border: 1px solid rgba(99, 70, 31, 0.26);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(248, 239, 220, 0.93), rgba(240, 229, 207, 0.96));
  box-shadow:
    0 12px 28px rgba(54, 35, 14, 0.09),
    inset 0 0 0 1px rgba(247, 236, 214, 0.6);
}

.index-card:hover {
  transform: translateY(-2px);
  border-color: rgba(152, 51, 52, 0.38);
}

.index-card h2 {
  margin: 0 0 0.38rem;
  font-family: "Baskerville", "Times New Roman", serif;
  color: #251d15;
  font-size: 1.35rem;
  letter-spacing: 0.02em;
}

.index-card p {
  margin: 0;
  color: #5a4a38;
  line-height: 1.58;
}

.index-card .meta {
  margin-top: 0.75rem;
  color: #7a6a57;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.footer-note {
  margin: 18px auto 0;
  text-align: center;
  color: #6a5a49;
  font-size: 0.82rem;
}

@media (max-width: 640px) {
  body {
    padding: 12px 6px 24px;
  }

  .site-nav {
    top: 6px;
    gap: 8px;
  }

  .site-nav a {
    font-size: 0.67rem;
    padding: 0.5rem 0.78rem;
  }

  .manuscript {
    padding: 28px 18px 30px;
    margin: 0 auto 16px;
    font-size: 16px;
    line-height: 1.58;
  }

  .index-header {
    padding-top: 18px;
  }

  .index-card {
    padding: 16px 14px 14px;
    border-radius: 14px;
  }
}
"""


@dataclass(frozen=True)
class Document:
  source: Path
  relative_path: Path
  output_path: Path
  title: str
  excerpt: str


def run(*args: str) -> str:
  result = subprocess.run(
      args,
      cwd=ROOT,
      check=True,
      capture_output=True,
      text=True,
  )
  return result.stdout


def list_documents() -> list[Document]:
  files = [Path(line) for line in run("git", "ls-files", "*.md").splitlines() if line]
  files = [path for path in files if not path.parts or path.parts[0] != "docs"]
  files.sort(key=lambda path: (path.name != "README.md", path.as_posix().lower()))

  documents: list[Document] = []
  for relative_path in files:
    source = ROOT / relative_path
    output_path = OUTPUT / relative_path.with_suffix(".html")
    text = source.read_text(encoding="utf-8")
    title = extract_title(text, relative_path)
    excerpt = extract_excerpt(text)
    documents.append(
        Document(
            source=source,
            relative_path=relative_path,
            output_path=output_path,
            title=title,
            excerpt=excerpt,
        )
    )
  return documents


def extract_title(text: str, relative_path: Path) -> str:
  match = TITLE_RE.search(text)
  if match:
    return match.group(1).strip()
  return relative_path.stem.replace("-", " ").replace("_", " ").title()


def extract_excerpt(text: str) -> str:
  cleaned = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL).strip()
  for block in re.split(r"\n\s*\n", cleaned):
    paragraph = " ".join(line.strip() for line in block.splitlines())
    if not paragraph:
      continue
    if paragraph.startswith("#"):
      continue
    if paragraph.startswith(("- ", "* ", "|", "1. ", "2. ", "3. ")):
      continue
    return clean_markdown_preview(paragraph)
  return "Leitura renderizada a partir do Markdown original."


def clean_markdown_preview(text: str) -> str:
  text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
  text = text.replace("**", "").replace("__", "").replace("`", "")
  return re.sub(r"\s+", " ", text).strip()


def extract_manuscript_css() -> str:
  note = STYLE_NOTE.read_text(encoding="utf-8")
  match = CSS_BLOCK_RE.search(note)
  if not match:
    raise RuntimeError(f"Nao encontrei o bloco CSS em {STYLE_NOTE}")

  css = match.group(1).strip()
  css = css.replace(".markdown-preview.markdown-preview", ".manuscript")
  css = css.replace(".markdown-preview ", ".manuscript ")
  css = css.replace(".markdown-preview", ".manuscript")
  return css


def render_markdown(source: Path) -> str:
  html_body = run(
      "pandoc",
      str(source),
      "--from=gfm+smart",
      "--to=html5",
      "--no-highlight",
      "--wrap=none",
  ).strip()
  return MD_LINK_RE.sub(r'href="\1.html\2"', html_body)


def relative_href(from_path: Path, to_path: Path) -> str:
  return os.path.relpath(to_path, start=from_path.parent).replace(os.sep, "/")


def page_template(title: str, css_href: str, body: str) -> str:
  return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)} · Freedom Skills</title>
    <link rel="stylesheet" href="{css_href}">
  </head>
  <body>
    {body}
  </body>
</html>
"""


def build_document_pages(documents: list[Document]) -> None:
  for index, document in enumerate(documents):
    document.output_path.parent.mkdir(parents=True, exist_ok=True)
    css_href = relative_href(document.output_path, ASSET_DIR / "site.css")
    index_href = relative_href(document.output_path, OUTPUT / "index.html")
    nav_links = [f'<a href="{index_href}">Indice</a>']

    if index > 0:
      previous_href = relative_href(document.output_path, documents[index - 1].output_path)
      nav_links.append(f'<a href="{previous_href}">Anterior</a>')

    if index + 1 < len(documents):
      next_href = relative_href(document.output_path, documents[index + 1].output_path)
      nav_links.append(f'<a href="{next_href}">Proximo</a>')

    content_html = render_markdown(document.source)
    source_label = html.escape(document.relative_path.as_posix())
    page_body = f"""
<main class="page-shell">
  <nav class="site-nav" aria-label="Navegacao">
    {''.join(nav_links)}
  </nav>
  <article class="manuscript">
    <p class="page-meta">{source_label}</p>
    {content_html}
    <div class="mpe-end"></div>
  </article>
</main>
""".strip()

    document.output_path.write_text(
        page_template(document.title, css_href, page_body),
        encoding="utf-8",
    )


def build_index(documents: list[Document]) -> None:
  index_path = OUTPUT / "index.html"
  css_href = relative_href(index_path, ASSET_DIR / "site.css")
  cards = []

  for document in documents:
    href = relative_href(index_path, document.output_path)
    title = html.escape(document.title)
    excerpt = html.escape(document.excerpt)
    source_label = html.escape(document.relative_path.as_posix())
    cards.append(
        f"""
<a class="index-card" href="{href}">
  <h2>{title}</h2>
  <p>{excerpt}</p>
  <p class="meta">{source_label}</p>
</a>
""".strip()
    )

  body = f"""
<main class="index-shell">
  <header class="index-header">
    <p class="eyebrow">Freedom Skills</p>
    <h1>Indice Da Pesquisa</h1>
    <p>Leitura rapida das notas existentes, renderizadas para celular sem alterar o conteudo em Markdown.</p>
  </header>
  <section class="index-list">
    {''.join(cards)}
  </section>
  <p class="footer-note">GitHub Pages minimo com o estilo inspirado no manuscrito medieval.</p>
</main>
""".strip()
  index_path.write_text(page_template("Indice", css_href, body), encoding="utf-8")


def write_assets() -> None:
  ASSET_DIR.mkdir(parents=True, exist_ok=True)
  (OUTPUT / ".nojekyll").write_text("\n", encoding="utf-8")
  (ASSET_DIR / "site.css").write_text(
      extract_manuscript_css() + "\n\n" + SITE_SHELL_CSS,
      encoding="utf-8",
  )


def main() -> None:
  documents = list_documents()
  OUTPUT.mkdir(parents=True, exist_ok=True)
  write_assets()
  build_document_pages(documents)
  build_index(documents)


if __name__ == "__main__":
  main()
