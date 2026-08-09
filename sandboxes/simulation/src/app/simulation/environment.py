from __future__ import annotations

from datetime import datetime

from app.application.purchase import CancelLimitBuy, CancelLimitBuyHandler, SubmitLimitBuy, SubmitLimitBuyHandler, SubmitMarketBuy, SubmitMarketBuyHandler
from app.domain.model import Account
from app.infrastructure.memory import AccountProjections, FixedMarketData, InMemoryEventStore


class StockplayerEnvironment:
    def __init__(self, prices: dict[str, int]) -> None:
        self.store = InMemoryEventStore()
        self.market = FixedMarketData(prices)
        self.projections = AccountProjections()

    def open_funded_account(self, account_id: str, name: str, cash_minor: int, now: datetime) -> None:
        account = Account()
        account.open(account_id, name, now)
        account.deposit(cash_minor, now)
        events = account.pull_events()
        self.store.append(account_id, 0, events)
        self.projections.project(events)

    def buy(self, command: SubmitMarketBuy):
        return SubmitMarketBuyHandler(self.store, self.market, self.projections).handle(command)

    def limit_buy(self, command: SubmitLimitBuy):
        return SubmitLimitBuyHandler(self.store, self.projections).handle(command)

    def cancel_limit_buy(self, command: CancelLimitBuy):
        return CancelLimitBuyHandler(self.store, self.projections).handle(command)
