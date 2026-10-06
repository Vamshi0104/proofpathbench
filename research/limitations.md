# Known limitations through Gate 2

- The literature audit is a structured rapid review, not yet a database-complete systematic review.
- Several closest works are very recent arXiv preprints; peer-review status and priority may change.
- “Independent” verification is graded, not binary. A read endpoint backed by the same corrupted subsystem may not provide meaningful independence.
- Stated failure probabilities in prompts measure reasoning about disclosed risk; experienced empirical risk is a distinct treatment.
- Synthetic costs and consequences may not reproduce real incentives.
- Plan pairs can accidentally differ in wording, length, salience, tool familiarity, reversibility, or perceived success probability.
- LLM nondeterminism and provider-side model updates can impair reproducibility even with fixed seeds.
- A 96-scenario pilot may detect moderate or large behavioral patterns but is not adequate
  for broad claims across domains and model families without power analysis and replication.
- State-based evaluation establishes benchmark truth only relative to the simulator specification.
- The proposed mixed-effects analysis may need Bayesian or cluster-robust alternatives if separation, sparse cells, or convergence failures occur; any change must be documented before unblinding outcome comparisons.
