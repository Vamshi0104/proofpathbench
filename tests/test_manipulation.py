from pathlib import Path

from proofpath.agents import FixtureAdapter
from proofpath.benchmark.generate import generate_scenarios
from proofpath.manipulation import (
    load_manipulation_records,
    run_manipulation_check,
    summarize_manipulation,
)


def test_manipulation_fixture_is_correct_but_cannot_pass_gate(tmp_path: Path) -> None:
    directory = run_manipulation_check(
        scenarios=generate_scenarios(),
        adapter=FixtureAdapter(),
        run_id="manipulation-test",
        output_root=tmp_path,
        design_empirical_eligible=False,
    )
    records = load_manipulation_records(directory / "records.jsonl")
    assert len(records) == 96
    assert all(record.evidence_classification_correct for record in records)
    assert all(record.cost_classification_correct for record in records)
    summary = summarize_manipulation(records, allow_nonempirical=True)
    assert summary["thresholds_numerically_met"] is True
    assert summary["pass_for_pilot"] is False
