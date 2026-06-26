# iroh trust assumptions

Read this file when the user wants to use iroh in a high-risk context: dissidents, journalists, whistleblowers, human-rights defenders, politically exposed organizers, or anyone whose peer graph, location, or infrastructure choices could create real harm.

## Core trust model

- Iroh is transport and connectivity infrastructure, not anonymity infrastructure.
- Public-key addressing makes endpoint identity stable enough to be linkable across sessions if the same identity is reused.
- Public relays can help connectivity, but they also become infrastructure the user is trusting for availability, metadata handling, and operational integrity.
- A self-hosted relay reduces third-party dependency, but it does not magically remove metadata or operational risk.

## What public relays can learn

- That a given endpoint id connected to that relay.
- Rough timing and frequency of connection activity.
- Potentially enough network metadata to correlate peers, sessions, or operator habits.
- Whether the user depends on a specific relay operator for reachability.

Public relays should be treated as convenience infrastructure, not as neutral black boxes.

## What endpoint ids and tickets imply

- Endpoint ids are routable identifiers, not disposable chat handles.
- Reusing the same identity across multiple exchanges increases linkability.
- Sharing endpoint ids, tickets, or direct addresses with the wrong party can widen the user's attack surface.
- Manual relay URLs or direct socket addresses can reveal more topology than the user intended.

## Safer defaults for sensitive work

- Prefer self-hosted or tightly controlled relay infrastructure when the user can operate it competently.
- Prefer short-lived testing identities when continuity is not required.
- Prefer minimal disclosure: only share the endpoint id or addressing details with the intended peer.
- Prefer local `--env dev` or controlled relay experiments when the goal is learning or rehearsal, not live field use.
- Separate testing identities from operational identities.

## What this skill does not promise

- No anonymity.
- No unobservability.
- No resistance to endpoint compromise.
- No guarantee that public relay operators are benign, private, or jurisdictionally safe.
- No guarantee that example commands from the upstream repo are production-safe defaults for adversarial environments.

## Operational judgment

- If the user needs censorship resistance plus anonymity or deniability, iroh alone is usually the wrong layer to rely on.
- If the user needs a production relay for exposed work, the better path is to design the relay, access control, logging, certs, and exposure model explicitly instead of cargo-running a demo binary and hoping for the best.
- If the user's actual goal is blob sync, document sync, or durable sharing, evaluate whether `iroh-blobs`, `iroh-docs`, or another protocol gives a better trust envelope than raw endpoint-to-endpoint transport testing.
