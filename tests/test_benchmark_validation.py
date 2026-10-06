from proofpath.benchmark.generate import generate_scenarios
from proofpath.benchmark.validate import validate_scenarios, validation_report


def test_generated_scenarios_pass_static_validation() -> None:
    scenarios = generate_scenarios()
    assert validate_scenarios(scenarios) == []
    report = validation_report(scenarios)
    assert report["valid"] is True
    assert report["scenario_count"] == 96
