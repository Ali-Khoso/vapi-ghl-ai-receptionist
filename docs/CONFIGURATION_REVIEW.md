# Review of the supplied screenshots

These observations describe the images, not a tested running integration.

| Screenshot | Observed configuration | Action |
| --- | --- | --- |
| 1: Assistant | John Williamson prompt; GPT-4.1, Soniox STT RT v5, Vapi Elliot voice visible | Reuse your available model, transcriber, and voice; preview the voice before recording |
| 2: Ghl_IBC_VA | Function tool; required string fields phone, address1, firstName; optional locationId; GHL contacts URL; 20-second timeout | Verify the tool protocol before using the GHL URL directly |
| 3: Authentication | A Bearer Token credential is selected | Keep the credential private; selection alone does not prove authorization succeeds |
| 4: Static body | locationId, firstName template, phone Number 20, address1 template | Keep locationId fixed; remove the three caller fields from static overrides |
| 5: Native GHL tool | Separate contact-create tool, Use Customer Phone selected | An alternative tool exists, but this does not prove it is attached or used |

## Corrections

1. `phone` must be a caller-supplied string, including the plus sign and country code. The static number `20` is not a valid mapping for this project.
2. Keep only `locationId` in static body fields. Do not override `firstName`, `phone`, or `address1` with constants or unverified Liquid variables. The screenshots do not establish that `caller_name` or `caller_address` exists.
3. Keep the location ID out of caller-generated parameters. It is supplied by the account owner, not the caller.
4. The visible tool is labelled Function. Vapi documents Function tools as webhook integrations; a direct GHL REST request should use an API Request tool. If you retain a Function tool, it needs an adapter that receives the Vapi envelope, calls GHL, and returns the matched tool result. This package documents the direct API Request option; it does not contain an adapter.
5. Configure the API headers described in SETUP.md. The screenshot does not show enough to confirm their presence.
6. Only one contact-saving tool should be attached for this prompt. A separate built-in tool with a different name will not automatically match `Ghl_IBC_VA`.

The author later supplied four screenshots now included in the [README gallery](../README.md#project-screenshots-and-demo): assistant overview, prompt and greeting, attached tool, and Function tool settings. They show the historical setup; the recommended template remains an API Request tool. The authentication, static-body, and native GHL tool screenshots discussed above remain historical observations without included image files. Configuration templates use placeholders.
