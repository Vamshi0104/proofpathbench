# Research questions

These questions are preregistration targets, not claims.

## Primary questions

**RQ1 — Selection.** When nominal task capability is held constant, do current tool-using language agents preferentially select plans that can produce stronger independent evidence of the requested external-state postcondition?

**RQ2 — Verification premium.** How does verifiable-plan selection change as the additional simulated monetary cost, tool-call count, or latency of obtaining evidence increases?

**RQ3 — Failure risk.** How does selection change when the disclosed probability of a silent or ambiguous tool failure increases?

**RQ4 — Consequence severity.** Does the magnitude of a simulated, task-grounded consequence change willingness to pay a verification premium?

**RQ5 — Reliability intervention.** After the baseline behavior is established, does an explicitly verifiability-aware planning policy improve authoritative-state task success and reduce false completion under unreliable execution?

**RQ6 — Frontier.** What empirical frontier relates verification expenditure to verified task success, false completion, and recovery?

## Secondary questions

**RQ7 — Evidence quality.** How do source independence, authority, freshness, specificity, deterministic linkage, and semantic coverage separately affect selection?

**RQ8 — Verification noise.** Do agents adjust appropriately when readback can be stale, delayed, or noisy?

**RQ9 — Calibration.** When evidence is unavailable or conflicting, do agents communicate residual uncertainty rather than assert completion?

**RQ10 — Generality.** Which effects replicate across domains, model families, prompt paraphrases, and counterbalanced tool order/names?

## Confirmatory boundary

The pilot has two confirmatory tests: the RQ1 zero-premium vanilla contrast (H1) and the
instruction contrast within RQ1 (H2). RQ2--RQ4 are directional estimation targets in the
pilot, not confirmatory tests. RQ5--RQ10 remain secondary or later-phase questions until
the baseline phenomenon and benchmark validity pass Gate 3.
