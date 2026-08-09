from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.market import SessionState
from app.domain.model import Account, DomainError, DomainEvent, DuplicateExecution, DuplicateOrder


class EventStore(Protocol):
    def load(self, stream_id: str) -> list[DomainEvent]: ...
    def append(self, stream_id: str, expected_version: int, events: list[DomainEvent]) -> None: ...


class MarketData(Protocol):
    def price_minor(self, symbol: str) -> int: ...


class ProjectionSink(Protocol):
    def project(self, events: list[DomainEvent]) -> None: ...


class SessionGate(Protocol):
    state: SessionState


def require_open_session(session: SessionGate | None) -> None:
    if session is not None and session.state != SessionState.OPEN:
        raise DomainError("market session is not open")


@dataclass(frozen=True)
class SubmitMarketBuy:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    occurred_at: datetime


class SubmitMarketBuyHandler:
    def __init__(self, store: EventStore, market: MarketData, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.market = market
        self.projections = projections
        self.session = session

    def handle(self, command: SubmitMarketBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.execute_market_buy(
                command.order_id, command.execution_id, command.symbol,
                command.quantity, self.market.price_minor(command.symbol),
                command.occurred_at,
            )
        except (DuplicateExecution, DuplicateOrder):
            return []
        except DomainError as error:
            # A rejected command is an auditable domain fact, but has no
            # economic effect. Provider and programming failures still escape.
            account.reject_order(command.order_id, command.symbol, str(error), command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class SubmitMarketSell:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    price_minor: int
    occurred_at: datetime


class SubmitMarketSellHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: SubmitMarketSell) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.execute_market_sell(
                command.order_id, command.execution_id, command.symbol,
                command.quantity, command.price_minor, command.occurred_at,
            )
        except (DuplicateExecution, DuplicateOrder):
            return []
        except DomainError as error:
            account.reject_order(command.order_id, command.symbol, str(error), command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class SubmitLimitBuy:
    account_id: str
    order_id: str
    symbol: str
    quantity: int
    limit_price_minor: int
    occurred_at: datetime


class SubmitLimitBuyHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: SubmitLimitBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.reserve_limit_buy(
                command.order_id, command.symbol, command.quantity,
                command.limit_price_minor, command.occurred_at,
            )
        except DuplicateOrder:
            return []
        except DomainError as error:
            account.reject_order(command.order_id, command.symbol, str(error), command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class SubmitMarketSellReservation:
    account_id: str
    order_id: str
    symbol: str
    quantity: int
    occurred_at: datetime


class SubmitMarketSellReservationHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: SubmitMarketSellReservation) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.reserve_market_sell(command.order_id, command.symbol, command.quantity, command.occurred_at)
        except DuplicateOrder:
            return []
        except DomainError as error:
            account.reject_order(command.order_id, command.symbol, str(error), command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class CancelMarketSellReservation:
    account_id: str
    order_id: str
    occurred_at: datetime


class CancelMarketSellReservationHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink) -> None:
        self.store = store
        self.projections = projections

    def handle(self, command: CancelMarketSellReservation) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        account.cancel_market_sell_reservation(command.order_id, command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class ExecuteMarketSellReservation:
    account_id: str
    order_id: str
    execution_id: str
    price_minor: int
    occurred_at: datetime


class ExecuteMarketSellReservationHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: ExecuteMarketSellReservation) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        require_open_session(self.session)
        try:
            account.execute_reserved_market_sell(command.order_id, command.execution_id, command.price_minor, command.occurred_at)
        except DuplicateExecution:
            return []
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class ExecutePartialMarketSellReservation:
    account_id: str
    order_id: str
    execution_id: str
    quantity: int
    price_minor: int
    occurred_at: datetime


class ExecutePartialMarketSellReservationHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: ExecutePartialMarketSellReservation) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        require_open_session(self.session)
        try:
            account.execute_reserved_market_sell_partially(command.order_id, command.execution_id, command.quantity, command.price_minor, command.occurred_at)
        except DuplicateExecution:
            return []
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class CancelLimitBuy:
    account_id: str
    order_id: str
    occurred_at: datetime


class CancelLimitBuyHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink) -> None:
        self.store = store
        self.projections = projections

    def handle(self, command: CancelLimitBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        account.cancel_limit_buy(command.order_id, command.occurred_at)
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class ExecuteLimitBuy:
    account_id: str
    order_id: str
    execution_id: str
    price_minor: int
    occurred_at: datetime


class ExecuteLimitBuyHandler:
    def __init__(self, store: EventStore, market: MarketData, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.market = market
        self.projections = projections
        self.session = session

    def handle(self, command: ExecuteLimitBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.execute_limit_buy(command.order_id, command.execution_id, command.price_minor, command.occurred_at)
        except DuplicateExecution:
            return []
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events


@dataclass(frozen=True)
class ExecutePartialLimitBuy:
    account_id: str
    order_id: str
    execution_id: str
    quantity: int
    price_minor: int
    occurred_at: datetime


class ExecutePartialLimitBuyHandler:
    def __init__(self, store: EventStore, projections: ProjectionSink, session: SessionGate | None = None) -> None:
        self.store = store
        self.projections = projections
        self.session = session

    def handle(self, command: ExecutePartialLimitBuy) -> list[DomainEvent]:
        history = self.store.load(command.account_id)
        account = Account.rehydrate(history)
        try:
            require_open_session(self.session)
            account.execute_limit_buy_partially(
                command.order_id, command.execution_id, command.quantity,
                command.price_minor, command.occurred_at,
            )
        except DuplicateExecution:
            return []
        events = account.pull_events()
        self.store.append(command.account_id, len(history), events)
        self.projections.project(events)
        return events
