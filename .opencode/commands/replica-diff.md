---
description: Phase 7: score feature parity and diff screenshots against the original.
agent: replica
---

Use the `replica-diff` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark diff in_progress`.

Expected artifacts:

- `replica/parity.json`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate diff`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark diff passed`.
Report the files you wrote and the final gate output.
