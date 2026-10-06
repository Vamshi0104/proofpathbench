import json
from pathlib import Path

import pytest

from proofpath.agents import FixtureAdapter
from proofpath.benchmark.generate import generate_scenarios
from proofpath.evaluation.metrics import summarize_records
from proofpath.experiments import load_records, run_registered_choice


def test_fixture_pipeline_is_immutable_and_nonempirical(tmp_path: Path) -> None:
    config_path = Path(__file__).parents[1] / "configs" / "pilot.yaml"
    run_directory = run_registered_choice(
        scenarios=generate_scenarios()[:2],
        adapter=FixtureAdapter("first"),
        run_id="pipeline-test",
        output_root=tmp_path,
        config_path=config_path,
        master_seed=20260928,
        instruction_conditions=("vanilla",),
        variants=("p1-o1", "p1-o2"),
        repetitions=1,
        design_empirical_eligible=False,
    )
    records = load_records(run_directory / "records.jsonl")
    assert len(records) == 4
    assert all(record.parsed_choice is not None for record in records)
    assert all(not record.empirical_eligible for record in records)
    manifest = json.loads((run_directory / "run_manifest.json").read_text())
    completion = json.loads((run_directory / "completion.json").read_text())
    assert manifest["planned_calls"] == 4
    assert completion["complete"] is True
    summary = summarize_records(records, allow_nonempirical=True)
    assert summary["scope"] == "non-empirical pipeline validation"
    with pytest.raises(ValueError, match="no empirically eligible"):
        summarize_records(records)

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        run_registered_choice(
            scenarios=generate_scenarios()[:1],
            adapter=FixtureAdapter(),
            run_id="pipeline-test",
            output_root=tmp_path,
            config_path=config_path,
            master_seed=20260928,
            instruction_conditions=("vanilla",),
            variants=("p1-o1",),
            repetitions=1,
            design_empirical_eligible=False,
        )


def test_run_id_rejects_path_traversal(tmp_path: Path) -> None:
    config_path = Path(__file__).parents[1] / "configs" / "pilot.yaml"
    with pytest.raises(ValueError, match="run_id"):
        run_registered_choice(
            scenarios=generate_scenarios()[:1],
            adapter=FixtureAdapter(),
            run_id="../escape",
            output_root=tmp_path,
            config_path=config_path,
            master_seed=1,
            instruction_conditions=("vanilla",),
            variants=("p1-o1",),
            repetitions=1,
            design_empirical_eligible=False,
        )
