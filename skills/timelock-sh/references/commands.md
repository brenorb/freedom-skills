# timelock.sh command patterns

Read this file only when the user needs raw `curl` and `openssl` patterns, service limits, or API error semantics beyond the default wrapper workflow.

## Encrypt to a future UTC minute

```bash
UNLOCK=2026-07-01T12:00:00Z
FILE=/absolute/path/to/plaintext.txt

curl -fsS "https://timelock.sh/api/v1/keys/${UNLOCK}/cert" -o cert.pem

openssl cms -encrypt -in "${FILE}" \
  -binary \
  -recip cert.pem \
  -keyopt rsa_padding_mode:oaep \
  -keyopt rsa_oaep_md:sha256 \
  -aes-256-gcm \
  -outform DER \
  -out "${FILE}.enc"
```

## Extract the unlock minute from a ciphertext

```bash
INPUT=/absolute/path/to/plaintext.txt.enc

openssl asn1parse -inform DER -in "${INPUT}" \
  | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z' \
  | head -1
```

## Decrypt after release

```bash
INPUT=/absolute/path/to/plaintext.txt.enc
OUTPUT=/absolute/path/to/plaintext.txt
TIMESTAMP=$(openssl asn1parse -inform DER -in "${INPUT}" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z' | head -1)

openssl cms -decrypt -inform DER -in "${INPUT}" \
  -binary \
  -inkey <(curl -fsS "https://timelock.sh/api/v1/keys/${TIMESTAMP}/key") \
  -out "${OUTPUT}"
```

## Check service status and horizon

```bash
curl -fsS https://timelock.sh/api/v1/status
```

Use this when the user asks whether the service is healthy or how far ahead certificates are currently pre-generated.

## Supported time formats

- `YYYY-MM-DDTHH:MM:00Z`
- `YYYY-MM-DDTHH:MMZ`

All times are UTC and truncated to the minute.

## Stable API errors

All non-2xx responses use:

```json
{"error":"","message":""}
```

- `400 invalid_minute`: the timestamp path segment is not a supported RFC3339 minute.
- `404 not_found`: no key exists for that minute, commonly because it is outside the current horizon.
- `425 not_yet_released`: the key exists but is not public yet. Check `Retry-After`.
- `500 internal`: unexpected service-side failure.

## Important constraints

- The service uses standard CMS `AuthEnvelopedData` so other CMS-capable tooling can decrypt once the key is public.
- Certificates are available for about 30 days ahead.
- Once released, keys remain public permanently.
- This provides "decrypt after time T", not "decrypt only by recipient X".
