# Evaluations and optimization

Public task definitions travel with each skill under `skills/<name>/evals/`.
Runtime instructions, references and scripts remain independently installable.
Generated workspaces, provider state and full traces do not belong in a skill.

This layout adapts the Agent Skills [output evaluation guide](https://agentskills.io/skill-creation/evaluating-skills),
[description optimization guide](https://agentskills.io/skill-creation/optimizing-descriptions)
and [specification](https://agentskills.io/specification). `evals/evals.json` and
separate iteration workspaces follow those examples. The repository-wide study
registry, GEPA records, archive policy and extra metadata are local conventions.

## What is committed

```text
skills/<name>/
  SKILL.md
  references/                   # Runtime resources
  scripts/                      # Runtime helpers, when actually useful
  evals/evals.json               # Public prompts, expected outputs, assertions
  evals/files/                   # Public input fixtures
  evals/trigger-queries.json     # Separate discovery queries, when authored
benchmarks/
  index.json                    # All known studies and their availability
  harness/                      # Small reusable infrastructure
  <name>/studies/<study-id>/
    study.json                  # Frozen models, conditions, budgets and sources
    protocol.md
    optimization/               # Method, candidate lineage and decision
    results.json                # Every compact per-record result
    results.csv
    benchmark.json              # Per-model/configuration aggregates
    report.md
    source-manifest.json
    artifacts.json              # Raw archive checksum and access status
.benchmark-workspaces/           # Ignored generated files
  <name>/<study-id>/iteration-1/<model>/<case>/<condition>/<repetition>/
    outputs/
    timing.json
    grading.json
    trace.jsonl
```

Create a new study directory for new inputs, model settings, grader rules or
budgets. Do not rewrite old results into a new study or overwrite earlier
iterations. Record the exact evaluated case IDs: a GEPA minibatch is not a full
suite. Preserve failed and infrastructure attempts with their admission status.

The committed btcdeb records are historical exports, not new model runs. The
original dated directories remain in place and are ignored; their absolute
paths and original hashes have not been rewritten. Hosted Nowhere already has
committed study artifacts at its original path and is indexed without migration.

## Runtime packaging and task inputs

Use the runtime-only builder before a student evaluation:

```sh
mkdir -p .benchmark-workspaces/btcdeb/example
python3 benchmarks/harness/package.py skills/btcdeb \
  .benchmark-workspaces/btcdeb/example/skill
```

It includes `SKILL.md` plus `scripts/`, `references/`, `assets/` and `agents/` when
present; it excludes `evals/`, tests and benchmark metadata, and rejects runtime
symlinks. Resolve helper paths from the installed skill directory. A normal
skill installer may copy evals too: the evaluation runner must use this explicit
packaging boundary rather than giving the student the repository checkout.

Only pass the selected prompt and its input fixtures to the student. In public
evals, `fixture_destinations` maps authored fixture paths to names in the task
workspace. Keep `expected_output`, `assertions`, domain `checks`, graders and
held-out final data parent-only. The builder is not a filesystem/network sandbox;
the runner must enforce those access restrictions separately.

## Two distinct evaluation loops

**Discovery:** install/register the skill and observe actual `SKILL.md` activation
for positive queries and near-miss negatives. Keep query splits fixed and repeat
runs to estimate trigger rate. The btcdeb trigger queries are authored but
unexecuted; no triggering improvement is claimed.

**Output quality:** run identical tasks with the skill and an appropriate
baseline. For a new capability, compare no skill; for revisions, freeze and use
the old skill. Record model, effort, condition, task, repetition, package hash,
dataset/grader versions, budgets and network policy. Existing study conditions
include `skill-offline`, `offline-no-skill` and `web-no-skill`; never combine them.

Record per-run duration and usage immediately. `timing.json` may extend the guide's
minimal example with input, cached input, output, reasoning, provider-specific
cache creation, lower-bound flags, and explicit null/reason for unavailable usage.
Cached input is already included in normalized input; reasoning is already in
output. Keep teacher, reviewer and orchestration costs separate. Do not insert
zero for an unavailable measurement.

`grading.json` records each assertion's result and concrete evidence. Use code
for mechanical checks and reviewed evidence for claims such as actual execution
and a central explanation. Keep original completion, automatic checks and
secondary quality issues separate; changing a grader requires a new labeled cohort.
Present case-level rows as well as per-model side-by-side completion, time and
token comparisons. Include failed attempts in expenditure; successful-only
latencies compare different subsets unless explicitly paired.

## Optimization and promotion

Put optimizer configuration, exact prompts/responses or their archived hashes,
parent/candidate identities, evaluated cases and selection decisions under the
study's `optimization/` directory. GEPA is one optional optimizer; it is not a
repository-wide runner or an automatic release process.

Freeze train/search/final access boundaries before inference. Use globally
split-qualified cache keys (`train/B05`, `validation/SV01`); verify cached package,
case, model, limits and record hashes. Retain original usage once when reusing a
measurement. Audit reported validation against the actual evaluated case IDs.

Inspect the candidate, freeze an eligible package, then open final tests.
Promotion follows the declared per-model gate, never the optimizer's mean alone.
A negative result is valid evidence: retain the baseline and record no promotion.
The btcdeb GEPA study ended this way; its final cases remain sealed.

## Evidence archives and access gaps

Only filtered local archives were created for the two btcdeb legacy studies.
They are not uploaded or available from a fresh clone. Each `artifacts.json`
gives the relative local filename, SHA-256, size, coverage and retrieval status.
Ask the study maintainer for that exact file through an approved transfer channel;
place it at the recorded local path, then verify without extracting:

```sh
python3 benchmarks/harness/archive.py verify /path/to/evidence.tar.gz \
  --sha256 <archive_sha256-from-artifacts.json>
```

Create a new archive without changing or deleting the original directory:

```sh
mkdir -p .benchmark-workspaces/archives
python3 benchmarks/harness/archive.py create /path/to/closed-study \
  .benchmark-workspaces/archives/new-evidence.tar.gz
```

The in-archive inventory hashes every included regular file and lists omitted
boundaries. No symlinks are followed. Named auth-state/cache directories, copied
executables and sealed-final/fresh holdout-authoring files are omitted; originals
are retained. This path policy is not a transcript secret scanner. Archives are
captured sequentially from closed studies, not an atomic filesystem snapshot.
No portable historical replay is promised without the archive, pinned tools,
original access assumptions and reconstruction of original paths. Compact
results alone cannot replace full trace review.

## Fast checks and model execution

```sh
python3 -m unittest discover -s tests/benchmark_harness -v
node --test tests/benchmark_harness/test_telemetry.mjs
./scripts/validate_skills_ref.sh skills/btcdeb/SKILL.md
```

PR CI runs deterministic packaging, fixture, cache, telemetry, archive and result
contract checks. Skill-schema validation uses a pinned `skills-ref` revision.
No paid/model evaluation is launched by importing these modules, running tests,
opening a PR or merging. Real model runs require an explicitly budgeted study,
fresh contexts, owned-resource coordination and appropriate isolation. The
historical host-specific CLI runners remain in their archives; this small shared
layer does not pretend to replace them.
