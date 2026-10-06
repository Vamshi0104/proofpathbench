# ProofPathBench pilot preregistration draft

**Status:** not frozen. No empirical model response is admissible while the config status
is `gate2_approved_not_preregistered`.

This draft incorporates the approved Gate 2 design, the deterministic runtime acceptance
report, and the prospective instruction-effect power simulation. The exact provider model
snapshot(s), completed blinded-review report, empirical manipulation-check run ID, and
interaction-power decision remain blank and must be filled before freezing.

## Primary outcome

The primary outcome is the immutable pre-execution indicator that the registered plan is
the evaluator-authored evidence-dominant plan. Schema-invalid responses after the fixed
zero-repair allowance are exclusions and are reported by condition. Model mistakes and
unexpected choices remain outcomes.

## Primary factors

- total verification premium: `1.00, 1.10, 1.50, 2.00`;
- disclosed mutation-fault probability: `0, .05, .20`;
- concrete consequence severity: low/high;
- instruction: vanilla/verify instruction.

Evidence mechanism, domain, prompt paraphrase, tool aliases, displayed plan order, and
exact model snapshot are preregistered nuisance variables. Cost and latency move together,
so the estimand is total execution premium.

## Pilot tests and estimation targets

1. H1: vanilla VPSR at zero premium exceeds 0.5.
2. H2: verify instruction increases VPSR.

H3 (premium slope), H4 (premium by risk), and H5 (premium by severity) are preregistered
directional **estimation targets** in the pilot. Prospective power is inadequate for
confirmatory premium or interaction claims. Their estimates and cluster-robust intervals
inform the post-Gate-3 main-experiment sample size; they must not be promoted to pilot
“discoveries” based on observed signs or intervals.

The former H6 is treated as a construct/manipulation requirement rather than a sixth
behavioral test because it largely duplicates H1 and the matched-cost independent-readback
subset has only eight base scenarios. The human author accepted this prospective change
with the Gate 2 package on 2026-09-28.

Holm correction covers the two confirmatory pilot tests. Directional tests must be frozen
before data.
The smallest effect size of interest is 10 percentage points. Raw proportions with Wilson
intervals are descriptive. The three-model pilot uses model fixed effects and
scenario-cluster-robust uncertainty; model-cluster sandwich inference is not used with
only three model clusters. A later study may use two-way clustering if it contains at
least 20 distinct model clusters.

## Exclusions and stopping

- Exclude only provider/network failure before a response, schema-invalid output after
  zero repair attempts, or recorded infrastructure failure.
- Preserve partial runs and never overwrite a run directory.
- Do not inspect condition summaries until the planned run is complete or formally
  terminated for a documented infrastructure reason.
- Do not increase repetitions after observing outcomes.

## Required freeze fields

- Exact immutable model snapshot IDs and provider parameters.
- Completed two-reviewer report and adjudication disposition.
- Passing empirical manipulation check.
- Interaction-power assessment and final model count.
- UTC freeze timestamp and SHA-256 of the frozen configuration.
