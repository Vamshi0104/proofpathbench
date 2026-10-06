#!/usr/bin/env bash
set -euo pipefail

mode="${1:-draft}"
if [[ "$mode" != "draft" && "$mode" != "release" ]]; then
  echo "Usage: $0 [draft|release]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
cd "$repo_root"

for command_name in python3 latexmk tar pdftoppm pdfinfo pdftotext pdffonts grep awk diff find; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command is unavailable: $command_name" >&2
    exit 1
  fi
done

if command -v rg >/dev/null 2>&1; then
  search=(rg)
else
  search=(grep -E)
fi

if [[ "$mode" == "release" ]]; then
  if "${search[@]}" -qi \
    'Author identity to be supplied|Firstname Lastname|Your Name|\\author\{[[:space:]]*\}|\\author\{(anonymous|tbd|todo)\}' \
    paper/main.tex; then
    echo "Release blocked: replace the author placeholder in paper/main.tex." >&2
    exit 1
  fi
fi

mkdir -p output/pdf paper/arxiv/figures paper/arxiv/tables paper/arxiv/anc

MPLBACKEND=Agg \
MPLCONFIGDIR=/tmp/proofpath-mpl \
XDG_CACHE_HOME=/tmp/proofpath-cache \
  python3 paper/build_assets.py

# paper/main.tex and paper/references.bib are canonical.  The arXiv tree is a
# generated, upload-only mirror so author edits cannot silently diverge.
cp paper/main.tex paper/arxiv/main.tex
cp paper/references.bib paper/arxiv/references.bib
cp paper/figures/proofpath_architecture.pdf paper/arxiv/figures/
cp paper/figures/prospective_power.pdf paper/arxiv/figures/
cp paper/tables/benchmark_composition.tex paper/arxiv/tables/
cp paper/tables/design_factors.tex paper/arxiv/tables/
cp paper/tables/mechanism_composition.tex paper/arxiv/tables/
cp paper/tables/power_summary.tex paper/arxiv/tables/
cp paper/tables/validation_summary.tex paper/arxiv/tables/

(
  cd paper
  # Start from a clean dependency state so a changed bibliography cannot leave
  # latexmk with a stale warning-bearing log from an earlier partial build.
  latexmk -C main.tex
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
)

cp paper/main.pdf output/pdf/proofpath_benchmark.pdf
cp paper/main.bbl paper/arxiv/main.bbl

if "${search[@]}" -n 'Overfull|undefined citations|undefined references|Citation .* undefined|Reference .* undefined|LaTeX Error|Fatal error' paper/main.log; then
  echo "Release-quality LaTeX check failed; inspect paper/main.log." >&2
  exit 1
fi

if [[ "$mode" == "release" ]]; then
  if [[ ! -f output/proofpath_artifact.tar.gz ]]; then
    echo "Release blocked: output/proofpath_artifact.tar.gz is missing." >&2
    exit 1
  fi

  cp output/proofpath_artifact.tar.gz paper/arxiv/anc/proofpath_artifact.tar.gz

  artifact_listing="$(tar -tzf paper/arxiv/anc/proofpath_artifact.tar.gz)"
  if "${search[@]}" -q '(^|/)__pycache__(/|$)|\.py[co]$|(^|/)\.DS_Store$|(^|/)\._|(^|/)__MACOSX(/|$)|(^|/)\.(idea|vscode)(/|$)|\.swp$|~$|(^|/)\.(pytest|mypy|ruff)_cache(/|$)|(^|/)(review_key|blinding_manifest)\.json$|(^|/)results/raw(/|$)|(^|/)\.env($|\.)' \
    <<< "$artifact_listing"; then
    echo "Release blocked: private, raw, or generated cache files were found in the ancillary archive." >&2
    exit 1
  fi

  for required_artifact_member in LICENSE README.md CITATION.cff pyproject.toml \
    benchmark/validation_report.json benchmark/runtime_validation_report.json \
    research/citation_audit.md research/related_work_matrix.md \
    research/textual_integrity_audit.md research/confound_diagnostics.json \
    research/human_validation/protocol.md research/human_validation/review_form.csv; do
    if ! "${search[@]}" -Fxq "$required_artifact_member" <<< "$artifact_listing"; then
      echo "Release blocked: ancillary member is missing: $required_artifact_member" >&2
      exit 1
    fi
  done

  archive_tmp="output/.proofpath_arxiv_source.tar.gz.tmp"
  source_stage="$(mktemp -d /tmp/proofpath-arxiv-stage.XXXXXX)"
  source_tar="$(mktemp /tmp/proofpath-arxiv-source.XXXXXX.tar)"
  source_list="$(mktemp /tmp/proofpath-arxiv-list.XXXXXX)"
  trap 'rm -rf -- "$source_stage"; rm -f -- "$source_tar" "$source_list"' EXIT
  cp paper/arxiv/main.tex paper/arxiv/main.bbl paper/arxiv/references.bib "$source_stage/"
  cp -R paper/arxiv/figures paper/arxiv/tables paper/arxiv/anc "$source_stage/"
  find "$source_stage" -exec touch -t 197001010000 {} +
  (
    cd "$source_stage"
    LC_ALL=C find . -mindepth 1 -print | sed 's#^\./##' | LC_ALL=C sort > "$source_list"
    # The sorted list already names every directory and file.  Disable tar's
    # directory recursion so members are not inserted a second time.
    COPYFILE_DISABLE=1 tar --no-recursion --format ustar --uid 0 --gid 0 --uname root --gname root \
      -cf "$source_tar" -T "$source_list"
  )
  gzip -n -c "$source_tar" > "$archive_tmp"
  mv "$archive_tmp" output/proofpath_arxiv_source.tar.gz
  rm -rf -- "$source_stage"
  rm -f -- "$source_tar" "$source_list"
  trap - EXIT

  archive_bytes="$(stat -f '%z' output/proofpath_arxiv_source.tar.gz 2>/dev/null || \
    stat -c '%s' output/proofpath_arxiv_source.tar.gz)"
  if (( archive_bytes > 50 * 1024 * 1024 )); then
    echo "Release blocked: the source archive exceeds 50 MiB." >&2
    exit 1
  fi

  archive_listing="$(tar -tzf output/proofpath_arxiv_source.tar.gz)"
  if LC_ALL=C "${search[@]}" -n '[^A-Za-z0-9_+.,=/\-]' <<< "$archive_listing"; then
    echo "Release blocked: an arXiv-incompatible filename was found." >&2
    exit 1
  fi

  for required_member in main.tex main.bbl references.bib \
    figures/proofpath_architecture.pdf figures/prospective_power.pdf \
    anc/proofpath_artifact.tar.gz; do
    if ! "${search[@]}" -Fxq "$required_member" <<< "$archive_listing"; then
      echo "Release blocked: archive member is missing: $required_member" >&2
      exit 1
    fi
  done

  if "${search[@]}" -q '(^|/)main\.(aux|blg|fdb_latexmk|fls|log|out|pdf)$' \
    <<< "$archive_listing"; then
    echo "Release blocked: a generated LaTeX build product entered the source archive." >&2
    exit 1
  fi

  clean_dir="$(mktemp -d /tmp/proofpath-arxiv-release.XXXXXX)"
  trap 'rm -rf -- "$clean_dir"' EXIT
  tar -xzf output/proofpath_arxiv_source.tar.gz -C "$clean_dir"
  (
    cd "$clean_dir"
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
  )

  if "${search[@]}" -n 'Overfull|undefined citations|undefined references|Citation .* undefined|Reference .* undefined|LaTeX Error|Fatal error' "$clean_dir/main.log"; then
    echo "Clean-source LaTeX check failed; inspect the compiler output above." >&2
    exit 1
  fi

  local_pages="$(pdfinfo output/pdf/proofpath_benchmark.pdf | awk '/^Pages:/ {print $2}')"
  clean_pages="$(pdfinfo "$clean_dir/main.pdf" | awk '/^Pages:/ {print $2}')"
  if [[ "$local_pages" != "$clean_pages" ]]; then
    echo "Page-count mismatch: local=$local_pages clean-source=$clean_pages" >&2
    exit 1
  fi

  pdftotext output/pdf/proofpath_benchmark.pdf "$clean_dir/local.txt"
  pdftotext "$clean_dir/main.pdf" "$clean_dir/clean.txt"
  if ! diff -q "$clean_dir/local.txt" "$clean_dir/clean.txt" >/dev/null; then
    echo "Text mismatch between local and clean-source PDFs." >&2
    exit 1
  fi

  if "${search[@]}" -qi \
    'Author identity to be supplied|Firstname Lastname|Your Name|(^|[^A-Za-z])(TODO|TBD)([^A-Za-z]|$)' \
    "$clean_dir/clean.txt"; then
    echo "Release blocked: placeholder text remains in the final PDF." >&2
    exit 1
  fi

  # pdffonts splits the two-word font type (for example, "Type 1" or
  # "CID TrueType") into two awk fields.  The embedding and subsetting
  # columns are therefore fields 5 and 6 in the data rows.
  if ! pdffonts "$clean_dir/main.pdf" | awk \
    'NR > 2 && ($5 != "yes" || $6 != "yes") {bad=1} END {exit bad}'; then
    echo "Release blocked: the clean-source PDF contains an unembedded or unsubset font." >&2
    exit 1
  fi

  mkdir -p tmp/pdfs/final
  find tmp/pdfs/final -type f -name 'page-*.png' -delete
  pdftoppm -png -r 140 output/pdf/proofpath_benchmark.pdf tmp/pdfs/final/page

  mkdir -p docs/downloads
  cp output/pdf/proofpath_benchmark.pdf docs/downloads/proofpath_benchmark.pdf
  cp output/proofpath_artifact.tar.gz docs/downloads/proofpath_artifact.tar.gz
  cp CITATION.cff docs/downloads/CITATION.cff
  for download in proofpath_benchmark.pdf proofpath_artifact.tar.gz CITATION.cff; do
    if [[ ! -s "docs/downloads/$download" ]]; then
      echo "Release download is missing or empty: $download" >&2
      exit 1
    fi
  done

  echo "Release outputs:"
  echo "  output/pdf/proofpath_benchmark.pdf"
  echo "  output/proofpath_arxiv_source.tar.gz"
  echo "  docs/downloads/"
  echo "Visual-QA pages: tmp/pdfs/final/page-*.png"
else
  echo "Draft PDF: output/pdf/proofpath_benchmark.pdf"
fi
