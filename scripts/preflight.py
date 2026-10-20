"""Run the public repository's offline validation, tests and integrity checks."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    checks = (
        ("Caller arguments", ["scripts/validate.py", "--arguments", "examples/tool-arguments.json"]),
        ("Outgoing payload", ["scripts/validate.py", "--payload", "examples/contact-payload.json"]),
        ("Regression tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("Repository integrity", ["scripts/check_repository.py"]),
    )
    for label, arguments in checks:
        print(f"Checking: {label}", flush=True)
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, check=False)
        if result.returncode:
            print(f"Preflight failed: {label}", file=sys.stderr)
            return 1
    print("Offline preflight passed. No contact requests sent; live account behavior remains unverified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
