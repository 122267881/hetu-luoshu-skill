#!/usr/bin/env python3
"""Run all deterministic validation and regression tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(label: str, command: list[str], root: Path) -> int:
    print(f"==> {label}", flush=True)
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode:
        print(f"Check failed: {label}", file=sys.stderr)
    return result.returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands = [
        ("quality", [sys.executable, "scripts/quality_check.py", "."]),
        ("models", [sys.executable, "scripts/validate_models.py"]),
        ("knowledge", [sys.executable, "scripts/knowledge_cli.py", "validate-kb"]),
        ("tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ]
    for label, command in commands:
        code = run(label, command, root)
        if code:
            return code
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
