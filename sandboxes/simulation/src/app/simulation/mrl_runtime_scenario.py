from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.application.purchase import SubmitMarketBuy
from app.simulation.environment import StockplayerEnvironment
from mrl_simulation_runtime.actors import Actor
from mrl_simulation_runtime.invariants import Invariant
from mrl_simulation_runtime.scenario import InitialScheduledAction, ObservatoryEdge, ObservatoryNode, Scenario

INITIAL_TIME = datetime(2026, 1, 5, 13, 0, tzinfo=timezone.utc)


def create_simulation() -> Scenario:
    environment = StockplayerEnvironment({"AUR": 2_500})

    def fund_account(context) -> None:
        environment.open_funded_account("acct-demo", "Demo Architect", 100_000, context.clock.now())
        context.environment = environment
        context.emit("domain_events", "account_opened_and_funded", source="Stockplayer", actor="demo-user", correlation_id="setup-001", payload={"account_id": "acct-demo", "cash_minor": 100_000})

    def purchase(context) -> None:
        events = environment.buy(SubmitMarketBuy("acct-demo", "order-001", "execution-001", "AUR", 10, context.clock.now()))
        context.emit("command", "market_buy_submitted", source="DemoUser", actor="demo-user", correlation_id="order-001", payload={"symbol": "AUR", "quantity": 10})
        context.emit("domain_events", "market_buy_executed", source="Stockplayer", actor="demo-user", correlation_id="order-001", payload={"event_count": len(events), "cash_minor": environment.projections.cash_minor["acct-demo"], "position_quantity": environment.projections.positions[("acct-demo", "AUR")]})

    return Scenario(
        name="stockplayer-simple-purchase", seed=20260105,
        initial_time=INITIAL_TIME, run_id="simple-purchase-20260105",
        actors=[Actor("demo-user")],
        scheduled_actions=[
            InitialScheduledAction(INITIAL_TIME, fund_account, "fund_account", "Stockplayer", "setup-001"),
            InitialScheduledAction(INITIAL_TIME + timedelta(seconds=1), purchase, "submit_market_buy", "DemoUser", "order-001"),
        ],
        invariants=[
            Invariant("cash never negative", lambda context: not hasattr(context, "environment") or all(value >= 0 for value in context.environment.projections.cash_minor.values())),
            Invariant("ledger explains cash", lambda context: not hasattr(context, "environment") or all(sum(entry.amount_minor for entry in context.environment.projections.ledger[account_id]) == cash for account_id, cash in context.environment.projections.cash_minor.items())),
        ],
        observatory_nodes=[
            ObservatoryNode("actor", "Demo user", "actor", "simulation"),
            ObservatoryNode("use-case", "Submit market buy", "use_case", "application"),
            ObservatoryNode("account", "Account", "aggregate", "domain"),
            ObservatoryNode("projections", "Ledger and position", "projection", "application"),
        ],
        observatory_edges=[
            ObservatoryEdge("actor", "use-case", "submits"),
            ObservatoryEdge("use-case", "account", "decides"),
            ObservatoryEdge("account", "projections", "events update"),
        ],
    )
