---
name: p2p-transfer-filepizza
description: Use this skill when the user wants to share a local file through the public https://file.pizza site without relying on a normal upload API, especially for one-off large files where a temporary peer-to-peer link is acceptable and a local seeding process can stay online.
---

# P2P Transfer FilePizza

Use the public `file.pizza` website through a bundled local automation wrapper. This skill is for the hosted public site only, not a self-hosted server.

## Default workflow

1. Confirm the file path exists locally.
2. Start the upload through the bundled wrapper:

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py upload /absolute/path/to/file
```

3. If `tmux` is available, the wrapper should prefer running the seeding worker in a persistent detached tmux session automatically. If `tmux` is unavailable, it should fall back to its normal detached background process.
4. Read the JSON result and use the returned `short_url` or `long_url`.
5. If the user asks whether an upload is still alive, inspect it with:

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py list
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py status <upload_id>
```

6. If the user wants to stop seeding, or the transfer is no longer needed, stop it explicitly:

```bash
python3 skills/p2p-transfer-filepizza/scripts/filepizza_public.py stop <upload_id>
```

7. If the user needs raw operational notes or troubleshooting patterns beyond this workflow, read `references/commands.md`.
8. If the file or sharing context is politically sensitive, adversarial, or related to dissidents, activists, journalists, or human rights work, read `references/trust-assumptions.md` before recommending `file.pizza`.

## Defaults

- Prefer the bundled wrapper over ad hoc browser automation.
- Prefer the wrapper's automatic `tmux` launcher when `tmux` is installed, because it makes long-lived uploads easier to supervise and less brittle across shell/session boundaries.
- Prefer the public site workflow only for files that are acceptable to expose to a third-party web app at the browser-JavaScript trust level.
- Prefer the short URL for user-facing sharing and the long URL for logging or debugging.
- Prefer keeping exactly one seeding process per upload alive until the recipient confirms they have the file.

## Safety rules

- Treat starting an upload as an external action because it creates a shareable public link.
- Do not use this skill for seed phrases, private keys, raw wallets, or similarly high-risk secrets.
- Do not use this skill by default for covert exfiltration, whistleblowing against a state adversary, or situations where website-delivered JavaScript and browser fingerprinting are unacceptable risks.
- Call out that `file.pizza` is peer-to-peer and the uploader must remain online.
- Call out that WebRTC traffic is encrypted in transit, but the site still serves the client-side JavaScript.
- Do not assume the generated link will keep working after the seeding process exits.

## Gotchas

- `file.pizza` does not expose a normal REST upload API. This skill uses Playwright against the public site.
- The first run may take longer because the wrapper bootstraps a local Playwright runtime under the user's cache directory.
- When `tmux` is present, stopping the upload should kill the tmux session, not just the worker pid.
- Manual browser behavior can vary. If a transfer fails in Arc, retry in Chrome before assuming the service is down.
- Large files depend on browser memory and WebRTC behavior; success is not as deterministic as a server-side object store.
- If the `file.pizza` UI changes, the bundled worker may need an update.
