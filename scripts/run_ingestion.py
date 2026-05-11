from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        choices=["apple-notes", "onedrive"],
        default=os.getenv("THOUGHT_PIPELINE_INGESTION_MODE", "onedrive"),
    )
    parser.add_argument("--folder", default="Ideas")
    parser.add_argument("--url", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_URL", ""))
    parser.add_argument("--secret", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_SECRET", ""))
    parser.add_argument("--provider", choices=["auto", "local", "openai"], default="auto")
    parser.add_argument("--input-dir", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--include-processed", action="store_true")
    parser.add_argument("--skip-pending", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable]
    if args.source == "apple-notes":
        command.extend(
            [
                str(SCRIPTS_DIR / "pull_ios_notes.py"),
                "--folder",
                args.folder,
            ]
        )
        if args.url:
            command.extend(["--url", args.url])
        if args.secret:
            command.extend(["--secret", args.secret])
        if args.limit:
            command.extend(["--limit", str(args.limit)])
        if args.include_processed:
            command.append("--include-processed")
        if args.dry_run:
            command.append("--dry-run")
        if args.stdout:
            command.append("--stdout")
        if args.skip_pending:
            command.append("--skip-pending")
        return command

    command.extend(
        [
            str(SCRIPTS_DIR / "process_onedrive_shortcuts.py"),
            "--folder",
            args.folder,
            "--provider",
            args.provider,
        ]
    )
    if args.input_dir:
        command.extend(["--input-dir", args.input_dir])
    if args.url:
        command.extend(["--url", args.url])
    if args.secret:
        command.extend(["--secret", args.secret])
    if args.pretty:
        command.append("--pretty")
    return command


def main() -> int:
    args = parse_args()
    command = build_command(args)
    print("Running:", " ".join(command))
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
