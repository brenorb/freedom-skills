---
name: evidence-export-packager
description: Package selected evidence and its provenance into a reviewable export with hashes, an index, access notes, and safe derivatives.
---

# Evidence Export Packager

Create the smallest export that answers the recipient's question without
leaking unrelated sources or personal data.

## Workflow

1. Define the recipient, purpose, scope, redaction policy, and required format
   before selecting files.
2. Copy only approved originals or derivatives and create an index containing
   evidence ID, filename, media type, source relationship, and SHA-256 hash.
3. Include a provenance/readme file with collection times, transformations,
   tool versions, known gaps, consent limits, and contact for corrections.
4. Scan the package for hidden files, thumbnails, metadata, temporary files,
   absolute paths, and unrelated case material.
5. Verify the archive by extracting it into a clean directory and rechecking
   every hash before transfer.

Use encryption and a separate channel for credentials when requested. Do not
publish an export merely because it is packaged.

## Minimal check

The clean extraction contains exactly the indexed files and all hashes match.
