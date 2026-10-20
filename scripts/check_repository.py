"""Check JSON, local Markdown links, template safety and preserved media offline."""

import hashlib
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    from scripts.validate import (CREDENTIAL_PLACEHOLDER, LOCATION_PLACEHOLDER, ROOT,
                                  load_json, validate_arguments, validate_payload, validate_tool)
except ModuleNotFoundError:
    # Support both `python -m scripts.check_repository` and the README's direct command.
    from validate import (CREDENTIAL_PLACEHOLDER, LOCATION_PLACEHOLDER, ROOT,
                          load_json, validate_arguments, validate_payload, validate_tool)


def check_links(root):
    errors = []
    files = list(root.glob("*.md"))
    for directory in ("docs", "prompts", "examples", "assets"):
        files.extend((root / directory).rglob("*.md"))
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"{path.relative_to(root)}: unreadable UTF-8 Markdown")
            continue
        for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", text):
            try:
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                valid = destination.is_relative_to(root.resolve()) and destination.exists()
            except (OSError, ValueError):
                valid = False
            if not valid:
                errors.append(f"{path.relative_to(root)}: broken or escaping local link")
    return errors


def check_repository(root=ROOT):
    root = Path(root)
    errors = []
    for directory in ("config", "examples"):
        for path in (root / directory).rglob("*.json"):
            if path.name.endswith(".private.json"):
                continue
            try:
                load_json(path)
            except ValueError:
                errors.append(f"{path.relative_to(root)}: invalid JSON")
    try:
        tool = load_json(root / "config/vapi-api-request.template.json")
        errors.extend(validate_tool(tool))
        if not isinstance(tool, dict) or tool.get("credentialId") != CREDENTIAL_PLACEHOLDER:
            errors.append("public tool: restore credential reference placeholder")
        if not isinstance(tool, dict) or tool.get("parameters") != [{"key": "locationId", "value": LOCATION_PLACEHOLDER}]:
            errors.append("public tool: restore fixed location placeholder")
        arguments = load_json(root / "examples/tool-arguments.json")
        payload = load_json(root / "examples/contact-payload.json")
        errors.extend(validate_arguments(arguments))
        errors.extend(validate_payload(payload))
        if not isinstance(arguments, dict) or payload != {**arguments, "locationId": LOCATION_PLACEHOLDER}:
            errors.append("example payload: must match arguments plus the public location placeholder")
    except ValueError:
        errors.append("required template or fixture: unreadable JSON")
    errors.extend(check_links(root))
    try:
        entries = (root / "assets/SHA256SUMS").read_text(encoding="utf-8").splitlines()
        expected_names = {"AI_Receptionist_Demo_90s.mp4", "vapi-call-demo.png",
                          "vapi-assistant-overview.png", "vapi-prompt-and-greeting.png",
                          "vapi-attached-contact-tool.png", "vapi-contact-tool-settings.png"}
        seen = set()
        for line in entries:
            expected, filename = line.split()
            if filename not in expected_names or filename in seen:
                errors.append("media manifest: require each original asset exactly once")
                continue
            seen.add(filename)
            actual = hashlib.sha256((root / "assets" / filename).read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f"assets/{filename}: original media hash changed")
        if seen != expected_names:
            errors.append("media manifest: missing original asset")
    except (OSError, ValueError):
        errors.append("media manifest: missing, malformed or unreadable asset")
    return errors


def main():
    errors = check_repository()
    if errors:
        print("Repository checks failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Repository checks passed: JSON, public placeholders, mappings, local links and original media hashes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
