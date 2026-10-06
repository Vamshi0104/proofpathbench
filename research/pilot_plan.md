# Exact pilot plan

**Status:** Gate 2 design and split-plot amendment approved; pre-pilot human review,
empirical manipulation check, model-panel freeze, and preregistration remain. No model
calls should be made from this document alone.

## Objective

Validate that ProofPathBench can isolate ex-ante preference for independently observable outcomes and estimate its sensitivity to verification premium, disclosed silent-failure probability, and concrete consequence severity.

## Stage P0 — deterministic benchmark validation

1. Implement the schema, typed models, in-memory authoritative store, agent-visible tool facade, oracle trace, seeded failure injector, and evaluator.
2. Author 96 scenarios: 12 per domain across the eight specified domains.
3. For every scenario, execute both candidate plans without faults and assert identical intended postconditions and collateral constraints.
4. Activate every supported failure deterministically and assert the intended divergence between authoritative state and tool-visible response.
5. Generate two prompt paraphrases, two neutral alias/order variants, and a hidden evidence-dominance label.
6. Have two blinded human reviewers independently assess semantic equivalence and evidence dominance. Adjudicate disagreements. Record agreement; do not admit unresolved cases.
7. Run prompt leakage checks that search agent-visible material for normative labels such as “verified,” “safe,” “recommended,” or hidden label keys.

**P0 pass rule:** 100% deterministic tests pass; all 96 pairs have adjudicated equivalence and unique evidence dominance; no hidden labels leak.

## Stage P1 — manipulation check

Use a separate, non-agent model call or human coding task to classify which candidate offers stronger independent evidence and which costs more, without asking which should be chosen.

**Pass rule:** lower 95% confidence bound for correct evidence-strength classification is at least 0.85 overall and at least 0.75 in every domain. Otherwise revise descriptions; do not run the behavioral pilot.

## Stage P2 — preregistered plan-choice pilot

### Design

- 96 base scenarios.
- Split-plot 24-cell design: every base scenario is crossed with all four verification
  premiums (`1.00, 1.10, 1.50, 2.00`); disclosed silent-failure probability
  (`0, .05, .20`) and concrete severity (`low, high`) remain between-task assignments.
  This yields 16 treatment units per premium × risk × severity cell.
- Domain, task archetype, alias set, and plan order are counterbalanced by the published
  assignment manifest. The three strong-evidence mechanisms are nuisance conditions:
  32 each overall, exactly balanced across cost and severity margins, and within one
  count across every risk margin. Mechanism is a preregistered adjustment variable.
- Two instruction conditions: vanilla and explicit verify instruction.
- Four presentation variants per scenario: two prompt paraphrases × two plan/tool
  orderings, deterministically rotated one-to-one over the four premiums.
- One independent call per premium/presentation unit, instruction, and model. This
  post-Gate-2 allocation was selected before outcome collection by the prospective
  simulation in `power_analysis.json`.
- Three model tiers selected and frozen only after confirming API/version availability.
  The pilot's single-provider limitation is explicit; an independent or open-weight
  family is reserved for the post-Gate-3 main experiment if feasible.

Planned maximum: `96 × 2 instructions × 4 premium/presentation units × 1 repetition × 3 models = 2,304` registered-choice runs. The prospective simulation estimated 0.991 power (Monte Carlo SE 0.0009) for its assumed approximately eight-percentage-point marginal instruction effect under the two-test Holm threshold. Premium and interaction power estimates are recorded separately and keep H3–H5 as pilot estimation targets. Never reduce or extend based on observed condition effects.

### Procedure per run

1. Reset authoritative and visible stores from the manifest.
2. Derive and log all sub-seeds from `(master_seed, scenario_id, model_id, instruction, presentation, repetition)`.
3. Present the task, two neutral candidate plans, plan costs/latencies, and disclosed risk.
4. Require `register_plan` before any execution tool is enabled.
5. Record the immutable selection and optional categorical rationale.
6. Execute the registered plan in the deterministic mock environment with the pre-sampled failure schedule.
7. Allow bounded recovery only after the registered choice; recovery cannot change the primary selection label.
8. Record terminal claim, tool trace, token usage, simulated and observed latency, tool cost, authoritative terminal state, oracle events, and exclusions.

### Primary analysis

The proposed primary model is logistic regression with model/domain/presentation nuisance
effects and scenario-cluster-robust uncertainty. Model is a fixed effect because three
model clusters are too few for a defensible model-cluster sandwich. A Bayesian logistic mixed
model with scenario and model random intercepts is the sensitivity analysis. Both predict
selection of the evidence-dominant plan from standardized premium, disclosed risk,
severity, instruction condition, evidence mechanism, and preregistered premium×risk and
premium×severity interactions. Freeze exact formulas after interaction-power simulation
and before empirical calls. Report raw cell rates and clustered/bootstrap intervals.

Confirmatory pilot tests correspond to H1–H2. Holm correction covers this two-test
family. H3–H5 are directional estimation targets for sizing the post-Gate-3 study. H6 is
a construct/manipulation requirement, as approved with Gate 2. The smallest effect size
of interest is 10 percentage points.

### Exclusions

Exclude only runs with provider/network failure before a valid model response, schema-invalid `register_plan` after the fixed repair allowance, or benchmark infrastructure failure. Agent mistakes remain outcomes. Report every exclusion by condition and model.

## Stage P3 — open-action ecological check

Run a stratified 24-scenario subset with the plan menu removed. Use the same tools and costs; classify traces mechanically. This stage is secondary and estimates whether forced registered choice changes behavior.

## Stage P4 — Gate 3 decision

Recommend:

- **GO:** manipulation checks pass, anti-confound audits pass, and the pilot yields estimable non-degenerate selection behavior with a meaningful risk/cost/severity pattern or a scientifically informative, precise negative result.
- **MODIFY:** construct validity passes but ceiling/floor effects, model heterogeneity, or weak ecological transfer require redesign.
- **NO-GO:** matched-plan validity fails, presentation artifacts dominate, or a precise null rules out the preregistered smallest effect of interest across the target conditions.

No ProofPath planner is implemented before this gate.

## Intended commands after implementation

```bash
python -m pytest
python -m proofpath.validate_benchmark --config configs/pilot.yaml
python -m proofpath.run_manipulation --provider openai --model MODEL --run-id RUN_ID --confirm-review-complete
python -m proofpath.run_pilot --config configs/pilot.yaml --stage registered-choice --provider openai --model MODEL --run-id RUN_ID --confirm-preregistered
python -m proofpath.analyze results/raw/RUN_ID/records.jsonl
```

Each command must emit a run manifest and refuse to overwrite an existing raw run directory.
