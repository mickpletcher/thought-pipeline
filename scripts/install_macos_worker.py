from __future__ import annotations

import argparse
import plistlib
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LABEL = "com.thoughtpipeline.notespull"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-path", default=shutil.which("python3") or shutil.which("python") or "")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--folder", default="Ideas")
    parser.add_argument("--url", default="")
    parser.add_argument("--secret", default="")
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--load", action="store_true")
    return parser.parse_args()


def build_program_arguments(args: argparse.Namespace) -> list[str]:
    command = [
        args.python_path,
        str(ROOT / "scripts" / "pull_ios_notes.py"),
        "--folder",
        args.folder,
    ]
    if args.url:
        command.extend(["--url", args.url])
    if args.secret:
        command.extend(["--secret", args.secret])
    return command


def launch_agents_dir() -> Path:
    return Path.home() / "Library" / "LaunchAgents"


def output_dir() -> Path:
    return ROOT / "output"


def plist_path(label: str) -> Path:
    return launch_agents_dir() / f"{label}.plist"


def main() -> int:
    args = parse_args()
    if not args.python_path:
        raise SystemExit("Could not find python. Pass --python-path explicitly.")
    launch_agents_dir().mkdir(parents=True, exist_ok=True)
    output_dir().mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": args.label,
        "ProgramArguments": build_program_arguments(args),
        "WorkingDirectory": str(ROOT),
        "RunAtLoad": True,
        "StartInterval": args.interval_seconds,
        "StandardOutPath": str(output_dir() / "launchd.stdout.log"),
        "StandardErrorPath": str(output_dir() / "launchd.stderr.log"),
    }
    target = plist_path(args.label)
    with target.open("wb") as handle:
        plistlib.dump(plist, handle)
    print(f"Created plist: {target}")
    if args.load:
        subprocess.run(["launchctl", "unload", str(target)], check=False)
        subprocess.run(["launchctl", "load", str(target)], check=True)
        print(f"Loaded launchd job: {args.label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
