# Human-validation analysis plan

This plan is fixed before reviews are collected.

For every categorical field, report raw agreement. For nominal fields, report unweighted Cohen's kappa. For ordered evidence ratings and guess confidence, report quadratic-weighted Cohen's kappa on pairs where both reviewers selected an ordered, non-`uncertain` category; report that denominator and retain `uncertain` in raw-agreement/category counts. Report item count, all denominators, and the IDs of every disagreement. Do not collapse categories after inspecting results.

Interpretation thresholds are diagnostic rather than automatic proof: target raw agreement is at least 0.80 for semantic equivalence and evidence dominance; target kappa is at least 0.60 for nominal fields and 0.60 for ordered fields. Prevalence can depress kappa, so raw agreement and the full category table remain primary context. No item is automatically admitted from a pooled score.

After independent review, compare each reviewer's evidence-dominance judgment with the private manifest. This comparison is a check on the authors' operationalization, not a test with human reviewers as ground truth. The third adjudicator resolves disagreements while blinded to the manifest. An item is admissible for a future empirical study only when adjudication records `yes` for semantic-goal, authorization/input, and no-fault-outcome equivalence; one dominant candidate; and no material presentation bias. Report revisions and exclusions transparently.

The analysis script rejects missing values and mismatched item sets. It never imputes ratings. Reviewer replacements and protocol deviations must be logged before analysis. Human-validation results remain `NOT YET RUN` until two authentic independent forms and any required adjudication record exist.
