(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ProofPathEngine = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  "use strict";

  const FAILURE_TYPES = [
    "explicit_failure",
    "false_success",
    "timeout_before",
    "timeout_after",
    "partial_update",
    "stale_readback",
    "delayed_visibility",
    "wrong_target",
    "duplicated_action",
  ];

  function hashSeed(input) {
    let hash = 2166136261;
    for (let index = 0; index < input.length; index += 1) {
      hash ^= input.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function seededRandom(seed) {
    let state = seed || 1;
    return function next() {
      state += 0x6d2b79f5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function resolveFailure(requested, risk, random) {
    if (requested !== "random") return requested;
    if (random() >= risk) return "none";
    return FAILURE_TYPES[Math.floor(random() * FAILURE_TYPES.length)];
  }

  function failureState(failure) {
    const states = {
      none: { goal: true, collateral: true, response: "success", readbackVisible: true, duplicateEffect: false },
      explicit_failure: { goal: false, collateral: false, response: "failure", readbackVisible: true, duplicateEffect: false },
      false_success: { goal: false, collateral: false, response: "success", readbackVisible: true, duplicateEffect: false },
      timeout_before: { goal: false, collateral: false, response: "timeout", readbackVisible: true, duplicateEffect: false },
      timeout_after: { goal: true, collateral: true, response: "timeout", readbackVisible: true, duplicateEffect: false },
      partial_update: { goal: true, collateral: false, response: "partial", readbackVisible: true, duplicateEffect: false },
      stale_readback: { goal: true, collateral: true, response: "success", readbackVisible: false, duplicateEffect: false },
      delayed_visibility: { goal: true, collateral: true, response: "success", readbackVisible: false, duplicateEffect: false },
      wrong_target: { goal: false, collateral: false, response: "success", readbackVisible: true, duplicateEffect: false },
      duplicated_action: { goal: true, collateral: true, response: "success", readbackVisible: true, duplicateEffect: true }
    };
    return { ...(states[failure] || states.none) };
  }

  function simulate(options) {
    const plan = options.plan;
    const scenario = options.scenario;
    const random = options.random || Math.random;
    const failure = resolveFailure(options.failure || "none", options.risk || 0, random);
    const state = failureState(failure);
    const taskSuccess = state.goal && state.collateral;
    const hasIndependentEvidence = plan === "verified";
    const verifierCanSee = state.readbackVisible || scenario.mechanism !== "independent_readback";

    let claim;
    if (!hasIndependentEvidence) {
      claim = state.response === "success" ? "complete" : state.response === "failure" ? "failed" : "uncertain";
    } else if (!verifierCanSee) {
      claim = "uncertain";
    } else if (taskSuccess) {
      claim = "complete";
    } else {
      claim = "failed";
    }

    return {
      plan,
      failure,
      response: state.response,
      goalSatisfied: state.goal,
      collateral: state.collateral,
      duplicateEffect: state.duplicateEffect,
      taskSuccess,
      claim,
      falseCompletion: claim === "complete" && !taskSuccess,
      evidenceIndependent: hasIndependentEvidence,
      verifierCanSee
    };
  }

  function compare(options) {
    const count = options.count || 100;
    const seed = hashSeed(
      `${options.scenario.id}:${options.failure}:${options.risk}:${count}:${options.seed ?? "default"}`
    );
    const summary = {};

    ["direct", "verified"].forEach(function (plan) {
      // Reuse the same deterministic failure schedule for both plans so that
      // differences reflect evidence handling, not different random draws.
      const random = seededRandom(seed);
      const outcomes = [];
      for (let index = 0; index < count; index += 1) {
        outcomes.push(simulate({ ...options, plan, random }));
      }
      summary[plan] = {
        count,
        taskSuccess: outcomes.filter((item) => item.taskSuccess).length,
        supportedCompletion: outcomes.filter(
          (item) => item.claim === "complete" && item.taskSuccess
        ).length,
        falseCompletion: outcomes.filter((item) => item.falseCompletion).length,
        honestClaims: outcomes.filter((item) => !item.falseCompletion).length,
        uncertain: outcomes.filter((item) => item.claim === "uncertain").length,
        detectedFailure: outcomes.filter((item) => item.claim === "failed").length,
        failuresInjected: outcomes.filter((item) => item.failure !== "none").length
      };
    });

    return summary;
  }

  return { FAILURE_TYPES, compare, failureState, hashSeed, seededRandom, simulate };
});
