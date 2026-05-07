from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA_PATH = ROOT / "schemas" / "input.schema.json"
OUTPUT_SCHEMA_PATH = ROOT / "schemas" / "output.schema.json"
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "later",
    "my",
    "of",
    "on",
    "or",
    "so",
    "that",
    "the",
    "them",
    "they",
    "this",
    "to",
    "turns",
    "up",
    "we",
    "with",
    "you"
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--provider", choices=["auto", "local", "openai"], default="auto")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | None, payload: dict, pretty: bool) -> None:
    text = json.dumps(payload, indent=2 if pretty else None, ensure_ascii=True)
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
        return
    sys.stdout.write(text + "\n")


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(payload: dict, schema_path: Path) -> None:
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(payload), key=lambda item: item.path)
    if errors:
        lines = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            lines.append(f"{location}: {error.message}")
        raise ValueError("Schema validation failed:\n" + "\n".join(lines))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def build_output_id(captured_at: str, capture_id: str) -> str:
    timestamp = captured_at.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "")
    return f"idea-{timestamp}-{capture_id}"


def build_local_summary(raw_idea: str) -> str:
    text = normalize_text(raw_idea)
    if len(text) <= 140:
      return text[0].upper() + text[1:]
    snippet = text[:137].rstrip(" ,.;:")
    return snippet + "..."


def build_local_tags(raw_idea: str) -> list[str]:
    counts: dict[str, int] = {}
    for word in re.findall(r"[A-Za-z][A-Za-z0-9]+", raw_idea.lower()):
        if len(word) < 4 or word in STOP_WORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    tags = [word for word, _ in ranked[:5]]
    if not tags:
        return ["idea"]
    return tags


def build_local_steps(raw_idea: str) -> list[str]:
    text = normalize_text(raw_idea)
    return [
        "Rewrite the idea into a one sentence problem statement",
        "List the first buildable workflow that proves the concept",
        f"Review whether this idea needs research, automation, or storage first: {text[:80]}{'...' if len(text) > 80 else ''}"
    ]


def enrich_local(payload: dict) -> dict:
    normalized = normalize_text(payload["raw_idea"])
    return {
        "id": build_output_id(payload["captured_at"], payload["capture_id"]),
        "raw_idea": normalized,
        "captured_at": payload["captured_at"],
        "source": payload["source"],
        "capture_id": payload["capture_id"],
        "summary": build_local_summary(normalized),
        "tags": build_local_tags(normalized),
        "next_steps": build_local_steps(normalized),
        "provider": "local",
        "processed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    }


def build_openai_request(payload: dict, output_schema: dict) -> dict:
    return {
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "thought_pipeline_output",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["summary", "tags", "next_steps"],
                    "properties": {
                        "summary": output_schema["properties"]["summary"],
                        "tags": output_schema["properties"]["tags"],
                        "next_steps": output_schema["properties"]["next_steps"]
                    }
                }
            }
        },
        "messages": [
            {
                "role": "system",
                "content": (
                    "You process captured ideas. Return concise JSON only. "
                    "Keep the summary short. Keep tags simple lowercase words. "
                    "Keep next_steps practical and specific."
                )
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "raw_idea": payload["raw_idea"],
                        "captured_at": payload["captured_at"],
                        "source": payload["source"],
                        "capture_id": payload["capture_id"]
                    },
                    ensure_ascii=True
                )
            }
        ]
    }


def enrich_openai(payload: dict) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required when provider is openai")
    output_schema = load_schema(OUTPUT_SCHEMA_PATH)
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=build_openai_request(payload, output_schema),
        timeout=60
    )
    response.raise_for_status()
    body = response.json()
    content = body["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    enriched = {
        "id": build_output_id(payload["captured_at"], payload["capture_id"]),
        "raw_idea": normalize_text(payload["raw_idea"]),
        "captured_at": payload["captured_at"],
        "source": payload["source"],
        "capture_id": payload["capture_id"],
        "summary": parsed["summary"],
        "tags": parsed["tags"],
        "next_steps": parsed["next_steps"],
        "provider": "openai",
        "processed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    }
    return enriched


def select_provider(choice: str) -> str:
    if choice in {"local", "openai"}:
        return choice
    return "openai" if os.getenv("OPENAI_API_KEY") else "local"


def main() -> int:
    args = parse_args()
    payload = load_json(args.input)
    validate_payload(payload, INPUT_SCHEMA_PATH)
    provider = select_provider(args.provider)
    result = enrich_openai(payload) if provider == "openai" else enrich_local(payload)
    validate_payload(result, OUTPUT_SCHEMA_PATH)
    write_json(args.output, result, args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
