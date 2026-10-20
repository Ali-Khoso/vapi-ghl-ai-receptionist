from contextlib import redirect_stderr, redirect_stdout
import io
import subprocess
import unittest
from unittest.mock import patch

from scripts.preflight import ROOT, main


class PreflightTests(unittest.TestCase):
    def test_failed_validation_stops_before_test_execution(self):
        failure = subprocess.CompletedProcess([], 1)
        with patch("scripts.preflight.subprocess.run", return_value=failure) as run:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as output:
                self.assertEqual(1, main())
            self.assertEqual(1, run.call_count)
            self.assertEqual(ROOT, run.call_args.kwargs["cwd"])
            self.assertIn("Caller arguments", output.getvalue())


if __name__ == "__main__":
    unittest.main()
