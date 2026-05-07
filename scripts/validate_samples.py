from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def validate(instance_path: Path, schema_path: Path) -> None:
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(instance), key=lambda item: item.path)
    if errors:
        lines = []
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            lines.append(f"{instance_path.name} {location}: {error.message}")
        raise SystemExit("\n".join(lines))


def main() -> int:
    validate(ROOT / "samples" / "sample-input.json", ROOT / "schemas" / "input.schema.json")
    validate(ROOT / "samples" / "sample-ios-note-payload.json", ROOT / "schemas" / "input.schema.json")
    validate(ROOT / "samples" / "sample-output.json", ROOT / "schemas" / "output.schema.json")
    print("SAMPLES_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
