#!/usr/bin/env python3
"""Regenerate the website data, the README skill tables and live site pages from skills/.

    uv run --with pyyaml python scripts/build_site_data.py           # write everything
    uv run --with pyyaml python scripts/build_site_data.py --check   # exit 1 if anything is stale
    uv run --with pyyaml python scripts/build_site_data.py --new my-skill   # start a catalog card

Sources (the only files to edit by hand):
- skills/<slug>/SKILL.md              name and description (frontmatter)
- catalog/skills/<slug>.yaml          the website card: category, tagline, prompts, demo, caveats...
- catalog/categories.yaml             category ids, names and blurbs, in display order
- connectors/<slug>/PROMPT.md         a connector: the prompt a person pastes into their agent
- catalog/connectors/<slug>.yaml      optional connector card: name, tagline, readme, works_with, upstream

Cards live in catalog/, never in a skill folder: `npx skills add` copies the whole skill folder
into the user's agent, so anything there that isn't for the agent is shipped for nothing.

Outputs (never edit by hand):
- site/content/skills.json, skills.js                  the catalog every page reads
- site/content/skill-details.json, skill-details.js    prompts, demo steps, caveats per skill
- README.md, between <!-- skills:start --> and <!-- skills:end --> (and the connectors markers)
- Live pages: any site/**/*.html with <!--gen:...--> regions. Each region is rebuilt from a
  <template id="..."> in the same file, and the skill count ("all 27 skills") is updated in every
  .html and .js of that page's folder. Pages without regions are left alone.

Template syntax inside a <template>: {{field}} (HTML-escaped). In a category template,
{{each:TEMPLATE_ID}} renders that template once per skill in the category.
Region syntax:  <!--gen:KIND tpl=ID--> ... <!--/gen-->  where KIND is categories, skills or connectors.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

import yaml

REPO = "https://github.com/brenorb/freedom-skills"
INSTALL = "npx skills add brenorb/freedom-skills"
README_START, README_END = "<!-- skills:start -->", "<!-- skills:end -->"
CONN_START, CONN_END = "<!-- connectors:start -->", "<!-- connectors:end -->"
REGION = re.compile(r"(<!--gen:(categories|skills|connectors) tpl=([\w-]+)-->\n)(.*?)(<!--/gen-->)", re.S)
TEMPLATE = re.compile(r'<template id="([\w-]+)">\n?(.*?)\n?[ \t]*</template>', re.S)
PLACEHOLDER = re.compile(r"\{\{([\w:-]+)\}\}")
DETAIL_FIELDS = ("what_for", "prompts", "demo", "caveats", "needs", "music")


class SiteDataError(Exception):
    """A source file is missing or invalid; the message says how to fix it."""


# ---------- reading sources ----------

def read_frontmatter(path: Path) -> dict:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SiteDataError(f"{path}: no YAML frontmatter")
    return yaml.safe_load(m.group(1)) or {}


CATALOG = "catalog"  # website and README cards; never inside a skill folder


def first_sentence(text: str, limit: int = 140) -> str:
    s = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def load(root: Path) -> dict:
    cats_file = root / CATALOG / "categories.yaml"
    if not cats_file.exists():
        raise SiteDataError("catalog/categories.yaml is missing")
    categories = yaml.safe_load(cats_file.read_text())["categories"]
    cat_ids = [c["id"] for c in categories]
    problems, skills = [], []
    for stray in sorted((root / "skills").glob("*/site.yaml")) + sorted((root / "connectors").glob("*/site.yaml")):
        kind, slug = stray.parent.parent.name, stray.parent.name
        problems.append(f"{kind}/{slug}/site.yaml must not be in the {kind[:-1]} folder (it would be installed "
                        f"into users' agents). Move it to catalog/{kind}/{slug}.yaml")
    slugs = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    for card_path in sorted((root / CATALOG / "skills").glob("*.yaml")):
        if card_path.stem not in slugs:
            problems.append(f"catalog/skills/{card_path.name} has no skills/{card_path.stem}/SKILL.md; "
                            f"delete the card or restore the skill")
    for skill_md in sorted((root / "skills").glob("*/SKILL.md")):
        slug = skill_md.parent.name
        fm = read_frontmatter(skill_md)
        card_path = root / CATALOG / "skills" / f"{slug}.yaml"
        if not card_path.exists():
            problems.append(f"catalog/skills/{slug}.yaml is missing. Create it with:\n"
                            f"    uv run --with pyyaml python scripts/build_site_data.py --new {slug}")
            continue
        card = yaml.safe_load(card_path.read_text()) or {}
        if card.get("category") not in cat_ids:
            problems.append(f"catalog/skills/{slug}.yaml: category must be one of {', '.join(cat_ids)} "
                            f"(got {card.get('category')!r})")
            continue
        description = " ".join(str(fm.get("description", "")).split())
        summary = card.get("summary") or description
        demo = card.get("demo") or {}
        skills.append({
            "slug": slug,
            "name": card.get("name") or fm.get("name", slug),
            "category": card["category"],
            "order": int(card.get("order", 100)),
            "summary": summary,
            "tagline": card.get("tagline") or first_sentence(summary),
            "readme": card.get("readme") or summary,
            "example_prompt": card.get("example_prompt") or (card.get("prompts") or [""])[0] or demo.get("prompt", ""),
            "tool": card.get("tool", ""),
            "upstream": card.get("upstream") or (fm.get("metadata") or {}).get("repository", ""),
            "details": {k: card.get(k) for k in DETAIL_FIELDS},
        })
    if problems:
        raise SiteDataError("\n".join(problems))
    order = {c: i for i, c in enumerate(cat_ids)}
    connectors = load_connectors(root)
    skills.sort(key=lambda s: (order[s["category"]], s["order"], s["slug"]))
    for i, s in enumerate(skills, 1):
        s["no"] = i
    return {"categories": categories, "skills": skills, "connectors": connectors}


def load_connectors(root: Path) -> list[dict]:
    """Every connectors/<slug>/PROMPT.md is a connector; catalog/connectors/<slug>.yaml is optional."""
    out = []
    for prompt_md in sorted((root / "connectors").glob("*/PROMPT.md")):
        d = prompt_md.parent
        card_path = root / CATALOG / "connectors" / f"{d.name}.yaml"
        card = yaml.safe_load(card_path.read_text()) if card_path.exists() else {}
        card = card or {}
        readme = (d / "README.md").read_text() if (d / "README.md").exists() else ""
        title = re.search(r"^#\s+(.+)$", readme, re.M)
        para = next((p.strip() for p in re.split(r"\n\s*\n", readme) if p.strip() and not p.lstrip().startswith("#")), "")
        para = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", " ".join(para.split()))
        prompt = prompt_md.read_text()
        body = prompt.split("\n---\n", 1)[1] if "\n---\n" in prompt else prompt
        name = card.get("name") or (re.sub(r"\s+connector$", "", title.group(1).strip(), flags=re.I) if title else d.name)
        out.append({
            "slug": d.name, "name": name, "order": int(card.get("order", 100)),
            "tagline": card.get("tagline") or first_sentence(para),
            "readme": card.get("readme") or first_sentence(para),
            "works_with": list(card.get("works_with") or []),
            "upstream": card.get("upstream", ""),
            "prompt": body.strip() + "\n",
        })
    out.sort(key=lambda c: (c["order"], c["slug"]))
    return out


# ---------- building outputs ----------

def catalog(data: dict) -> dict:
    skills = [{
        "slug": s["slug"], "name": s["name"], "category": s["category"], "summary": s["summary"],
        "tagline": s["tagline"], "example_prompt": s["example_prompt"], "tool": s["tool"],
        "upstream": s["upstream"], "url": f"{REPO}/tree/main/skills/{s['slug']}",
    } for s in data["skills"]]
    cats = [{**c, "count": sum(1 for s in skills if s["category"] == c["id"])} for c in data["categories"]]
    connectors = [{
        "slug": c["slug"], "name": c["name"], "tagline": c["tagline"], "works_with": c["works_with"],
        "upstream": c["upstream"], "url": f"{REPO}/tree/main/connectors/{c['slug']}",
        "prompt_url": f"{REPO}/blob/main/connectors/{c['slug']}/PROMPT.md", "prompt": c["prompt"],
    } for c in data["connectors"]]
    return {
        "site": {"name": "Freedom Skills", "repo": REPO, "standard": "https://agentskills.io",
                 "license_note": "Open source, community-driven"},
        "categories": [c for c in cats if c["count"]],
        "skills": skills,
        "connectors": connectors,
    }


def details(data: dict) -> dict:
    out = {}
    for s in data["skills"]:
        d = {"slug": s["slug"], "install": f"{INSTALL} -s {s['slug']}"}
        for k in DETAIL_FIELDS:
            d[k] = s["details"][k] if s["details"][k] is not None else ([] if k in ("prompts", "caveats") else ({} if k == "demo" else (None if k == "music" else "")))
        out[s["slug"]] = d
    return out


def dump_json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def dump_js(var: str, obj, note: str) -> str:
    return f"// {note}\n// Generated by scripts/build_site_data.py from catalog/. Do not edit.\nwindow.{var} = " + json.dumps(obj, indent=2, ensure_ascii=False) + ";\n"


def readme_section(data: dict) -> str:
    parts = []
    for c in data["categories"]:
        rows = [s for s in data["skills"] if s["category"] == c["id"]]
        if not rows:
            continue
        parts.append(f"### {c['name']}\n\n| Skill | What it enables |\n|---|---|")
        parts += [f"| [`{s['slug']}`](skills/{s['slug']}/) | {s['readme']} |" for s in rows]
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def replace_between(text: str, start: str, end: str, body: str) -> str:
    if start not in text or end not in text:
        raise SiteDataError(f"README.md needs {start} and {end} around the generated table")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{body}{end}{tail}"


def update_readme(text: str, data: dict) -> str:
    note = "<!-- Generated from catalog/ by scripts/build_site_data.py. Edit those cards, not this. -->\n\n"
    text = replace_between(text, README_START, README_END, note + readme_section(data) + "\n")
    if data["connectors"] or CONN_START in text:
        rows = "\n".join(f"| [`{c['slug']}`](connectors/{c['slug']}/) | {c['readme']} |" for c in data["connectors"])
        text = replace_between(text, CONN_START, CONN_END, f"| Connector | What it enables |\n|---|---|\n{rows}\n")
    return text


# ---------- live pages ----------

def two(n: int) -> str:
    return f"{n:02d}"


def skill_fields(s: dict, data: dict) -> dict:
    cat = next(c for c in data["categories"] if c["id"] == s["category"])
    return {
        "slug": s["slug"], "name": s["name"], "tagline": s["tagline"], "summary": s["summary"],
        "example_prompt": s["example_prompt"], "tool": s["tool"], "upstream": s["upstream"],
        "install": f"{INSTALL} -s {s['slug']}", "url": f"{REPO}/tree/main/skills/{s['slug']}",
        "skill_md_url": f"{REPO}/blob/main/skills/{s['slug']}/SKILL.md", "no": two(s["no"]),
        "category_id": cat["id"], "category_name": cat["name"], "total": str(len(data["skills"])),
    }


def connector_fields(c: dict, data: dict) -> dict:
    return {
        "slug": c["slug"], "name": c["name"], "tagline": c["tagline"], "upstream": c["upstream"],
        "works_with": ", ".join(c["works_with"]), "prompt": c["prompt"],
        "no": two(data["connectors"].index(c) + 1),
        "url": f"{REPO}/tree/main/connectors/{c['slug']}",
        "prompt_url": f"{REPO}/blob/main/connectors/{c['slug']}/PROMPT.md",
        "total": str(len(data["connectors"])),
    }


def category_fields(c: dict, members: list[dict], data: dict) -> dict:
    first, last = members[0]["no"], members[-1]["no"]
    return {
        "id": c["id"], "name": c["name"], "blurb": c["blurb"], "count": str(len(members)),
        "count_label": f"{len(members)} skill" + ("" if len(members) == 1 else "s"),
        "range": two(first) if first == last else f"{two(first)}–{two(last)}",
        "first_no": two(first), "first_no_int": str(first), "total": str(len(data["skills"])),
    }


def render(template: str, fields: dict, templates: dict, members: list[dict], data: dict, where: str) -> str:
    def sub(m):
        key = m.group(1)
        if key.startswith("each:"):
            tid = key[5:]
            if tid not in templates:
                raise SiteDataError(f"{where}: {{{{{key}}}}} names a missing <template id=\"{tid}\">")
            return "\n".join(render(templates[tid], skill_fields(s, data), templates, [], data, where) for s in members)
        if key not in fields:
            raise SiteDataError(f"{where}: unknown placeholder {{{{{key}}}}}; known: {', '.join(sorted(fields))}")
        return html.escape(fields[key], quote=True)
    return PLACEHOLDER.sub(sub, template)


def update_page(text: str, data: dict, where: str, old_total: int | None) -> str:
    templates = dict(TEMPLATE.findall(text))

    def region(m):
        start, kind, tid, _, end = m.groups()
        if tid not in templates:
            raise SiteDataError(f"{where}: region uses tpl={tid}, but there is no <template id=\"{tid}\">")
        if kind == "skills":
            items = [render(templates[tid], skill_fields(s, data), templates, [], data, where) for s in data["skills"]]
        elif kind == "connectors":
            items = [render(templates[tid], connector_fields(c, data), templates, [], data, where) for c in data["connectors"]]
        else:
            items = []
            for c in data["categories"]:
                members = [s for s in data["skills"] if s["category"] == c["id"]]
                if members:
                    items.append(render(templates[tid], category_fields(c, members, data), templates, members, data, where))
        return start + "\n".join(items) + "\n" + end

    text = REGION.sub(region, text)
    new_total = len(data["skills"])
    if old_total and old_total != new_total:
        text = rewrite_total(text, old_total, new_total)
    return text


def rewrite_total(text: str, old: int, new: int) -> str:
    """Update phrases like 'all 27 skills', 'the 27 skills', '27 open skills', 'one of the 27'."""
    o = str(old)
    patterns = [
        rf"\b{o}(?=(?:\s|&nbsp;)+(?:open\s+|free\s+)?skills\b)",
        rf"(?i)(?<=\ball ){o}\b",
        rf"(?i)(?<=\bthe ){o}\b(?![\d–-])",
        rf"(?i)(?<=\bof ){o}\b(?![\d–-])",
    ]
    for p in patterns:
        text = re.sub(p, str(new), text)
    return text


SITE = "site"  # the website folder GitHub Pages publishes


def live_files(root: Path) -> list[Path]:
    """Pages kept current by this script: every .html/.js in a folder whose page has a gen region.

    Pages without a region are left alone."""
    site = root / SITE
    if not site.is_dir():
        return []
    dirs = sorted({p.parent for p in site.rglob("*.html") if REGION.search(p.read_text(errors="replace"))})
    return [f for d in dirs for f in sorted(d.iterdir()) if f.suffix in (".html", ".js")]


# ---------- orchestration ----------

def build(root: Path) -> dict[Path, str]:
    """Return {path: new content} for every output file."""
    data = load(root)
    content = root / SITE / "content"
    old_total = None
    if (content / "skills.json").exists():
        old_total = len(json.loads((content / "skills.json").read_text())["skills"])
    cat, det = catalog(data), details(data)
    out = {}
    if content.is_dir():
        out[content / "skills.json"] = dump_json(cat)
        out[content / "skills.js"] = dump_js("FREEDOM_SKILLS", cat, "Same data as skills.json, usable from file:// without fetch().")
        out[content / "skill-details.json"] = dump_json(det)
        out[content / "skill-details.js"] = dump_js("FREEDOM_SKILL_DETAILS", det, "Same data as skill-details.json.")
    readme = root / "README.md"
    out[readme] = update_readme(readme.read_text(), data)
    for page in live_files(root):
        out[page] = update_page(page.read_text(), data, str(page.relative_to(root)), old_total)
    return out


NEW_CARD = """# Website and README card for skills/{slug}/. Kept out of the skill folder so it isn't installed into agents.
# scripts/build_site_data.py turns it into the site's data, the README table and the skill pages.
category: {category}   # one of: {choices}
order: 100              # position inside the category (lower comes first)
name: {name}
tagline: {tagline}
summary: {summary}
readme: {summary}
tool: ""
upstream: {upstream}
example_prompt: ""
what_for: ""
needs: ""
prompts: []             # 4-6 real requests a person would type
caveats: []             # the most important warnings from SKILL.md
demo: {{}}              # prompt, steps (kind: match|run|check|caveat|confirm, text, cmd, action), result
music: null
"""


def new_card(root: Path, slug: str) -> Path:
    skill_md = root / "skills" / slug / "SKILL.md"
    if not skill_md.exists():
        raise SiteDataError(f"skills/{slug}/SKILL.md does not exist yet; create the skill first")
    target = root / CATALOG / "skills" / f"{slug}.yaml"
    if target.exists():
        raise SiteDataError(f"{target.relative_to(root)} already exists")
    fm = read_frontmatter(skill_md)
    cats = [c["id"] for c in yaml.safe_load((root / CATALOG / "categories.yaml").read_text())["categories"]]
    target.parent.mkdir(parents=True, exist_ok=True)
    description = " ".join(str(fm.get("description", "")).split())
    q = lambda s: json.dumps(s, ensure_ascii=False)
    target.write_text(NEW_CARD.format(
        slug=slug, category='""', choices=", ".join(cats), name=q(fm.get("name", slug)),
        tagline=q(first_sentence(description)), summary=q(description),
        upstream=q((fm.get("metadata") or {}).get("repository", "")),
    ))
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--check", action="store_true", help="don't write; exit 1 if any output is out of date")
    ap.add_argument("--new", metavar="SLUG", help="create catalog/skills/SLUG.yaml from its SKILL.md, then fill it in")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.new:
            path = new_card(root, args.new)
            print(f"Created {path.relative_to(root)}. Set its category, prompts and demo, then run this script again.")
            return 0
        outputs = build(root)
    except SiteDataError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    stale = [p for p, text in outputs.items() if not p.exists() or p.read_text() != text]
    if args.check:
        if stale:
            print("Out of date (run: uv run --with pyyaml python scripts/build_site_data.py):", file=sys.stderr)
            for p in stale:
                print(f"  - {p.relative_to(root)}", file=sys.stderr)
            return 1
        print(f"Up to date: {len(outputs)} generated files.")
        return 0
    for p in stale:
        p.write_text(outputs[p])
        print(f"wrote {p.relative_to(root)}")
    if not stale:
        print("Nothing to update.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
