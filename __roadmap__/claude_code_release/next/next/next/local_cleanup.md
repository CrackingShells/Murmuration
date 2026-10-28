# Local installs and worktrees cleanup

**Goal**: Only the main checkout keeps `murmuration@murmuration-local`; the stale installs, worktrees, cache and data dirs that Eliott names are gone.
**Pre-conditions**:
- [ ] The cleanup list shown to Eliott, with each worktree's uncommitted files
- [ ] Eliott's word on each item, quoted in this leaf
**Success Gates**:
- ⬜ [run] `installed_plugins.json` lists no `murmuration@murmuration-local` entry whose `projectPath` does not exist
- ⬜ [run] Every worktree Eliott named is gone from `git worktree list`, and its local install is gone too
- ⬜ [run] The main checkout's install and `~/.claude/plugins/data/murmuration-murmuration-local/bin/.verified` are still there
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
