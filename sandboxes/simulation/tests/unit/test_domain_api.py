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

        self.assertEqual(
            {"quantity": 6, "average_cost_minor": 2_500, "cost_basis_minor": 15_000,
             "realized_result_minor": 2_000, "unrealized_result_minor": 0},
            result["account"]["valuation"]["AUR"],
        )

    def test_draft_adapter_translates_market_sell_reservation(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-reserve-sell-api", "display_name": "Reserve Sell Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_market_buy({"account_id": "acct-reserve-sell-api", "order_id": "buy-reserve-sell", "execution_id": "buy-reserve-execution", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        result = facade.reserve_market_sell({"account_id": "acct-reserve-sell-api", "order_id": "sell-reserve-api", "symbol": "AUR", "quantity": 4, "occurred_at": now})
        self.assertEqual(["SellQuantityReserved"], result["event_types"])
        self.assertEqual({"AUR": 10}, result["account"]["positions"])
        self.assertEqual({"sell-reserve-api": 4}, result["account"]["reserved_quantities"])
        self.assertEqual("accepted", result["account"]["orders"]["sell-reserve-api"]["status"])

    def test_draft_adapter_translates_market_sell_reservation_cancellation(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-cancel-sell-api", "display_name": "Cancel Sell Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_market_buy({"account_id": "acct-cancel-sell-api", "order_id": "buy-cancel-sell", "execution_id": "buy-cancel-execution", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        facade.reserve_market_sell({"account_id": "acct-cancel-sell-api", "order_id": "sell-cancel-api", "symbol": "AUR", "quantity": 4, "occurred_at": now})
        result = facade.cancel_market_sell_reservation({"account_id": "acct-cancel-sell-api", "order_id": "sell-cancel-api", "occurred_at": now})
        self.assertEqual(["SellReservationCancelled"], result["event_types"])
        self.assertEqual({}, result["account"]["reserved_quantities"])
        self.assertEqual("cancelled", result["account"]["orders"]["sell-cancel-api"]["status"])

    def test_draft_adapter_translates_market_sell_reservation_execution(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-execute-sell-api", "display_name": "Execute Sell Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_market_buy({"account_id": "acct-execute-sell-api", "order_id": "buy-execute-sell", "execution_id": "buy-execute-execution", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        facade.reserve_market_sell({"account_id": "acct-execute-sell-api", "order_id": "sell-execute-api", "symbol": "AUR", "quantity": 4, "occurred_at": now})
        result = facade.execute_market_sell_reservation({"account_id": "acct-execute-sell-api", "order_id": "sell-execute-api", "execution_id": "sell-execute-execution", "price_minor": 3_000, "occurred_at": now})
        self.assertEqual(["SellReservationExecuted"], result["event_types"])
        self.assertEqual(87_000, result["account"]["available_cash_minor"])
        self.assertEqual({"AUR": 6}, result["account"]["positions"])
        self.assertEqual({}, result["account"]["reserved_quantities"])
        self.assertEqual("filled", result["account"]["orders"]["sell-execute-api"]["status"])

    def test_draft_adapter_translates_partial_market_sell_reservation_execution(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-partial-sell-api", "display_name": "Partial Sell Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_market_buy({"account_id": "acct-partial-sell-api", "order_id": "buy-partial-sell", "execution_id": "buy-partial-execution", "symbol": "AUR", "quantity": 10, "occurred_at": now})
        facade.reserve_market_sell({"account_id": "acct-partial-sell-api", "order_id": "sell-partial-api", "symbol": "AUR", "quantity": 4, "occurred_at": now})
        result = facade.execute_partial_market_sell_reservation({"account_id": "acct-partial-sell-api", "order_id": "sell-partial-api", "execution_id": "sell-partial-execution", "quantity": 2, "price_minor": 3_000, "occurred_at": now})
        self.assertEqual(["SellReservationPartiallyExecuted"], result["event_types"])
        self.assertEqual(81_000, result["account"]["available_cash_minor"])
        self.assertEqual({"AUR": 8}, result["account"]["positions"])
        self.assertEqual({"sell-partial-api": 2}, result["account"]["reserved_quantities"])
        self.assertEqual("partially_filled", result["account"]["orders"]["sell-partial-api"]["status"])

    def test_draft_adapter_translates_limit_buy_reservation(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-limit-api", "display_name": "Limit Demo", "cash_minor": 100_000, "occurred_at": now})
        result = facade.submit_limit_buy({"account_id": "acct-limit-api", "order_id": "limit-api", "symbol": "AUR", "quantity": 10, "limit_price_minor": 2_000, "occurred_at": now})
        self.assertEqual(["LimitBuyReserved"], result["event_types"])
        self.assertEqual(80_000, result["account"]["available_cash_minor"])
        self.assertEqual(20_000, result["account"]["reserved_cash_minor"])
        self.assertEqual("accepted", result["account"]["orders"]["limit-api"]["status"])

    def test_draft_adapter_translates_limit_buy_cancellation(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-cancel-api", "display_name": "Cancel Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_limit_buy({"account_id": "acct-cancel-api", "order_id": "limit-cancel-api", "symbol": "AUR", "quantity": 10, "limit_price_minor": 2_000, "occurred_at": now})
        result = facade.cancel_limit_buy({"account_id": "acct-cancel-api", "order_id": "limit-cancel-api", "occurred_at": now})
        self.assertEqual(["OrderCancelled"], result["event_types"])
        self.assertEqual(100_000, result["account"]["available_cash_minor"])
        self.assertEqual(0, result["account"]["reserved_cash_minor"])
        self.assertEqual("cancelled", result["account"]["orders"]["limit-cancel-api"]["status"])

    def test_draft_adapter_translates_limit_buy_execution(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-execute-api", "display_name": "Execute Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_limit_buy({"account_id": "acct-execute-api", "order_id": "limit-execute-api", "symbol": "AUR", "quantity": 10, "limit_price_minor": 2_000, "occurred_at": now})
        result = facade.execute_limit_buy({"account_id": "acct-execute-api", "order_id": "limit-execute-api", "execution_id": "execute-api", "price_minor": 1_800, "occurred_at": now})
        self.assertEqual(["LimitBuyExecuted"], result["event_types"])
        self.assertEqual(82_000, result["account"]["available_cash_minor"])
        self.assertEqual(0, result["account"]["reserved_cash_minor"])
        self.assertEqual({"AUR": 10}, result["account"]["positions"])
        self.assertEqual("filled", result["account"]["orders"]["limit-execute-api"]["status"])

    def test_draft_adapter_translates_partial_limit_buy_execution(self):
        facade = SimulationApiFacade(StockplayerEnvironment({"AUR": 2_500}))
        now = "2026-01-05T13:00:00Z"
        facade.open_account({"account_id": "acct-partial-api", "display_name": "Partial Demo", "cash_minor": 100_000, "occurred_at": now})
        facade.submit_limit_buy({"account_id": "acct-partial-api", "order_id": "limit-partial-api", "symbol": "AUR", "quantity": 10, "limit_price_minor": 2_000, "occurred_at": now})
        result = facade.execute_partial_limit_buy({"account_id": "acct-partial-api", "order_id": "limit-partial-api", "execution_id": "partial-api", "quantity": 4, "price_minor": 1_800, "occurred_at": now})
        self.assertEqual(["LimitBuyPartiallyExecuted"], result["event_types"])
        self.assertEqual(80_800, result["account"]["available_cash_minor"])
        self.assertEqual(12_000, result["account"]["reserved_cash_minor"])
        self.assertEqual({"AUR": 4}, result["account"]["positions"])
        self.assertEqual("partially_filled", result["account"]["orders"]["limit-partial-api"]["status"])


if __name__ == "__main__":
    unittest.main()
