"""Repair Markdown transcript timestamps using JSON sidecars.

The original Markdown transcripts stored segment times as whole seconds. The JSON
sidecars kept the original floating-point segment start/end values. This tool
updates Markdown segment timestamp brackets in place to centisecond resolution:

    [hh:mm:ss:ff-hh:mm:ss:ff]

Only the timestamp bracket is changed. The existing Markdown text is preserved.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKDOWN_DIR = Path(r"C:\תיק עבודות\טכניון\תואר שני\meetings\transcripts")
DEFAULT_JSON_DIR = WORKSPACE_ROOT / "data" / "processed" / "transcripts"
SEGMENT_LINE_RE = re.compile(
    r"^(?P<prefix>- \[)"
    r"(?P<start>\d{2}:\d{2}:\d{2}(?::\d{2})?)"
    r"-"
    r"(?P<end>\d{2}:\d{2}:\d{2}(?::\d{2})?)"
    r"(?P<suffix>\].*)$"
)


def format_time(seconds: float) -> str:
    total_centiseconds = int(round(seconds * 100))
    whole_seconds, centiseconds = divmod(total_centiseconds, 100)
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{centiseconds:02d}"


def matching_json_path(markdown_path: Path, json_dir: Path) -> Path | None:
    json_name = markdown_path.name.removesuffix(".md") + ".json"
    candidates = [markdown_path.with_name(json_name), json_dir / json_name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def repair_markdown(markdown_path: Path, json_path: Path, backup: bool, dry_run: bool) -> str:
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    segments = data.get("segments", [])
    lines = markdown_path.read_text(encoding="utf-8-sig").splitlines()
    segment_line_indexes = [
        index for index, line in enumerate(lines) if SEGMENT_LINE_RE.match(line)
    ]

    if len(segment_line_indexes) != len(segments):
        return (
            f"SKIP {markdown_path.name}: Markdown has {len(segment_line_indexes)} "
            f"segment lines, JSON has {len(segments)} segments."
        )

    changed = 0
    for line_index, segment in zip(segment_line_indexes, segments):
        match = SEGMENT_LINE_RE.match(lines[line_index])
        if match is None:
            continue
        new_line = (
            f"{match.group('prefix')}"
            f"{format_time(float(segment['start']))}"
            f"-"
            f"{format_time(float(segment['end']))}"
            f"{match.group('suffix')}"
        )
        if new_line != lines[line_index]:
            lines[line_index] = new_line
            changed += 1

    if dry_run:
        return f"DRY-RUN {markdown_path.name}: would update {changed} timestamps."

    if backup:
        backup_path = markdown_path.with_suffix(markdown_path.suffix + ".bak")
        backup_path.write_text(markdown_path.read_text(encoding="utf-8-sig"), encoding="utf-8")

    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f"UPDATED {markdown_path.name}: {changed} timestamps."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update Markdown transcript timestamps from JSON sidecars."
    )
    parser.add_argument(
        "--markdown-dir",
        type=Path,
        default=DEFAULT_MARKDOWN_DIR,
        help="Directory containing Markdown transcripts to repair.",
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=DEFAULT_JSON_DIR,
        help="Directory containing matching JSON sidecars.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Write .bak files before modifying Markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without modifying files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    markdown_paths = sorted(args.markdown_dir.glob("*.transcript.md"))
    if not markdown_paths:
        raise SystemExit(f"No *.transcript.md files found in {args.markdown_dir}")

    failures = 0
    for markdown_path in markdown_paths:
        json_path = matching_json_path(markdown_path, args.json_dir)
        if json_path is None:
            print(f"SKIP {markdown_path.name}: no matching JSON sidecar found.")
            failures += 1
            continue
        message = repair_markdown(markdown_path, json_path, args.backup, args.dry_run)
        print(message)
        if message.startswith("SKIP"):
            failures += 1

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
