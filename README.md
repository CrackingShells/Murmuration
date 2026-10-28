# Murmuration

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

> [!WARNING]
> **Claude Code only, macOS and Linux.** Murmuration is a Claude Code plugin (Claude Code 2.1.295 or
> later). Its hooks use Claude Code events and options that other harnesses do not have, so it does
> not install in Codex, VS Code, Cursor or other Agent Plugins clients; support for them is planned.
> Windows installs are not supported yet: the hook binary is built for Windows, but the hooks that
> install it run `python3`, which Windows does not provide under that name.

A research team for Claude Code: a principal investigator that follows what does not add up, and
colleagues who explore, prove, measure and check each other's work.

A murmuration is a flock of starlings that moves as one with no bird in command: each bird watches
a few neighbours, and a turn noticed at the edge travels through the whole flock. Murmuration aims
at the same property for a research team. Authors and verifiers talk to each other directly, every
member records the puzzles it cannot let go of, and the principal investigator decides which of
them change what the team does next. Murmuration is part of the Cracking Shells family of
repositories, alongside [Nest](https://github.com/CrackingShells/Nest), the org's plugin
marketplace.

## The team

| Role | Model | Does |
|:--|:--|:--|
| research-pi | Opus, main session | Frames the question, plans waves, decides which hunches become claims, writes the synthesis |
| explorer | Sonnet | Probes an open direction or surveys prior work; returns raw material and puzzles |
| author | Sonnet | Turns a hunch into a labelled claim by proof or experiment |
| reproducer | Sonnet | Verifies empirical claims independently, then questions the author |
| proof-adversary | Sonnet | Verifies proofs and exact claims independently, then questions the author |

## Install

Murmuration is listed in [Nest](https://github.com/CrackingShells/Nest), the Cracking Shells
marketplace:

```bash
claude plugin marketplace add CrackingShells/Nest
claude plugin install murmuration@cracking-shells --scope project
```

Run the install from each research project's folder, at project scope. Its permission guard would
otherwise run in every session on the machine. The guard denies edits to Claude Code settings files
and `claude` flags that skip your settings or hooks. To update:
`claude plugin marketplace update cracking-shells`, then
`claude plugin update murmuration@cracking-shells --scope project`, then start a new session. The
[plugin README](plugins/murmuration/README.md) has the details.

The plugin lives in [`plugins/murmuration/`](plugins/murmuration/); the marketplace installs that
folder only. To work on it from a clone, load it directly:

```bash
git clone https://github.com/CrackingShells/Murmuration.git
claude --plugin-dir Murmuration/plugins/murmuration
```

## Use

1. In the folder of your research project, run `/lab <your question>`. It creates the lab files
   and writes `.claude/settings.local.json`, which denies process kills by name pattern. It does
   not choose the session's main agent.
2. Start a new Claude Code session in that folder as the principal investigator, with
   `claude --agent murmuration:research-pi`. Or add `"agent": "murmuration:research-pi"` to
   `.claude/settings.local.json` so every new session there opens as the PI. In the Claude
   desktop app, use the settings line: its `@` agent menu offers only agents kept as files in
   `~/.claude/agents/` or `.claude/agents/`, so it does not list plugin agents. Then ask it to begin.
3. Run `/lab-status` at any time to see open puzzles, the current label of every claim, and spend
   in USD per agent (a lower bound while a session is open).

Each worker gets a budget in USD and in minutes, set by `Budget: USD <n>` and `Time: min <n>` lines
in its brief or a default per role (never under USD 0.30 and 3 minutes). Hooks tell the worker its
budgets at the start and send it `Spent X of USD Y (Z%); t of T min (W%)` at 50, 75, 87.5 and 93.75%
and at every check from 100%. From 100% the worker finishes if one or two more steps do it, and
otherwise hands back and asks the principal investigator, who holds the money, for more; the PI
decides whether to resume it with a raise. The figures are in `__statera__/harness.jsonl`. Each
worker's final report is also saved verbatim under `__statera__/handbacks/`. That copy is kept for
you and the principal investigator to recover from; it is never fed back to agents. An explorer that
hands back without its findings report is asked once to write it.

`/lab` creates:

| Path | Holds |
|:--|:--|
| `__design__/framing.md` | The question, notation, scope and rules for the team |
| `__statera__/` | Your words (recorded automatically), one note per wave, the synthesis, saved hand-backs, the budget log and a log of the report check |
| `__reports__/wave-NN/<agent>/` | Each explorer's findings report, from the research-loop template |
| `__instrumenta__/` | Helper scripts, one file each, named for what it does |
| `__pondus__/` | One file per claim, with each verifier's verdict |
| `__scrupuli__/` | Each agent's puzzles |

`/lab` also writes a `.ignore` and builds the colgrep index of the lab once. The `.ignore` hides the
hand-back copies, `raw/`, `runs/` and `generated/` folders from Grep and colgrep (Glob still lists
everything). Workers search `__instrumenta__/` for a script before writing one. A scratch lab you will
delete: start Claude Code in it with `COLGREP_DATA_DIR=<folder>/.colgrep`.

## Requirements

- Claude Code 2.1.295 or later (the permission guard fails closed through `onFailure: "block"`, added in 2.1.295; exec-form hooks need 2.1.139).
- macOS or Linux (x86_64 or arm64).
- Python 3 (standard library only) for the hooks and the status script.

The hooks run a small Rust program, `murmuration`, built by CI for each platform and installed at
session start into the plugin's data folder. It is installed only when its hash, the hashes of the
sources it was built from, and a self-test against the Python hooks all agree; otherwise the Python
hooks run instead, which is correct and slower, and the session is told why.

## Tools by role

Each worker gets an explicit tool list; the principal investigator inherits everything. MCP servers
named below are used when present and skipped when absent.

| Role | Built-in tools | MCP servers |
|:--|:--|:--|
| research-pi | all | all |
| explorer | Read, Glob, Grep, Bash, Write, Edit, WebFetch, WebSearch, ToolSearch | WolframToolkit, colgrep, arxiv, context7 |
| author | Read, Glob, Grep, Bash, Write, Edit, ToolSearch, SendMessage | WolframToolkit, colgrep, arxiv |
| reproducer, proof-adversary | Read, Glob, Grep, Bash, Write, Edit, ToolSearch, SendMessage | WolframToolkit, colgrep |

To use another server, add its `mcp__<server>__*` entry to the agent file's `tools` line. Workers
do not get the `Skill` tool: the `research-loop` skill is preloaded, and without `Skill` a worker
does not carry the listing of every installed skill in its context.

## Running a lab headless

`claude -p` can stop background agents that are still running 10 minutes after the principal
investigator's last turn; the worker is then cut off and the synthesis may never be written. This
does not happen in every run, and runs whose workers finish sooner are not affected. For an unattended run, set
`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` (no ceiling) and cap the spend instead:

```bash
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 claude -p --agent murmuration:research-pi --max-budget-usd 20 "<your question>"
```

## Repository layout

| Path | Holds |
|:--|:--|
| `plugins/murmuration/` | The plugin: agents, skills, hooks, the hook scripts, the Rust source of the hook binary, and the binaries CI built (`bin/`) |
| `.github/workflows/guard-binaries.yml` | Builds, checks and commits the hook binaries |
| everything else | The research record (below) |

## Research record

Murmuration was designed by running it, over nine research waves, and what the waves found changed
the plugin. The record of that design experiment is kept here, as notebooks are kept beside a paper.
Nothing in it is installed.

| Path | Holds |
|:--|:--|
| `__design__/` | The framing of the design question; `settings_record/` keeps the Claude Code settings the lab ran with |
| `__statera__/` | The maintainer's words (`user_words.md`), one note per wave, and the synthesis |
| `__reports__/` | Design reviews, the genesis study, platform probes, and every worker's findings report by wave |
| `__pondus__/` | One file per claim, with each verifier's verdict |
| `__scrupuli__/` | Each agent's puzzles |
| `__instrumenta__/` | The helper scripts the waves wrote |
| `__roadmap__/` | The build roadmaps, including the one for this release |
| `probes/`, `validation/` | Platform probes and the instrument validation of wave 1 |

Claims cite evidence as `path@commit`; paths in them are the paths at that commit (the plugin lived at
the repository root until this release).

## Maintainers

- **CI owns `plugins/murmuration/bin/`.** A push to `main` that touches `plugins/murmuration/rust/`
  or `plugins/murmuration/scripts/` builds the binary for five targets, checks each one against the
  Python guard, smoke-installs it, and commits the result as `build(bin): …`. Do not commit binaries
  by hand.
- **Bump the version only after the binaries.** Raise `version` in
  `plugins/murmuration/.claude-plugin/plugin.json` only once CI's `build(bin)` commit for the same
  sources is on `main`. Installed copies refresh only when the version changes, and a bump ahead of
  the binaries ships the Python fallback.
- **Dev copy beside the published one.** In this repository and its worktrees, load the working
  tree through a local, untracked marketplace (for example `murmuration-local`, a root
  `.claude-plugin/marketplace.json` whose source is `./plugins/murmuration`), installed at local
  scope. Never enable `murmuration@cracking-shells` here. Both copies are named `murmuration`, so
  with both enabled every hook runs twice and the agent names collide. Other projects use only
  `murmuration@cracking-shells`, at project scope. Nothing is installed at user scope.
- **Pre-commit hook (optional):**
  `ln -s ../../plugins/murmuration/scripts/git-hooks/pre-commit .git/hooks/pre-commit`. It rebuilds
  the host binary under `rust/target/` and replays the guard corpus against the Python guard; it
  never writes `bin/`.
- **Selftests:** each script under `plugins/murmuration/scripts/` has a `--selftest` mode
  (`python3 -I <script> --selftest`).

## Contributing

Questions and suggestions go to the [issue tracker](https://github.com/CrackingShells/Murmuration/issues).

## License

AGPL-3.0. See [LICENSE](LICENSE).
