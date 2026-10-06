#!/usr/bin/env python3
"""Build the public research artifact as a deterministic gzip-compressed tar."""

from __future__ import annotations

import gzip
import os
import tarfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "proofpath_artifact.tar.gz"
SOURCE_DATE_EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "1791244800"))
TOP_FILES = (
    "LICENSE", "README.md", "CITATION.cff", "Makefile", "pyproject.toml", "requirements.txt",
)
TOP_DIRS = (
    "benchmark", "configs", "experiments", "paper", "proofpath", "research", "results", "scripts", "tests",
)
PRIVATE_PATHS = {
    PurePosixPath("benchmark/review_key.json"),
    PurePosixPath("research/human_validation/blinding_manifest.json"),
}
GENERATED_SUFFIXES = {
    ".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".pdf", ".pyc", ".pyo",
}
GENERATED_PARTS = {
    "__pycache__", "__MACOSX", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
}


def prohibited(relative: PurePosixPath) -> bool:
    if relative in PRIVATE_PATHS or any(part in GENERATED_PARTS for part in relative.parts):
        return True
    if relative.name == ".DS_Store" or relative.name.startswith("._"):
        return True
    if relative.name.endswith("~") or relative.suffix in GENERATED_SUFFIXES:
        return True
    if relative.name == ".env" or relative.name.startswith(".env."):
        return True
    if relative.parts[:2] == ("results", "raw"):
        return True
    if relative.parts[:2] == ("paper", "arxiv"):
        return True
    return False


def members() -> list[tuple[Path, PurePosixPath]]:
    selected: list[tuple[Path, PurePosixPath]] = []
    for name in TOP_FILES:
        selected.append((ROOT / name, PurePosixPath(name)))
    for name in TOP_DIRS:
        base = ROOT / name
        selected.append((base, PurePosixPath(name)))
        for path in sorted(base.rglob("*"), key=lambda item: item.as_posix()):
            relative = PurePosixPath(path.relative_to(ROOT).as_posix())
            if prohibited(relative):
                continue
            if path.is_symlink():
                raise RuntimeError(f"symlink is not permitted in the public artifact: {relative}")
            selected.append((path, relative))
    return selected


def normalized(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = SOURCE_DATE_EPOCH
    info.pax_headers = {}
    if info.isdir():
        info.mode = 0o755
    elif info.isfile():
        info.mode = 0o755 if info.name.endswith((".sh", ".py")) else 0o644
    return info


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(OUTPUT.suffix + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for source, relative in members():
                    info = normalized(archive.gettarinfo(str(source), arcname=relative.as_posix()))
                    if info.isfile():
                        with source.open("rb") as stream:
                            archive.addfile(info, stream)
                    else:
                        archive.addfile(info)
    temporary.replace(OUTPUT)
    print(f"Artifact: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
