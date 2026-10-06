# arXiv submission checklist

The source package compiles, but it is not automatically approved or endorsed by arXiv.
The submitter remains responsible for authorship, subject classification, rights, and
scientific claims.

Official references checked on 2026-10-06: [submission
guidelines](https://info.arxiv.org/help/submit/index.html), [TeX submission
guidance](https://info.arxiv.org/help/submit_tex.html), and [content
moderation](https://info.arxiv.org/help/moderation/index.html).

## Step-by-step submission

1. Update `paper/main.tex` with final author, affiliation, email, date, acknowledgments,
   and any public repository/DOI. Update `CITATION.cff` to match.
2. From the repository root, run `make release`. Do not continue unless every check and
   clean-source compilation passes.
3. Read `output/pdf/proofpath_benchmark.pdf` page by page. Confirm the author metadata,
   figures, tables, links, bibliography, AI disclosure, and statement that human and
   provider-model results have not been run.
4. Inspect the members of `output/proofpath_arxiv_source.tar.gz`. This is the single
   upload file. It contains `main.tex`, `main.bbl`, `references.bib`, the required PDF
   figures and generated tables, plus `anc/proofpath_artifact.tar.gz`.
5. Sign in to the author's arXiv account and verify any endorsement requirement for the
   chosen category. Start a new submission from the user page.
6. Upload `output/proofpath_arxiv_source.tar.gz`, select the detected PDFLaTeX processor,
   and confirm that `main.tex` is the only top-level TeX file. Review every automatic
   deletion note before accepting it.
7. Open arXiv's compiled preview and compilation log. Compare the preview with the local
   final PDF; inspect every page and confirm the ancillary archive is listed.
8. Enter metadata manually: exact title, author order, abstract, comments, report number
   if applicable, primary category, cross-list category if justified, and license. Do not
   paste LaTeX commands that arXiv metadata does not support.
9. Recheck the abstract and title against the PDF, accept the submittal agreement
   personally, and submit. Save the submission identifier and status message.
10. Monitor the submission status. Moderation is discretionary; a successful local build
    is not an approval guarantee. If a correctable error is found before announcement,
    use arXiv's **Unsubmit** action, correct the source, rebuild, and resubmit. After
    announcement, use the replacement/version workflow rather than creating a duplicate.

## Exact files required

Use only `output/proofpath_arxiv_source.tar.gz` for upload. Its required paper members are
`main.tex`, `main.bbl`, `references.bib`, `figures/proofpath_architecture.pdf`,
`figures/prospective_power.pdf`, the generated files under `tables/`, and
`anc/proofpath_artifact.tar.gz`. Do not upload `paper/main.pdf`, LaTeX logs/auxiliary
files, raw model outputs, `.env` files, the development repository, `tmp/human_validation_private/review_key.json`,
or `tmp/human_validation_private/blinding_manifest.json`.

## Required human actions

- [ ] Verify that the author name, affiliation, and monitored email address in the PDF
  are complete and accurate.
- [ ] Confirm that the named author made the stated contribution and approved the exact
  generated PDF.
- [ ] Read the entire PDF and rewrite or correct any passage that does not represent the
  author's own scientific judgment.
- [ ] Keep the title and abstract explicit that this is an implemented benchmark with
  deterministic validation and no behavioral model results.
- [ ] Verify every bibliography record against the primary source and re-run the citation
  audit immediately before submission.
- [ ] Run an institutional similarity checker if one is available; inspect matches
  manually. Do not advertise a literal “0% plagiarism” guarantee.
- [ ] Disclose AI assistance according to the applicable institutional, venue, and arXiv
  policies.
- [ ] Choose the subject category. `cs.AI` is a plausible primary category and `cs.SE`
  is the strongest cross-list candidate given the closest verified work. Use `cs.CL`
  only if the author can justify a computation-and-language contribution. This remains a
  human classification decision.
- [ ] Confirm that `https://github.com/Vamshi0104/proofpathbench` remains public and that
  it contains no secret, private path, API key, evaluator-only review key, or unintended
  raw data.
- [ ] Confirm that the public artifact contains the benchmark manifests, schema,
  deterministic validation report, code, tests, configuration, and license claimed by
  the manuscript.
- [ ] Confirm the license selection and that all included material may be redistributed.
- [ ] Upload `output/proofpath_arxiv_source.tar.gz`, not local build products or the
  entire development repository.
- [ ] Keep `paper/arxiv/anc/proofpath_artifact.tar.gz` in the submission package and
  confirm that arXiv lists it as ancillary material during the Add Files step.
- [ ] Inspect arXiv's generated PDF for font, figure, hyperlink, and bibliography issues.
- [ ] Confirm that the arXiv metadata and PDF show exactly the same author names and
  ordering, and that every affiliation is accurate and current.
- [ ] Confirm that endorsement is active for the chosen primary category before relying
  on a planned announcement date.
- [ ] Read and accept the submittal agreement personally; do not delegate the authorship,
  rights, or license attestations.
- [ ] Do not add empirical results unless the prospective review, registration, manipulation check,
  pilot, analysis, and human gates are actually completed.

## Local clean-build command

After editing the canonical `paper/main.tex`, run from the repository root:

```bash
make release
```

This command rejects the author placeholder, rebuilds the generated assets, runs the
software and manuscript checks, compiles the source in a fresh directory, creates
`output/proofpath_arxiv_source.tar.gz`, and renders every final page under
`tmp/pdfs/final/`. Inspect those PNGs and then inspect arXiv's generated preview PDF.
