"""Immutable registered-choice experiment records and run orchestration."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from proofpath.agents import ModelAdapter, ModelResponse, PlanChoice
from proofpath.benchmark.generate import INDEX_PATH, PROJECT_ROOT
from proofpath.benchmark.models import Scenario
from proofpath.benchmark.render import InstructionCondition, render_prompt
from proofpath.environments import ExecutionTrace, execute_plan
from proofpath.evaluation.outcomes import OutcomeEvaluation, evaluate_outcome
from proofpath.failures import FaultSpec, sample_fault


RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class ExperimentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_schema_version: Literal["0.1"] = "0.1"
    run_id: str
    run_key: str
    scenario_id: str
    domain: str
    verification_cost_multiplier: float | None = None
    disclosed_failure_probability: float | None = None
    severity_condition: str | None = None
    strong_evidence_mechanism: str | None = None
    instruction_condition: str
    presentation_variant: str
    prompt_template: str | None = None
    tool_alias_set: str | None = None
    displayed_plan_order: list[str] | None = None
    repetition: int = Field(ge=1)
    prompt_sha256: str
    prompt: str
    model_response: ModelResponse
    parsed_choice: PlanChoice | None
    parse_error: str | None
    selected_plan_id: str | None
    evidence_dominant_plan_id: str
    selected_evidence_dominant: bool | None
    fault: FaultSpec | None
    execution_trace: ExecutionTrace | None
    outcome: OutcomeEvaluation | None
    selected_cost_units: float | None
    selected_latency_ms: int | None
    empirical_eligible: bool


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def source_tree_digest() -> str:
    """Hash research inputs even when the repository has no initial commit yet."""
    paths: list[Path] = []
    for root in ("proofpath", "benchmark", "configs", "research", "tests"):
        for path in (PROJECT_ROOT / root).rglob("*"):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix not in {".pyc"}
                and path.name not in {"runtime_validation_report.json", "validation_report.json"}
            ):
                paths.append(path)
    digest = hashlib.sha256()
    for path in sorted(paths):
        relative = path.relative_to(PROJECT_ROOT).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _parse_choice(response: ModelResponse) -> tuple[PlanChoice | None, str | None]:
    try:
        return PlanChoice.model_validate_json(response.output_text), None
    except Exception as error:  # Pydantic exposes multiple version-specific error types.
        return None, f"{type(error).__name__}: {error}"


def run_registered_choice(
    *,
    scenarios: list[Scenario],
    adapter: ModelAdapter,
    run_id: str,
    output_root: Path,
    config_path: Path,
    master_seed: int,
    instruction_conditions: tuple[InstructionCondition, ...],
    variants: tuple[str, ...],
    repetitions: int,
    design_empirical_eligible: bool = True,
    presentation_units: list[tuple[Scenario, str]] | None = None,
) -> Path:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("run_id must use 1-80 alphanumeric, dot, underscore, or hyphen characters")
    run_directory = output_root / run_id
    if run_directory.exists():
        raise FileExistsError(f"refusing to overwrite existing run directory: {run_directory}")
    run_directory.mkdir(parents=True)

    config_bytes = config_path.read_bytes()
    units = presentation_units or [
        (scenario, variant) for scenario in scenarios for variant in variants
    ]
    planned_calls = len(units) * len(instruction_conditions) * repetitions
    manifest = {
        "run_id": run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "stage": "registered-choice",
        "provider": adapter.provider,
        "requested_model": adapter.model,
        "adapter_empirical_eligible": adapter.empirical_eligible,
        "design_empirical_eligible": design_empirical_eligible,
        "planned_calls": planned_calls,
        "scenario_ids": [scenario.scenario_id for scenario in scenarios],
        "instruction_conditions": instruction_conditions,
        "presentation_variants": variants,
        "presentation_unit_count": len(units),
        "repetitions": repetitions,
        "master_seed": master_seed,
        "config_path": str(config_path),
        "config_sha256": _sha256_bytes(config_bytes),
        "scenario_index_sha256": _sha256_bytes(INDEX_PATH.read_bytes()),
        "source_tree_sha256": source_tree_digest(),
        "git_commit": _git_commit(),
        "raw_records": "records.jsonl",
    }
    (run_directory / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_directory / "config.yaml").write_bytes(config_bytes)

    schema = PlanChoice.model_json_schema()
    records_path = run_directory / "records.jsonl"
    completed = 0
    valid_choices = 0
    with records_path.open("x", encoding="utf-8") as stream:
        for scenario, variant in units:
            dominant_id = scenario.evidence_dominant_plan_id()
            for condition in instruction_conditions:
                presentation = next(
                    item
                    for item in scenario.presentation_variants
                    if item.variant_id == variant
                )
                prompt = render_prompt(scenario, variant, condition)
                prompt_digest = _sha256_bytes(prompt.encode("utf-8"))
                for repetition in range(1, repetitions + 1):
                    run_key = ":".join(
                        (
                            run_id,
                            scenario.scenario_id,
                            str(scenario.design_cell.verification_cost_multiplier),
                            condition,
                            variant,
                            str(repetition),
                            adapter.model,
                        )
                    )
                    response = adapter.complete(prompt, schema)
                    choice, parse_error = _parse_choice(response)
                    selected_plan_id = choice.plan_id if choice else None
                    fault: FaultSpec | None = None
                    trace: ExecutionTrace | None = None
                    outcome: OutcomeEvaluation | None = None
                    selected_cost: float | None = None
                    selected_latency: int | None = None
                    if choice:
                        plan = scenario.plan(choice.plan_id)
                        fault = sample_fault(scenario, master_seed, run_key)
                        environment, trace = execute_plan(scenario, plan, fault)
                        outcome = evaluate_outcome(
                            scenario,
                            environment,
                            trace,
                            "unresolved",
                        )
                        selected_cost = plan.total_cost_units
                        selected_latency = plan.total_latency_ms
                        valid_choices += 1
                    record = ExperimentRecord(
                        run_id=run_id,
                        run_key=run_key,
                        scenario_id=scenario.scenario_id,
                        domain=scenario.domain.value,
                        verification_cost_multiplier=(
                            scenario.design_cell.verification_cost_multiplier
                        ),
                        disclosed_failure_probability=(
                            scenario.design_cell.disclosed_failure_probability
                        ),
                        severity_condition=scenario.design_cell.severity,
                        strong_evidence_mechanism=scenario.plan(
                            dominant_id
                        ).evidence_mechanism,
                        instruction_condition=condition,
                        presentation_variant=variant,
                        prompt_template=presentation.prompt_template,
                        tool_alias_set=presentation.tool_alias_set,
                        displayed_plan_order=list(presentation.plan_order),
                        repetition=repetition,
                        prompt_sha256=prompt_digest,
                        prompt=prompt,
                        model_response=response,
                        parsed_choice=choice,
                        parse_error=parse_error,
                        selected_plan_id=selected_plan_id,
                        evidence_dominant_plan_id=dominant_id,
                        selected_evidence_dominant=(
                            selected_plan_id == dominant_id if selected_plan_id else None
                        ),
                        fault=fault,
                        execution_trace=trace,
                        outcome=outcome,
                        selected_cost_units=selected_cost,
                        selected_latency_ms=selected_latency,
                        empirical_eligible=(
                            response.empirical_eligible and design_empirical_eligible
                        ),
                    )
                    stream.write(record.model_dump_json() + "\n")
                    stream.flush()
                    completed += 1

    completion = {
        "completed_calls": completed,
        "valid_choices": valid_choices,
        "invalid_choices": completed - valid_choices,
        "complete": completed == planned_calls,
        "empirical_eligible": adapter.empirical_eligible and design_empirical_eligible,
        "completed_at_utc": datetime.now(UTC).isoformat(),
    }
    (run_directory / "completion.json").write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_directory


def load_records(path: Path) -> list[ExperimentRecord]:
    return [
        ExperimentRecord.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
