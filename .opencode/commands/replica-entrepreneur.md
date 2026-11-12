---
description: Phase 8: read real user reviews and turn complaints into a fix plan.
agent: replica
---

Use the `replica-entrepreneur` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark entrepreneur in_progress`.

Never invent a review, quote, rating or source. Every quote must be verbatim and linked.
Expected artifacts:

- `replica/reviews.csv`
- `replica/feedback.md`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate entrepreneur`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark entrepreneur passed`.
Report the files you wrote and the final gate output.
