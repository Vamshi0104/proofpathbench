#!/usr/bin/env python3
"""Validate public archive hygiene and final release-scope claims."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "proofpath_benchmark.pdf"
SOURCE = ROOT / "output" / "proofpath_arxiv_source.tar.gz"
ARTIFACT = ROOT / "output" / "proofpath_artifact.tar.gz"
FORBIDDEN_MEMBER = re.compile(
    r"(^|/)(review_key|blinding_manifest)\.json$|(^|/)results/raw/.+|"
    r"(^|/)\.env($|\.)|(^|/)__pycache__(/|$)|\.py[co]$|(^|/)\.DS_Store$|"
    r"(^|/)\._|(^|/)__MACOSX(/|$)|(^|/)\.(idea|vscode)(/|$)|\.swp$|~$"
)
SECRET_PATTERN = re.compile(
    rb"AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    rb"xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|"
    rb"/Users/[^/\s]+|/home/[^/\s]+|[A-Z]:\\Users\\"
)
SCAN_SUFFIXES = {".md", ".tex", ".bib", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt", ".csv", ".cff"}


def archive_members(path: Path) -> tuple[set[str], tarfile.TarFile]:
    archive = tarfile.open(path, "r:gz")
    ordered = [member.name.removeprefix("./") for member in archive.getmembers()]
    if len(ordered) != len(set(ordered)):
        duplicates = sorted({name for name in ordered if ordered.count(name) > 1})
        archive.close()
        raise SystemExit(f"duplicate archive members found in {path.name}: {duplicates}")
    return set(ordered), archive


def check_artifact() -> None:
    if not ARTIFACT.is_file() or ARTIFACT.stat().st_size == 0:
        raise SystemExit(f"missing artifact: {ARTIFACT}")
    names, archive = archive_members(ARTIFACT)
    try:
        bad = sorted(name for name in names if FORBIDDEN_MEMBER.search(name))
        if bad:
            raise SystemExit(f"private/generated artifact members found: {bad}")
        required = {
            "LICENSE", "README.md", "CITATION.cff",
            "benchmark/validation_report.json",
            "benchmark/runtime_validation_report.json",
            "research/FINAL_ARXIV_READINESS.md",
            "research/confound_diagnostics.json",
            "research/textual_integrity_audit.md",
            "research/human_validation/protocol.md",
            "research/human_validation/review_form.csv",
            "research/human_validation/sampled_items.json",
        }
        if missing := sorted(required - names):
            raise SystemExit(f"missing ancillary members: {missing}")
        # Release scanners necessarily contain the credential/path signatures
        # they search for.  Exempt only those scanner implementations from
        # content matching; their presence and filenames are still audited.
        skip = {
            "scripts/check_public_release.py",
            "scripts/check_website_release.py",
            "scripts/build_artifact.py",
        }
        for member in archive.getmembers():
            name = member.name.removeprefix("./")
            if name in skip or not member.isfile() or Path(name).suffix.lower() not in SCAN_SUFFIXES:
                continue
            stream = archive.extractfile(member)
            content = stream.read() if stream else b""
            if SECRET_PATTERN.search(content):
                raise SystemExit(f"credential pattern or local absolute path found in {name}")
    finally:
        archive.close()


def check_final() -> None:
    for path in (PDF, SOURCE):
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing public release file: {path}")
    source_names, archive = archive_members(SOURCE)
    archive.close()
    required = {
        "main.tex", "main.bbl", "references.bib",
        "figures/proofpath_architecture.pdf",
        "figures/prospective_power.pdf",
        "anc/proofpath_artifact.tar.gz",
    }
    if missing := sorted(required - source_names):
        raise SystemExit(f"missing arXiv-source members: {missing}")
    with tempfile.TemporaryDirectory(prefix="proofpath-release-check-") as directory:
        text_path = Path(directory) / "paper.txt"
        subprocess.run(["pdftotext", str(PDF), str(text_path)], check=True)
        normalized = " ".join(text_path.read_text(encoding="utf-8").split())
    claims = (
        "96 synthetic scenarios", "384 task-treatment units",
        "768 no-fault plan executions", "nine seeded failure types",
        "does not report results from language models",
    )
    if missing := [claim for claim in claims if claim not in normalized]:
        raise SystemExit(f"required scope statements absent from PDF: {missing}")
    if re.search(r"Author identity to be supplied|Firstname Lastname|\b(?:TODO|TBD)\b", normalized, re.IGNORECASE):
        raise SystemExit("placeholder text remains in public PDF")
    runtime = json.loads((ROOT / "benchmark/runtime_validation_report.json").read_text())
    counts = runtime["scenario_count"], runtime["split_plot_unit_count"], runtime["no_fault_plan_executions"]
    if counts != (96, 384, 768):
        raise SystemExit(f"runtime report counts disagree with the paper: {counts}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-only", action="store_true")
    args = parser.parse_args()
    check_artifact()
    if not args.archive_only:
        check_final()
    print("Public release check: PASS")


if __name__ == "__main__":
    main()
