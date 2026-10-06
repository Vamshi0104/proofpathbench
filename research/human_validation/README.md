# Blinded human validation package

This package is ready for two independent reviewers. No review has been run and no human-validation result is claimed.

Give each reviewer only `sampled_items.json`, `review_form.csv`, and `reviewer_instructions.md`. Make a separate copy of the CSV for each reviewer. Do **not** give reviewers `blinding_manifest.json`, the scenario manifests, or the manuscript before they finish.

Generate the committed public packet reproducibly. The private answer key is written to
the ignored `tmp/` tree by default; move it to access-controlled storage before sharing
the public repository:

```bash
python3 research/human_validation/analyze_reviews.py generate --seed 20261006
```

After both reviewers return complete files, keep their originals read-only and run:

```bash
python3 research/human_validation/analyze_reviews.py analyze \
  --reviewer-1 PATH/reviewer_1.csv \
  --reviewer-2 PATH/reviewer_2.csv \
  --manifest tmp/human_validation_private/blinding_manifest.json \
  --output PATH/human_validation_report.json
```

The private manifest is gitignored and excluded from the public ancillary archive. Follow
`protocol.md` and `analysis_plan.md` for recruitment, independence, adjudication, and
interpretation.
