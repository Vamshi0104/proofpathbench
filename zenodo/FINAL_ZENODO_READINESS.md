# Final Zenodo readiness

| Gate | Status | Evidence / required human review |
|---|---|---|
| Final paper | PASS | Exact final-audit PDF; eight pages; no scientific rewrite for Zenodo. |
| Paper/artifact consistency | PASS | Canonical counts, failure names, scope, tests, and prospective power records agree. |
| Metadata | PASS | Publication/preprint metadata parses; verified author affiliation, correspondence email, source repository, and project website are included. |
| CITATION.cff | PASS | CFF 1.2.0 parses; preferred citation present; contains the matching DOI `10.5281/zenodo.23196925`. |
| Licensing | WARNING | Artifact is Apache-2.0. Author must confirm the paper/content license in Zenodo; no separate manuscript license is declared. |
| Artifact completeness | PASS | Scenarios, schemas, implementation, failure/evaluation/analysis code, power analysis, tests, audits, and public human-review protocol included. |
| Archive cleanliness | PASS | Automated prohibited-member scan passes. |
| macOS metadata scan | PASS | Zero `.DS_Store`, `._*`, `__MACOSX`, or AppleDouble sidecars. |
| Secret/privacy scan | PASS | Focused recursive release and archive scan passes; intentional author identity is not treated as a secret. |
| Checksums | PASS | Deterministic checksum list verifies. |
| Manifest | PASS | Machine-derived counts and release hashes match. |
| Fresh extraction | PASS | Self-contained archive extracted and documented commands ran in a fresh temporary directory. |
| Tests | PASS (48/48) | Extracted Python suite result. Website suite remains a repository/GitHub Pages concern and is recorded separately in the manifest. |
| Reproducibility | PASS | Static/runtime checks, prospective power output, and generated assets reproduce. |
| Human-validation labeling | PASS | Described as a blinded human construct-validation protocol, not a human-validated benchmark. |
| Simulation/empirical labeling | PASS | Fixtures and simulations are not advertised as model results. |
| Textual-integrity/plagiarism review | PASS WITH LIMIT | Local and public-web phrase checks found no serious concern or distinctive multi-sentence match. No private similarity corpus was available, so no percentage is claimed. |
| Paper quality and voice | 8.7/10 | Clear, technically disciplined, and unusually candid about scope. The prose is dense and repeats claim-boundary language; the disclosed AI assistance and final human line edit must remain transparent. |
| GitHub integration readiness | PASS | Version/tag strategy is coherent (`v0.0.1`); manual deposit is the single-record strategy; the verified public source repository is linked. |
| GitHub Pages integration readiness | PASS | The canonical project URL and Zenodo DOI `10.5281/zenodo.23196925` are configured. |
| DOI readiness | PASS | DOI `10.5281/zenodo.23196925` matches the website, deposit metadata, citation metadata, and manifest. |
| Zenodo upload readiness | WARNING | Engineering package is ready. Before Publish, the author must confirm paper rights, final metadata, and the live Zenodo preview. |
| arXiv preservation | PASS | Zenodo build is additive and hash-checks all arXiv-named paths before/after. |

## Manuscript note

The approved manuscript contains two factual references to the separately preserved arXiv
ancillary archive. They are destination-specific artifact descriptions, not scientific
changes. The Zenodo PDF remains byte-identical to the approved manuscript; the wording is
reported rather than silently rewritten.

## Submission review checklist

1. Confirm the author name, contact email, contribution statement, and AI-assistance disclosure.
2. Confirm the paper/content license and configure mixed file licenses accurately.
3. Read the exact PDF and compare title/abstract against the Zenodo preview.
4. Confirm resource type Publication / Preprint, version 0.0.1, and publication date.
5. Confirm no provider-model or completed-human-validation claim appears in the record.
6. Inspect the artifact and checksum file names in the live file list.
7. Confirm the verified GitHub repository, project website, and Independent Researcher affiliation; add only verified ORCID, funding, arXiv, or DOI values.
8. If available, run the exact PDF through an institutional similarity service and review matches.
9. Confirm DOI `10.5281/zenodo.23196925` matches the reserved or published Zenodo record.
10. Publish one canonical record for this version and use Zenodo versioning for future releases.
