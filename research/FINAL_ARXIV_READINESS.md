# Final arXiv readiness report

**Audit date:** 2026-10-06  
**Release type:** benchmark, deterministic validation, and prospective evaluation protocol; no provider-model findings.  
**Technical decision:** **READY FOR AUTHOR REVIEW AND arXiv UPLOAD.** This is not a guarantee of arXiv moderation or peer-review acceptance.

## Release gates

| Gate | Status | Evidence |
|---|---|---|
| Automated tests | PASS | 48 Python tests and 25 browser-simulator/interface tests pass. Ruff and strict mypy pass. |
| Scientific consistency | PASS | Abstract, methods, limitations, conclusion, and artifact statements consistently describe a benchmark/methods release with no provider-model findings. |
| Numerical consistency | PASS | 96 scenarios × 4 premiums = 384 units; 384 × 2 plans = 768 no-fault executions; 96 × 4 × 2 instructions × 3 models = 2,304 prospective choices; nine failure classes. |
| Scenario integrity | PASS | Schema, identifier, hash, factor-balance, label-order rotation, state-isolation, and matched no-fault checks pass across all 96 scenarios. |
| Deterministic validation | PASS | Both plans reach the same no-fault goal across 768 executions, and all nine forced failure classes activate with their specified semantics. |
| Human-validation protocol | PASS | Fixed 32-item sample, four per domain; balanced hidden X/Y labels and display position; two independent reviewers; prespecified completeness, agreement, thresholds, exclusions, and adjudication. |
| Actual human-validation results | **NOT YET RUN** | Blank forms only. No reviewer ratings or fabricated results are present. This blocks future construct-validated behavioral claims, not an accurately labeled benchmark/protocol release. |
| Statistical analysis | PASS | Confirmatory and pilot-estimation targets, clustering, fixed effects, one-sided hypotheses, Holm adjustment, exclusions, denominators, and missing-data rules are stated prospectively. |
| Power analysis | PASS | Re-running `proofpath.planning.power` with `configs/power.yaml` reproduces `research/power_analysis.json`; these are simulations, not model outcomes. |
| Citation audit | PASS | All 21 manuscript citation keys resolve; cited metadata and characterizations were checked against primary records. One anonymous work remains marked unverified and is not cited. |
| Novelty framing / literature audit | PASS WITH SCOPE LIMIT | Search refreshed through 2026-10-06. The contribution is bounded to sources checked; this is a structured rapid review, not a database-complete systematic review. |
| Textual-integrity audit | PASS WITH SCOPE LIMIT | No serious concern was found in the strongest available local/public-web audit. No plagiarism percentage is claimed because private similarity corpora were unavailable. |
| AI disclosure | PASS | Assistance with development, search support, drafting, editing, and figure layout is disclosed; the human author retains responsibility. |
| Ethics | PASS | Synthetic mock actions, no live accounts or payments, no personal data, and the principal misinterpretation risk are stated. |
| Data/code availability | PASS | The public artifact contains benchmark manifests, code, configuration, deterministic reports, tests, and analysis scaffolding under the stated release boundary. |
| Confound diagnostics | PASS | Machine-readable report covers operations, plan length, tool count, verification steps, cost, latency, aliases, order, and evidence mechanism. It discloses longer verified plans and perfect cost/latency coupling. |
| Artifact reproducibility | PASS | Fresh extraction runs the 48-test core suite, lint, typing, static/runtime validation, and pre-pilot eligibility checks. Consecutive ancillary builds are byte-identical for identical inputs. |
| Source-package hygiene | PASS | The arXiv archive contains only required source, generated tables, figures, bibliography files, and the intentional ancillary archive; member names are unique. |
| Secret/privacy scan | PASS | Public archives exclude raw results, environment files, caches, local absolute paths, evaluator review keys, and the private human-review manifest. Credential-pattern scan passes. |
| PDF compilation | PASS | PDFLaTeX and BibTeX produce an eight-page PDF from both the working tree and clean source with all fonts embedded and subset. |
| Cross-references | PASS | No undefined citation or reference warning remains; local and clean-source extracted text and page counts match. |
| Figures | PASS | Both figures are generated from repository artifacts and render legibly; architecture arrow labels remain within their gutters. |
| Tables | PASS | All generated values match machine-readable sources and fit without overfull boxes. |
| Licensing | PASS | Software is released under Apache-2.0; `LICENSE` and `CITATION.cff` are included in the artifact. The submitter must still choose the arXiv distribution license. |
| README accuracy | PASS | Documented validation, test, regeneration, packaging, and submission commands match the checked workflows. |
| Archive extraction | PASS | The ancillary artifact and arXiv source both extract in fresh temporary directories; the former reruns checks/assets and the latter recompiles the paper. |
| Repository cleanliness | WARNING | Release archives are clean, but the working checkout contains ignored build products and has no committed baseline against which to certify a clean Git status. |
| arXiv source package | PASS | Contains canonical TeX, `.bbl`, bibliography, PDF figures, generated tables, and the screened ancillary archive; filenames, uniqueness, and size pass release checks. |

## Claim boundary

The repository supports claims about benchmark construction, deterministic execution, package reproducibility, and prospective design only. It does not support claims about how language models choose, whether instructions change selection, or whether verification improves observed task outcomes. The current design is not externally preregistered; `research/PREREGISTRATION_DRAFT.md` is a draft and `configs/pilot.yaml` records `gate2_approved_not_preregistered`.

## Required human actions before clicking Submit

1. Verify the exact author name, affiliation, monitored email, contribution statement, acknowledgments, and AI-assistance disclosure.
2. Read and approve the exact final PDF and confirm that the title/abstract entered in arXiv match it.
3. Choose the category and license, confirm endorsement and rights, and personally accept the submittal agreement.
4. If institutional access exists, run the exact final PDF through an approved similarity service and inspect every match; do not convert this local audit into a fabricated percentage.
5. Upload only `output/proofpath_arxiv_source.tar.gz`, inspect arXiv's compiled preview and ancillary listing, and correct any platform-specific warning before final submission.

No engineering or package blocker remains. arXiv moderation is discretionary, and the human-review results remain unrun by design.
