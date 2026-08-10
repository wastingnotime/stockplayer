from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.application.purchase import SubmitMarketBuy
from app.domain.engines import FullFillEngineV1, LiquidityCappedEngineV2, ExecutionRequest, compare_engines, comparison_payload
from app.domain.market import DeterministicPriceGenerator, PriceHistory
from app.infrastructure.memory import ProjectionFailure
from app.simulation.invariants import cash_non_negative, ledger_explains_total_cash, positions_non_negative, reservations_non_negative
from app.simulation.environment import StockplayerEnvironment
from mrl_simulation_runtime.actors import Actor
from mrl_simulation_runtime.invariants import Invariant
from mrl_simulation_runtime.scenario import InitialScheduledAction, ObservatoryEdge, ObservatoryNode, Scenario

INITIAL_TIME = datetime(2026, 1, 5, 13, 0, tzinfo=timezone.utc)


def create_simulation() -> Scenario:
    environment = StockplayerEnvironment({"AUR": 2_500})
    price_history = PriceHistory()
    price_generator = DeterministicPriceGenerator(20260105)

    def fund_account(context) -> None:
        environment.open_funded_account("acct-demo", "Demo Architect", 100_000, context.clock.now())
        context.environment = environment
        context.emit("domain_events", "account_opened_and_funded", source="Stockplayer", actor="demo-user", correlation_id="setup-001", payload={"account_id": "acct-demo", "cash_minor": 100_000})
        context.emit("market_state", "market_session_opened", source="Stockplayer", actor="market-simulator", correlation_id="session-001", payload={"state": environment.session.state.value})

    def purchase(context) -> None:
        events = environment.buy(SubmitMarketBuy("acct-demo", "order-001", "execution-001", "AUR", 10, context.clock.now()))
        context.emit("command", "market_buy_submitted", source="DemoUser", actor="demo-user", correlation_id="order-001", payload={"symbol": "AUR", "quantity": 10})
        context.emit("domain_events", "market_buy_executed", source="Stockplayer", actor="demo-user", correlation_id="order-001", payload={"event_count": len(events), "cash_minor": environment.projections.cash_minor["acct-demo"], "position_quantity": environment.projections.positions[("acct-demo", "AUR")]})
        order = environment.projections.orders[("acct-demo", "order-001")]
        context.emit("projection", "order_status_updated", source="Stockplayer", actor="projection-worker", correlation_id="order-001", payload={"order_id": "order-001", "status": order.status, "remaining_quantity": order.remaining_quantity})

    def advance_market(context) -> None:
        tick = price_generator.next_tick("AUR", environment.market.price_minor("AUR"), 1, context.clock.now())
        price_history.append(tick)
        environment.market.prices["AUR"] = tick.price_minor
        unrealized = environment.projections.unrealized_result_minor("acct-demo", "AUR", tick.price_minor)
        context.emit("market_fact", "price_tick", source="SeededMarket", actor="market-simulator", correlation_id="price-001", payload={"symbol": tick.symbol, "price_minor": tick.price_minor, "sequence": tick.sequence, "source_seed": tick.source_seed})
        context.emit("projection", "unrealized_result_updated", source="Stockplayer", actor="market-simulator", correlation_id="price-001", payload={"symbol": "AUR", "unrealized_result_minor": unrealized})

    def fail_and_recover_projection(context) -> None:
        environment.fail_next_projection()
        try:
            environment.buy(SubmitMarketBuy("acct-demo", "order-002", "execution-002", "AUR", 1, context.clock.now()))
        except ProjectionFailure:
            history = environment.store.load("acct-demo")
            context.emit("failure", "projection_failed_after_append", source="Stockplayer", actor="projection-worker", correlation_id="recovery-001", payload={"stream_event_count": len(history)})
            environment.projections.rebuild(history)
            context.emit("recovery", "projection_rebuilt", source="Stockplayer", actor="projection-worker", correlation_id="recovery-001", payload={"cash_minor": environment.projections.cash_minor["acct-demo"], "position_quantity": environment.projections.positions[("acct-demo", "AUR")]})
            order = environment.projections.orders[("acct-demo", "order-002")]
            context.emit("projection", "order_status_recovered", source="Stockplayer", actor="projection-worker", correlation_id="recovery-001", payload={"order_id": "order-002", "status": order.status, "remaining_quantity": order.remaining_quantity})

    def compare_execution_engines(context) -> None:
        request = ExecutionRequest("candidate-order", "AUR", 10, environment.market.price_minor("AUR"), 4)
        decisions = compare_engines(request, (FullFillEngineV1(), LiquidityCappedEngineV2()))
        context.emit("engine_comparison", "execution_engines_compared", source="Stockplayer", actor="engine-lab", correlation_id="engine-001", payload=comparison_payload(request, decisions))

    def close_market(context) -> None:
        environment.session.close(context.clock.now())
        context.emit("market_state", "market_session_closed", source="Stockplayer", actor="market-simulator", correlation_id="session-002", payload={"state": environment.session.state.value})

    return Scenario(
        name="stockplayer-simple-purchase", seed=20260105,
        initial_time=INITIAL_TIME, run_id="simple-purchase-20260105",
        actors=[Actor("demo-user")],
        scheduled_actions=[
            InitialScheduledAction(INITIAL_TIME, fund_account, "fund_account", "Stockplayer", "setup-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(seconds=1), purchase, "submit_market_buy", "DemoUser", "order-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(seconds=2), advance_market, "advance_market_price", "SeededMarket", "price-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(milliseconds=2500), fail_and_recover_projection, "fail_and_recover_projection", "Stockplayer", "recovery-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(milliseconds=2750), compare_execution_engines, "compare_execution_engines", "Stockplayer", "engine-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(seconds=3), close_market, "close_market_session", "Stockplayer", "session-002"),
        ],
        invariants=[
            Invariant("cash never negative", lambda context: not hasattr(context, "environment") or cash_non_negative(context.environment.projections)),
            Invariant("positions never negative", lambda context: not hasattr(context, "environment") or positions_non_negative(context.environment.projections)),
            Invariant("reservations never negative", lambda context: not hasattr(context, "environment") or reservations_non_negative(context.environment.projections)),
            Invariant("ledger explains total cash", lambda context: not hasattr(context, "environment") or ledger_explains_total_cash(context.environment.projections)),
        ],
        observatory_nodes=[
            ObservatoryNode("actor", "Demo user", "actor", "simulation"),
            ObservatoryNode("use-case", "Submit market buy", "use_case", "application"),
            ObservatoryNode("account", "Account", "aggregate", "domain"),
            ObservatoryNode("projections", "Ledger and position", "projection", "application"),
            ObservatoryNode("market", "Seeded market", "provider", "simulation"),
        ],
        observatory_edges=[
            ObservatoryEdge("actor", "use-case", "submits"),
            ObservatoryEdge("use-case", "account", "decides"),
            ObservatoryEdge("account", "projections", "events update"),
            ObservatoryEdge("market", "projections", "valuation input"),
        ],
    )
