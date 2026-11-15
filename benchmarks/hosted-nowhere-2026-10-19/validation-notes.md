# Validation notes

The final gate uses the 18 stories in `stories.json` and the frozen final-v12 skill,
with trace-bound unchanged-instruction audits for earlier unaffected cells.
Earlier development and targeted runs are diagnostic evidence,
not substitutes for missing final cells. Raw attempts are retained under
`/private/tmp/hosted-nowhere-e2e/runs/`.

## Changes supported by observed failures

- Message tips and fundraiser methods must share tag `l`; a separate custom
  payment tag can survive encoding while being ignored by the method parser.
- A Haiku petition run saved signer input under the requested response name.
  Petition examples now give inputs distinct names and capture the actual response;
  the oracle correlates its event ID with the accepted relay event.
- Capture write and invoice output in its original invocation. Repeating a
  command to save its output caused a second invoice request in a development run.
- A Haiku forum run repeated a successful publish to capture its output after
  local topic validation failed. Forum examples now omit unconfigured topics,
  show the CLI salt flag, retain redirection during recovery, and explain how to
  save an existing response instead of sending again. `final-v3` is superseded.
- Torrent submissions require `b`; fixed category roots use `F` and `q`.
  Verification tag `V` does not enable torrents.
- Runtime commands need explicit relay overrides. An encoded relay tag does not
  override every CLI default.
- Store inventory is enabled by tag presence, including `k=0`. CLI 0.3.0 adds
  `k=1` when omitted, and the live beta builder requires inventory management.
  The initial inventory-free test requirement was unsupported; the corrected
  story verifies the supported stock-status-before-checkout flow instead.
- Built-in Store PayID uses tag `j`; custom method tag `5` is a different format.
  Preserve the quoted buyer country, and extract the actual receipt object from
  checkout output before decrypting or verifying it.
- A technically successful Haiku chat run still called relay acceptance
  “delivery” in its report. That manual-review failure superseded `final-v1`
  rather than being counted as a pass. Chat was split into a focused reference
  with an explicit acceptance/delivery/history/page completion record.
- Ephemeral chat acceptance does not establish recipient delivery. The independent
  receiver decrypts all four recorded sends and verifies their inner signatures;
  the relay deliberately does not retain them for later listing.

## Runner and oracle corrections

The SOMP extension argument adapter was corrected before scoring Qwen. Fresh OMP
state now declares the server's usable 32K window and a 4K generation cap. A pilot
stalled on bitmap/handoff compaction under the local server's memory cap; final
runs use text summarization on the same Qwen model. Haiku's turn allowance was
raised after an otherwise progressing torrent run hit the original cap. Codex's
outer sandbox now permits the workspace writes provided by the scoped tools.

The deterministic oracle was checked against real positive evidence and corrupted
order/receipt controls. Assertion corrections retain original verdicts and use
the unchanged browser/CLI observations: only explicitly requested artifacts are
mandatory; metadata may use descriptive URL keys; CLI JSON may be wrapped in a
captured stdout object; browser-created descriptions may use tag `b`; a style may
put the name in the document title; and Drop line numbers must not be mistaken
for lost code content. Event themes may apply uppercase CSS, so their rendered
text comparison ignores case while decoded source text remains byte-exact.
Identical fragments on `nowhr.xyz` and `hostednowhere.com`
are equivalent renderer targets. A specific owner is required only when the story specifies one; the disposable
chat/torrent stories permit another disposable creator. Exact decoded bytes,
geometry, amounts, explicitly requested owner
keys, signature checks, relay event counts and readback IDs remain required.

## Isolation correction during development

Before tool networking was restricted, a Haiku petition run omitted the relay
override and published one disposable test signature through CLI public defaults.
It used only public fixture keys and reserved example data. That run was reported
to the user and is not counted as a final pass. In-flight development cells were
stopped. Tool networking is now enforced as loopback-only, npm uses a warmed
offline cache, and the browser blocks public WebSocket relays. The boundary was
checked with a successful localhost request and a denied non-loopback socket.

Final relay writes use local disposable services. LNURL invoices are simulated
`TEST_ONLY` values, not payable invoices; manual checkout does not send money.
The real production renderer/builders are exercised in isolated Chrome. These
checks establish the tested workflows, not real-world relay retention, recipient
delivery, payment settlement, or availability of an arbitrary deployed signer.

All fixture keys are deliberately public, disposable values. Reports that copy
those private inputs do not qualify, even though no production or host secret is
supplied. Earlier waivers were corrected, preserving the prior reviews. Passing
fixture checks does not establish confidential production credential handling.

## Final-run assertion clarification and replay policy

N14 requests repaired JSON but does not prescribe CLI-output schema for that
file. A valid repaired-input file is accepted only alongside its delivered URL,
matching real browser observation and independent decode with no invented body.
N03 likewise requests `final.json` without a schema. Qwen saved the valid event
input there and the real CLI response separately in `create-output.txt`. The
oracle now accepts that format only when every saved field/tag agrees with the
independently decoded, fully delivered and actually observed final URL. Its
original false verdict is preserved. An altered saved-description control fails
even while the correct delivered/browser URL remains unchanged.
Haiku N10 saves the permitted metadata URL under `explanation.storeUrl`.
Extraction now traverses nested JSON, while requiring a single unambiguous
fragment when there is no explicit CLI URL. It still independently checks all
Store fields, owner, actual writes, receipt, exports and browser/delivered URL.
The first false verdict remains; conflicting nested fragments are a negative
control rather than a reason to guess which version is final.
An audit of all 18 specifications confirms that only N01, N02, N04, N12 and
N13 expressly prescribe raw creation/sign/update output in `final.json`.
N17 permits its correct message/tipping metadata; its overstrict raw-output
failure was corrected without replaying the model or altering its observations.
For N18, original content is now independently decoded from the saved original
URL and compared with the final body, rather than trusting an assumed `siteData`
wrapper. Actual original/final signatures and two remote signing RPCs remain
mandatory. Nested-original metadata and an unsigned-original rejection are
separate oracle controls.
N18's unquoted sentence “body Remote signer test. Then update…” is ambiguous
about whether the sentence-ending period is content. Either punctuation reading
is accepted, while the update must preserve its original body exactly.

A failed final attempt remains a failure in the report. A fresh unassisted replay
may establish completion of that story, but cannot turn its first attempt into a
pass. Report both initial-attempt reliability and replay results. In final-v4,
Haiku N18 genuinely failed exact-final-link browser verification after it
repeated a local signing command and opened an earlier signature variant. Its
first attempt is retained; neither equivalent content nor a valid signature
waives the exact-final-link requirement.

Haiku's fresh N18 replay omitted the embedded author key, and its final
`verify.json` correctly said `signed: false` despite its success claim. This is a
second genuine failure, not an oracle exception. The protection reference now
gives a complete captured-output NIP-46 create/update sequence, requires the
connected public key in the input, and checks actual signature fields. Runs using
the previous skill hash are diagnostic only for the revised final gate.

Qwen N06 in final-v4 manually copied a truncated but decodable URL and published
a signature in the wrong petition namespace, then attempted another submission
for the intended petition. This is a genuine failure even though the data and
relay are disposable. Petition now captures creation output and extracts its URL
programmatically, uses it for all operations, and requires reporting a wrong-URL
publish rather than silently adding a corrective signature. The previous final
matrix is superseded after this and the remote-signer fixes.

The final-v5 Haiku lane hit Claude's session limit (HTTP 429, reported reset
23:10 America/Sao_Paulo) before completing its workflows. These are retained
capacity failures, not skill passes. A fresh same-hash Haiku lane is required
after reset before push; Luna and Qwen continue independently.

Qwen final-v5 N03 failed during inference with “Metal command exceeded
120 seconds,” before generating an app artifact. Splash subsequently recovered
automatically (transport restart counter incremented, Metal healthy). No shared
daemon was manually restarted. That cell requires a fresh same-hash replay and
remains recorded as an infrastructure failure.

## Component and packaging checks

All 16 tests in `tests/hosted_nowhere/test_workflows.py` passed against the
published nowhere-cli 0.3.0 package through pinned npx with a warmed offline
cache, including all app fixtures, protection semantics, required-field failures,
private-recipient encoding and isolated relay contracts. An earlier component
run also used an independent temporary installation of the published CLI.
All final model E2Es invoke npx from an offline warmed cache. The latest skill
also passes quick_validate.py and this repository's skills-ref validation.

Run the portable component suite from the repository root with:

```sh
python3 -m unittest discover -s tests/hosted_nowhere -v
```

Luna final-v5 N17 completed its CLI/browser workflow correctly but duplicated a
fragment substring in the final response's share URL. This is a genuine manual
review failure. The oracle now also requires the response to contain the exact
final artifact's share fragment. The original failure remains recorded; any
successful fresh unassisted same-hash replay is reported separately.

The final oracle was checked again against eight retained real attempts:
four passing Petition/chat/Store/NIP-46 workflows and four genuine failures
(corrupted delivered URL, wrong browser signature variant, absent embedded
signer key, wrong Petition response artifact). All expected outcomes match;
`oracle-controls.json` records their provenance, errors, and current oracle hash.

Qwen final-v5 N06 correctly produced one signature, count, and owner export in
the intended namespace, but manually copied a different URL into the browser.
It investigated that unrelated page and hand-decoded keys/fragment bytes, then
hit its 1800-second deadline without completing browser verification or a final
account. This remains a genuine incomplete-workflow failure; it is not excused
as an infrastructure outage. Any same-hash fresh replay remains separate.

The two npx cache entries and independent component-test installation all report
version 0.3.0 and have identical complete `dist/` hashes. `cli-integrity.json`
records that read-only dependency identity check; the tested CLI is not a
workflow-specific stub.

A report-gate control uses a real passing row, then adds an interrupted replay
with no metrics. The reporter retains the unfinished attempt and rejects that
cell rather than falling back to the earlier pass. `report-gate-controls.json`
records both expected outcomes and the tested reporter hash.

All eight documented builder routes returned HTTP 200 with the expected creation
page title in a separate isolated Chrome profile (`builder-routes.json`). These
are route/title checks, not eight additional complete browser user stories. A
plain HTTP probe received 403 responses; that client-specific attempt is retained
separately in `builder-routes-http.json` and does not establish missing routes.

Qwen final-v5 N07 produced valid post/reply/readback/isolation artifacts and the
correct browser page, but the runner hit its 30-minute bound before completing
a final response. It remains an incomplete-workflow failure. Qwen continuation
and fresh replays use a 60-minute bound to accommodate local compaction. The
just-started base N08 attempt was stopped and marked `operator-stop.json`; only
benchmark-owned processes were stopped, and the shared Splash daemon was kept.
This changes the runtime allowance, not any content, signature, event-count,
identity, final-link or review assertion.

Qwen continuation N08 emitted its complete final report before another automatic
compaction. It eventually exited normally (0) in 1416.8 seconds and passed; it
finished before a manual cleanup was attempted, so no cancellation/recollection
was needed for that case. The controller now stops post-answer maintenance after
a verified native final-stop event. Real N07's unfinished trace is a negative
control; it has no such final answer and remains failed. Collector controls also
prove that a synthetic cancellation preserves the real -15 status and exact native
final text while permitting logical completion, and that later tool calls
invalidate a marker. These controls are not additional model runs.

The final-v6 revision addresses a genuine documentation gap observed in Qwen
N07. Forum's outer event uses a fresh envelope key; `authorPubkeyHex` and verified
readback `payload.p` carry authorship. The guide now distinguishes these from
`event.pubkey` and the reply-channel key. The protection guide also gives the
CLI's public-key conversion command and explains preserving all32 bytes of
Nostr public keys. These statements were checked against published0.3.0 source
and real post/readback artifacts. Earlier substantive revisions remain diagnostic;
final-v6 restarted every story after those changes.

Luna final-v6 Art and its fresh same-hash replay both produced the correct artwork
but abbreviated the delivered URL (once with a placeholder, once with ellipsis).
These remain genuine failures. Final-v7 changes only Art's reference: deliver a
short Markdown label whose target preserves the complete saved URL. Fresh Luna
Art now passes and its screenshot is byte-identical to the visually verified
image. Art must also pass freshly on Haiku and Qwen. Haiku's full lane uses v7.

To avoid rerunning unrelated routes, every reused final-v6 case receives an
explicit audit of all tool inputs. The only changed file is `references/art.md`;
the router, metadata, shared instructions and other app references are unchanged.
Loaded instruction files and any broad content searches must have identical
contents/outputs. Uncertain or dynamic accesses require fresh tests. Source
hashes remain distinct and trace-bound audits are exported, not represented as
same-hash runs. This revision to the original blanket rerun protocol is explicit
in `protocol.md` and `instruction-equivalence.json`.

Qwen final-v6 N04 created the requested fundraiser and invoice but made extra
direct callback and CLI invoice requests while investigating the test response.
This is a genuine side-effect failure, despite correct saved artifacts. The
existing payment reference already prohibits repeat invoice requests for
inspection. The service-journal count remains strict, the failed account is
retained, and completion requires a fresh unassisted replay.

Qwen's remaining lane moved to final-v7 rather than continuing to test the old
Art reference. The in-progress final-v6 N05 was stopped explicitly and retained
with `operator-stop.json`, native metrics and raw trace; it is not a completed
model result. Only that benchmark model group, old orchestrator and local fixture
were stopped. The shared Splash daemon remained running. Fresh final-v7 Qwen
starts with N04 replay, then tests N05–N18. Operator interruptions are counted
separately from inference/capacity failures and functional failures.

Haiku final-v7 N06 passes the deterministic state checks (one accepted signature
and correct owner export), but manual review rejects its timeout recovery and
account. It repeated signing after checking only an empty output file, without
reconciling relay state, then claimed zero errors. That manual failure remains
distinct from the technical pass; a fresh same-skill replay is required.

Final-v8 appends only a Petition reference clarification after Qwen spent its
otherwise-correct run investigating the browser's zero count versus the selected
relay's count of one. A CLI relay override does not edit the link or configure
the browser's relays. Report the two observations separately; do not republish,
edit the namespace or switch relays to synchronize a display. If the user
requires a matching live count, that step remains unverified until confirmed.
The incomplete v7 Qwen run is retained as an operator revision interruption,
with native metrics and partial correct artifacts. Its queue/local fixture were
stopped while preserving shared Splash; fresh Qwen N06–N18 use final-v8.

Petition is freshly retested on Luna High, native Claude Haiku and SOMP Qwen.
The 39 completed non-Petition cases have trace-bound instruction-input audits
against final-v8: all their loaded instruction files are byte-identical, directory
reads expose unchanged filenames, and the one recursive content query returns
identical matching lines/line numbers with path ordering normalized. No changed
text was exposed. Original source hashes remain visible. Direct broker-read
completeness is also checked automatically, alongside manual shell/helper audits.

The fresh final-v8 Petition tests pass on all three runners. Qwen explicitly
reports browser count zero versus selected-relay CLI count one and does not
resubmit, change the namespace or switch relays to synchronize the display.
Functional passes do not certify every unrequested narrative detail: Qwen's
summary calls the encryption NIP-04, whereas the published 0.3.0
`src/lib/petition-live.ts` imports and uses NIP-44, and its command table reverses
`create petition`. The actual executed commands, matching-owner-key explanation,
encrypted payload/decryption and requested artifacts are correct. These
nonfunctional reporting errors remain explicit in its review record; the skill
itself gives the correct command and makes no NIP-04 claim.

The enforced browser/public-WebSocket and tool loopback/offline policy was
documented in the protocol but initially omitted from the model-facing generic
environment description. That missing context encouraged Qwen to investigate
intentional network boundaries. Fresh remaining runs now receive those facts;
no app-specific answer, expected result or weaker check is added. Actual network
capabilities remain identical. Prompt hashes and network policy are exported per
row rather than presenting this as a perfectly identical-prompt comparison.
The ongoing v8 N07 agent keeps its original prompt and full deadline. Only its
old queue parent is paused; a watcher collects it unchanged and then starts
fresh N08–N18 in `final-v8-env`. There is no operator interruption of that agent.

Original final-v8 Qwen N07 exhausted its uninterrupted 3600-second native
deadline (exit 1, `Deadline exceeded`). Its post/reply, owner, WoT and salt
artifacts were correct, but it did not deliver a completed final report/link.
It remains failed. The watcher collected this outcome and started fresh N08–N18
in final-v8-env; a fresh N07 replay is required after that serial lane.

Qwen final-v8-env N08 completed its torrent/reply artifacts and exact-link
browser feature checks, but continued investigating why the forum header rendered
while browser activity was empty. The root already identifies the URL fragment
as the site; Forum's selected reference did not explicitly explain this static
header versus relay activity distinction. Final-v9 adds that general explanation
and the CLI/browser relay separation, citing upstream architecture. No app
commands, fixtures or acceptance checks change. All four Forum stories retest
on all three runners, while 34 completed non-Forum cells receive trace-bound
unchanged-instruction audits. The original Qwen N08 agent continues uninterrupted
under its original deadline; only its queue parent is paused. A watcher collects
its actual outcome, then resumes fresh final-v9 Qwen N07–N18. The waiting old N07
recovery watcher was stopped before it launched an agent.

Fresh v9 Haiku N09 meets the requested functional send/list task and explicitly
reports recipient delivery as unverified. Two bad recipient-key-format attempts
fail locally before the sole accepted private send; the journal contains exactly
four requested ephemeral events and independent receiver decryption verifies
their payloads/signatures. Its extra narrative overstates browser functionality
beyond the observed static controls and incorrectly calls recipient reading
impossible to verify. An explicit recipient acknowledgment could provide evidence.
Neither browser live-relay behavior nor read acknowledgment was tested; the
functional pass does not certify those unrequested claims.

Fresh v9 Haiku N15 passes the deterministic rejection/uncertainty checks but
fails manual content review: its actual attempted post title is "Rejected trial
against the rejecting relay" rather than the requested "Rejected trial". The
rejected single write does not excuse this mismatch. A fresh unassisted identical
story/skill replay is required; the original technical pass and manual failure
remain separate. No skill or acceptance criterion is changed for the replay.

Original final-v8-env Qwen N08 completed normally (exit 0) in 2382.2 seconds
without interruption. Its workflow state checks pass, but manual report review
fails: it invents a forum-creation event ID not present in actual local create
output, mislabels tag i as torrent enablement, and asserts an unproven browser
loopback restriction. Public WebSockets were blocked; local relay connections
were permitted. The original technical pass and manual failure remain distinct.
After collecting it, the watcher closed only its fixture/old queue and started
fresh final-v9 Qwen N07–N18.

The unchanged-prompt Haiku N15 replay chose the same longer title. This exposed
an ambiguous boundary in the test's unquoted title. The scenario now quotes
"Rejected trial" explicitly, preserving all other expected behavior. The two
nonqualifying title outcomes remain recorded; they are not strong evidence of a
skill defect under ambiguous input. N15 retests freshly on Luna, Haiku and Qwen.
All other story objects and skill bytes remain unchanged. The reporter accepts
only the declared historical task-wording correction and requires selected
records to match their batch and final story exactly.

Fresh v9 Qwen N07 completes normally and passes the actual owner post/reply,
moderated readback, WoT, salt isolation and final-page/link requirements without
republishing or changing namespaces. Its browser activity remains explicitly
unverified. Extra prose still says the forum was created on the relay and that
the browser cannot reach loopback. Local create does not register a forum, and
the policy permits local browser relay connections; the page was not configured
for that relay. Those claims are not certified by the functional pass. Unlike
the prior N08 report, it does not invent a creation-event ID as CLI evidence.

Fresh v9 Qwen N08 passes the torrent workflow and delivers the exact final URL
without inventing a creation-event ID. A mistyped 66-character secret is rejected
locally before publication; fixture-key recovery produces the sole accepted
torrent, followed by one reply. Browser activity and the category dropdown remain
explicitly unverified. Extra prose still mislabels i as the torrent-enable tag
(actual input correctly has b) and describes the signing wrapper as a WoT witness;
those claims are not certified. Disposable public fixture secrets were printed
in local diagnostics, so production-secret confidentiality is not tested.

Qwen N09 inspected public installed nowhere-cli code in the runtime-readable
npm cache during diagnostics. This adds information beyond the starting skill
context. Runtime directories must be readable to execute the real CLI; these
results are functional acceptance, not strict skill-only knowledge or generic
instruction-following evaluation. Private credentials and other runs were not
exposed. Public-package integrity remains independently checked.

Qwen's unfinished v9 Chat attempt spent its run inspecting feature definitions
instead of creating the requested forum. Final-v10 adds the missing default
explicitly to the selected Chat reference: basic Forum creation needs no extra
chat/private/room enable flag, and room names/codes are runtime inputs. This is
general CLI behavior already exercised by the other successful chat cases. The
old diagnostic-only attempt was explicitly operator-interrupted for the revision
(native143/aborted, no requested artifacts), not classified as a completed model
workflow failure. Chat retests freshly on all3. Forty-two unaffected completed
cells retain original hashes with explicit unchanged-instruction audits. No CLI
commands, fixture values, assertions or model settings change.

Fresh v10 Haiku Chat completes the technical operations but its final report
prints the recipient private/session secret, violating the selected Chat guide's
explicit reporting rule. Fixtures are deliberately public and disposable, so
this is not a production-credential incident; the reporting failure still does
not qualify. It also claims menu/private UI verification beyond its two browser
observations. A fresh unchanged-skill/story Haiku replay is required; original
technical pass and manual failure remain recorded.

Haiku's unchanged-skill v10 replay omitted secret values from its final reply,
but copied the owner private/session key into TASK_COMPLETION_REPORT.md. That
extra narrative artifact also violates the selected Chat reporting rule. Final-v11
emphasizes the existing rule for prose, extra reports and command examples,
including disposable data, and favors the brief completion record. All3 Chat
tests restart; the same42 non-Chat cases have unchanged loaded instructions.
Qwen's unfinished v10 Chat attempt is retained as another operator interruption;
no requested artifacts existed. Independent N10–N18 proceed first at low effort.
The subsequent fresh Chat replay uses medium effort on the exact same SOMP Qwen
model; its invocation and per-row effort are recorded. Skill, story and service
checks are not weakened for that runtime choice, and no global model setting
changes. No additional Skill revisions are planned merely for diagnostic delay.

Fresh v11 Haiku avoids secret values in its final reply, but calls empty lists
cryptographic proof and asserts real-time recipient distribution/purge without
a live acknowledgment or retention audit. The requested operations technically
pass; the core delivery/ephemerality explanation does not. This remains a manual
failure and requires a fresh unchanged-skill/story replay. No further guide or
criterion change is made for this failure.

A consistent scan of selected human-facing reports found two previously waived
private-fixture values: Haiku v8 Petition and quoted v9 N15. Those reviews are
corrected to nonqualifying, with prior review text retained. Public disposable
keys are not a production incident, but private-key reporting still violates the
shared guide. A deterministic check now rejects provided private fixture scalars
in final replies and root Markdown/text reports (plus result.json); CLI inputs
and requested raw CLI JSON/CSV are separate artifacts. Selected reports are
checked consistently rather than treating public-fixture examples as a waiver.

The harness also replaced Claude/SOMP's native generic system context, unlike
Codex which retained its normal role. Fresh native-context replays append the
same isolated benchmark instructions to the native generic context; all ambient
skill/memory/rule disabling and the three-tool broker remain. Prompt mode is
exported explicitly, and the supplied-text hash is not a hash of the native base
context. These are recorded functional acceptance configurations, not identical-
prompt model comparisons. No app-specific answers or weaker state checks are
added. Haiku replays N06/N09/N15; the later medium SOMP Chat replay also retains
native context. Skill bytes and story objects remain unchanged.

Fresh native Haiku replays qualify Chat and the quoted rejecting-relay story.
Petition still copied a private fixture scalar into an extra report in two
attempts, including one with the explicit generic privacy reminder. Those failures
remain. A further fresh unchanged-skill/story replay completed without the value
in its final reply or narrative artifacts and passes the functional checks. Its
extra report incorrectly says public counts require an owner secret; actual count
ran without one. This unrequested claim is not certified by the functional pass.

The generic benchmark instructions now explicitly treat disposable fixture
private values as private inputs, use placeholders in command examples, and
request brief observed-only reports. This is recorded supplied context, not an
app-specific answer or a change to the skill/story. Native-context invocations
retain only the three isolated tools; the actual Claude init inventory is checked.

Qwen N14 exposed a URL-selection oracle bug: the corrupted page's captured text
also included the previous page title, so the grader selected the deliberately
invalid URL from the report. Candidate URLs now require independent decoding,
expected app/name and one unique fragment before saved-input comparison. The
original false verdict remains, and real/synthetic controls cover this recovery.
The actual response and browser records are unchanged.

The first native-medium Qwen Chat replay completed its four actual sends and
listings, then sent a malformed diagnostic JSON object to the relay. The fixture
destructured it as an array and crashed with an uncaught TypeError. Its later
connection-refused diagnostics exposed that infrastructure defect. The affected
replay was operator-stopped (native143; no final browser check/report), with all
outputs retained. It does not qualify. No skill/story or acceptance rule changed.

The fixture now rejects malformed frames and filter shapes with NOTICE while
keeping the process alive. `harness/test_services.mjs` checks six malformed
requests, a subsequent real signed persistent event and an ephemeral event,
live receipt of both, and later retention of only the persistent event. The
control result and service hash are in service-controls.json. This changes only
malformed-input handling; normal CLI, relay, browser and cryptographic contracts
remain unchanged. Chat is replayed freshly at the same medium/native settings.

The repaired-fixture native-medium Qwen replay reached its actual one-hour
deadline (native exit1, 3600.95 seconds, Deadline exceeded, 85 tool calls) without
creating the forum or requested artifacts. It repeatedly inspected CLI source
and compacted context. This is retained as a full workflow failure, not an
operator interruption or a successful partial run.

The next fresh replay uses `harness/qwen_action_first.py`: the same exact SOMP
Qwen model at medium effort, with the compact replacement system context used
by earlier Qwen workflows, plus generic action-first guidance reflecting the
repository instructions and the true per-invocation shell contract. The supplied
role contains no app-specific answers, fixture values, expected event IDs or
grader assertions. Skill bytes, story, tools, network policy, fixture and
acceptance checks remain unchanged. Prompt mode/hash distinguish this configuration;
it is functional acceptance under a recorded context, not default-native-role
reliability or an identical-prompt model comparison.

The compact action-first replay completes the actual Chat operations and browser
checks. Its unrequested diagnosis incorrectly calls a valid fixture npub malformed;
the actual error is that the private-recipient option requires 64-character hex.
This repeated local failure exposed a real missing input-format gotcha. Final-v12
adds only that public-encoding clarification to the Chat reference; root metadata,
other routes and examples remain byte-identical. Chat retests freshly on all3.
The real-CLI component suite now has16 passing tests through npx, including rejection
of npub/Nowhere encodings before any publication and exactly one valid signed
hex-recipient event. The guidance requests no recipient secret for sending.

Fifty-one selected non-Chat cells have trace-bound unchanged-instruction audits
against v12 (53 historical attestations remain; two old behavior failures are
independent). The validator's15 positive/negative controls pass for the new target.
Luna and Haiku v12 use the correct recipient format immediately. Their reports
qualify the measured functional workflow; broad claims that empty lists alone
prove retention or event IDs prove recipient broadcast are not certified. The
actual relay contract is separately tested; recipient delivery stays unverified.

Qwen's first v12 replay executes the complete actual workflow with the correct
hex recipient on its first private send. Technical checks pass, but manual review
fails: the final report calls relay acceptance "Delivery evidence" without a live
recipient acknowledgment, and calls an unsigned URL signed (actual signed:false).
Browser-activity uncertainty does not cure those claims. Technical pass and
manual failure remain separate. A fresh unchanged-skill/story/config replay is
required; no acceptance rule or further guide change is made.

The unchanged v12 Qwen replay repeats the same final-report errors: send responses
are called delivery evidence and the unsigned page is called a signed discussion.
Actual workflow state remains correct, but manual review fails again. A fresh
`qwen_completion_record.py` configuration now prioritizes the completion record
already provided by the selected reference and rechecks factual claims against
saved outputs. This generic reporting instruction supplies no app-specific facts
or grader answers. Task, frozen skill, fixtures and acceptance checks remain
unchanged. The action-first wrapper was factored into a shared function; its
original generated prompt is byte-identical, verified against the real launch
config. Each context variant remains identifiable by its actual prompt hash.

The completion-record-priority replay correctly marks recipient delivery
unverified and avoids the false signing claim. Its final account instead
misattributes the forum to the fixture author key, while the saved input and
embedded page use the fixture owner key; it also labels the room announcement
with the room-message text. This failed manual identity review is retained.
The generic harness phrase "verification account" was ambiguous: the intended
request was an account of verification checks, not an identity/account credential.
The next fresh configuration clarifies that phrase to "a brief statement
describing what you verified". It does not change the user story, require a
different owner, supply an identity answer, or weaken factual-claim checks.
Actual per-run system hashes preserve the difference. The frozen skill remains
4e07e081100a8e2ca5e0a1ea57231f39a8597fd4aba76b69404ca75e14d79155.


## Final recorded outcome

The final exported gate is 54/54 eventual functional passes: 18 stories each for
fresh Codex Luna High, Claude CLI Haiku, and the exact requested SOMP Qwen model.
The first recorded matrix attempt passed 46/54; failures and replays remain in
results.json. Fifty-one selected non-Chat cases qualify through trace-bound
unchanged-input audits; all three Chat cases ran freshly against final-v12.

The final Qwen Chat replay uses medium effort and the recorded compact,
completion-record-focused replacement context. It correctly distinguishes the
unsigned Forum URL, four accepted signed events, empty later lists and unverified
recipient delivery. All reported event IDs match the actual saved publications.
Its broader inference about private/room browser enablement is not established
by the visible General/Posts/Chat navigation or the empty Posts view; that browser
UI inference is outside the certified result. Private and room CLI operations are
independently checked. This is eventual functional acceptance under the recorded
configurations, not default-context or first-attempt reliability.

After all model runs, the published CLI files and package manifests matched the
independent installation across all three installations. Two extra empty local
diagnostic files were removed only after that comparison; cli-integrity.json
records their names and hashes. No published CLI code was modified.
