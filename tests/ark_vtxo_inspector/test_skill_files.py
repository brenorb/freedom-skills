from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = ROOT / "skills" / "ark-vtxo-inspector" / "SKILL.md"
AGENT_PATH = ROOT / "skills" / "ark-vtxo-inspector" / "agents" / "openai.yaml"
REFERENCE_PATH = ROOT / "skills" / "ark-vtxo-inspector" / "references" / "site-behavior.md"


def read_frontmatter_and_body(path: Path) -> tuple[str, str]:
    text = path.read_text()
    parts = text.split("---", 2)
    assert len(parts) == 3, "expected YAML frontmatter fenced by ---"
    _, frontmatter, body = parts
    return frontmatter.strip(), body.strip()


def test_skill_frontmatter_has_expected_trigger_text() -> None:
    frontmatter, body = read_frontmatter_and_body(SKILL_PATH)

    assert "name: ark-vtxo-inspector" in frontmatter
    assert "https://labs.second.tech/inspector/" in frontmatter
    assert "decode or inspect Ark VTXO hex" in frontmatter

    assert "https://labs.second.tech/inspector/#<hex>" in body
    assert "exit chain" in body
    assert "Decoded" not in body  # keep UI copy out of the skill body


def test_agent_metadata_and_reference_cover_core_behavior() -> None:
    agent_text = AGENT_PATH.read_text()
    reference_text = REFERENCE_PATH.read_text()

    assert 'display_name: "Ark VTXO Inspector"' in agent_text
    assert "$ark-vtxo-inspector" in agent_text

    assert "location.hash" in reference_text
    assert "?h=<hex>" in reference_text
    assert "Hash-locked cosigned" in reference_text
    assert "not sent in HTTP requests" in reference_text
