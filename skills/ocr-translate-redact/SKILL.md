---
name: ocr-translate-redact
description: Extract, translate, and redact text in images or documents while preserving the original, OCR uncertainty, translation limits, and redaction coverage.
---

# OCR, Translate, Redact

Create a readable working copy without turning imperfect OCR or translation
into a false original.

## Workflow

1. Preserve the original and define target language, audience, sensitive fields,
   and whether text must be searchable or visually redacted.
2. Run OCR on a derivative and retain confidence/region information; inspect
   names, numbers, negation, dates, and handwriting manually.
3. Translate with source and target text side by side, marking uncertain terms,
   dialect, idiom, and untranslated proper nouns.
4. Apply irreversible redaction to the distribution copy and inspect both visual
   pixels and extracted text for leakage.
5. Record tools, versions, languages, transformations, hashes, and reviewer
   corrections without overwriting the original.

Do not use OCR output as a verbatim transcript without review.

## Minimal check

The final redacted file has no recoverable target text in its text layer,
metadata, thumbnails, or alternate page representation.
