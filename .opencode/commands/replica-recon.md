---
description: Phase 1: reverse-engineer the target app into a recon map and feature matrix.
agent: replica
---

Use the `replica-recon` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark recon in_progress`.

Use public sources and the user's own account only. Never bypass a login or paywall.
Expected artifacts:

- `replica/recon.md`
- `replica/features.csv`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate recon`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark recon passed`.
Report the files you wrote and the final gate output.
