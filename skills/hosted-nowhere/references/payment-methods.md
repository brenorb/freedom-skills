# Message tips and fundraiser donations

Read this only when configuring or using payment methods for Message or Fundraiser.
Their methods share **one tag with key `l`**, whose value is a comma-separated list:

```json
{"key":"l","value":"reader@wallet.example,*PayPal:example.com/alice"}
```

The first entry is the Lightning address. A custom entry has the form
`*Label:destination`; `*!Label:destination` also requests a QR code. Replace the
example destinations with the ones the user supplied. Do not create a tag whose
key is `*PayPal`: it may survive encoding while being ignored by the renderer and
the methods command. Store uses a different custom-payment format; do not reuse
its tag `5` syntax here.

For destinations/labels containing separators, escape backslashes, commas, and
colons with a backslash at the method-string layer, then JSON-encode normally.
Use a JSON writer rather than hand-building nested shell escapes.

Finish the page and method configuration **before** requesting an invoice. Run
the app's methods command and confirm both the type and exact destination of
every requested method. Correct missing methods and recheck before proceeding.
Decoding a fragment does not establish that its payment methods are functional.

Only the `lightning` method supports invoice generation. Custom methods have IDs
such as `custom_0` and are list/copy flows. Use positive integer sats. Inspect the
returned invoice and any expiry data; generating an invoice does not pay it.
Retain a successful response. If only page text changed and the payment method
and amount are unchanged, do not request another invoice just to refresh saved
outputs. Do not blindly retry a timed-out invoice request.

Capture invoice JSON to the requested output file **in the same invocation**.
Read that file to inspect or deliver the invoice. Re-running the invoice command
to display or save its output creates another invoice request, not a read check.

Validated against `nowhere-cli@0.3.0`, whose parser is
[`src/lib/tips.ts`](https://github.com/brenorb/nowhere-cli/blob/main/src/lib/tips.ts).
