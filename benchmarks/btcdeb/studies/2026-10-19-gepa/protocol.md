# GEPA evolution protocol — predeclared before student inference

This study extends the completed 2026-10-18 study without changing its runs,
metrics, snapshots or grading. The current skill, including metadata, is frozen
under snapshots/seed. All 20 previously exposed cases are training data here.

Official gepa==0.1.4 optimize_anything evolves only the SKILL.md body, with a
500-word entrypoint limit and 3000-word Markdown / 42000-byte package limits.
Original metadata and five domain references stay fixed. A separately tested,
frozen stdlib Python execution helper and 412-word usage reference are optional
catalog components, included only when the evolved body links them. This measures
a combined GEPA/instruction/helper intervention, not a pure-prose causal effect.
No per-case answers, IDs, fixture bytes or task-result schemas may enter the skill.

Student models and conditions are unchanged: Claude CLI Haiku, and local
incoai/Qwen3.8-27B-Splash through OMP only. Each receives a fresh isolated context,
read/write/bash tools, no internet, the selected readonly skill and public fixtures.
The old H2 runner supplies 240-second, 24-turn and 64-tool caps; OMP has 32768
context and 4096 per-request output tokens. One Qwen queue; Haiku may overlap.
Do not treat infrastructure errors as model failures. Failed infrastructure
attempts remain recorded and excluded with reasons; any retry is a new attempt.

GEPA uses fresh Codex app GPT-6.1 Sol/high reflection subagents. The app route
passed its exact-model smoke. User explicitly prohibits gpt-6-sol; its earlier
transport-only smoke is excluded, and no proposals were generated with it.
The CLI rejected gpt-6.1-sol, so there is no model fallback. A request/response
bridge supplies only the exact GEPA prompt to a fresh reflection agent, with no
tools/network or sealed final data. Prompts, responses, agent identity and wall
time are retained. The collaboration API does not expose provider token usage;
reflection tokens are unavailable, not zero or GEPA character estimates.
Student token/time measurements remain unchanged and separate.

Initial search budget: three proposals, at most 32 paired metric calls; seed19,
Pareto candidate selection, hybrid scalar/per-model frontier. Each metric is the
mean of two strict binary completion judgments. Side objectives retain separate
Haiku and Qwen completion. Reflection batches of two prioritize known training
failures B05/B08, B10/B17, B07/B15. Four fresh search-validation cases drive
selection; they are not final tests. Partial progress is diagnostic only.

Completion requires deterministic artifact checks AND independently reviewed
actual operation evidence AND the central explanation requested by the prompt.
Reviewers inspect immutable tool traces and delivered files/final responses.
Private reasoning and correct-looking JSON alone do not count. Helper output
can substantiate execution but does not replace a requested result schema.
Model-assisted reviews are not human-calibrated or blinded; report this limit.
Review annotations bind exact tools.jsonl hashes, identify evidence, and remain
outside student workspaces. Record automatic checks and reviewer decisions
separately. Parent adjudicates genuine checker/reviewer ambiguity explicitly.

Selection gate: compare each candidate on identical search-validation cases.
Prefer a candidate improving completion for both models over the seed. A model
at the validation ceiling may retain its ceiling while the other improves;
otherwise require both to improve. Never hide a per-model regression behind a
mean. Final promotion still requires improvement for both on the final set.
If no eligible improvement, continue only on training/search-validation,
versioning the search extension; do not
inspect sealed final cases to guide changes. Ties favor worst-model completion,
then mean completion; size/cost are secondary, never rewards for faster failure.
Inspect candidate instructions for reusable correctness before final freeze.

After a concrete finalist is frozen, unseal the eight independently authored
final cases. Run matched seed/finalist conditions twice per case and model,
with counterbalanced condition order and identical caps. Do not tune on final
failures. Report completion counts, paired transitions, case-specific failures,
measured time and token usage with missing/lower-bound flags. Distinguish all-run
latency from successful-run latency. This small convenience sample supports a
local finding, not a general statistical guarantee. Preserve unsuccessful attempts.
Promote only truthful, reusable changes with evidence of improvement for both.

Skill size and actual progressive-disclosure reads are reported separately.
No old-study internet/offline baseline is relabeled as a new matched comparison.
Stop only the new owned Splash server/engine after all runs complete.
