from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-petition-cli"
    / "SKILL.md"
)


def test_petition_skill_mentions_builder_and_signing_commands():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-petition-cli" in text
    assert "nowhere create petition" in text
    assert "nowhere petition sign" in text
    assert "nowhere petition count" in text
    assert "nowhere petition signatures" in text


def test_petition_skill_mentions_validation_behavior():
    text = SKILL_PATH.read_text()
    assert "required signer fields" in text
    assert "country restrictions" in text

