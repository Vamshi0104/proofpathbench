# ProofPathBench reproducibility artifact v0.0.1

This frozen artifact accompanies the ProofPathBench research preprint. It contains the
96-scenario synthetic benchmark, schemas, deterministic runtime, nine failure classes,
evaluation and analysis code, prospective power configuration/output, public validation
records, tests, citation/related-work audits, and the blinded human construct-validation
protocol.

Canonical source: <https://github.com/Vamshi0104/proofpathbench>  
Project website: <https://vamshi0104.github.io/proofpathbench/>

It contains no provider-model behavioral results. Fixture executions and power
simulations are non-empirical. The human-review protocol has not been run.

## Requirements

- Python 3.11 or newer
- dependencies declared in `pyproject.toml` / `requirements.txt`

Install into an isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Validate

```bash
python3 -m proofpath.benchmark.validate
python3 -m proofpath.validate_benchmark --config configs/pilot.yaml
python3 -m pytest -q
```

Regenerate machine-derived prospective power output to a temporary file and compare it
with `research/power_analysis.json`:

```bash
python3 -m proofpath.planning.power --config configs/power.yaml --output /tmp/proofpath-power.json
```

Regenerate manuscript figures and tables from the frozen JSON/YAML inputs:

```bash
python3 paper/build_assets.py
```

The benchmark's machine-readable acceptance evidence is in
`benchmark/validation_report.json` and `benchmark/runtime_validation_report.json`.
Software and benchmark material are licensed under Apache-2.0; see `LICENSE`.
