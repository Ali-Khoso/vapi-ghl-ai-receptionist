# Contributing

This repository contains receptionist configuration and offline authoring checks. Keep changes reproducible with synthetic input; live account deployment requires separate account access and acceptance checks.

## Before changing files

Read the [setup guide](docs/SETUP.md), [configuration review](docs/CONFIGURATION_REVIEW.md) and [test checklist](docs/TEST_CHECKLIST.md). Preserve the supplied media and original prompt. Change the active prompt and greeting together when adapting the business identity.

Keep `.private.json` files, credentials, call recordings and customer information out of commits. Use synthetic reproductions in bug reports. Inspect the staged diff even when ignore rules are present.

## Validate a change

```sh
python -m pip install -r requirements-dev.txt
python scripts/preflight.py
git diff --check
git diff
```

For validator or repository-check behavior changes, include a regression case that would fail without the fix. Keep negative fixtures invalid for their declared field. Changes to caller fields must update the schema, tool body, examples, prompt mappings and documentation together.

The public template must retain its credential and location placeholders. A configured private copy passing local validation is not evidence of successful authorization or CRM writes.

## Commit and publish

Stage intended paths explicitly, inspect `git diff --cached`, and describe the concrete behavior changed in each commit. Preserve existing history and supplied assets. Do not create empty commits to increase a count.

Follow [GitHub maintenance](docs/GITHUB_UPLOAD.md) to push and verify the remote commit. Wait for the checks on that exact commit before reporting CI success. Old failed notifications remain historical records after a later run succeeds.

In a change description, state what changed, why, which checks passed and whether live account testing occurred. Avoid claims of appointment booking, dispatch, deduplication or automatic follow-up unless those capabilities were implemented and verified.
