# skillspector providers

Read this file only when the user needs a provider other than the main OpenAI-compatible API, Claude Code, or Codex CLI examples in `SKILL.md`.

Canonical upstream docs:

- https://github.com/NVIDIA/SkillSpector#configuration
- https://github.com/NVIDIA/SkillSpector#llm-analysis

## Main provider families

- `openai`: OpenAI API or any OpenAI-compatible endpoint such as Ollama.
- `claude_cli`: local Claude Code / Claude CLI login session.
- `codex_cli`: local Codex CLI login session.
- `anthropic`: direct Anthropic API key.
- `anthropic_proxy`: Anthropic-compatible corporate or Vertex-style proxy.
- `bedrock`: AWS Bedrock via SigV4 and boto3 credentials.
- `nv_build`: NVIDIA build.nvidia.com inference key.
- `gemini_cli`: local Gemini CLI login session when supported upstream.

## Examples

Anthropic API:

```bash
export SKILLSPECTOR_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

AWS Bedrock:

```bash
export SKILLSPECTOR_PROVIDER=bedrock
export AWS_REGION=us-west-2
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

Ollama or another OpenAI-compatible local endpoint:

```bash
export SKILLSPECTOR_PROVIDER=openai
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://localhost:11434/v1
export SKILLSPECTOR_MODEL=llama3.1:8b
uvx --from 'git+https://github.com/NVIDIA/SkillSpector.git' \
  skillspector scan ./skills --recursive
```

## Notes

- CLI providers do not need an API key; they use the local CLI login session.
- `--no-llm` keeps the scan local except for SkillSpector's OSV dependency lookup.
- If provider details seem stale, defer to the upstream README links above.
