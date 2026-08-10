import pathlib
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "src"))

from app.application.purchase import CancelLimitBuy, CancelMarketSellReservation, ExecuteLimitBuy, ExecuteMarketSellReservation, ExecutePartialLimitBuy, ExecutePartialMarketSellReservation, SubmitLimitBuy, SubmitMarketBuy, SubmitMarketSell, SubmitMarketSellReservation
from app.domain.model import Account, DomainError, LimitBuyExecuted, LimitBuyPartiallyExecuted, LimitBuyReserved, MarketSellExecuted, OrderCancelled, OrderRejected, SellQuantityReserved, SellReservationCancelled, SellReservationExecuted, SellReservationPartiallyExecuted
from app.infrastructure.memory import AccountProjections, OrderView, ProjectionFailure
from app.simulation.invariants import cash_non_negative, ledger_explains_total_cash, positions_non_negative, reservations_non_negative
from app.simulation.catalog import SCENARIOS, get_scenario, implemented_scenarios
from app.domain.market import DeterministicPriceGenerator, MarketSession, PriceHistory, PriceTick, SessionState
from app.domain.engines import ExecutionDecision, ExecutionRequest, FullFillEngineV1, LiquidityCappedEngineV2, compare_engines, comparison_payload
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

    def test_cancellation_releases_cash_and_replay_closes_reservation(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))

        events = environment.cancel_limit_buy(CancelLimitBuy("account-1", "limit-1", NOW))
        self.assertIsInstance(events[0], OrderCancelled)
        self.assertEqual(100_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(0, environment.projections.reserved_cash_minor["account-1"])
        replayed = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(100_000, replayed.available_cash_minor)
        self.assertEqual(0, replayed.reserved_cash_minor)
        self.assertEqual({}, replayed.reservations)

    def test_cancelling_missing_order_does_not_append_a_fact(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        before = environment.store.load("account-1")

        with self.assertRaisesRegex(DomainError, "not found"):
            environment.cancel_limit_buy(CancelLimitBuy("account-1", "missing", NOW))

        self.assertEqual(before, environment.store.load("account-1"))
        self.assertEqual(100_000, environment.projections.cash_minor["account-1"])

    def test_limit_buy_executes_below_limit_and_releases_unused_reservation(self):
        environment = StockplayerEnvironment({"AUR": 1_800})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))

        events = environment.execute_limit_buy(ExecuteLimitBuy("account-1", "limit-1", "execution-1", 1_800, NOW))
        self.assertIsInstance(events[0], LimitBuyExecuted)
        self.assertEqual(64_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(0, environment.projections.reserved_cash_minor["account-1"])
        self.assertEqual(20, environment.projections.positions[("account-1", "AUR")])
        self.assertEqual(-36_000, environment.projections.ledger["account-1"][-1].amount_minor)
        replayed = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(64_000, replayed.available_cash_minor)
        self.assertEqual({}, replayed.reservations)

    def test_limit_buy_above_limit_does_not_consume_reservation(self):
        environment = StockplayerEnvironment({"AUR": 2_100})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))

        with self.assertRaisesRegex(DomainError, "exceeds limit"):
            environment.execute_limit_buy(ExecuteLimitBuy("account-1", "limit-1", "execution-1", 2_100, NOW))

        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(40_000, account.reserved_cash_minor)

    def test_partial_execution_preserves_remaining_quantity_and_hold(self):
        environment = StockplayerEnvironment({"AUR": 1_800})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))

        events = environment.execute_partial_limit_buy(
            ExecutePartialLimitBuy("account-1", "limit-1", "execution-1", 10, 1_800, NOW)
        )
        self.assertIsInstance(events[0], LimitBuyPartiallyExecuted)
        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(62_000, account.available_cash_minor)
        self.assertEqual(20_000, account.reserved_cash_minor)
        self.assertEqual(10, account.reservation_details["limit-1"][1])
        self.assertEqual(10, account.positions["AUR"])

        environment.execute_limit_buy(
            ExecuteLimitBuy("account-1", "limit-1", "execution-2", 1_700, NOW)
        )
        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(65_000, account.available_cash_minor)
        self.assertEqual(0, account.reserved_cash_minor)
        self.assertEqual(20, account.positions["AUR"])

    def test_duplicate_execution_command_and_projection_are_idempotent(self):
        environment = StockplayerEnvironment({"AUR": 1_800})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))
        command = ExecutePartialLimitBuy("account-1", "limit-1", "execution-1", 10, 1_800, NOW)
        first = environment.execute_partial_limit_buy(command)
        before = Account.rehydrate(environment.store.load("account-1"))

        self.assertEqual([], environment.execute_partial_limit_buy(command))
        environment.projections.project(first)
        after = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(before.available_cash_minor, after.available_cash_minor)
        self.assertEqual(before.reserved_cash_minor, after.reserved_cash_minor)
        self.assertEqual(before.positions, after.positions)
        self.assertEqual(2, len(environment.projections.ledger["account-1"]))
        self.assertTrue(cash_non_negative(environment.projections))
        self.assertTrue(positions_non_negative(environment.projections))
        self.assertTrue(reservations_non_negative(environment.projections))
        self.assertTrue(ledger_explains_total_cash(environment.projections))

    def test_scenario_catalog_has_unique_ids_and_explicit_planned_boundaries(self):
        ids = [scenario.scenario_id for scenario in SCENARIOS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual("implemented", get_scenario("simple_purchase").status)
        self.assertEqual("implemented", get_scenario("sell_reservation").status)
        self.assertGreaterEqual(len(implemented_scenarios()), 10)
        with self.assertRaises(KeyError):
            get_scenario("does-not-exist")

    def test_sell_reservation_reduces_available_owned_quantity(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))
        accepted = environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-1", "AUR", 6, NOW))
        rejected = environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-2", "AUR", 5, NOW))
        self.assertIsInstance(accepted[0], SellQuantityReserved)
        self.assertIsInstance(rejected[0], OrderRejected)
        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(10, account.positions["AUR"])
        self.assertEqual(6, account.reserved_quantities["sell-res-1"])

    def test_sell_reservation_cancellation_releases_quantity(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))
        environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-1", "AUR", 6, NOW))

        events = environment.cancel_sell_reservation(CancelMarketSellReservation("account-1", "sell-res-1", NOW))
        self.assertIsInstance(events[0], SellReservationCancelled)
        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual({}, account.reserved_quantities)
        accepted = environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-2", "AUR", 10, NOW))
        self.assertIsInstance(accepted[0], SellQuantityReserved)

    def test_sell_reservation_execution_consumes_hold_and_settles_proceeds(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))
        environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-1", "AUR", 6, NOW))

        direct = environment.sell(SubmitMarketSell("account-1", "sell-direct", "execution-direct", "AUR", 5, 3_000, NOW))
        self.assertIsInstance(direct[0], OrderRejected)
        events = environment.execute_sell_reservation(ExecuteMarketSellReservation("account-1", "sell-res-1", "execution-res", 3_000, NOW))
        self.assertIsInstance(events[0], SellReservationExecuted)
        self.assertEqual(93_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(4, environment.projections.positions[("account-1", "AUR")])
        self.assertEqual({}, Account.rehydrate(environment.store.load("account-1")).reserved_quantities)

    def test_partial_sell_reservation_execution_preserves_remaining_hold(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))
        environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-1", "AUR", 6, NOW))

        events = environment.execute_partial_sell_reservation(ExecutePartialMarketSellReservation("account-1", "sell-res-1", "execution-partial", 2, 3_000, NOW))
        self.assertIsInstance(events[0], SellReservationPartiallyExecuted)
        account = Account.rehydrate(environment.store.load("account-1"))
        self.assertEqual(8, account.positions["AUR"])
        self.assertEqual(4, account.reserved_quantities["sell-res-1"])
        self.assertEqual(81_000, environment.projections.cash_minor["account-1"])

    def test_order_status_projection_tracks_partial_and_rejected_lifecycles(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))
        environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-1", "AUR", 6, NOW))
        environment.execute_partial_sell_reservation(ExecutePartialMarketSellReservation("account-1", "sell-res-1", "execution-partial", 2, 3_000, NOW))
        view = environment.projections.orders[("account-1", "sell-res-1")]
        self.assertEqual(OrderView("sell", "AUR", 6, 4, "partially_filled"), view)
        rejected = environment.reserve_sell(SubmitMarketSellReservation("account-1", "sell-res-2", "AUR", 9, NOW))
        self.assertEqual("rejected", environment.projections.orders[("account-1", "sell-res-2")].status)

    def test_repeating_same_order_command_is_a_no_op_even_with_new_execution_id(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        first = environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-1", "AUR", 10, NOW))
        before = environment.store.load("account-1")
        second = environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-2", "AUR", 10, NOW))
        self.assertEqual(1, len(first))
        self.assertEqual([], second)
        self.assertEqual(before, environment.store.load("account-1"))
        self.assertEqual(75_000, environment.projections.cash_minor["account-1"])

    def test_projection_rebuild_matches_incremental_projection(self):
        environment = StockplayerEnvironment({"AUR": 1_800})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.limit_buy(SubmitLimitBuy("account-1", "limit-1", "AUR", 20, 2_000, NOW))
        environment.execute_partial_limit_buy(
            ExecutePartialLimitBuy("account-1", "limit-1", "execution-1", 10, 1_800, NOW)
        )

        rebuilt = AccountProjections()
        rebuilt.rebuild(environment.store.load("account-1"))
        self.assertEqual(environment.projections.cash_minor, rebuilt.cash_minor)
        self.assertEqual(environment.projections.reserved_cash_minor, rebuilt.reserved_cash_minor)
        self.assertEqual(environment.projections.reservations, rebuilt.reservations)
        self.assertEqual(environment.projections.ledger, rebuilt.ledger)
        self.assertEqual(environment.projections.positions, rebuilt.positions)
        self.assertEqual(environment.projections.position_cost_minor, rebuilt.position_cost_minor)
        self.assertEqual(environment.projections.realized_result_minor, rebuilt.realized_result_minor)

    def test_market_sell_settles_proceeds_and_prevents_short_selling(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy", "AUR", 10, NOW))

        events = environment.sell(SubmitMarketSell("account-1", "sell-1", "execution-sell", "AUR", 4, 3_000, NOW))
        self.assertIsInstance(events[0], MarketSellExecuted)
        self.assertEqual(87_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(6, environment.projections.positions[("account-1", "AUR")])

        rejected = environment.sell(SubmitMarketSell("account-1", "sell-2", "execution-sell-2", "AUR", 7, 3_000, NOW))
        self.assertIsInstance(rejected[0], OrderRejected)
        self.assertEqual("insufficient owned quantity", rejected[0].reason)
        self.assertEqual(6, Account.rehydrate(environment.store.load("account-1")).positions["AUR"])

    def test_position_cost_and_realized_result_use_deterministic_floor_rounding(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-buy-1", "AUR", 10, NOW))
        environment.market.prices["AUR"] = 3_000
        environment.buy(SubmitMarketBuy("account-1", "buy-2", "execution-buy-2", "AUR", 5, NOW))

        self.assertEqual(15, environment.projections.positions[("account-1", "AUR")])
        self.assertEqual(2_666, environment.projections.average_cost_minor("account-1", "AUR"))
        self.assertEqual(5_000, environment.projections.unrealized_result_minor("account-1", "AUR", 3_000))
        environment.sell(SubmitMarketSell("account-1", "sell-1", "execution-sell", "AUR", 5, 3_000, NOW))
        self.assertEqual(10, environment.projections.positions[("account-1", "AUR")])
        self.assertEqual(2_666, environment.projections.average_cost_minor("account-1", "AUR"))
        self.assertEqual(1_667, environment.projections.realized_result_minor[("account-1", "AUR")])
        self.assertEqual(3_333, environment.projections.unrealized_result_minor("account-1", "AUR", 3_000))

    def test_price_ticks_are_sequenced_and_rebuildable(self):
        history = PriceHistory()
        history.append(PriceTick("AUR", 2_500, 1, NOW, 42))
        history.append(PriceTick("AUR", 2_700, 2, NOW, 42))
        self.assertEqual(2_700, history.price_minor("AUR"))

        rebuilt = PriceHistory()
        rebuilt.rebuild(history.events)
        self.assertEqual(history.current, rebuilt.current)
        self.assertEqual(history.events, rebuilt.events)
        with self.assertRaisesRegex(ValueError, "expected price sequence"):
            history.append(PriceTick("AUR", 2_800, 4, NOW, 42))

    def test_seeded_price_generation_is_reproducible(self):
        def generate():
            generator = DeterministicPriceGenerator(42)
            price = 2_500
            ticks = []
            for sequence in range(1, 4):
                tick = generator.next_tick("AUR", price, sequence, NOW)
                ticks.append(tick)
                price = tick.price_minor
            return ticks

        first_ticks = generate()
        second_ticks = generate()
        self.assertEqual(first_ticks, second_ticks)
        self.assertTrue(all(t.source_seed == 42 and t.price_minor > 0 for t in first_ticks))

    def test_market_session_transitions_are_replayable_and_closed_is_terminal(self):
        session = MarketSession()
        session.open(NOW)
        session.pause(NOW)
        session.open(NOW)
        session.close(NOW)
        self.assertEqual(SessionState.CLOSED, session.state)
        rebuilt = MarketSession()
        rebuilt.rebuild(session.events)
        self.assertEqual(session.state, rebuilt.state)
        self.assertEqual(session.events, rebuilt.events)
        with self.assertRaisesRegex(ValueError, "cannot transition"):
            session.open(NOW)

    def test_engine_comparison_is_deterministic_and_surfaces_partial_fill_difference(self):
        request = ExecutionRequest("order-1", "AUR", 10, 2_500, 4)
        first = compare_engines(request, (FullFillEngineV1(), LiquidityCappedEngineV2()))
        second = compare_engines(request, (FullFillEngineV1(), LiquidityCappedEngineV2()))
        self.assertEqual(first, second)
        self.assertEqual((0, 4), tuple(decision.filled_quantity for decision in first))
        self.assertEqual(("insufficient liquidity for full fill", "partial fill"), tuple(decision.reason for decision in first))

    def test_engine_comparison_rejects_empty_or_duplicate_engine_sets(self):
        request = ExecutionRequest("order-1", "AUR", 10, 2_500, 4)
        with self.assertRaises(ValueError):
            compare_engines(request, ())
        with self.assertRaises(ValueError):
            compare_engines(request, (FullFillEngineV1(), FullFillEngineV1()))

    def test_comparison_payload_preserves_engine_order_and_delta(self):
        request = ExecutionRequest("order-1", "AUR", 10, 2_500, 4)
        decisions = compare_engines(request, (FullFillEngineV1(), LiquidityCappedEngineV2()))
        payload = comparison_payload(request, decisions)
        self.assertEqual(["v1-full-fill", "v2-liquidity-capped"], payload["engine_versions"])
        self.assertEqual(4, payload["fill_delta"])

    def test_execution_decision_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            ExecutionDecision("v1", "order-1", -1, 2_500, "invalid")
        with self.assertRaises(ValueError):
            ExecutionDecision("v1", "order-1", True, 2_500, "invalid")

    def test_execution_request_rejects_boolean_numeric_values(self):
        with self.assertRaises(ValueError):
            ExecutionRequest("order-1", "AUR", True, 2_500, 1)
        with self.assertRaises(ValueError):
            ExecutionRequest("order-1", "AUR", 1, 2_500, False)
        with self.assertRaises(ValueError):
            ExecutionRequest(1, "AUR", 1, 2_500, 1)

    def test_liquidity_capped_engine_handles_zero_and_full_liquidity(self):
        engine = LiquidityCappedEngineV2()
        no_liquidity = engine.decide(ExecutionRequest("order-1", "AUR", 2, 2_500, 0))
        full_liquidity = engine.decide(ExecutionRequest("order-2", "AUR", 2, 2_500, 2))
        self.assertEqual((0, "no liquidity"), (no_liquidity.filled_quantity, no_liquidity.reason))
        self.assertEqual((2, "full fill"), (full_liquidity.filled_quantity, full_liquidity.reason))

    def test_engine_comparison_rejects_decisions_that_change_request_or_overfill(self):
        request = ExecutionRequest("order-1", "AUR", 2, 2_500, 2)

        class InvalidEngine:
            version = "invalid"

            def decide(self, request):
                return ExecutionDecision(self.version, "other-order", 3, request.price_minor + 1, "invalid")

        with self.assertRaises(ValueError):
            compare_engines(request, (InvalidEngine(),))

    def test_closed_session_rejects_new_buy_without_economic_effect(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.session.close(NOW)
        before = environment.store.load("account-1")

        events = environment.buy(SubmitMarketBuy("account-1", "buy-closed", "execution-closed", "AUR", 1, NOW))
        self.assertIsInstance(events[0], OrderRejected)
        self.assertEqual("market session is not open", events[0].reason)
        self.assertEqual(100_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(before + events, environment.store.load("account-1"))

    def test_projection_failure_after_append_recovers_from_event_history(self):
        environment = StockplayerEnvironment({"AUR": 2_500})
        environment.open_funded_account("account-1", "Ada", 100_000, NOW)
        environment.fail_next_projection()

        with self.assertRaisesRegex(ProjectionFailure, "injected"):
            environment.buy(SubmitMarketBuy("account-1", "buy-1", "execution-1", "AUR", 10, NOW))

        history = environment.store.load("account-1")
        self.assertEqual(3, len(history))
        self.assertEqual(100_000, environment.projections.cash_minor["account-1"])
        environment.projections.rebuild(history)
        self.assertEqual(75_000, environment.projections.cash_minor["account-1"])
        self.assertEqual(10, environment.projections.positions[("account-1", "AUR")])
        self.assertEqual(2, len(environment.projections.ledger["account-1"]))


if __name__ == "__main__":
    unittest.main()
