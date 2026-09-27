# Audio To Text Tool Workspace

This workspace owns reusable audio-transcription tooling and experiments.

## Purpose

Use this folder for free/local audio-to-text setup, model trials, raw audio staging, generated transcripts, and summary drafts before manually promoting selected outputs into a separate research project's records.

## Boundaries

- Keep transcription code in `code/`.
- Put raw input audio in `data/raw/`.
- Put generated transcripts and derived outputs in `data/processed/`.
- Put tool decisions, comparison notes, and trial-run documentation in `docs/specs/`. Each file name under start with date_time: `docs/specs/yyyy-mm-dd_hh-mm-ss_subject.md`

## Environment

Use this workspace's own Python environment. The first accepted environment decision is to use `uv` with `.venv`, `pyproject.toml`, and `uv.lock` local to this folder.

## Transcript Status

Machine transcripts are drafts. Human review is required before a transcript or summary is valid to be copied into a project's `lab_log/meetings` folder.
