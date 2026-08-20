---
name: media-redaction
description: Redact faces, documents, screens, audio, or other identifying media while preserving a reviewable unredacted original separately.
---

# Media Redaction

Create a distribution copy that removes the requested identifying content and
does not accidentally expose it through the pixels, audio, filename, or file
metadata.

## Workflow

1. Confirm the audience, threat model, exact regions or speakers to protect,
   and whether the original must remain preserved for authorized review.
2. Work from a copy. Prefer opaque, irreversible redaction for documents and
   images; mute or replace audio segments rather than relying on visual marks.
3. Inspect frames, pages, audio channels, subtitles, thumbnails, previews,
   filenames, and embedded metadata for leakage.
4. Export to a new file, hash it, and record the redaction method and coverage.
5. Have a second pass review the exported artifact at normal and enlarged
   scale before publication.

Do not blur when a person or text must be unrecoverable. Do not overwrite the
original or upload it to an online editor without explicit authorization.

## Minimal check

Re-open the exported artifact in a separate viewer and verify that every target
region is covered in every relevant frame/page/channel.
