# btcdeb skill benchmark protocol

## Research question

How well do fresh small-model agents complete practical btcdeb workflows with a progressively disclosed skill and no tool Internet access, compared with the same models with Internet access but no skill, and with neither skill nor Internet access?

Execution history: `v1-development` is an excluded 36-attempt diagnostic batch. A context-window/output/accounting defect prompted a full restart under corrected harness H2 with unchanged skill v1; see `oracle/harness-h1-deviation.md`. Scored phases use the `h2-` prefix. All original records remain available separately.

## Arms and isolation

- skill-offline: skill entrypoint plus discoverable mode-specific references; tool network denied.
- web-no-skill: no skill or local reference documentation; Internet retrieval allowed.
- offline-no-skill: no skill or local reference documentation; tool network denied.

All arms have identical preinstalled btcdeb/btcc/tap binaries and neutral raw fixtures. Tool help is available in every arm because it is part of the software. No arm gets prior chat history, expected answers, graders, other benchmark outputs, repository context, personal files, or unrelated skill metadata. Use the same minimal system prompt and custom tool schemas across models/arms, with network availability and the skill path as the only condition changes. Model API authentication/inference is not agent tool Internet access.

Codex and Claude use a shared custom MCP server; OMP Qwen uses the same broker through custom tools. Model runner differences remain a measurement limitation.

The harness owns configuration outside agent-writable directories. File tools resolve symlinks and enforce workspace containment. Every command executes inside an OS sandbox restricting filesystem access; offline tools also deny networking. Online tool access retains the same filesystem restrictions. Test these restrictions with allowed/denied probes before model runs. Log attempts, including denied accesses. Record any imperfect isolation as a limitation rather than claiming a closed-book result.

## Models

- Codex CLI gpt-6-luna with high reasoning.
- Claude CLI Haiku: exact model/date recorded after authentication; never substitute another model silently.
- OMP splash/incoai/Qwen3.8-27B-Splash: use a supported reasoning level and record it (installed catalog advertises low/medium/xhigh, not high). User's high requirement applies to Luna.

Use the same model and reasoning per arm. No automatic model switching, fallback delegation, or continuation across cases. Fresh sessions, empty contextFiles and discovered skills, no global extensions/rules, and no LSP/browser/computer/subagent tools. API credentials remain inaccessible to model tools and are never copied into logs.

## Dataset and split

Three failure-oriented dimensions are specified in user-stories.md. The user confirmed all twenty draft tuples on 2026-10-18 under the invoked generate-synthetic-data workflow. Natural-language task queries were generated in a separate pass after that review, checked against each tuple and frozen before launch. Ten additional tuples are retained as an unscored reserve.

Frozen split: development B01/B02/B03/B05/B06/B08/B09/B10/B12/B13/B17/B18; holdout B04/B07/B11/B14/B15/B16/B19/B20. Preserve the split and task bytes across all arms. Use development traces for improvements; inspect held-out results only after freezing the revised skill. Record any later deviation. Each model/arm/case is one independent attempt. The full 20-case, three-model, three-arm initial matrix is 180 attempts; missing provider access is reported as unavailable, never as a model failure or a zero-token run.

## Oracle checks before launch

For executable cases, independently replay expected behavior with pinned actual binaries. Include positive, negative, and boundary cases. Verify fixture transaction IDs, input indices, amounts, script version, expected stack/error, and any mutation. Check the grader itself against deliberate correct and incorrect submissions, including false-stack/exit-zero confusion and mocked-signature overclaims. Separate compile/encoding checks, interpreter outcomes, script-spend success, and Bitcoin Core consensus/policy validation. Do not infer one from another.

Prompts state required artifacts and any missing data deliberately. Acceptance must follow the prompt, not unstated stricter rules or incidental reference quirks. Record tool version/source/build and executable hashes. The Nix package version label can differ from the binary's reported version; preserve both.

## Timing, tokens, and completion

Start elapsed time immediately before fresh session creation; stop after the final model turn or the hard run limit. Separately record setup/toolchain preparation time, request/tool timings where available, and whether a run was cold or warmed. Interleave arm order deterministically within each model to reduce cache/order effects. Serialize local Qwen runs to avoid GPU contention; label wall-time comparisons across runtimes as observational.

Frozen shared limits are 240 seconds and 64 tool calls per attempt. Claude and OMP also have a 24-model-turn cap; OMP has a 4096-token per-response cap. Codex lacks equivalent native model-turn/output caps. This asymmetry is retained rather than hidden. A timeout measures completion within the declared budget, not eventual capability. SDK deadlines can leave outer `timed_out` false; derive budget exhaustion from provider timeout/error telemetry as well.

Capture complete model event traces (including emitted reasoning when supplied), tool names/arguments/results, final response, generated artifacts, prompts/configuration, tool/skill/fixture hashes, provider/model/reasoning, start/end UTC timestamps, elapsed seconds, turn count, timeout/error state, and token usage. Token metrics include input, output, cache read/write, and reasoning when exposed. Missing fields are null, not zero. Do not add reasoning tokens twice when included in provider output tokens. Report total input+output and uncached input+output where definitions permit; do not equate provider-specific billing units across models. Do not claim identical cache conditions unless verified.

A completed process is not a completed task. Code graders check actual artifacts and re-execute relevant scripts/vectors. Record functional checks and required workflow evidence separately, then manually inspect traces and explanations for overclaims or incomplete requirements. A task intentionally missing required data can succeed by correctly identifying the blocker. Infrastructure/provider errors are reported separately from model completion rates, with both attempted and evaluable denominators.

## Diagnosis and improvement

Keep every initial run and received skill snapshot immutable. For each failed/slow run, locate the first relevant error and inspect the exact reference content available/read before it. Attribute as agent, skill, harness/grader, environment/provider, mixed, or unresolved. Adequate guidance ignored by a model is not automatically a skill defect. Ordinary recoverable code mistakes do not justify case-specific instructions.

Make narrow, generalizable changes for demonstrated incorrect facts, ambiguities, missing prerequisites, or defensible repeated-agent guardrails (label the latter). Measure entrypoint, individual reference, and total package bytes/tokens; use actual read traces to measure loaded reference cost. Avoid making every model read all files.

Freeze revision 2 before its evaluation. Re-run affected development cases and at least some unchanged controls under identical limits; include matched revision-1 repeats if causal claims are desired. Evaluate held-out cases only after revision freeze. Single retries can show improvement in an observed run, not causal or statistical superiority. Report tradeoffs among completion, time, tokens, and skill size, plus case-level results and access audit.

## Timing accounting clarification from frozen H2 source

The configured run budget is 240 seconds; it is not an identical strict wall cap across transports. OMP has its own 240-second SDK deadline/abort timer. The parent process wrapper kills any remaining CLI at timeout_seconds+10 (250 seconds), then waits up to 5 seconds before SIGKILL. Codex/Claude have the same outer guard and their documented other limits. This source behavior is unchanged across all H2 arms/revisions. Actual measured elapsed values are retained, never trimmed to 240, and no new retrospective completion cutoff is imposed. See oracle/timing-accounting.json.

Per-attempt elapsed starts immediately before spawning the model process, after workspace copying and adapter filesystem preparation. It includes CLI/request startup, model and tool work. A complete one-time toolchain/server setup duration was planned but not captured and remains null; setup time is not claimed in run medians or invented from partial timestamps. This is an accounting limitation, not a change to frozen tasks, tools or scored acceptance.
