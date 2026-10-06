#!/usr/bin/env python3
"""Check the self-contained GitHub Pages site and cross-artifact release claims."""

from __future__ import annotations

import json
import re
import struct
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TEXT_SUFFIXES = {".bib", ".cff", ".cjs", ".csv", ".html", ".js", ".json", ".md", ".py", ".sh", ".tex", ".toml", ".txt", ".yaml", ".yml"}
SECRET_PATTERNS = (
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(rb"-----BEGIN (?:RSA|OPENSSH|EC|DSA)? ?PRIVATE KEY-----"),
    re.compile(rb"Authorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{12,}", re.I),
)
PRIVATE_PATH = re.compile(rb"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Z]:\\Users\\[^\\\s]+)")


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.elements.append((tag, values))
        if identifier := values.get("id"):
            self.ids.add(identifier)
        for attribute in ("href", "src"):
            if value := values.get(attribute):
                self.refs.append((attribute, value))


def parse_pages() -> dict[Path, Page]:
    pages: dict[Path, Page] = {}
    for path in DOCS.rglob("*.html"):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        pages[path.resolve()] = page
    return pages


def check_links(pages: dict[Path, Page]) -> None:
    errors: list[str] = []
    for source, page in pages.items():
        for attribute, raw in page.refs:
            parsed = urlsplit(raw)
            if parsed.scheme in {"http", "https", "mailto", "tel", "data"} or raw.startswith("//"):
                continue
            target = source if not parsed.path else (source.parent / unquote(parsed.path)).resolve()
            try:
                target.relative_to(DOCS.resolve())
            except ValueError:
                errors.append(f"{source.name}: path escapes docs: {raw}")
                continue
            if not target.is_file():
                errors.append(f"{source.name}: missing {attribute} target: {raw}")
                continue
            if parsed.fragment:
                target_page = pages.get(target)
                if target_page is None or unquote(parsed.fragment) not in target_page.ids:
                    errors.append(f"{source.name}: missing anchor target: {raw}")
    css = (DOCS / "styles.css").read_text(encoding="utf-8")
    for raw in re.findall(r"url\((?:['\"]?)([^)'\"]+)", css):
        if not raw.startswith(("data:", "http://", "https://", "#")) and not (DOCS / raw).is_file():
            errors.append(f"styles.css: missing url() target: {raw}")
    if errors:
        raise SystemExit("broken site references:\n" + "\n".join(errors))


def js_number(source: str, name: str) -> int:
    match = re.search(rf"\b{re.escape(name)}:\s*(\d+)", source)
    if not match:
        raise SystemExit(f"missing site data field: {name}")
    return int(match.group(1))


def check_claims() -> None:
    runtime = json.loads((ROOT / "benchmark/runtime_validation_report.json").read_text(encoding="utf-8"))
    static = json.loads((ROOT / "benchmark/validation_report.json").read_text(encoding="utf-8"))
    data = (DOCS / "data.js").read_text(encoding="utf-8")
    expected = {
        "scenarioCount": static["scenario_count"],
        "domainCount": len(static["domain_counts"]),
        "treatmentUnitCount": runtime["split_plot_unit_count"],
        "noFaultExecutionCount": runtime["no_fault_plan_executions"],
        "failureClassCount": len(runtime["forced_failure_results"]),
    }
    if mismatches := {key: (value, js_number(data, key)) for key, value in expected.items() if js_number(data, key) != value}:
        raise SystemExit(f"website scientific-count mismatch: {mismatches}")

    engine = (DOCS / "engine.js").read_text(encoding="utf-8")
    block = re.search(r"const FAILURE_TYPES = \[(.*?)\];", engine, re.S)
    failures = set(re.findall(r'"([a-z_]+)"', block.group(1) if block else ""))
    if failures != set(runtime["forced_failure_results"]):
        raise SystemExit("browser failure classes disagree with runtime validation")

    public_copy = (DOCS / "index.html").read_text(encoding="utf-8") + (DOCS / "app.js").read_text(encoding="utf-8")
    required = (
        "deterministic sandbox", "Simulated failure risk", "Paired simulation",
        "Simulated output, not empirical results", "No provider-model runs in this release",
        "96 scenarios", "384 task-treatment units", "9 failure classes",
    )
    if missing := [item for item in required if item not in public_copy]:
        raise SystemExit(f"required scope statement missing from site: {missing}")
    if re.search(r"Paired risk model|Live-model failure risk|arXiv:\s*(?:X+|0+\.0+)", public_copy, re.I):
        raise SystemExit("ambiguous simulation language or placeholder arXiv ID remains")


def check_metadata(pages: dict[Path, Page]) -> None:
    index = pages[(DOCS / "index.html").resolve()]
    names = {(attrs.get("name"), attrs.get("property")) for tag, attrs in index.elements if tag == "meta"}
    required = {
        ("description", None), ("viewport", None), ("theme-color", None),
        (None, "og:title"), (None, "og:description"), (None, "og:image"),
        ("twitter:card", None),
    }
    if missing := required - names:
        raise SystemExit(f"missing HTML metadata: {sorted(missing, key=str)}")
    png = (DOCS / "og-image.png").read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", png[16:24]) != (1200, 630):
        raise SystemExit("Open Graph image must be a 1200 x 630 PNG")
    config = (DOCS / "site-config.js").read_text(encoding="utf-8")
    if re.search(r"github\.com/(?:owner|username|your)|arxivId:\s*['\"](?:X+|0+)", config, re.I):
        raise SystemExit("publication configuration contains a fabricated placeholder")


def intended_public_files() -> list[Path]:
    output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return [ROOT / item.decode() for item in output.split(b"\0") if item]


def check_privacy() -> None:
    exempt = {"scripts/build_artifact.py", "scripts/check_public_release.py", "scripts/check_website_release.py"}
    for path in intended_public_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in exempt:
            continue
        content = path.read_bytes()
        if any(pattern.search(content) for pattern in SECRET_PATTERNS):
            raise SystemExit(f"credential-like content in intended public file: {relative}")
        if PRIVATE_PATH.search(content):
            raise SystemExit(f"private absolute path in intended public file: {relative}")
    for name in ("index.html", "app.js", "data.js", "engine.js", "site-config.js", "release-meta.js", "styles.css"):
        if re.search(r"localhost|127\.0\.0\.1|file://|/Users/", (DOCS / name).read_text(encoding="utf-8"), re.I):
            raise SystemExit(f"development-only reference in published runtime asset: {name}")


def main() -> None:
    pages = parse_pages()
    check_links(pages)
    check_claims()
    check_metadata(pages)
    check_privacy()
    print("Website release check: PASS")


if __name__ == "__main__":
    main()
