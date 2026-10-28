# Ship 0.1.1 and check the update path

**Goal**: 0.1.1 is on `main` with `doubt()` None, and an install of 0.1.0 from `cracking-shells` updates to it with the user's two commands.
**Pre-conditions**:
- [ ] `lab_pi_choice` and `readme_install` merged into `main`
- [ ] A scratch install of `murmuration@cracking-shells` 0.1.0 exists (publish step 3)
- [ ] Eliott's go-ahead #4 (push `main`), quoted here
**Success Gates**:
- ⬜ [run] `plugin.json` says `0.1.1` on `origin/main`, and `doubt()` returns None on that commit
- ⬜ [run] After `claude plugin marketplace update cracking-shells` and `claude plugin update murmuration@cracking-shells --scope project` in the scratch folder, `cache/cracking-shells/murmuration/0.1.1/` exists, and after one session start `data/murmuration-cracking-shells/bin/.verified` is present with a Mach-O binary
- ⬜ [run] `lab_init.py` from the 0.1.1 cache writes no `agent` key in a fresh scratch folder
**References**: campaign README Gotchas (version bump rule); `plugins/murmuration/scripts/install_binary.py` (`doubt`)

## Step 1: Bump, push, update
**Goal**: The update path a user follows, checked once.
**Implementation Logic**:
1. On `main` after the merges, run `doubt()` (expected None: `lab_init.py`, `SKILL.md` and the README are not hashed sources). Bump `plugins/murmuration/.claude-plugin/plugin.json` to `0.1.1`.
2. Ask go-ahead #4; `env -u GH_TOKEN -u GITHUB_TOKEN git push origin main`. If the workflow runs (the paths filter sees `scripts/**`), wait with a background `gh run watch`; any `build(bin)` it commits must leave `doubt()` None.
3. In the scratch folder, run the two update commands, then one session start; check the cache and data dir.
**Deliverables**: `plugins/murmuration/.claude-plugin/plugin.json` (`version`)
**Consistency Checks**: `python3 -I -c 'import json;print(json.load(open("plugins/murmuration/.claude-plugin/plugin.json"))["version"])' | grep -qx 0.1.1` (expected: PASS)
**Commit**: `build(release): 0.1.1, /lab no longer sets the agent`
