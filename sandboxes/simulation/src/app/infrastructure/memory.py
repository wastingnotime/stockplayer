from __future__ import annotations

from dataclasses import dataclass

from app.domain.model import AccountOpened, CashDeposited, DomainEvent, LimitBuyExecuted, LimitBuyPartiallyExecuted, LimitBuyReserved, MarketBuyExecuted, MarketSellExecuted, OrderCancelled


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
        self.position_cost_minor: dict[tuple[str, str], int] = {}
        self.realized_result_minor: dict[tuple[str, str], int] = {}
        self.processed_execution_ids: set[str] = set()

    def rebuild(self, events: list[DomainEvent]) -> None:
        """Replace this read model with a projection of the complete stream."""
        self.cash_minor.clear()
        self.reserved_cash_minor.clear()
        self.reservations.clear()
        self.ledger.clear()
        self.positions.clear()
        self.position_cost_minor.clear()
        self.realized_result_minor.clear()
        self.processed_execution_ids.clear()
        self.project(events)

    def project(self, events: list[DomainEvent]) -> None:
        for event in events:
            if isinstance(event, (MarketBuyExecuted, MarketSellExecuted, LimitBuyExecuted, LimitBuyPartiallyExecuted)):
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
                self._record_buy(event.account_id, event.symbol, event.quantity, event.cost_minor)
            elif isinstance(event, MarketSellExecuted):
                self.cash_minor[event.account_id] += event.proceeds_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", event.proceeds_minor, event.execution_id))
                self._record_sell(event.account_id, event.symbol, event.quantity, event.proceeds_minor)
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
                self._record_buy(event.account_id, event.symbol, event.quantity, event.cost_minor)
                del self.reservations[(event.account_id, event.order_id)]
            elif isinstance(event, LimitBuyPartiallyExecuted):
                self.cash_minor[event.account_id] += event.released_cash_minor
                self.reserved_cash_minor[event.account_id] -= event.reserved_cash_minor
                self.ledger[event.account_id].append(LedgerEntry("trade_settlement", -event.cost_minor, event.execution_id))
                self._record_buy(event.account_id, event.symbol, event.quantity, event.cost_minor)
                self.reservations[(event.account_id, event.order_id)] = event.remaining_reserved_cash_minor

    def average_cost_minor(self, account_id: str, symbol: str) -> int:
        key = (account_id, symbol)
        quantity = self.positions.get(key, 0)
        return self.position_cost_minor.get(key, 0) // quantity if quantity else 0

    def _record_buy(self, account_id: str, symbol: str, quantity: int, cost_minor: int) -> None:
        key = (account_id, symbol)
        self.positions[key] = self.positions.get(key, 0) + quantity
        self.position_cost_minor[key] = self.position_cost_minor.get(key, 0) + cost_minor

    def _record_sell(self, account_id: str, symbol: str, quantity: int, proceeds_minor: int) -> None:
        key = (account_id, symbol)
        quantity_before = self.positions[key]
        cost_before = self.position_cost_minor[key]
        cost_basis = (cost_before * quantity) // quantity_before
        remaining = quantity_before - quantity
        self.realized_result_minor[key] = self.realized_result_minor.get(key, 0) + proceeds_minor - cost_basis
        if remaining:
            self.positions[key] = remaining
            self.position_cost_minor[key] = cost_before - cost_basis
        else:
            self.positions.pop(key, None)
            self.position_cost_minor.pop(key, None)
