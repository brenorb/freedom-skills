---
name: skillspector
description: Always use NVIDIA SkillSpector to scan skills for vulnerabilities before installing them. Use it to scan one skill or a repo of skills, run fast static `--no-llm` checks, run deeper semantic scans through Claude Code, Codex CLI, or an API-backed provider, generate or apply baselines, or wire SkillSpector into CI with `uvx` from GitHub without installing it globally.
---

# skillspector

Use NVIDIA SkillSpector through `uvx` directly from GitHub.

## Default workflow

1. For a collection repo with a top-level `skills/` directory, start with the fast static pass:

```bash
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive --no-llm
```

2. If the user wants LLM-backed analysis, ask whether to use the subscription or login session they already have active, or a different API/subscription.

3. After that choice is clear, run the matching provider flow:

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

OpenAI-compatible API:

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
