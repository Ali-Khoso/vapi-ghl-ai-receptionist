# Maintain the GitHub repository

Target: [Ali-Khoso/vapi-ghl-ai-receptionist](https://github.com/Ali-Khoso/vapi-ghl-ai-receptionist).

The supplied folder originally had no Git history and the target remote was empty. The original project and demo assets were imported before improvements. Work in this checkout without reinitializing Git or replacing history.

## Inspect and verify first

```sh
git status --short --branch
git remote -v
git log -5 --oneline
```

Confirm that `origin` points to the intended repository. If GitHub CLI is installed, `gh auth status` checks its login; Git's credential manager may have a separate saved login. Use GitHub's sign-in flow when needed. Never put access tokens in commands or remote URLs.

## Validate and publish coherent changes

```sh
python scripts/validate.py --payload examples/contact-payload.json
python -m unittest discover -s tests -v
python scripts/check_repository.py
git diff --check
git diff
git status --short
```

Stage the intended files explicitly, inspect `git diff --cached`, and commit a useful change. Use a normal `git push origin main` when working on main, or push a review branch.

If a push is rejected because the remote advanced, fetch and inspect the incoming commits. Integrate the history carefully before retrying. Never force-push, delete existing branches to bypass a rejection, or create empty commits to inflate a count.

Keep the supplied MP4 and PNG. Never commit private configuration, bearer tokens, real customer information, call logs, or transcripts. `.gitignore` reduces accidental additions but is not a credential scanner.

## Verify what GitHub received

After a successful push, run:

```sh
git rev-list --count HEAD
git rev-parse HEAD
git ls-remote origin refs/heads/main
git status --short --branch
```

The local HEAD hash and the remote main hash must match. The count reports commits reachable from local HEAD; a matching remote hash confirms that history is on GitHub. A clean working tree confirms there are no outstanding tracked edits, but ignored private files are intentionally excluded.

To check tracked filenames, compare `git ls-files` with the repository's Code view. A single commit can upload many files, so file count, commit count and workflow-run count measure different things.

Open the repository's [commit history](https://github.com/Ali-Khoso/vapi-ghl-ai-receptionist/commits/main) to inspect commits, and [Actions](https://github.com/Ali-Khoso/vapi-ghl-ai-receptionist/actions) to inspect checks. A failed Actions run does not roll back an uploaded commit. Verify the newest run's commit hash and all matrix jobs; older failure notifications can remain in the inbox after a fix.

The workflow caches dependencies using `requirements-dev.txt`. Keep its `cache-dependency-path` aligned with the actual installation file when renaming dependencies. See [contributing](../CONTRIBUTING.md) for change and review expectations.
