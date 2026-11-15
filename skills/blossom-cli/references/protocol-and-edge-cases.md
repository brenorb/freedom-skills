# Blossom server workflows and edge cases

Read this file for multi-server replication, recovery, authorization, paid servers, transformed media, server-list publication, or ambiguous HTTP responses.

## Contents

- [Multi-server replication](#multi-server-replication)
- [Preflight is tri-state](#preflight-is-tri-state)
- [BUD-06 upload preflight](#bud-06-upload-preflight)
- [Authorization](#authorization)
- [Paid servers](#paid-servers)
- [Media processing](#media-processing)
- [Blob URI and server fallback](#blob-uri-and-server-fallback)
- [Errors and retries](#errors-and-retries)
- [Listing and large accounts](#listing-and-large-accounts)
- [Sources](#sources)

## Multi-server replication

Treat the SHA-256 as the blob's canonical identity. Use this workflow when the user requests redundancy:

1. Upload the bytes to one selected origin server with `--no-publish`.
2. Preserve the returned blob descriptor.
3. Check each destination for the returned hash when that can be done unambiguously.
4. Ask each remaining server to mirror the origin descriptor.
5. If mirroring fails and the local bytes remain available, use a direct upload fallback only when multi-server replication is already within the user's request and the failure is not a permanent rejection.
6. Verify the same hash on every destination.
7. Report a per-server result; never collapse partial success into a single success statement.
8. Publish NIP-94 metadata and a kind `10063` server list only after the final replica set is known and only when the user requested publication.

Do not publish a separate one-server list during every upload. Replaceable kind `10063` events can otherwise advertise only the last server rather than the intended ordered replica set.

## Preflight is tri-state

Existence checks need `present`, `absent`, and `unknown` states:

| Result | Classification | Next step |
|---|---|---|
| Successful `2xx` `HEAD /SHA256` | Present | Mirror/register ownership when needed; do not resend bytes unnecessarily. |
| `404` | Absent | Mirror from an existing URL or upload bytes. |
| `401` or `403` | Unknown/auth required | Resolve scoped authorization before deciding. |
| `429` | Unknown/rate limited | Respect retry guidance or report partial replication. |
| `5xx` | Unknown/server failure | Retry with bounds or attempt the authorized fallback; never call it present. |
| Timeout, DNS, TLS, reset | Unknown/transport failure | Retry with bounds, fail over, or report partial replication. |

The TypeScript SDK's `hasBlob()` returns true for every non-`404` response. Copying that behavior would allow a `500` to suppress a needed upload. Track the Rust-side design decision in [brenorb/blossom-cli#1](https://github.com/brenorb/blossom-cli/issues/1).

Even when bytes already exist, a destination may still require `/mirror` or another authenticated operation to register ownership. Presence and ownership are separate facts.

## BUD-06 upload preflight

Servers may support `HEAD /upload` using:

- `X-SHA-256`
- `X-Content-Length`
- `X-Content-Type`

Use it to discover authorization, payment, size, and content-type requirements before transferring bytes. Treat a missing preflight endpoint as a compatibility condition, not proof that upload is impossible. Fall back to the normal upload flow when the client supports it.

## Authorization

Prefer short-lived kind `24242` authorization events scoped by:

- operation in the `t` tag (`upload`, `media`, `get`, `list`, or `delete`);
- blob hash in the `x` tag for upload, media, and delete;
- destination hostname in the `server` tag when possible;
- expiration.

Reuse a signed event only when operation, hash, server scope, and expiration still match. Never reuse broad authorization for a destructive request. Normalize server hostnames before comparing scope.

Attempt anonymous reads first when appropriate and sign only after a `401`. Never send signed authorization or secret key material over remote plaintext HTTP.

## Paid servers

A Blossom server can return `402 Payment Required` with an `X-Cashu` payment request. Treat payment as a separate user-authorized action:

1. Parse and display the amount, unit, mint or token constraints, operation, and server without exposing secrets.
2. Confirm payment authority if it was not already granted.
3. Pay through the supported wallet flow.
4. Retry the same scoped operation with the returned `X-Cashu` token.

Do not treat `402` as a transient network error and do not pay a different server automatically.

## Media processing

The `/media` endpoint may resize, recompress, or otherwise transform a file. The processed descriptor's SHA-256 is therefore authoritative for replication.

Process media on one suitable server, then mirror the processed result. Do not mirror or upload the original bytes under the processed hash. If no `/media` endpoint exists, use raw upload only when the user accepts that fallback.

## Blob URI and server fallback

For a `blossom:` URI, try sources in this order:

1. Embedded `xs` server hints, preserving their order.
2. Servers found through each `as` author hint's kind `10063` event.
3. User-configured fallback servers.

Normalize each server to its origin, prefer HTTPS for bare domains, and deduplicate before requests. Verify the returned bytes against the URI hash regardless of source.

For ordinary HTTP Blossom URLs, extract the last valid 64-character hexadecimal hash before constructing fallback URLs. Preserve the extension only as a content hint; the hash remains canonical.

## Errors and retries

Handle protocol rejections separately from availability failures:

| Status | Meaning | Default behavior |
|---|---|---|
| `401` | Authentication required | Obtain narrowly scoped authorization, then retry once. |
| `402` | Payment required | Enter the explicit payment flow. |
| `403` | Not authorized | Stop and report policy failure. |
| `409` | Conflict | Report server state; do not retry blindly. |
| `413` | Too large | Skip that replica or select another user-approved server. |
| `415` | Unsupported media type | Correct metadata or skip that server. |
| `422` | Unprocessable blob/request | Stop and preserve the server reason. |
| `429` | Rate limited | Honor retry guidance with a bound. |
| `5xx` | Server failure | Retry with timeout/backoff or fail over reads. |

Use request timeouts and bounded retries. Preserve cancellation. For writes, continue to another destination only when the user requested replication; for reads, trying the next configured source is expected fallback behavior.

## Listing and large accounts

Prefer cursor pagination with bounded page sizes when the server supports `cursor`, `limit`, `since`, and `until`. Do not assume one `list` response represents the complete account. Preserve the cursor and report incomplete scans.

## Sources

- [blossom-client-sdk README](https://github.com/hzrd149/blossom-client-sdk)
- [SDK multi-server upload](https://github.com/hzrd149/blossom-client-sdk/blob/master/src/actions/multi-server.ts)
- [SDK authorization](https://github.com/hzrd149/blossom-client-sdk/blob/master/src/auth.ts)
- [SDK upload preflight](https://github.com/hzrd149/blossom-client-sdk/blob/master/src/actions/upload.ts)
- [SDK URI resolution](https://github.com/hzrd149/blossom-client-sdk/blob/master/src/actions/resolve.ts)
