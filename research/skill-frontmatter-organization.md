# Skill Frontmatter Organization Research

## Recommendation

The best default is a split model:

- Keep `SKILL.md` frontmatter minimal and portable.
- Put descriptive metadata such as `version`, `author`, `homepage`, and `repository` under `metadata`.
- Put host-specific behavior in a namespaced metadata block or, when the host supports it, a sidecar manifest.
- Prefer sidecar manifests over frontmatter for UI-only or dependency-only configuration when the platform explicitly supports that pattern.

This gives you the best tradeoff between:

- compatibility with the [Agent Skills spec](https://agentskills.io/specification)
- portability across OpenAI, Anthropic, Hermes, GitHub Copilot, and registry ecosystems
- clean separation between agent-facing instructions and host/runtime integration details

The core reason is simple: the common denominator across ecosystems is small, but many products add their own frontmatter extensions. If you treat top-level frontmatter as the shared ABI and treat everything else as metadata or sidecar config, you avoid the most common portability failures.

## Recommended Canonical Format

```yaml
---
name: api-debugging
description: Diagnose API failures, request mismatches, and auth problems. Use when the user mentions API errors, bad responses, failed requests, or integration debugging.
license: Apache-2.0
compatibility: Requires network access and either curl or a language runtime available in the workspace.
allowed-tools: Bash Read Write WebSearch
metadata:
  version: "1.0.0"
  author: "Example Team"
  homepage: "https://example.com/skills/api-debugging"
  repository: "https://github.com/example/skills"
  tags:
    - api
    - debugging
    - integrations
  openclaw:
    primaryEnv: API_TOKEN
    requires:
      env:
        - API_TOKEN
      bins:
        - curl
  hermes:
    tags:
      - api
      - debugging
---
```

This example is intentionally frontmatter-only. The point here is to show the recommended metadata split, not to prescribe a full skill body structure.

## Why This Format Is Best

### 1. It matches the spec's center of gravity

The [Agent Skills specification](https://agentskills.io/specification) defines a very small standardized top level: `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`. Its own optional example places `version` under `metadata`, not at the top level.

That makes `metadata` the safest home for descriptive fields that are useful but not behaviorally essential.

### 2. It survives stricter validators

Some ecosystems accept extra top-level keys. Some do not.

Anthropic's public docs and examples are mostly minimal, and an [Anthropic repo issue about skill validation](https://github.com/anthropics/skills/issues/37) shows a real failure mode: frontmatter keys such as `version` and `author` caused packaging/import failures in a Claude surface that only accepted `name`, `description`, `license`, `allowed-tools`, and `metadata`.

If you want one format that travels well, assume the stricter validator exists.

### 3. It separates shared semantics from host integration

OpenAI's Codex docs recommend a minimal `SKILL.md` and move UI/dependency behavior into [`agents/openai.yaml`](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md). That is the cleanest architecture in this survey: keep skill instructions portable, keep product integration separate.

Even when a platform does not yet offer a sidecar manifest, the same design still holds conceptually:

- top-level frontmatter for portable semantics
- `metadata.<vendor>` for product-specific configuration

### 4. It reduces accidental trigger and context costs

OpenAI and Anthropic both emphasize that `description` is the main trigger surface. That means top-level frontmatter should optimize for invocation behavior first, not catalog completeness. Treat the top level as "what helps the agent find and run the skill correctly," not "all metadata we might want to store."

## Field Policy

### Mandatory

These are the fields you should treat as effectively mandatory for any serious shared skill:

- `name`
- `description`

Why:

- The [Agent Skills spec](https://agentskills.io/specification) requires both.
- [OpenAI Codex](https://developers.openai.com/codex/skills) says `SKILL.md` must include `name` and `description`.
- [Anthropic's skills repo](https://github.com/anthropics/skills) says the frontmatter requires only those two fields in the basic template.
- [GitHub Copilot skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) also document `name` and `description` as the minimal required pair.

### Optional, but Recommended

These should usually be present in a portable public skill:

- `license`
- `metadata.version`
- `metadata.author`
- `metadata.homepage`
- `metadata.repository`

Recommended because:

- `license` is standardized, low-risk, and useful for reuse.
- `version`, `author`, `homepage`, and `repository` are genuinely useful catalog metadata.
- Keeping them under `metadata` preserves the information without overfitting to a permissive parser.

Usually recommended when relevant:

- `compatibility`
- `allowed-tools`

Use `compatibility` only when the environment assumptions matter enough that a user or host needs to know them up front.

Use `allowed-tools` when your target runtime actually consumes it. The spec includes it as experimental, Anthropic and Claude Code document it, and GitHub/OpenAI ecosystems may have analogous approval patterns. Still, it should represent real execution policy, not decorative documentation.

### Optional, but Usually Dismissible

These are useful only in specific ecosystems and should usually stay out of the portable top level:

- `argument-hint`
- `when_to_use`
- `arguments`
- `user-invocable`
- `disable-model-invocation`
- `disallowed-tools`
- `model`
- `effort`
- `context`
- `agent`
- `paths`
- `hooks`
- `platforms`
- top-level `version`
- top-level `author`

Why these are usually dismissible:

- They are runtime- or UI-specific, not core skill semantics.
- They are not part of the shared cross-vendor core.
- Several of them are product extensions from Claude Code or Hermes, not broadly portable conventions.

### Best Practice for Vendor-Specific Data

If you need host-specific information, prefer one of these:

1. Sidecar manifest, if the host supports it.
2. `metadata.<vendor>` namespaced block, if no sidecar exists.

Examples:

- `agents/openai.yaml` for OpenAI Codex
- `metadata.openclaw` for OpenClaw/ClawHub
- `metadata.hermes` for Hermes tags/config that do not need to be portable

## Practical Rules

### Put At The Top Level

Keep the top level for fields that are both:

- standardized or broadly accepted
- directly involved in discovery, permissions, or compatibility

The safe portable top-level set is:

- `name`
- `description`
- `license`
- `compatibility`
- `metadata`
- `allowed-tools`

### Put Under `metadata`

Put catalog and provenance data here:

- `version`
- `author`
- `homepage`
- `repository`
- generic tags
- publishing provenance
- vendor-specific metadata blocks

### Put In Sidecar Files

Put these outside `SKILL.md` when your platform supports it:

- display name
- short UI description
- icons
- brand color
- dependency manifests
- invocation policy that is product-specific
- MCP wiring or tool transport configuration

This keeps the skill document focused on what the model should know, while the host reads the mechanical integration data separately.

## Source-by-Source Findings

### 1. Agent Skills Spec (`agentskills.io`)

Source: [Specification](https://agentskills.io/specification)

Findings:

- The spec standardizes a small frontmatter surface.
- Required fields: `name`, `description`.
- Optional fields: `license`, `compatibility`, `metadata`, `allowed-tools`.
- `metadata` is explicitly an arbitrary key-value mapping.
- The official optional example puts `version` and `author` under `metadata`.

Implication:

- If you want the most standards-aligned answer to "where should `version` live?", the spec itself points to `metadata`, not top-level frontmatter.

### 2. OpenAI

Sources:

- [Codex skills docs](https://developers.openai.com/codex/skills)
- [OpenAI skills repo](https://github.com/openai/skills)
- [OpenAI `agents/openai.yaml` reference](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md)

Findings:

- OpenAI documents a minimal skill structure: a directory with `SKILL.md`, optional `scripts/`, `references/`, `assets/`, and optional `agents/openai.yaml`.
- `SKILL.md` must include `name` and `description`.
- OpenAI explicitly uses `agents/openai.yaml` for appearance metadata, tool dependencies, and invocation policy.
- This means OpenAI does not push you toward putting UI/dependency metadata into frontmatter.

Implication:

- OpenAI is the cleanest example of separating portable instructions from host configuration.
- If you are designing your own convention, this is the architecture worth copying.

### 3. Anthropic / Claude / Claude Code

Sources:

- [Anthropic skills repo](https://github.com/anthropics/skills)
- [Claude Code skills docs](https://code.claude.com/docs/en/skills)
- [Anthropic validation issue on unexpected frontmatter keys](https://github.com/anthropics/skills/issues/37)

Findings:

- Anthropic's public repo presents the minimal template with `name` and `description`.
- Claude Code extends the base format with many product-specific frontmatter fields such as `argument-hint`, `user-invocable`, `disable-model-invocation`, `context`, `agent`, `paths`, `hooks`, `model`, and others.
- Claude Code explicitly says only `description` is recommended and that frontmatter fields are optional in its product context.
- A real validator/import path in the Anthropic ecosystem rejected extra top-level keys like `version` and `author`.

Implication:

- Anthropic has two overlapping realities:
  - a portable core that is strict and small
  - a product runtime with many powerful extensions
- If you want Anthropic-only ergonomics, extra top-level keys can be useful.
- If you want portability, do not treat Claude Code's extended top level as a universal pattern.

### 4. Hermes

Source: [Hermes skills docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)

Findings:

- Hermes documents a broader top-level schema than the common spec.
- It explicitly includes top-level `version`, `author`, and `platforms`.
- It also documents `metadata.hermes.tags` and `metadata.hermes.config`.
- Hermes installs skills from GitHub repos and treats them as a richer registry-style package format.

Implication:

- Hermes is more permissive and package-oriented than OpenAI or the strict Anthropic paths.
- Hermes proves that top-level `version` and `author` are a valid ecosystem choice, but not a portable baseline.

### 5. GitHub Copilot Skills

Source: [GitHub Copilot skill docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)

Findings:

- GitHub documents a minimal `SKILL.md` with YAML frontmatter and a Markdown body.
- It explicitly requires `name` and `description`.
- It documents `license` as optional.
- The examples stay lean and do not present `version` or `author` as part of the core format.
- GitHub CLI skill workflows support versioned install/publish behavior at the repository/package level rather than making top-level frontmatter carry all of that.

Implication:

- GitHub's docs reinforce the "minimal frontmatter, external publishing metadata elsewhere" pattern.

### 6. OpenClaw / ClawHub

Source: [OpenClaw skill format](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md)

Findings:

- OpenClaw accepts YAML frontmatter and uses `description` as registry/search summary.
- It explicitly documents runtime requirements under `metadata.openclaw`.
- It shows `version` as a common frontmatter field in examples.
- It uses the metadata block for environment variables, binaries, install specs, emoji, homepage, OS restrictions, and related packaging/runtime information.

Implication:

- OpenClaw is a good example of pragmatic vendor namespacing inside `metadata`.
- If you cannot rely on sidecar files, `metadata.<vendor>` is a workable pattern.

## Cross-Ecosystem Summary

| Ecosystem | Minimal required core | Permissive top-level extras | Vendor metadata pattern | Best takeaway |
| --- | --- | --- | --- | --- |
| Agent Skills spec | `name`, `description` | `license`, `compatibility`, `metadata`, `allowed-tools` | `metadata` | Use as portability baseline |
| OpenAI | `name`, `description` | very lean `SKILL.md` | sidecar `agents/openai.yaml` | Best separation of concerns |
| Anthropic / strict validators | `name`, `description` | often strict | `metadata` | Assume stricter validation if portability matters |
| Claude Code | `description` recommended, many optional extensions | many | frontmatter extensions | Good product ergonomics, weak as universal baseline |
| Hermes | richer package-style top level | `version`, `author`, `platforms` | `metadata.hermes.*` | Valid richer schema, but ecosystem-specific |
| GitHub Copilot | `name`, `description` | `license` optional | mostly minimal examples | Keep core frontmatter lean |
| OpenClaw | common YAML frontmatter | examples include `version` | `metadata.openclaw` | Good namespaced metadata model |

## Final Recommendation

If you want one convention that holds up well across toolchains:

1. Treat top-level frontmatter as a portability surface, not a dumping ground.
2. Keep `name` and `description` mandatory.
3. Keep `license`, `compatibility`, and `allowed-tools` top-level only when they are actually meaningful.
4. Move `version`, `author`, `homepage`, and `repository` under `metadata`.
5. Put vendor-specific config under `metadata.<vendor>` unless the host offers a proper sidecar manifest.
6. Prefer sidecar manifests for UI, dependency, and invocation policy when possible.

In short:

- `version` belongs in `metadata` by default.
- `author`, `homepage`, and `repository` also belong in `metadata` by default.
- Top-level frontmatter should stay as small as possible unless you are optimizing for one specific runtime instead of portability.
