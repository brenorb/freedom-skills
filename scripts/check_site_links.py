#!/usr/bin/env python3
"""Check that the README and the website never point at skills or files that don't exist.

Run from the repository root (or pass --root):

    python3 scripts/check_site_links.py

What it checks
- Every skill in the website catalog (site/content/skills.json) has skills/<slug>/SKILL.md.
- Every skills/<slug>/SKILL.md is listed in that catalog and in README.md.
- Every skill in the catalog has demo/prompt data in site/content/skill-details.json.
- Every connectors/<slug>/PROMPT.md is in the catalog and the README, and nothing else is.
- Every link to this repository on GitHub (github.com/brenorb/freedom-skills/tree|blob/main/...)
  in README.md, the site's data and its live pages points at a path that exists in this checkout.
  (Live pages are those in site/ that scripts/build_site_data.py regenerates.)
- Every relative link in README.md points at a path that exists.
- Phrases like "all 27 skills" match the real number of skills.

Links are checked against this checkout, so in CI a pull request fails if it would merge a
page that links to something the same pull request doesn't contain.

Exit status: 0 when everything checks out, 1 when anything is wrong.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

REPO_URL = re.compile(
    r"https://github\.com/brenorb/freedom-skills/(?:tree|blob)/main/([^\s\"'<>)\]`#?]*)"
)
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
COUNT_CLAIM = re.compile(r"(?i)\b(?:all|the) (\d+) (?:open )?skills\b")
# Same marker scripts/build_site_data.py uses: a page with a generated region is a live page.
GEN_REGION = re.compile(r"<!--gen:(?:categories|skills|connectors) tpl=[\w-]+-->")
WEB_SUFFIXES = {".html", ".js", ".json", ".md", ".css"}


@dataclass
class Problem:
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


def skill_dirs(root: Path) -> set[str]:
    base = root / "skills"
    if not base.is_dir():
        return set()
    return {p.parent.name for p in base.glob("*/SKILL.md")}


def load_catalog(root: Path) -> list[dict] | None:
    path = root / "site" / "content" / "skills.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())["skills"]


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_catalog(root: Path, skills: set[str]) -> list[Problem]:
    problems: list[Problem] = []
    catalog = load_catalog(root)
    if catalog is None:
        return problems
    where = "site/content/skills.json"
    listed = [s["slug"] for s in catalog]
    for slug in listed:
        if slug not in skills:
            problems.append(Problem(where, f"lists '{slug}', but skills/{slug}/SKILL.md does not exist"))
    for slug in sorted(skills - set(listed)):
        problems.append(Problem(where, f"is missing skills/{slug} (add it to the website catalog)"))
    for s in catalog:
        expected = f"https://github.com/brenorb/freedom-skills/tree/main/skills/{s['slug']}"
        if s.get("url") != expected:
            problems.append(Problem(where, f"'{s['slug']}' url should be {expected}"))

    details_path = root / "site" / "content" / "skill-details.json"
    if details_path.exists():
        details = json.loads(details_path.read_text())
        for slug in listed:
            if slug not in details:
                problems.append(Problem("site/content/skill-details.json", f"has no entry for '{slug}'"))
        for slug in sorted(set(details) - set(listed)):
            problems.append(Problem("site/content/skill-details.json", f"has '{slug}', which is not in skills.json"))
    return problems


def connector_dirs(root: Path) -> set[str]:
    base = root / "connectors"
    return {p.parent.name for p in base.glob("*/PROMPT.md")} if base.is_dir() else set()


def check_connectors(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    connectors = connector_dirs(root)
    readme = (root / "README.md").read_text() if (root / "README.md").exists() else ""
    for slug in sorted(connectors):
        if f"(connectors/{slug}/)" not in readme and f"(connectors/{slug})" not in readme:
            problems.append(Problem("README.md", f"does not list connectors/{slug}"))
    path = root / "site" / "content" / "skills.json"
    if path.exists():
        listed = [c["slug"] for c in json.loads(path.read_text()).get("connectors", [])]
        for slug in listed:
            if slug not in connectors:
                problems.append(Problem("site/content/skills.json", f"lists connector '{slug}', but connectors/{slug}/PROMPT.md does not exist"))
        for slug in sorted(connectors - set(listed)):
            problems.append(Problem("site/content/skills.json", f"is missing connectors/{slug} (run scripts/build_site_data.py)"))
    return problems


def check_readme(root: Path, skills: set[str]) -> list[Problem]:
    path = root / "README.md"
    if not path.exists():
        return [Problem("README.md", "not found")]
    text = path.read_text()
    problems: list[Problem] = []
    for slug in sorted(skills):
        if f"(skills/{slug}/)" not in text and f"(skills/{slug})" not in text:
            problems.append(Problem("README.md", f"does not list skills/{slug}"))
    for m in MD_LINK.finditer(text):
        target = m.group(1)
        if re.match(r"^(?:[a-z]+:|#)", target):
            continue
        target = unquote(target.split("#", 1)[0])
        if target and not (root / target).exists():
            problems.append(Problem(f"README.md:{line_of(text, m.start())}", f"links to '{target}', which does not exist"))
    return problems


def web_files(root: Path) -> list[Path]:
    """README, the site's data, and every file in a live page's folder.

    Live pages are the ones scripts/build_site_data.py keeps current (they contain a generated
    region). Other pages are not checked."""
    files = [root / "README.md"] if (root / "README.md").exists() else []
    site = root / "site"
    if not site.is_dir():
        return files
    content = site / "content"
    if content.is_dir():
        files += [p for p in sorted(content.iterdir()) if p.suffix in WEB_SUFFIXES]
    live = sorted({p.parent for p in site.rglob("*.html") if GEN_REGION.search(p.read_text(errors="replace"))})
    for d in live:
        files += [p for p in sorted(d.iterdir()) if p.is_file() and p.suffix in WEB_SUFFIXES]
    return files


def check_repo_urls(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for f in web_files(root):
        text = f.read_text(errors="replace")
        rel = f.relative_to(root)
        for m in REPO_URL.finditer(text):
            target = unquote(m.group(1)).rstrip(".,;:")
            # A URL built in code ends where the string literal ends, e.g. '.../skills/' + slug.
            # The literal part must still exist; the slug comes from the catalog checked above.
            if not target or (root / target).exists():
                continue
            problems.append(Problem(f"{rel}:{line_of(text, m.start())}", f"links to '{target}' on GitHub, which does not exist in this repository"))
    return problems


def check_counts(root: Path, skills: set[str]) -> list[Problem]:
    problems: list[Problem] = []
    count = len(skills)
    for f in web_files(root):
        if f.suffix not in {".html", ".js", ".md"} or f.name in {"FEEDBACK.md", "BRIEF.md"}:
            continue
        text = f.read_text(errors="replace")
        rel = f.relative_to(root)
        for m in COUNT_CLAIM.finditer(text):
            n = int(m.group(1))
            if n != count:
                problems.append(Problem(f"{rel}:{line_of(text, m.start())}", f"says '{m.group(0)}', but there are {count} skills"))
    return problems


def run(root: Path) -> list[Problem]:
    skills = skill_dirs(root)
    if not skills:
        return [Problem("skills/", "no skills/*/SKILL.md found; run from the repository root or pass --root")]
    return (
        check_catalog(root, skills)
        + check_connectors(root)
        + check_readme(root, skills)
        + check_repo_urls(root)
        + check_counts(root, skills)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root (default: current directory)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    problems = run(root)
    if problems:
        print(f"Found {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"OK: {len(skill_dirs(root))} skills; catalog, README and links all point at files that exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
