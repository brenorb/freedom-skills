from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-event-cli"
    / "SKILL.md"
)


def test_event_skill_mentions_creation_and_updates():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-event-cli" in text
    assert "nowhere create event" in text
    assert "nowhere update" in text


def test_event_skill_mentions_signing_and_verification():
    text = SKILL_PATH.read_text()
    assert "nowhere sign <event>" in text
    assert "nowhere verify <event>" in text
    assert "poster-style event fragment or URL" in text
