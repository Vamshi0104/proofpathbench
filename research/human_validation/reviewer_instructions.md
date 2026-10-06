# Reviewer instructions

You are comparing two fixed action plans, X and Y. Judge the plans as written; do not execute them and do not guess what the researchers prefer.

For each row in your copy of `review_form.csv`, find the same `review_id` in `sampled_items.json` and complete every field. Use one stable reviewer ID in every row.

Equivalence fields use `yes`, `no`, or `uncertain`. Rate each candidate on independence, authority, specificity, freshness, linkage, and coverage using `none`, `weak`, `strong`, or `uncertain`. These ratings concern evidence that the requested external state actually holds, not whether the write call merely reported success.

For `evidence_dominant_candidate`, enter `X`, `Y`, `equal`, `incomparable`, or `uncertain`. Dominance means at least as strong on all six evidence dimensions and stronger on at least one. `presentation_bias` is `none`, `X`, `Y`, `both`, or `uncertain`; use it when wording, aliases, ordering, or formatting favor a candidate for reasons unrelated to the underlying plan. `intended_answer_guess` is `X`, `Y`, or `cannot_tell`; this is a blinding check, not an evidence judgment. `guess_confidence` is `low`, `medium`, `high`, or `uncertain`. `severity_plausibility` is `plausible`, `implausible`, or `uncertain`.

Work independently. Do not open the manuscript, repository scenarios, source code, or `blinding_manifest.json`. Do not discuss items with the other reviewer. Put concise reasons, ambiguities, or defects in `concerns`. Return only your completed CSV to the coordinator.
