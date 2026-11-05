from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-drop-cli"
    / "SKILL.md"
)


def test_drop_skill_mentions_core_commands():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-drop-cli" in text
    assert "nowhere create drop" in text
    assert "nowhere update <drop-fragment-or-url>" in text
    assert "nowhere verify <drop>" in text


def test_drop_skill_mentions_current_builder_constraints():
    text = SKILL_PATH.read_text()
    assert "`description` is required" in text
    assert "builder-only in the CLI today" in text

