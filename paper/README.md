# Paper

This directory contains a complete, compilable **benchmark and validation manuscript**.
It is not an empirical agent-results paper. The manuscript reports the implemented
benchmark, deterministic software validation, and prospective evaluation sizing; it does
not present behavioral model outcomes.

From the repository root, rebuild the generated tables, vector figures, and local PDF:

```bash
make draft
```

After verifying the author metadata in `paper/main.tex`, create the validated PDF,
clean source archive, bibliography output, ancillary package, and website downloads with:

```bash
make release
```

The release target runs the test, lint, type-check, deterministic benchmark, LaTeX-log,
clean-source compilation, page-count, and extracted-text gates. It also renders every
final PDF page to `tmp/pdfs/final/` for mandatory visual inspection. Upload
`output/proofpath_arxiv_source.tar.gz`; do not upload the development repository.

Before public submission, a human author must supply genuine author metadata, review
every claim and citation, and follow `ARXIV_SUBMISSION_CHECKLIST.md` and
`ARXIV_UPLOAD_GUIDE.md`.
