.PHONY: draft metadata checks artifact public-release-check release

# Rebuild generated figures/tables and the local PDF. Draft builds permit the
# explicit author placeholder so layout can be reviewed before author metadata.
draft:
	bash scripts/build_paper.sh draft

# Derive displayed test counts from the runnable suites.
metadata:
	@if [ -d docs ]; then python3 scripts/generate_release_metadata.py; else echo "Release metadata: docs not included in ancillary archive"; fi

# Software and deterministic benchmark checks used by the release gate.
checks: metadata
	python3 research/human_validation/analyze_reviews.py generate --seed 20261006
	python3 -m proofpath.benchmark.diagnostics
	pytest -q
	ruff check .
	mypy proofpath
	@if [ -d docs ]; then cd docs && npm test; else echo "Interactive demo tests: skipped (docs not included in ancillary archive)"; fi
	python3 -m proofpath.validate_benchmark --config configs/pilot.yaml
	python3 -m proofpath.prepilot --config configs/pilot.yaml --write-report research/prepilot_status.json --allow-ineligible

# Build a clean ancillary archive directly from the canonical source tree.
artifact:
	bash scripts/build_artifact.sh

# Validate publication paths, claims, archive hygiene, and accidental secrets.
public-release-check:
	python3 scripts/check_public_release.py
	python3 scripts/check_website_release.py

# After editing paper/main.tex with genuine author metadata, this is the only
# command needed to rebuild, validate, and package the arXiv submission.
release: checks artifact
	bash scripts/build_paper.sh release
	python3 scripts/check_public_release.py
	python3 scripts/check_website_release.py
