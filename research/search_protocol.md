# Related-work search protocol

**Search date:** 2026-10-06  
**Scope freeze:** Submission-readiness refresh following the Gate 1 snapshot.  
**Primary-source rule:** metadata and substantive claims must be checked against an author-hosted paper page, arXiv, OpenReview, proceedings page, DOI record, or the paper itself. Search snippets are discovery aids only.

## Research question for the search

Has prior work already conducted a controlled evaluation in which a tool-using language agent chooses among otherwise viable plans that differ in independent outcome observability, while verification cost and/or failure risk are experimentally manipulated?

## Concept families

The search covered the prompt's required families and spelling variants:

- verification-aware / verifiable agent planning;
- outcome, postcondition, action, tool-call, and external-state verification;
- verified tool calls and proof-carrying actions;
- false success, false completion, silent tool failure, and ambiguous execution;
- observability-aware planning and agent observability;
- verification cost, budget, strategic verification, and reliability–cost trade-offs;
- reliable tool use, recovery, transactional actions, and state-based evaluation.

## Query log

Queries were issued in combinations against web search with site restrictions for `arxiv.org`, `aclanthology.org`, and `openreview.net`. Representative exact queries:

```text
agent tool use verification external state postcondition verification planning
tool use agents verify outcomes external state
LLM agent verification tool use planning failures
"silent failure" LLM agents tools
LLM agent "verification cost" tools
LLM agent "verification budget"
LLM agent "state verification" risky mutations
LLM agent "postcondition" tools verify
agent chooses verification action cost tradeoff LLM tool
agent strategic verification cost tool calls
observability-aware planning LLM agent tools
"outcome observability" agent planning
"outcome verifiability" agents planning
"verifiability-aware" agent planning
"independent verification" "tool-using agents"
"tool environment unreliability" agent benchmark
"tool selection" bias names descriptions LLM agents
"proxy state" evaluation tool calling agents
"pre-execution" plan verification LLM agents
LLM plan selection execution gap agent
LLM tool command pre-execution verification
```

Backward and forward chaining was then performed from the closest papers, especially *Callability Is Not Operability*, *Verified Tool Calls*, *Tools Fail*, and *ToolGate*. This surfaced schema-first interfaces, transactional runtimes, stateful benchmarks, and false-success studies.

## Inclusion criteria

A work enters the detailed matrix if it satisfies at least two of the following:

1. studies a tool-using language agent that changes or reasons about external state;
2. separates reported/tool-visible status from environment state;
3. studies silent, ambiguous, partial, or non-atomic tool failure;
4. provides postcondition or outcome verification during execution;
5. manipulates an interface, plan, verification mechanism, or execution budget relevant to observable outcomes.

General surveys, ordinary function-calling benchmarks, generic agent observability platforms, answer-verification work, formal verification of neural networks, theorem proving, and safety-only pre-execution guards were excluded unless they directly informed the boundary of the proposed contribution.

## Screening questions

For each included work:

- Is verification performed before, during, or after execution?
- Does the agent choose among functionally equivalent ways to attempt the same external-state goal?
- Is independent outcome observability a property used in plan selection?
- Is the price of verification directly manipulated?
- Are tool responses distinct from authoritative state?
- Does the work test ex-ante planning behavior, post-hoc checking, interface treatment, or runtime recovery?

## Limitations of this search

- This is a structured rapid review, not a completed systematic literature review.
- arXiv contains very recent 2026 work whose review status may change.
- Search-engine indexing can miss terminology that does not use “verification” or “observability.”
- One highly relevant anonymous submission (*Failing Tools*) has incomplete bibliographic metadata and is marked **UNVERIFIED**.
- The October refresh added ToolBench-X, Proxy State-Based Evaluation, ToolTweak,
  VerifyLLM, CARE, ACEBench, TOOLVERIFIER, and the Plan Declaration--Execution Gap study,
  but it does not make the review database-complete.
- Before stronger priority or completeness claims are made, the author should repeat
  searches in Semantic Scholar, DBLP, Google Scholar, ACM DL, IEEE Xplore, and
  Scopus/Web of Science if available, and perform citation chaining from all close works.
