# Troubleshooting

Start with local validation. It sends no network requests and returns a nonzero exit code for invalid input. Error output intentionally identifies fields and rules without printing submitted values.

| Symptom | Action |
| --- | --- |
| `Missing jsonschema` | Use the virtual environment and run `python -m pip install -r requirements-dev.txt` |
| PowerShell blocks activation | Invoke `.venv\Scripts\python.exe` directly; activation is optional |
| Invalid JSON | Check quotes, commas, duplicate keys, encoding, and non-JSON values such as NaN; use UTF-8 |
| Python setup fails before CI tests | Keep `cache-dependency-path: requirements-dev.txt` in the workflow; the default requirements.txt/pyproject.toml lookup does not find this project's dependency file |
| Media integrity fails | Check the named asset against its supplied original; do not regenerate hashes to conceal accidental replacement |
| Invalid fixture rejection is missing | Restore the synthetic negative example or investigate why its declared field is now accepted |
| Phone validation fails | Use a string with `+` and 2-15 ASCII digits; no spaces, leading zero country prefix, or trailing newline; ask the caller rather than guessing |
| Required or blank field | Confirm name, phone, and full service address before invoking the tool |
| Unsupported arguments | Send only firstName, phone, address1; the location comes from static configuration |
| Schema mismatch | Keep the tool's body identical to config/contact-body.schema.json |
| Static parameters rejected | Keep exactly one fixed locationId; remove caller-field overrides and unresolved Liquid variables |
| Placeholder failure | Expected with `--configured` on the public template; replace identifiers only in an ignored private copy |
| Payload destination differs | Match its locationId to the private tool's fixed destination; do not accept a caller-selected location |
| Wrong name or phone in CRM | Check historical phone=20 overrides and undefined caller_name/caller_address templates |

The following rows concern a future account deployment. They were not tested against live accounts here.

| Observation | Investigation |
| --- | --- |
| No tool invocation | Check exact `Ghl_IBC_VA` name, attachment, saved assistant version, confirmed required details, and call logs |
| Authentication or forbidden response | Privately verify credential validity, contact-write authorization, and destination location; local validation cannot prove these |
| Invalid request response | Compare method, endpoint, Version header, types, required locationId, and actual outgoing body |
| Function request fails at GHL URL | Use API Request or implement the Vapi webhook adapter contract; none is included here |
| Timeout, rate limit, or server failure | Inspect the result and whether the contact already exists before deciding on recovery; do not blindly repeat a create |
| Duplicate/rejected contact | Inspect location duplicate policies and previous synthetic test contacts; no durable idempotency exists here |
| No issue or urgency in GHL | Expected: the current payload does not map them |
| No booking, dispatch, or manual task | Expected: these workflows are not implemented |
| Historical greeting differs | Keep preserved media as history; configure the active prompt and first message with John Williamson and BrightFix Home Services |

When sharing an error, provide the rule, status category, and a synthetic reproduction. Do not publish tokens, private identifiers, transcripts, or real caller details. Consult [official references](SOURCES.md) for current API behavior.
