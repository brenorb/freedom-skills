"""Tests for scripts/build_site_data.py on a tiny fake repository."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_site_data.py"
spec = importlib.util.spec_from_file_location("build_site_data", SCRIPT)
gen = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gen
spec.loader.exec_module(gen)

CATEGORIES = """categories:
- id: talk
  name: Talk
  blurb: Say things.
- id: pay
  name: Pay
  blurb: Move money.
"""

README = """# Repo

## Available skills

<!-- skills:start -->
old tables
<!-- skills:end -->

## Hooks
"""

PAGE = """<p>Install all 3 skills</p>
<ol>
<!--gen:categories tpl=t-cat-->
stale
<!--/gen-->
</ol>
<template id="t-cat">
<li id="{{id}}">{{range}} {{name}} · {{count_label}}<ul>
{{each:t-skill}}
</ul></li>
</template>
<template id="t-skill">
  <li data-no="{{no}}"><a href="{{skill_md_url}}">{{name}}</a> “{{example_prompt}}”</li>
</template>
"""


def skill(root: Path, slug: str, card: str | None, description: str = "Does a thing. More detail here."):
    d = root / "skills" / slug
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: {description}\n---\n\n# {slug}\n")
    if card is not None:
        (d / "site.yaml").write_text(card)


def make_repo(root: Path) -> Path:
    (root / "skills").mkdir()
    (root / "skills" / "categories.yaml").write_text(CATEGORIES)
    skill(root, "zeta", "category: talk\norder: 10\nname: Zeta\nexample_prompt: Say \"hi\" to Ana\nreadme: Zeta row.\n")
    skill(root, "alpha", "category: pay\nname: Alpha\nprompts: [Pay Bob 5 sats]\n")
    skill(root, "beta", "category: talk\norder: 20\n")
    (root / "README.md").write_text(README)
    content = root / "site" / "content"
    content.mkdir(parents=True)
    # The previous catalog had 3 skills listed under an old name; the count is still 3.
    (content / "skills.json").write_text(json.dumps({"skills": [{"slug": "x"}, {"slug": "y"}, {"slug": "z"}]}))
    (root / "site" / "index.html").write_text(PAGE)
    (root / "site" / "app.js").write_text("label = 'Every one of the 3 skills';\n")
    (root / "site" / "old").mkdir()
    (root / "site" / "old" / "index.html").write_text("<p>Install all 3 skills</p>\n")
    return root


def run(root: Path, *args: str) -> int:
    return gen.main(["--root", str(root), *args])


def test_catalog_order_numbers_and_defaults(tmp_path):
    root = make_repo(tmp_path)
    assert run(root) == 0
    cat = json.loads((root / "site/content/skills.json").read_text())
    assert [s["slug"] for s in cat["skills"]] == ["zeta", "beta", "alpha"]  # category order, then order
    beta = cat["skills"][1]
    assert beta["name"] == "beta"  # falls back to the SKILL.md name
    assert beta["tagline"] == "Does a thing."  # first sentence of the description
    assert beta["url"] == "https://github.com/brenorb/freedom-skills/tree/main/skills/beta"
    assert [(c["id"], c["count"]) for c in cat["categories"]] == [("talk", 2), ("pay", 1)]
    assert cat["skills"][2]["example_prompt"] == "Pay Bob 5 sats"  # falls back to the first prompt
    js = (root / "site/content/skills.js").read_text()
    assert js.startswith("// ") and "window.FREEDOM_SKILLS = " in js


def test_details_file_has_every_skill_with_install_line(tmp_path):
    root = make_repo(tmp_path)
    run(root)
    det = json.loads((root / "site/content/skill-details.json").read_text())
    assert set(det) == {"zeta", "beta", "alpha"}
    assert det["alpha"]["install"] == "npx skills add brenorb/freedom-skills -s alpha"
    assert det["beta"]["prompts"] == [] and det["beta"]["music"] is None


def test_readme_tables_are_regenerated_between_markers(tmp_path):
    root = make_repo(tmp_path)
    run(root)
    text = (root / "README.md").read_text()
    assert "old tables" not in text
    assert "### Talk\n\n| Skill | What it enables |" in text
    assert "| [`zeta`](skills/zeta/) | Zeta row. |" in text
    assert text.index("### Talk") < text.index("### Pay") < text.index("## Hooks")


def test_live_page_regions_counts_and_escaping(tmp_path):
    root = make_repo(tmp_path)
    run(root)
    page = (root / "site/index.html").read_text()
    assert "stale" not in page
    assert '<li id="talk">01–02 Talk · 2 skills<ul>' in page
    assert '<li id="pay">03 Pay · 1 skill<ul>' in page
    assert '<a href="https://github.com/brenorb/freedom-skills/blob/main/skills/zeta/SKILL.md">Zeta</a>' in page
    assert "“Say &quot;hi&quot; to Ana”" in page
    assert "<p>Install all 3 skills</p>" in page  # 3 skills before and after: nothing to rewrite
    assert '<template id="t-skill">' in page  # templates stay in the page


def test_count_changes_reach_live_folder_but_not_frozen_pages(tmp_path):
    root = make_repo(tmp_path)
    (root / "site/content/skills.json").write_text(json.dumps({"skills": [{"slug": s} for s in "wxyz"]}))
    (root / "site/index.html").write_text(PAGE.replace("all 3", "all 4"))
    (root / "site/app.js").write_text("label = 'Every one of the 4 skills';\n")
    run(root)
    assert "Install all 3 skills" in (root / "site/index.html").read_text()
    assert "Every one of the 3 skills" in (root / "site/app.js").read_text()
    assert (root / "site/old/index.html").read_text() == "<p>Install all 3 skills</p>\n"


def test_check_mode_reports_stale_files_then_passes(tmp_path, capsys):
    root = make_repo(tmp_path)
    assert run(root, "--check") == 1
    assert "README.md" in capsys.readouterr().err
    assert run(root) == 0
    assert run(root, "--check") == 0
    assert run(root) == 0  # second build changes nothing


def test_missing_card_explains_how_to_create_it(tmp_path, capsys):
    root = make_repo(tmp_path)
    skill(root, "gamma", None)
    assert run(root) == 1
    err = capsys.readouterr().err
    assert "skills/gamma/site.yaml is missing" in err and "--new gamma" in err


def test_bad_category_is_rejected(tmp_path, capsys):
    root = make_repo(tmp_path)
    skill(root, "gamma", "category: cooking\n")
    assert run(root) == 1
    assert "category must be one of talk, pay" in capsys.readouterr().err


def test_new_card_is_scaffolded_from_skill_md(tmp_path):
    root = make_repo(tmp_path)
    skill(root, "gamma", None, description="Sends postcards. Very slowly.")
    assert run(root, "--new", "gamma") == 0
    card = (root / "skills/gamma/site.yaml").read_text()
    assert 'name: "gamma"' in card and 'tagline: "Sends postcards."' in card
    assert "one of: talk, pay" in card
    assert run(root) == 1  # the category is still empty, so the build asks for it
    assert run(root, "--new", "gamma") == 1  # never overwrites an existing card


def test_unknown_placeholder_is_an_error(tmp_path, capsys):
    root = make_repo(tmp_path)
    page = root / "site/index.html"
    page.write_text(PAGE.replace("{{name}}</a>", "{{nmae}}</a>"))
    assert run(root) == 1
    assert "unknown placeholder {{nmae}}" in capsys.readouterr().err


@pytest.mark.parametrize("text,expected", [
    ("Install all 27 skills", "Install all 28 skills"),
    ("Browse the 27 skills", "Browse the 28 skills"),
    ("27 open skills for agents", "28 open skills for agents"),
    ("page 3 of 27", "page 3 of 28"),
    ("range 22–27 · 6 skills", "range 22–27 · 6 skills"),
    ("all 270 skills", "all 270 skills"),
])
def test_rewrite_total(text, expected):
    assert gen.rewrite_total(text, 27, 28) == expected


def add_connectors(root: Path, readme_markers: bool = True):
    c = root / "connectors" / "chat"
    c.mkdir(parents=True)
    (c / "README.md").write_text("# Chat connector\n\nTalk to your agent from [Chat](https://example.com). More here.\n")
    (c / "PROMPT.md").write_text("# Connect\n\nPaste below the line.\n\n---\n\nStep 1. Do it.\n")
    d = root / "connectors" / "relay"
    d.mkdir(parents=True)
    (d / "PROMPT.md").write_text("Just do it.\n")
    (d / "site.yaml").write_text("order: 1\nname: Relay\ntagline: Relay things.\nreadme: Relay row.\nworks_with: [A, B]\n")
    if readme_markers:
        text = (root / "README.md").read_text().replace(
            "## Hooks", "## Connectors\n\n<!-- connectors:start -->\nold\n<!-- connectors:end -->\n\n## Hooks")
        (root / "README.md").write_text(text)


def test_connectors_in_catalog_readme_and_pages(tmp_path):
    root = make_repo(tmp_path)
    add_connectors(root)
    page = root / "site/index.html"
    page.write_text(PAGE + '<ul>\n<!--gen:connectors tpl=t-conn-->\n<!--/gen-->\n</ul>\n'
                    '<template id="t-conn">\n<li id="c-{{slug}}">{{no}} {{name}}: {{tagline}} [{{works_with}}] <button data-copy="{{prompt}}"></button></li>\n</template>\n')
    assert run(root) == 0
    cat = json.loads((root / "site/content/skills.json").read_text())
    conns = {c["slug"]: c for c in cat["connectors"]}
    assert [c["slug"] for c in cat["connectors"]] == ["relay", "chat"]  # order 1 before default 100
    assert conns["chat"]["name"] == "Chat"  # README title without "connector"
    assert conns["chat"]["tagline"] == "Talk to your agent from Chat."  # links flattened, first sentence
    assert conns["chat"]["prompt"] == "Step 1. Do it.\n"  # only the part below the --- line
    assert conns["relay"]["prompt"] == "Just do it.\n"
    assert conns["chat"]["prompt_url"].endswith("/blob/main/connectors/chat/PROMPT.md")
    readme = (root / "README.md").read_text()
    assert "| [`relay`](connectors/relay/) | Relay row. |" in readme and "\nold\n" not in readme
    html = page.read_text()
    assert '<li id="c-relay">01 Relay: Relay things. [A, B]' in html
    assert 'data-copy="Step 1. Do it.\n"' in html


def test_readme_without_connector_markers_is_left_alone_when_there_are_no_connectors(tmp_path):
    root = make_repo(tmp_path)
    assert run(root) == 0
    assert "connectors:start" not in (root / "README.md").read_text()


def test_connectors_need_readme_markers(tmp_path, capsys):
    root = make_repo(tmp_path)
    add_connectors(root, readme_markers=False)
    assert run(root) == 1
    assert "<!-- connectors:start -->" in capsys.readouterr().err
