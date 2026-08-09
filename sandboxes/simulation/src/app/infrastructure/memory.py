from __future__ import annotations

from dataclasses import dataclass

from app.domain.model import AccountOpened, CashDeposited, DomainEvent, LimitBuyExecuted, LimitBuyPartiallyExecuted, LimitBuyReserved, MarketBuyExecuted, OrderCancelled


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
        self.reserved_cash_minor: dict[str, int] = {}
        self.reservations: dict[tuple[str, str], int] = {}
        self.ledger: dict[str, list[LedgerEntry]] = {}
        self.positions: dict[tuple[str, str], int] = {}
        self.processed_execution_ids: set[str] = set()

    def rebuild(self, events: list[DomainEvent]) -> None:
        """Replace this read model with a projection of the complete stream."""
        self.cash_minor.clear()
        self.reserved_cash_minor.clear()
        self.reservations.clear()
        self.ledger.clear()
        self.positions.clear()
        self.processed_execution_ids.clear()
        self.project(events)

    def project(self, events: list[DomainEvent]) -> None:
        for event in events:
            if isinstance(event, (MarketBuyExecuted, LimitBuyExecuted, LimitBuyPartiallyExecuted)):
                if event.execution_id in self.processed_execution_ids:
                    continue
                self.processed_execution_ids.add(event.execution_id)
            if isinstance(event, AccountOpened):
                self.cash_minor[event.account_id] = 0
                self.reserved_cash_minor[event.account_id] = 0
                self.ledger[event.account_id] = []
            elif isinstance(event, CashDeposited):
                self.cash_minor[event.account_id] += event.amount_minor
                self.ledger[event.account_id].append(LedgerEntry("initial_deposit", event.amount_minor, "deposit"))
            elif isinstance(event, MarketBuyExecuted):
                self.cash_minor[event.account_id] -= event.cost_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", -event.cost_minor, event.execution_id))
                key = (event.account_id, event.symbol)
                self.positions[key] = self.positions.get(key, 0) + event.quantity
            elif isinstance(event, LimitBuyReserved):
                self.cash_minor[event.account_id] -= event.reserved_cash_minor
                self.reserved_cash_minor[event.account_id] += event.reserved_cash_minor
                self.reservations[(event.account_id, event.order_id)] = event.reserved_cash_minor
            elif isinstance(event, OrderCancelled):
                self.cash_minor[event.account_id] += event.released_cash_minor
                self.reserved_cash_minor[event.account_id] -= event.released_cash_minor
                del self.reservations[(event.account_id, event.order_id)]
            elif isinstance(event, LimitBuyExecuted):
                self.cash_minor[event.account_id] += event.released_cash_minor
                self.reserved_cash_minor[event.account_id] -= event.reserved_cash_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", -event.cost_minor, event.execution_id))
                key = (event.account_id, event.symbol)
                self.positions[key] = self.positions.get(key, 0) + event.quantity
                del self.reservations[(event.account_id, event.order_id)]
            elif isinstance(event, LimitBuyPartiallyExecuted):
                self.cash_minor[event.account_id] += event.released_cash_minor
                self.reserved_cash_minor[event.account_id] -= event.reserved_cash_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", -event.cost_minor, event.execution_id))
                key = (event.account_id, event.symbol)
                self.positions[key] = self.positions.get(key, 0) + event.quantity
                self.reservations[(event.account_id, event.order_id)] = event.remaining_reserved_cash_minor
