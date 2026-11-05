from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-fundraiser-cli"
    / "SKILL.md"
)


def test_fundraiser_skill_mentions_builder_commands():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-fundraiser-cli" in text
    assert "nowhere create fundraiser" in text
    assert "nowhere update <fundraiser-fragment-or-url>" in text


def test_fundraiser_skill_mentions_donation_helpers():
    text = SKILL_PATH.read_text()
    assert "nowhere fundraiser donate methods" in text
    assert "nowhere fundraiser donate invoice" in text
    assert "Lightning methods encoded in tag `l`" in text
