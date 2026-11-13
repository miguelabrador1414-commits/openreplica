# OpenReplica

[![tests](https://github.com/miguelabrador1414-commits/openreplica/actions/workflows/tests.yml/badge.svg)](https://github.com/miguelabrador1414-commits/openreplica/actions/workflows/tests.yml)

Eleven opencode-native skills that rebuild an app's functionality clean-room,
then give the result its own name, brand and launch. Free, MIT, no signup, no
API key required by the pack itself.

[Leer en español](README.es.md)

OpenReplica is a fork of [The Replica skill](https://github.com/Jakeschincariol/replica-skill)
by Jake Schincariol, rebuilt around a single `replica` CLI, explicit project
state and deterministic quality gates.

## What it does

One skill reverse-engineers the app you want to clone. One rebuilds it. One
tests it for bugs. Another reads what the original's users hate and turns it
into a fix plan. In between, the pack plans the stack, rebuilds the design
system, wires auth and payments, scores parity, names and rebrands the result,
writes the launch, and ships it.

The workflow is:

```text
recon -> architect -> design -> build -> backend -> test -> diff
      -> entrepreneur -> brand -> launch -> deploy
```

Each phase writes evidence into `replica/` in your project. Each phase has a
gate. You do not move on until the gate passes.

**It rebuilds what an app does, never what it owns.** Features and flows,
clean-room style. Not its source code, logo, copy, fonts, content or private
APIs.

## Requirements

- [opencode](https://opencode.ai) with a model that can call tools.
- Python 3.8 or newer for the CLI.
- Optional: Playwright and Chromium for real browser capture. The default
  capture path is offline and does not download anything.

The core CLI has no runtime dependencies outside the Python standard library.

## Install

### Global

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cd openreplica
./scripts/install.sh --global
export PATH="$HOME/.local/bin:$PATH"
replica doctor
```

This installs:

- the CLI in `~/.local/share/openreplica`,
- the wrapper in `~/.local/bin/replica`,
- skills in `~/.config/opencode/skills`,
- commands in `~/.config/opencode/commands`,
- the agent in `~/.config/opencode/agents`.

Restart opencode after installing so it loads the new files.

### Per project

```bash
./scripts/install.sh --project /path/to/your-app
```

This copies the skills, commands, agent, project config and a local CLI into
the target project. It does not touch your global config. If the project
already has `.opencode/opencode.json`, the installer leaves it alone and asks
you to add the two settings yourself. Use the local CLI when `replica` is not
on your `PATH`:

```bash
/path/to/your-app/.opencode/bin/replica doctor
```

### Manual

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cp -R openreplica/.opencode/skills/* ~/.config/opencode/skills/
cp -R openreplica/.opencode/commands/* ~/.config/opencode/commands/
cp -R openreplica/.opencode/agents/* ~/.config/opencode/agents/
ln -sf "$PWD/openreplica/bin/replica" ~/.local/bin/replica
```

### Claude Code compatibility

The upstream `.claude-plugin` manifest is kept and points at `.opencode/skills`.
opencode is the tested target; Claude Code support is best-effort and not part
of the test matrix.

## Quick start

```bash
cd my-app
replica init
opencode
```

Then run the phases in order:

```text
/replica-recon https://example.com
/replica-architect
/replica-design
/replica-build
/replica-backend
/replica-test
/replica-diff
/replica-entrepreneur
/replica-brand
/replica-launch
/replica-deploy
```

You can run any phase on its own. `/replica-entrepreneur` on an app you are
only thinking about cloning is a good way to decide whether it is worth it.

## The eleven phases

| # | Command | What it produces | Gate checks |
| --- | --- | --- | --- |
| 1 | `/replica-recon` | `replica/recon.md`, `replica/features.csv`, screenshots | Map, matrix, priorities, must-haves |
| 2 | `/replica-architect` | `replica/architecture.md` | Stack, schema, routes, build order |
| 3 | `/replica-design` | `replica/design/tokens.json`, component specs | Tokens and WCAG AA contrast |
| 4 | `/replica-build` | App screens, `replica/build-log.md`, updated matrix | Implemented features and clone screenshots |
| 5 | `/replica-backend` | Migrations, server code, `replica/backend.md` | Backend notes, `.env.example`, no secrets |
| 6 | `/replica-test` | `replica/test-plan.md`, `replica/bugs.md`, e2e tests | Plan present, no open S1 or S2 |
| 7 | `/replica-diff` | `replica/parity.json`, diff images | Parity score at least 70 |
| 8 | `/replica-entrepreneur` | `replica/reviews.csv`, `replica/feedback.md`, `replica/fixes.md` | Linked reviews and a fix plan |
| 9 | `/replica-brand` | `replica/brand.md`, `replica/brand.json` | Clean rebrand sweep |
| 10 | `/replica-launch` | `replica/launch/`, `replica/listing.json` | Store listing lint has no errors |
| 11 | `/replica-deploy` | `replica/preflight.md`, production setup | Full preflight, parity at least 80, clean sweep |

The skills contain the detailed method. The gates are the contract.

## State and gates

```bash
replica init                 # create replica/state.json
replica status               # current phase and next step
replica mark recon in_progress
# do the work
replica gate recon           # exit 0 pass, exit 2 blocked
replica mark recon passed    # only after the gate passes
```

`replica gate` checks the artifacts, not your confidence. If it fails, it
lists the exact file or value to fix.

## The CLI

| Command | Purpose |
| --- | --- |
| `replica init` | Create `replica/` and the state file. |
| `replica status` | Show phase status and the next phase. |
| `replica mark` | Update a phase status, note or artifact list. |
| `replica gate` | Check a phase against its evidence rules. |
| `replica doctor` | Check Python, git, node, Playwright, state and PATH. |
| `replica capture` | Capture a URL or a local fixture. Offline by default. |
| `replica extract` | Read routes, controls, colours and fonts from HTML. |
| `replica imgdiff` | Compare two screenshots by layout or pixels. |
| `replica parity` | Score the feature matrix and list what is missing. |
| `replica contrast` | Check WCAG contrast on design tokens. |
| `replica sweep` | Find the original's name, domain or colours. |
| `replica reviews` | Rank real reviews into complaints and requests. |
| `replica listing` | Lint an App Store or Google Play listing. |

Examples:

```bash
replica parity replica/features.csv --visual replica/diffs/*.json --markdown
replica imgdiff replica/screens/S07.png replica/clone-screens/S07.png --out diff-S07.png
replica contrast replica/design/tokens.json
replica sweep . --config replica/brand.json
replica listing replica/launch/listing.json
```

## Offline capture, real capture

`replica capture` defaults to a deterministic path:

- `--backend stub` with `--fixture` reads a local HTML or folder. No network,
  no downloads.
- `--backend manual` writes a checklist with the exact viewports to capture.
- `--backend playwright --allow-network` uses a real browser. It only works if
  Playwright and Chromium are installed by you.

The pack never downloads Chromium on its own.

## Models

The project default is `opencode/deepseek-v4.1-flash-free`. It is set in:

- `.opencode/opencode.json` as the project model and default agent,
- `.opencode/agents/replica.md` as the agent model.

To use another model, change both files. Model IDs always carry a provider
prefix. The deterministic CLI and the gates reduce how much the result depends
on the model, but use a model that can call tools reliably.

## Repository layout

```text
.opencode/
  skills/replica-*/SKILL.md    the 11 phase skills and their references
  commands/replica-*.md        one opencode command per phase
  agents/replica.md            orchestrator agent
  opencode.json                project default agent and model
tools/replkit/                 dependency-free Python CLI
bin/replica                    wrapper for a checkout
tests/                         unit, fixture and repository tests
docs/es/                       Spanish guides
scripts/install.sh             global or per-project install
```

Your project artifacts live in `replica/` in your own app, not in this repo.

## Development

```bash
make check     # compile, run 102 tests, lint if ruff is installed
make test      # unit tests only
./bin/replica --help
```

Rules for contributors:

- Core Python stays standard library only.
- Deterministic logic goes in `tools/replkit/`, not in skill prose.
- Every CLI command needs a test.
- English is the main language. Keep `README.es.md` and `docs/es/` in sync.
- No em dashes in repository text. The tests enforce it.
- Do not commit secrets, private screenshots or personal review exports.

## Spanish guides

- [Instalación](docs/es/instalacion.md)
- [Flujo de trabajo](docs/es/flujo.md)
- [Referencia del CLI](docs/es/cli.md)
- [Modelos y agente](docs/es/modelos.md)
- [Seguridad y legal](docs/es/seguridad-legal.md)

## Safety and legal

**Clean room.** OpenReplica studies what an app does and how a user moves
through it, then writes everything fresh. It never copies the target's source
code, proprietary assets, logos, trademarks, copy or private APIs.

**Allowed sources only.** Public pages and your own account. It never logs into
someone else's account, bypasses a paywall or scrapes behind a login. If your
account terms forbid using it to build a competitor, the skills say so and
stick to public sources.

**Rebrand before launch.** New name, new palette, new logo, new words. The
deploy gate blocks until the sweep is clean.

**"Clone any app" means functionality and flow.** Not the content, network or
licences an app owns. You can rebuild a music app's player, playlists and
sharing. You cannot clone its catalogue.

**No perfect clone guarantee.** Results depend on the app. A booking tool is
weeks. A spreadsheet engine is not. Recon sizes it honestly and parity gives
you a number, not a vibe.

**No invented evidence.** The Entrepreneur never fabricates reviews, quotes,
ratings or sources. Every quote is verbatim and linked, and the sample size is
stated.

**Check before you sell.** Run the trademark and domain checks the brand phase
lists, read the terms of everything you use, and talk to a lawyer before
launch if there is money on the line. This is not legal advice.

## Credit

Original project: [The Replica skill](https://github.com/Jakeschincariol/replica-skill)
by Jake Schincariol, [opusjake.ai](https://opusjake.ai). The upstream
copyright and MIT terms are retained in `LICENSE` and `NOTICE`.

OpenReplica modifications and the opencode integration are maintained by
Miguel.

## License

MIT. Take it, change it, ship it. See [LICENSE](LICENSE).
