# Final website and public-release gate

**Audit date:** 2026-10-06  
**Decision:** **READY TO HOST.** No known engineering blocker remains. The warnings below are publication-configuration or coverage limits, not defects hidden by the release gate.

## Release-gate result

| Gate | Status | Evidence and boundary |
|---|---|---|
| HTML validity | WARNING | The standard-library parser, link/anchor checker, and Chromium parser found no structural failure. The legacy macOS `tidy` build cannot recognize modern HTML5 elements, so no claim is made that an independent current HTML5 conformance service was run. |
| CSS | PASS | The stylesheet loads without a browser warning, every local `url()` target resolves, focus styles and reduced-motion rules are present, and the requested layouts render without page overflow. |
| JavaScript | PASS | 25 interface/engine tests pass; the rendered interaction path produces no Chromium console warning or error. The public runtime has no dependency, analytics, tracker, cookie, backend, or external service. |
| Simulation correctness | PASS | All nine canonical failure classes are implemented. Deterministic schedules, equal paired schedules, zero-risk behavior, state isolation, timeout-before/after, false success, partial update, stale/delayed readback, wrong target, duplicate effect, ledger evidence, and direct/verified claims have regression coverage. |
| Unit/regression tests | PASS | 48 Python benchmark tests and 25 website interface/engine tests pass. Ruff and strict mypy pass. |
| Scientific consistency | PASS | Website, runtime report, artifact, and final PDF agree on 96 scenarios, 8 domains, 384 task-treatment units, 768 no-fault executions, 9 failure classes, deterministic scope, and absence of provider-model results. |
| Artifact download | PASS | `docs/downloads/proofpath_artifact.tar.gz` exists and is byte-identical to the release artifact. Fresh extraction reruns documented validation, test, lint, type, pre-pilot, and paper-asset commands. |
| Archive cleanliness | PASS | The ancillary archive contains no AppleDouble entries, `.DS_Store`, `__MACOSX`, caches, private review keys, raw results, environment files, editor files, or duplicate members. Archive-member checks are automated. |
| Reproducible archive | PASS | Two consecutive builds from unchanged inputs produced byte-identical SHA-256 results. The digest is intentionally not embedded in the archive itself, which would make the package self-referential. |
| Secret/privacy scan | PASS | Intended public files and archive text were scanned for common API-key, token, bearer-header, private-key, cloud-key, and private absolute-path patterns. Private review keys/manifests are generated only under ignored `tmp/`. The published author email is intentionally exempt. |
| Accessibility | WARNING | No known major blocker: native controls and dialog, landmarks, one `h1`, skip link, table caption/scope, labels, non-color text labels, visible focus, reduced motion, and correctly named live results are present. Full assistive-technology testing with VoiceOver/NVDA and an independent axe/WAVE run were not available, so those are not claimed. |
| Keyboard navigation | PASS | Plan cards use roving `tabindex` and arrow keys; the citation dialog initially focuses its close control, closes with Escape, and restores focus to its trigger. Native selects, ranges, links, and buttons remain keyboard operable. |
| Responsive layouts | PASS | Rendered Chromium checks at 320, 375, 390, 430, 768, 1024, 1280, 1440, and 1920 px found zero document-level horizontal overflow and zero clipped interactive controls. The wide evidence table remains an intentionally scrollable data table on narrow screens. |
| Zoom/reflow | PASS WITH LIMIT | Fluid widths, wrapping, and the 320 px layout provide the required reflow behavior for normal text zoom. A separate OS/browser 200% zoom automation was not available; no false claim of that exact run is made. |
| Performance | PASS | The dependency-free site uses local system fonts and local static assets, has no runtime network call, and performs bounded deterministic loops (100, 1,000, or 10,000 pairs). Non-download assets are under 1 MB; the 1200 x 630 social preview is the largest asset at about 744 KB. |
| SEO metadata | PASS | Title, description, viewport, theme color, favicon, robots policy, and canonical production URL are present. |
| Social metadata | PASS | Open Graph and summary-large-image metadata are present with a verified 1200 x 630 preview and canonical absolute page/image URLs. |
| Citation metadata | PASS | Website BibTeX, `CITATION.cff`, author, title, year, and release version agree. No arXiv identifier is fabricated. One `site-config.js` update can expose a future arXiv link. |
| Internal links | PASS | Automated `href`, `src`, download, CSS asset, and fragment checks pass; no path escapes `docs/`. |
| External research links | PASS WITH SCOPE LIMIT | The dated citation audit records a primary-source recheck for every cited work. This is a 2026-10-06 link/metadata audit, not a promise that third-party URLs can never change. |
| Paper download | PASS | The eight-page PDF exists in `docs/downloads/`, compiles locally and from the clean arXiv archive, has embedded subset fonts, and has no final undefined citation/reference or overfull-box warning. |
| Repository link | PASS | The author-supplied canonical source URL is configured in the website and citation metadata. |
| GitHub Pages compatibility | PASS | `docs/` is self-contained, uses relative case-correct paths, requires no server routing, has `.nojekyll`, and contains the paper, artifact, citation file, favicon, and preview image. CI validates and deploys both `main` and `master`. |
| README | PASS | The root README answers scope, question, novelty, contents, exclusions, validation, figure/table reproduction, local site use, Pages deployment, citation, license, scenario/failure locations, power, human validation, and citation audit. |
| License | PASS | Apache-2.0 is present and included in the artifact; citation metadata agrees. The submitter must separately choose an arXiv distribution license. |
| Cross-browser checks | WARNING | Chromium was rendered and exercised. Firefox and WebKit/Safari engines were not available in this environment, so cross-engine PASS is not fabricated. The implementation uses conservative native HTML/CSS/JavaScript and has no known engine-specific dependency. |

## What changed in the final engineering pass

- Preserved the existing visual system and static architecture.
- Replaced ambiguous simulation terminology with “Paired simulation” and “Simulated failure risk.”
- Aligned the browser engine with all nine benchmark failure semantics and the canonical operation-ledger behavior.
- Made paired comparisons use the same deterministic failure schedule and made single runs seed-controlled.
- Added high-value regression coverage, increasing the website suite from 10 to 25 tests.
- Generated website test counts from the actual suites so benchmark and interface counts cannot be confused.
- Added honest research navigation for paper, artifact, citation, and a conditionally configured repository/arXiv link.
- Added a native accessible citation dialog and corrected its focus, Escape, and live-result naming behavior.
- Added release checks for scientific counts, failure classes, links, assets, metadata, preview dimensions, secrets, private paths, and development-only URLs.
- Rebuilt the artifact deterministically, removed AppleDouble/macOS debris, moved evaluator keys out of public paths, and tested the extracted package.
- Added a restrained 1200 x 630 Open Graph image without adding runtime dependencies.
- Made the Pages workflow validate the benchmark, website, archive, and downloads before deployment.

## Honest 2026 assessment

### Website implementation: **9.1 / 10**

This is now a strong research-artifact website rather than a generic landing page. Its best qualities are the immediate scientific boundary, unusually clear response/state/evaluator separation, deterministic interactive explanation, excellent visual restraint, local-only operation, low dependency risk, and reproducible release checks. The interaction teaches the core idea instead of merely advertising it.

The score is not 10 because two assurances remain external to the implementation: only Chromium was available for rendered engine testing, and no independent assistive-technology audit was run. Those are real limits. They do not justify more speculative redesign or another framework.

### Research artifact and reproducibility: **9.2 / 10**

The package is the strongest part of the release. Scenarios, schema, hashes, deterministic runtime reports, forced-failure semantics, power inputs, confound diagnostics, tests, analysis scaffolding, human-review protocol, citation audit, and build/release checks are all exposed. The clean extraction and deterministic archive build materially improve scientific trust.

The remaining gap is scientific rather than engineering: blinded human validation and provider-model evaluation have not been run. The repository says this plainly.

### Paper as a benchmark/methods release: **8.3 / 10**

The manuscript has a sharp question, bounded novelty claim, explicit state/evidence semantics, reproducible counts, prospective analysis, honest limitations, and a clean eight-page presentation. It no longer pretends deterministic software validation is behavioral evidence.

Its main weakness is also its scope: it introduces an implemented benchmark and protocol but provides no provider-model results and no completed blinded human-validation results. That is acceptable for an arXiv benchmark/methods release, but it makes the paper less compelling than a full empirical study. Interaction effects are explicitly underpowered, the design is not externally preregistered, cost and latency are perfectly coupled, and verified plans are necessarily longer. Those limits correctly prevent stronger causal or behavioral claims.

### Paper if judged as an empirical-model-results paper: **5.5 / 10**

This lower score is intentional and honest. There are no provider-model observations, no empirical manipulation check, no frozen model snapshots, and no completed human construct-validation result. Do not market this version as evidence that models choose or benefit from verifiable plans. A later preregistered empirical paper could be much stronger without changing the benchmark contribution.

## Textual integrity / plagiarism

**Finding: no serious concern found, with a hard scope limit.** The audit searched distinctive phrases publicly, compared related-work descriptions against primary sources, reviewed local n-gram/sentence evidence, and checked for copied-looking passages, voice discontinuities, uncited titles, and source-specific claims. The overlap observed is expected bibliography, paper titles, method names, identifiers, and standard technical terminology. No distinctive multi-sentence passage was found verbatim in the public checks.

No honest plagiarism percentage can be produced from this evidence. A similarity percentage is corpus- and settings-dependent, and similarity is not the same as plagiarism. Before submission, run the exact final PDF through iThenticate, Turnitin, or the institutionally approved equivalent if access exists. Manually classify every match; do not optimize blindly for a low number or rewrite standard/cited terminology merely to defeat a detector.

## arXiv readiness and approval confidence

**Technical submission readiness: 9 / 10.** The PDF and source archive compile, the ancillary artifact is screened, citations resolve, fonts embed, metadata is present, and the scope is explicit.

**Estimated arXiv moderation approval confidence: 80–90%, conditional on correct category, endorsement, rights, and author metadata.** This is a judgment, not a guarantee. The manuscript is scholarly, self-contained, cited, technically substantive, and transparent about its non-empirical scope. The main moderation risk is not formatting; it is whether a moderator views a benchmark/protocol release without model results or completed human validation as sufficiently substantive for the selected category. A suitable category and a restrained abstract materially reduce that risk.

arXiv approval is not peer-review acceptance. For a competitive conference or journal, confidence is substantially lower until human validation and a preregistered multi-model study are complete. Do not conflate repository quality with evidentiary strength.

## Required author actions before arXiv submission

1. Read the exact final eight-page PDF line by line. Confirm author name, affiliation, monitored email, acknowledgments, author contributions, ethics language, and AI-assistance disclosure.
2. Confirm that every sentence describing prior work is supported by the cited primary source. The current citation audit is strong, but the named author owns the final characterization.
3. Run the exact final PDF through an approved similarity service if available and review matches in context. Retain the service/date/settings report privately.
4. Choose the arXiv category and distribution license, verify endorsement eligibility, accept the submission agreement personally, and enter title/abstract metadata exactly as shown in the PDF.
5. Upload `output/proofpath_arxiv_source.tar.gz`, inspect arXiv's compiled preview page by page, verify the ancillary archive appears, and resolve any platform warning before finalizing.
6. Confirm the configured repository and project URLs are correct after the first push and Pages deployment; rerun `make release` if either URL changes.
7. After an arXiv identifier exists, add only the identifier to `docs/site-config.js` and the canonical citation metadata, regenerate the release, and verify the website link/BibTeX. Do not guess an identifier beforehand.
8. If the site is launched before an arXiv ID exists, the current build is safe: it omits that CTA and does not fabricate an identifier.

## What the author should review from their side

- **Scientific ownership:** Can you defend the exact distinction among tool-visible response, authoritative state, and evaluator trace without relying on implementation jargon?
- **Claim discipline:** Search the PDF and website for “shows,” “demonstrates,” “improves,” and “models.” Confirm none implies observed provider behavior.
- **Scenario face validity:** Manually sample scenarios from every domain, including both severities, all evidence mechanisms, and long/awkward goals. Confirm both plans really pursue the same postcondition.
- **Failure semantics:** Read the nine appendix definitions and check that timeout-before, timeout-after, partial update, stale readback, delayed visibility, wrong target, and duplicate effect match the intended real-world analogies.
- **Human protocol:** Decide whether to run the two-reviewer protocol before arXiv. It is not required for the honestly labeled methods release, but completing it would remove the largest construct-validity weakness.
- **Future empirical boundary:** Do not run provider experiments until model snapshots, manipulation checks, preregistration, reviewer gates, and unique run directories are complete. The pre-pilot command correctly reports the current ineligibility.
- **Power interpretation:** Treat premium and interaction estimates as pilot targets, not confirmatory evidence. Do not turn simulated power into an observed result.
- **Authorship and disclosure:** Ensure the AI-assistance statement exactly matches actual use and that every author/contributor agrees with it.
- **Visual inspection:** Open the final PDF and hosted site yourself on a phone and desktop. Check the title page, figure labels, bibliography, downloads, citation copy, and the public source link after configuration.
- **Repository launch:** Add a real Git remote, commit the intended public tree, review ignored files, enable Pages from the documented workflow, and inspect the first deployment logs.

## Stop decision

The final rule is satisfied for engineering scope: automated tests pass; no known simulation defect, broken internal link, archive junk, secret/private material, scientific mismatch, major accessibility blocker, or Pages packaging defect remains. Further visual redesign, dependency changes, or speculative polishing would add risk without fixing a demonstrated release problem. Stop modifying the implementation until a real repository URL, production URL, arXiv identifier, human-review result, or empirical study creates new information.
