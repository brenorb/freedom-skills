# Repo AGENTS Notes

## Skill authoring

- Default workflows in skills should be action-first.
- Start with the command that directly matches the user's goal.
- Only fall back to environment checks or onboarding if that action fails, or if the environment is genuinely uncertain.
- Do not make `command -v ...` or setup verification the mandatory first step when the tool is already known-good.
