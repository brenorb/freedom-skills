---
name: whitenoise-agents
description: Connect an existing AI agent runtime to White Noise encrypted chats, or troubleshoot its connector. Applies to Hermes, OpenClaw, Claude Code, Codex, OpenCode, Pi, and Goose integrations maintained by Marmot Protocol.
metadata:
  version: "0.1.0"
  repository: "https://github.com/marmot-protocol/mdk"
---

# White Noise Agent Connectors

Use the maintained Marmot Protocol connector for the user's chosen runtime. This skill guides setup and use; it does not reimplement or vendor the connectors.

## Set up or use a connector

1. Read the [upstream White Noise + Agents quickstart](https://github.com/marmot-protocol/mdk/blob/master/integrations/README.md). Treat it as the current source for supported runtimes, prerequisites, release assets, commands, and connector behavior.
2. Pick the connector matching the runtime the user named:
   - Hermes and OpenClaw use plugins for their existing gateways.
   - Claude Code, Codex, OpenCode, Pi, and Goose use terminal harness connectors.
   - If no runtime is specified, ask which one they want to connect; don't install all of them by default.
3. For a requested installation, use the upstream installer and its adjacent checksum for the selected runtime. Follow the quickstart's verification and setup flow; don't substitute an unverified `curl | sh` command or copy a version-pinned command from this skill.
4. Complete identity bootstrap using the account the user authorizes. Default installs create a separate White Noise identity and local home for each connector. Show the resulting identity details to the user so they can add it in White Noise.
5. Help the user invite the agent identity to a DM or group and test the connection. Do not send invitations or messages on the user's behalf unless their request explicitly asks for that action.
6. For a broken setup, consult the selected connector's README and the upstream integration guide before changing service, runtime, allowlist, or account configuration.

## Architecture and boundaries

All supported connectors talk to the local `wn-agent` service through the `marmot.agent-control.v2` protocol over a Unix-domain socket. `wn-agent` owns the Marmot account/runtime boundary, MLS group state, relay transport, and durable encrypted sends. Connector-specific behavior lives in upstream integration folders; use their docs for current feature support and security settings.

The default installation isolates each connector in its own home, service, and identity. Sharing one account or socket across runtimes is an advanced deployment choice: consult the upstream guide and preserve each connector's sender authorization and activation rules. In particular, invite admission is not the same as permission for an inbound message to invoke an agent.

This skill is for connecting an agent runtime to White Noise. For ordinary Nostr identity or messaging workflows, use the relevant Nostr or messaging skill instead.
