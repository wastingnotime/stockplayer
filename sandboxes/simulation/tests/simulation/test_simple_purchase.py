import pathlib
import json
import sys
import unittest

ROOT = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path.home() / ".wnt/runtime/mrl"))

from app.simulation.mrl_runtime_scenario import create_simulation
from mrl_simulation_runtime.runner import SimulationRunner


class SimplePurchaseScenarioTests(unittest.TestCase):
    def test_observatory_graph_covers_built_simulation_boundaries(self):
        scenario = create_simulation()
        node_ids = {node.id for node in scenario.observatory_nodes}
        self.assertEqual(
            {
                "actor", "use-case", "account", "projections", "market", "session",
                "price-history", "orders", "reservations", "recovery", "engines", "invariants",
            },
            node_ids,
        )
        edges = {(edge.from_node, edge.to_node, edge.label) for edge in scenario.observatory_edges}
        self.assertIn(("recovery", "projections", "rebuilds from events"), edges)
        self.assertIn(("use-case", "engines", "compares candidates"), edges)
        self.assertIn(("projections", "invariants", "checked by"), edges)

    def test_run_is_deterministic_and_invariants_pass(self):
        first = SimulationRunner().run(create_simulation()).observations.to_jsonl()
        second = SimulationRunner().run(create_simulation()).observations.to_jsonl()

        self.assertEqual(first, second)
        self.assertIn('"cash_minor": 75000', first)
        self.assertIn('"name": "price_tick"', first)
        self.assertIn('"name": "unrealized_result_updated"', first)
        self.assertIn('"name": "market_session_opened"', first)
        self.assertIn('"name": "market_session_closed"', first)
        self.assertIn('"name": "projection_failed_after_append"', first)
        self.assertIn('"name": "projection_rebuilt"', first)
        self.assertIn('"name": "order_status_updated"', first)
        self.assertIn('"name": "order_status_recovered"', first)
        self.assertIn('"name": "execution_engines_compared"', first)
        self.assertIn('"fill_delta": 4', first)
        self.assertIn('"engine_versions": ["v1-full-fill", "v2-liquidity-capped"]', first)
        self.assertIn('"price_minor": 2594', first)
        self.assertNotIn('"passed": false', first)

        comparison = next(json.loads(line) for line in first.splitlines() if json.loads(line)["name"] == "execution_engines_compared")
        self.assertEqual("engine-001", comparison["correlation_id"])
        self.assertEqual("2026-01-05T13:00:02.750000+00:00", comparison["sim_time"])
        self.assertEqual(
            {"request_quantity", "price_minor", "liquidity", "engine_versions", "decisions", "fill_delta"},
            set(comparison["payload"]),
        )
        self.assertEqual(4, comparison["payload"]["fill_delta"])
        self.assertEqual([0, 4], [decision["filled_quantity"] for decision in comparison["payload"]["decisions"]])


if __name__ == "__main__":
    unittest.main()
