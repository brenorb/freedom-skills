# p2p-transfer-filepizza trust assumptions

Read this file when the sharing context is high-risk.

`file.pizza` can be useful for convenience. It should not be described as a strong anonymity or anti-surveillance tool.

## Core trust assumptions

Using `filepizza-cli` with the public `file.pizza` service assumes all of the following are acceptable:

- The sender trusts the npm CLI and its dependencies with local file access and network connections. The sender does not need to run the website in a browser.
- The recipient trusts the FilePizza site enough to run its JavaScript in their browser.
- Both sides accept network metadata exposure, including IP addresses and connection timing. The recipient also accepts the web client's browser fingerprinting surface.
- The user accepts WebRTC-related network exposure and whatever ICE, STUN, TURN, or signaling infrastructure the service uses at that moment.
- The user can keep the uploader online long enough for the recipient to fetch the file.
- The recipient can safely open the link without that act itself creating unacceptable suspicion or exposure.

If any of those assumptions are false, do not treat `file.pizza` as a safe default.

## What `file.pizza` does provide

- WebRTC transfer from the CLI seeder to the recipient's browser, directly when connectivity permits or through a TURN relay when required.
- Transport encryption through WebRTC.
- No normal server-side file hosting step in the standard happy path.

Those properties are useful, but they are not the same thing as a hardened anonymity system.

## What it does not guarantee

Do not imply any of the following unless independently verified for the exact deployment and threat model:

- anonymity
- resistance to traffic analysis
- protection against a malicious site operator
- protection against browser compromise
- protection against local device compromise
- deniability
- metadata minimization
- survivability against nation-state surveillance

## High-risk warning

In high-risk contexts, the main problem is usually not just whether the file bytes are encrypted in transit. The real problem is often:

- who can observe the sender contacting FilePizza infrastructure or the recipient opening the site
- who can correlate sender and receiver timing
- whether the sender's network connections or the recipient's browser reveal identifying information
- whether the recipient opening the link is itself dangerous

In those environments, this sharing workflow may be unsuitable even if the payload is not stored on the server.

## Safer framing for agents

When the threat model is serious, describe `file.pizza` like this:

- good for temporary peer-to-peer convenience sharing
- not a substitute for a dedicated anonymity or anti-surveillance workflow
- not the default recommendation for high-risk transfers

## Agent guidance

- Surface these assumptions explicitly instead of implying safety by omission.
- If the user is in a high-risk environment, recommend a threat-model discussion before recommending this tool.
- Prefer language like "transport-encrypted CLI-to-browser P2P sharing" over "secure" or "private" without qualifiers.

## Implementation reference

The pinned `filepizza-cli@0.1.0` release corresponds to [upstream commit 6f28903](https://github.com/brenorb/filepizza-cli/tree/6f289039c02044586be6914460a51679f434e9ec). See `src/filepizza-api.ts` for service API calls and `src/seeder-service.ts` for WebRTC sharing and channel lifecycle.
