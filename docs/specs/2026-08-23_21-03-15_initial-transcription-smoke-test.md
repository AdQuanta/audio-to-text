# Initial Transcription Smoke Test

Date: 2026-08-23

## Decision 1: Environment Location

Use a dedicated `uv` Python environment inside this `Audio to text` tool workspace.

Rationale: transcription tooling is general-purpose and dependency-heavy. It should not be installed into unrelated research repositories, and transcription code should not live in a project's `lab_log` folder.

Chosen files:

- `pyproject.toml`
- `.python-version`
- `.venv/` after `uv sync`
- `uv.lock` after dependency resolution

## Current Structure

- `code/`: reusable transcription scripts.
- `data/raw/`: local raw audio staging area.
- `data/processed/transcripts/`: generated transcript drafts and sidecars.
- `docs/specs/`: tool decisions, model comparisons, and trial-run notes.

## First Pipeline Tested

Pipeline: `faster-whisper` using `ivrit-ai/whisper-large-v3-turbo-ct2`.

Reason: the first-pass goal was a free, local, Hebrew-first pipeline that can run on the available Windows machine. Heavy models such as VibeVoice or Caspi may still be worth comparing, but they are not a safe first assumption for a 4 GB GTX 1650 / CPU-first workflow.

Command used in the original smoke test:

```powershell
.venv\Scripts\python.exe "lab_log\meetings\scripts\transcribe_with_faster_whisper.py" "lab_log\meetings\2026_08_02-18_15_00 - ido.m4a" "lab_log\meetings\2026_08_02-18_05_00 - ido.m4a" --output-dir "lab_log\meetings\transcripts" --model "ivrit-ai/whisper-large-v3-turbo-ct2" --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

That command was run from the wrong project repository. The code and outputs have now been moved here. Future runs should instead use paths under this workspace, for example:

```powershell
uv run python "code\transcribe_with_faster_whisper.py" "data\raw\example.m4a" --output-dir "data\processed\transcripts" --model "ivrit-ai/whisper-large-v3-turbo-ct2" --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

## Inputs Tested

- `2026_08_02-18_15_00 - ido.m4a`: 47.350 s, 297590 bytes.
- `2026_08_02-18_05_00 - ido.m4a`: 74.624 s, 468231 bytes.

The raw audio files remain in the source project for now. This workspace currently holds the generated transcript drafts from that trial.

## Outputs Preserved Here

- `data/processed/transcripts/2026_08_02-18_15_00_-_ido.transcript.md`
- `data/processed/transcripts/2026_08_02-18_15_00_-_ido.transcript.json`
- `data/processed/transcripts/2026_08_02-18_05_00_-_ido.transcript.md`
- `data/processed/transcripts/2026_08_02-18_05_00_-_ido.transcript.json`

## Observations

- The model downloaded successfully from Hugging Face. The CT2 model file is about 1.6 GB.
- CPU `int8` transcription completed successfully, but slowly: roughly 7.5 minutes wall time including first model download/load for about 2 minutes of audio.
- Output files are UTF-8 Hebrew; some Windows terminal views may display Hebrew as mojibake even when the files are valid.
- Output is not diarized.
- These transcripts are machine-generated drafts and require human review before being copied into any project lab log.

## Next Trials

- Re-run from this workspace with raw audio staged under `data/raw/`.
- Compare throughput and quality on a representative longer recording.
- Consider a smaller Faster-Whisper draft model if CPU runtime is unacceptable.
- Compare Caspi or VibeVoice only if hardware/runtime constraints are explicitly accepted.
