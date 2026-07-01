from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-message-cli"
    / "SKILL.md"
)


def test_message_skill_mentions_core_commands():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-message-cli" in text
    assert "nowhere create message" in text
    assert "nowhere update <message-fragment-or-url>" in text
    assert "nowhere sign <message>" in text
    assert "nowhere verify <message>" in text


def test_message_skill_mentions_builder_only_scope():
    text = SKILL_PATH.read_text()
    assert "builder-only in the CLI today" in text
    assert "relay-backed inbox or reply flow" in text

