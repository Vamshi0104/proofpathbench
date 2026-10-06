# Blinded benchmark-review packet

Send `review_items.jsonl`, the instructions below, and a private copy of
`review_form_template.csv` to each of two reviewers. Do **not** send
`tmp/human_validation_private/review_key.json`. The private key is gitignored and must be
kept out of the public repository and ancillary archive.

For every item, reviewers independently record:

- `semantic_equivalent`: `yes`, `no`, or `uncertain` — whether the fixed candidates
  attempt the same task outcome and differ only by read/status evidence operations;
- `stronger_evidence_candidate`: `X`, `Y`, `equal`, `incomparable`, or `uncertain`;
- `wording_bias_candidate`: `none`, `X`, `Y`, or `uncertain` — whether wording or naming
  normatively suggests a preferred candidate beyond its functional description;
- concise notes, especially for any non-`yes`, `equal`, `incomparable`, `uncertain`, or
  wording-bias response.

Reviewers must work independently. Copy their completed files to paths outside this
template directory, then run:

```bash
python -m proofpath.review adjudicate \
  --reviewer-1 PATH/TO/reviewer_1.csv \
  --reviewer-2 PATH/TO/reviewer_2.csv \
  --output research/human_review_report.json
```

Any item not unanimously accepted requires documented adjudication and regeneration or
exclusion before the manipulation check.
