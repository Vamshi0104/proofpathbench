# Human-validation protocol

## Purpose and status

Two independent human reviewers will assess whether the paired plans pursue the same goal and whether one produces stronger outcome evidence. This is a construct check, not a model-behavior experiment. As of the release date, the protocol is prepared but results are **NOT YET RUN**.

## Sample

The fixed seed `20261006` selects 32 of 96 scenarios: four from each of eight domains. Within each domain, a deterministic greedy rule favors levels that are under-represented in the accumulating sample across verification premium, risk, severity, evidence mechanism, and canonical dominant-plan label. Thirty-two items are sufficient to expose systematic construct and wording defects while keeping two-reviewer workload reasonable; the sample is not claimed to power a population prevalence estimate.

Candidate labels and order are randomized independently of the internal A/B labels. Four presentation variants rotate equally. The public packet omits scenario IDs, evidence profiles, evidence-mechanism labels, canonical dominant labels, and the answer key.

## Reviewers and independence

- Recruit two adults able to read technical task descriptions and reason about state-changing software tools.
- Neither reviewer may have authored the scenarios, seen the answer key, or discuss ratings with the other before both forms are locked.
- Record reviewer qualifications, recruitment date, conflicts, and compensation outside the blinded form.
- Each reviewer completes every item without code execution or access to repository files beyond the three-item reviewer packet.

## Exclusions and missing data

No item or rating is excluded after viewing agreement. A reviewer file with a missing/invalid field, duplicate ID, unknown ID, or incomplete item set fails analysis and must be returned for completion without showing the other review or answer key. A reviewer is replaced only for documented withdrawal, protocol exposure, or inability to complete; retain the reason and the untouched partial file.

## Adjudication and acceptance

After both independent forms are locked, compute agreement as specified in `analysis_plan.md`. List every field disagreement for adjudication by a third qualified person who has not seen the expected labels. Any item fails construct admission if adjudication does not conclude all three equivalence fields are `yes`, identifies one evidence-dominant candidate, and finds no material presentation bias. Failed items must be revised and independently re-reviewed or excluded from a later empirical study. The released 96-item corpus is not silently changed by this protocol.
