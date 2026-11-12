---
description: Phase 10: write the landing page, pricing and store listing.
agent: replica
---

Use the `replica-launch` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark launch in_progress`.

Expected artifacts:

- `replica/listing.json`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate launch`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark launch passed`.
Report the files you wrote and the final gate output.
