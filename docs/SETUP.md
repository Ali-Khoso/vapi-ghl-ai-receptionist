# Build and use the receptionist

## 1. Prepare the accounts

Use your own Vapi account and GHL sub-account. Obtain an authorized GHL access token with contact-creation access for that location. Save it as a private Bearer credential in Vapi; do not paste a token into the prompt or repository. Copy your location ID privately.

## 2. Create the assistant

Create or open your Vapi assistant. Paste `prompts/john-williamson-original.md` into its system prompt. The screenshots show GPT-4.1, Soniox STT RT v5, and the Vapi Elliot voice; choose supported options in your account and preview them.

Suggested first message: “Hi, thank you for calling BrightFix Home Services. I'm John Williamson, the virtual receptionist. How can I help you today?”

## 3. Configure the direct GHL request

The included API Request template is a proposed correction to the screenshot's Function configuration, not a live export.

Create an API Request tool named exactly `Ghl_IBC_VA`:

| Setting | Value |
| --- | --- |
| Method | POST |
| URL | https://services.leadconnectorhq.com/contacts/ |
| Authentication | Your private Bearer credential |
| Version header | 2021-07-28 |
| Content-Type header | application/json |
| Timeout | 20 seconds |
| Body schema | `config/contact-body.schema.json` |
| Static body field | locationId = your own location ID |

The JSON template contains a credential **ID** placeholder, not a token. Replace both placeholders privately before using it. Configure through the dashboard or use the JSON with Vapi's Create Tool API after checking the current API schema. Do not paste the whole tool template into the assistant prompt.

Make all three caller fields required strings. Delete static entries for firstName, phone, and address1. Confirm that the outgoing request resembles `examples/contact-payload.json`, with your own location ID and test values.

If you keep a Function tool instead, point it to your own Vapi-compatible webhook adapter, not directly to the GHL contacts endpoint. See the official references for the request and response contract.

## 4. Attach and save

Attach `Ghl_IBC_VA` to this assistant and save/publish the configuration in Vapi. For this demo, remove the separate native contact-create tool from the assistant's attached tools so there is one contact-saving path. Suppress tool-progress messages that would announce internal CRM work, while keeping normal conversation responses.

## 5. Review the prompt before live use

The original text remains unchanged. Consider these explicit adjustments when configuring your own assistant:

- Replace “I'd love to get this scheduled for you” with “I can take your details for the team.” This integration does not book a slot.
- Do not promise that a technician is already on the way or that a specific response time is guaranteed.
- If only the address is refused, explain that the service request cannot be completed without the address. A phone callback may still be possible if a valid phone number is available.
- Ask for the country code if ambiguous; never invent missing phone digits.
- A failed contact write does not create a manual follow-up task. Arrange human review of failed calls before promising a callback after failure.
- Treat the exactly-once instruction as a testable prompt goal. For enforced deduplication, use an implementation with durable tracking; this template does not provide it.

## 6. Test and use

Open the assistant's Talk/test-call option for a browser demonstration. For actual inbound phone calls, connect an available phone number to the assistant using your Vapi phone-number configuration.

Give a sample service issue, name, phone, and address. Confirm the read-backs. After the address is confirmed, check that the contact tool ran before the call ended. Finish the urgency question and summary. Then inspect the tool response and search GHL Contacts for the test phone number.

Run the checklist in TEST_CHECKLIST.md. A friendly voice response alone is not proof that the contact was saved.

## 7. Adapt the content

Edit the business name in the prompt and greeting together. Replace services and escalation wording to match the business. Keep `Ghl_IBC_VA`, `firstName`, `phone`, and `address1` consistent across prompt and tool. Set locationId and credentials for the destination account. Do not claim issue/urgency storage until you implement and test those additional fields.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Wrong phone value | Remove static phone=20; use a required string |
| Literal template text saved | Remove undefined caller_name/caller_address overrides |
| No tool call | Exact tool name, attachment, required details, saved assistant version |
| Authentication error | Credential validity and authorization for the selected location |
| Invalid body | Field spelling, data types, locationId, and API headers |
| Function call fails at GHL URL | Use API Request or implement the required webhook adapter |
| Duplicate or rejected contact | Inspect location duplicate settings and previous test contacts; do not retry blindly |
| No issue or urgency in GHL | Those fields are absent from the current payload |
