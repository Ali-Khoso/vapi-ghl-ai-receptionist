# Synthetic fixtures

All names, addresses, and identifiers here are invented. The phone uses the fictional North American 555-01xx range; do not dial it.

- `tool-arguments.json`: exactly the three caller-generated arguments.
- `contact-payload.json`: outgoing GHL body after Vapi adds the fixed `locationId`. Its placeholder is intentionally unusable.
- `invalid-inputs.json`: labeled invalid arguments with the expected failing field. These are negative test fixtures, not requests to send.

The schema checks phone syntax, not whether a number exists or belongs to a caller. Name/address checks reject empty or whitespace-only strings; they cannot prove an address is complete. Confirm details in conversation. Full name goes into GHL `firstName` for compatibility with the original mapping; `address1` holds the combined service address. No automatic name/address splitting is implemented.
