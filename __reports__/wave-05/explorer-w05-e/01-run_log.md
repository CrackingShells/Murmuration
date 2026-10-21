# Run log, explorer-w05-e (2026-10-21, claude 2.1.304, macOS)

Scratch: `/private/tmp/murmuration-w05/explorer-w05-e/` holds `repo/` (main checkout, branch main), `wt/` (git worktree of it,
branch wt), `cfg*/` (one scratch `CLAUDE_CONFIG_DIR` per experiment; nothing under `~/.claude/` was written: its two registries
have mtime 14:41:47 and 14:41:48, before the first run), `dbg_*.log` (debug files, NOT copied here: they carry account data),
`hook.log` (overwritten by each run), `runp.sh` (= `__instrumenta__/w05e_probe_run.sh`).
Dummy plugin: `.claude-plugin/plugin.json`, a one-plugin `marketplace.json` (source `./`), `hooks/hooks.json` with one
SessionStart command running `scripts/echo_root.py` (= `__instrumenta__/w05e_dummy_echo_root.py`), and a `MARKER` file
that differs per branch (`main` in `repo/`, `wt` in `wt/`).

All runs are headless `claude -p ok --model haiku` in a scratch config dir that is NOT logged in: the CLI answers "Not logged
in" after SessionStart has fired, so the hook line is produced and no model call is made (cost: none). Each cell below is one run
unless a pair is shown (a marketplace added by a settings file is installed after SessionStart in the first headless run; the
second run loads it; see run E2/E2b).

Settings files used in E1: `repo/.claude/settings.json` and `.local.json`, `wt/.claude/settings.json` and `.local.json`, each
with a distinct `env` key (`W05_<dir>_PROJECT`, `W05_<dir>_LOCAL`) and one shared key per level, so the hook can print which files
were merged.

| run | cwd | flags | what was read / result (from hook.log and the debug "Watching for changes in setting files" line) |
|:--|:--|:--|:--|
| B | wt | `--plugin-dir wt` | env seen by hook: `W05_wt_PROJECT`, `W05_wt_LOCAL`, `W05_repo_LOCAL`; not `W05_repo_PROJECT`. Shared local key = `repo_local` (main's local beat wt's local); shared project key = `wt_project`. Watched files: cfg/settings.json, wt/.claude/settings.json, wt/.claude/settings.local.json, repo/.claude/settings.local.json |
| C | repo | `--plugin-dir repo` | baseline: repo project + repo local only (no wt files) |
| D | wt/sub | `--plugin-dir wt` | project dir = wt/sub; watched files: cfg/settings.json, repo/.claude/settings.local.json only; wt/.claude not read (no `.claude` in the subfolder, and no walk up) |
| E1 | wt | none; project settings.json holds `extraKnownMarketplaces` (`directory`, path `.`) and `enabledPlugins` | debug: `installPluginsForHeadless: no marketplaces declared`; `Skipped auto-recording dummy@dummy-mp: enabled only by repo-authored settings`. Headless runs ignore a project-scope marketplace declaration |
| E2, E2b | wt | `--settings flag_settings_rel.json` (same JSON, path `.`) | debug: `Reading marketplace from .../repo/.claude-plugin/marketplace.json`; hook (second run): root=`repo`, marker=`main`, cwd=`wt`. `.` resolved to the MAIN checkout |
| E3a, E3b | wt | `--settings` with path `./only_in_wt` (a folder that exists only in wt) | `Marketplace file not found at .../repo/only_in_wt/.claude-plugin/marketplace.json` |
| E4a | wt | `--settings` with path `${CLAUDE_PROJECT_DIR}/only_in_wt` | not expanded: `Reading marketplace from .../repo/${CLAUDE_PROJECT_DIR}/only_in_wt/...` |
| E4b, E4c | wt, wt/only_in_wt | `--plugin-dir .`, `--plugin-dir ..` | relative `--plugin-dir` resolves against cwd: root = wt, marker = wt |
| CLI add (cfg5) | wt | `claude plugin marketplace add ./only_in_wt --scope local` | wrote `repo/.claude/settings.local.json` (md5 changed), wt's local unchanged; the path stored is absolute (`.../wt/only_in_wt`): the CLI resolves against cwd when adding |
| CLI add (cfg5) | wt | same with `--scope project` | wrote `wt/.claude/settings.json` (the worktree's own, tracked file), absolute path |
| E5a | wt | marketplace user-scope; main local `enabledPlugins` true, wt local false | plugin loaded (hook fired): main wins |
| E5b | wt | main local false, wt local true | plugin NOT loaded (no hook line): main wins |
| E5d | wt | main local `{}`, wt local true | plugin loaded |
| (E5c invalid: `null` is not a boolean, the file failed to load) | | | not counted |
| E6a, E6b | wt | marketplace = repo; main local enables | root=`repo`, marker=`main` |
| E6c | wt | same + `--plugin-dir wt` | one hook line, root=`wt`; debug: `Plugin "dummy" from --plugin-dir overrides installed version` |
| E7a, E7b | wt | two marketplaces (repo: `dummy-mp`, wt: `dummy-wt-mp`), both with plugin `dummy`; main local enables `dummy@dummy-mp`; wt local disables it and enables `dummy@dummy-wt-mp` | one hook line, root=`repo`; debug: `Found 5 plugins (5 enabled)`; `Skipping duplicate hook registration for plugin "dummy" from dummy@dummy-wt-mp - already registered from another source` |
| update (cfg7) | wt | `claude plugin update dummy@dummy-mp` x2, `claude plugin marketplace update dummy-mp` | `dummy is read from its folder, .../repo: nothing to update. Edits there take effect at the next session start or /reload-plugins.` Wall 0.49 s, 0.44 s; marketplace update 0.43 s. `installed_plugins.json` has a cache `installPath` that does not exist on disk |
| ps of the Desktop session | | `ps -o command= -p $CLAUDE_PID` | flags: `--setting-sources=user,project,local --add-dir=<main> --project-config-root <main> --settings {fastMode, deniedMcpServers, permissions.deny: Edit(<main>/.claude/settings.json), Edit(<main>/.claude/settings.local.json), Edit(<main>/.claude/hooks/**), .../skills/**, .../agents/** ...}`; no `--plugin-dir` |
| G_nofl / G_rootmain / G_rootwt | wt | none / `--project-config-root repo` / `--project-config-root wt` | nofl: wt project + wt local + repo local. rootmain: repo project + repo local only, `CLAUDE_PROJECT_DIR`=repo, wt/.claude not read. rootwt: wt project + wt local only, `CLAUDE_PROJECT_DIR`=wt |
| F1, F2, F2b | wt | `--project-config-root wt` (+ `--settings` with path `.`) | marketplace read from `wt/.claude-plugin/marketplace.json`; hook root=wt, marker=wt |
| H1, H2 | wt | `--project-config-root repo` (what Desktop passes), marketplace = repo, enabled by `--settings` | hook payload cwd=wt, git toplevel=wt, `CLAUDE_PROJECT_DIR`=repo, root=repo |
| H3 | wt | same, repo's hooks.json also runs `plugin_root_check.py` | debug: `Hooks: Parsed initial response: ... "WARNING: this session runs the plugin read from .../repo, but its own folder .../wt holds a plugin too. Edits there are not what runs."` The hook reports `finished with status 0 (322ms)` |
| I1, I2 | wt | `--project-config-root repo`, marketplace path = symlink `current_plugin` | link -> repo: marker `main`; after `ln -sfn wt current_plugin`: marker `wt`. No re-registration. Plugin root is reported as the link path |

Timings (python3 from `miniforge3`, 20 to 30 runs each, subprocess spawn, payload on stdin):

| command | median ms | max ms |
|:--|--:|--:|
| `python3 -c pass` | 33.2 | 37.7 |
| `plugin_root_check.py` (walk up to `.git`, no git call) | 42.5 | 57.4 |
| `check_root.py` (compares with `CLAUDE_PROJECT_DIR`; wrong under Desktop, see report) | 65.4 | 91.5 |
| `echo_root.py` (json + `git rev-parse`) | 158.1 | 283.1 |
| `claude plugin update` on a directory marketplace | ~450 | 490 |
