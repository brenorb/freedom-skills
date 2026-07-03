---
name: skillspector
description: Use NVIDIA SkillSpector when an agent needs to scan a skill or a repo of skills for security findings, compare fast static `--no-llm` scans with deeper local semantic scans through Claude Code or Codex CLI, run API-backed scans with OpenAI-compatible credentials, generate or apply baselines, or wire SkillSpector into CI with `uvx` from GitHub without installing it globally.
---

# skillspector

Use NVIDIA SkillSpector through `uvx` directly from GitHub.

## Default workflow

1. For a collection repo with a top-level `skills/` directory, start with the fast static pass:

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive --no-llm
```

2. If the user wants the deeper semantic pass through a local agent login, prefer Claude Code or Codex:

Claude Code:

```bash
SKILLSPECTOR_PROVIDER=claude_cli \
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

Codex CLI:

```bash
SKILLSPECTOR_PROVIDER=codex_cli \
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

3. If the user wants an API-backed scan instead of local CLI auth, use the OpenAI-compatible provider:

```bash
export SKILLSPECTOR_PROVIDER=openai
export OPENAI_API_KEY=sk-...
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

4. For one skill, scan the skill directory directly:

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills/signal-cli --no-llm
```

5. Interpret the report before acting on it. Separate real workflow and supply-chain risks from scanner noise.
6. If the user needs other providers, baseline generation, CI wiring, or JSON output, read `references/providers.md` and `references/commands.md`.

## Defaults

- Prefer `--recursive` when the input path is a directory of many skills like `./skills`.
- Prefer `--no-llm` for CI and quick repo-wide checks.
- Prefer `SKILLSPECTOR_PROVIDER=claude_cli` or `SKILLSPECTOR_PROVIDER=codex_cli` when the user already has a local agent CLI session.
- Prefer `SKILLSPECTOR_PROVIDER=openai` when the user wants an API-backed semantic scan.
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
- CLI providers use the local agent login session; API providers send scanned content to the configured remote endpoint.
