---
type: findings
wave: wave-05
author: explorer-w05-e
date: 2026-10-21
version: v0
decision-required: intervene
---

# Running a worktree's own plugin branch: findings (v0)

I stayed inside the brief. One addition: I read the command line of the Desktop session I run in (`ps`), which the brief did not ask for. It gave the cause of the main-checkout routing (below).

## Result

A Desktop worktree session does not read the worktree's `.claude/` at all, and no worktree-local declaration can make it run the worktree's plugin branch. The Desktop launches the session with the hidden flag `--project-config-root <main checkout>`. With that flag, project settings, local settings, `CLAUDE_PROJECT_DIR` and the base of a relative `directory` marketplace path all become the main checkout (CHECKED, headless, scratch repo plus worktree, claude 2.1.304) [source: `01-run_log.md`, rows ps, G_*, F*, H*]. The user's reinstall-on-start idea cannot work for this plugin: `claude plugin update` on a `directory` marketplace is a documented no-op ("read from its folder: nothing to update"), and plugins are loaded before SessionStart fires.

Leanest ways, by what they need (details in the table):
- Desktop, no flag control: one change in the main checkout's `.claude/settings.local.json` (outside my remit, and the Desktop denies Edit on that file to the session) so that the marketplace path is a symlink, plus one `ln -sfn <worktree> <link>` per worktree switch, taking effect at the next session start (CHECKED headless). Per-session cost, once set up: 0 s and 0 tokens. The link is global: concurrent sessions on different branches would share it (CONJECTURE, not run).
- Terminal CLI: `claude --plugin-dir .` from the worktree overrides the enabled same-name plugin (CHECKED). Not available in Desktop (no setting known; CONJECTURE).
- A SessionStart check that warns when the plugin root is not the session folder's git toplevel: 42 ms median, works under Desktop only if it reads the event's `cwd`, not `CLAUDE_PROJECT_DIR` (CHECKED). It detects the problem; it fixes nothing, and it only runs if the plugin that is read already contains it.

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Settings files read, CLI in worktree root, no flag | worktree `settings.json` and `settings.local.json`, plus the MAIN checkout's `settings.local.json`; main's `settings.json` not read. On a key set in both local files, main's value wins | CHECKED (scratch, n=1 per case, env-key probe) | `01-run_log.md` run B |
| Settings files read, CLI in a subfolder of the worktree | project dir = the subfolder; only main's local file is read (no walk up to the worktree root) | CHECKED (n=1) | run D |
| Settings files read, `--project-config-root <main>` (what this Desktop session was launched with) | main `settings.json` and main `settings.local.json` only; the worktree's `.claude/` is not read; `CLAUDE_PROJECT_DIR` = main; hook payload `cwd` = worktree | CHECKED headless; Desktop's flag value CHECKED by `ps` on this session; that the Desktop session then behaves as the headless one is CONJECTURE | runs G_rootmain, H1; ps row |
| `--project-config-root <worktree>` | only the worktree's files; `.` marketplace path resolves to the worktree; plugin read from the worktree | CHECKED (n=1) | runs G_rootwt, F1, F2b |
| Flag in `claude --help` | absent (hidden); the binary has the option string and errors `--project-config-root must be an absolute local path` | CHECKED (`strings` on the binary) | run log, ps row |
| Local-vs-local conflict on `enabledPlugins` | main true / wt false: loaded. main false / wt true: not loaded. So a worktree's local file cannot disable what main's local enables, nor override it | CHECKED (n=1 each) | runs E5a, E5b |
| The PI's setup (second marketplace, same plugin name, `murmuration-local` disabled in the worktree's local) | both plugins count as enabled (`Found 5 plugins (5 enabled)`); the second one's hooks are dropped: `Skipping duplicate hook registration ... already registered from another source`; the hooks that ran were main's | CHECKED on the dummy plugin; Desktop not run | run E7 |
| Relative `directory` marketplace path in settings (`.`, `./sub`) | resolved against the main checkout (or the `--project-config-root`), not the session cwd; `${CLAUDE_PROJECT_DIR}` is not expanded | CHECKED (n=1 each) | runs E2, E3, E4a |
| Same relative path, project-scope `settings.json` declaration, headless | ignored: `no marketplaces declared`. Only a user-level or `--settings` declaration loads, so project-scope relative paths were tested through `--settings` | CHECKED headless; interactive behaviour NOT tested | run E1 |
| `claude plugin marketplace add <relative> --scope local` from a worktree | writes main's `settings.local.json`; the stored path is absolute, made from the cwd | CHECKED (reproduces the PI's observation; n=1) | CLI add row |
| `... --scope project` from a worktree | writes the worktree's own `.claude/settings.json` (tracked), absolute path (not portable across checkouts) | CHECKED (n=1) | CLI add row |
| `--plugin-dir <relative>` | resolved against cwd; overrides an installed same-name plugin (`overrides installed version`), one hook set runs | CHECKED (n=1) | runs E4b, E6c |
| `claude plugin update` / `marketplace update` on a directory marketplace | no-op: "read from its folder ... nothing to update. Edits there take effect at the next session start or /reload-plugins"; 0.44 to 0.49 s per call; the cache `installPath` recorded in `installed_plugins.json` is never created | CHECKED (2 calls) | update row |
| When plugin hooks are active relative to SessionStart | the plugin is loaded before SessionStart fires (debug order); in a headless first run a newly declared marketplace is installed after SessionStart, so its hook does not fire until the second run | CHECKED (debug order, n=1) | runs E2 and E2b |
| Marketplace path = symlink, repointed between runs | next session reads the new target with no re-registration; reported root is the link path | CHECKED (2 runs) | runs I1, I2 |
| SessionStart check hook | 42.5 ms median (30 runs, 57 ms max); platform-reported 322 ms for the hook launch in a cold headless run; output arrives as `additionalContext` | MEASURED for the script alone (`__instrumenta__/plugin_root_check.py`, 30 runs, `python3`), the platform number is one run | run log timings, H3 |
| Reload scope: `/reload-plugins` re-reads plugins, skills, agents, hooks, servers | the docs say a reload prints counts for these; changes that add or remove a plugin MCP server need `--force` | CITED: code.claude.com/docs/en/plugins/troubleshooting (retrieved through context7 `/websites/code_claude`); not run, headless cannot reload | |
| Plugins "load at session start from `installed_plugins.json` and the cache"; `plugin update` loads "next session or after `/reload-plugins`" | consistent with the runs, except that a directory marketplace is read in place | CITED: code.claude.com/docs/en/plugins/loading and /plugins/cli-reference (context7) | |

### The user's reinstall-on-start idea, answered
- A project- or local-scope SessionStart (or resume) hook that runs `claude plugin update murmuration@murmuration-local`: it does nothing for this plugin (no-op message above), costs about 0.45 s, and by then the session has already loaded its plugins, so even a real update would show only after `/reload-plugins` or next start (CHECKED order; CITED docs). For a `git`/`github` marketplace it would fetch the remote head, never the worktree's uncommitted branch tree (CITED; not run, no downloads).
- The hook must also come from somewhere: in a Desktop worktree session project/local settings come from main, whose `settings.json` and `settings.local.json` the Desktop denies Edit on in the session's own permissions (ps row). So the hook could only be added by a human editing main, and it would run in every worktree session for that checkout.
- What "always the latest version" already is here: a `directory` marketplace is read from the main checkout's working tree at every session start, so the plugin is always the latest *of the branch checked out in main*. The gap is that wave work lives in worktree branches; what is missing is "the worktree's branch", not "a newer install".

### What each lever cannot do
| Lever | Cannot |
|:--|:--|
| Worktree-local settings (the PI's `murmuration-w5` setup) | be read under Desktop's `--project-config-root`; under a plain CLI it is merged under main's local file, and main's enabled plugin wins on conflicts, with the duplicate hooks dropped |
| Relative marketplace path | resolve against the session folder; it resolves against the config root (main) |
| `--plugin-dir` | be passed by the Desktop (no setting known) |
| Project-scope declaration committed in the branch | work headless; also an absolute path (what the CLI writes) is per checkout and wrong in any other |
| Symlink pointer | serve two sessions on different branches at once; it needs one edit to main's local settings and a repoint at each switch |
| SessionStart check | change what runs; it can only say so, and only after the stale plugin contains it |
| `/reload-plugins` | change what a reload reads: the same config root and the same marketplace path |

## Worst-fitting case
The story "the Desktop reads main's settings" fits the runs, but two cases fit worse. (1) The first check script I wrote compared the plugin root with `CLAUDE_PROJECT_DIR`. Under Desktop that variable is the main checkout, so root and "project" agree and it stays silent exactly where it is needed (`02-check_root_wrong_variant.py`, 65 ms; the corrected one reads the payload `cwd`). (2) The settings in this worktree on disk do not match the wave-05 note: `.claude/settings.local.json` here still enables `murmuration@murmuration-local` and declares no `murmuration-w5` marketplace, and `.claude-plugin/` holds only `plugin.json` [source: `ls` and `cat` of this worktree, 14:42 JST]. So I could not tell from disk what the PI's session loaded.
Prior work: only the docs above (CITED, via context7). Nothing is claimed about the Desktop beyond the `ps` flags and the headless runs.

## Not covered
- Desktop itself (a real worktree session, `/reload-plugins`, the trust prompt for project-scope marketplaces): not testable headless. CONJECTURE that it matches the headless runs given the same flags.
- Whether the Desktop has a setting that changes `--project-config-root`: unknown.
- A reload in a running session (`/reload-plugins` re-reading hooks and agents): CITED only.
- Concurrency of the symlink pointer between two sessions: not run.
- Git-sourced marketplaces (`git`, `github` source) and `autoUpdate`: not run (no downloads).
- Cost in tokens: every run was a not-logged-in headless run with no model call, so no token cost is measured.

## Steering questions
- [now] Is the user willing to edit the main checkout's `.claude/settings.local.json` once (point `murmuration-local` at a symlink path)? I may not, and the Desktop denies the session that edit.
- [now] Is a one-line `ln -sfn` at worktree creation (or at the start of a wave) acceptable as "no manual step", given that two concurrent sessions on different branches would then share one plugin?
- [now] Should the SessionStart check be proposed as a claim against `hooks/hooks.json`? Prototype: `__instrumenta__/plugin_root_check.py`.

## Pointers
- `__reports__/wave-05/explorer-w05-e/01-run_log.md`: every run, with the flags and what was read.
- `__reports__/wave-05/explorer-w05-e/02-check_root_wrong_variant.py`: the check that fails under Desktop.
- `__instrumenta__/plugin_root_check.py`, `__instrumenta__/w05e_probe_run.sh`, `__instrumenta__/w05e_dummy_echo_root.py` (cite as `@<commit>` once committed).
- Scratch, not committed: `/private/tmp/murmuration-w05/explorer-w05-e/` (`repo/`, `wt/`, `cfg*/`, `dbg_*.log`; debug files carry account data).
- Commands: `ps -o command= -p $CLAUDE_PID`; `./runp.sh <label> <cwd> <flags>` with `CFG=<scratch config dir>`; `claude plugin update dummy@dummy-mp` in `wt/` under `CLAUDE_CONFIG_DIR=cfg7`.
