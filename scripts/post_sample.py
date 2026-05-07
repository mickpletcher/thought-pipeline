from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE = ROOT / "samples" / "sample-input.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_URL"))
    parser.add_argument("--secret", default=os.getenv("THOUGHT_PIPELINE_WEBHOOK_SECRET"))
    parser.add_argument("--input", default=str(DEFAULT_SAMPLE))
    parser.add_argument("--timeout", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.url:
        raise SystemExit("Webhook URL is required. Pass --url or set THOUGHT_PIPELINE_WEBHOOK_URL.")
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    headers = {"Content-Type": "application/json"}
    if args.secret:
        headers["X-Webhook-Secret"] = args.secret
    response = requests.post(args.url, headers=headers, json=payload, timeout=args.timeout)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=True))
    except ValueError:
        print(response.text)
    response.raise_for_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
