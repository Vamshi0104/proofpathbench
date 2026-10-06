"""Authoritative-state predicate evaluation."""

from __future__ import annotations

from typing import Any

from proofpath.benchmark.models import Predicate

MISSING = object()


def resolve_path(state: dict[str, Any], path: str) -> Any:
    current: Any = state
    for part in path.split("."):
        if part == "__count__":
            if not isinstance(current, (dict, list)):
                return MISSING
            current = len(current)
            continue
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current


def evaluate_predicate(state: dict[str, Any], predicate: Predicate) -> bool:
    actual = resolve_path(state, predicate.path)
    if predicate.operator == "absent":
        return actual is MISSING
    if actual is MISSING:
        return False
    if predicate.operator == "eq":
        return bool(actual == predicate.expected)
    if predicate.operator == "ne":
        return bool(actual != predicate.expected)
    if predicate.operator == "contains":
        try:
            return bool(predicate.expected in actual)
        except TypeError:
            return False
    if predicate.operator == "count_eq":
        return bool(actual == predicate.expected)
    if predicate.operator == "version_ge":
        return isinstance(actual, (int, float)) and actual >= predicate.expected
    raise ValueError(f"unsupported operator: {predicate.operator}")
