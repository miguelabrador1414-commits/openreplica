---
description: Phase 5: add auth, database, payments, email and integrations.
agent: replica
---

Use the `replica-backend` skill for this request:

$ARGUMENTS

Before starting, run `replica doctor`. If `replica/state.json` is missing, run `replica init`.
Mark the phase as in progress: `replica mark backend in_progress`.

Never ask for, write or commit real keys. The user creates accounts and puts keys in `.env.local`; you write `.env.example`.
Expected artifacts:

- `replica/backend.md`
- `.env.example`

Do the work from the skill. Write evidence and decisions under `replica/`, not just in chat.
Before finishing, run `replica gate backend`.
If it fails, fix every reported item and run it again.
Only when it passes, run `replica mark backend passed`.
Report the files you wrote and the final gate output.
