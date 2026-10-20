from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft7Validator
from scripts.validate import (ROOT, build_payload, caller_schema, load_json, main,
                              validate_arguments, validate_payload, validate_tool)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.network = patch("socket.socket", side_effect=AssertionError("network is forbidden in offline tests"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.arguments = load_json(ROOT / "examples/tool-arguments.json")
        self.tool = load_json(ROOT / "config/vapi-api-request.template.json")

    def test_schema_and_template(self):
        Draft7Validator.check_schema(caller_schema())
        self.assertEqual([], validate_tool(self.tool))
        self.assertEqual([], validate_arguments(self.arguments))

    def test_invalid_fixtures(self):
        for case in load_json(ROOT / "examples/invalid-inputs.json"):
            with self.subTest(case=case["case"]):
                errors = validate_arguments(case["arguments"])
                self.assertTrue(errors)
                expected_field = case["errorField"] if case["errorField"] in self.arguments else "body"
                self.assertIn(expected_field, " ".join(errors))

    def test_phone_boundaries(self):
        for phone in ("+12", "+123456789012345"):
            with self.subTest(valid=phone):
                self.assertEqual([], validate_arguments({**self.arguments, "phone": phone}))
        for phone in ("+1", "+0123", "+1234567890123456", "+12025550147\n", "+١٢٣", " +12025550147", "+1 2025550147", True, None):
            with self.subTest(invalid=phone):
                self.assertTrue(validate_arguments({**self.arguments, "phone": phone}))

    def test_all_fields_required_nonblank_strings(self):
        for field in self.arguments:
            for value in (None, 20, True, "", " \n\t"):
                with self.subTest(field=field, value=value):
                    self.assertTrue(validate_arguments({**self.arguments, field: value}))
            partial = dict(self.arguments)
            del partial[field]
            self.assertTrue(validate_arguments(partial))

    def test_nonobject_inputs(self):
        for value in ([], None, "contact", 20):
            self.assertTrue(validate_arguments(value))
            self.assertTrue(validate_tool(value))
            self.assertTrue(validate_payload(value))

    def test_merge_matches_example_without_mutation(self):
        original = deepcopy(self.arguments)
        payload = build_payload(self.arguments, self.tool["parameters"][0]["value"])
        self.assertEqual(load_json(ROOT / "examples/contact-payload.json"), payload)
        self.assertEqual(original, self.arguments)
        self.assertEqual([], validate_payload(payload))
        self.assertTrue(validate_arguments(payload))

    def test_merge_rejects_missing_or_injected_values(self):
        for arguments in ({}, {**self.arguments, "locationId": "injected"}):
            with self.assertRaises(ValueError):
                build_payload(arguments, "SYNTHETIC_LOCATION")
        for location in (None, 20, "", " "):
            with self.assertRaises(ValueError):
                build_payload(self.arguments, location)

    def test_tool_misconfiguration(self):
        cases = {"type": "function", "name": "OtherTool", "method": "GET", "url": "https://example.com",
                 "timeoutSeconds": 0, "description": " ", "credentialId": "Bearer PRIVATE_VALUE",
                 "headers": {"Authorization": "PRIVATE_VALUE"}, "body": {},
                 "parameters": [{"key": "phone", "value": 20}]}
        for key, value in cases.items():
            with self.subTest(key=key):
                self.assertTrue(validate_tool({**self.tool, key: value}))
        for key in self.tool:
            tool = deepcopy(self.tool)
            del tool[key]
            self.assertTrue(validate_tool(tool), key)
        self.assertTrue(validate_tool({**self.tool, "function": {}}))

    def test_timeout_requires_an_integer(self):
        for timeout in (20.0, "20", True, None):
            with self.subTest(timeout=timeout):
                errors = validate_tool({**self.tool, "timeoutSeconds": timeout})
                self.assertTrue(any("timeoutSeconds" in error for error in errors))
        self.assertEqual([], validate_tool({**self.tool, "timeoutSeconds": 20}))

    def test_malformed_static_parameters(self):
        for value in (None, {}, [], [None], [{"key": "locationId"}],
                      [{"key": "locationId", "value": "{{ caller.location }}"}],
                      [{"key": "locationId", "value": None}],
                      self.tool["parameters"] * 2):
            with self.subTest(parameters=value):
                self.assertTrue(validate_tool({**self.tool, "parameters": value}))

    def test_configured_mode_rejects_placeholders(self):
        self.assertEqual(2, len(validate_tool(self.tool, configured=True)))
        tool = deepcopy(self.tool)
        tool["credentialId"] = "00000000-0000-4000-8000-000000000000"
        tool["parameters"][0]["value"] = "offline-location"
        self.assertEqual([], validate_tool(tool, configured=True))
        payload = build_payload(self.arguments, "SYNTHETIC_LOCATION")
        self.assertTrue(validate_payload(payload, configured=True))

    def test_json_read_errors_are_private(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for content in ('{"secret":"PRIVATE_VALUE",}', '{"phone":1,"phone":2}', '{"phone":NaN}', '"\ud800"'):
                path.write_text(content, encoding="utf-8", errors="surrogatepass")
                with self.assertRaises(ValueError) as error:
                    load_json(path)
                self.assertNotIn("PRIVATE_VALUE", str(error.exception))
            with self.assertRaises(ValueError):
                load_json(Path(directory) / "missing.json")

    def test_json_exponents_must_stay_finite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "number.json"
            for number in ("1e999", "-1e999"):
                path.write_text('{"value":' + number + '}', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "invalid JSON"):
                    load_json(path)
            path.write_text('{"value":1.25e2}', encoding="utf-8")
            self.assertEqual({"value": 125.0}, load_json(path))

    def test_deep_json_reports_a_private_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deep.private.json"
            path.write_text('[' * 2000 + '"PRIVATE_VALUE"' + ']' * 2000, encoding="utf-8")
            output = io.StringIO()
            with redirect_stderr(output):
                self.assertEqual(1, main(["--arguments", str(path)]))
            self.assertNotIn("PRIVATE_VALUE", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())
            with patch("scripts.validate.json.loads", side_effect=RecursionError("PRIVATE_VALUE")):
                with self.assertRaisesRegex(ValueError, "invalid JSON"):
                    load_json(path)

    def test_cli_exit_codes_and_redacted_errors(self):
        for argv, expected in (([], 0), (["--arguments", str(ROOT / "examples/tool-arguments.json")], 0),
                               (["--payload", str(ROOT / "examples/contact-payload.json")], 0),
                               (["--configured"], 1), (["--tool", "missing.private.json"], 1)):
            with self.subTest(argv=argv), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(expected, main(argv))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"phone":"PRIVATE_VALUE"}', encoding="utf-8")
            output = io.StringIO()
            with redirect_stderr(output):
                self.assertEqual(1, main(["--arguments", str(path)]))
            self.assertNotIn("PRIVATE_VALUE", output.getvalue())

    def test_payload_destination_must_match_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            import json
            path.write_text(json.dumps(build_payload(self.arguments, "different-location")), encoding="utf-8")
            with redirect_stderr(io.StringIO()) as output:
                self.assertEqual(1, main(["--payload", str(path)]))
            self.assertIn("destination differs", output.getvalue())


if __name__ == "__main__":
    unittest.main()
