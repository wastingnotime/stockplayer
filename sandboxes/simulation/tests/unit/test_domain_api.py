import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "src"))

from app.interfaces.api_facade import SimulationApiFacade
from app.simulation.environment import StockplayerEnvironment


class SimulationApiFacadeTests(unittest.TestCase):
    def test_draft_adapter_rejects_naive_timestamps_at_boundary(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        with self.assertRaisesRegex(ValueError, "explicit UTC offset"):
            facade.open_account({"account_id": "acct-naive", "display_name": "Naive", "cash_minor": 100_000, "occurred_at": "2026-01-05T13:00:00"})

    def test_draft_adapter_translates_command_and_query_without_domain_duplication(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        account = facade.open_account({"account_id": "acct-api", "display_name": "API Demo", "cash_minor": 100_000, "occurred_at": now})
        result = facade.submit_market_buy({"account_id": "acct-api", "order_id": "order-api", "execution_id": "execution-api", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        self.assertEqual(100_000, account["available_cash_minor"])
        self.assertEqual(["MarketBuyExecuted"], result["event_types"])
        self.assertEqual(75_000, result["account"]["available_cash_minor"])
        self.assertEqual("filled", result["account"]["orders"]["order-api"]["status"])
        self.assertEqual(
            {"account_id": "acct-api", "order_id": "order-api", "side": "buy", "symbol": "AUR",
             "requested_quantity": 10, "remaining_quantity": 0, "status": "filled"},
            facade.order("acct-api", "order-api"),
        )
        self.assertIsNone(facade.order("acct-api", "missing"))

    def test_draft_adapter_translates_market_sell(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-sell-api", "display_name": "Sell Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_market_buy({"account_id": "acct-sell-api", "order_id": "buy-api", "execution_id": "buy-execution", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        result = facade.submit_market_sell({"account_id": "acct-sell-api", "order_id": "sell-api", "execution_id": "sell-execution", "symbol": "AUR", "quantity": 4, "price_minor": 3_000, "occurred_at": now})
        self.assertEqual(["MarketSellExecuted"], result["event_types"])
        self.assertEqual(87_000, result["account"]["available_cash_minor"])
        self.assertEqual({"AUR": 6}, result["account"]["positions"])
        self.assertEqual("filled", result["account"]["orders"]["sell-api"]["status"])

    def test_draft_adapter_translates_limit_buy_reservation(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-limit-api", "display_name": "Limit Demo", "cash_minor": 100_000, "occurred_at": now})
        result = facade.submit_limit_buy({"account_id": "acct-limit-api", "order_id": "limit-api", "symbol": "AUR", "quantity": 10, "limit_price_minor": 2_000, "occurred_at": now})
        self.assertEqual(["LimitBuyReserved"], result["event_types"])
        self.assertEqual(80_000, result["account"]["available_cash_minor"])
        self.assertEqual(20_000, result["account"]["reserved_cash_minor"])
        self.assertEqual("accepted", result["account"]["orders"]["limit-api"]["status"])


if __name__ == "__main__":
    unittest.main()
