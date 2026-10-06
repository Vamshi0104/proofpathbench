# Gate 2 amendment — split-plot verification premium

**Decision:** APPROVED by the human author on 2026-09-28 as part of the current Gate 2
package. No empirical model responses were collected before approval.

## Why the approved assignment needed revision

The approved 96-task design assigned each task to only one of 24 premium × risk × severity
cells, leaving four independent tasks per cell. A prospective 10,000-replicate simulation
found that repeated prompt calls did not repair the task-level limitation: under the stated
moderate log-odds effects, estimated power was only about 6–10% for the premium and
interaction coefficients in the original between-task assignment.

This was detected before preregistration and before any eligible model response. Fixture
outputs in `results/raw/*smoke*` are explicitly marked non-empirical.

## Proposed amendment

- Keep the same 96 task archetypes, risk assignment, concrete severity assignment,
  evidence mechanism, and hidden dominant-plan label.
- Present **all four premiums within every task** (`1.00, 1.10, 1.50, 2.00`).
- Rotate the four existing presentation variants over the four premiums with a Latin-style
  deterministic assignment. Across tasks, every premium receives every presentation 24
  times.
- This creates 384 task-treatment units and 16 independent tasks in every one of the 24
  premium × risk × severity cells.
- One call per unit, instruction condition, and model gives the same total as the reduced
  budget: `96 × 4 premiums × 2 instructions × 3 models = 2,304` calls.

The static validator confirms 384 units, four premiums per task, 16 units per treatment
cell, and 96 uses of every presentation variant. Runtime validation executes both plans in
all 384 units without faults (768 executions).

## What the amendment does and does not solve

The split plot makes the premium curve a within-task contrast and improves estimated power.
After limiting the confirmatory pilot family to adequately motivated H1--H2, the updated
prospective approximation at one call per task-treatment/instruction/model estimates:

- premium main effect: 0.484;
- premium × risk: 0.290;
- premium × severity: 0.377.

These are still below conventional confirmatory power for the assumed moderate effects.
Additional repetitions improve call-level precision but do not create new task archetypes;
at three repetitions the estimates are approximately 0.909, 0.671, and 0.802.

Therefore the recommended scientific interpretation is:

1. use the pilot for construct validation, manipulation checks, variance estimation, and
   the Gate 3 GO/MODIFY/NO-GO decision;
2. avoid definitive H3–H5 claims from the pilot;
3. use blinded pilot variance estimates—not observed effect optimization—to power the
   larger confirmatory experiment after Gate 3.

## Approval meaning

Approval authorizes the split-plot design for the pilot. It does not authorize external
API spending, waive the two-reviewer requirement, freeze model snapshots, or treat the
underpowered pilot interactions as confirmatory findings.
