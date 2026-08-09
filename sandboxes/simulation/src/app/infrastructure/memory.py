from __future__ import annotations

from dataclasses import dataclass

from app.domain.model import AccountOpened, CashDeposited, DomainEvent, MarketBuyExecuted


class ConcurrencyError(Exception):
    pass


class InMemoryEventStore:
    def __init__(self) -> None:
        self.streams: dict[str, list[DomainEvent]] = {}

    def load(self, stream_id: str) -> list[DomainEvent]:
        return list(self.streams.get(stream_id, []))

    def append(self, stream_id: str, expected_version: int, events: list[DomainEvent]) -> None:
        stream = self.streams.setdefault(stream_id, [])
        if len(stream) != expected_version:
            raise ConcurrencyError("event stream version conflict")
        stream.extend(events)


class FixedMarketData:
    def __init__(self, prices: dict[str, int]) -> None:
        self.prices = dict(prices)

    def price_minor(self, symbol: str) -> int:
        try:
            return self.prices[symbol]
        except KeyError as error:
            raise ValueError(f"no current price for {symbol}") from error


@dataclass(frozen=True)
class LedgerEntry:
    entry_type: str
    amount_minor: int
    reference: str


class AccountProjections:
    def __init__(self) -> None:
        self.cash_minor: dict[str, int] = {}
        self.ledger: dict[str, list[LedgerEntry]] = {}
        self.positions: dict[tuple[str, str], int] = {}

    def project(self, events: list[DomainEvent]) -> None:
        for event in events:
            if isinstance(event, AccountOpened):
                self.cash_minor[event.account_id] = 0
                self.ledger[event.account_id] = []
            elif isinstance(event, CashDeposited):
                self.cash_minor[event.account_id] += event.amount_minor
                self.ledger[event.account_id].append(LedgerEntry("initial_deposit", event.amount_minor, "deposit"))
            elif isinstance(event, MarketBuyExecuted):
                self.cash_minor[event.account_id] -= event.cost_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", -event.cost_minor, event.execution_id))
                key = (event.account_id, event.symbol)
                self.positions[key] = self.positions.get(key, 0) + event.quantity
