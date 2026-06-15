# filepizza trust assumptions

Read this file when the sharing context is high-risk: dissidents, human rights advocates, whistleblowers, journalists under surveillance, or users facing state repression.

`file.pizza` can be useful for convenience. It should not be described as a strong anonymity or anti-surveillance tool.

## Core trust assumptions

Using the public `file.pizza` site assumes all of the following are acceptable:

- The user trusts the site enough to run its JavaScript in their browser.
- The user accepts normal browser-identifiable metadata exposure such as IP address, TLS metadata, browser fingerprint surface, and timing patterns.
- The user accepts WebRTC-related network exposure and whatever ICE, STUN, TURN, or signaling infrastructure the service uses at that moment.
- The user can keep the uploader online long enough for the recipient to fetch the file.
- The recipient can safely open the link without that act itself creating unacceptable suspicion or exposure.

If any of those assumptions are false, do not treat `file.pizza` as a safe default.

## What `file.pizza` does provide

- Direct browser-to-browser transfer in the normal case.
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

For dissidents and human rights advocates in tyrannical regimes, the main problem is usually not just whether the file bytes are encrypted in transit. The real problem is often:

- who can observe that the user visited the site
- who can correlate sender and receiver timing
- whether the browser reveals identifying information
- whether the recipient opening the link is itself dangerous

In those environments, a convenience file-sharing website may be the wrong tool even if the payload is not stored on the server.

## Safer framing for agents

When the threat model is serious, describe `file.pizza` like this:

- good for temporary peer-to-peer convenience sharing
- not a substitute for a dedicated anonymity or anti-surveillance workflow
- not the default recommendation for politically sensitive or life-and-liberty-sensitive transfers

## Agent guidance

- Surface these assumptions explicitly instead of implying safety by omission.
- If the user is in a high-risk environment, recommend a threat-model discussion before recommending this tool.
- Prefer language like "transport-encrypted browser P2P sharing" over "secure" or "private" without qualifiers.
