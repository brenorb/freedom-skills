---
name: fast-transcript
description: Use this skill when the user wants to transcribe or inspect audio or video with fast-transcript via `fscript`, including local files and remote URLs such as social media links. Prefer text output for facts, summaries, and notes. Use diarization only when speaker attribution matters.
---

# fast-transcript

Use the local `fscript` CLI for transcript-first analysis of media.

## Onboarding

Install with Homebrew:

```bash
brew tap brenorb/tap
brew install fast-transcript
```

Run without installing:

```bash
uvx fscript --help
```

Or install the Python entrypoint with `uv`:

```bash
uv tool install fscript
```

First use downloads the ASR model automatically. Remote URLs also rely on `yt-dlp`, so make sure `yt-dlp` is on `PATH` or available via `uvx yt-dlp`.

## Default workflow

1. For questions, summaries, note-taking, quote-finding, and general information extraction, use text output:

```bash
fscript "<media-or-url>" --stdout --text
fscript "<media-or-url>" "/tmp/transcript.txt" --text
```

Use `--stdout` when you want printed output and a file path when you want a saved transcript. `--text` keeps timestamps but removes speaker labels. In current upstream `fscript`, text modes do not run diarization.

2. If you want to remove timestamps, switch to plain text:

```bash
fscript "<media-or-url>" --stdout --text=plain
```

3. Read the transcript, answer the user, and only keep the transcript on disk when it helps with follow-up work.

4. Only check availability or open help when there is a real reason:

```bash
command -v fscript
fscript --version
```

Use these checks on first-session failures, when `fscript` is missing from `PATH`, or when you need to confirm flags. Do not run them mechanically before every transcription.

If your installed release supports it, `--text=compact` is the single-string text variant.

## When to use diarization

Only opt in to diarization when the task depends on speaker identity, turn-taking, or quotes attributed to different people.

```bash
fscript "<media-or-url>" --stdout
```

Examples:

- Interviews where the user asks who said a quote
- Podcasts with multiple recurring speakers
- Panels or debates where attribution matters

## Defaults

- Prefer `--text` for information retrieval.
- Prefer stdout for quick one-off analysis and a file path for longer transcripts you will revisit.
- Use `--text=plain` if timestamps are noise.
- Use `-D` only when you explicitly want a faster no-diarization run outside text mode.
- Diarization is slower; only enable it when speaker attribution matters.

## Remote media notes

- `fscript` accepts remote URLs directly, including YouTube links and other social media URLs that `yt-dlp` supports.
- For remote URLs, `fscript` prefers platform-provided manual subtitles when they exist.
- If you want to override that and transcribe locally anyway, rerun with `-l` / `--local`.
- If only auto-captions or no captions exist, `fscript` falls back to downloading the media and transcribing locally.

## Gotchas

- The default speaker-aware mode enables diarization when available, but `--text` avoids that path.
- `--speakers` is useful for attribution, but it adds clutter when the user only wants facts or answers.
- `--clean` is on by default and compresses pathological repetition such as `we we we we` into `we... we`. Use `--raw` to disable that cleanup for a run.
- If stdout is too large for the current task, write to a temporary file and search or summarize from there.
