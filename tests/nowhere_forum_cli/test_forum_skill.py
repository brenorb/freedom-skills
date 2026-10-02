from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-forum-cli"
    / "SKILL.md"
)


def test_forum_skill_mentions_core_flows():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-forum-cli" in text
    assert "nowhere create forum" in text
    assert "nowhere forum post" in text
    assert "nowhere forum replies" in text
    assert "nowhere forum torrent publish" in text
    assert "nowhere forum chat send" in text
    assert "nowhere forum private list" in text
    assert "nowhere forum room list" in text
    assert "nowhere forum wot check" in text


def test_forum_skill_mentions_moderation_and_preflight():
    text = SKILL_PATH.read_text()
    assert "--moderated" in text
    assert "forum torrent check" in text

