from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import requests

from enrich_idea import enrich_local
from enrich_idea import enrich_openai
from enrich_idea import select_provider
from enrich_idea import validate_payload
from enrich_idea import INPUT_SCHEMA_PATH
from enrich_idea import OUTPUT_SCHEMA_PATH


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "output"
DEFAULT_SOURCE_NAME = "onedrive"
DEFAULT_INPUT_DIR = DEFAULT_OUTPUT_ROOT / "incoming" / DEFAULT_SOURCE_NAME / "Ideas"
DEFAULT_CAPTURED_DIR = DEFAULT_OUTPUT_ROOT / "captured" / DEFAULT_SOURCE_NAME
DEFAULT_ENRICHED_DIR = DEFAULT_OUTPUT_ROOT / "enriched" / DEFAULT_SOURCE_NAME
DEFAULT_ARCHIVE_DIR = DEFAULT_OUTPUT_ROOT / "processed" / DEFAULT_SOURCE_NAME
DEFAULT_FAILED_DIR = DEFAULT_OUTPUT_ROOT / "failed" / DEFAULT_SOURCE_NAME


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=os.getenv("THOUGHT_PIPELINE_ONEDRIVE_FOLDER", "Ideas"))
    parser.add_argument("--input-dir", default=os.getenv("THOUGHT_PIPELINE_ONEDRIVE_INPUT_DIR", ""))
    parser.add_argument("--captured-dir", default=str(DEFAULT_CAPTURED_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_ENRICHED_DIR))
    parser.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--failed-dir", default=str(DEFAULT_FAILED_DIR))
    parser.add_argument("--provider", choices=["auto", "local", "openai"], default="auto")
    parser.add_argument("--url", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_URL"))
    parser.add_argument("--secret", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_SECRET"))
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict, pretty: bool) -> None:
    text = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def post_payload(payload: dict, url: str, secret: str | None) -> None:
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Webhook-Secret"] = secret
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()


def move_file(source: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if target.exists():
        target.unlink()
    shutil.move(str(source), str(target))
    return target


def resolve_input_dir(args: argparse.Namespace) -> Path:
    if args.input_dir:
        return Path(args.input_dir)
    onedrive_root = os.getenv("OneDrive")
    if onedrive_root:
        return Path(onedrive_root) / "Shortcuts" / "thought-pipeline" / args.folder
    return DEFAULT_OUTPUT_ROOT / "incoming" / DEFAULT_SOURCE_NAME / args.folder


def process_file(path: Path, args: argparse.Namespace, provider: str) -> tuple[str, str]:
    payload = load_json(path)
    validate_payload(payload, INPUT_SCHEMA_PATH)

    captured_path = Path(args.captured_dir) / path.name
    write_json(captured_path, payload, args.pretty)

    result = enrich_openai(payload) if provider == "openai" else enrich_local(payload)
    validate_payload(result, OUTPUT_SCHEMA_PATH)

    output_path = Path(args.output_dir) / path.name
    write_json(output_path, result, args.pretty)

    if args.url:
        post_payload(payload, args.url, args.secret)

    archived_path = move_file(path, Path(args.archive_dir))
    return str(output_path), str(archived_path)


def main() -> int:
    args = parse_args()
    provider = select_provider(args.provider)
    input_dir = resolve_input_dir(args)
    input_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(path for path in input_dir.glob("*.json") if path.is_file())
    if not files:
        print("NO_FILES")
        return 0

    failed_dir = Path(args.failed_dir)
    for path in files:
        try:
            output_path, archived_path = process_file(path, args, provider)
            print(f"PROCESSED {path.name} -> {output_path}")
            print(f"ARCHIVED {path.name} -> {archived_path}")
        except Exception as exc:
            failed_path = move_file(path, failed_dir)
            print(f"FAILED {path.name} -> {failed_path}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
