# Browser workflow

Open the selected app's `https://hostednowhere.com/create/<app>` route and inspect
the actual UI. Read only its app reference. The legacy Store route first needs
the deprecation explanation in [Store](store.md).

1. Fill required fields to uncover validation problems, then complete all the
   user's requested content and options. Reaching Share Link is an intermediate
   checkpoint, not the completed task.
2. For real petitions, forums, and legacy stores, use the intended owner's public
   key. Use Generate npub only for explicitly disposable identities; do not assume
   the control provides a recoverable private key.
3. Review the preview and verification phrases. Sign/encrypt only as requested
   or when preserving the input's required protections. Use the application's
   supported signing flow rather than pasting private keys into ordinary fields.
4. After every final edit, regenerate Share Link if the UI marks it stale. Copy
   the entire fragment. Never synthesize a link from a screenshot or guessed data.
5. Open the copied link separately and perform the shared
   [completion checks](verification.md#completion-checks). If encrypted, verify
   password entry and do not substitute a plaintext preview link for delivery.

For edits, use the builder's import/edit controls when available. Preserve fields
outside the request and keep the original URL. New content produces a new link;
previously shared copies continue to represent their original content.

Use semantic labels rather than step numbers, since the UI changes. If live
validation disagrees with a reference, follow the observed UI, report the mismatch,
and do not silently alter installed skill files during the user's publishing task.
Avoid submitting a signature, order, post, or payment merely to test a preview.
