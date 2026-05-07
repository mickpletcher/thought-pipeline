from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA_PATH = ROOT / "schemas" / "input.schema.json"
DEFAULT_OUTPUT_ROOT = ROOT / "output"
DEFAULT_STATE_PATH = DEFAULT_OUTPUT_ROOT / "ios-notes-state.json"
DEFAULT_EXPORT_DIR = DEFAULT_OUTPUT_ROOT / "ios-notes"
DEFAULT_PENDING_DIR = DEFAULT_OUTPUT_ROOT / "pending-webhook"
DEFAULT_LOG_PATH = DEFAULT_OUTPUT_ROOT / "ios-notes-run.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=os.getenv("THOUGHT_PIPELINE_NOTES_FOLDER", "Ideas"))
    parser.add_argument("--state", default=os.getenv("THOUGHT_PIPELINE_NOTES_STATE", str(DEFAULT_STATE_PATH)))
    parser.add_argument("--output-dir", default=os.getenv("THOUGHT_PIPELINE_NOTES_OUTPUT_DIR", str(DEFAULT_EXPORT_DIR)))
    parser.add_argument("--pending-dir", default=os.getenv("THOUGHT_PIPELINE_PENDING_DIR", str(DEFAULT_PENDING_DIR)))
    parser.add_argument("--log-path", default=os.getenv("THOUGHT_PIPELINE_LOG_PATH", str(DEFAULT_LOG_PATH)))
    parser.add_argument("--url", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_URL"))
    parser.add_argument("--secret", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_SECRET"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--include-processed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--skip-pending", action="store_true")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_log(log_path: Path, event: str, **details: object) -> None:
    ensure_parent(log_path)
    record = {
        "timestamp": utc_now(),
        "event": event,
        "details": details,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validator() -> Draft202012Validator:
    schema = load_schema(INPUT_SCHEMA_PATH)
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def validate_payload(payload: dict) -> None:
    errors = sorted(validator().iter_errors(payload), key=lambda item: item.path)
    if errors:
        messages = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            messages.append(f"{location}: {error.message}")
        raise ValueError("Schema validation failed:\n" + "\n".join(messages))


def ensure_macos() -> None:
    if platform.system() != "Darwin":
        raise SystemExit("Apple Notes pull only works on macOS because it uses osascript.")


def applescript_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def read_notes(folder_name: str) -> list[dict]:
    folder_literal = applescript_escape(folder_name)
    script = f'''
    set outputList to {{}}
    tell application "Notes"
        if not (exists folder "{folder_literal}") then
            error "Notes folder not found: {folder_literal}"
        end if
        repeat with n in notes of folder "{folder_literal}"
            set end of outputList to id of n & "|||" & name of n & "|||" & body of n & "|||" & (modification date of n as string)
        end repeat
    end tell
    set AppleScript's text item delimiters to "###"
    return outputList as string
    '''
    raw = subprocess.check_output(["osascript", "-e", script], text=True)
    notes: list[dict] = []
    for item in raw.split("###"):
        item = item.strip()
        if not item:
            continue
        parts = item.split("|||", 3)
        if len(parts) != 4:
            continue
        note_id, title, body, modified = parts
        notes.append(
            {
                "note_id": note_id.strip(),
                "title": title.strip(),
                "body": body.strip(),
                "modified_text": modified.strip(),
            }
        )
    return notes


def normalize_note_body(body: str) -> str:
    text = body.replace("<br>", "\n").replace("<div>", "\n").replace("</div>", "\n")
    for token in ["<html>", "</html>", "<body>", "</body>", "<p>", "</p>"]:
        text = text.replace(token, "\n")
    text = text.replace("&nbsp;", " ")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


def parse_modified_text(value: str) -> str:
    formats = [
        "%A, %B %d, %Y at %I:%M:%S %p",
        "%A, %B %d, %Y at %I:%M:%S %p %Z",
        "%a %b %d %H:%M:%S %Y",
    ]
    for current in formats:
        try:
            parsed = datetime.strptime(value, current)
            local_tz = datetime.now().astimezone().tzinfo
            if local_tz is not None:
                parsed = parsed.replace(tzinfo=local_tz)
            return parsed.isoformat()
        except ValueError:
            continue
    return value


def note_to_payload(note: dict) -> dict:
    body = normalize_note_body(note["body"])
    raw_idea = body or note["title"]
    payload = {
        "raw_idea": raw_idea,
        "captured_at": parse_modified_text(note["modified_text"]),
        "source": "ios_notes",
        "capture_id": note["note_id"],
    }
    validate_payload(payload)
    return payload


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"processed": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def is_processed(state: dict, payload: dict) -> bool:
    processed = state.get("processed", {})
    return processed.get(payload["capture_id"]) == payload["captured_at"]


def mark_processed(state: dict, payload: dict) -> None:
    state.setdefault("processed", {})[payload["capture_id"]] = payload["captured_at"]


def safe_name(value: str) -> str:
    return value.replace("/", "_").replace(":", "_").replace("\\", "_")


def write_payload(output_dir: Path, payload: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{safe_name(payload['capture_id'])}.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return target


def queue_payload(pending_dir: Path, payload: dict) -> Path:
    pending_dir.mkdir(parents=True, exist_ok=True)
    target = pending_dir / f"{safe_name(payload['capture_id'])}.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return target


def post_payload(url: str, secret: str | None, payload: dict) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Webhook-Secret"] = secret
    return requests.post(url, headers=headers, json=payload, timeout=60)


def flush_pending_queue(pending_dir: Path, url: str | None, secret: str | None, log_path: Path, dry_run: bool) -> tuple[int, int]:
    if not url or not pending_dir.exists():
        return 0, 0
    retried = 0
    delivered = 0
    for file_path in sorted(pending_dir.glob("*.json")):
        retried += 1
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if dry_run:
            append_log(log_path, "pending_queue_skip_dry_run", file=str(file_path))
            continue
        try:
            response = post_payload(url, secret, payload)
            response.raise_for_status()
            file_path.unlink()
            delivered += 1
            append_log(log_path, "pending_queue_delivered", file=str(file_path), status_code=response.status_code)
        except Exception as exc:
            append_log(log_path, "pending_queue_failed", file=str(file_path), error=str(exc))
    return retried, delivered


def main() -> int:
    args = parse_args()
    ensure_macos()
    state_path = Path(args.state)
    output_dir = Path(args.output_dir)
    pending_dir = Path(args.pending_dir)
    log_path = Path(args.log_path)
    append_log(log_path, "run_started", folder=args.folder, webhook=bool(args.url), dry_run=args.dry_run)
    state = load_state(state_path)
    retried_count = 0
    delivered_count = 0
    if not args.skip_pending:
        retried_count, delivered_count = flush_pending_queue(pending_dir, args.url, args.secret, log_path, args.dry_run)
    notes = read_notes(args.folder)
    processed_count = 0
    exported_count = 0
    posted_count = 0
    queued_count = 0
    for note in notes:
        payload = note_to_payload(note)
        if not args.include_processed and is_processed(state, payload):
            continue
        if args.limit and processed_count >= args.limit:
            break
        processed_count += 1
        if args.stdout:
            sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
        if not args.dry_run:
            write_payload(output_dir, payload)
            exported_count += 1
        if args.url and not args.dry_run:
            try:
                response = post_payload(args.url, args.secret, payload)
                response.raise_for_status()
                posted_count += 1
                append_log(log_path, "payload_posted", capture_id=payload["capture_id"], status_code=response.status_code)
            except Exception as exc:
                queue_payload(pending_dir, payload)
                queued_count += 1
                append_log(log_path, "payload_queued", capture_id=payload["capture_id"], error=str(exc))
        mark_processed(state, payload)
    if not args.dry_run:
        save_state(state_path, state)
    summary = {
        "folder": args.folder,
        "notes_seen": len(notes),
        "payloads_processed": processed_count,
        "payloads_exported": exported_count,
        "payloads_posted": posted_count,
        "payloads_queued": queued_count,
        "pending_retried": retried_count,
        "pending_delivered": delivered_count,
        "state_path": str(state_path),
        "output_dir": str(output_dir),
        "pending_dir": str(pending_dir),
        "log_path": str(log_path),
    }
    append_log(log_path, "run_completed", **summary)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
