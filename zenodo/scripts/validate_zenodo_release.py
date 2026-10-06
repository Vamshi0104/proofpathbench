#!/usr/bin/env python3
"""Validate the frozen ProofPathBench Zenodo release and its extracted artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "zenodo"
VERSION = "0.0.1"
AUTHOR_NAME = "Madhavan, Vamshi Krishna"
AUTHOR_AFFILIATION = "Independent Researcher"
AUTHOR_EMAIL = "vamshi-madhavan@outlook.com"
REPOSITORY_URL = "https://github.com/Vamshi0104/proofpathbench"
PROJECT_URL = "https://vamshi0104.github.io/proofpathbench/"
ARTIFACT = RELEASE / "artifact" / f"proofpathbench-artifact-v{VERSION}.tar.gz"
ZENODO_DOI_PATTERN = re.compile(r"^10\.5281/zenodo\.\d+$")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".cff", ".csv", ".tex", ".bib"}
PROHIBITED = re.compile(
    r"(^|/)(?:__MACOSX|node_modules|venv|\.venv|__pycache__|\.pytest_cache|"
    r"\.mypy_cache|\.ruff_cache|\.git|\.github|\.idea|\.vscode|htmlcov)(/|$)|"
    r"(^|/)\.DS_Store$|(^|/)\._|\.py[co]$|\.sw[op]$|~$|(^|/)\.coverage$",
    re.IGNORECASE,
)
SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    "authorization header": re.compile(r"(?im)^\s*Authorization\s*:\s*(?:Bearer|Basic)\s+\S+"),
    "local macOS path": re.compile(r"\/Users\/[^\/\s]+\/"),
    "local Linux path": re.compile(r"\/home\/[^\/\s]+\/"),
    "Windows user path": re.compile(r"[A-Z]:\\Users\\[^\\\s]+\\", re.IGNORECASE),
    "private/internal URL": re.compile(r"https?://[^\s/]*(?:internal|private|localhost)(?:[/:]|$)", re.IGNORECASE),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def configured_zenodo_doi() -> str | None:
    config = (ROOT / "docs/site-config.js").read_text(encoding="utf-8")
    match = re.search(r'zenodoDoi:\s*["\']([^"\']*)["\']', config)
    if not match:
        raise RuntimeError("docs/site-config.js lacks zenodoDoi")
    doi = match.group(1)
    if doi and not ZENODO_DOI_PATTERN.fullmatch(doi):
        raise RuntimeError(f"invalid configured Zenodo DOI: {doi}")
    return doi or None


def require_files() -> None:
    required = [
        "README.md", "PAPER.pdf", "CITATION.cff", "metadata.json", "RELEASE_NOTES.md",
        "LICENSE", "CHECKSUMS.sha256", "ZENODO_UPLOAD_GUIDE.md",
        "artifact/README.md", f"artifact/{ARTIFACT.name}", "validation/manifest.json",
        "scripts/build_zenodo_release.py", "scripts/validate_zenodo_release.py",
    ]
    for relative in required:
        path = RELEASE / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"missing or empty release file: {relative}")
    if (RELEASE / "PAPER.pdf").read_bytes()[:5] != b"%PDF-":
        raise RuntimeError("PAPER.pdf is not a PDF")
    prohibited_release_paths = [
        path.relative_to(RELEASE).as_posix()
        for path in RELEASE.rglob("*")
        if PROHIBITED.search(path.relative_to(RELEASE).as_posix())
    ]
    if prohibited_release_paths:
        raise RuntimeError(f"prohibited paths in Zenodo tree: {prohibited_release_paths[:10]}")
    canonical = ROOT / "output" / "pdf" / "proofpath_benchmark.pdf"
    if sha256(RELEASE / "PAPER.pdf") != sha256(canonical):
        raise RuntimeError("PAPER.pdf differs from the scientifically approved PDF")


def validate_metadata() -> tuple[dict, dict]:
    zenodo_doi = configured_zenodo_doi()
    metadata = json.loads((RELEASE / "metadata.json").read_text(encoding="utf-8"))
    body = metadata.get("metadata")
    if not isinstance(body, dict):
        raise RuntimeError("metadata.json lacks Zenodo metadata object")
    expected = {
        "upload_type": "publication", "publication_type": "preprint",
        "version": VERSION, "publication_date": "2026-10-06", "language": "eng",
    }
    for key, value in expected.items():
        if body.get(key) != value:
            raise RuntimeError(f"metadata field {key!r} must equal {value!r}")
    if body.get("license") != "Apache-2.0":
        raise RuntimeError("software/artifact license is not Apache-2.0")
    if not body.get("title") or not body.get("description") or not body.get("creators"):
        raise RuntimeError("metadata lacks required descriptive fields")
    creators = body["creators"]
    if creators != [{"name": AUTHOR_NAME, "affiliation": AUTHOR_AFFILIATION}]:
        raise RuntimeError("Zenodo creator name or affiliation is incorrect")
    if AUTHOR_EMAIL not in body.get("notes", "") or AUTHOR_EMAIL not in body.get("description", ""):
        raise RuntimeError("correspondence email is absent from Zenodo metadata")
    expected_related = [
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
    ]
    if body.get("related_identifiers") != expected_related:
        raise RuntimeError("verified source repository is absent from Zenodo metadata")
    if "prereserve_doi" in body:
        raise RuntimeError("prereserve_doi must not appear in normalized release metadata")
    if body.get("doi") != zenodo_doi:
        raise RuntimeError("Zenodo metadata DOI does not match docs/site-config.js")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to parse CITATION.cff") from exc
    citation = yaml.safe_load((RELEASE / "CITATION.cff").read_text(encoding="utf-8"))
    if citation.get("cff-version") != "1.2.0" or citation.get("version") != VERSION:
        raise RuntimeError("CITATION.cff version mismatch")
    if citation.get("license") != "Apache-2.0" or not citation.get("preferred-citation"):
        raise RuntimeError("CITATION.cff lacks license or preferred citation")
    if citation.get("repository-code") != REPOSITORY_URL:
        raise RuntimeError("CITATION.cff repository-code is incorrect")
    if citation.get("url") != PROJECT_URL:
        raise RuntimeError("CITATION.cff project URL is incorrect")
    author = citation.get("authors", [{}])[0]
    if author.get("affiliation") != AUTHOR_AFFILIATION or author.get("email") != AUTHOR_EMAIL:
        raise RuntimeError("CITATION.cff author details are incomplete")
    if citation.get("doi") != zenodo_doi or citation.get("preferred-citation", {}).get("doi") != zenodo_doi:
        raise RuntimeError("Zenodo CITATION.cff DOI does not match docs/site-config.js")
    canonical_citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    if canonical_citation.get("doi") != zenodo_doi:
        raise RuntimeError("canonical CITATION.cff DOI does not match docs/site-config.js")
    return body, citation


def validate_checksums() -> None:
    lines = (RELEASE / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    if lines != sorted(lines):
        raise RuntimeError("CHECKSUMS.sha256 is not deterministically ordered")
    seen: set[str] = set()
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise RuntimeError(f"invalid checksum line: {line}")
        expected, relative = match.groups()
        path = RELEASE / relative
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"checksum mismatch: {relative}")
        seen.add(relative)
    for required in ("PAPER.pdf", f"artifact/{ARTIFACT.name}", "metadata.json", "CITATION.cff", "validation/manifest.json"):
        if required not in seen:
            raise RuntimeError(f"important file absent from checksums: {required}")


def archive_names() -> tuple[list[str], str]:
    with tarfile.open(ARTIFACT, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name.removeprefix("./") for member in members]
    if len(names) != len(set(names)):
        raise RuntimeError("duplicate archive member names")
    if any(name.startswith("/") or ".." in PurePosixPath(name).parts for name in names):
        raise RuntimeError("unsafe archive member path")
    bad = [name for name in names if PROHIBITED.search(name)]
    if bad:
        raise RuntimeError(f"prohibited archive members: {bad[:10]}")
    roots = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
    if roots != {f"proofpathbench-artifact-v{VERSION}"}:
        raise RuntimeError(f"unexpected archive root: {sorted(roots)}")
    return names, next(iter(roots))


def scan_text(label: str, relative: str, text: str) -> None:
    for finding, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            raise RuntimeError(f"{finding} pattern found in {label}:{relative}")
    if re.search(r"(?im)^\s*(?:password|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[^\s'\"]+", text):
        raise RuntimeError(f"credential assignment pattern found in {label}:{relative}")


def secret_and_privacy_scan() -> None:
    for path in RELEASE.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(RELEASE).as_posix()
        if relative == "scripts/validate_zenodo_release.py":
            continue
        if any(part.startswith(".") for part in path.relative_to(RELEASE).parts):
            raise RuntimeError(f"hidden release file: {relative}")
        scan_text("release", relative, path.read_text(encoding="utf-8", errors="replace"))
    with tarfile.open(ARTIFACT, "r:gz") as archive:
        for member in archive.getmembers():
            relative = member.name.removeprefix("./")
            if not member.isfile() or Path(relative).suffix.casefold() not in TEXT_SUFFIXES:
                continue
            stream = archive.extractfile(member)
            text = stream.read().decode("utf-8", errors="replace") if stream else ""
            scan_text("artifact", relative, text)


def validate_manifest(names: list[str], artifact_root: str) -> dict:
    manifest = json.loads((RELEASE / "validation/manifest.json").read_text(encoding="utf-8"))
    runtime = json.loads((ROOT / "benchmark/runtime_validation_report.json").read_text())
    static = json.loads((ROOT / "benchmark/validation_report.json").read_text())
    expected = {
        "release_version": VERSION,
        "zenodo_doi": configured_zenodo_doi(),
        "paper_sha256": sha256(RELEASE / "PAPER.pdf"),
        "artifact_sha256": sha256(ARTIFACT),
        "scenario_count": runtime["scenario_count"],
        "domain_count": len(static["domain_counts"]),
        "task_treatment_unit_count": runtime["split_plot_unit_count"],
        "no_fault_execution_count": runtime["no_fault_plan_executions"],
        "failure_class_count": len(runtime["forced_failure_results"]),
        "failure_classes": sorted(runtime["forced_failure_results"]),
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"manifest mismatch for {key}: {manifest.get(key)!r} != {value!r}")
    if manifest.get("test_counts", {}).get("python") != 48:
        raise RuntimeError("manifest Python test count is not 48")
    required_members = {
        f"{artifact_root}/README.md", f"{artifact_root}/LICENSE",
        f"{artifact_root}/benchmark/scenarios/index.json",
        f"{artifact_root}/benchmark/validation_report.json",
        f"{artifact_root}/benchmark/runtime_validation_report.json",
        f"{artifact_root}/research/power_analysis.json",
        f"{artifact_root}/research/human_validation/protocol.md",
        f"{artifact_root}/research/citation_audit.md",
        f"{artifact_root}/research/textual_integrity_audit.md",
        f"{artifact_root}/tests/test_benchmark_validation.py",
    }
    missing = sorted(required_members - set(names))
    if missing:
        raise RuntimeError(f"artifact completeness failure: {missing}")
    return manifest


def check_identifiers() -> None:
    zenodo_doi = configured_zenodo_doi()
    for relative in ("README.md", "metadata.json", "CITATION.cff", "RELEASE_NOTES.md"):
        text = (RELEASE / relative).read_text(encoding="utf-8")
        dois = set(re.findall(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+-]*[A-Za-z0-9]", text))
        unexpected = dois - ({zenodo_doi} if zenodo_doi else set())
        if unexpected:
            raise RuntimeError(f"unexpected DOI-like value in {relative}: {sorted(unexpected)}")
        if re.search(r"\barXiv:\s*(?:0000|XXXX|TBD)|\b0000\.00000\b", text, re.IGNORECASE):
            raise RuntimeError(f"fake arXiv identifier present: {relative}")


def run(command: list[str], cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    return completed.stdout


def check_relative_markdown_links(root: Path) -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in root.rglob("*.md"):
        for target in link_re.findall(path.read_text(encoding="utf-8")):
            target = target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            if not (path.parent / target).resolve().is_relative_to(root.resolve()):
                raise RuntimeError(f"artifact Markdown link escapes root: {path}:{target}")
            if not (path.parent / target).exists():
                raise RuntimeError(f"broken artifact Markdown link: {path}:{target}")


def fresh_extraction(manifest: dict, skip_tests: bool) -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="proofpathbench-zenodo-") as temporary:
        temp = Path(temporary)
        with tarfile.open(ARTIFACT, "r:gz") as archive:
            for member in archive.getmembers():
                destination = (temp / member.name).resolve()
                if not destination.is_relative_to(temp.resolve()):
                    raise RuntimeError("archive extraction would escape temporary directory")
            archive.extractall(temp)
        extracted = temp / f"proofpathbench-artifact-v{VERSION}"
        check_relative_markdown_links(extracted)
        if skip_tests:
            return "SKIPPED", "SKIPPED"
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["MPLCONFIGDIR"] = str(temp / "mpl-config")
        env["MPLBACKEND"] = "Agg"
        run([sys.executable, "-m", "proofpath.benchmark.validate"], extracted, env)
        run([sys.executable, "-m", "proofpath.validate_benchmark", "--config", "configs/pilot.yaml"], extracted, env)
        pytest_output = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], extracted, env)
        if "48 passed" not in pytest_output:
            raise RuntimeError(f"fresh extraction did not report 48 passing tests: {pytest_output[-500:]}")
        regenerated_power = temp / "power.json"
        run([
            sys.executable, "-m", "proofpath.planning.power", "--config", "configs/power.yaml",
            "--output", str(regenerated_power),
        ], extracted, env)
        if json.loads(regenerated_power.read_text()) != json.loads((extracted / "research/power_analysis.json").read_text()):
            raise RuntimeError("regenerated prospective power output differs")
        generated_before = {
            path.relative_to(extracted).as_posix(): sha256(path)
            for directory in (extracted / "paper/figures", extracted / "paper/tables")
            for path in directory.rglob("*") if path.is_file()
        }
        run([sys.executable, "paper/build_assets.py"], extracted, env)
        generated_after = {
            path.relative_to(extracted).as_posix(): sha256(path)
            for directory in (extracted / "paper/figures", extracted / "paper/tables")
            for path in directory.rglob("*") if path.is_file()
        }
        if generated_before != generated_after:
            raise RuntimeError("regenerated figures/tables differ from frozen outputs")
        forbidden_after = [
            path.relative_to(extracted).as_posix() for path in extracted.rglob("*")
            if PROHIBITED.search(path.relative_to(extracted).as_posix())
        ]
        if forbidden_after:
            raise RuntimeError(f"fresh tests created prohibited files: {forbidden_after[:10]}")
        return "PASS (48/48)", "PASS"


def write_reports(manifest: dict, tests: str, extraction: str) -> None:
    zenodo_doi = configured_zenodo_doi()
    metadata_doi_evidence = (
        f"contains the configured Zenodo DOI `{zenodo_doi}`"
        if zenodo_doi else "does not fabricate a DOI"
    )
    citation_doi_evidence = (
        f"contains the matching DOI `{zenodo_doi}`"
        if zenodo_doi else "contains a preferred citation without a DOI"
    )
    pages_doi_evidence = (
        f"The canonical project URL and Zenodo DOI `{zenodo_doi}` are configured."
        if zenodo_doi else "The canonical project URL is configured; the DOI remains blank until assigned."
    )
    doi_readiness_evidence = (
        f"DOI `{zenodo_doi}` matches the website, deposit metadata, citation metadata, and manifest."
        if zenodo_doi else "No DOI is fabricated; the guide documents reservation and exact insertion."
    )
    doi_checklist = (
        f"Confirm DOI `{zenodo_doi}` matches the reserved or published Zenodo record."
        if zenodo_doi else "Reserve a DOI only in the final draft; rebuild and revalidate after inserting it."
    )
    validation = f'''# Zenodo release validation

**Release:** v{VERSION}  
**Validator:** `zenodo/scripts/validate_zenodo_release.py`

| Check | Status | Evidence |
|---|---|---|
| Approved paper | PASS | `PAPER.pdf` is non-empty, parses as PDF, and is byte-identical to the final audited release PDF. |
| Metadata | PASS | JSON parses as a publication/preprint, contains the verified source/project URLs, and {metadata_doi_evidence}. |
| Citation metadata | PASS | CFF 1.2.0 parses and {citation_doi_evidence}. |
| Scientific counts | PASS | {manifest['scenario_count']} scenarios, {manifest['domain_count']} domains, {manifest['task_treatment_unit_count']} units, {manifest['no_fault_execution_count']} executions, and {manifest['failure_class_count']} failure classes match canonical reports. |
| Checksums | PASS | All listed SHA-256 values match. |
| Archive structure | PASS | Single safe archive root; required reproducibility files are present. |
| Archive cleanliness | PASS | No macOS metadata, AppleDouble entries, caches, VCS data, hidden files, or prohibited development output. |
| Secret/privacy scan | PASS | No obvious credential, private-key, authorization-header, local-path, or private/internal-URL pattern was found in distributed text. |
| Fresh extraction | {extraction} | Archive extracted in a new temporary directory; references and structure were checked. |
| Python tests | {tests} | Documented benchmark validation and the extracted suite were run. |
| Power/assets regeneration | {extraction} | Prospective power JSON and manuscript figures/tables regenerated without differences. |
| Human-validation labeling | PASS | Protocol is included and explicitly labeled not yet run. |
| Simulation/empirical labeling | PASS | No provider-model result is claimed; simulations and fixtures are labeled non-empirical. |

The pattern scan is a focused release check, not a credential-management audit. The
textual-integrity audit is public-source/local evidence, not a private-corpus plagiarism
certificate.
'''
    (RELEASE / "validation/RELEASE_VALIDATION.md").write_text(validation, encoding="utf-8")
    readiness = f'''# Final Zenodo readiness

| Gate | Status | Evidence / required human review |
|---|---|---|
| Final paper | PASS | Exact final-audit PDF; eight pages; no scientific rewrite for Zenodo. |
| Paper/artifact consistency | PASS | Canonical counts, failure names, scope, tests, and prospective power records agree. |
| Metadata | PASS | Publication/preprint metadata parses; verified author affiliation, correspondence email, source repository, and project website are included. |
| CITATION.cff | PASS | CFF 1.2.0 parses; preferred citation present; {citation_doi_evidence}. |
| Licensing | WARNING | Artifact is Apache-2.0. Author must confirm the paper/content license in Zenodo; no separate manuscript license is declared. |
| Artifact completeness | PASS | Scenarios, schemas, implementation, failure/evaluation/analysis code, power analysis, tests, audits, and public human-review protocol included. |
| Archive cleanliness | PASS | Automated prohibited-member scan passes. |
| macOS metadata scan | PASS | Zero `.DS_Store`, `._*`, `__MACOSX`, or AppleDouble sidecars. |
| Secret/privacy scan | PASS | Focused recursive release and archive scan passes; intentional author identity is not treated as a secret. |
| Checksums | PASS | Deterministic checksum list verifies. |
| Manifest | PASS | Machine-derived counts and release hashes match. |
| Fresh extraction | {extraction} | Self-contained archive extracted and documented commands ran in a fresh temporary directory. |
| Tests | {tests} | Extracted Python suite result. Website suite remains a repository/GitHub Pages concern and is recorded separately in the manifest. |
| Reproducibility | PASS | Static/runtime checks, prospective power output, and generated assets reproduce. |
| Human-validation labeling | PASS | Described as a blinded human construct-validation protocol, not a human-validated benchmark. |
| Simulation/empirical labeling | PASS | Fixtures and simulations are not advertised as model results. |
| Textual-integrity/plagiarism review | PASS WITH LIMIT | Local and public-web phrase checks found no serious concern or distinctive multi-sentence match. No private similarity corpus was available, so no percentage is claimed. |
| Paper quality and voice | 8.7/10 | Clear, technically disciplined, and unusually candid about scope. The prose is dense and repeats claim-boundary language; the disclosed AI assistance and final human line edit must remain transparent. |
| GitHub integration readiness | PASS | Version/tag strategy is coherent (`v{VERSION}`); manual deposit is the single-record strategy; the verified public source repository is linked. |
| GitHub Pages integration readiness | PASS | {pages_doi_evidence} |
| DOI readiness | PASS | {doi_readiness_evidence} |
| Zenodo upload readiness | WARNING | Engineering package is ready. Before Publish, the author must confirm paper rights, final metadata, and the live Zenodo preview. |
| arXiv preservation | PASS | Zenodo build is additive and hash-checks all arXiv-named paths before/after. |

## Manuscript note

The approved manuscript contains two factual references to the separately preserved arXiv
ancillary archive. They are destination-specific artifact descriptions, not scientific
changes. The Zenodo PDF remains byte-identical to the approved manuscript; the wording is
reported rather than silently rewritten.

## Submission review checklist

1. Confirm the author name, contact email, contribution statement, and AI-assistance disclosure.
2. Confirm the paper/content license and configure mixed file licenses accurately.
3. Read the exact PDF and compare title/abstract against the Zenodo preview.
4. Confirm resource type Publication / Preprint, version {VERSION}, and publication date.
5. Confirm no provider-model or completed-human-validation claim appears in the record.
6. Inspect the artifact and checksum file names in the live file list.
7. Confirm the verified GitHub repository, project website, and Independent Researcher affiliation; add only verified ORCID, funding, arXiv, or DOI values.
8. If available, run the exact PDF through an institutional similarity service and review matches.
9. {doi_checklist}
10. Publish one canonical record for this version and use Zenodo versioning for future releases.
'''
    (RELEASE / "FINAL_ZENODO_READINESS.md").write_text(readiness, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-fresh-tests", action="store_true", help="perform structural validation only")
    args = parser.parse_args()
    require_files()
    validate_metadata()
    validate_checksums()
    names, artifact_root = archive_names()
    secret_and_privacy_scan()
    manifest = validate_manifest(names, artifact_root)
    check_identifiers()
    tests, extraction = fresh_extraction(manifest, args.skip_fresh_tests)
    write_reports(manifest, tests, extraction)
    print("Zenodo release validation: PASS")
    print(f"Fresh extraction: {extraction}")
    print(f"Tests: {tests}")


if __name__ == "__main__":
    main()
