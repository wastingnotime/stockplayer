import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path.home() / ".wnt/runtime/mrl"))

from app.simulation.mrl_runtime_scenario import create_simulation
from mrl_simulation_runtime.runner import SimulationRunner


class SimplePurchaseScenarioTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
