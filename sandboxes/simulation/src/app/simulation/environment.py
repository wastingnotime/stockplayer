from __future__ import annotations

from datetime import datetime

from app.domain.market import MarketSession
from app.application.purchase import CancelLimitBuy, CancelLimitBuyHandler, ExecuteLimitBuy, ExecuteLimitBuyHandler, ExecutePartialLimitBuy, ExecutePartialLimitBuyHandler, SubmitLimitBuy, SubmitLimitBuyHandler, SubmitMarketBuy, SubmitMarketBuyHandler, SubmitMarketSell, SubmitMarketSellHandler
from app.domain.model import Account
from app.infrastructure.memory import AccountProjections, FixedMarketData, InMemoryEventStore


class StockplayerEnvironment:
    def __init__(self, prices: dict[str, int]) -> None:
        self.store = InMemoryEventStore()
        self.market = FixedMarketData(prices)
        self.projections = AccountProjections()
        self.session = MarketSession()

    def open_funded_account(self, account_id: str, name: str, cash_minor: int, now: datetime) -> None:
        account = Account()
        if self.session.state.value == "scheduled":
            self.session.open(now)
        account.open(account_id, name, now)
        account.deposit(cash_minor, now)
        events = account.pull_events()
        self.store.append(account_id, 0, events)
        self.projections.project(events)

    def fail_next_projection(self) -> None:
        self.projections.inject_failure()

    def buy(self, command: SubmitMarketBuy):
        return SubmitMarketBuyHandler(self.store, self.market, self.projections, self.session).handle(command)

    def sell(self, command: SubmitMarketSell):
        return SubmitMarketSellHandler(self.store, self.projections, self.session).handle(command)

    def limit_buy(self, command: SubmitLimitBuy):
        return SubmitLimitBuyHandler(self.store, self.projections, self.session).handle(command)

    def cancel_limit_buy(self, command: CancelLimitBuy):
        return CancelLimitBuyHandler(self.store, self.projections).handle(command)

    def execute_limit_buy(self, command: ExecuteLimitBuy):
        return ExecuteLimitBuyHandler(self.store, self.market, self.projections, self.session).handle(command)

    def execute_partial_limit_buy(self, command: ExecutePartialLimitBuy):
        return ExecutePartialLimitBuyHandler(self.store, self.projections, self.session).handle(command)
