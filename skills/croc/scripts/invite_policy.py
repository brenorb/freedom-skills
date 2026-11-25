#!/usr/bin/env python3
"""Read the plain-text privacy choice in this installed skill's SKILL.md."""

import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
START = "<!-- croc-config:start -->"
END = "<!-- croc-config:end -->"
PREFIX = "Model may handle transfer links and codes: "


def read_policy(skill_dir=SKILL_DIR):
    path = Path(skill_dir) / "SKILL.md"
    result = {"model_access": "ask", "skill_path": str(path)}
    try:
        text = path.read_text()
        if text.count(START) != 1 or text.count(END) != 1:
            return result
        start, end = text.index(START) + len(START), text.index(END)
        if end < start:
            return result
        section = text[start:end]
        choices = [line[len(PREFIX):].strip() for line in section.splitlines() if line.startswith(PREFIX)]
        if len(choices) == 1:
            result["model_access"] = {"allowed": "allow", "private": "deny"}.get(choices[0], "ask")
    except (OSError, UnicodeError):
        pass
    return result


if __name__ == "__main__":
    print(json.dumps(read_policy()))
