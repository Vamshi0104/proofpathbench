# Moderation-readiness audit

This audit tracks controllable risks under arXiv's published submission and moderation
rules. It is not a prediction or guarantee of a moderator's discretionary decision.

## Controls currently passing

- **Scholarly form:** the manuscript has a conventional abstract, problem formulation,
  related work, implemented method, deterministic validation, limitations, ethics,
  conclusion, references, and technical appendices.
- **Substantive contribution:** the release is an implemented 96-scenario benchmark with
  typed manifests, executable mock environments, nine injected failure classes,
  automated tests, an evaluator, and analysis code. It is not presented as a proposal.
- **Claim discipline:** simulated power is identified as prospective; fixtures are marked
  non-empirical; the paper explicitly states that no language-model behavioral result is
  reported.
- **Originality language:** the novelty statement is bounded to a documented structured
  review and does not claim universal priority.
- **Category fit:** `cs.AI` is the strongest primary fit because the work concerns AI
  planning and uncertainty. `cs.SE` is a defensible optional cross-list because the
  artifact centers on testing, failure injection, reliability metrics, and reproducible
  software evaluation. `cs.CL` is not recommended without a stronger NLP contribution.
- **Attribution:** related-work claims are cited, bibliography records were checked
  against primary records, the submission-readiness search was refreshed on 2026-10-05,
  and the final LaTeX build has no undefined citations.
- **AI disclosure:** the manuscript reports assistance with software, literature-search
  support, manuscript drafting/editing, and figure layout; no AI system is an author;
  responsibility remains with the named human authors.
- **Technical format:** PDFLaTeX compilation succeeds; figures are included as PDF;
  headings, tables, captions, and references were visually reviewed; fonts are embedded;
  and no overfull boxes or unresolved references remain.
- **Source hygiene:** the upload archive contains only required TeX, bibliography,
  figures, generated tables, and a sanitized ancillary archive. Raw results, review keys,
  secrets, local paths, and build products are excluded.
- **Reproducibility:** `make release` runs tests, linting, strict typing, deterministic
  validation, clean-source compilation, archive checks, page-count and extracted-text
  comparison, font checks, and page rendering.

## Human-controlled blockers before upload

- Verify the listed human authorship, affiliation, and contact metadata before submission.
- Confirm that the named author approves the exact generated PDF.
- Confirm that account identity and affiliation are accurate and that category
  endorsement is active.
- Choose an irrevocable license after checking institution, funder, and intended-journal
  requirements.
- Run the final named-author PDF through an institutional similarity service if one is
  available and review every match in context.
- Select categories and enter metadata; the form data must match the PDF.
- Review arXiv's own compilation log and generated PDF before selecting Submit Article.

## Residual risks that cannot be automated away

- A moderator may disagree about significance, originality, category, or community fit.
- A private-corpus similarity service may identify material unavailable to public-web
  searches.
- Endorsement, rights, affiliation, license, and author-consent facts cannot be inferred
  from repository files.
- arXiv may change its processing environment or policies after this audit.
