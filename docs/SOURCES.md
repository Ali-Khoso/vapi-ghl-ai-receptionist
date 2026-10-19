# Official technical references

Reviewed 19 October 2026. These sources describe API contracts; no live Vapi or HighLevel service request was made. Dashboard labels and supported schema details can change.

- [Vapi API Request tools](https://docs.vapi.ai/tools/api-request): direct HTTP requests from structured caller arguments.
- [Request configuration](https://docs.vapi.ai/tools/api-request/configuration): `body` is the model-facing schema; `parameters` are merged static fields; credential references are separate from management API keys.
- [Static parameters](https://docs.vapi.ai/tools/static-variables-and-aliases/static-parameters): top-level `{key, value}` entries override generated arguments.
- [Create Tool API](https://docs.vapi.ai/api-reference/tools/create): current tool configuration contract.
- [API Request versus Function tools](https://docs.vapi.ai/tools/api-request-vs-function): direct REST requests versus webhook envelopes.
- [Function tool protocol](https://docs.vapi.ai/tools/custom-tools): adapters must return the correct tool-call result.
- [HighLevel Create Contact](https://marketplace.gohighlevel.com/docs/2021-07-28/ghl/contacts/create-contact/index.html): `POST /contacts/`, Version `2021-07-28`, fixed required `locationId`, and supported contact fields.

Full name in `firstName` and combined service address in `address1` are compatibility choices from this project's original prompt, not automatic HighLevel field splitting. The project requires three caller fields more strictly than the general GHL endpoint contract.

The original prompt, historical screenshot review, and media came from the supplied project. Only the call screenshot and MP4 are included. The five account-configuration screenshots mentioned in the historical review were not supplied as files here. Voice behavior, account permissions, actual tool attachment, runtime schema enforcement, and CRM success remain unverified.
