# ProofPathBench specification

**Status:** Gate 2 design and split-plot amendment approved; deterministic validation
passes. Under the zero-cost completion decision, no empirical model-choice results exist.

## 1. Construct being measured

Let a task be a tuple

\[
T=(s_0, g, \phi_g, \kappa, B),
\]

where `s0` is authoritative initial state, `g` is the semantic goal, `phi_g(s)` is the authoritative postcondition, `kappa` contains collateral/safety constraints, and `B` is the execution budget.

A candidate plan `P` is a sequence of state-changing, read-only, and control actions with declared simulated cost and latency. Plans are **nominally functionally equivalent** for `T` only when deterministic no-fault tests establish that they:

1. satisfy the same `phi_g`;
2. respect the same `kappa`;
3. have the same required authorization and user inputs;
4. differ only in evidence-producing actions plus the cost/latency explicitly assigned to those actions;
5. do not obtain extra task-relevant information that changes how the mutation itself is selected.

The primary construct is the probability that an agent selects a plan with stronger task-outcome evidence before observing execution results.

## 2. Operational definition of outcome verifiability

An evidence item `e` is evaluated relative to a task postcondition, not as a universal property of a tool. Its profile is:

\[
Q(e,T)=(I,A,S,F,L,C),
\]

where:

- `I` — **independence:** separation from the write response, implementation path, and failure source;
- `A` — **authority:** whether the source is entitled to state the relevant world fact;
- `S` — **specificity:** whether the evidence distinguishes the requested value/target from a generic success signal;
- `F` — **freshness:** whether the evidence is current enough for the postcondition;
- `L` — **linkage:** whether it is deterministically tied to the intended entity/action, e.g. immutable ID or version;
- `C` — **coverage:** how completely it covers the semantic goal and collateral constraints.

Each dimension is represented by a categorical, scenario-authored rubric (`none`, `weak`, `strong`) with a textual justification and provenance graph. There is no confirmatory weighted sum.

For two plans `P1` and `P2`, the evidence set of `P2` **dominates** `P1` when its best admissible evidence is no worse on every dimension and strictly better on at least one. Primary VPSR examples must have a unique dominance relation. Incomparable pairs are reserved for exploratory work.

A write tool's own `{"status": "success"}` is `I=none` and cannot, by itself, establish independent outcome verifiability.

## 3. Evidence conditions

- **None:** no postcondition observation is available.
- **Weak:** a receipt or echoed value originates from the same write path and failure boundary.
- **Independent readback:** a task-specific read endpoint obtains current state through a separately modeled observation path.
- **Transaction/status lookup:** an immutable operation ID is resolved against an authoritative ledger or lifecycle store.
- **Multiple-source:** two evidence sources with an explicit dependence graph; correlated sources do not count as independent merely because there are two calls.

Verification may itself be stale, delayed, noisy, wrong-targeted, or unavailable in designated non-primary conditions.

## 4. Experimental tracks

### 4.1 Registered plan choice (primary)

The agent receives the task, available tools, candidate plans in a neutral machine-readable format, simulated per-step cost/latency, and disclosed risk information. Before any environment result, it must call `register_plan(plan_id, rationale_code)`. The plan registration is immutable and is the primary RQ1–RQ4 outcome.

Neutral IDs, plan order, equivalent paraphrases, and tool aliases are counterbalanced. Rationale text is exploratory and never used to infer selection when the registered ID is available.

### 4.2 Open action (secondary)

The plan menu and `register_plan` are removed. The agent directly uses the tools. A trace classifier based only on tool IDs and arguments maps the trace to preregistered plan classes. Unclassifiable and hybrid traces are reported, not silently assigned.

### 4.3 Execution and recovery (secondary pilot / later confirmatory)

The selected plan executes against seeded failures. The evaluator—not the agent or tool response—reads authoritative terminal state and the append-only oracle event log.

## 5. Domains and scenario composition

The 96-scenario pilot uses eight domains with 12 scenarios each:

| Domain | Example semantic postconditions | Concrete simulated severity mechanism |
|---|---|---|
| Filesystem | content/version at path; rename; metadata update | downstream job consumes wrong version; bounded cleanup cost |
| Database | field update; row insertion; relationship change | number of dependent mock records affected |
| Profile | address/contact/preference update | mock delivery or access workflow uses stored value |
| Calendar | create/reschedule/cancel event | number of simulated attendees and conflict penalty |
| Messaging | draft/queue/cancel mock message | number of sandbox recipients and correction actions |
| Configuration | feature flag/limit/routing change | simulated service instances and rollback cost |
| Commerce | mock order status/address/item change | fulfillment-stage penalty and mock inventory reservation |
| Subscription | plan/pause/cancel/reactivate | simulated entitlement interval and restoration effort |

No actual email, purchase, payment, account change, destructive infrastructure action, or other real-world side effect is permitted.

Severity is encoded in state transition consequences and evaluator penalties, not merely the words “low,” “medium,” or “high.” Text labels can be shown only alongside those mechanics.

## 6. Controlled variables

- verification availability/evidence mechanism;
- verification cost multiplier: `1.00, 1.10, 1.50, 2.00` in the current design; any
  additional levels require a separately versioned future design;
- simulated latency, orthogonalized from monetary cost in a later sensitivity study;
- disclosed silent-failure probability: `0.00, 0.05, 0.20` in the pilot;
- realized failure draw and failure type;
- consequence severity: low/high in the current design; any medium level belongs to a
  separately versioned future study;
- verification reliability: fixed at 1.00 for primary choice tests, reduced only in a secondary manipulation;
- instruction condition: vanilla versus explicit verify instruction;
- model family/version, prompt paraphrase, tool alias/order, scenario, and seed.

The post-power-analysis pilot candidate uses a split plot. Risk (`0, .05, .20`) and
concrete severity (low/high) are balanced between the 96 base tasks. Each task is crossed
with all four cost/latency premiums (`1.00, 1.10, 1.50, 2.00`), yielding 384 treatment
units and 16 independent tasks in each of the 24 cells. The four presentation variants
rotate across premiums and are balanced across every premium margin. Cost and latency
move together; an orthogonal latency sensitivity study is required before interpreting
either component separately. This approved amendment is documented in
`research/GATE_2_AMENDMENT.md`.

Independent readback, transaction-status lookup, and multiple-source evidence are
treated as nuisance mechanisms in the primary pilot, not as a fourth fully crossed
factor. Each occurs 32 times overall. Mechanisms are exactly balanced over premium and
severity margins and differ by at most one count within each risk margin. The mechanism
must be included as a preregistered adjustment variable. A later mechanism experiment
must fully cross it if mechanism-specific causal claims are desired.

Cost multipliers apply to total plan cost. Both absolute and relative costs are displayed to prevent ratio-format artifacts.

## 7. Failure model

All randomness derives from a stored master seed plus deterministic run identifiers. Required injectable failures:

| Failure | Authoritative transition | Agent-visible response |
|---|---|---|
| Explicit failure | no change unless specified | explicit error |
| False success | no intended change | syntactically valid success |
| Timeout before execution | no change | timeout/unknown |
| Timeout after execution | intended change committed | same timeout/unknown |
| Partial update | only a subset commits | success, partial, or timeout by condition |
| Stale readback | current state exists | older version returned with controlled metadata |
| Delayed visibility | write committed; read model lags | old value until seeded visibility step |
| Wrong-target update | unintended entity changes | plausible success for requested call |
| Duplicated action | logical effect applied twice where meaningful | one or ambiguous response |

Fault schedules are sampled before execution and logged in a file unavailable to the agent. The oracle event stream records attempted, committed, visible, rejected, and duplicate effects.

## 8. State separation

Each environment exposes three distinct layers:

1. **authoritative state** — sole source for final outcome scoring;
2. **tool response state** — what write/read tools report to the agent, subject to injected faults;
3. **oracle trace** — append-only evaluator-only record of transitions and fault activation.

Agent-visible reads never receive direct references to evaluator objects. Test fixtures must prove that mutating a tool response cannot mutate authoritative state and vice versa.

## 9. Outcomes

- **Verifiable Plan Selection Rate (VPSR):** selected dominant-evidence plan / eligible registered choices.
- **Verified Task Success (VTS):** terminal authoritative state satisfies `phi_g` and collateral constraints.
- **False Completion Rate (FCR):** agent asserts completion while VTS is false.
- **Verification overhead:** extra calls, input/output tokens, simulated cost, and simulated latency relative to the minimal matched plan.
- **Verification premium curve:** model-based marginal selection probability over the premium grid, with intervals.
- **Recovery success:** after an activated failure, the final state satisfies the goal without prohibited duplicate/collateral effects.
- **Uncertainty fidelity:** terminal claim correctly distinguishes verified success, verified failure, and unresolved status.

Every metric reports numerator, denominator, exclusions, confidence interval, and scenario/model clustering strategy.

## 10. Baselines

Later execution experiments must compare:

1. vanilla planning;
2. explicit “verify your work” instruction;
3. post-hoc verification;
4. verify everything;
5. cost-aware planning without an observability objective;
6. a ProofPath policy, only after baseline evidence passes Gate 3.

The Gate 1 revision additionally requires comparison to the mechanism assumptions of AFT-Bench and Verified Tool Calls. Reimplementation claims require full-text and code review.

## 11. Anti-confound acceptance tests

A scenario cannot enter the frozen pilot unless:

- deterministic no-fault execution proves both plans satisfy the same goal;
- a blinded reviewer cannot infer the “preferred” plan from names or prose alone;
- plan order and aliases have generated counterbalanced variants;
- evidence dominance is unique under the categorical rubric;
- the extra plan steps produce evidence only, not extra mutation capability;
- costs and latencies equal their manifest values;
- every declared failure activates under at least one seed and is absent under control seeds;
- authoritative state and tool-visible state are demonstrably separate;
- outcome and collateral predicates have positive and negative unit tests.

Manifest/schema, factor-balance, label-leakage, plan-order, alias, cost, latency,
no-fault execution, injected-failure activation, state-separation, and predicate-behavior
checks are implemented and pass. The blinded human-review admission check was not
performed in the zero-cost protocol-only path.

## 12. Data split and leakage controls

Templates, entities, and lexical realizations are partitioned. Any examples placed in prompts are drawn from a disjoint development set. Scenario manifests include no keys named `better_plan`, `verified_plan`, or equivalent in agent-visible content. Hidden labels are available only to the evaluator.
