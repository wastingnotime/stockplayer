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
        if not self.order_id or not self.symbol:
            raise ValueError("order and symbol are required")
        if self.quantity <= 0 or self.price_minor <= 0 or self.available_liquidity < 0:
            raise ValueError("quantity and price must be positive; liquidity cannot be negative")


@dataclass(frozen=True)
class ExecutionDecision:
    engine_version: str
    order_id: str
    filled_quantity: int
    price_minor: int
    reason: str


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
    return tuple(engine.decide(request) for engine in engines)
