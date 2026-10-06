"""Deterministic mock state with strict oracle/tool-response separation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from proofpath.benchmark.models import Scenario
from proofpath.environments.models import OracleEvent, ToolResult
from proofpath.failures.models import FaultSpec


class MockEnvironment:
    """Execute one scenario without exposing mutable evaluator state to tool callers."""

    def __init__(self, scenario: Scenario, fault: FaultSpec) -> None:
        self.scenario = scenario
        self.fault = fault
        self._initial_state = deepcopy(scenario.initial_state)
        self._authoritative = deepcopy(scenario.initial_state)
        self._visible = deepcopy(scenario.initial_state)
        self._events: list[OracleEvent] = []
        self._operation_counter = 0
        self._mutation_count = 0
        self._stale_reads_remaining = 0
        self._visibility_delay_reads_remaining = 0

    def authoritative_state(self) -> dict[str, Any]:
        return deepcopy(self._authoritative)

    def visible_state(self) -> dict[str, Any]:
        return deepcopy(self._visible)

    def oracle_events(self) -> list[OracleEvent]:
        return [event.model_copy(deep=True) for event in self._events]

    def _event(
        self,
        event: str,
        operation_id: str | None = None,
        **details: Any,
    ) -> None:
        self._events.append(
            OracleEvent(
                sequence=len(self._events) + 1,
                event=event,  # type: ignore[arg-type]
                operation_id=operation_id,
                details=deepcopy(details),
            )
        )

    def _next_operation_id(self) -> str:
        self._operation_counter += 1
        return f"op-{self._operation_counter:04d}"

    def _record_operation(
        self,
        operation_id: str,
        *,
        resource_id: str,
        field: str,
        value: Any,
        committed: bool,
        outcome: str,
        duplicate_count: int = 0,
    ) -> None:
        self._authoritative["operation_ledger"][operation_id] = {
            "resource_id": resource_id,
            "field": field,
            "value": deepcopy(value),
            "committed": committed,
            "outcome": outcome,
            "duplicate_count": duplicate_count,
        }

    def _append_audit(
        self,
        operation_id: str,
        resource_id: str,
        field: str,
        value: Any,
        effect: str,
    ) -> None:
        self._authoritative["audit_projection"].append(
            {
                "operation_id": operation_id,
                "resource_id": resource_id,
                "field": field,
                "value": deepcopy(value),
                "effect": effect,
            }
        )

    def _commit_assignment(
        self,
        resource_id: str,
        field: str,
        value: Any,
        operation_id: str,
        *,
        duplicate: bool = False,
    ) -> None:
        resource = self._authoritative["resources"][resource_id]
        resource[field] = deepcopy(value)
        resource["version"] += 1
        resource["last_operation_id"] = operation_id
        effect = "duplicate" if duplicate else "committed"
        self._append_audit(operation_id, resource_id, field, value, effect)
        self._event(
            "duplicate_commit" if duplicate else "mutation_committed",
            operation_id,
            resource_id=resource_id,
            field=field,
        )

    def mutate(self, resource_id: str, field: str, value: Any) -> ToolResult:
        self._mutation_count += 1
        operation_id = self._next_operation_id()
        self._event(
            "mutation_attempted",
            operation_id,
            resource_id=resource_id,
            field=field,
            value=value,
        )
        failure = self.fault.failure_type if self.fault.activated and self._mutation_count == 1 else None
        if failure:
            self._event("fault_activated", operation_id, failure_type=failure)

        if resource_id not in self._authoritative["resources"]:
            self._event("mutation_rejected", operation_id, reason="resource_not_found")
            return ToolResult(
                tool="mutate",
                status="not_found",
                payload={"operation_id": operation_id},
            )

        if failure == "explicit_failure":
            self._record_operation(
                operation_id,
                resource_id=resource_id,
                field=field,
                value=value,
                committed=False,
                outcome="explicit_failure",
            )
            self._event("mutation_rejected", operation_id, reason=failure)
            return ToolResult(
                tool="mutate",
                status="error",
                payload={"operation_id": operation_id, "error": "injected_failure"},
            )

        if failure in {"false_success", "timeout_before"}:
            self._record_operation(
                operation_id,
                resource_id=resource_id,
                field=field,
                value=value,
                committed=False,
                outcome=failure,
            )
            self._event("mutation_rejected", operation_id, reason=failure)
            if failure == "false_success":
                return ToolResult(
                    tool="mutate",
                    status="success",
                    payload={"operation_id": operation_id, "reported_value": deepcopy(value)},
                )
            return ToolResult(
                tool="mutate",
                status="timeout",
                ambiguous=True,
                payload={"operation_id": operation_id},
            )

        if failure == "partial_update":
            resource = self._authoritative["resources"][resource_id]
            resource[field] = deepcopy(value)
            self._record_operation(
                operation_id,
                resource_id=resource_id,
                field=field,
                value=value,
                committed=False,
                outcome="partial_update",
            )
            self._event("partial_commit", operation_id, omitted=["version", "last_operation_id"])
            self._visible = deepcopy(self._authoritative)
            return ToolResult(
                tool="mutate",
                status="partial",
                payload={"operation_id": operation_id, "reported_value": deepcopy(value)},
            )

        if failure == "wrong_target":
            original = deepcopy(self._authoritative["resources"][resource_id])
            wrong_id = f"wrong-{resource_id}"
            original[field] = deepcopy(value)
            original["version"] += 1
            original["last_operation_id"] = operation_id
            self._authoritative["resources"][wrong_id] = original
            self._record_operation(
                operation_id,
                resource_id=wrong_id,
                field=field,
                value=value,
                committed=True,
                outcome="wrong_target",
            )
            self._append_audit(operation_id, wrong_id, field, value, "wrong_target")
            self._event("wrong_target_commit", operation_id, wrong_resource_id=wrong_id)
            self._visible = deepcopy(self._authoritative)
            return ToolResult(
                tool="mutate",
                status="success",
                payload={"operation_id": operation_id, "reported_value": deepcopy(value)},
            )

        self._commit_assignment(resource_id, field, value, operation_id)
        duplicate_count = 0
        if failure == "duplicated_action":
            self._commit_assignment(resource_id, field, value, operation_id, duplicate=True)
            duplicate_count = 1
        self._record_operation(
            operation_id,
            resource_id=resource_id,
            field=field,
            value=value,
            committed=True,
            outcome=failure or "committed",
            duplicate_count=duplicate_count,
        )

        if failure == "stale_readback":
            self._stale_reads_remaining = 1
        elif failure == "delayed_visibility":
            self._visibility_delay_reads_remaining = 1
        else:
            self._visible = deepcopy(self._authoritative)

        if failure == "timeout_after":
            return ToolResult(
                tool="mutate",
                status="timeout",
                ambiguous=True,
                payload={"operation_id": operation_id},
            )
        return ToolResult(
            tool="mutate",
            status="success",
            payload={"operation_id": operation_id, "reported_value": deepcopy(value)},
        )

    def readback(self, resource_id: str, freshness: str = "current") -> ToolResult:
        if self._stale_reads_remaining:
            self._stale_reads_remaining -= 1
            source = self._initial_state
            stale = True
        elif self._visibility_delay_reads_remaining:
            self._visibility_delay_reads_remaining -= 1
            source = self._visible
            stale = True
            self._visible = deepcopy(self._authoritative)
            self._event("visibility_advanced", details="next read observes committed state")
        else:
            self._visible = deepcopy(self._authoritative)
            source = self._visible
            stale = False
        resource = source["resources"].get(resource_id)
        self._event("read_observed", resource_id=resource_id, stale=stale)
        if resource is None:
            return ToolResult(tool="readback", status="not_found")
        return ToolResult(
            tool="readback",
            status="success",
            payload={"resource": deepcopy(resource), "stale": stale, "freshness": freshness},
        )

    def operation_status(self, operation_id: str | None) -> ToolResult:
        record = self._authoritative["operation_ledger"].get(operation_id)
        self._event("status_observed", operation_id, found=record is not None)
        if record is None:
            return ToolResult(tool="operation_status", status="not_found")
        return ToolResult(
            tool="operation_status",
            status="success",
            payload={"operation": deepcopy(record)},
        )

    def audit_read(self, operation_id: str | None) -> ToolResult:
        entries = [
            deepcopy(item)
            for item in self._authoritative["audit_projection"]
            if item["operation_id"] == operation_id
        ]
        self._event("audit_observed", operation_id, entry_count=len(entries))
        return ToolResult(
            tool="audit_read",
            status="success" if entries else "not_found",
            payload={"entries": entries},
        )
