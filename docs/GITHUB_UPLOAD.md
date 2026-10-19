# Put the project on GitHub

Suggested repository name: `vapi-ghl-ai-receptionist`

Suggested description: “Inbound AI receptionist using Vapi and GoHighLevel for conversational contact capture, with prompt, setup guide, and test checklist.”

This package is ready for a repository. A hosted GitHub repository has not been created by this delivery.

## Browser method — no GitHub CLI needed

1. Extract the ZIP.
2. Open https://github.com/new while signed in to your own account.
3. Use the suggested name and description. Choose the visibility you want. Leave automatic README creation unchecked because this project already includes README.md.
4. Create the repository and choose Upload files.
5. Drag the CONTENTS of the extracted `repo` folder into GitHub: README.md and the assets, config, docs, examples, and prompts folders. Do not upload the ZIP as the only file or nest the whole project one level below the root.
6. Commit the upload. Confirm that GitHub displays the README on the repository homepage.

## VS Code terminal method

Create an empty repository first. Open the extracted project folder in VS Code. Run these commands one line at a time, replacing YOUR_USERNAME with the account you used:

```sh
git init
git add .
git commit -m "Add Vapi and GoHighLevel receptionist project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/vapi-ghl-ai-receptionist.git
git push -u origin main
```

If Git asks for your author identity, configure your own name and email. If authentication is needed, use GitHub's sign-in flow. Do not put tokens in remote URLs. These commands assume a new extracted folder with no existing remote.

Before publishing, confirm that placeholders remain in templates. Add a demo link to README.md after recording. Suggested topics: vapi, gohighlevel, voice-ai, ai-receptionist, crm-automation.
