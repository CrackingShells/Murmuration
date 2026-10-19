# Murmuration

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

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

Murmuration is not yet published to a marketplace. To try it, load it from a local clone:

```bash
git clone https://github.com/CrackingShells/Murmuration.git
claude --plugin-dir /path/to/Murmuration
```

## Use

1. In the folder of your research project, run `/lab <your question>`. It creates the lab files
   and writes `.claude/settings.local.json`, which makes the next session open as the principal
   investigator and denies process kills by name pattern.
2. Start a new Claude Code session in that folder and ask it to begin.
3. Run `/lab-status` at any time to see open puzzles, the current label of every claim, and spend
   in USD per agent (a lower bound while a session is open).

Each worker's final report is saved verbatim under `__statera__/handbacks/`. That copy is kept for
you and the principal investigator to recover from; it is never fed back to agents. An explorer that
hands back without its findings report is asked once to write it.

`/lab` creates:

| Path | Holds |
|:--|:--|
| `__design__/framing.md` | The question, notation, scope and rules for the team |
| `__statera__/` | Your words (recorded automatically), one note per wave, the synthesis, saved hand-backs and a log of the report check |
| `__reports__/wave-NN/<agent>/` | Each explorer's findings report, from the research-loop template |
| `__pondus__/` | One file per claim, with each verifier's verdict |
| `__scrupuli__/` | Each agent's puzzles |

## Requirements

- Claude Code 2.1.271 or later.
- Python 3 (standard library only) for the hooks and the status script.

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

## Contributing

Design records for contributors are in [`__reports__/`](__reports__/) and the build plan in
[`__roadmap__/`](__roadmap__/). Questions and suggestions go to the issue tracker once the
repository is published.

## License

AGPL-3.0. See [LICENSE](LICENSE).
