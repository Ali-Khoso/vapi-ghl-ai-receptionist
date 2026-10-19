# Configure John Williamson

## 1. Run the offline baseline

Use Python 3.11+ and install `requirements-dev.txt` in a virtual environment as described in [README](../README.md). Run:

```sh
python scripts/validate.py --payload examples/contact-payload.json
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

No Vapi/GHL credentials or calls are required. These commands do not create tools, contacts, or appointments. This repository has no local server to start.

## 2. Prepare private account settings

For future deployment, use your own Vapi account and GHL sub-account. Obtain GHL contact-creation authorization for the chosen location and save it as a private Bearer credential in Vapi. The Vapi credential **reference ID** belongs in `credentialId`; the GHL access token does not belong in any repository file. A Vapi API key used to manage tools is separate from this endpoint credential.

Copy `config/vapi-api-request.template.json` to `config/vapi-api-request.private.json`. Replace only:

- `credentialId`: the private Vapi credential reference.
- `parameters[0].value`: your GHL location ID.

The private suffix is ignored by Git. Confirm with `git check-ignore config/vapi-api-request.private.json` before storing account-specific configuration. Do not force-add private files.

```sh
python scripts/validate.py --tool config/vapi-api-request.private.json --configured
```

This rejects known placeholders and checks the project's configuration policy. It cannot verify credential existence, token scope, location ownership, or whether an arbitrary identifier is real. It never authenticates to Vapi/GHL. Omitting `--configured` permits the intentionally unusable public placeholders.

## 3. Recreate the API Request tool

Configure an **API Request** tool named exactly `Ghl_IBC_VA` through Vapi's dashboard, using the template as a reference.

| Setting | Value |
| --- | --- |
| Type | `apiRequest` |
| Method / URL | `POST https://services.leadconnectorhq.com/contacts/` |
| Credential | Private Bearer credential reference |
| Headers | `Version: 2021-07-28`, `Content-Type: application/json` |
| Timeout | 20 seconds |
| Dynamic body schema | [contact-body.schema.json](../config/contact-body.schema.json) |
| Static parameters | Only `locationId`, with the account owner's fixed location ID |

Do not add a plain-text Authorization header alongside `credentialId`. Do not use undefined Liquid caller variables or static values for `firstName`, `phone`, or `address1`. Vapi merges static parameters after generated values, so such overrides would replace caller information.

The [argument fixture](../examples/tool-arguments.json) intentionally lacks `locationId`. The [outgoing payload fixture](../examples/contact-payload.json) includes it. Do not add the outgoing payload's `locationId` to the model-facing schema.

The JSON is an authoring template based on official references, not a live assistant export or a guarantee that a dashboard import will accept every schema keyword. Confirm supported fields against the [Create Tool reference](https://docs.vapi.ai/api-reference/tools/create) when deploying.

A Function tool needs a Vapi-compatible webhook adapter that receives the tool-call envelope and returns matched results. This repository does not implement that adapter; the GHL REST endpoint should not receive a Function webhook envelope.

## 4. Configure the assistant

Paste only [john-williamson.md](../prompts/john-williamson.md) as the active system prompt. Keep the original source as reference. Set the first message to:

> Hi, thank you for calling BrightFix Home Services. I'm John Williamson, the virtual receptionist. How can I help you today?

Choose a currently supported model, voice, and transcriber in your account. Historical screenshot selections are not requirements. Attach exactly one contact-saving tool, `Ghl_IBC_VA`, and save/publish the assistant configuration. Avoid tool-progress messages that announce internal CRM activity.

John confirms all three details and attempts the tool once before closing. A successful contact creation does not book an appointment or save issue/urgency. A failed request does not enqueue a human task. The prompt explains uncertainty without inventing success.

## 5. Understand acceptance limits

The offline suite checks field constraints, template consistency, destination matching, invalid inputs, and useful error exits. It does not simulate voice comprehension, prove runtime schema enforcement, or verify a CRM write. Only an account-level acceptance exercise can establish those outcomes.

No live calls or writes were performed during repository improvement. If you later choose to deploy, use synthetic details, inspect actual tool results and the destination contact, and follow [the separate account checklist](TEST_CHECKLIST.md). Arrange human review of failed calls before promising follow-up. Do not retry a timed-out create blindly; its result may be unknown.

For real inbound operation, a phone number must be connected to the assistant in Vapi; this repository does not provision one. See [troubleshooting](TROUBLESHOOTING.md) for failure handling.

## 6. Adapt the business

Update the active prompt and first message together. Keep John Williamson as the receptionist identity for this project. Change supported services as appropriate. If changing the name/address mappings, update the schema, template, fixtures, tests, and docs together rather than relying on automatic field splitting.
