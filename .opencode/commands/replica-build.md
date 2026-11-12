---
description: Phase 4: build the clone screen by screen from the recon map.
agent: replica
---

Use the `replica-build` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark build in_progress`.

Expected artifacts:

- `replica/features.csv`
- `replica/build-log.md`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate build`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark build passed`.
Report the files you wrote and the final gate output.
