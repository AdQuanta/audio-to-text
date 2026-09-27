# Audio to Text

Local, privacy-conscious draft transcription for Hebrew and Hebrew-English audio using Faster-Whisper.

This repository is a reusable tool and experiment workspace. Audio and generated transcripts are excluded from Git. Machine transcripts are drafts and require human review before they are used as research records.

## Requirements

- Python 3.11 (`>=3.11,<3.12`)
- [uv](https://docs.astral.sh/uv/)
- Internet access for the first model download
- Enough disk space for the selected model (the default Hebrew model is approximately 1.6 GB)

## Install

From the repository root:

```powershell
uv sync
```

This creates or updates the local `.venv` using the committed `uv.lock` file.

## Transcribe audio

Place private recordings in `data/raw/`, then run:

```powershell
uv run python code/transcribe_with_faster_whisper.py "data/raw/example.m4a"
```

Draft Markdown transcripts are written to `data/processed/transcripts/` by default. For Hebrew meetings, a typical CPU command is:

```powershell
uv run python code/transcribe_with_faster_whisper.py "data/raw/example.m4a" `
  --output-dir data/processed/transcripts `
  --model ivrit-ai/whisper-large-v3-turbo-ct2 `
  --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

Use `--device cuda` and an appropriate compute type only when the local CTranslate2/CUDA setup supports it. The first run downloads and caches the model; later runs reuse it. CPU transcription can be slow for long recordings. Multiple audio paths can be supplied in one command so the model is loaded once.

See [`code/README.md`](code/README.md) for all options and the timestamp-repair utility.

## Output and limitations

- Output is UTF-8 Markdown with centisecond timestamps.
- The default model is optimized for Hebrew; use another Faster-Whisper-compatible model when appropriate.
- The tool does not perform speaker diarization.
- Names, technical terms, punctuation, code-switching, and speaker identity require review.
- Do not commit recordings, transcripts, sidecars, or other sensitive data. The repository `.gitignore` excludes `data/` by default.

## Repository layout

```text
code/                 transcription scripts
data/raw/             local input audio (not tracked)
data/processed/       generated outputs (not tracked)
docs/specs/           dated decisions and experiment notes
```

## Development

```powershell
uv run python code/transcribe_with_faster_whisper.py --help
uv run python -m compileall code
```

There is currently no automated accuracy test suite. Validate changes with a short, non-sensitive recording and inspect the generated transcript manually.

## Privacy and review

The pipeline runs inference locally after model files have been downloaded, but the initial model download requires network access. Confirm that your audio may be processed and stored on the machine. Treat every generated transcript as an unverified draft until a human reviews it.

## License

No license has been selected yet. Until one is added, the repository should be treated as source-available to authorized users rather than as software granted for unrestricted reuse.
