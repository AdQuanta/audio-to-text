# Full Raw Transcription Night Run

Date: 2026-08-24

## Goal

Transcribe all recordings staged under `data/raw/`.

The two shortest recordings were already completed and verified in
`docs/specs/2026-08-23_21-03-15_initial-transcription-smoke-test.md`.

## Method

Pipeline: `faster-whisper` with `ivrit-ai/whisper-large-v3-turbo-ct2`.

Settings:

- Device: `cpu`
- Compute type: `int8`
- Language hint: `he`
- Beam size: `5`
- VAD filter: enabled

Representative longer-file trial:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "data\raw\2026_08_04-14_22_00 - ido.m4a" --output-dir data\processed\transcripts --model ivrit-ai/whisper-large-v3-turbo-ct2 --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

Full remaining batch:

```powershell
.venv\Scripts\python.exe code\transcribe_with_faster_whisper.py "data\raw\2025_12_08-08_30_00 - michael birk and tom.m4a" "data\raw\2026_06_09-10_00_00 - michael yannai.m4a" "data\raw\2026_06_15-13_30_00 - ido.m4a" "data\raw\2026_06_17-11_30_00 - tomer bar lev.m4a" "data\raw\2026_06_24-13_57_00 - yuval adiv.m4a" "data\raw\2026_06_25-12_05_00 - michael yannai and tom.m4a" --output-dir data\processed\transcripts --model ivrit-ai/whisper-large-v3-turbo-ct2 --device cpu --compute-type int8 --language he --beam-size 5 --vad-filter
```

## Output Inventory

All 9 raw `.m4a` files now have matching `.transcript.md` and `.transcript.json`
files under `data/processed/transcripts/`.

| Source | Minutes | Segments | Detected language | Language probability |
| --- | ---: | ---: | --- | ---: |
| `2025_12_08-08_30_00 - michael birk and tom.m4a` | 47.17 | 604 | he | 1 |
| `2026_06_09-10_00_00 - michael yannai.m4a` | 46.37 | 598 | he | 1 |
| `2026_06_15-13_30_00 - ido.m4a` | 80.54 | 1052 | he | 1 |
| `2026_06_17-11_30_00 - tomer bar lev.m4a` | 77.55 | 1032 | he | 1 |
| `2026_06_24-13_57_00 - yuval adiv.m4a` | 66.59 | 974 | he | 1 |
| `2026_06_25-12_05_00 - michael yannai and tom.m4a` | 74.68 | 1060 | he | 1 |
| `2026_08_02-18_05_00 - ido.m4a` | 1.24 | 22 | he | 1 |
| `2026_08_02-18_15_00 - ido.m4a` | 0.79 | 16 | he | 1 |
| `2026_08_04-14_22_00 - ido.m4a` | 13.75 | 228 | he | 1 |

## Validation Performed

- Confirmed each raw audio file has both Markdown and JSON transcript outputs.
- Checked each new long-file JSON sidecar for duration, segment count, detected language, language probability, text length, first segment, and last segment.
- Checked repeated segment clusters on representative long files; observed repeats were ordinary short acknowledgements such as "yes" or "okay", not obvious runaway hallucination loops.
- The Windows terminal renders Hebrew as mojibake in command output, but the transcript files are written as UTF-8 with `ensure_ascii=False`, matching the earlier smoke-test behavior.

## Caveats

- These are machine-generated draft transcripts only.
- They are not diarized.
- Hebrew-English code-switching, speaker identity, punctuation, proper names, and technical vocabulary still require human review before promotion into any research project's lab records.
- CPU-only throughput is slow but completed successfully. This run did not require switching to another method from `docs/specs/2026-08-23_20-22-00_transcribe-options.md`.
