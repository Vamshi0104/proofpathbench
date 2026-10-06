window.PROOFPATH_DATA = {
  benchmark: {
    scenarioCount: 96,
    domainCount: 8,
    treatmentUnitCount: 384,
    noFaultExecutionCount: 768,
    failureClassCount: 9,
    representativeScenarioCount: 8
  },
  citation: {
    key: "madhavan2026proofpathbench",
    author: "Vamshi Krishna Madhavan",
    title: "ProofPathBench: A Benchmark for Verifiability-Aware Planning by Tool-Using Language Agents",
    year: "2026",
    version: "0.0.1"
  },
  scenarios: [
    {
      id: "ppb-filesystem-001",
      domain: "Filesystem",
      goal: "Replace file-001 content with ‘approved-v2’.",
      resource: "file-001.content",
      before: "draft-v1",
      target: "approved-v2",
      severity: "low",
      dependents: 1,
      consequence: "One isolated mock dependent consumes this state.",
      mechanism: "independent_readback"
    },
    {
      id: "ppb-database-001",
      domain: "Database",
      goal: "Update record-001 status to ‘approved’.",
      resource: "record-001.status",
      before: "pending",
      target: "approved",
      severity: "high",
      dependents: 20,
      consequence: "Twenty mock dependents consume the state before the next checkpoint.",
      mechanism: "transaction_status"
    },
    {
      id: "ppb-profile-001",
      domain: "Profile",
      goal: "Update profile-001 city to ‘Dallas’.",
      resource: "profile-001.city",
      before: "Houston",
      target: "Dallas",
      severity: "low",
      dependents: 1,
      consequence: "One isolated mock dependent consumes this state.",
      mechanism: "transaction_status"
    },
    {
      id: "ppb-calendar-001",
      domain: "Calendar",
      goal: "Reschedule event-001 to October 6, 2026.",
      resource: "event-001.day",
      before: "2026-10-05",
      target: "2026-10-06",
      severity: "high",
      dependents: 20,
      consequence: "Twenty mock dependents consume the state before the next checkpoint.",
      mechanism: "multiple_source"
    },
    {
      id: "ppb-messaging-001",
      domain: "Messaging",
      goal: "Change message-001 subject to ‘Approved’.",
      resource: "message-001.subject",
      before: "Draft",
      target: "Approved",
      severity: "low",
      dependents: 1,
      consequence: "One isolated mock dependent consumes this state.",
      mechanism: "multiple_source"
    },
    {
      id: "ppb-configuration-001",
      domain: "Configuration",
      goal: "Enable setting-001.",
      resource: "setting-001.enabled",
      before: "false",
      target: "true",
      severity: "high",
      dependents: 20,
      consequence: "Twenty mock dependents consume the state before the next checkpoint.",
      mechanism: "independent_readback"
    },
    {
      id: "ppb-commerce-001",
      domain: "Commerce",
      goal: "Change order-001 destination city to ‘Dallas’.",
      resource: "order-001.city",
      before: "Houston",
      target: "Dallas",
      severity: "low",
      dependents: 1,
      consequence: "One isolated mock dependent consumes this state.",
      mechanism: "independent_readback"
    },
    {
      id: "ppb-subscription-001",
      domain: "Subscription",
      goal: "Change subscription-001 plan to ‘plus’.",
      resource: "subscription-001.plan",
      before: "basic",
      target: "plus",
      severity: "high",
      dependents: 20,
      consequence: "Twenty mock dependents consume the state before the next checkpoint.",
      mechanism: "transaction_status"
    }
  ],
  evidenceDimensions: [
    ["Independence", "Does the evidence avoid the mutation’s failure boundary?"],
    ["Authority", "Does it come from a source that knows the committed state?"],
    ["Specificity", "Does it establish the exact requested postcondition?"],
    ["Freshness", "Was it observed after the attempted change?"],
    ["Linkage", "Can it be tied to this target and operation?"],
    ["Coverage", "Does it include the goal and collateral constraints?"]
  ],
  mechanisms: {
    independent_readback: "Readback",
    transaction_status: "Operation ledger",
    multiple_source: "Readback + audit"
  }
};
