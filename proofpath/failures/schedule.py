"""Stable failure-seed derivation and schedule sampling."""

from __future__ import annotations

import hashlib
import random

from proofpath.benchmark.models import Scenario
from proofpath.failures.models import FailureType, FaultSpec


def derive_seed(master_seed: int, *parts: str) -> int:
    material = ":".join((str(master_seed), *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def sample_fault(scenario: Scenario, master_seed: int, run_id: str) -> FaultSpec:
    """Resolve the scenario probability into a stored deterministic fault decision."""
    seed = derive_seed(master_seed, scenario.failure_policy.seed_namespace, run_id)
    rng = random.Random(seed)
    draw = rng.random()
    probability = scenario.failure_policy.disclosed_probability
    if draw >= probability:
        return FaultSpec(activated=False, derived_seed=seed, draw=draw)
    failure_type: FailureType = rng.choice(scenario.failure_policy.allowed_failures)
    return FaultSpec(
        activated=True,
        failure_type=failure_type,
        derived_seed=seed,
        draw=draw,
    )


def forced_fault(failure_type: FailureType, seed: int = 0) -> FaultSpec:
    """Construct a fault for deterministic acceptance tests, never for sampled results."""
    return FaultSpec(
        activated=True,
        failure_type=failure_type,
        derived_seed=seed,
        draw=0.0,
    )


def no_fault(seed: int = 0) -> FaultSpec:
    return FaultSpec(activated=False, derived_seed=seed, draw=0.999999)
