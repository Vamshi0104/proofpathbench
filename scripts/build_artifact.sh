#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
archive="$repo_root/output/proofpath_artifact.tar.gz"
extract_dir="$(mktemp -d /tmp/proofpath-artifact-release.XXXXXX)"
trap 'rm -rf -- "$extract_dir"' EXIT

python3 "$script_dir/build_artifact.py"
python3 "$script_dir/check_public_release.py" --archive-only

tar -xzf "$archive" -C "$extract_dir"
(
  cd "$extract_dir"
  python3 -m proofpath.benchmark.validate
  python3 -m proofpath.validate_benchmark --config configs/pilot.yaml
  python3 -m pytest -q
  ruff check .
  mypy proofpath
  python3 -m proofpath.prepilot --config configs/pilot.yaml --allow-ineligible
  mkdir -p .cache .mpl
  MPLBACKEND=Agg MPLCONFIGDIR="$extract_dir/.mpl" XDG_CACHE_HOME="$extract_dir/.cache" \
    python3 paper/build_assets.py
)

echo "Extracted-artifact README commands: PASS"
