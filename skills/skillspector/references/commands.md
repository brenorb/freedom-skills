# skillspector commands

Read this file only when the default workflow in `SKILL.md` is not enough.

## Recursive static scan

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive --no-llm
```

## Single-skill static scan with JSON output

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills/signal-cli --no-llm --format json
```

## Recursive semantic scan inside Codex

```bash
SKILLSPECTOR_PROVIDER=codex_cli \
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

## Generate a baseline for one skill

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector baseline ./skills/signal-cli --no-llm -o /tmp/signal-cli-baseline.yaml
```

## CI-friendly per-skill loop with a shared baseline file

```bash
while IFS= read -r skill; do
  uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
    skillspector scan "$skill" --no-llm \
    --baseline .skillspector-baseline.yaml
done < <(find skills -mindepth 1 -maxdepth 1 -type d | sort)
```

Use this loop when you need baseline suppressions to apply consistently in automation.
