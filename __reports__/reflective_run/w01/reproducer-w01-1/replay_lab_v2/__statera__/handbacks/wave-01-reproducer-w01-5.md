# Hand-backs of wave-01-reproducer-w01-5

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T12:00:11+09:00 | agent_id=a492a8c08e69c24bf type=murmuration:reproducer event=PostToolUse status=delivered bytes=4451 sha256=1265b992f7d4
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

verdict: ESCALATE on w01-c5. Reason: the author wants to change what the claim states, so the PI decides. As filed the head is OVERSTATED.

**What I reproduced with my own code** (`python3 -I` scripts in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5/`, applying the author's `--until 2026-10-19T02:24:30Z`):
- **The three stops.** 60 turns before each stop in b, c and d. Notice to resume was 7.7, 10.9 and 31.9 s. First-resumed-turn context was 301,857, 281,185 and 296,922 tokens, of which only 1,798, 1,256 and 1,853 (0.4 to 0.6 percent) were written to cache. Whole-run totals were 3.061, 2.916 and 3.065 USD. Exposure is context x 2.30 / 1e6 = 0.65 to 0.69 USD.
- **Warm/cold split.** 12 distinct resumes: warm at gaps up to 238.9 s (cache-write share 0.006 to 0.015), cold at 425.4 s and above (share 0.81 to 0.87). This matches `resume_vs_gap.csv`.
- **Turn-distribution cells.** The pooled Sonnet runs above 6 turns have n = 18, median 41, and 6 above 60. This run's explorers had 46 49 52 62 62 63 turns.
- **Result 5.** The first puzzle-file write came in the last 1 to 7 turns of every explorer, and there were six refused `report.md` writes.
- **Prices.** They match the `claude-api` skill's `shared/models.md` (Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, cache reads $0.20 each).
- **Cache-write multipliers.** The skill's `shared/cost-optimization.md` states them (1.25 for 5 minutes, 2 for 1 hour), so the claim's "assumption" label is wrong but harmless.
- **PI cost.** The 0.056 and 0.203 USD for b and c reproduce. For d the author counts only the reacting turn (0.139 USD) and rightly excludes the 02:17:28 dispatch turn, which started 22 s before the notice; that turn is why the notice sat unread for 25 of the 31.9 s.

**What did not reproduce, and the fix.**
- **Result 3.** The author's own full command printed this-run n 11, max 424.5 s, 1 over 300 s, against the committed n 9, max 29.0 s, 0. `--until` bounded the notices but not the reaction messages, so the head's "a re-run gives the same numbers" was false. The author fixed the script; my re-run now matches `run_log.txt` and the tables.
- **A second bug I found.** "0 of 42 worker notices" double counted, because the design session repeats the forked genesis notices. The distinct count is 32. The author agreed and fixed it; I re-ran and got this run 9, genesis 11, design 12, none above 300 s.

**Wording against the evidence.**
- The title states as MEASURED two things that are not. The "0.65 to 0.70 USD exposure" is an ESTIMATE (a formula on measured context). "Re-writes the context only when the gap passes the TTL" rests on 12 resumes, a split between 238.9 and 425.4 s, and a TTL inferred from a field name; "because" is causal on that inference.
- The "2 to 7 percent" of a run is a lower-bound ratio, because subagent output tokens are understated.
- The `maxTurns` values (75, 120, 80, 80) sit under a heading "Proposal (CONJECTURE ...)" and are not in the head sentence, so they are kept apart. The file carries a single MEASURED label.
- USD figures are presented as list-price estimates on recorded tokens, with subagent output understated. That is stated.
- The proposed values survive either reading of whether the limit restarts on resume (author-like single segments above 60 are 65, 75 and 89; explorer-like longest segment is 75; verifier-like maximum is 42). Whether the limit restarts is still untested.
- Turns of the genesis and design runs sum resumed segments.

**Exchange.** I asked four questions and then a fifth on the double count. The author wants the title restated (dropping the exposure, "only when", and "2 to 7 percent") and has not edited the head. That is why this is ESCALATE. The author then filed the restatement as a superseding claim, `__pondus__/w01-c8.md` ("0 of 32 worker notices"), which needs its own verdict. I did not review its other tables.

**Files.**
- Claim with my section appended: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c5.md`
- Puzzles (5): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-5.md`
- My scripts: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5/`
