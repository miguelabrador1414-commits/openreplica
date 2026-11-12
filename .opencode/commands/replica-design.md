---
description: Phase 3: rebuild the design system as tokens and component specs.
agent: replica
---

Use the `replica-design` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark design in_progress`.

Expected artifacts:

- `replica/design/tokens.json`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate design`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark design passed`.
Report the files you wrote and the final gate output.
