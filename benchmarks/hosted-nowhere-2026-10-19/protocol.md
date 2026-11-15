# Hosted Nowhere end-to-end acceptance

The push gate is a completed pass of every story in `stories.json` on each of:

- a fresh Codex `gpt-6-luna` agent, reasoning `high`;
- a fresh Claude CLI Haiku session (actual dated model recorded);
- a fresh Qwen session launched through the user's `somp` shell function,
  `splash/incoai/Qwen3.8-27B-Splash`, reasoning `low` by default. The fresh
  Chat replay uses supported `medium` effort after diagnostic-only low-effort
  interruptions. Actual effort is recorded per row; the model is unchanged.

No model is substituted silently. Every scenario gets a fresh workspace, frozen
skill snapshot, fresh conversation, disposable identities and isolated local
services. Qwen scenarios run serially to avoid local inference contention.
Initial model context contains the skill, scenario raw inputs, and generic
tool/environment instructions. Public CLI/runtime files are readable for process
execution and can be inspected through the tools; this is functional workflow
acceptance, not a skill-only knowledge test. Graders and other runs remain
outside the tool sandbox. The same read/write/bash broker is used by
all runners. Tool subprocesses are restricted to loopback networking; npx uses a
prewarmed package cache, and browser access goes through the restricted helper.
Models can use a generic browser helper for actual headless Chrome
interaction, including screenshots and DOM observations; it has no app-specific
selectors or implementation of the requested task.

Nostr writes target an isolated in-memory relay. Ephemeral events are forwarded
to current subscribers and not retained. A separate rejecting endpoint exercises
failure handling. Relay event journals remain outside the model workspace.
Lightning resolution and rate lookups cross an explicitly simulated network
boundary; invoices are visibly TEST_ONLY strings and no real payment is made.
The production Hosted Nowhere renderer and builders are used for browser checks;
public WebSocket relay traffic is blocked in that browser.

Assertions use CLI decoding, artifact contents, local relay/service observations,
and real browser observations. Merely reporting success is not a pass. Safety and
limitation explanations also receive manual review. Failures are retained. Skill
fixes require fresh affected runs. The final gate requires a full matrix using
the final skill or an explicit trace-bound audit proving the instructions loaded
by an earlier run are byte-identical. Infrastructure failures are classified separately and
rerun without treating them as evidence of skill correctness. A functional failure
may receive a fresh unassisted replay of the identical story and skill; the report
retains every failed attempt and separately counts first-attempt completion. A
replay does not rewrite a failure as a first-attempt pass.

Coverage spans all eight routes, preservation of unrelated content/arrays,
signed/encrypted updates, identity checks, methods/invoices, owner-only review and
CSV export, forum post/reply/torrent/chat/room flows, Store's deprecated status
and legacy checkout/status flows, browser-only creation, stale share links, and
malformed input/rejected relay recovery. NIP-46 remote signer setup uses a disposable local protocol fixture. Live payment
settlement is outside the skill’s invoice-generation scope and is never claimed.
The final report distinguishes these controlled protocol checks from real-world
relay retention, signer deployments, and payment-provider availability.

## Reproduction and evidence

The E2E harness targets the author's macOS environment: `sandbox-exec`, Python,
Node/npx, Codex CLI, Claude CLI, Chrome, and the installed OMP runtime are required.
`harness/suite.py` declares the runtime/cache paths. Warm the npm cache with the
pinned package before starting; tool subprocesses have loopback-only networking
and offline npm resolution. Native model transports remain outside that sandbox.

```sh
python3 harness/suite.py --batch UNIQUE_NAME --models luna,haiku,qwen
```

Run from this benchmark directory, or use the full harness path. A batch freezes
both the skill and stories. `--resume --models qwen` can add a fresh lane to that
same batch; existing cells are never overwritten. The Qwen adapter uses a fresh
OMP state directory with a truthful 32K context and 4K generation limit, and
same-model text summarization. It still invokes the user's `somp` function. No
global model settings or host signer configuration are edited.

After reviewing final responses and relevant browser evidence, record primary-
agent review decisions in the batch's `reviews.json`. Export compact results with:

```sh
python3 harness/regrade.py /private/tmp/hosted-nowhere-e2e/runs/UNIQUE_NAME
python3 harness/report.py /private/tmp/hosted-nowhere-e2e/runs/UNIQUE_NAME .
# For retained fresh replays, append --replay /private/tmp/hosted-nowhere-e2e/runs/REPLAY_NAME
```

The regrader preserves first verdicts and records the current oracle hash. The
exporter exits successfully only when every technical check, review, model
identity, frozen skill hash (or audited unchanged inputs), and oracle hash passes. It copies no auth state or raw logs.
A final regrade uses one oracle revision across all cells; preserve original
verdicts when correcting an assertion using unchanged observations. The oracle
compares exact decoded content and ordered rendered lines (Drop inserts line
numbers), and recognizes identical fragments on either official renderer origin.
It accepts a story's requested metadata format rather than inventing additional
output files or key names. It still requires real CLI JSON where expressly asked.

Stories remain identical within a revision. An explicitly recorded raw-input
clarification requires fresh affected runs on all three models; selected runs
must match the final story object exactly. Other story objects must remain
identical. Skill snapshots retain their original hashes.
Final-v7 changed only `references/art.md`; Art passed freshly on all three
models. Final-v8 appends a Petition clarification: CLI relay selection does not
reconfigure browser observations, and a count mismatch does not justify another
submission. Petition is retested freshly on all three. Qwen's unstarted N07–N18
also use final-v8. Its unfinished superseded v6 Art and v7 Petition runs are
retained as operator interruptions, separately from functional failures.
Unaffected final-v6/final-v7 cells qualify only
after primary-agent inspection of every tool input, including shell scripts,
argv and writes, proves no changed instruction content was read. Explicit loaded
files must be byte-identical; content-search outputs spanning a changed file
must be independently compared (path order normalized for recursive searches;
matching lines and line numbers remain exact). Unknown/dynamic accesses require a fresh run.
The audit binds both snapshots and the complete tool/context traces with hashes
in `instruction-equivalence.json`; pass `--equivalence` with that file to the
exporter. `same_skill` remains false for such cells, and their source hash and
full audit record remain visible. No older substantive revisions qualify.
The validator independently checks completeness of direct broker instruction
reads; shell/helper reads require the explicit manual audit. Directory reads
expose only unchanged filenames. The audit may omit inert quoted data heredoc
bodies from its display, while retaining every executable/file-access input and
the full original trace hash.

The latest attempt for a replayed cell must pass every gate; earlier failures and
review notes are included in results.json and the summary reports replay counts.

A provider session limit stops that model's lane; remaining cells stay pending.
Attempt directories without completed runner metrics are retained as incomplete
attempts and cannot be hidden by selecting an earlier passing attempt.

Qwen's initial bound was 1800 seconds. After two deadlines with expensive native
compaction, the continuation and fresh Qwen replays use 3600 seconds; all original
failures remain. The just-started N08 base attempt was explicitly stopped during
that transition and retained as an operator interruption. The skill/story
snapshots, Qwen model, low effort and tool capabilities stay identical. Per-row
launch budgets are exported alongside actual runtimes.

SOMP may emit a genuine final assistant `stop` reply and then run automatic
post-answer compaction before its process exits. The controller recognizes only
a nonempty native final-stop reply with no tool calls followed by compaction;
subsequent tool work invalidates that marker. It cancels that post-answer
maintenance, preserves the real process exit code, records the final event/hash
in `controller-completion.json`, and reports logical `normal_completion`. All
app/artifact/relay/browser assertions and manual final-answer review still apply.
Errors before the final answer remain errors; post-completion cleanup errors are
recorded separately. The shared Splash daemon is excluded from cleanup.

The initial model prompt did not explicitly describe the already-enforced
loopback/offline/public-WebSocket boundary. After Qwen investigated unavailable
browser relay state, remaining fresh runs receive that neutral environment
description. No app-specific expected values, outcome hints, tool capabilities or
acceptance checks change. Earlier outcomes remain actual tests under the same
network policy; this is not claimed to be an identical-prompt model comparison.
Each row exports its original system-prompt hash and network policy. The active
v8 N07 attempt finishes under its original prompt and deadline; the old queue is
paused only to prevent unstarted cases from inheriting the missing disclosure.
Its agent, controller and fixture remain uninterrupted. Once collected, fresh
N08–N18 run in `final-v8-env` with the explicit environment facts.

Final-v9 adds only a Forum reference paragraph explaining that the header and
enabled features decode from the URL without relay registration, while live
activity needs separate browser relay connectivity. A CLI override does not
configure the browser. Empty browser activity is reported separately from CLI
readbacks; it does not justify changing namespaces or publishing again. This
clarifies general app behavior confirmed by the upstream architecture, not a
fixture-specific answer. All four Forum stories (N07, N08, N09, N15) are retested
freshly on all three runners. Thirty-four completed non-Forum cases qualify
through trace-bound unchanged-instruction audits, including the three final-v8
Petition tests. Original hashes and earlier failures remain visible.

The ongoing original final-v8-env Qwen N08 keeps its full deadline and original
prompt/skill. Only its queue parent is paused. After its outcome is collected,
fresh final-v9 Qwen N07–N18 starts serially. The waiting v8 N07 replay watcher was
canceled before starting an agent; N07 instead retests on final-v9.

N15's original title was unquoted. Two independent Haiku runs parsed "against
the rejecting relay" as part of the title. The clarified scenario quotes
"Rejected trial" explicitly; all expected behavior and assertions remain the
same. `scenario-revisions.json` binds the old and final story objects. The exporter
permits only that declared task-wording change in history, requires every other
field to remain identical, binds the selected record's original `story.json` to
its batch, and rejects any selected run using the earlier wording. N15 retests
on all three models. This is a fixture-input correction, not an identical-prompt
comparison or a claim that those two title choices prove a skill defect.

For this retained multi-batch matrix, pass
`--scenario-revisions scenario-revisions.json` to the exporter. Its prompt check
binds the selected run's original prompt file/hash and launch configuration to
the final story wording. Changing story metadata alone cannot qualify an old
prompt. The first-recorded-attempt count retains earlier wording versions and
is not an identical-prompt comparison. Scenario-gate controls cover both real
positive cases and rejection of stale, undeclared, non-task and metadata-only
changes.

Final-v10 changes only the Chat reference: a basic Forum supports chat, private
messages and rooms without additional creation flags; room names/codes are
runtime input. This keeps the selected route actionable without searching other
feature flags. Chat N09 retests on all three models. Forty-two other completed
cells have trace-bound unchanged-instruction audits, including fresh v9 Forum
posts/torrents and the explicitly quoted N15 tests. The unfinished v9 Qwen N09
was operator-interrupted during diagnostics, before requested artifacts existed;
its native143/aborted outcome and complete trace remain recorded. Its old queue
and waiting quoted-N15 watcher were stopped while preserving shared Splash.
Fresh v10 Qwen N09–N18 includes the already-clarified N15 wording, so no extra
quoted-N15 replay watcher is needed.

Final-v11 strengthens only the existing Chat reporting rule: keep completion
brief, avoid unnecessary extra reports, and do not copy private/session values
into prose or command examples even for disposable tests. Haiku's prior replay
kept the final reply clean but copied a private value into an extra report; both
reporting failures remain recorded. Chat retests on all three models, while the
same 42 non-Chat instruction-input audits establish unchanged loaded text.
Behavior and report checks remain separate; two old Haiku private-input reports
were later rejected and retested freshly, leaving 40 selected audited cells.

Qwen's unfinished low-effort v10 Chat diagnostics were operator-interrupted for
this revision. Independent N10–N18 run first at low effort; then a fresh N09 runs
at medium effort through the same SOMP model and isolated tools. Reproduce the
medium variant with `python3 harness/qwen_medium.py --batch UNIQUE_NAME --models
qwen --stories N09`. This wrapper sets per-run Qwen effort and retains native generic agent context, leaves
global settings untouched, and records the actual invocation/configuration.
The matrix is functional acceptance across recorded configurations, not a claim
that every story succeeds at low effort or on its first attempt.

Native-context replays use `python3 harness/native_context.py --batch UNIQUE_NAME
--models haiku --stories N06,N09,N15`. Claude/SOMP append the supplied benchmark
instructions to their native generic role, while keeping no ambient skills,
memory, rules, hooks or tools. The reported supplied-context hash excludes the
native base prompt; `system_prompt_mode` distinguishes these configurations.
The three-tool Claude init inventory is independently checked. Earlier replacement
prompt configurations remain recorded and are not claimed identical.

Human-facing final replies and root narrative Markdown/text reports (plus
result.json) are scanned for known fixture private scalars. Necessary CLI inputs
and requested raw JSON/CSV outputs are not narrative reports. Private values
remain prohibited even when fixtures are deliberately public. Generic launch
instructions explicitly state this and favor brief reports without extra docs.
Original failures and corrected reviews are retained; fresh replays never edit
prior responses or outputs. The matrix is eventual functional acceptance across
the recorded attempts, not a first-attempt reliability estimate.

Fixture malformed-frame regression: run `node harness/test_services.mjs
SERVICES_CONFIG.json service-controls.json` with an existing local service config
(the CLI installation and OMP dependency paths must exist). It starts a new
isolated fixture and performs no model inference. Invalid frames/filters receive
NOTICE without killing the service or poisoning subscriptions; signed normal
events still have the same live/history behavior. The original model-triggered
fixture crash and interrupted attempt remain recorded.

After the repaired-fixture native-medium Chat replay exhausted its full deadline
without executing the goal operation, a fresh compact-context variant uses
`python3 harness/qwen_action_first.py --batch UNIQUE_NAME --models qwen --stories
N09`. It retains the exact SOMP model and medium effort, uses custom replacement
context, and explicitly carries generic repository action-first guidance and
the shell's non-persistent environment contract. No app-specific answer or weaker
check is supplied. Original failures remain; per-row prompt hashes/modes identify
the actual configuration. This is not a default-native-role reliability claim.

Final-v12 changes only the Chat reference to specify the private-recipient
option's 64-character hexadecimal public encoding. Other public encodings fail
locally despite being accepted for site authors. A real CLI regression verifies
no events on two invalid encodings and one genuine signed publication on hex.
Chat retests on all3;51 selected non-Chat cases qualify only through explicit
unchanged-instruction audits. Extra unrequested narrative claims are recorded
separately from measured functional checks; passing does not certify every claim.

After two correct-operation/incorrect-report Chat outcomes, a fresh reporting
variant uses `python3 harness/qwen_completion_record.py --batch UNIQUE_NAME
--models qwen --stories N09`. It shares the exact compact action-first context
and adds a generic requirement to use the selected reference's completion record,
fill it from observations, and recheck factual claims against saved output. It
provides no app-specific values or answers. Failed accounts remain recorded.

The final reporting variant also clarifies the generic phrase "verification
account" to request a brief statement of checks performed. The phrase was
intended as a narrative account, not a new identity/account claim. The task,
frozen skill and factual acceptance checks remain unchanged; prior wrong-identity
reports remain failures. System-prompt hashes distinguish the wording versions.
