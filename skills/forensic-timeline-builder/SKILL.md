---
name: forensic-timeline-builder
description: Build a source-linked event timeline from records, media, messages, and testimony while preserving time precision and uncertainty.
---

# Forensic Timeline Builder

Make sequence and gaps visible without manufacturing precision.

## Workflow

1. Define the time zone, clock sources, case scope, and event granularity.
2. Extract events with source ID, stated or observed timestamp, precision,
   location confidence, actor as identified by the source, and description.
3. Normalize display times while preserving the original time and offset; mark
   device-clock drift, approximate dates, and conflicting records.
4. Sort events and show gaps, overlaps, dependencies, and alternative sequences.
5. Link each event to source spans and distinguish observed, reported,
   inferred, and disputed events.

Do not infer intent from chronology alone or identify a person from a weak
temporal coincidence.

## Minimal check

The timeline can be regenerated from the event table, and every event displays
its original timestamp and source reference.
