# First real project as a lab

**Goal**: One real project of Eliott's, chosen with him, runs as a Murmuration lab from `murmuration@cracking-shells` at project scope.
**Pre-conditions**:
- [x] `ship_update` done (0.1.1 installed from Nest)
- [x] The project chosen with Eliott, quoted here: "Context Sustainability" (the repo `~/Documents/explore/youzuoqi`, named in the CS-01 reminder)
**Success Gates**:
- ✅ [run] In the project, `.claude/settings.json` enables `murmuration@cracking-shells`, and `claude plugin list` there shows it at project scope
- ✅ [run] `claude plugin list` in a non-lab folder shows no `murmuration` entry enabled (entries from other projects appear as `✘ disabled`; corrected 2026-10-28 from "shows no entry", which cannot pass)
- ✅ [behavioral] `/lab <question>` creates the lab files; a new session opened with `claude --agent murmuration:research-pi` is the PI; a plain new session is not
- ⬜ [behavioral] A Desktop worktree of the project loads the plugin without a new install (or what it asks is recorded)
- ✅ [behavioral] A plain new session in the Murmuration repo, not a side session, is or is not the PI; the result is recorded against the plan's puzzle
**References**: plan "Decisions" 1 to 3; the `Murmuration` Reminders list

## Step 1: Install and open the lab
**Goal**: The scaffold in daily use.
**Implementation Logic**:
1. Choose the project with Eliott (his Reminders project lists). Install with `claude plugin install murmuration@cracking-shells --scope project` from its folder, and commit `.claude/settings.json` there only if Eliott says so.
2. Eliott runs `/lab <his question>`; check the files and the deny rules.
3. Open the PI as the README says; check that one guard deny fires there (fixture `a01` fed through Python to the installed binary).
4. Open a Desktop worktree of that repo and record whether the plugin loads.
5. Run the Consistency Check from the project folder.
6. Append log lines to the Reminders item through the scheduling-work writer.
**Deliverables**: this leaf's Results; the project's `.claude/settings.json` (in that project, on Eliott's word)
**Consistency Checks**: `claude plugin list 2>&1 | grep -q 'murmuration@cracking-shells'` (expected: PASS)
**Commit**: `docs(roadmap): record the first real project set up as a lab`

## Results (2026-10-28)
- Project: Eliott chose "Context Sustainability"; repo `~/Documents/explore/youzuoqi` (clean, `main` at b144c52).
- Install: `claude plugin install murmuration@cracking-shells --scope project` gave 0.1.1, project scope, enabled. On Eliott's "Commit both, no push": youzuoqi 17203b0 `infra(lab): enable murmuration at project scope` (`.claude/settings.json` and a `.gitignore` line for `.claude/settings.local.json`); the youzuoqi hook (`cz check`) passed; nothing pushed.
- `/lab`: `lab_init.py` from the 0.1.1 cache, run on Eliott's question, which he gave as "The CS-01 kickoff. But also indicate that to reduce running and testing costs, it should consult the skill `using-rivault` to leverage the models over there". It was recorded as: "Kick off: review round-00 reports, decide hypotheses, models and δ. To reduce running and testing costs, consult the skill `using-rivault` to leverage the models over there." Lab files created, colgrep index built (14 added), `settings.local.json` holds `permissions.deny` only (no `agent`), and git ignores it. The lab files (`__statera__/`, `__design__/`, `.ignore`) are left uncommitted.
- Sessions (headless, prompt fed through a file): plain `claude -p` answered "PI: no"; `claude -p --agent murmuration:research-pi` answered "PI: yes"; both listed the five `murmuration:` agents. None of the test prompts reached `user_words.md`.
- Guard in a live session (`--allowedTools Bash`, so only a hook can deny): a G3 probe on `.claude/settings.probe.json` was denied by Claude Code's own sensitive-file rule, which does not separate the two layers. Fixture b01 (G2, `--setting-sources project`) was denied by "permission_guard (G2): the child `claude` is started with `--setting-sources project`, …".
- Worktree: `git worktree add --detach` of youzuoqi (scratchpad, since removed): `claude plugin list` there shows `murmuration@cracking-shells` at project scope, enabled, with no install; a session there lists the five agents. This is a plain git worktree, which is what the Desktop app creates, but it was not opened through the app, so the Desktop gate stays open until Eliott opens one.
- Non-lab folder: `murmuration@cracking-shells` and `murmuration@murmuration-local` both show `✘ disabled`.
- Murmuration repo puzzle: settled earlier (see `publish.md`): a plain `claude -p` in the repo is not the PI.
- Consistency Check from youzuoqi: PASS.
- Scratch cleanup: the `nest-test` project install was uninstalled; `data/murmuration-cracking-shells` is kept (youzuoqi uses it). The installs left are the dev copy (local, Murmuration main checkout) and youzuoqi (project). Observed, not acted on: the dev copy's record points at a stale cache `cache/murmuration-local/murmuration/0.1.0` (10-19, 9eb759b, the old root layout), but sessions load skills from the working tree, so that cache is unused; the orphaned `cache/cracking-shells/murmuration/0.1.0/` is left for Claude Code to clean up.
- Open: `user_words.py` keeps a headless prompt only when `entrypoint` is `sdk-cli`, and none of four headless prompts here was recorded. Whether a person's own `claude -p` in a lab is recorded was not tested.
