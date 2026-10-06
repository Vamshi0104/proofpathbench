const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const engine = require("../engine.js");

const readbackScenario = { id: "test-readback", mechanism: "independent_readback" };
const ledgerScenario = { id: "test-ledger", mechanism: "transaction_status" };

test("direct plan can falsely complete after a false-success response", () => {
  const result = engine.simulate({
    plan: "direct",
    scenario: readbackScenario,
    failure: "false_success",
    risk: 0
  });

  assert.equal(result.taskSuccess, false);
  assert.equal(result.claim, "complete");
  assert.equal(result.falseCompletion, true);
});

test("verified plan catches false success", () => {
  const result = engine.simulate({
    plan: "verified",
    scenario: readbackScenario,
    failure: "false_success",
    risk: 0
  });

  assert.equal(result.taskSuccess, false);
  assert.equal(result.claim, "failed");
  assert.equal(result.falseCompletion, false);
});

test("verified readback preserves uncertainty when evidence is stale", () => {
  const result = engine.simulate({
    plan: "verified",
    scenario: readbackScenario,
    failure: "stale_readback",
    risk: 0
  });

  assert.equal(result.taskSuccess, true);
  assert.equal(result.claim, "uncertain");
  assert.equal(result.falseCompletion, false);
});

test("operation ledger can confirm success despite stale readback", () => {
  const result = engine.simulate({
    plan: "verified",
    scenario: ledgerScenario,
    failure: "stale_readback",
    risk: 0
  });

  assert.equal(result.taskSuccess, true);
  assert.equal(result.claim, "complete");
});

test("duplicated action is successful state with a separately recorded duplicate effect", () => {
  const result = engine.simulate({
    plan: "verified",
    scenario: ledgerScenario,
    failure: "duplicated_action",
    risk: 0
  });

  assert.equal(result.goalSatisfied, true);
  assert.equal(result.collateral, true);
  assert.equal(result.taskSuccess, true);
  assert.equal(result.duplicateEffect, true);
  assert.equal(result.claim, "complete");
});

test("browser simulator exposes all nine canonical failure classes", () => {
  assert.deepEqual(engine.FAILURE_TYPES, [
    "explicit_failure",
    "false_success",
    "timeout_before",
    "timeout_after",
    "partial_update",
    "stale_readback",
    "delayed_visibility",
    "wrong_target",
    "duplicated_action"
  ]);
});

test("timeout before and timeout after preserve their different state semantics", () => {
  const before = engine.simulate({ plan: "verified", scenario: ledgerScenario, failure: "timeout_before" });
  const after = engine.simulate({ plan: "verified", scenario: ledgerScenario, failure: "timeout_after" });
  assert.deepEqual(
    [before.response, before.goalSatisfied, before.taskSuccess, before.claim],
    ["timeout", false, false, "failed"]
  );
  assert.deepEqual(
    [after.response, after.goalSatisfied, after.taskSuccess, after.claim],
    ["timeout", true, true, "complete"]
  );
});

test("direct plan preserves uncertainty for either timeout", () => {
  for (const failure of ["timeout_before", "timeout_after"]) {
    const result = engine.simulate({ plan: "direct", scenario: readbackScenario, failure });
    assert.equal(result.claim, "uncertain");
    assert.equal(result.falseCompletion, false);
  }
});

test("partial update reaches the goal but fails collateral constraints", () => {
  const result = engine.simulate({ plan: "verified", scenario: ledgerScenario, failure: "partial_update" });
  assert.equal(result.response, "partial");
  assert.equal(result.goalSatisfied, true);
  assert.equal(result.collateral, false);
  assert.equal(result.taskSuccess, false);
  assert.equal(result.claim, "failed");
});

test("delayed readback preserves uncertainty while an operation ledger can confirm", () => {
  const readback = engine.simulate({ plan: "verified", scenario: readbackScenario, failure: "delayed_visibility" });
  const ledger = engine.simulate({ plan: "verified", scenario: ledgerScenario, failure: "delayed_visibility" });
  assert.equal(readback.taskSuccess, true);
  assert.equal(readback.claim, "uncertain");
  assert.equal(ledger.claim, "complete");
});

test("wrong-target update cannot satisfy the intended task", () => {
  const direct = engine.simulate({ plan: "direct", scenario: readbackScenario, failure: "wrong_target" });
  const verified = engine.simulate({ plan: "verified", scenario: readbackScenario, failure: "wrong_target" });
  assert.equal(direct.goalSatisfied, false);
  assert.equal(direct.falseCompletion, true);
  assert.equal(verified.claim, "failed");
});

test("failure state snapshots cannot mutate later simulations", () => {
  const first = engine.failureState("false_success");
  first.goal = true;
  assert.equal(engine.failureState("false_success").goal, false);
});

test("repeated comparisons are deterministic for the same inputs", () => {
  const options = {
    scenario: readbackScenario,
    failure: "random",
    risk: 0.2,
    count: 100
  };

  const first = engine.compare(options);
  const second = engine.compare(options);
  assert.deepEqual(first, second);
  assert.equal(first.direct.taskSuccess, first.verified.taskSuccess);
});

test("batch outcome categories account for every run", () => {
  const count = 1000;
  const result = engine.compare({
    scenario: readbackScenario,
    failure: "random",
    risk: 0.2,
    count,
    seed: 27
  });

  for (const plan of ["direct", "verified"]) {
    const item = result[plan];
    assert.equal(
      item.supportedCompletion + item.falseCompletion + item.uncertain + item.detectedFailure,
      count
    );
  }
  assert.equal(result.direct.failuresInjected, result.verified.failuresInjected);
});

test("a user seed deterministically controls the random failure schedule", () => {
  const options = {
    scenario: readbackScenario,
    failure: "random",
    risk: 0.2,
    count: 1000
  };

  const seed27 = engine.compare({ ...options, seed: 27 });
  const seed28 = engine.compare({ ...options, seed: 28 });
  assert.notEqual(seed27.direct.failuresInjected, seed28.direct.failuresInjected);
});

test("paired plans receive the exact same seeded failure schedule", () => {
  const seed = engine.hashSeed("paired-schedule");
  const schedules = ["direct", "verified"].map((plan) => {
    const random = engine.seededRandom(seed);
    return Array.from({ length: 250 }, () => engine.simulate({
      plan,
      scenario: readbackScenario,
      failure: "random",
      risk: 0.2,
      random
    }).failure);
  });
  assert.deepEqual(schedules[0], schedules[1]);
});

test("zero disclosed risk produces no random failures", () => {
  const result = engine.compare({
    scenario: readbackScenario,
    failure: "random",
    risk: 0,
    count: 100
  });

  assert.equal(result.direct.taskSuccess, 100);
  assert.equal(result.direct.falseCompletion, 0);
  assert.equal(result.verified.taskSuccess, 100);
  assert.equal(result.verified.falseCompletion, 0);
});

test("research page exposes paper, artifact, and citation downloads", () => {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  assert.match(html, /href="downloads\/proofpath_benchmark\.pdf"/);
  assert.match(html, /href="downloads\/proofpath_artifact\.tar\.gz"/);
  assert.match(html, /href="downloads\/CITATION\.cff"/);
  assert.match(html, /no\s+behavioral model results/i);
});

test("site states the simulation boundary and avoids ambiguous live-model language", () => {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  assert.match(html, /Paired simulation/);
  assert.match(html, /Simulated failure risk/);
  assert.doesNotMatch(html, /Paired risk model|Live-model failure risk/);
});

test("research navigation supports paper, source configuration, artifact, and citation", () => {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  const config = fs.readFileSync(path.join(__dirname, "..", "site-config.js"), "utf8");
  assert.match(html, /id="repository-link"/);
  assert.match(html, /id="zenodo-link"/);
  assert.match(html, /id="citation-button"/);
  assert.match(html, /id="citation-dialog"/);
  assert.match(config, /repositoryUrl:\s*"https:\/\/github\.com\/Vamshi0104\/proofpathbench"/);
  assert.match(config, /projectUrl:\s*"https:\/\/vamshi0104\.github\.io\/proofpathbench\/"/);
});

test("Zenodo integration accepts a blank or valid Zenodo DOI", () => {
  const config = fs.readFileSync(path.join(__dirname, "..", "site-config.js"), "utf8");
  const app = fs.readFileSync(path.join(__dirname, "..", "app.js"), "utf8");
  const context = { window: {} };
  vm.runInNewContext(config, context);
  assert.match(context.window.PROOFPATH_SITE_CONFIG.zenodoDoi, /^(?:|10\.5281\/zenodo\.\d+)$/);
  assert.match(app, /10\\\.5281\\\/zenodo\\\.\\d\+/);
});

test("critical local site assets and downloads exist", () => {
  const root = path.join(__dirname, "..");
  for (const relative of [
    "app.js", "data.js", "engine.js", "release-meta.js", "site-config.js", "styles.css",
    "favicon.svg", "og-image.png", "downloads/proofpath_benchmark.pdf",
    "downloads/proofpath_artifact.tar.gz", "downloads/CITATION.cff"
  ]) {
    assert.equal(fs.existsSync(path.join(root, relative)), true, relative);
  }
});

test("website benchmark counts match the canonical release reports", () => {
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "..", "data.js"), "utf8"), context);
  const runtime = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "benchmark", "runtime_validation_report.json"), "utf8"));
  const staticReport = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "benchmark", "validation_report.json"), "utf8"));
  assert.equal(context.window.PROOFPATH_DATA.benchmark.scenarioCount, staticReport.scenario_count);
  assert.equal(context.window.PROOFPATH_DATA.benchmark.treatmentUnitCount, runtime.split_plot_unit_count);
  assert.equal(context.window.PROOFPATH_DATA.benchmark.noFaultExecutionCount, runtime.no_fault_plan_executions);
  assert.equal(context.window.PROOFPATH_DATA.benchmark.failureClassCount, Object.keys(runtime.forced_failure_results).length);
});

test("major accessibility invariants are present in static markup", () => {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  assert.match(html, /class="skip-link"/);
  assert.match(html, /<main id="top">/);
  assert.match(html, /<nav aria-label="Primary navigation">/);
  assert.match(html, /<caption class="sr-only">/);
  assert.match(html, /role="radiogroup"/);
  assert.match(html, /<dialog id="citation-dialog" aria-labelledby="citation-title">/);
});

test("live result region follows the visible result heading", () => {
  const root = path.join(__dirname, "..");
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
  assert.match(html, /id="result-card"[^>]+aria-labelledby="result-title"/);
  assert.match(html, /id="comparison-title">What each plan can honestly claim/);
  assert.match(app, /setAttribute\("aria-labelledby", "result-title"\)/);
  assert.match(app, /setAttribute\("aria-labelledby", "verdict-title"\)/);
  assert.match(app, /setAttribute\("aria-labelledby", "comparison-title"\)/);
});

test("social metadata uses the release preview image", () => {
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  assert.match(html, /property="og:image" content="https:\/\/vamshi0104\.github\.io\/proofpathbench\/og-image\.png"/);
  assert.match(html, /property="og:image:width" content="1200"/);
  assert.match(html, /property="og:image:height" content="630"/);
  assert.match(html, /name="twitter:card" content="summary_large_image"/);
  assert.match(html, /rel="canonical" href="https:\/\/vamshi0104\.github\.io\/proofpathbench\/"/);
  assert.match(html, /property="og:url" content="https:\/\/vamshi0104\.github\.io\/proofpathbench\/"/);
});
