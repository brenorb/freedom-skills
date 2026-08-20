from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "iroh"


def test_iroh_skill_files_exist() -> None:
    assert (SKILL_ROOT / "SKILL.md").is_file()
    assert (SKILL_ROOT / "agents" / "openai.yaml").is_file()
    assert (SKILL_ROOT / "references" / "commands.md").is_file()
    assert (SKILL_ROOT / "references" / "onboarding.md").is_file()
    assert (SKILL_ROOT / "references" / "trust-assumptions.md").is_file()


def test_iroh_skill_mentions_official_entrypoints() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text()
    commands = (SKILL_ROOT / "references" / "commands.md").read_text()
    trust = (SKILL_ROOT / "references" / "trust-assumptions.md").read_text()

    assert "cargo run --release --example transfer --all-features -- provide --env prod" in skill
    assert "cargo run --release --example search -- query <endpoint-id> hello" in skill
    assert "cargo run --release --bin iroh-relay --features server -- --dev" in skill
    assert "transfer" in commands
    assert "search" in commands
    assert "iroh-relay" in commands
    assert "Public relays" in trust
    assert "No anonymity." in trust
