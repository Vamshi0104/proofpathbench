import math

from proofpath.evaluation.metrics import proportion_metric, wilson_interval


def test_wilson_interval_known_shape() -> None:
    lower, upper = wilson_interval(50, 100)
    assert 0.40 < lower < 0.41
    assert 0.59 < upper < 0.60
    assert lower < 0.5 < upper


def test_wilson_interval_empty_is_nan() -> None:
    lower, upper = wilson_interval(0, 0)
    assert math.isnan(lower)
    assert math.isnan(upper)
    assert proportion_metric(0, 0)["rate"] is None
