from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
