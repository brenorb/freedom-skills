---
name: rampart-hook-configurator
description: Use this skill when the user wants to install, tune, or verify the paired Rampart pre-send and post-send hooks, especially when they need to decide which labels to keep, whether URLs should reach the model, how to wire session IDs, and how to test the round-trip safely.
---

# Rampart Hook Configurator

Configure the hook pair like a transport control, not like a prompt trick.

## Default workflow

1. Start with the harness boundary:
   - what data goes into the pre-send hook
   - what comes out of the post-send hook
   - where the session id comes from
2. Check the privacy goal next:
   - strict redaction before hosted LLM calls
   - reversible placeholders for assistant replies
   - labels that should stay visible, such as `URL` in some workflows
3. Tune the hook config in one place, preferably `hooks/rampart-pre-send/rampart-hooks.config.example.json` copied to a local config file for the target harness.
4. Keep the policy explicit:
   - `keepLabels` for classes the model should still see
   - `skipKeys` for request fields that must not be rewritten
   - `responseSkipKeys` for reply fields that must not be rehydrated
5. Verify the round trip with one real request:
   - pre-send redacts the outbound payload
   - post-send restores the placeholders in the reply
   - repeated turns reuse the same placeholder ids in the same session

## Defaults

- Prefer a unique session id per conversation or thread.
- Prefer `failOpen: false` for pre-send when the hosted request must never leave unfiltered.
- Prefer `allowMissingSession: true` for post-send unless the harness can guarantee paired state.
- Keep the default keep-set unless there is a concrete reason to widen it.
- If URLs matter to the model, add `URL` to `keepLabels` instead of bypassing the whole hook.

## Common adjustments

- To let URLs through:
  add `URL` to `keepLabels`
- To preserve city, state, and ZIP:
  leave the default keep-set as-is
- To avoid corrupting provider metadata:
  keep structural fields such as `model`, `id`, `tool_call_id`, `url`, `image_url`, and `file_id` in the skip lists
- To make post-send reveal work:
  wire the same session id into both hooks

## Minimum output

Return these sections when helping with hook setup:

```text
Recommended hook wiring
Config changes to make
What stays visible to the model
What gets redacted and restored
Verification steps
```

## Safety rules

- Do not recommend bypassing the pre-send hook just because one class is inconvenient.
- Do not widen `keepLabels` without naming the privacy tradeoff.
- Do not assume a missing session id is harmless; explain the reveal failure mode.
- Do not describe the model as a security boundary. It is an exposure-reduction layer with known miss cases.
