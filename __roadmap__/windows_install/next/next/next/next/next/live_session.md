# Windows install and session from Nest

**Goal**: 0.3.0 installs from Nest on a real Windows machine and a lab session runs its budget and hand-back hooks from `murmuration.exe`; the docs drop "CI only".
**Pre-conditions**:
- [ ] `release` done (0.3.0 on Nest)
- [ ] A Windows machine (reminder `murmuration-win-live`)
**Success Gates**:
- ⬜ [behavioral] `claude plugin install murmuration@cracking-shells` from Nest on Windows: SessionStart installs `murmuration.exe` and `murmuration.exe.verified` in the data dir, no launcher note
- ⬜ [behavioral] `/lab` works; in one lab wave, `budget` and `handback` run from the binary (rows in `harness.jsonl`, hand-back saved under `__statera__/handbacks/`)
- ⬜ [behavioral] What a user sees without a real `python3` (python.org-only install, Store stub) matches the README's Requirements text
- ⬜ The cached plugin checkout's line endings and `.gitattributes` handling checked (`core.autocrlf` true on that machine)
- ⬜ Banner and description flipped to "Windows supported" (ships with the next release-type commit)
**References**: reminder `murmuration-win-live`; `release.md` results; `install.md` Step 3 Requirements text

## Step 1: Install, session, observe
**Goal**: See on a real machine what CI could not show.
**Implementation Logic**:
Install from Nest at project scope in a scratch folder; start a session; run `/lab` and one wave; read the data dir, `harness.jsonl`, and the hook output. Repeat once with `python3` removed from PATH to check the README's failure text. Record everything in this leaf.
**Deliverables**: results in this leaf's Progress row; `README.md`, `plugins/murmuration/README.md`, `plugins/murmuration/.claude-plugin/plugin.json` (`description`)
**Consistency Checks**: `python3 -I -c "import json,sys; d=json.load(open('plugins/murmuration/.claude-plugin/plugin.json',encoding='utf-8')); sys.exit(0 if 'CI only' not in d['description'] else 1)"` (expected: PASS)
**Commit**: `docs(readme): Windows observed in a live session`
