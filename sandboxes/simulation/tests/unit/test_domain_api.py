import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "src"))

from app.interfaces.api_facade import SimulationApiFacade
from app.simulation.environment import StockplayerEnvironment


class SimulationApiFacadeTests(unittest.TestCase):
    def test_draft_adapter_translates_command_and_query_without_domain_duplication(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        account = facade.open_account({"account_id": "acct-api", "display_name": "API Demo", "cash_minor": 100_000, "occurred_at": now})
        result = facade.submit_market_buy({"account_id": "acct-api", "order_id": "order-api", "execution_id": "execution-api", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        self.assertEqual(100_000, account["available_cash_minor"])
        self.assertEqual(["MarketBuyExecuted"], result["event_types"])
        self.assertEqual(75_000, result["account"]["available_cash_minor"])
        self.assertEqual("filled", result["account"]["orders"]["order-api"]["status"])


if __name__ == "__main__":
    unittest.main()
