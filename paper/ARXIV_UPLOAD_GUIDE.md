# arXiv upload guide for ProofPathBench

This is a project-specific operational guide, not a guarantee of acceptance. arXiv
moderation is distinct from peer review and may reclassify, delay, or decline a work.

## 1. Finalize the paper locally

1. Edit only the canonical manuscript, `paper/main.tex`.
2. Verify the complete, accurate author information. The named author must consent to
   submission; do not list an AI system as an author.
3. Keep the existing Generative-AI Assistance Disclosure unless the named authors revise
   it to more accurately describe the assistance used.
4. Run `make release` from the repository root.
5. Inspect all PNG pages under `tmp/pdfs/final/` and the final PDF at
   `output/pdf/proofpath_benchmark.pdf`.
6. If available, run the final PDF through an institutional similarity service and
   review every match manually.

The upload file is `output/proofpath_arxiv_source.tar.gz`. It contains only the top-level
TeX source, generated `.bbl`, bibliography database, PDF figures, generated table inputs,
and the sanitized `anc/proofpath_artifact.tar.gz` ancillary archive.

## 2. Prepare the arXiv account

1. Register or sign in at arXiv and keep the account's name and affiliation accurate.
2. Connect ORCID if desired.
3. Confirm endorsement for the intended category. A first submission, or a first
   submission to a new category, may require endorsement. Starting a submission exposes
   the endorsement workflow when it applies.

## 3. Start and upload

1. From the arXiv user page, choose **START NEW SUBMISSION**.
2. Choose the license only after checking funder, institution, and intended-journal
   requirements. The selected license is irrevocable for that version.
3. At **Add Files / Prepare Files**, upload
   `output/proofpath_arxiv_source.tar.gz`.
4. Choose/check **PDFLaTeX** and confirm `main.tex` is the top-level file.
5. Review arXiv's deletion suggestions. The `anc/` directory is intentional; confirm
   that `anc/proofpath_artifact.tar.gz` remains recognized as ancillary material.
6. Continue only after compilation succeeds. Read the compilation log and open the
   generated PDF. Check every page, figure, reference, hyperlink, heading,
   author details, and the AI-assistance disclosure.

## 4. Enter metadata

- **Title:** `ProofPathBench: A Benchmark for Verifiability-Aware Planning by Tool-Using Language Agents`
- **Authors:** `Vamshi Krishna Madhavan (Independent Researcher)`. The metadata must
  agree with the PDF; the correspondence email is `vamshi-madhavan@outlook.com`.
- **Abstract:** paste the final abstract from the PDF as ASCII/TeX-safe text. Do not copy
  ligatures, curly quotation marks, or Unicode dashes from a PDF viewer.
- **Comments:** after the final local build, a suitable factual pattern is `[page count]
  pages, 2 figures; benchmark and deterministic validation artifact; no behavioral model
  results; source: https://github.com/Vamshi0104/proofpathbench; project page:
  https://vamshi0104.github.io/proofpathbench/.`
- **Primary category:** `cs.AI` is the current best-fit recommendation.
- **Cross-list:** `cs.SE` is the strongest optional cross-list. Use `cs.CL` only if the
  named authors can justify a computation-and-language contribution.
- **Journal reference / DOI:** leave blank unless the same work is already published and
  the supplied metadata is accurate.

## 5. Final review and submission

1. Verify title, author ordering, affiliations, abstract, categories, comments, license,
   and every processed file.
2. Confirm all authors approve the exact submitted version.
3. Select **Submit Article** only after reviewing arXiv's generated PDF.
4. If an error is found before public announcement, use **Unsubmit**, correct the source,
   run `make release` again, replace the files, and resubmit. Do not create a second new
   submission for a correction.
5. Monitor email and the arXiv dashboard for processing, moderation, or required-action
   messages; timing depends on the submission and announcement schedule.
