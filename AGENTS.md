# Repo AGENTS Notes

## Skill authoring

- Default workflows in skills should be action-first.
- Start with the command that directly matches the user's goal.
- Only fall back to environment checks or onboarding if that action fails, or if the environment is genuinely uncertain.
- Do not make `command -v ...` or setup verification the mandatory first step when the tool is already known-good.

## Language

- Write everything in English: skills, docs, code comments, commit messages, pull request and issue titles and bodies, and review comments.
- This applies even when the user writes to you in another language. Reply to them in their language if you like, but keep everything that lands in the repo or on GitHub in English.
- A squash merge takes its message from the commit messages, so write those in English too.
