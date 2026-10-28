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

## Install on macOS

Murmuration is listed in the CrackingShells Nest marketplace as `murmuration@cracking-shells`.
Install it in each research project, at project scope, from that project's folder:

```bash
claude plugin marketplace add CrackingShells/Nest
claude plugin install murmuration@cracking-shells --scope project
```

Or, inside Claude Code (2.1.275 or later), in one step:

```
/plugin install murmuration --marketplace CrackingShells/Nest
```

Project scope writes `"murmuration@cracking-shells": true` under `enabledPlugins` in the project's
`.claude/settings.json`. Commit that file, and clones and worktrees of the project load the plugin
too. To let them find the marketplace on a machine that does not know it yet, add it with
`--scope project` as well.

Do not install it at user scope. Its permission guard would then run in every session on the
machine. It denies Claude's edits to `.claude/settings*.json` and `claude` flags that skip your
settings or hooks (`--bare`, `--setting-sources` without `user`, `CLAUDE_CONFIG_DIR=`). That is
right in a lab, but it gets in the way in your other projects.

The first session after the install copies the compiled guard for your machine into the plugin's
data folder (`~/.claude/plugins/data/murmuration-cracking-shells/bin/`) after checking it against
`bin/manifest.json`. If no binary fits, it falls back to the Python guard.

## Use

1. In the folder of your research project, run `/lab <your question>`. It creates:
   - `__statera__/`, holding `user_words.md` (your question, dated, kept as you typed it) and
     `wave-01.md`, the first wave note;
   - `__design__/framing.md`, a framing stub for the principal investigator;
   - `__pondus__/` (claims), `__scrupuli__/` (puzzles) and `__instrumenta__/` (helper scripts);
   - a block in `.ignore` that leaves hand-backs and raw data out of search;
   - the deny rules `Bash(pkill:*)` and `Bash(killall:*)` in `.claude/settings.local.json`
     (personal settings; keep that file out of version control).

   It never writes `.claude/settings.json` and never sets the session's main agent.
2. Open a new session in that folder as the principal investigator, in either of two ways:
   - start `claude --agent murmuration:research-pi`;
   - or add `"agent": "murmuration:research-pi"` to `.claude/settings.local.json`, so every new
     session there opens as the principal investigator.

   Then ask it to begin, for example: `Frame my question and plan the first wave.`
3. Run `/lab-status` to see open puzzles, the state of every claim, and spend per agent.

## Update

```bash
claude plugin marketplace update cracking-shells
claude plugin update murmuration@cracking-shells --scope project
```

Then start a new session. An update arrives only when the plugin's version number changes.

## Requirements

- Claude Code 2.1.295 or later.
- macOS or Linux (x86_64 or arm64), with Python 3 (standard library only).

Source, documentation and the research record of how the plugin was designed:
<https://github.com/CrackingShells/Murmuration>. Licence: AGPL-3.0-only (`LICENSE`).
