(function () {
  "use strict";

  const data = window.PROOFPATH_DATA;
  const engine = window.ProofPathEngine;
  const siteConfig = window.PROOFPATH_SITE_CONFIG || {};
  const releaseMeta = window.PROOFPATH_RELEASE_META || {};
  if (!data || !engine) return;

  const RISK_LEVELS = [0, 5, 20];
  const PREMIUM_LEVELS = [0, 10, 50, 100];

  const elements = {
    scenario: document.querySelector("#scenario-select"),
    failure: document.querySelector("#failure-select"),
    risk: document.querySelector("#risk-range"),
    riskOutput: document.querySelector("#risk-output"),
    premium: document.querySelector("#premium-range"),
    premiumOutput: document.querySelector("#premium-output"),
    sampleSize: document.querySelector("#sample-size"),
    seed: document.querySelector("#seed-input"),
    domain: document.querySelector("#domain-badge"),
    severity: document.querySelector("#severity-badge"),
    goal: document.querySelector("#scenario-goal"),
    before: document.querySelector("#before-value"),
    target: document.querySelector("#target-value"),
    consequence: document.querySelector("#consequence-copy"),
    verifiedCost: document.querySelector("#verified-cost"),
    mechanism: document.querySelector("#mechanism-label"),
    selection: document.querySelector("#selection-status"),
    liveDistribution: document.querySelector("#live-distribution"),
    avoided: document.querySelector("#avoided-value"),
    overhead: document.querySelector("#overhead-value"),
    efficiency: document.querySelector("#efficiency-value"),
    computeTime: document.querySelector("#compute-time"),
    modelNote: document.querySelector("#model-note"),
    planCards: Array.from(document.querySelectorAll(".plan-card")),
    run: document.querySelector("#run-button"),
    compare: document.querySelector("#compare-button"),
    reset: document.querySelector("#reset-button"),
    resultCard: document.querySelector("#result-card"),
    empty: document.querySelector("#empty-result"),
    single: document.querySelector("#single-result"),
    comparison: document.querySelector("#comparison-result"),
    verdictTitle: document.querySelector("#verdict-title"),
    verdictBadge: document.querySelector("#verdict-badge"),
    trace: document.querySelector("#trace-list"),
    insight: document.querySelector("#result-insight"),
    metrics: document.querySelector("#metric-grid"),
    comparisonNote: document.querySelector("#comparison-note"),
    comparisonSample: document.querySelector("#comparison-sample"),
    evidenceBody: document.querySelector("#evidence-body"),
    repositoryLink: document.querySelector("#repository-link"),
    repositoryNote: document.querySelector("#repository-note"),
    zenodoLink: document.querySelector("#zenodo-link"),
    arxivLink: document.querySelector("#arxiv-link"),
    benchmarkTestCount: document.querySelector("#benchmark-test-count"),
    interactiveTestCount: document.querySelector("#interactive-test-count"),
    citationButton: document.querySelector("#citation-button"),
    citationDialog: document.querySelector("#citation-dialog"),
    citationClose: document.querySelector("#citation-close"),
    citationIdentifierNote: document.querySelector("#citation-identifier-note"),
    bibtex: document.querySelector("#bibtex-output"),
    copyCitation: document.querySelector("#copy-citation"),
    copyStatus: document.querySelector("#copy-status")
  };

  let selectedPlan = "verified";
  let liveResult = null;
  let liveFrame = null;

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function currentScenario() {
    return data.scenarios.find((item) => item.id === elements.scenario.value) || data.scenarios[0];
  }

  function premiumMultiplier() {
    return 1 + currentPremiumPercent() / 100;
  }

  function currentRiskPercent() {
    return RISK_LEVELS[Number(elements.risk.value)] ?? RISK_LEVELS[0];
  }

  function currentPremiumPercent() {
    return PREMIUM_LEVELS[Number(elements.premium.value)] ?? PREMIUM_LEVELS[0];
  }

  function formatValue(value) {
    return typeof value === "boolean" ? String(value) : `“${value}”`;
  }

  function populateScenarios() {
    elements.scenario.innerHTML = data.scenarios
      .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.domain)} · ${escapeHtml(item.id)}</option>`)
      .join("");
  }

  function renderScenario() {
    const scenario = currentScenario();
    elements.domain.textContent = scenario.domain;
    elements.severity.textContent = `${scenario.severity} consequence`;
    elements.goal.textContent = scenario.goal;
    elements.before.textContent = formatValue(scenario.before);
    elements.before.title = String(scenario.before);
    elements.target.textContent = formatValue(scenario.target);
    elements.target.title = String(scenario.target);
    elements.consequence.textContent = scenario.consequence;
    elements.mechanism.textContent = data.mechanisms[scenario.mechanism];
    renderEvidence();
    renderLiveModel();
    clearResult();
  }

  function renderControls() {
    const risk = currentRiskPercent();
    const premium = currentPremiumPercent();
    elements.riskOutput.textContent = `${risk}%`;
    elements.premiumOutput.textContent = premium === 0 ? "same cost" : `+${premium}%`;
    elements.verifiedCost.textContent = `${premiumMultiplier().toFixed(1)} units`;
    elements.risk.setAttribute("aria-valuetext", `${risk}% simulated failure risk`);
    elements.premium.setAttribute("aria-valuetext", premium === 0 ? "same cost" : `${premium}% verification premium`);
  }

  function asPercent(value, count) {
    const percentage = (value / count) * 100;
    return count >= 1000 ? percentage.toFixed(1) : percentage.toFixed(0);
  }

  function formatInteger(value) {
    return new Intl.NumberFormat("en-US").format(value);
  }

  function distributionSegment(className, count, total, label) {
    const width = (count / total) * 100;
    if (count === 0) return "";
    return `<span class="${className}" style="width:${width}%" title="${escapeHtml(label)}: ${escapeHtml(asPercent(count, total))}%"></span>`;
  }

  function distributionRow(plan, item) {
    const label = plan === "direct" ? "Direct plan" : "Verified plan";
    const evidence = plan === "direct" ? "response only" : "independent evidence";
    const segments = [
      distributionSegment("supported", item.supportedCompletion, item.count, "Supported completion"),
      distributionSegment("false", item.falseCompletion, item.count, "False completion"),
      distributionSegment("uncertain", item.uncertain, item.count, "Uncertain"),
      distributionSegment("caught", item.detectedFailure, item.count, "Failure detected")
    ].join("");
    const description = `Supported ${asPercent(item.supportedCompletion, item.count)}%, false completion ${asPercent(item.falseCompletion, item.count)}%, uncertain ${asPercent(item.uncertain, item.count)}%, failure detected ${asPercent(item.detectedFailure, item.count)}%`;

    return `<div class="distribution-row"><div class="distribution-name"><strong>${label}</strong><small>${evidence}</small></div><div class="stacked-bar" role="img" aria-label="${escapeHtml(`${label}: ${description}`)}">${segments}</div><div class="distribution-total">${asPercent(item.honestClaims, item.count)}% honest</div></div>`;
  }

  function renderLiveModel() {
    const start = performance.now();
    const scenario = currentScenario();
    const count = Number(elements.sampleSize.value);
    const risk = currentRiskPercent() / 100;
    const seed = Math.max(0, Math.min(999999, Number(elements.seed.value) || 0));
    const result = engine.compare({ scenario, failure: "random", risk, count, seed });
    const elapsed = performance.now() - start;
    const avoided = result.direct.falseCompletion - result.verified.falseCompletion;
    const overhead = (premiumMultiplier() - 1) * count;
    const efficiency = avoided > 0 ? overhead / avoided : null;

    liveResult = { result, count, risk, seed, overhead, avoided };
    elements.liveDistribution.innerHTML = [
      distributionRow("direct", result.direct),
      distributionRow("verified", result.verified)
    ].join("");
    elements.avoided.textContent = `${formatInteger(avoided)} / ${formatInteger(count)}`;
    elements.overhead.textContent = `+${formatInteger(Math.round(overhead))} units`;
    elements.efficiency.textContent = efficiency === null ? "—" : `${efficiency.toFixed(2)} units`;
    elements.computeTime.textContent = elapsed < 0.1 ? "<0.1 ms" : `${elapsed.toFixed(1)} ms`;
    elements.modelNote.textContent =
      `${formatInteger(count)} paired runs · seed ${seed} · ${Math.round(risk * 100)}% disclosed risk · ${formatInteger(result.direct.failuresInjected)} failures sampled. Both plans receive the same failure schedule. Simulated output, not empirical results.`;
  }

  function scheduleLiveModel() {
    if (liveFrame !== null) cancelAnimationFrame(liveFrame);
    liveFrame = requestAnimationFrame(() => {
      renderLiveModel();
      liveFrame = null;
    });
  }

  function selectPlan(plan) {
    selectedPlan = plan;
    elements.planCards.forEach((card) => {
      const active = card.dataset.plan === plan;
      card.classList.toggle("is-selected", active);
      card.setAttribute("aria-checked", String(active));
      card.tabIndex = active ? 0 : -1;
    });
    elements.selection.textContent = `${plan === "verified" ? "Verified" : "Direct"} plan selected`;
    clearResult();
  }

  function clearResult() {
    elements.empty.hidden = false;
    elements.single.hidden = true;
    elements.comparison.hidden = true;
    elements.resultCard.setAttribute("aria-labelledby", "result-title");
  }

  function level(label, className) {
    return `<span class="level ${className}">${label}</span>`;
  }

  function renderEvidence() {
    elements.evidenceBody.innerHTML = data.evidenceDimensions
      .map(([dimension, question], index) => {
        const directLevel = index === 0 ? level("None", "none") : level("Weak", "weak");
        const verifiedLevel = level("Strong", "strong");
        return `<tr><th scope="row">${escapeHtml(dimension)}</th><td>${directLevel}</td><td>${verifiedLevel}</td><td>${escapeHtml(question)}</td></tr>`;
      })
      .join("");
  }

  function failureLabel(failure) {
    const option = Array.from(elements.failure.options).find((item) => item.value === failure);
    return option ? option.textContent.split(" — ")[0] : failure.replaceAll("_", " ");
  }

  function traceItem(label, value, detail) {
    return `<div class="trace-item"><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong><em>${escapeHtml(detail)}</em></div>`;
  }

  function singleOutcomeCopy(outcome) {
    if (outcome.falseCompletion) {
      return "The plan claimed completion because it trusted the mutation response. The evaluator found that the requested postcondition was false.";
    }
    if (outcome.claim === "uncertain") {
      return "The available evidence cannot justify a completion claim. Preserving uncertainty is safer than converting an ambiguous response into success.";
    }
    if (outcome.claim === "failed" && !outcome.taskSuccess) {
      return "Independent evidence prevented a false completion claim by revealing that the goal or a collateral constraint was not satisfied.";
    }
    if (outcome.duplicateEffect) {
      return "The requested state is satisfied, but the evaluator-only operation ledger records that the logical effect occurred twice. Verified task success and duplicate-effect auditing are reported separately.";
    }
    if (outcome.taskSuccess && outcome.evidenceIndependent) {
      return "The goal is true in authoritative state, and the plan has independent evidence that supports its completion claim.";
    }
    return "The goal is true in authoritative state, but this plan's only evidence shares the mutation service's failure boundary.";
  }

  function renderSingle() {
    const scenario = currentScenario();
    const outcome = engine.simulate({
      plan: selectedPlan,
      scenario,
      failure: elements.failure.value,
      risk: currentRiskPercent() / 100,
      random: engine.seededRandom(engine.hashSeed(`${scenario.id}:single:${elements.failure.value}:${currentRiskPercent()}:${elements.seed.value}`))
    });

    elements.empty.hidden = true;
    elements.comparison.hidden = true;
    elements.single.hidden = false;
    elements.resultCard.setAttribute("aria-labelledby", "verdict-title");

    const titleMap = {
      complete: "The plan can claim completion.",
      failed: "The plan detected that the goal failed.",
      uncertain: "The plan must preserve uncertainty."
    };
    elements.verdictTitle.textContent = titleMap[outcome.claim];
    elements.verdictBadge.className = "verdict-badge";
    if (outcome.falseCompletion) {
      elements.verdictBadge.textContent = "False completion";
      elements.verdictBadge.classList.add("bad");
    } else if (outcome.claim === "uncertain") {
      elements.verdictBadge.textContent = "Uncertain";
      elements.verdictBadge.classList.add("warn");
    } else if (outcome.claim === "failed") {
      elements.verdictBadge.textContent = "Failure caught";
      elements.verdictBadge.classList.add("bad");
    } else {
      elements.verdictBadge.textContent = outcome.evidenceIndependent ? "Verified success" : "Unverified success";
    }

    const responseText = outcome.response === "success" ? "{ status: success }" : outcome.response === "timeout" ? "Request timed out" : outcome.response === "partial" ? "{ status: partial }" : "{ status: failed }";
    const stateText = outcome.goalSatisfied ? `${scenario.resource} = ${formatValue(scenario.target)}` : `${scenario.resource} = ${formatValue(scenario.before)}`;
    const collateralText = outcome.collateral ? "constraints satisfied" : "collateral violation";
    const evidenceText = outcome.evidenceIndependent ? (outcome.verifierCanSee ? "Independent check returned" : "Independent check inconclusive") : "No independent check";

    elements.trace.innerHTML = [
      traceItem("Injected condition", failureLabel(outcome.failure), `Plan: ${selectedPlan}`),
      traceItem("Tool-visible response", responseText, "Visible to the agent"),
      traceItem("Evidence path", evidenceText, data.mechanisms[scenario.mechanism]),
      traceItem("Authoritative state", stateText, "Evaluator-only oracle"),
      traceItem("Collateral state", collateralText, `${scenario.dependents} mock dependent${scenario.dependents === 1 ? "" : "s"}`),
      traceItem("Operation effect", outcome.duplicateEffect ? "duplicate recorded" : "single attempt", "Append-only operation ledger"),
      traceItem("Agent claim", outcome.claim, outcome.falseCompletion ? "Does not match reality" : "Calibrated to evidence")
    ].join("");
    elements.insight.textContent = singleOutcomeCopy(outcome);
  }

  function metricLine(label, value, className) {
    return `<div class="metric-line"><span>${escapeHtml(label)}</span><b>${value}%</b><div class="metric-bar ${className || ""}"><span style="width:${value}%"></span></div></div>`;
  }

  function renderComparison() {
    renderLiveModel();
    const { result, count, risk, seed } = liveResult;

    elements.empty.hidden = true;
    elements.single.hidden = true;
    elements.comparison.hidden = false;
    elements.resultCard.setAttribute("aria-labelledby", "comparison-title");
    elements.metrics.innerHTML = ["direct", "verified"]
      .map((plan) => {
        const label = plan === "direct" ? "Direct plan" : "Verified plan";
        const item = result[plan];
        return `<article class="metric-plan"><strong>${label}</strong>${metricLine("True task success", asPercent(item.taskSuccess, count))}${metricLine("Honest claims", asPercent(item.honestClaims, count))}${metricLine("False completion", asPercent(item.falseCompletion, count), "bad")}${metricLine("Preserved uncertainty", asPercent(item.uncertain, count))}</article>`;
      })
      .join("");

    const premium = Math.round((premiumMultiplier() - 1) * 100);
    elements.comparisonSample.textContent = `n = ${formatInteger(count)} per plan`;
    elements.comparisonNote.textContent =
      `Paired simulation with ${Math.round(risk * 100)}% disclosed risk and seed ${seed}. The verified plan pays ${premium}% more. The comparison measures whether evidence prevents unsupported completion claims; verification does not change the underlying mutation success rate.`;
  }

  function citationText() {
    const citation = data.citation;
    const lines = [
      `@misc{${citation.key},`,
      `  author = {${citation.author}},`,
      `  title = {${citation.title}},`,
      `  year = {${citation.year}},`
    ];
    if (/^\d{4}\.\d{4,5}(v\d+)?$/.test(siteConfig.arxivId || "")) {
      lines.push(`  eprint = {${siteConfig.arxivId}},`, "  archivePrefix = {arXiv},");
    }
    if (/^10\.5281\/zenodo\.\d+$/.test(siteConfig.zenodoDoi || "")) {
      lines.push(`  doi = {${siteConfig.zenodoDoi}},`);
    }
    if (/^https:\/\/[^\s]+$/.test(siteConfig.projectUrl || "")) {
      lines.push(`  url = {${siteConfig.projectUrl}},`);
    }
    lines.push(`  note = {Version ${citation.version}; benchmark software and manuscript}`);
    return `${lines.join("\n")}\n}`;
  }

  function configureResearchLinks() {
    if (/^https:\/\/github\.com\/[^/]+\/[^/]+\/?$/.test(siteConfig.repositoryUrl || "")) {
      elements.repositoryLink.href = siteConfig.repositoryUrl;
      elements.repositoryLink.hidden = false;
      elements.repositoryNote.hidden = true;
    }
    if (/^\d{4}\.\d{4,5}(v\d+)?$/.test(siteConfig.arxivId || "")) {
      elements.arxivLink.href = `https://arxiv.org/abs/${siteConfig.arxivId}`;
      elements.arxivLink.hidden = false;
    }
    if (/^10\.5281\/zenodo\.\d+$/.test(siteConfig.zenodoDoi || "")) {
      elements.zenodoLink.href = `https://doi.org/${siteConfig.zenodoDoi}`;
      elements.zenodoLink.hidden = false;
      elements.citationIdentifierNote.textContent =
        `Zenodo DOI: ${siteConfig.zenodoDoi}. The citation below includes this release DOI.`;
    }
    elements.benchmarkTestCount.textContent = releaseMeta.benchmarkValidationTests ?? "—";
    elements.interactiveTestCount.textContent = releaseMeta.interactiveTests ?? "—";
    elements.bibtex.textContent = citationText();
  }

  async function copyBibtex() {
    const value = elements.bibtex.textContent;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
      } else {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(elements.bibtex);
        selection.removeAllRanges();
        selection.addRange(range);
        if (!document.execCommand("copy")) throw new Error("copy command unavailable");
        selection.removeAllRanges();
      }
      elements.copyStatus.textContent = "BibTeX copied.";
    } catch (_error) {
      elements.copyStatus.textContent = "Copy was unavailable. Select the BibTeX above manually.";
    }
  }

  function reset() {
    elements.scenario.value = data.scenarios[0].id;
    elements.failure.value = "false_success";
    elements.risk.value = "2";
    elements.premium.value = "2";
    elements.sampleSize.value = "1000";
    elements.seed.value = "27";
    selectPlan("verified");
    renderControls();
    renderScenario();
  }

  populateScenarios();
  configureResearchLinks();
  renderControls();
  renderScenario();

  elements.planCards.forEach((card) => {
    card.addEventListener("click", () => selectPlan(card.dataset.plan));
    card.addEventListener("keydown", (event) => {
      if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
        event.preventDefault();
        const next = card.dataset.plan === "direct" ? "verified" : "direct";
        selectPlan(next);
        document.querySelector(`[data-plan="${next}"]`).focus();
      }
    });
  });
  elements.scenario.addEventListener("change", renderScenario);
  elements.failure.addEventListener("change", clearResult);
  elements.risk.addEventListener("input", () => { renderControls(); scheduleLiveModel(); clearResult(); });
  elements.premium.addEventListener("input", () => { renderControls(); scheduleLiveModel(); clearResult(); });
  elements.sampleSize.addEventListener("change", () => { renderLiveModel(); clearResult(); });
  elements.seed.addEventListener("input", () => { scheduleLiveModel(); clearResult(); });
  elements.run.addEventListener("click", renderSingle);
  elements.compare.addEventListener("click", renderComparison);
  elements.reset.addEventListener("click", reset);
  elements.citationButton.addEventListener("click", () => {
    elements.copyStatus.textContent = "";
    elements.citationDialog.showModal();
  });
  elements.citationClose.addEventListener("click", () => elements.citationDialog.close());
  elements.copyCitation.addEventListener("click", copyBibtex);
  elements.citationDialog.addEventListener("close", () => elements.citationButton.focus());
})();
