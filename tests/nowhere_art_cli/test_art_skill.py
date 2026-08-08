from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-art-cli"
    / "SKILL.md"
)


def test_art_skill_mentions_core_commands():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-art-cli" in text
    assert "nowhere create art" in text
    assert "nowhere update <art-fragment-or-url>" in text
    assert "nowhere verify <art>" in text


def test_art_skill_mentions_svg_support():
    text = SKILL_PATH.read_text()
    assert "Inline `svg` content" in text
    assert "relay-backed publishing workflow for `art`" in text

