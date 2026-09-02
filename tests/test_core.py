import unittest

from claude_model_sync.core import ConfigError, Model, generate_alias, normalize_models, plan_changes


class AliasTests(unittest.TestCase):
    def test_known_alias_patterns(self):
        self.assertEqual(generate_alias("claude-sonnet-4-6"), "claude-sonnet-4-6")
        self.assertEqual(generate_alias("gpt-5.6-sol"), "claude-o56-sol")
        self.assertEqual(generate_alias("gemini-3.8-flash-high"), "claude-g38-flash-high")

    def test_conflicting_alias_is_rejected(self):
        with self.assertRaises(ConfigError):
            normalize_models([
                {"alias": "claude-one", "target": "model-a"},
                {"alias": "claude-one", "target": "model-b"},
            ])

    def test_prune_is_explicit(self):
        current = [Model("claude-old", "old")]
        desired = [Model("claude-new", "new")]
        safe = plan_changes(current, desired, prune=False)
        destructive = plan_changes(current, desired, prune=True)
        self.assertEqual(safe["removed"], [])
        self.assertEqual(len(safe["models"]), 2)
        self.assertEqual([row["alias"] for row in destructive["removed"]], ["claude-old"])


if __name__ == "__main__":
    unittest.main()
