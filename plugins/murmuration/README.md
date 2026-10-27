# Murmuration (plugin)

> [!WARNING]
> **Claude Code only, macOS and Linux.** Needs Claude Code 2.1.295 or later. Other harnesses and
> Windows installs are not supported yet.

A research team for Claude Code: a principal investigator that follows what does not add up, and
colleagues who explore, prove, measure and check each other's work.

| Role | Model | Does |
|:--|:--|:--|
| research-pi | Opus, main session | Frames the question, plans waves, decides which hunches become claims, writes the synthesis |
| explorer | Sonnet | Probes an open direction or surveys prior work; returns raw material and puzzles |
| author | Sonnet | Turns a hunch into a labelled claim by proof or experiment |
| reproducer | Sonnet | Verifies empirical claims independently, then questions the author |
| proof-adversary | Sonnet | Verifies proofs and exact claims independently, then questions the author |

## Use

1. In the folder of your research project, run `/lab <your question>`. It creates the lab files and
   writes `.claude/settings.local.json`, so the next session opens as the principal investigator.
2. Start a new Claude Code session in that folder and ask it to begin.
3. Run `/lab-status` to see open puzzles, the state of every claim, and spend per agent.

## Requirements

- Claude Code 2.1.295 or later.
- macOS or Linux (x86_64 or arm64), with Python 3 (standard library only).

Source, documentation and the research record of how the plugin was designed:
<https://github.com/CrackingShells/Murmuration>. Licence: AGPL-3.0-only (`LICENSE`).
