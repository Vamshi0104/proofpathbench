# ProofPathBench manifests

This directory contains the implemented 96-scenario benchmark: 12 scenarios in each of
eight synthetic, stateful domains. Each manifest defines authoritative initial state, a
task-relative postcondition, collateral constraints, two no-fault-equivalent candidate
plans, evidence provenance, cost/latency, presentation variants, and seeded fault policy.

The primary track records a plan choice before any execution result. The deterministic
runtime, evaluator, and all nine failure classes are implemented and mechanically
validated. The blinded human-validation protocol is prepared but not run, and no provider
model result is included.

Key files:

- `specification.md`: canonical construct, design, failure, and metric definitions;
- `schemas/scenario.schema.json`: machine-readable scenario schema;
- `scenarios/index.json`: scenario hashes and corpus count;
- `validation_report.json`: static design validation;
- `runtime_validation_report.json`: deterministic execution validation.

Validate without modifying the corpus:

```bash
python3 -m proofpath.benchmark.validate
python3 -m proofpath.validate_benchmark --config configs/pilot.yaml
python3 -m pytest -q
```

Regenerate manifests only after an intentional design change:

```bash
python3 -m proofpath.benchmark.generate
```

All validation evidence is software evidence, not behavioral evidence about agents.
