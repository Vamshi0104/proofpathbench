#!/usr/bin/env python3
"""Generate website test counts from the suites that visitors can run."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "release-meta.js"


def _run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode:
        raise SystemExit(result.stdout.rstrip() or f"command failed: {' '.join(command)}")
    return result.stdout


def _counts() -> tuple[int, int]:
    python_output = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    python_match = re.search(r"(\d+) tests? collected", python_output)
    if not python_match:
        raise RuntimeError("could not derive the benchmark validation-test count")

    test_files = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "docs" / "tests").glob("*.test.cjs"))
    node_output = _run(["node", "--test", *test_files])
    node_match = re.search(r"(?:#|ℹ) tests (\d+)", node_output)
    if not node_match:
        raise RuntimeError("could not derive the interactive-test count")
    return int(python_match.group(1)), int(node_match.group(1))


def _render(benchmark_tests: int, interactive_tests: int) -> str:
    return (
        "// Generated and verified by scripts/generate_release_metadata.py.\n"
        "window.PROOFPATH_RELEASE_META = Object.freeze({\n"
        f"  benchmarkValidationTests: {benchmark_tests},\n"
        f"  interactiveTests: {interactive_tests}\n"
        "});\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail instead of updating stale metadata")
    args = parser.parse_args()
    content = _render(*_counts())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("docs/release-meta.js is stale; regenerate it before release")
        print("Release metadata: current")
        return
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Release metadata: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
