import pathlib
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "src"))

from app.application.purchase import SubmitLimitBuy, SubmitMarketBuy
from app.domain.model import Account, DomainError, LimitBuyReserved, OrderRejected
from app.simulation.environment import StockplayerEnvironment


NOW = datetime(2026, 1, 5, 13, 0, tzinfo=timezone.utc)


class AccountTests(unittest.TestCase):
    def test_purchase_is_exact_and_replayable(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "order-1", "execution-1", "AUR", 10, NOW))

        history = environment.store.load("account-1")
        replayed = Account.rehydrate(history)

        self.assertEqual(75_000, replayed.available_cash_minor)
        self.assertEqual(10, replayed.positions["AUR"])
        self.assertEqual(75_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(25_000, -environment.projections.ledger["account-1"][-1].amount_minor)

    def test_insufficient_cash_has_no_economic_effect(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 1_000, NOW)
        before = environment.store.load("account-1")

        events = environment.buy(SubmitMarketBuy("account-1", "order-1", "execution-1", "AUR", 10, NOW))

        self.assertEqual(1, len(events))
        self.assertIsInstance(events[0], OrderRejected)
        self.assertEqual("insufficient available cash", events[0].reason)
        self.assertEqual(before + events, environment.store.load("account-1"))
        self.assertEqual(1_000, environment.projections.cash_minor["account-1"])
        replayed = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(1_000, replayed.available_cash_minor)
        self.assertEqual({}, replayed.positions)

    def test_binary_floats_and_non_positive_values_are_rejected(self):
        account = Account()
        account.open("account-1", "Ada", NOW)
        with self.assertRaises(ValueError):
            account.deposit(10.5, NOW)
        with self.assertRaises(ValueError):
            account.deposit(0, NOW)

    def test_limit_buy_reserves_available_cash_and_rejects_competing_order(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)

        accepted = environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))
        rejected = environment.limit_buy(SubmitLimitBuy("account-1", "limit-2", "AUR", 31, 2_000, NOW))

        self.assertIsInstance(accepted[0], LimitBuyReserved)
        self.assertIsInstance(rejected[0], OrderRejected)
        self.assertEqual(60_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(40_000, environment.projections.reserved_cash_minor["account-1"])
        self.assertEqual(40_000, Account.rehydrate(environment.store.load("account-1")).reserved_cash_minor)


if __name__ == "__main__":
    unittest.main()
