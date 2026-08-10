from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExecutionRequest:
    order_id: str
    symbol: str
    quantity: int
    price_minor: int
    available_liquidity: int

    def __post_init__(self) -> None:
        if not isinstance(self.order_id, str) or not isinstance(self.symbol, str) or not self.order_id or not self.symbol:
            raise ValueError("order and symbol are required")
        if (
            isinstance(self.quantity, bool) or not isinstance(self.quantity, int) or self.quantity <= 0
            or isinstance(self.price_minor, bool) or not isinstance(self.price_minor, int) or self.price_minor <= 0
            or isinstance(self.available_liquidity, bool) or not isinstance(self.available_liquidity, int) or self.available_liquidity < 0
        ):
            raise ValueError("quantity and price must be positive; liquidity cannot be negative")


@dataclass(frozen=True)
class ExecutionDecision:
    engine_version: str
    order_id: str
    filled_quantity: int
    price_minor: int
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.engine_version, str) or not isinstance(self.order_id, str) or not self.engine_version or not self.order_id:
            raise ValueError("engine version and order are required")
        if (
            isinstance(self.filled_quantity, bool) or not isinstance(self.filled_quantity, int) or self.filled_quantity < 0
            or isinstance(self.price_minor, bool) or not isinstance(self.price_minor, int) or self.price_minor <= 0
            or not isinstance(self.reason, str) or not self.reason
        ):
            raise ValueError("decision values must be valid")


class ExecutionEngine(Protocol):
    version: str

    def decide(self, request: ExecutionRequest) -> ExecutionDecision: ...


class FullFillEngineV1:
    version = "v1-full-fill"

    def decide(self, request: ExecutionRequest) -> ExecutionDecision:
        if request.available_liquidity < request.quantity:
            return ExecutionDecision(self.version, request.order_id, 0, request.price_minor, "insufficient liquidity for full fill")
        return ExecutionDecision(self.version, request.order_id, request.quantity, request.price_minor, "full fill")


class LiquidityCappedEngineV2:
    version = "v2-liquidity-capped"

    def decide(self, request: ExecutionRequest) -> ExecutionDecision:
        filled = min(request.quantity, request.available_liquidity)
        reason = "full fill" if filled == request.quantity else ("partial fill" if filled else "no liquidity")
        return ExecutionDecision(self.version, request.order_id, filled, request.price_minor, reason)


def compare_engines(request: ExecutionRequest, engines: tuple[ExecutionEngine, ...]) -> tuple[ExecutionDecision, ...]:
    if not engines:
        raise ValueError("at least one execution engine is required")
    versions = [engine.version for engine in engines]
    if len(set(versions)) != len(versions):
        raise ValueError("execution engine versions must be unique")
    decisions = tuple(engine.decide(request) for engine in engines)
    for decision in decisions:
        if decision.order_id != request.order_id or decision.price_minor != request.price_minor:
            raise ValueError("engine decision must preserve request identity and price")
        if decision.filled_quantity > request.quantity:
            raise ValueError("engine decision cannot overfill request quantity")
    return decisions


def comparison_payload(request: ExecutionRequest, decisions: tuple[ExecutionDecision, ...]) -> dict[str, object]:
    """Serialize validated comparison facts for runtime observations."""
    if not decisions:
        raise ValueError("comparison payload requires decisions")
    for decision in decisions:
        if decision.order_id != request.order_id or decision.price_minor != request.price_minor:
            raise ValueError("comparison payload decision does not match request")
        if decision.filled_quantity > request.quantity:
            raise ValueError("comparison payload decision cannot overfill request")
    return {
        "request_quantity": request.quantity,
        "price_minor": request.price_minor,
        "liquidity": request.available_liquidity,
        "engine_versions": [decision.engine_version for decision in decisions],
        "decisions": [
            {
                "engine_version": decision.engine_version,
                "filled_quantity": decision.filled_quantity,
                "price_minor": decision.price_minor,
                "reason": decision.reason,
            }
            for decision in decisions
        ],
        "fill_delta": decisions[-1].filled_quantity - decisions[0].filled_quantity,
    }
