---
description: Phase 2: choose the stack and design the database, API and build order.
agent: replica
---

Use the `replica-architect` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark architect in_progress`.

Expected artifacts:

- `replica/architecture.md`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate architect`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark architect passed`.
Report the files you wrote and the final gate output.
