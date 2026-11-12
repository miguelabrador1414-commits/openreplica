---
description: Phase 6: test every flow and write reproducible bug reports.
agent: replica
---

Use the `replica-test` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark test in_progress`.

Expected artifacts:

- `replica/test-plan.md`
- `replica/bugs.md`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate test`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark test passed`.
Report the files you wrote and the final gate output.
