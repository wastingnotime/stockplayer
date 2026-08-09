from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from app.application.purchase import SubmitMarketBuy
from app.simulation.environment import StockplayerEnvironment


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SimulationApiFacade:
    """Framework-free draft adapter; domain policy remains in use cases."""

    def __init__(self, environment: StockplayerEnvironment) -> None:
        self.environment = environment

    def open_account(self, payload: dict[str, object]) -> dict[str, object]:
        account_id = str(payload["account_id"])
        self.environment.open_funded_account(
            account_id, str(payload["display_name"]), int(payload["cash_minor"]), _time(str(payload["occurred_at"]))
        )
        return self.account(account_id)

    def submit_market_buy(self, payload: dict[str, object]) -> dict[str, object]:
        account_id = str(payload["account_id"])
        events = self.environment.buy(SubmitMarketBuy(
            account_id, str(payload["order_id"]), str(payload["execution_id"]),
            str(payload["symbol"]), int(payload["quantity"]), _time(str(payload["occurred_at"])),
        ))
        return {"event_types": [type(event).__name__ for event in events], "account": self.account(account_id)}

    def account(self, account_id: str) -> dict[str, object]:
        projection = self.environment.projections
        positions = {symbol: quantity for (owner, symbol), quantity in projection.positions.items() if owner == account_id}
        orders = {order_id: asdict(view) for (owner, order_id), view in projection.orders.items() if owner == account_id}
        return {
            "account_id": account_id,
            "available_cash_minor": projection.cash_minor.get(account_id, 0),
            "reserved_cash_minor": projection.reserved_cash_minor.get(account_id, 0),
            "positions": positions,
            "orders": orders,
        }
