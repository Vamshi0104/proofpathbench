# Gate 2 — ProofPathBench design review

**Decision requested:** APPROVE, MODIFY, or STOP before mock-environment and pilot
implementation. Gate 1 was approved on 2026-09-28. No agent/model experiments have run.

## Recommendation

**APPROVE WITH PRE-PILOT CONDITIONS.** The current benchmark design is sufficiently
specified and mechanically validated to implement the authoritative mock environment,
failure injector, evaluator, and manipulation check. Approval does not authorize claims
about agent behavior and does not waive the acceptance tests below.

## Implemented design

- 96 deterministic manifests: 12 task archetypes in each of eight mock domains.
- 24 primary cells: four verification premiums × three disclosed fault probabilities ×
  two concrete consequence severities, with four scenarios per cell.
- Two candidate plans per scenario with the same mutation. One stops at the mutation
  response; the other adds independent readback, operation-ledger lookup, or readback
  plus append-only history.
- Evaluator-side evidence profiles use a six-dimensional categorical partial order:
  independence, authority, specificity, freshness, linkage, and coverage.
- Four presentation variants per scenario: two prompt paraphrases and two reversed plan
  orders, with two neutral alias sets.
- A vanilla instruction and a verify-instruction manipulation. Only the instruction text
  changes between those conditions.
- Agent-visible rendering excludes authoritative initial state, design cells, evidence
  profiles, provenance labels, seeds, severity labels, and the dominant-plan label.

## Static validation result

`benchmark/validation_report.json` records a passing report with zero errors:

- 96 unique scenarios and 12 per domain;
- all 24 treatment cells represented four times;
- 48/48 balance for dominant plan label A/B, including 2/2 within every cell;
- 32 scenarios for each strong-evidence mechanism;
- exact within-domain balance for premium (3 each), risk (4 each), severity (6/6), and
  dominant label (6/6);
- exact mechanism balance across premium and severity margins and near-exact balance
  across risk margins (10/11/11 in each 32-scenario margin);
- matched mutation steps, no added mutations in the evidence plan, declared cost totals,
  and declared latency totals;
- stable schema validation, content hashes, presentation order/alias behavior, and
  evaluator-label leakage tests.

The test suite currently contains 10 passing tests. These are design tests, not evidence
for any research hypothesis.

## Design judgments requiring human approval

1. **Between-scenario factorial.** Task archetypes are assigned to one primary factor
   cell rather than repeated across every cell. Counterbalancing and planned domain/
   scenario effects reduce confounding, but a fully within-task factorial would be much
   larger.
2. **Mechanism as nuisance variable.** The three strong evidence mechanisms are balanced
   rather than fully crossed. Mechanism-specific causal claims are therefore exploratory
   unless a later fully crossed study is added.
3. **Joint cost/latency premium.** Cost and latency rise together in the pilot. RQ2 can be
   interpreted as total execution premium, not as a separate cost-only or latency-only
   effect. Orthogonal sensitivity runs are required for component-specific claims.
4. **Forced-choice primary outcome.** Immutable pre-execution plan registration cleanly
   measures selection but is less ecological than free tool use. A preregistered
   open-action subset is retained as a secondary check.
5. **Planned run budget.** Gate 2 allowed up to 6,912 registered-choice calls before
   manipulation checks and open-action runs. The prospective post-approval simulation
   subsequently recommended one call per presentation (2,304 calls for three models).
   That reduction occurred before any empirical model response; interaction power still
   requires review before preregistration.

## Mandatory conditions before Gate 3

After Gate 2 approval, implementation must satisfy all of the following before a pilot is
treated as valid:

- both plans pass deterministic no-fault semantic-equivalence and collateral tests;
- authoritative state, tool-visible state, and oracle trace are demonstrably isolated;
- every declared failure activates under known seeds and is absent under controls;
- outcome predicates have positive and negative tests;
- two blinded human reviewers assess evidence dominance and semantic equivalence, with
  disagreements adjudicated and agreement reported;
- a manipulation check meets the preregistered confidence-bound thresholds;
- power/budget simulation freezes the number of models, repetitions, and smallest effect
  size of interest;
- model identifiers, prompts, tool schemas, provider parameters, seeds, exclusions, and
  raw outputs are logged without overwrite.

## Gate 2 response format

Please record one decision:

- **APPROVE:** implement the environment and pre-pilot acceptance suite under this design.
- **MODIFY:** identify the design changes required before implementation.
- **STOP:** end the project and preserve the Gate 1/Gate 2 audit artifacts.
