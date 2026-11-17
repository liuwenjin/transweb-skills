import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "transweb_create.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )


class CliTests(unittest.TestCase):
    def test_help(self):
        result = run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("selftest", result.stdout)
        self.assertNotIn("ppt", result.stdout)

    def test_selftest_json(self):
        result = run("selftest", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill"], "transweb-create")

    def test_version(self):
        result = run("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1.0.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
