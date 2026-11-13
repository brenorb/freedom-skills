# Connect an agent to White Noise

Paste everything below the line into an agent running in a terminal on the Mac or Linux machine where the connector will live, or tell the agent to follow this file.

---

Connect an agent runtime on this machine to White Noise encrypted chats using the maintained Marmot connectors. Do not write, copy or modify connector code.

1. Read the upstream guide first: <https://github.com/marmot-protocol/mdk/blob/master/integrations/README.md>. It is the source of truth for supported runtimes, prerequisites, the current release, commands and troubleshooting. If anything here disagrees with it, follow the guide.
2. Ask which one runtime I want to connect: Hermes, OpenClaw, Claude Code, Codex, OpenCode, Pi or Goose. Install only that one.
3. Ask for the White Noise account (`npub`) that may invite and message the agent.
4. Check the guide's prerequisites for that runtime: the runtime is installed, signed in and working, and the OS and architecture are supported. Report what is missing. Do not install or sign in to the runtime unless I ask.
5. Install with the guide's verified-installer helper: download the installer and its adjacent `.sha256` from the `marmot-protocol/mdk` release, verify the checksum, and only then run the local file. Never pipe a download into a shell. Use the release version the guide documents; do not invent or reuse a version from memory.
6. When the install finishes, show me the agent's new White Noise identity (`npub`) so I can add it in White Noise and invite it to a DM or group. Do not send invitations or messages on my behalf unless I ask.
7. Run the guide's first-install verification and tell me the result, including anything you could not check, such as the relay list on my phone.
8. If something breaks, read the selected connector's README and the guide before changing the service, runtime, allowlist or account configuration.

Rules:

- Keep the default isolation: one identity, home and service per connector. Share an account or socket across runtimes only if I ask, and then follow the guide.
- An accepted invite is not permission to run the agent. Keep the sender allowlist, and never widen it without my explicit instruction.
- Never ask for, print or store my White Noise private key (`nsec`).
- For ordinary Nostr identity or messaging tasks, use the Nostr tools instead of this connector.
