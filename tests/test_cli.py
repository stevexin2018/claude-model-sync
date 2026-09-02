import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
        return subprocess.run(
            [sys.executable, "-m", "claude_model_sync", "--json", *args],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_plan_apply_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            config.write_text(json.dumps({
                "source": {"type": "inline"},
                "models": ["gpt-5.6-sol"],
                "output": {"manifest": "models.json"},
            }), encoding="utf-8")
            planned = self.run_cli(root, "plan", "--config", str(config))
            self.assertEqual(planned.returncode, 0, planned.stderr)
            self.assertTrue(json.loads(planned.stdout)["changed"])
            denied = self.run_cli(root, "apply", "--config", str(config))
            self.assertEqual(denied.returncode, 1)
            applied = self.run_cli(root, "apply", "--config", str(config), "--yes")
            self.assertEqual(applied.returncode, 0, applied.stderr)
            verified = self.run_cli(root, "verify", "--config", str(config))
            self.assertEqual(verified.returncode, 0, verified.stdout)


if __name__ == "__main__":
    unittest.main()
