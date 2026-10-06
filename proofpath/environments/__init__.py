"""Deterministic mock execution and authoritative-state evaluation primitives."""

from proofpath.environments.execute import execute_plan
from proofpath.environments.mock import MockEnvironment
from proofpath.environments.models import ExecutionTrace, OracleEvent, ToolResult, TraceStep
from proofpath.environments.predicates import evaluate_predicate, resolve_path

__all__ = [
    "ExecutionTrace",
    "MockEnvironment",
    "OracleEvent",
    "ToolResult",
    "TraceStep",
    "evaluate_predicate",
    "execute_plan",
    "resolve_path",
]
