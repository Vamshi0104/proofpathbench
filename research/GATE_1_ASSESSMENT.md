# Gate 1 — related work and novelty assessment

**Date:** 2026-09-28  
**Recommendation:** **MODIFY**  
**Implementation status:** paused pending human review.

## Decision

The broad project framing—“agents should plan for verifiable outcomes”—is too close to recent work to support a defensible novelty claim. In particular:

- AFT-Bench treats postcondition verification as a controlled interface mechanism, evaluates against persistent world state, injects relevant failures, and measures incorrect terminal claims.
- Verified Tool Calls introduces postcondition verification, verify-before-retry, and idempotency under non-atomic failures.
- ToolGate uses explicit pre/postconditions to gate state updates.
- Agent-First Tool API includes a verify phase in its semantic protocol.
- Tools Fail, ToolMaze, SilentProbe, Failing Tools, and the false-success study all expose adjacent failures of tool-result trust and recovery.

However, in the verified sources reviewed, these works do **not** appear to make the central dependent variable the agent's ex-ante selection among nominally equivalent plans as the price of independently observable evidence is varied. They generally test interface treatments, mandatory wrappers, recovery after failure, or post-hoc outcome classification.

## Required modification

Proceed only with this narrower positioning:

> ProofPathBench is a behavioral benchmark of verification demand: it estimates whether and how much tool-using agents are willing to pay—in calls, latency, or simulated cost—for independently observable evidence of an external-state postcondition, under controlled risk and consequence severity.

The proposed planner must be secondary. First establish whether a behavioral gap exists. Do not claim novelty for the wrapper, verifier, failure taxonomy, authoritative state, or state-based evaluation.

## Conditions for GO at Gate 1

Human approval should require all of the following:

1. accept the narrowed “verification demand / plan-selection” contribution;
2. approve the operational definition and anti-confound requirements in the benchmark specification;
3. agree that the next phase is implementation of only the benchmark core and deterministic manipulation checks;
4. require another citation search immediately before pilot freeze;
5. add AFT-Bench and Verified Tool Calls as explicit baselines or comparison points, not merely citations.

## Conditions for NO-GO

Stop if deeper full-text review finds a benchmark that already crosses matched plan alternatives, evidence independence, verification premium, failure risk, and state-based outcomes, or if the proposed pairs cannot isolate observability from ordinary plan length/safety/reliability cues.

## Human decision requested

Approve, revise, or reject the narrowed contribution before Phase 3 implementation begins.
