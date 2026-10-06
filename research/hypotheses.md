# Preregistered hypotheses

**Status:** design-stage hypotheses; no result is implied. Effect directions and analysis rules must be frozen before collecting model outputs.

## Confirmatory pilot hypotheses

**H1 — Baseline observability sensitivity.** In the vanilla condition at zero verification premium, the probability of selecting an independently verifiable plan will exceed the probability of selecting a weakly verifiable plan after counterbalancing order and labels.

**H2 — Incomplete spontaneous preference.** The vanilla agent's verifiable-plan selection rate at zero premium will remain below the verify-instruction condition's rate. This replaces the vague claim that agents “will not consistently prefer” verification with a direct contrast.

## Preregistered pilot estimation targets

The pilot reports estimates and cluster-robust confidence intervals for H3--H5, but it
does not test them confirmatorily. Prospective power is inadequate for definitive claims;
the estimates are used to size a later study without optimizing effects after inspection.

**H3 — Cost elasticity.** Verifiable-plan selection will decrease as the verification cost/latency premium rises from 1.00× to 2.00×, holding task, risk, severity, and evidence quality constant.

**H4 — Failure-risk interaction.** The negative effect of verification premium will be attenuated as disclosed silent-failure probability increases; equivalently, agents will accept a larger premium when silent failure is more likely.

**H5 — Severity interaction.** Agents will accept a larger verification premium in high-consequence scenarios than in low-consequence scenarios when the modeled consequences are concrete and otherwise matched.

**H6 — Evidence independence.** Independent authoritative readback will be selected more often than weak confirmation derived from the write response when nominal cost and latency are matched.

## Later-phase hypotheses

These are not tested confirmatorily in the first choice pilot unless separately powered and frozen.

**H7 — False completion reduction.** Under injected silent failures, a verifiability-aware planner will reduce false completion relative to vanilla and cost-aware-only planners.

**H8 — Recovery mediation.** The improvement in verified task success from a verifiability-aware planner will be partially mediated by failure detection followed by a non-duplicating recovery action.

**H9 — Noisy-verifier adaptation.** Selection of a verifier will decrease as its stated and empirically realized reliability decreases, but high-severity conditions will favor corroboration from a second independent source rather than abandonment of verification.

## Nulls and smallest effect size of interest

- Primary null for H1/H6: odds ratio = 1 for evidence-quality treatment after planned covariate adjustment.
- Later-study null for H3: no average trend in selection across premiums.
- Primary interaction nulls for H4/H5: interaction coefficient = 0.
- Proposed smallest effect size of interest: 10 percentage points in selection probability, subject to simulation-based power analysis and author approval before data collection.

## Analysis discipline

- Test H1 as the marginal vanilla, zero-premium VPSR against 0.5 with
  scenario-cluster-robust uncertainty.
- Model H2 and the H3--H5 estimation targets with a preregistered logistic regression and
  model fixed effects and scenario-cluster-robust uncertainty; report H3 as the
  design-average premium slope rather than a single reference cell. Do not use a
  model-cluster sandwich with only three model clusters.
- Report marginal effects, odds ratios, cluster/bootstrap confidence intervals, and raw cell counts.
- Treat model-family comparisons, individual evidence dimensions, and non-monotonic effects as exploratory unless separately powered.
- Do not replace failed confirmatory tests with post-hoc hypotheses. Label deviations and exploratory analyses explicitly.
