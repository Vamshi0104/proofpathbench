"""Audit whether the pilot is eligible to collect empirical model responses."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import yaml

from proofpath.benchmark.generate import PROJECT_ROOT


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def prepilot_audit(config_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    checks: dict[str, dict[str, Any]] = {}

    runtime_path = PROJECT_ROOT / "benchmark" / "runtime_validation_report.json"
    runtime = _load_json(runtime_path)
    current_config_digest = hashlib.sha256(config_path.read_bytes()).hexdigest()
    checks["runtime_validation"] = {
        "passed": bool(
            runtime
            and runtime.get("valid")
            and runtime.get("config_sha256") == current_config_digest
        ),
        "evidence": str(runtime_path.relative_to(PROJECT_ROOT)),
        "current_config_sha256": current_config_digest,
        "validated_config_sha256": runtime.get("config_sha256") if runtime else None,
    }

    review_path = PROJECT_ROOT / config["preregistration"]["blinded_human_review_report"]
    review = _load_json(review_path)
    checks["blinded_human_review"] = {
        "passed": bool(review and review.get("admission_ready_without_adjudication")),
        "evidence": str(review_path.relative_to(PROJECT_ROOT)),
        "note": "Missing or unresolved reviewer disagreements require human action.",
    }

    manipulation_run_id = config["preregistration"].get("empirical_manipulation_run_id")
    manipulation_path = (
        PROJECT_ROOT / "results" / "raw" / manipulation_run_id / "summary.json"
        if manipulation_run_id
        else None
    )
    manipulation = _load_json(manipulation_path) if manipulation_path else None
    checks["empirical_manipulation_check"] = {
        "passed": bool(manipulation and manipulation.get("pass_for_pilot")),
        "evidence": str(manipulation_path.relative_to(PROJECT_ROOT)) if manipulation_path else None,
        "note": "Fixture smoke output is never eligible.",
    }

    power_path = PROJECT_ROOT / config["preregistration"]["power_report"]
    power = _load_json(power_path)
    instruction_power = power.get("instruction_contrast", {}) if power else {}
    recommended = instruction_power.get("minimum_repetition_recommendation")
    repetitions = config["study"]["repetitions_per_presentation"]
    checks["instruction_power_and_budget"] = {
        "passed": bool(power and recommended == repetitions),
        "evidence": str(power_path.relative_to(PROJECT_ROOT)),
        "configured_repetitions": repetitions,
        "recommended_repetitions": recommended,
    }
    factorial = power.get("factorial_effects", {}) if power else {}
    matching_grid = next(
        (
            item
            for item in factorial.get("power_grid", [])
            if item.get("repetitions_per_presentation") == repetitions
        ),
        None,
    )
    interaction_powers = matching_grid.get("estimated_power", {}) if matching_grid else {}
    premium_confirmatory = config["preregistration"].get("premium_confirmatory_in_pilot", True)
    interactions_confirmatory = config["preregistration"].get(
        "interactions_confirmatory_in_pilot", True
    )
    amendment_approved = config["preregistration"].get("gate2_amendment_approved", False)
    premium_adequately_powered = bool(
        interaction_powers and interaction_powers.get("premium_scaled", 0) >= 0.8
    )
    checks["premium_power_review"] = {
        "passed": premium_adequately_powered or (amendment_approved and not premium_confirmatory),
        "evidence": str(power_path.relative_to(PROJECT_ROOT)),
        "estimated_power": interaction_powers.get("premium_scaled"),
        "premium_confirmatory_in_pilot": premium_confirmatory,
        "gate2_amendment_approved": amendment_approved,
        "note": ("An underpowered premium slope must remain an approved pilot estimation target."),
    }
    adequately_powered = bool(
        interaction_powers
        and interaction_powers.get("premium_by_risk", 0) >= 0.8
        and interaction_powers.get("premium_by_severity", 0) >= 0.8
    )
    checks["interaction_power_review"] = {
        "passed": adequately_powered or (amendment_approved and not interactions_confirmatory),
        "evidence": str(power_path.relative_to(PROJECT_ROOT)),
        "estimated_power": interaction_powers,
        "interactions_confirmatory_in_pilot": interactions_confirmatory,
        "gate2_amendment_approved": amendment_approved,
        "note": (
            "Underpowered interactions require approved prospective designation as pilot "
            "estimation targets rather than confirmatory tests."
        ),
    }

    models = config["study"].get("pilot_models", [])
    checks["model_snapshots_frozen"] = {
        "passed": bool(models and all("provider" in item and "model" in item for item in models)),
        "evidence": models,
    }
    checks["config_preregistered"] = {
        "passed": config["study"].get("status") == "preregistered"
        and bool(config["preregistration"].get("frozen_at_utc")),
        "evidence": {
            "status": config["study"].get("status"),
            "frozen_at_utc": config["preregistration"].get("frozen_at_utc"),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "eligible_for_empirical_pilot": passed,
        "checks": checks,
        "next_actions": [name for name, check in checks.items() if not check["passed"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "pilot.yaml")
    parser.add_argument("--write-report", type=Path)
    parser.add_argument(
        "--allow-ineligible",
        action="store_true",
        help="write the audit report without treating expected unmet human gates as an error",
    )
    args = parser.parse_args()
    report = prepilot_audit(args.config.resolve())
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_report:
        args.write_report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if not report["eligible_for_empirical_pilot"] and not args.allow_ineligible:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
