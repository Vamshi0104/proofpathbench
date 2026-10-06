#!/usr/bin/env python3
"""Build the additive ProofPathBench Zenodo release without touching arXiv assets."""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "zenodo"
ARTIFACT_DIR = RELEASE / "artifact"
VALIDATION_DIR = RELEASE / "validation"
PAPER_SOURCE = ROOT / "output" / "pdf" / "proofpath_benchmark.pdf"
SOURCE_DATE_EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "1791244800"))
RELEASE_DATE = "2026-10-06"
TITLE = "ProofPathBench: A Benchmark for Verifiability-Aware Planning by Tool-Using Language Agents"
AUTHOR_GIVEN = "Vamshi Krishna"
AUTHOR_FAMILY = "Madhavan"
AUTHOR_AFFILIATION = "Independent Researcher"
AUTHOR_EMAIL = "vamshi-madhavan@outlook.com"
REPOSITORY_URL = "https://github.com/Vamshi0104/proofpathbench"
PROJECT_URL = "https://vamshi0104.github.io/proofpathbench/"
ZENODO_DOI_PATTERN = re.compile(r"^10\.5281/zenodo\.\d+$")

PROHIBITED_PARTS = {
    ".git", ".github", "node_modules", "venv", ".venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "htmlcov",
    ".idea", ".vscode", "__MACOSX", "tmp", "output",
}
PROHIBITED_SUFFIXES = {".pyc", ".pyo", ".swp", ".swo", ".log"}
RESEARCH_FILES = {
    "PREREGISTRATION_DRAFT.md", "citation_audit.md", "confound_diagnostics.json",
    "experiment_log.md", "hypotheses.md", "limitations.md", "model_selection.md",
    "novelty_criteria.md", "pilot_cost_estimate.json", "pilot_plan.md",
    "power_analysis.json", "prepilot_status.json", "related_work_matrix.md",
    "research_questions.md", "search_protocol.md", "textual_integrity_audit.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version() -> str:
    match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError("canonical version not found in pyproject.toml")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if not re.search(rf"^version:\s*{re.escape(match.group(1))}\s*$", citation, re.MULTILINE):
        raise RuntimeError("pyproject.toml and canonical CITATION.cff versions disagree")
    return match.group(1)


def configured_zenodo_doi() -> str | None:
    config = (ROOT / "docs/site-config.js").read_text(encoding="utf-8")
    match = re.search(r'zenodoDoi:\s*["\']([^"\']*)["\']', config)
    if not match:
        raise RuntimeError("docs/site-config.js lacks zenodoDoi")
    doi = match.group(1)
    if doi and not ZENODO_DOI_PATTERN.fullmatch(doi):
        raise RuntimeError(f"invalid configured Zenodo DOI: {doi}")
    return doi or None


def arxiv_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or RELEASE in path.parents:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if "arxiv" in relative.casefold():
            snapshot[relative] = sha256(path)
    return snapshot


def assert_release_boundary() -> None:
    if "arxiv" in RELEASE.as_posix().casefold() or ROOT not in RELEASE.parents:
        raise RuntimeError("unsafe Zenodo release path")
    for target in (
        RELEASE / "PAPER.pdf", RELEASE / "CITATION.cff", RELEASE / "metadata.json",
        RELEASE / "LICENSE", RELEASE / "CHECKSUMS.sha256", ARTIFACT_DIR,
        VALIDATION_DIR,
    ):
        if "arxiv" in target.as_posix().casefold():
            raise RuntimeError(f"refusing arXiv write target: {target}")


def write_metadata(release_version: str, zenodo_doi: str | None) -> None:
    description = (
        "ProofPathBench is an implemented research benchmark for whether tool-using "
        "language agents select matched plans that produce independent evidence of "
        "external-state outcomes. Version 0.0.1 contains 96 synthetic scenarios across "
        "eight domains, 384 task-treatment units, 768 deterministic no-fault plan "
        "executions, and nine seeded failure classes. The deposit includes a research "
        "preprint and an Apache-2.0 benchmark software artifact. It reports no provider-"
        "model behavioral results; fixtures and prospective power simulations are not "
        "empirical model results. A blinded human construct-validation protocol is "
        "included but has not been run. The work has not undergone peer review. "
        f"Author: {AUTHOR_GIVEN} {AUTHOR_FAMILY}, {AUTHOR_AFFILIATION}. "
        f"Correspondence: {AUTHOR_EMAIL}. Source repository: {REPOSITORY_URL}. "
        f"Project website: {PROJECT_URL}."
    )
    identifier_note = (
        f"Zenodo DOI: {zenodo_doi}. No arXiv identifier, ORCID, or funding record is asserted."
        if zenodo_doi
        else "No DOI, Zenodo record ID, arXiv identifier, ORCID, or funding record is asserted."
    )
    payload = {
        "metadata": {
            "upload_type": "publication",
            "publication_type": "preprint",
            "title": TITLE,
            "creators": [{
                "name": f"{AUTHOR_FAMILY}, {AUTHOR_GIVEN}",
                "affiliation": AUTHOR_AFFILIATION,
            }],
            "description": description,
            "access_right": "open",
            "license": "Apache-2.0",
            "keywords": [
                "tool-using language agents", "LLM agents", "verification",
                "verifiability-aware planning", "agent reliability", "tool use",
                "benchmark", "false success", "state verification", "evaluation",
            ],
            "language": "eng",
            "version": release_version,
            "publication_date": RELEASE_DATE,
            "related_identifiers": [
                {
                    "identifier": REPOSITORY_URL,
                    "relation": "isSupplementedBy",
                    "resource_type": "software",
                },
                {
                    "identifier": PROJECT_URL,
                    "relation": "isDocumentedBy",
                    "resource_type": "other",
                },
            ],
            "notes": (
                "Research preprint with a benchmark software artifact; not peer reviewed. "
                f"Corresponding author: {AUTHOR_GIVEN} {AUTHOR_FAMILY} "
                f"({AUTHOR_AFFILIATION}), {AUTHOR_EMAIL}. "
                "Apache-2.0 is the canonical software/artifact license. The repository "
                "does not declare a separate manuscript content license; confirm that "
                f"license manually before publication. {identifier_note}"
            ),
        }
    }
    if zenodo_doi:
        payload["metadata"]["doi"] = zenodo_doi
    (RELEASE / "metadata.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_citation(release_version: str, zenodo_doi: str | None) -> None:
    doi_line = f'doi: "{zenodo_doi}"\n' if zenodo_doi else ""
    preferred_doi_line = f'  doi: "{zenodo_doi}"\n' if zenodo_doi else ""
    content = f'''cff-version: 1.2.0
message: "If you use ProofPathBench, please cite the research release below."
title: "{TITLE}"
type: software
version: {release_version}
date-released: {RELEASE_DATE}
authors:
  - family-names: {AUTHOR_FAMILY}
    given-names: {AUTHOR_GIVEN}
    affiliation: {AUTHOR_AFFILIATION}
    email: {AUTHOR_EMAIL}
repository-code: "{REPOSITORY_URL}"
url: "{PROJECT_URL}"
{doi_line}license: Apache-2.0
abstract: >-
  A deterministic benchmark and evaluation protocol for measuring whether tool-using
  language agents select plans that produce independent evidence of external outcomes.
keywords:
  - tool-using language agents
  - verification
  - verifiability-aware planning
  - agent reliability
  - benchmark
preferred-citation:
  type: article
  title: "{TITLE}"
  authors:
    - family-names: {AUTHOR_FAMILY}
      given-names: {AUTHOR_GIVEN}
      affiliation: {AUTHOR_AFFILIATION}
      email: {AUTHOR_EMAIL}
  year: 2026
{preferred_doi_line}'''
    (RELEASE / "CITATION.cff").write_text(content, encoding="utf-8")


def prohibited(relative: PurePosixPath) -> bool:
    if any(part in PROHIBITED_PARTS or part.startswith("._") for part in relative.parts):
        return True
    if any(part.startswith(".") for part in relative.parts):
        return True
    if relative.name == ".DS_Store" or relative.name.endswith("~"):
        return True
    return relative.suffix.casefold() in PROHIBITED_SUFFIXES


def artifact_sources() -> list[tuple[Path, PurePosixPath]]:
    selected: list[tuple[Path, PurePosixPath]] = [
        (ARTIFACT_DIR / "README.md", PurePosixPath("README.md")),
        (ROOT / "LICENSE", PurePosixPath("LICENSE")),
        (ROOT / "CITATION.cff", PurePosixPath("CITATION.cff")),
        (ROOT / "pyproject.toml", PurePosixPath("pyproject.toml")),
        (ROOT / "requirements.txt", PurePosixPath("requirements.txt")),
        (ROOT / "paper" / "build_assets.py", PurePosixPath("paper/build_assets.py")),
    ]
    for directory in ("benchmark", "configs", "experiments", "proofpath", "tests"):
        base = ROOT / directory
        for path in base.rglob("*"):
            if path.is_file():
                selected.append((path, PurePosixPath(path.relative_to(ROOT).as_posix())))
    for name in RESEARCH_FILES:
        selected.append((ROOT / "research" / name, PurePosixPath(f"research/{name}")))
    for path in (ROOT / "research" / "human_validation").rglob("*"):
        if path.is_file():
            selected.append((path, PurePosixPath(path.relative_to(ROOT).as_posix())))
    for directory in ("paper/figures", "paper/tables"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file():
                selected.append((path, PurePosixPath(path.relative_to(ROOT).as_posix())))
    clean: list[tuple[Path, PurePosixPath]] = []
    for source, relative in selected:
        if not source.is_file():
            raise RuntimeError(f"missing artifact source: {source}")
        if source.is_symlink():
            raise RuntimeError(f"symlink not permitted in artifact: {relative}")
        if prohibited(relative):
            continue
        clean.append((source, relative))
    destinations = [relative.as_posix() for _, relative in clean]
    if len(destinations) != len(set(destinations)):
        raise RuntimeError("duplicate artifact destination")
    return sorted(clean, key=lambda item: item[1].as_posix())


def normalized(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = SOURCE_DATE_EPOCH
    info.pax_headers = {}
    info.mode = 0o755 if info.isdir() or info.name.endswith(".py") else 0o644
    return info


def build_artifact(release_version: str) -> Path:
    target = ARTIFACT_DIR / f"proofpathbench-artifact-v{release_version}.tar.gz"
    temporary = target.with_suffix(target.suffix + ".tmp")
    top = PurePosixPath(f"proofpathbench-artifact-v{release_version}")
    sources = artifact_sources()
    directories = {top}
    for _, relative in sources:
        parent = top / relative.parent
        while parent != PurePosixPath(".") and parent not in directories:
            directories.add(parent)
            if parent == top:
                break
            parent = parent.parent
    with (
        temporary.open("wb") as raw,
        gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9
        ) as gz,
        tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive,
    ):
        for directory in sorted(
            directories, key=lambda item: (len(item.parts), item.as_posix())
        ):
            info = tarfile.TarInfo(directory.as_posix())
            info.type = tarfile.DIRTYPE
            archive.addfile(normalized(info))
        for source, relative in sources:
            info = archive.gettarinfo(str(source), arcname=(top / relative).as_posix())
            info = normalized(info)
            with source.open("rb") as stream:
                archive.addfile(info, stream)
    temporary.replace(target)
    return target


def write_manifest(release_version: str, artifact: Path, zenodo_doi: str | None) -> None:
    runtime = json.loads((ROOT / "benchmark/runtime_validation_report.json").read_text())
    static = json.loads((ROOT / "benchmark/validation_report.json").read_text())
    failure_names = sorted(runtime["forced_failure_results"])
    test_meta = (ROOT / "docs/release-meta.js").read_text(encoding="utf-8")
    python_tests = int(re.search(r"benchmarkValidationTests:\s*(\d+)", test_meta).group(1))
    website_tests = int(re.search(r"interactiveTests:\s*(\d+)", test_meta).group(1))
    manifest = {
        "release_version": release_version,
        "zenodo_doi": zenodo_doi,
        "build_timestamp_utc": dt.datetime.fromtimestamp(
            SOURCE_DATE_EPOCH, tz=dt.UTC
        ).isoformat().replace("+00:00", "Z"),
        "paper_sha256": sha256(RELEASE / "PAPER.pdf"),
        "artifact_sha256": sha256(artifact),
        "scenario_count": runtime["scenario_count"],
        "domain_count": len(static["domain_counts"]),
        "domain_counts": static["domain_counts"],
        "task_treatment_unit_count": runtime["split_plot_unit_count"],
        "no_fault_execution_count": runtime["no_fault_plan_executions"],
        "failure_class_count": len(failure_names),
        "failure_classes": failure_names,
        "test_counts": {"python": python_tests, "website": website_tests},
        "expected_major_files": [
            "README.md", "PAPER.pdf", "CITATION.cff", "metadata.json",
            "RELEASE_NOTES.md", "LICENSE", "CHECKSUMS.sha256",
            artifact.relative_to(RELEASE).as_posix(),
            "validation/RELEASE_VALIDATION.md", "validation/manifest.json",
            "ZENODO_UPLOAD_GUIDE.md", "FINAL_ZENODO_READINESS.md",
        ],
        "release_scope": (
            "Research preprint plus deterministic benchmark artifact and prospective "
            "evaluation design; no provider-model behavioral results and no completed "
            "human-validation results."
        ),
        "human_validation": "blinded protocol included; not yet run",
        "empirical_model_results_included": False,
    }
    (VALIDATION_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def write_checksums(artifact: Path) -> None:
    paths = [
        RELEASE / "README.md", RELEASE / "PAPER.pdf", RELEASE / "CITATION.cff",
        RELEASE / "metadata.json", RELEASE / "RELEASE_NOTES.md", RELEASE / "LICENSE",
        RELEASE / "ZENODO_UPLOAD_GUIDE.md", ARTIFACT_DIR / "README.md", artifact,
        VALIDATION_DIR / "manifest.json",
    ]
    lines = [f"{sha256(path)}  {path.relative_to(RELEASE).as_posix()}" for path in paths]
    (RELEASE / "CHECKSUMS.sha256").write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def main() -> None:
    assert_release_boundary()
    before = arxiv_snapshot()
    if not before:
        raise RuntimeError("no arXiv-related files found to protect")
    release_version = version()
    zenodo_doi = configured_zenodo_doi()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    expected_artifact = ARTIFACT_DIR / f"proofpathbench-artifact-v{release_version}.tar.gz"
    for target in (
        RELEASE / "PAPER.pdf", RELEASE / "CITATION.cff", RELEASE / "metadata.json",
        RELEASE / "LICENSE", RELEASE / "CHECKSUMS.sha256", expected_artifact,
        VALIDATION_DIR / "manifest.json", VALIDATION_DIR / "RELEASE_VALIDATION.md",
        RELEASE / "FINAL_ZENODO_READINESS.md",
    ):
        if target.exists():
            if target.is_dir():
                raise RuntimeError(f"expected generated file, found directory: {target}")
            target.unlink()
    shutil.copyfile(PAPER_SOURCE, RELEASE / "PAPER.pdf")
    shutil.copyfile(ROOT / "LICENSE", RELEASE / "LICENSE")
    write_citation(release_version, zenodo_doi)
    write_metadata(release_version, zenodo_doi)
    artifact = build_artifact(release_version)
    write_manifest(release_version, artifact, zenodo_doi)
    write_checksums(artifact)
    subprocess.run(
        [sys.executable, str(RELEASE / "scripts" / "validate_zenodo_release.py")],
        cwd=ROOT,
        check=True,
    )
    after = arxiv_snapshot()
    if before != after:
        changed = sorted(set(before) ^ set(after) | {key for key in before.keys() & after.keys() if before[key] != after[key]})
        raise RuntimeError(f"arXiv preservation failure: {changed}")
    print(f"Zenodo release built: zenodo/ (v{release_version})")
    print("ARXIV TREE MODIFIED: NO")


if __name__ == "__main__":
    main()
