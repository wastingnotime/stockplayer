from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    title: str
    demonstrates: str
    status: str


SCENARIOS: tuple[ScenarioSpec, ...] = (
    ScenarioSpec("simple_purchase", "Simple purchase", "deterministic command, execution, ledger, and position", "implemented"),
    ScenarioSpec("insufficient_funds", "Insufficient funds", "explicit rejection without economic effect", "implemented"),
    ScenarioSpec("cash_reservation", "Cash reservation", "available versus reserved cash", "implemented"),
    ScenarioSpec("cancellation", "Cancellation", "reservation release and lifecycle", "implemented"),
    ScenarioSpec("partial_execution", "Partial execution", "remaining quantity and repeated settlement", "implemented"),
    ScenarioSpec("duplicate_execution", "Duplicate execution", "idempotent command and projection delivery", "implemented"),
    ScenarioSpec("projection_rebuild", "Projection rebuild", "recoverable read models", "implemented"),
    ScenarioSpec("market_sell", "Market sell", "ownership invariant and proceeds", "implemented"),
    ScenarioSpec("price_ticks", "Price ticks", "seeded deterministic market movement", "implemented"),
    ScenarioSpec("session_enforcement", "Session enforcement", "availability state at order boundary", "implemented"),
    ScenarioSpec("projection_failure_recovery", "Projection failure and recovery", "event-before-projection recovery", "implemented"),
    ScenarioSpec("engine_comparison", "Engine comparison", "versioned deterministic strategy differences", "implemented"),
    ScenarioSpec("sell_reservation", "Sell reservation", "reserved owned quantity", "implemented"),
    ScenarioSpec("api_adapter", "API adapter", "technology-facing released contract", "planned"),
)


def get_scenario(scenario_id: str) -> ScenarioSpec:
    for scenario in SCENARIOS:
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"unknown scenario: {scenario_id}")


def implemented_scenarios() -> tuple[ScenarioSpec, ...]:
    return tuple(scenario for scenario in SCENARIOS if scenario.status == "implemented")
