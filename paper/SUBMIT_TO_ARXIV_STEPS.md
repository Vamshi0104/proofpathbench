# ProofPathBench: steps to submit to arXiv

Use this checklist for the current eight-page release. The upload package is:

`output/proofpath_arxiv_source.tar.gz`

Do not upload the development repository, the PDF by itself, or the contents of
`paper/arxiv/` one file at a time.

## 1. Complete the human checks

1. Read the complete final PDF at `output/pdf/proofpath_benchmark.pdf`.
2. Confirm that the following details are complete and accurate in both the PDF and the
   arXiv account:
   - author name and ordering;
   - current affiliation;
   - monitored email address; and
   - author consent and contribution statement.
3. Confirm that the submitter has endorsement for the selected category, if arXiv asks
   for it.
4. Choose the arXiv license only after checking any intended journal, funder, or
   institutional requirements. The license selected for an arXiv version is irrevocable.
5. If an institutional Turnitin or iThenticate service is available, check the final PDF
   and review every match in context. Bibliography entries, paper titles, standard
   terminology, formulas, and software names normally produce legitimate similarity.

## 2. Rebuild the final package after any edit

From the repository root, run:

```bash
make release
```

Do not continue unless this command succeeds. It runs the software tests and validation,
rebuilds the figures and tables, compiles the manuscript, checks citations and fonts,
creates a clean ancillary archive, compiles the upload package in a fresh directory, and
renders every page for visual review.

After the command finishes, inspect:

- `output/pdf/proofpath_benchmark.pdf`
- all PNG files under `tmp/pdfs/final/`
- `output/proofpath_arxiv_source.tar.gz`

## 3. Start the arXiv submission

1. Sign in at <https://arxiv.org/>.
2. Open the user page and select **START NEW SUBMISSION**.
3. Read and accept the submission agreement personally.
4. Choose the license selected during the human checks.
5. At **Prepare Files**, upload `output/proofpath_arxiv_source.tar.gz`.
6. Select **Check Files**.
7. Confirm that arXiv detects:
   - processor: **PDFLaTeX**;
   - top-level file: **main.tex**; and
   - ancillary file: **anc/proofpath_artifact.tar.gz**.
8. Review every auto-detected deletion suggestion. Keep the `anc/` archive.
9. Accept and continue only after compilation succeeds.
10. Read the compilation log and open arXiv's generated PDF. Verify all eight pages,
    including the title, author details, equations, tables, both figures, arrow labels,
    headings, references, appendices, and AI-assistance disclosure.

## 4. Enter the metadata

- **Title:** `ProofPathBench: A Benchmark for Verifiability-Aware Planning by Tool-Using Language Agents`
- **Authors:** `Vamshi Krishna Madhavan`
- **Affiliation:** `Independent Researcher`
- **Correspondence email:** `vamshi-madhavan@outlook.com`
- **Abstract:** paste the final abstract from `paper/main.tex`, not from a PDF viewer.
  arXiv metadata fields require ASCII/TeX-safe text.
- **Comments:** `8 pages, 2 figures; benchmark and deterministic validation artifact; no behavioral model results; source: https://github.com/Vamshi0104/proofpathbench; project page: https://vamshi0104.github.io/proofpathbench/.`
- **Primary category:** `cs.AI`
- **Optional cross-list:** `cs.SE`
- **Journal reference and DOI:** leave blank unless this same work has verified publication
  metadata.

The title, author list, author order, affiliation, and abstract entered on the website
must agree with the PDF.

## 5. Submit and monitor

1. Review the metadata, selected category, license, processed files, and generated PDF a
   final time.
2. Select **Submit Article**.
3. Monitor the arXiv dashboard and the author's email for moderation or required-action
   messages.
4. If an error is found before public announcement, use **Unsubmit**, fix
   `paper/main.tex`, run `make release` again, and replace the files. Do not create a
   second submission for a correction.

## Current plagiarism/similarity status

The repository's documented public-source checks found no suspicious copied long-form
prose or exact matches for the distinctive manuscript passages tested. Citations and
bibliographic metadata were also reviewed against primary records. This is good evidence
for submission readiness, but it is not a Turnitin or iThenticate certificate and cannot
produce a defensible universal plagiarism percentage. Private student-paper repositories,
paywalled similarity corpora, translations, and close paraphrases are outside the public
check's coverage.

The manuscript includes a generative-AI assistance disclosure, and the named human author
remains responsible for every claim, citation, and sentence. Do not remove or weaken that
disclosure unless it would make the description more accurate.

## Final decision rule

The package is ready to upload when all of the following are true:

- `make release` passes;
- the author identity, affiliation, and email are accurate;
- the author approves the exact generated PDF;
- the license and category have been chosen;
- endorsement is available if required;
- any available institutional similarity report has been reviewed; and
- arXiv's own compilation log and preview PDF are correct.

Passing these checks cannot guarantee moderation acceptance. arXiv may still reclassify
or decline a submission under its discretionary moderation policy.

## Official arXiv references

- Submission process: <https://info.arxiv.org/help/submit/index.html>
- TeX/PDFLaTeX preparation: <https://info.arxiv.org/help/submit_tex.html>
- Metadata fields: <https://info.arxiv.org/help/prep.html>
- Ancillary files: <https://info.arxiv.org/help/ancillary_files.html>
- Licenses: <https://info.arxiv.org/help/license/index.html>
- Moderation policy: <https://info.arxiv.org/help/moderation/index.html>
