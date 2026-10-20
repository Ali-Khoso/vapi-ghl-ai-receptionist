"""Validate local contact arguments and Vapi configuration without sending requests."""

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import re
import sys

try:
    from jsonschema import Draft7Validator
except ImportError:
    raise SystemExit("Missing jsonschema. Run: python -m pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parents[1]
LOCATION_PLACEHOLDER = "REPLACE_WITH_GHL_LOCATION_ID"
CREDENTIAL_PLACEHOLDER = "REPLACE_WITH_VAPI_BEARER_CREDENTIAL_ID"


def load_json(path):
    """Reject malformed JSON, duplicate keys and non-JSON numeric constants."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(_value):
        raise ValueError("non-JSON numeric constant")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("non-finite JSON number")
        return result

    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                          object_pairs_hook=unique_pairs, parse_constant=reject_constant,
                          parse_float=finite_float)
    except (OSError, ValueError, RecursionError) as exc:
        # Do not echo file contents, account identifiers or caller details.
        reason = "cannot read file" if isinstance(exc, OSError) else "invalid JSON (check syntax, duplicate keys and constants)"
        raise ValueError(reason) from None


def caller_schema():
    return load_json(ROOT / "config/contact-body.schema.json")


def schema_errors(value, schema):
    """Return field-specific diagnostics without including submitted values."""
    errors = []
    for error in Draft7Validator(schema).iter_errors(value):
        path = ".".join(str(part) for part in error.absolute_path) or "body"
        if error.validator == "required" and isinstance(error.instance, dict):
            errors.extend(f"{path}.{key}: required field is missing"
                          for key in error.validator_value if key not in error.instance)
        elif error.validator == "additionalProperties":
            # Key names are untrusted too: report known fields without echoing arbitrary input.
            allowed = ", ".join(sorted(schema.get("properties", {})))
            errors.append(f"{path}: unsupported fields; allowed fields: {allowed}")
        else:
            messages = {"type": "must be a string" if error.validator_value == "string" else "must be an object",
                        "pattern": "must contain non-whitespace text",
                        "minLength": "must not be empty"}
            message = messages.get(error.validator, "does not match the project schema")
            if error.validator == "pattern" and path == "phone":
                message = "must use E.164 syntax: +, nonzero country prefix, 2-15 ASCII digits"
            elif error.validator == "pattern" and path == "locationId":
                message = "must be a nonempty fixed identifier using ASCII letters, digits, underscores or hyphens"
            errors.append(f"{path}: {message}")
    return sorted(set(errors))


def validate_arguments(value):
    return schema_errors(value, caller_schema())


def validate_payload(value, configured=False):
    schema = deepcopy(caller_schema())
    schema["properties"]["locationId"] = {"type": "string", "pattern": r"^[A-Za-z0-9_-]+(?![\s\S])"}
    schema["required"].append("locationId")
    errors = schema_errors(value, schema)
    if isinstance(value, dict) and configured and is_placeholder(value.get("locationId")):
        errors.append("locationId: replace the placeholder in a private configuration")
    return errors


def is_placeholder(value):
    return isinstance(value, str) and value.upper().startswith(("REPLACE_", "SYNTHETIC_"))


def validate_tool(tool, configured=False):
    if not isinstance(tool, dict):
        return ["tool: must be an object"]
    errors = []
    expected = {"type": "apiRequest", "name": "Ghl_IBC_VA", "method": "POST",
                "url": "https://services.leadconnectorhq.com/contacts/", "timeoutSeconds": 20}
    for key, value in expected.items():
        if tool.get(key) != value or type(tool.get(key)) is not type(value):
            errors.append(f"{key}: must match the documented project setting")
    allowed = set(expected) | {"description", "credentialId", "headers", "body", "parameters"}
    if set(tool) - allowed:
        errors.append("tool: unsupported configuration fields")
    if not isinstance(tool.get("description"), str) or not tool["description"].strip():
        errors.append("description: provide a nonempty tool description")
    if tool.get("body") != caller_schema():
        errors.append("body: must match config/contact-body.schema.json exactly; locationId is static")
    if tool.get("headers") != {"Version": "2021-07-28", "Content-Type": "application/json"}:
        errors.append("headers: require Version 2021-07-28 and Content-Type application/json; use credentialId for authorization")
    credential = tool.get("credentialId")
    if not isinstance(credential, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", credential):
        errors.append("credentialId: provide a Vapi credential reference, never a bearer token")
    elif configured and is_placeholder(credential):
        errors.append("credentialId: replace the placeholder with your private credential reference")
    parameters = tool.get("parameters")
    if (not isinstance(parameters, list) or len(parameters) != 1
            or not isinstance(parameters[0], dict) or set(parameters[0]) != {"key", "value"}
            or parameters[0].get("key") != "locationId"):
        errors.append("parameters: require exactly one static field, locationId; never override caller fields")
    else:
        location = parameters[0]["value"]
        if not isinstance(location, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", location):
            errors.append("parameters.locationId: provide a fixed location identifier without Liquid or whitespace")
        elif configured and is_placeholder(location):
            errors.append("parameters.locationId: replace the placeholder in a private configuration")
    return errors


def build_payload(arguments, location_id):
    """Preview the documented merge; never normalizes or guesses caller details."""
    errors = validate_arguments(arguments)
    if errors:
        raise ValueError("; ".join(errors))
    payload = {**arguments, "locationId": location_id}
    errors = validate_payload(payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, default=ROOT / "config/vapi-api-request.template.json")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--arguments", type=Path, help="validate caller arguments with the tool")
    group.add_argument("--payload", type=Path, help="validate an outgoing contact body with the tool")
    parser.add_argument("--configured", action="store_true", help="reject known placeholder identifiers")
    args = parser.parse_args(argv)
    try:
        tool = load_json(args.tool)
        errors = validate_tool(tool, args.configured)
        if args.arguments:
            errors += validate_arguments(load_json(args.arguments))
        if args.payload:
            payload = load_json(args.payload)
            errors += validate_payload(payload, args.configured)
            if not errors and payload["locationId"] != tool["parameters"][0]["value"]:
                errors.append("locationId: payload destination differs from the tool's static destination")
    except ValueError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    mode = "configured identifiers" if args.configured else "template placeholders allowed"
    print(f"Offline validation passed ({mode}). No request sent; authorization and live behavior are unverified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
