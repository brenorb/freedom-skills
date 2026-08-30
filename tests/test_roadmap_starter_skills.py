from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
VALIDATOR = Path(
    "/Users/breno/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
)

ROADMAP_STARTER_SKILLS = [
    "ai-request-coach",
    "skill-auditor",
    "secure-project-bootstrap",
    "threat-model-lite",
    "private-comms-setup",
    "wallet-comparator",
    "harness-chooser",
]


def test_roadmap_starter_skills_pass_quick_validate():
    for skill_name in ROADMAP_STARTER_SKILLS:
        skill_dir = SKILLS_DIR / skill_name
        result = subprocess.run(
            ["uv", "run", "--with", "pyyaml", "python3", str(VALIDATOR), str(skill_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"{skill_name}: {result.stdout}\n{result.stderr}"


def test_roadmap_starter_skills_have_no_template_todos():
    for skill_name in ROADMAP_STARTER_SKILLS:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text()
        assert "[TODO:" not in content, skill_name
        assert "Structuring This Skill" not in content, skill_name


def test_roadmap_starter_skills_default_prompt_mentions_skill():
    for skill_name in ROADMAP_STARTER_SKILLS:
        content = (SKILLS_DIR / skill_name / "agents" / "openai.yaml").read_text()
        assert f"$${skill_name}" not in content, skill_name
        assert f"${skill_name}" in content, skill_name
        assert "default_prompt:" in content, skill_name
