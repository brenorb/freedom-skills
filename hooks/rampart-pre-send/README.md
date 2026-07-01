# Rampart Hook Pair

Portable pre-send and post-send hooks for running [National Design Studio Rampart](https://github.com/nationaldesignstudio/rampart) around hosted LLM calls.

This package is meant to be shared with other agent setups. Anything that can pipe request and response payloads through shell commands can use it.

## What it does

- `rampart-pre-send.mjs` redacts PII before a request reaches the model.
- `rampart-post-send.mjs` restores saved placeholders in the model reply.
- Placeholder identity stays stable across turns when both hooks share the same session id.
- Raw text and JSON payloads are supported.
- Structural keys such as `model`, `id`, `url`, `image_url`, and `file_id` are skipped by default to avoid corrupting provider payloads.
- Fail-closed is the default; fail-open is available when availability matters more than blocking.

## What it is not

- Not a hard security boundary.
- Not a replacement for transport or storage controls.
- Not a claim of perfect recall across every PII type or language.

## Install

```bash
cd hooks/rampart-pre-send
npm install
```

The package pins:

- `@nationaldesignstudio/rampart@0.1.2`
- `@huggingface/transformers@3.7.5`

## Basic contract

Your harness needs to do two things:

1. Pipe the outbound request through `rampart-pre-send`.
2. Pipe the inbound model reply through `rampart-post-send`.

Both hooks must receive the same:

- `RAMPART_SESSION_ID`
- `RAMPART_SESSION_DIR`

Without shared session state, the post-send hook cannot restore placeholders.

## Usage

Pre-send on raw text:

```bash
export RAMPART_SESSION_ID=thread-123
export RAMPART_SESSION_DIR=.rampart-sessions

printf 'My email is alice@example.com and my SSN is 123-45-6789.\n' \
  | node ./rampart-pre-send.mjs --mode text
```

Post-send on a model reply:

```bash
export RAMPART_SESSION_ID=thread-123
export RAMPART_SESSION_DIR=.rampart-sessions

printf 'I will email [EMAIL_1] about [SSN_1].\n' \
  | node ./rampart-post-send.mjs --mode text
```

JSON request payload:

```bash
cat request.json | node ./rampart-pre-send.mjs --mode json
```

JSON response payload:

```bash
cat response.json | node ./rampart-post-send.mjs --mode json
```

Auto-detect JSON first, otherwise treat stdin as text:

```bash
cat payload.txt | node ./rampart-pre-send.mjs
cat reply.txt | node ./rampart-post-send.mjs
```

Emit stats on stderr:

```bash
cat request.json | node ./rampart-pre-send.mjs --stats
cat response.json | node ./rampart-post-send.mjs --stats
```

Clear session state after rehydrating the reply:

```bash
cat response.json | node ./rampart-post-send.mjs --clear-session
```

## Config file

Copy the example and adjust it for the target harness:

```bash
cp ./rampart-hooks.config.example.json ./rampart-hooks.config.json
```

Then run:

```bash
cat request.json | node ./rampart-pre-send.mjs --config ./rampart-hooks.config.json
cat response.json | node ./rampart-post-send.mjs --config ./rampart-hooks.config.json
```

Important knobs:

- `keepLabels`: classes the model should still see
- `skipKeys`: request fields that must not be rewritten
- `responseSkipKeys`: reply fields that must not be rehydrated
- `failOpen`: whether pre-send should pass through on failure
- `allowMissingSession`: whether post-send should no-op when session state is absent
- `clearSession`: whether post-send should delete the session file after reveal

If URLs matter to the model, prefer adding `URL` to `keepLabels` instead of bypassing the hook.

## Environment variables

- `RAMPART_HOOK_MODE=auto|json|text`
- `RAMPART_SESSION_ID=<conversation-or-thread-id>`
- `RAMPART_SESSION_DIR=<directory>`
- `RAMPART_MODEL=nationaldesignstudio/rampart`
- `RAMPART_HEURISTICS_ONLY=1`
- `RAMPART_FAIL_OPEN=1`
- `RAMPART_KEEP_LABELS=URL,CITY,STATE,ZIP_CODE`
- `RAMPART_SKIP_KEYS=model,id,url,image_url,file_id`
- `RAMPART_RESPONSE_SKIP_KEYS=id,url,image_url,file_id,data`
- `RAMPART_ALLOW_MISSING_SESSION=1`
- `RAMPART_CLEAR_SESSION=1`
- `RAMPART_ALIASES_JSON='{"GIVEN_NAME":"NAME"}'`
- `RAMPART_BACKEND_CMD='node ./tests/fake-redactor.mjs'`

`RAMPART_BACKEND_CMD` exists mainly for testing or swapping in a different local backend command.

## Example wrapper

```bash
#!/bin/sh
set -eu

HOOK_DIR="/absolute/path/to/freedom_skills/hooks/rampart-pre-send"

export RAMPART_SESSION_ID="${RAMPART_SESSION_ID:?missing session id}"
export RAMPART_SESSION_DIR="${RAMPART_SESSION_DIR:-$HOOK_DIR/.rampart-sessions}"

exec node "$HOOK_DIR/rampart-pre-send.mjs" --config "$HOOK_DIR/rampart-hooks.config.json"
```

The response-side wrapper is the same shape, but calls `rampart-post-send.mjs`.

## Verification

Run the full local suite:

```bash
cd hooks/rampart-pre-send
npm test
```

Print a human-readable end-to-end transcript for one real round trip:

```bash
cd hooks/rampart-pre-send
npm run demo:e2e
```

The suite covers:

- fake-backend request redaction
- realistic OpenAI Chat Completions, OpenAI Responses, and Anthropic Messages payloads
- fail-open and fail-closed behavior
- config and environment-variable wiring
- real model-backed multilingual coverage across the seven published Latin-script languages
- real model-backed taxonomy checks including email, phone, SSN, credit card, URL, IP, CPF phrasing, routing, government ID, passport, driver's license, address components, and geo keep-policy behavior
- stable placeholder reuse across turns
- pre/post round-trip restoration with shared session state
- a recorded transcript that shows user text, redacted payload, simulated LLM reply over placeholders, restored user-visible reply, and saved session mappings

The test runner is serialized with `--test-concurrency=1` to avoid model cache races during ONNX initialization.

## Limits

Treat this as exposure reduction, not perfect protection.

Rampart's own documentation scopes this release to seven Latin-script languages and calls out weaker behavior on non-Latin scripts. If your threat model depends on those cases, do not rely on this hook pair alone.
