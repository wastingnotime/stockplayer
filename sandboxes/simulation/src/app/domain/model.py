from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def positive(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True)
class AccountOpened:
    account_id: str
    display_name: str
    occurred_at: datetime


@dataclass(frozen=True)
class CashDeposited:
    account_id: str
    amount_minor: int
    occurred_at: datetime


@dataclass(frozen=True)
class MarketBuyExecuted:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    price_minor: int
    occurred_at: datetime

    @property
    def cost_minor(self) -> int:
        return self.quantity * self.price_minor


@dataclass(frozen=True)
class MarketSellExecuted:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    price_minor: int
    occurred_at: datetime

    @property
    def proceeds_minor(self) -> int:
        return self.quantity * self.price_minor


@dataclass(frozen=True)
class OrderRejected:
    account_id: str
    order_id: str
    symbol: str
    reason: str
    occurred_at: datetime


@dataclass(frozen=True)
class LimitBuyReserved:
    account_id: str
    order_id: str
    symbol: str
    quantity: int
    limit_price_minor: int
    reserved_cash_minor: int
    occurred_at: datetime


@dataclass(frozen=True)
class OrderCancelled:
    account_id: str
    order_id: str
    released_cash_minor: int
    occurred_at: datetime


@dataclass(frozen=True)
class LimitBuyExecuted:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    price_minor: int
    reserved_cash_minor: int
    released_cash_minor: int
    occurred_at: datetime

    @property
    def cost_minor(self) -> int:
        return self.quantity * self.price_minor


@dataclass(frozen=True)
class LimitBuyPartiallyExecuted:
    account_id: str
    order_id: str
    execution_id: str
    symbol: str
    quantity: int
    price_minor: int
    reserved_cash_minor: int
    released_cash_minor: int
    remaining_quantity: int
    remaining_reserved_cash_minor: int
    occurred_at: datetime

    @property
    def cost_minor(self) -> int:
        return self.quantity * self.price_minor


DomainEvent = AccountOpened | CashDeposited | MarketBuyExecuted | MarketSellExecuted | OrderRejected | LimitBuyReserved | OrderCancelled | LimitBuyExecuted | LimitBuyPartiallyExecuted


class DomainError(Exception):
    pass


class DuplicateExecution(DomainError):
    pass


class Account:
    def __init__(self) -> None:
        self.account_id: str | None = None
        self.available_cash_minor = 0
        self.reserved_cash_minor = 0
        self.reservations: dict[str, int] = {}
        self.reservation_details: dict[str, tuple[str, int, int]] = {}
        self.execution_ids: set[str] = set()
        self.positions: dict[str, int] = {}
        self.version = 0
        self._pending: list[DomainEvent] = []

    @classmethod
    def rehydrate(cls, events: list[DomainEvent]) -> Account:
        account = cls()
        for event in events:
            account._apply(event)
        return account

    def open(self, account_id: str, display_name: str, now: datetime) -> None:
        if self.account_id is not None:
            raise DomainError("account already opened")
        if not account_id or not display_name:
            raise DomainError("account id and display name are required")
        self._record(AccountOpened(account_id, display_name, now))

    def deposit(self, amount_minor: int, now: datetime) -> None:
        self._require_open()
        self._record(CashDeposited(self.account_id or "", positive(amount_minor, "amount_minor"), now))

    def execute_market_buy(
        self, order_id: str, execution_id: str, symbol: str,
        quantity: int, price_minor: int, now: datetime,
    ) -> None:
        self._require_open()
        self._ensure_new_execution(execution_id)
        quantity = positive(quantity, "quantity")
        price_minor = positive(price_minor, "price_minor")
        cost = quantity * price_minor
        if cost > self.available_cash_minor:
            raise DomainError("insufficient available cash")
        self._record(MarketBuyExecuted(
            self.account_id or "", order_id, execution_id, symbol,
            quantity, price_minor, now,
        ))

    def execute_market_sell(
        self, order_id: str, execution_id: str, symbol: str,
        quantity: int, price_minor: int, now: datetime,
    ) -> None:
        self._require_open()
        self._ensure_new_execution(execution_id)
        quantity = positive(quantity, "quantity")
        price_minor = positive(price_minor, "price_minor")
        owned = self.positions.get(symbol, 0)
        if quantity > owned:
            raise DomainError("insufficient owned quantity")
        self._record(MarketSellExecuted(
            self.account_id or "", order_id, execution_id, symbol,
            quantity, price_minor, now,
        ))

    def reject_order(self, order_id: str, symbol: str, reason: str, now: datetime) -> None:
        self._require_open()
        if not order_id or not symbol or not reason:
            raise DomainError("rejection requires order, symbol, and reason")
        self._record(OrderRejected(self.account_id or "", order_id, symbol, reason, now))

    def reserve_limit_buy(
        self, order_id: str, symbol: str, quantity: int,
        limit_price_minor: int, now: datetime,
    ) -> None:
        self._require_open()
        quantity = positive(quantity, "quantity")
        limit_price_minor = positive(limit_price_minor, "limit_price_minor")
        if order_id in self.reservations:
            raise DomainError("order already exists")
        reserved = quantity * limit_price_minor
        if reserved > self.available_cash_minor:
            raise DomainError("insufficient available cash")
        self._record(LimitBuyReserved(
            self.account_id or "", order_id, symbol, quantity,
            limit_price_minor, reserved, now,
        ))

    def cancel_limit_buy(self, order_id: str, now: datetime) -> None:
        self._require_open()
        try:
            reserved = self.reservations[order_id]
        except KeyError as error:
            raise DomainError("open limit-buy order not found") from error
        self._record(OrderCancelled(self.account_id or "", order_id, reserved, now))

    def execute_limit_buy(self, order_id: str, execution_id: str, price_minor: int, now: datetime) -> None:
        self._require_open()
        self._ensure_new_execution(execution_id)
        price_minor = positive(price_minor, "price_minor")
        try:
            symbol, quantity, limit_price = self.reservation_details[order_id]
            reserved = self.reservations[order_id]
        except KeyError as error:
            raise DomainError("open limit-buy order not found") from error
        if price_minor > limit_price:
            raise DomainError("current price exceeds limit price")
        cost = quantity * price_minor
        self._record(LimitBuyExecuted(
            self.account_id or "", order_id, execution_id, symbol, quantity,
            price_minor, reserved, reserved - cost, now,
        ))

    def execute_limit_buy_partially(
        self, order_id: str, execution_id: str, quantity: int,
        price_minor: int, now: datetime,
    ) -> None:
        self._require_open()
        self._ensure_new_execution(execution_id)
        quantity = positive(quantity, "quantity")
        price_minor = positive(price_minor, "price_minor")
        try:
            symbol, remaining, limit_price = self.reservation_details[order_id]
            reserved = self.reservations[order_id]
        except KeyError as error:
            raise DomainError("open limit-buy order not found") from error
        if quantity >= remaining:
            raise DomainError("partial quantity must be less than remaining quantity")
        if price_minor > limit_price:
            raise DomainError("current price exceeds limit price")
        reserved_for_fill = quantity * limit_price
        cost = quantity * price_minor
        self._record(LimitBuyPartiallyExecuted(
            self.account_id or "", order_id, execution_id, symbol, quantity,
            price_minor, reserved_for_fill, reserved_for_fill - cost,
            remaining - quantity, reserved - reserved_for_fill, now,
        ))

    def pull_events(self) -> list[DomainEvent]:
        events, self._pending = self._pending, []
        return events

    def _require_open(self) -> None:
        if self.account_id is None:
            raise DomainError("account is not open")

    def _ensure_new_execution(self, execution_id: str) -> None:
        if not execution_id:
            raise DomainError("execution id is required")
        if execution_id in self.execution_ids:
            raise DuplicateExecution(f"execution {execution_id} already applied")

    def _record(self, event: DomainEvent) -> None:
        self._apply(event)
        self._pending.append(event)

    def _apply(self, event: DomainEvent) -> None:
        if isinstance(event, AccountOpened):
            self.account_id = event.account_id
        elif isinstance(event, CashDeposited):
            self.available_cash_minor += event.amount_minor
        elif isinstance(event, MarketBuyExecuted):
            self.execution_ids.add(event.execution_id)
            self.available_cash_minor -= event.cost_minor
            self.positions[event.symbol] = self.positions.get(event.symbol, 0) + event.quantity
        elif isinstance(event, MarketSellExecuted):
            self.execution_ids.add(event.execution_id)
            self.available_cash_minor += event.proceeds_minor
            remaining = self.positions.get(event.symbol, 0) - event.quantity
            if remaining:
                self.positions[event.symbol] = remaining
            else:
                self.positions.pop(event.symbol, None)
        elif isinstance(event, LimitBuyReserved):
            self.available_cash_minor -= event.reserved_cash_minor
            self.reserved_cash_minor += event.reserved_cash_minor
            self.reservations[event.order_id] = event.reserved_cash_minor
            self.reservation_details[event.order_id] = (event.symbol, event.quantity, event.limit_price_minor)
        elif isinstance(event, OrderCancelled):
            self.available_cash_minor += event.released_cash_minor
            self.reserved_cash_minor -= event.released_cash_minor
            del self.reservations[event.order_id]
            del self.reservation_details[event.order_id]
        elif isinstance(event, LimitBuyExecuted):
            self.execution_ids.add(event.execution_id)
            self.available_cash_minor += event.released_cash_minor
            self.reserved_cash_minor -= event.reserved_cash_minor
            self.positions[event.symbol] = self.positions.get(event.symbol, 0) + event.quantity
            del self.reservations[event.order_id]
            del self.reservation_details[event.order_id]
        elif isinstance(event, LimitBuyPartiallyExecuted):
            self.execution_ids.add(event.execution_id)
            self.available_cash_minor += event.released_cash_minor
            self.reserved_cash_minor -= event.reserved_cash_minor
            self.positions[event.symbol] = self.positions.get(event.symbol, 0) + event.quantity
            self.reservations[event.order_id] = event.remaining_reserved_cash_minor
            self.reservation_details[event.order_id] = (
                event.symbol, event.remaining_quantity,
                event.remaining_reserved_cash_minor // event.remaining_quantity,
            )
        self.version += 1
