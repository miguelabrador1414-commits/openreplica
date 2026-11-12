# OpenReplica project rules

OpenReplica is a fork of "The Replica skill" by Jake Schincariol, rebuilt as an
opencode-native agent pack. It takes an app from recon to a rebranded launch
through 11 phases, each with a skill, a CLI check and a gate.

## Layout

- `.opencode/skills/replica-*/SKILL.md`: the 11 phase skills.
- `.opencode/commands/replica-*.md`: one command per phase.
- `.opencode/agents/replica.md`: the orchestrator agent.
- `.opencode/opencode.json`: project default agent and model.
- `tools/replkit/`: the dependency-free Python CLI.
- `bin/replica`: wrapper for a checkout.
- `tests/`: unit tests, fixtures and repo contract tests.
- `docs/es/`: Spanish translations. English is the main language.

## Development

- `make check`: compile, run the full unittest suite and lint if `ruff` exists.
- `make test`: unittest only.
- `python3 -m unittest discover -s tests -v`: same as `make test`.
- `./bin/replica --help`: CLI help.
- `./bin/replica doctor`: environment check.

## Conventions

- Core Python is standard library only. Do not add a runtime dependency without
  a strong reason and a test.
- Keep deterministic logic in `tools/replkit/`, not in the skill prose.
- Every new CLI subcommand needs a test and a mention in the README.
- Docs are English first. Keep `README.es.md` and `docs/es/` in sync.
- No em dashes in repository text. The test suite enforces it.
- Do not add comments to code unless they explain a non-obvious reason.
- Respect the MIT license and the upstream attribution in `NOTICE`.
- Never commit secrets, `.env` files, captured screenshots of private data or
  personal review exports.

## Safety

- Clean-room only: no original source, assets, copy, fonts or private APIs.
- Public sources and the user's own account only.
- No purchases, deployments or real credentials without explicit user action.
- Read reviews and pages manually; no scraping that violates terms.

## Adding a phase

1. Add the skill folder and `SKILL.md` with `name` and `description`.
2. Add the command file and the agent route.
3. Add the phase to `PHASES`, `ARTIFACTS` and `gate.CHECKS`.
4. Add a gate test and a command test.
5. Update the README, `README.es.md` and `docs/es/`.
