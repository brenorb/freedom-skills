from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "openauspex"
VALIDATOR = Path(
    "/Users/breno/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
)


def test_openauspex_skill_passes_quick_validate():
    result = subprocess.run(
        ["uv", "run", "--with", "pyyaml", "python3", str(VALIDATOR), str(SKILL_DIR)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_openauspex_skill_has_no_template_todos():
    content = (SKILL_DIR / "SKILL.md").read_text()
    assert "[TODO:" not in content
    assert "Structuring This Skill" not in content


def test_openauspex_default_prompt_mentions_skill():
    content = (SKILL_DIR / "agents" / "openai.yaml").read_text()
    assert "$$openauspex" not in content
    assert "$openauspex" in content
    assert "default_prompt:" in content
