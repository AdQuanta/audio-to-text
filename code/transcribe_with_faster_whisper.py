"""Transcribe meeting audio with a local Faster-Whisper model.

Purpose:
    Create provisional meeting transcripts from local audio files.
Inputs:
    One or more audio paths, an output directory, and optional model/device
    settings. Audio is read through PyAV/FFmpeg-compatible decoding.
Method:
    Loads a CTranslate2 Faster-Whisper ASR model once, transcribes each audio
    file with timestamped segments, and records run provenance.
Outputs:
    For each input audio file, writes a Markdown transcript under the selected
    output directory.
Conventions:
    Segment timestamps are centisecond-resolution offsets from the start of the
    source audio. Default language hint is Hebrew ("he") and task is
    transcription, not translation.
Validation and limits:
    The transcript is machine-generated and unverified. Hebrew-English
    code-switching, speaker identity, punctuation, proper names, and technical
    vocabulary must be reviewed by a human before being treated as a lab record.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from faster_whisper import WhisperModel


DEFAULT_MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"


def format_time(seconds: float) -> str:
    total_centiseconds = int(round(seconds * 100))
    whole_seconds, centiseconds = divmod(total_centiseconds, 100)
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{centiseconds:02d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe local meeting audio files with Faster-Whisper."
    )
    parser.add_argument("audio", nargs="+", type=Path, help="Audio files to transcribe.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/transcripts"),
        help="Directory for Markdown transcript outputs.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Faster-Whisper model ID.")
    parser.add_argument("--device", default="cpu", help="Inference device, e.g. cpu or cuda.")
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="CTranslate2 compute type, e.g. int8, float16, or int8_float16.",
    )
    parser.add_argument(
        "--language",
        default="he",
        help="Language hint. Use an empty string for auto-detection.",
    )
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size for decoding.")
    parser.add_argument(
        "--vad-filter",
        action="store_true",
        help="Enable Silero VAD filtering before transcription.",
    )
    return parser.parse_args()


def transcribe_file(model: WhisperModel, audio_path: Path, args: argparse.Namespace) -> dict:
    language = args.language if args.language else None
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        task="transcribe",
        beam_size=args.beam_size,
        vad_filter=args.vad_filter,
        word_timestamps=False,
    )
    segments = [
        {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
        }
        for segment in segments_iter
    ]
    return {
        "source_audio": str(audio_path),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "device": args.device,
        "compute_type": args.compute_type,
        "language_hint": language,
        "detected_language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration_seconds": getattr(info, "duration", None),
        "beam_size": args.beam_size,
        "vad_filter": args.vad_filter,
        "status": "machine-generated-unverified",
        "segments": segments,
        "text": "\n".join(segment["text"] for segment in segments),
    }


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = Path(result["source_audio"])
    stem = source.stem.replace(" ", "_")
    md_path = output_dir / f"{stem}.transcript.md"

    lines = [
        f"# Transcript: {source.name}",
        "",
        "> Machine-generated transcript. Review before treating as a lab record.",
        "",
        "## Provenance",
        "",
        f"- Source audio: `{result['source_audio']}`",
        f"- Created UTC: `{result['created_utc']}`",
        f"- Model: `{result['model']}`",
        f"- Device: `{result['device']}`",
        f"- Compute type: `{result['compute_type']}`",
        f"- Language hint: `{result['language_hint']}`",
        f"- Detected language: `{result['detected_language']}`",
        f"- Duration seconds: `{result['duration_seconds']}`",
        f"- VAD filter: `{result['vad_filter']}`",
        "",
        "## Segments",
        "",
    ]
    for segment in result["segments"]:
        start = format_time(segment["start"])
        end = format_time(segment["end"])
        lines.append(f"- [{start}-{end}] {segment['text']}")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {md_path}")


def main() -> None:
    args = parse_args()
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    for audio_path in args.audio:
        result = transcribe_file(model, audio_path, args)
        write_outputs(result, args.output_dir)


if __name__ == "__main__":
    main()
