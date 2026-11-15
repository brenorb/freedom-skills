"""Tests for scripts/check_site_links.py: each case builds a tiny fake repository."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_site_links.py"
spec = importlib.util.spec_from_file_location("check_site_links", SCRIPT)
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker  # dataclasses look the module up while the class is built
spec.loader.exec_module(checker)

GH = "https://github.com/brenorb/freedom-skills"
# A page with a generated region is a live page; the checker only reads live pages.
LIVE = "<!--gen:skills tpl=t-->\n<!--/gen-->\n"


def make_repo(root: Path, slugs=("alpha", "beta"), catalog=None, details=None, readme=None, pages=None) -> Path:
    for slug in slugs:
        d = root / "skills" / slug
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: test\n---\n")
    catalog = list(slugs) if catalog is None else catalog
    details = list(catalog) if details is None else details
    content = root / "site" / "content"
    content.mkdir(parents=True)
    (content / "skills.json").write_text(json.dumps({"skills": [
        {"slug": s, "url": f"{GH}/tree/main/skills/{s}"} for s in catalog
    ]}))
    (content / "skill-details.json").write_text(json.dumps({s: {} for s in details}))
    if readme is None:
        readme = "# Skills\n\n" + "\n".join(f"- [`{s}`](skills/{s}/)" for s in slugs) + "\n"
    (root / "README.md").write_text(readme)
    for rel, text in (pages or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return root


def messages(root: Path) -> list[str]:
    return [str(p) for p in checker.run(root)]


def test_clean_repo_passes(tmp_path):
    root = make_repo(tmp_path, pages={
        "site/index.html": LIVE + f'<a href="{GH}/blob/main/skills/alpha/SKILL.md">Read</a> Install all 2 skills',
        "site/app.js": f"var u = '{GH}/blob/main/skills/' + slug + '/SKILL.md';",
    })
    assert messages(root) == []
    assert checker.main(["--root", str(root)]) == 0


def test_catalog_lists_a_skill_that_is_not_in_the_repo(tmp_path):
    root = make_repo(tmp_path, catalog=["alpha", "beta", "ghost"], details=["alpha", "beta", "ghost"])
    out = messages(root)
    assert any("lists 'ghost'" in m and "skills/ghost/SKILL.md does not exist" in m for m in out)
    assert checker.main(["--root", str(root)]) == 1


def test_skill_in_repo_missing_from_catalog(tmp_path):
    root = make_repo(tmp_path, catalog=["alpha"], details=["alpha"])
    assert any("is missing skills/beta" in m for m in messages(root))


def test_skill_missing_from_readme(tmp_path):
    root = make_repo(tmp_path, readme="# Skills\n\n- [`alpha`](skills/alpha/)\n")
    assert any("README.md: does not list skills/beta" in m for m in messages(root))


def test_readme_relative_link_to_missing_path(tmp_path):
    readme = "# Skills\n\n- [`alpha`](skills/alpha/)\n- [`beta`](skills/beta/)\n- [hooks](hooks/missing/README.md)\n"
    root = make_repo(tmp_path, readme=readme)
    out = messages(root)
    assert any("README.md:5" in m and "hooks/missing/README.md" in m for m in out)


def test_github_link_to_missing_skill_is_reported_with_file_and_line(tmp_path):
    root = make_repo(tmp_path, pages={
        "site/index.html": f'<p>intro</p>\n<a href="{GH}/blob/main/skills/ghost/SKILL.md">Read</a>\n' + LIVE,
    })
    out = messages(root)
    assert any(m.startswith("site/index.html:2") and "skills/ghost/SKILL.md" in m for m in out)


def test_github_tree_link_to_missing_folder(tmp_path):
    root = make_repo(tmp_path, pages={"site/index.html": LIVE + f'<a href="{GH}/tree/main/hooks/rampart-pre-send">x</a>'})
    assert any("hooks/rampart-pre-send" in m for m in messages(root))


def test_catalog_url_must_point_at_the_skill_folder(tmp_path):
    root = make_repo(tmp_path)
    path = root / "site" / "content" / "skills.json"
    data = json.loads(path.read_text())
    data["skills"][0]["url"] = f"{GH}/tree/main/skills/somewhere-else"
    path.write_text(json.dumps(data))
    assert any("'alpha' url should be" in m for m in messages(root))


def test_skill_details_must_match_catalog(tmp_path):
    root = make_repo(tmp_path, details=["alpha", "extra"])
    out = messages(root)
    assert any("has no entry for 'beta'" in m for m in out)
    assert any("has 'extra'" in m for m in out)


@pytest.mark.parametrize("phrase", ["Install all 27 skills", "Browse the 3 skills", "all 5 open skills"])
def test_wrong_skill_count_claims(tmp_path, phrase):
    root = make_repo(tmp_path, pages={"site/index.html": LIVE + f"<p>{phrase}</p>"})
    assert any("but there are 2 skills" in m for m in messages(root))


def test_category_counts_are_not_mistaken_for_totals(tmp_path):
    root = make_repo(tmp_path, pages={"site/index.html": LIVE + "<p>Money and payments · 6 skills</p>"})
    assert messages(root) == []


def test_no_skills_directory_is_an_error(tmp_path):
    (tmp_path / "README.md").write_text("# empty\n")
    assert any("no skills/*/SKILL.md found" in m for m in messages(tmp_path))


def test_frozen_prototype_pages_are_not_checked(tmp_path):
    root = make_repo(tmp_path, pages={
        "site/old-design/index.html": f'<a href="{GH}/blob/main/skills/ghost/SKILL.md">x</a> all 99 skills',
    })
    assert messages(root) == []


def test_every_file_in_a_live_page_folder_is_checked(tmp_path):
    root = make_repo(tmp_path, pages={
        "site/index.html": LIVE,
        "site/app.js": f"var u = '{GH}/blob/main/skills/ghost/SKILL.md';",
    })
    assert any(m.startswith("site/app.js:1") for m in messages(root))


def add_connector(root: Path, slug: str = "chat", in_readme: bool = True, in_catalog: bool = True):
    d = root / "connectors" / slug
    d.mkdir(parents=True)
    (d / "PROMPT.md").write_text("Do it.\n")
    if in_readme:
        with (root / "README.md").open("a") as f:
            f.write(f"- [`{slug}`](connectors/{slug}/)\n")
    path = root / "site" / "content" / "skills.json"
    data = json.loads(path.read_text())
    if in_catalog:
        data.setdefault("connectors", []).append({"slug": slug})
    path.write_text(json.dumps(data))


def test_connector_listed_everywhere_passes(tmp_path):
    root = make_repo(tmp_path)
    add_connector(root)
    assert messages(root) == []


def test_connector_missing_from_readme_and_catalog(tmp_path):
    root = make_repo(tmp_path)
    add_connector(root, in_readme=False, in_catalog=False)
    out = messages(root)
    assert any("README.md: does not list connectors/chat" in m for m in out)
    assert any("is missing connectors/chat" in m for m in out)


def test_catalog_connector_without_folder(tmp_path):
    root = make_repo(tmp_path)
    path = root / "site" / "content" / "skills.json"
    data = json.loads(path.read_text())
    data["connectors"] = [{"slug": "ghost"}]
    path.write_text(json.dumps(data))
    assert any("lists connector 'ghost'" in m for m in messages(root))
