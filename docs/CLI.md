# Offline command reference

Use Python 3.11 or newer and install `requirements-dev.txt` first. Commands below run from the repository root. None sends requests to Vapi or GHL.

## Full preflight

```sh
python scripts/preflight.py
```

Runs caller-argument validation, outgoing-payload validation, regression tests and repository integrity checks in order. It stops at the first failure and uses the same Python interpreter for every step. CI runs this command on Windows and Linux with Python 3.11 and 3.14. Whitespace is checked separately with Git.

The runner always checks the public template and synthetic fixtures. For private configuration, use the validator directly.

## Individual validation

```sh
python scripts/validate.py --help
python scripts/validate.py --arguments examples/tool-arguments.json
python scripts/validate.py --payload examples/contact-payload.json
python scripts/validate.py --tool config/account.private.json --configured
python scripts/validate.py --tool config/account.private.json --payload examples/contact.private.json --configured
```

Create private copies as described in [setup](SETUP.md) before using the last two commands. `--arguments` and `--payload` are mutually exclusive. Arguments contain three caller fields; a payload additionally contains the fixed `locationId`, which must match the tool destination. `--configured` rejects known placeholder identifiers but does not establish that identifiers exist or have permission.

JSON input must use UTF-8, with an optional BOM. Duplicate keys, NaN, Infinity and numeric exponents that overflow to infinity are rejected. Error messages omit submitted values. Unreadable files and parser recursion failures return validation errors.

## JSON reports

```sh
python scripts/validate.py --json --payload examples/contact-payload.json
```

Example success output:

```json
{"ok": true, "mode": "template placeholders allowed", "errors": [], "request_sent": false}
```

With `--json`, validation results go to stdout on both success and failure. `errors` contains redacted rule descriptions; `mode` changes to `configured identifiers` with `--configured`. Invalid command-line syntax still uses argparse's text output on stderr.

| Exit code | Meaning |
| --- | --- |
| 0 | Offline validation passed |
| 1 | Validation failed, input could not be read, or a dependency is missing |
| 2 | Invalid CLI syntax, including conflicting input options |

Missing dependencies are reported before argument parsing and produce text rather than a JSON report. A successful offline report does not verify credentials, live schema enforcement or contact creation.

## Repository integrity

```sh
python scripts/check_repository.py
python -m unittest discover -s tests -v
git diff --check
```

Integrity checks cover public placeholders, fixture mappings, invalid fixture contracts, local Markdown destinations and all six supplied media hashes. They do not follow external links or scan private files for credentials. Never regenerate media hashes simply to hide a changed asset; inspect the change first.
