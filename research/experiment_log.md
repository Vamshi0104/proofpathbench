# Experiment log

No experiments have been run.

| Date | Phase | Action | Artifact | Decision |
|---|---|---|---|---|
| 2026-09-28 | 0 | Initialized repository scaffold and reproducibility policy | repository files | Complete |
| 2026-09-28 | 1 | Conducted structured rapid related-work search and citation audit | `search_protocol.md`, `related_work_matrix.md`, `citation_audit.md` | Gate 1 review required |
| 2026-09-28 | 2 | Drafted novelty criteria, RQs, and hypotheses | research documents | Not frozen |
| 2026-09-28 | 3 | Drafted benchmark and pilot specifications only | benchmark documents/config | Implementation blocked on Gate 1 |
| 2026-09-28 | Gate 1 | Human approved narrowed novelty/design direction | `GATE_1_ASSESSMENT.md` | Proceed to benchmark design |
| 2026-09-28 | 3 | Implemented typed 96-scenario manifests, schema, hash index, counterbalanced renderings, and static validation | `benchmark/`, `proofpath/benchmark/`, `tests/` | Gate 2 review required; no experiments run |
| 2026-09-28 | Gate 2 | Human approved the benchmark design | `GATE_2_DESIGN_REVIEW.md` | Proceed to environment and pre-pilot acceptance implementation |
| 2026-09-28 | 4 | Implemented authoritative/visible/oracle state separation, all nine seeded failures, evaluator, immutable run records, manipulation runner, review packet, and prospective power simulation | runtime report, tests, non-empirical smoke runs | No empirical model responses collected |
| 2026-09-28 | Gate 2 amendment | Prospective power audit found original between-task factorial underpowered; implemented split-plot premium expansion | `GATE_2_AMENDMENT.md`, `power_analysis.json` | Human approved the current Gate 2 package; pilot H4–H5 remain estimation targets |
| 2026-09-28 | 4 validation | Regenerated static/runtime evidence against the approved config and ran quality suite | `benchmark/validation_report.json`, `benchmark/runtime_validation_report.json`, test output | Validation suite, lint, and strict type checking pass; no empirical model responses collected |
| 2026-09-29 | Zero-cost closeout | Owner selected protocol-only completion with no external model calls | `ZERO_COST_COMPLETION.md`, `paper/` | No empirical behavioral claims; manuscript is a study protocol |
| 2026-10-06 | Release audit | Added fixed 32-item blinded two-reviewer protocol, explicit confound diagnostics, refreshed literature/text-integrity audits, and archive privacy checks | `research/human_validation/`, `research/confound_diagnostics.json`, release report | Protocol prepared; human review and provider studies remain unrun |

All future runs must append rather than overwrite entries and must identify config digest, git commit, model version, prompt version, tool-schema version, seed manifest, and raw-output directory.
