---
name: skillspector
description: Use NVIDIA SkillSpector when Codex needs to scan a skill or a repo of skills for security findings, compare quick static `--no-llm` scans with local semantic scans via `SKILLSPECTOR_PROVIDER=codex_cli`, generate or apply baselines, or wire SkillSpector into CI with `uvx` from GitHub without installing it globally.
---

# skillspector

Use NVIDIA SkillSpector through `uvx` directly from GitHub.

## Default workflow

1. For a collection repo with a top-level `skills/` directory, start with the fast static pass:

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive --no-llm
```

2. For one skill, scan the skill directory directly:

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills/signal-cli --no-llm
```

3. If you are running inside Codex and want the deeper semantic pass, rerun with the Codex provider:

```bash
SKILLSPECTOR_PROVIDER=codex_cli \
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

4. Interpret the report before acting on it. Separate real workflow and supply-chain risks from scanner noise.
5. If the user needs baseline generation, CI wiring, JSON output, or per-skill loop patterns, read `references/commands.md`.

## Defaults

- Prefer `--recursive` when the input path is a directory of many skills like `./skills`.
- Prefer `--no-llm` for CI and quick repo-wide checks.
- Prefer `SKILLSPECTOR_PROVIDER=codex_cli` for local deep review inside Codex.
- Prefer the direct `uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git'` form over a permanent install when the goal is one-off or low-frequency use.
- Prefer scanning skills individually in a loop when you need baseline suppressions to gate CI reliably.

## Interpretation rules

- Do not accept a `HIGH` or `DO_NOT_INSTALL` verdict blindly. Read the issue list and inspect the flagged file.
- Treat generic subprocess findings with skepticism when the code uses argv lists and not `shell=True`.
- Treat implicit package installs, browser/runtime bootstrap, public network actions, credential handling, and irreversible payments as higher-signal findings.
- Baseline only current accepted findings. Keep real unresolved issues visible unless the user explicitly wants “fail on regressions only”.

## Gotchas

- The environment variable is `SKILLSPECTOR_PROVIDER`, not `KILLSPECTOR_PROVIDER`.
- `skillspector scan ./skills` without `--recursive` treats the whole directory as one bundle and overstates risk for a multi-skill repo.
- Current recursive scans do not honor baselines consistently, so use a per-skill loop for CI if baseline suppressions matter.
- Exit code `1` means findings were reported; it is not necessarily a crash.
