from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random


@dataclass(frozen=True)
class PriceTick:
    symbol: str
    price_minor: int
    sequence: int
    occurred_at: datetime
    source_seed: int

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.price_minor <= 0:
            raise ValueError("price_minor must be positive")
        if self.sequence <= 0:
            raise ValueError("sequence must be positive")


class SessionState(str, Enum):
    SCHEDULED = "scheduled"
    OPEN = "open"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass(frozen=True)
class MarketSessionChanged:
    from_state: SessionState
    to_state: SessionState
    occurred_at: datetime


class MarketSession:
    """Replayable exchange availability state; closed is terminal."""

    def __init__(self) -> None:
        self.state = SessionState.SCHEDULED
        self.events: list[MarketSessionChanged] = []

    def open(self, now: datetime) -> None:
        self._transition(SessionState.OPEN, now, (SessionState.SCHEDULED, SessionState.PAUSED))

    def pause(self, now: datetime) -> None:
        self._transition(SessionState.PAUSED, now, (SessionState.OPEN,))

    def close(self, now: datetime) -> None:
        self._transition(SessionState.CLOSED, now, (SessionState.OPEN, SessionState.PAUSED))

    def rebuild(self, events: list[MarketSessionChanged]) -> None:
        self.state = SessionState.SCHEDULED
        self.events.clear()
        for event in events:
            if event.from_state != self.state:
                raise ValueError("session event history is not contiguous")
            self.state = event.to_state
            self.events.append(event)

    def _transition(self, target: SessionState, now: datetime, allowed: tuple[SessionState, ...]) -> None:
        if self.state not in allowed:
            raise ValueError(f"cannot transition session from {self.state} to {target}")
        event = MarketSessionChanged(self.state, target, now)
        self.state = target
        self.events.append(event)


class PriceHistory:
    """Append-only deterministic market facts and a rebuildable price view."""

    def __init__(self) -> None:
        self.events: list[PriceTick] = []
        self.current: dict[str, int] = {}

    def append(self, tick: PriceTick) -> None:
        expected = len(self.events) + 1
        if tick.sequence != expected:
            raise ValueError(f"expected price sequence {expected}")
        self.events.append(tick)
        self.current[tick.symbol] = tick.price_minor

    def rebuild(self, events: list[PriceTick]) -> None:
        self.events.clear()
        self.current.clear()
        for tick in events:
            self.append(tick)

    def price_minor(self, symbol: str) -> int:
        try:
            return self.current[symbol]
        except KeyError as error:
            raise ValueError(f"no price tick for {symbol}") from error


class DeterministicPriceGenerator:
    """Seeded price movement that never reads wall-clock or global randomness."""

    def __init__(self, seed: int, step_minor: int = 100) -> None:
        if step_minor <= 0:
            raise ValueError("step_minor must be positive")
        self.seed = seed
        self.step_minor = step_minor
        self._random = random.Random(seed)

    def next_tick(self, symbol: str, current_price_minor: int, sequence: int, occurred_at: datetime) -> PriceTick:
        if current_price_minor <= 0:
            raise ValueError("current_price_minor must be positive")
        change = self._random.randint(-self.step_minor, self.step_minor)
        return PriceTick(
            symbol=symbol,
            price_minor=max(1, current_price_minor + change),
            sequence=sequence,
            occurred_at=occurred_at,
            source_seed=self.seed,
        )
