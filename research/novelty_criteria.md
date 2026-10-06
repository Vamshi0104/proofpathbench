# Formal novelty criteria

## Candidate contribution

ProofPath is not proposed as evidence that agents should verify work. Its candidate contribution is a controlled behavioral measurement:

> Given two or more plans that are matched in nominal ability to attempt the same external-state postcondition, does a tool-using language agent prefer the plan that yields stronger independent evidence of that postcondition, and how does this preference change with verification price, silent-failure probability, and consequence severity?

The unit of analysis is the **plan choice before outcome evidence is observed**, not merely whether a verifier later catches an error.

## Required novelty dimensions

The project remains viable only if the final literature audit supports all of N1–N5:

- **N1 — Matched alternatives:** prior work has not already benchmarked choice among semantically matched action paths whose principal controlled difference is outcome evidence.
- **N2 — Ex-ante selection:** prior work has not already measured whether an agent incorporates independent observability into plan selection before it knows whether the write succeeded.
- **N3 — Price curve:** prior work has not already estimated a verification-selection curve under controlled cost or latency premiums.
- **N4 — Risk interaction:** prior work has not already crossed verification choice with failure probability and consequence severity in a stateful tool environment.
- **N5 — Ground-truth separation:** ProofPath can evaluate both choice and correctness against authoritative state that is independent of tool responses and the agent's completion claim.

N5 alone is not novel; AppWorld, tau-bench, ToolSandbox, AFT-Bench, and other environments already use state-based evaluation.

## Equivalence test for a NO-GO

Issue a **NO-GO** if a verified prior work includes all of the following:

1. language-model agents with external-state-changing tools;
2. at least two nominally viable plans for the same semantic goal;
3. a controlled difference in the independence/authority/freshness/specificity of obtainable postcondition evidence;
4. observation of which plan the agent selects without mandating verification;
5. explicit manipulation of verification cost or latency;
6. authoritative state-based evaluation under silent or ambiguous failures.

Substantial overlap on only items 3 and 6 is a **MODIFY** signal, not automatically a NO-GO.

## Claims that are out of scope

ProofPath must not claim novelty for:

- detecting silent tool errors;
- postcondition checks;
- state-based agent evaluation;
- transaction IDs, status handles, retries, or idempotency;
- verification-aware tool wrappers;
- generic agent or trace observability;
- runtime monitors or safety guardrails.

## Falsification criteria for the project

Even if the literature gap survives, recommend NO-GO after the pilot if any of the following holds:

- plan pairs are not judged semantically matched by blinded human reviewers;
- tool naming, plan length, or prompt wording predicts choices more strongly than observability treatment;
- models nearly always verify or nearly never verify across all cost/risk cells, leaving no estimable trade-off;
- the manipulation check fails: agents cannot distinguish the evidence strength offered by the plans;
- the estimated selection effect is negligible and confidence intervals exclude the smallest effect size of interest;
- authoritative evaluation cannot reliably distinguish intended success, collateral change, partial success, and false completion.

## Terminology boundary

Use **outcome verifiability** for the task-relative availability of evidence that can support or refute a postcondition. Use **agent observability** only for telemetry about the agent itself. This avoids collision with AgentOps and systems-observability literature.
