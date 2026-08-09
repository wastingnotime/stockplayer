from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.model import Account, DomainEvent


class EventStore(Protocol):
    def load(self, stream_id: str) -> list[DomainEvent]: ...
    def append(self, stream_id: str, expected_version: int, events: list[DomainEvent]) -> None: ...


class MarketData(Protocol):
    def price_minor(self, symbol: str) -> int: ...


class ProjectionSink(Protocol):
    def project(self, events: list[DomainEvent]) -> None: ...


@dataclass(frozen=True)
class SubmitMarketBuy:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    occurred_at: datetime


class SubmitMarketBuyHandler:
    def __init__(self, store: EventStore, market: MarketData, projections: ProjectionSink) -> None:
        self.store = store
        self.market = market
        self.projections = projections

    def handle(self, command: SubmitMarketBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        account.execute_market_buy(
            command.order_id, command.execution_id, command.symbol,
            command.quantity, self.market.price_minor(command.symbol),
            command.occurred_at,
        )
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events
