from proofpath.benchmark.models import Predicate
from proofpath.environments.predicates import evaluate_predicate, resolve_path

STATE = {
    "resources": {
        "x": {"value": "target", "version": 2, "tags": ["a", "b"]},
    }
}


def test_resolve_path_and_special_count() -> None:
    assert resolve_path(STATE, "resources.x.value") == "target"
    assert resolve_path(STATE, "resources.__count__") == 1


def test_predicate_positive_and_negative_cases() -> None:
    predicates = [
        Predicate(path="resources.x.value", operator="eq", expected="target"),
        Predicate(path="resources.x.value", operator="ne", expected="other"),
        Predicate(path="resources.x.tags", operator="contains", expected="b"),
        Predicate(path="resources.__count__", operator="count_eq", expected=1),
        Predicate(path="resources.x.version", operator="version_ge", expected=2),
        Predicate(path="resources.missing", operator="absent"),
    ]
    assert all(evaluate_predicate(STATE, predicate) for predicate in predicates)
    assert not evaluate_predicate(
        STATE, Predicate(path="resources.x.value", operator="eq", expected="wrong")
    )
    assert not evaluate_predicate(
        STATE, Predicate(path="resources.missing", operator="eq", expected=None)
    )
