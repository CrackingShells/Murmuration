# Draft: the next PI session (wave 4 of the reflective run)

Date: 2026-10-19, 23:56 JST. Written by the PI of waves 1–3 for the user to edit and launch.

## How to launch

1. In Claude Desktop, open a new Code session in `/Users/hacker/Documents/src/CrackingShells/Murmuration`.
   That folder is `main`, at the merge `84ff038` or later. Its `.claude/settings.local.json` opens the
   session as `murmuration:research-pi`. The plugin is read from that folder (`claude plugin list`
   shows "Read from: …/Murmuration"), so the session runs the merged code.
2. Paste the prompt below, after editing the budget line if you want a different figure.

## Prompt to paste

> Continue the reflective run on Murmuration with wave 4. This lab is in this repository. Read
> `__statera__/synthesis.md` (the "Still open" table), `__statera__/wave-03.md` and
> `__reports__/pilot/02-next_pi_session_v0.md` first. I will be asleep and will not answer, so
> decide by experiment and by the lab's own logging, as in waves 2 and 3.
>
> Work on a new branch, not on `main`, and do not merge. Every change to the plugin is a claim with
> an independent verdict, as before. I decide which ones land.
>
> In this order, as far as the budget goes:
> 1. **Open item 1, the Desktop probe.** You are a Desktop session. Find out what the plugin's
>    hooks receive here (`cwd`, `CLAUDE_PROJECT_DIR`, the lab root that `user_words.py` resolves).
>    Check whether my prompt landed in this lab's `__statera__/user_words.md`; answers I gave in
>    the question dialog never reached it in waves 2 and 3. That decides the parked w01-c10.
> 2. **Open item 8.** The report check pushes explorers past 100% of their budget after they have
>    decided to stop. Try the one-line fix in the explorer file (write the report before handing
>    back), and check it.
> 3. **Open item 10, compliance or anxiety.** 5 of 8 workers handed back at 75–99%. Run a control
>    without notes at the same budgets.
> 4. **Open item 11, search and reuse of `__instrumenta__/`.** Use a lab whose workers start after
>    scripts already exist, with enough scripts that `ls` is not the cheaper search.
> 5. **Open item 9, the hooks' own cost.** The budget hook costs about 90–100 ms of Python on every
>    tool call of every agent, the PI's included, and rescans the transcript each time. I said:
>    "Everything has a cost. things that look fast (like 100ms) piles up [...] the system itself must
>    be frugal [...] be lean." Measure first, then make the hooks lean.
> 6. **Open item 14,** the small fixes, if budget is left.
>
> Leave alone:
> - **Open item 12:** whether verifiers are exempt from the reuse rule for the code they check. I am
>   undecided.
> - **Open item 4:** budgets and team size. It needs several runs per arm.
>
> Budget: USD 25 of total spend for this wave, and stop by 08:00 JST. Pre-register each
> experiment's metrics and decision rule in a committed file before running it. Quote spend only from
> Claude Code's cost records or `/lab-status`. Close the wave with every puzzle disposed, update the
> synthesis, and show me what is still open.

## Notes for the session (the PI's lessons from waves 1–3)

- **Where headless runs go.** Run them outside this repository, in a `/tmp` folder:
  - with `--plugin-dir` pointing to an export of the branch;
  - with `COLGREP_DATA_DIR` set inside that folder, and `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`;
  - checking the md5 of `~/.claude/plugins/installed_plugins.json` before and after. In waves 1–2,
    runs made under a folder with this repository's `settings.local.json` added 210 registry
    entries; those were removed on 2026-10-19.
- **Raw run folders carry the user's email and organization id.** Keep them out of git, and move
  them to the Trash at the end of the wave.
- **The running session's plugin is the `main` checkout.** Changes on the wave's branch do not
  affect it; test them through `--plugin-dir` exports.
- **A `decision: block` sent on `PostToolBatch` ends a worker with no hand-back.** Blocks belong on
  `PostToolUse` (w03-c1).
- **A pre-registered rule must test what the user asked.** The wave-2 budget rule tested how tightly
  the stop holds, which the user had not asked about (wave 3 note).
- **The PI has overrun its own spend cap in every wave so far** (synthesis, "Cost of the study").
  Check spend at each phase against the cap above.

## Done on 2026-10-19 before this draft

- **Merged.** `claude/murmuration-system-optimization-8cff9e` went into `roadmap/reflective_run`
  (`256fa6d`), and that went into `main` (`84ff038`), both with `--no-ff`. The selftests and
  `claude plugin validate .` pass on `main`.
- **Open item 2, the plugin registry.** The 210 scratch-lab entries were removed from
  `installed_plugins.json`, leaving 2. A backup is in the session scratchpad.
- **Open item 3, the raw run folders.** They (662 MB) were moved to
  `~/.Trash/murmuration-raw-runs-2026-10-19/`, not deleted. Emptying the Trash deletes them.
- **Open item 13, stale colgrep indexes.** 156 of them (3.63 GB) were moved to
  `~/.Trash/colgrep-stale-indexes-2026-10-19/`. One, with a Unicode path, was left in place. 75
  indexes remain, 1 of them stale.
- **Plugin installation.** The local marketplace was refreshed. The plugin is read from the `main`
  folder, so the next session loads the merged code. The old 0.1.0 cache copy is not used.
