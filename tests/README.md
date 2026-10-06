# Planned test coverage

Before the pilot, tests must cover:

- separation and reset of authoritative versus agent-visible state;
- every seeded failure transition and response;
- deterministic seed derivation and replay;
- postcondition and collateral predicates;
- evidence-profile dominance and incomparability;
- plan-equivalence validation;
- VPSR, VTS, FCR, recovery, cost, latency, and interval calculations;
- schema validation, config snapshots, and refusal to overwrite raw runs.

Executable tests cover typed manifests, evidence dominance, split-plot factor balance,
agent-visible rendering, evaluator-label leakage, authoritative-state isolation, all
seeded failure modes, evaluation metrics, preregistration guards, and statistics.
