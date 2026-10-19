# Live test checklist

These checks are pending execution in the owner's accounts. No passing results are claimed here.

| Test | Expected result |
| --- | --- |
| Complete standard request | Confirmed name, phone, address; one tool invocation before end of call; matching contact |
| Caller corrects phone before save | Corrected number repeated and sent as a string |
| Missing country code | Ask for clarification rather than invent a country |
| Missing required detail after two asks | No contact-tool call; polite close |
| Quote-only request | No invented price; quote-only urgency reflected in conversation |
| Tool authentication failure | No false claim that a contact or appointment was created; failure visible in logs |
| Static body inspection | Only locationId fixed; caller fields are dynamic |
| Repeated/duplicate contact | Inspect actual GHL behavior; no assumption of deduplication |
| Call interrupted before required details | No partial contact request |
| Post-save detail correction | Note original value remains unless an update path is implemented |
| Issue and urgency | Summary includes them; no claim they are persisted in GHL |
| Final recording | Real observed results; no credentials or real customer details visible |

Record: test date, case, actual result, tool-call count, and any correction needed. Keep real transcripts and account-specific logs private.
