# Test checklist

## Automated offline checks

Run from the repository root after installing `requirements-dev.txt`:

```sh
python scripts/preflight.py
git diff --check
```

The shared preflight runs both fixture validations, all regression tests and repository integrity checks. See the [command reference](CLI.md) to run each step separately or request JSON validation output.

Expected: validation succeeds with placeholders permitted, all unit tests pass, repository checks pass, and Git reports no whitespace errors. The unit tests forbid socket creation while exercising validators. No service credentials are needed.

The suite covers missing/blank/wrong-type caller fields, E.164 syntax boundaries, extra fields, caller-injected location, unsafe static overrides, schema drift, endpoint/header/tool-name errors, malformed JSON, duplicate keys, destination mismatches, placeholder rejection, and CLI failure exits without echoing submitted values.

`python scripts/validate.py --configured` against the public template **must fail** because the credential and location are placeholders. This is a negative preflight, not a broken repository.

## Optional future account acceptance

These account-level checks are **pending and were not executed**. They require a separate decision to deploy and use the owner's accounts; repository automation never runs them.

| Case | Expected observation |
| --- | --- |
| Greeting | John Williamson at BrightFix Home Services; first message matches active prompt |
| Complete standard inquiry | Three confirmed string arguments; one mid-call tool attempt; matching contact after confirmed success |
| Correct phone before save | Corrected number repeated and sent |
| Missing country code | Clarification; no invented digits |
| Missing required detail after two asks | No tool attempt; polite explanation |
| Quote-only | No invented price or appointment |
| Authentication/authorization failure | No success claim or automatic retry; result visible to account operator |
| Timeout/unknown outcome | No claim that nothing was saved; no blind second create |
| Static body | Only locationId fixed; caller values stay dynamic |
| Duplicate contact | Inspect account settings and actual result; no assumed deduplication |
| Call ends before required details | No partial request |
| Correction after submission | No second create; no unsupported update claim |
| Issue and urgency | Summarized conversationally; no claim that this payload stores them |
| Failed contact write | No claim a manual task was automatically created |

Record date, case, observed result, tool-attempt count, and any correction privately. Inspect both the tool response and destination contact; a friendly voice response alone proves neither. Keep credentials, customer details, transcripts, and account logs out of Git. The preserved demo media is historical evidence, not a passing result for these cases.
