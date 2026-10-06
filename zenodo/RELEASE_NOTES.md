# ProofPathBench v0.0.1 release notes

Initial public ProofPathBench benchmark release.

- Includes the research preprint and a frozen, self-contained reproducibility artifact.
- Provides 96 synthetic scenarios across 8 domains and 384 task-treatment units.
- Mechanically validates 768 deterministic no-fault plan executions.
- Implements nine seeded failure classes and explicit authoritative/tool-visible/oracle
  state separation.
- Includes static and runtime validation infrastructure, evaluation and analysis code,
  prospective power analysis, and reproducibility tests.
- Includes a fixed blinded human construct-validation protocol. No human-review result is
  claimed because the protocol has not been run.
- Complements the interactive GitHub Pages website while leaving website development
  assets in the canonical source repository.
- Records the canonical source at <https://github.com/Vamshi0104/proofpathbench> and the
  project website at <https://vamshi0104.github.io/proofpathbench/>.
- Contains no provider-model behavioral evaluation. Fixtures and simulations are not
  reported as observed model outcomes.

The release is versioned `v0.0.1` to match the canonical repository version. The primary
Zenodo resource is a research preprint with an accompanying benchmark software artifact;
it is not described as peer reviewed or as a journal/conference publication.
