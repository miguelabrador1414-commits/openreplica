---
description: Phase 11: run preflight and ship to the user's own domain.
agent: replica
---

Use the `replica-deploy` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark deploy in_progress`.

Do not deploy, buy a domain or enter payment data. Ask for explicit approval and give the user the exact steps.
Expected artifacts:

- `replica/preflight.md`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate deploy`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark deploy passed`.
Report the files you wrote and the final gate output.
