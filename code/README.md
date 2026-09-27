# Audio Transcription Code

This folder contains reusable scripts for creating draft transcripts from local audio recordings.

## Current Script

`transcribe_with_faster_whisper.py` transcribes one or more audio files with a local Faster-Whisper model and writes Markdown transcripts only:

```text
*.transcript.md
```

By default, outputs are written to:

```text
data/processed/transcripts/
```

That `data/` location is only the code default. You can input audio from another folder and write Markdown transcripts to another folder by passing paths explicitly.

## Setup

Run commands from the workspace root:

```powershell
uv sync
```

The workspace is configured to use its own local Python environment in `.venv/`.
Python 3.11 is required. The first transcription run downloads the selected model from Hugging Face; the default Hebrew model is approximately 1.6 GB.

## Input Files

The default place for raw audio is:

```text
data/raw/
```

The script accepts any format supported by the local FFmpeg/PyAV stack, including `.m4a`.

## Basic Usage

Transcribe one file:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "data\raw\example.m4a"
```

Transcribe multiple files in one run:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "data\raw\first.m4a" "data\raw\second.m4a"
```

Recommended Hebrew meeting settings:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "data\raw\example.m4a" --output-dir data\processed\transcripts --model ivrit-ai/whisper-large-v3-turbo-ct2 --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

Example using an audio file and output folder outside this workspace:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "C:\path\to\audio.m4a" --output-dir "C:\path\to\transcripts"
```

## Timestamp Format

Segment timestamps use centisecond resolution:

```text
[hh:mm:ss:ff-hh:mm:ss:ff]
```

`ff` is hundredths of a second.

## Useful Options

- `--output-dir`: where Markdown transcript files are written.
- `--model`: Faster-Whisper model ID. Current default is `ivrit-ai/whisper-large-v3-turbo-ct2`.
- `--device`: inference device, such as `cpu` or `cuda`.
- `--compute-type`: CTranslate2 compute type, such as `int8`, `float16`, or `int8_float16`.
- `--language`: language hint. Use `he` for Hebrew. Use an empty string for automatic detection.
- `--beam-size`: decoding beam size.
- `--vad-filter`: enables voice activity detection before transcription.

## Output Naming

Output filenames are based on the source audio filename. Spaces are replaced with underscores.

Example:

```text
data/raw/2026_08_04-14_22_00 - ido.m4a
```

produces:

```text
data/processed/transcripts/2026_08_04-14_22_00_-_ido.transcript.md
```

## Repair Existing Markdown Timestamps

`tools/repair_markdown_timestamps.py` updates old Markdown transcripts from whole-second timestamps to centisecond timestamps using matching JSON sidecars from a previous run.

Dry run:

```powershell
.venv\Scripts\python.exe code\tools\repair_markdown_timestamps.py --dry-run
```

Repair the current external transcript folder in place:

```powershell
.venv\Scripts\python.exe code\tools\repair_markdown_timestamps.py
```

The default Markdown folder for this repair tool is:

```text
C:\תיק עבודות\טכניון\תואר שני\meetings\transcripts
```

The default JSON sidecar folder is:

```text
data/processed/transcripts/
```

To use different folders:

```powershell
.venv\Scripts\python.exe code\tools\repair_markdown_timestamps.py --markdown-dir "C:\path\to\transcripts" --json-dir "C:\path\to\json-sidecars"
```

The repair tool changes only the timestamp brackets in existing Markdown segment lines. It preserves the rest of each Markdown file.

## Notes

- New transcription runs do not write JSON sidecars.
- The first run may take longer because the model may need to download or load.
- Network access is required for the initial model download; later runs use the local model cache.
- CPU transcription can be slow for long meetings. For overnight runs, pass several files in one command so the model loads once.
- Transcripts are machine-generated drafts. Human review is required before a transcript or summary is treated as a valid lab record.
- The script does not perform speaker diarization.
