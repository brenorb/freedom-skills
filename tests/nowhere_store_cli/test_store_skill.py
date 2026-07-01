from pathlib import Path


SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "nowhere-store-cli"
    / "SKILL.md"
)


def test_store_skill_frontmatter_and_trigger_text():
    text = SKILL_PATH.read_text()
    assert "name: nowhere-store-cli" in text
    assert "Create, update, inspect, sign, encrypt, and operate Nowhere store sites" in text
    assert "store-side order or status management" not in text


def test_store_skill_covers_checkout_and_seller_flows():
    text = SKILL_PATH.read_text()
    assert "nowhere create store" in text
    assert "nowhere store checkout quote" in text
    assert "nowhere store checkout begin" in text
    assert "nowhere store orders" in text
    assert "nowhere store verify" in text
    assert "nowhere store status publish" in text
