---
name: metadata-scrubber
description: Inspect and remove identifying metadata from documents, images, audio, video, and archives before sharing a derivative copy.
---

# Metadata Scrubber

Treat metadata removal as a separate review from content redaction.

## Workflow

1. Identify the file type, recipient, intended use, and metadata that must be
   retained for provenance versus removed for privacy.
2. Inspect container metadata, EXIF/XMP, document properties, revision data,
   embedded thumbnails, subtitles, archive paths, and filesystem names.
3. Make a derivative copy and remove only the approved fields with a format-
   aware tool. Keep the original and the before/after reports separately.
4. Re-inspect the output after export or recompression; conversion can create
   new metadata and may change hashes.
5. Rename the derivative safely, hash it, and record the remaining intentional
   metadata.

Metadata scrubbing does not remove identifying content, network logs, or
information visible in the media. Do not claim anonymity from a clean file.

## Minimal check

The post-scrub inspection report must be generated from the final file, not the
intermediate working copy.
