from pathlib import Path

from proofpath.prepilot import prepilot_audit


def test_current_design_is_not_mislabeled_as_pilot_ready() -> None:
    config = Path(__file__).parents[1] / "configs" / "pilot.yaml"
    report = prepilot_audit(config)
    assert report["eligible_for_empirical_pilot"] is False
    assert report["checks"]["runtime_validation"]["passed"] is True
    assert report["checks"]["premium_power_review"]["passed"] is True
    assert report["checks"]["blinded_human_review"]["passed"] is False
    assert report["checks"]["empirical_manipulation_check"]["passed"] is False
