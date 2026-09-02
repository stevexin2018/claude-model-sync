import json
import tempfile
import unittest
from pathlib import Path

from claude_model_sync.core import Model
from claude_model_sync.state import apply_plan, make_plan, rollback


class StateTests(unittest.TestCase):
    def test_apply_is_idempotent_and_rollback_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "models.json"
            first_models = [Model("claude-a", "a")]
            first = make_plan(output, first_models, prune=True)
            first_result = apply_plan(output, first, "test")
            self.assertTrue(first_result["changed"])
            self.assertFalse(make_plan(output, first_models, prune=True)["changed"])

            second_models = [Model("claude-b", "b")]
            second = make_plan(output, second_models, prune=True)
            second_result = apply_plan(output, second, "test")
            rollback(Path(second_result["transaction"]))
            restored = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(restored["models"][0]["alias"], "claude-a")


if __name__ == "__main__":
    unittest.main()
