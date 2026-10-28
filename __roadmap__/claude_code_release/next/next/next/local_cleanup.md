# Local installs and worktrees cleanup

**Goal**: Only the main checkout keeps `murmuration@murmuration-local`; the stale installs, worktrees, cache and data dirs that Eliott names are gone.
**Pre-conditions**:
- [x] The cleanup list shown to Eliott, with each worktree's uncommitted files (2026-10-28; the 3 `.pid` files in wave-8 pointed at no live process)
- [x] Eliott's word on each item, 2026-10-28: he selected all three options, "Orphans + stale dirs", "7 clean worktrees" and "6 dirty worktrees"
**Success Gates**:
- ✅ [run] `installed_plugins.json` lists no `murmuration@murmuration-local` entry whose `projectPath` does not exist
- ✅ [run] Every worktree Eliott named is gone from `git worktree list`, and its local install is gone too
- ✅ [run] The main checkout's install and `~/.claude/plugins/data/murmuration-murmuration-local/bin/.verified` are still there
**References**: plan `plan-murmuration-publish-step3.md` (shared notes folder of session local_e5401f72), "Leftover state"

## Step 1: List, ask, remove
**Goal**: Remove only what Eliott names.
**Implementation Logic**:
1. Show the list: 2 orphaned `/private/tmp/murmuration-w08/…` entries; 7 clean merged worktrees (`task/ci-workflow`, `task/posix-redirects`, `task/rust-portability`, `task/targets-contract`, `task/windows-paths`, `release/claude-code`, `claude/murmuration-system-optimization-8cff9e`); 6 merged worktrees with uncommitted files (blissful-villani 2, lab-system-optimization 2, research-wave-9 3, wave-4 2, wave-8 9, xenodochial-franklin 3), each with its `git status --short`; cache `murmuration-w5`; data `murmuration-inline`.
2. For each named worktree: `claude plugin uninstall murmuration@murmuration-local --scope local` run with that worktree as cwd, then `git worktree remove <path>`. The branch is kept unless Eliott says otherwise.
3. For the orphaned entries, whose folders are gone: uninstall from a recreated empty folder at that path, or edit nothing by hand and report what the CLI allows.
4. Never `pkill` or `killall`; never `--force` on a dirty worktree without Eliott's word.
**Deliverables**: none in the repo; this leaf's Results (what was removed, on which word)
**Consistency Checks**: `python3 -I -c 'import json,os;d=json.load(open(os.path.expanduser("~/.claude/plugins/installed_plugins.json")));raise SystemExit(any(not os.path.isdir(e.get("projectPath","/")) for e in d["plugins"].get("murmuration@murmuration-local",[])))'` (expected: PASS)
**Commit**: `docs(roadmap): record the local install cleanup`
**Results (2026-10-28)**:
- Uninstalled `murmuration@murmuration-local` at local scope from the 7 worktrees that held it (murmuration-system-optimization, blissful-villani, lab-system-optimization, research-wave-9, wave-4, wave-8, xenodochial-franklin). The 5 `cc-*` task worktrees and `release-claude-code` had no install: the CLI answered "not installed in local scope".
- The 2 orphaned entries (`/private/tmp/murmuration-w08/author-w08-3/m6/cwd`, `…/reproducer-w08-3/m6/B`): the folders were recreated empty, the plugin was uninstalled from each, and the empty folders were deleted again.
- `git worktree remove` on the 7 clean worktrees, and `git worktree remove --force` on the 6 dirty ones (their untracked `handbacks/`, `harness.jsonl`, the wave-8 logs and `08e_compact_run.py`, and the modified `user_words.md` in wave-9 and xenodochial-franklin were discarded, as Eliott chose). Branches kept.
- Deleted `~/.claude/plugins/cache/murmuration-w5` (14 MB) and `~/.claude/plugins/data/murmuration-inline` (628 KB).
- After: `installed_plugins.json` has `murmuration@murmuration-local` only for the main checkout (local scope), plus the scratch `murmuration@cracking-shells` project install. `data/murmuration-murmuration-local/bin/` still holds `murmuration` and `.verified` (14:59). The Consistency Check exits 0.
