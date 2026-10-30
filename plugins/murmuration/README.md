# Murmuration (plugin)

> [!WARNING]
> **Claude Code only; macOS and Linux. Windows tested in CI only, no live session yet.** Needs
> Claude Code 2.1.295 or later. Other harnesses are not supported yet.

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

Do not install it at user scope. Its hooks run on every prompt and tool call, and act only in a
folder that holds `__statera__/`, so at user scope every session on the machine would start them for
nothing.

The first session after the install copies the compiled hook binary for your machine into the
plugin's data folder (`~/.claude/plugins/data/murmuration-cracking-shells/bin/`) after checking it
against `bin/manifest.json`. If no binary fits, the Python hooks run instead.

## Hardening

Murmuration no longer ships a permission guard. To stop Claude from switching to bypass mode, where
every tool runs without asking, set this in `~/.claude/settings.json`:

```json
{ "permissions": { "disableBypassPermissionsMode": "disable" } }
```

Outside bypass mode, Claude Code never auto-approves a write under `.claude`, so edits to your
settings files still wait for your approval.

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
     session there opens as the principal investigator. In the Claude desktop app this is the
     way: its `@` agent menu offers only agents kept as files in `~/.claude/agents/` or
     `.claude/agents/`, so it does not list plugin agents.

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
- macOS or Linux (x86_64 or arm64), or Windows (x86_64; tested in CI only, no live session yet), with
  Python 3 (standard library only). On Windows it must be reachable as `python3` on PATH: Microsoft
  Store Python provides that name, but a python.org-only install has only `python` and `py`, so add a
  `python3` alias. Stock Windows ships a Store `python3.exe` App Execution Alias that prints "Python
  was not found" and exits 9009; that stub counts as no `python3`. A real `python3` must come before
  `WindowsApps` on PATH, or turn the alias off (Settings, Apps, Advanced app settings, App execution
  aliases). Without a real one, the install, resume-brief and user-words hooks fail without
  blocking, and the budget and hand-back hooks error.

Source, documentation and the research record of how the plugin was designed:
<https://github.com/CrackingShells/Murmuration>. Licence: AGPL-3.0-only (`LICENSE`).
