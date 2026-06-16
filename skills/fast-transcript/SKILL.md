---
name: fast-transcript
description: Use this skill when the user wants to transcribe or inspect audio or video with fast-transcript via `fscript`, including local files and remote URLs such as YouTube links. Prefer the no-diarization workflow (`-D`) for extracting facts, answers, summaries, and notes. Only enable diarization when speaker attribution is part of the task.
---

# fast-transcript

Use the local `fscript` CLI for transcript-first analysis of media.

## Default workflow

1. Confirm the tool is available:

```bash
command -v fscript
fscript --help
```

2. For questions, summaries, note-taking, quote-finding, and general information extraction, use the bundled wrapper:

```bash
bash skills/fast-transcript/scripts/fscript_info.sh "<media-file-or-url>"
bash skills/fast-transcript/scripts/fscript_info.sh "<media-file-or-url>" "/tmp/transcript.txt"
```

This standard path runs `fscript` with `--text=plain -D` so the transcript stays focused on content instead of speaker labels.

3. If you need timestamps while still staying in the no-diarization workflow, call `fscript` directly:

```bash
fscript "<media-file-or-url>" - --text=timestamps -D
```

4. Read the transcript, answer the user, and only keep the transcript on disk when it helps with follow-up work.

## When to use diarization

Only opt in to diarization when the task depends on speaker identity, turn-taking, or quotes attributed to different people.

```bash
fscript "<media-file-or-url>" - --speakers=timestamps -d
```

Examples:

- Interviews where the user asks who said a quote
- Podcasts with multiple recurring speakers
- Panels or debates where attribution matters

## Defaults

- Prefer `--text=plain -D` for information retrieval.
- Prefer stdout for quick one-off analysis and a file path for longer transcripts you will revisit.
- Prefer `--text=timestamps -D` before trying diarization if the user only needs rough navigation.
- Treat diarization as slower and noisier; do not enable it by default.

## Remote media notes

- `fscript` accepts remote URLs directly, including YouTube links.
- If a remote source is flaky or you expect repeated follow-ups, rerun with `-l` to force a local download before transcription.

## Gotchas

- The `fscript` default behavior enables diarization when available. Override that with `-D` for content-only tasks.
- `--speakers` is useful for attribution, but it adds clutter when the user only wants facts or answers.
- If stdout is too large for the current task, write to a temporary file and search or summarize from there.
