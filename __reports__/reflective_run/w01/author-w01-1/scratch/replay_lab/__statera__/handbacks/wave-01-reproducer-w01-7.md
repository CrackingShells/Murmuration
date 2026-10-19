# Hand-backs of wave-01-reproducer-w01-7

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:46+09:00 | agent_id=a5efc74c3a545b66c type=murmuration:reproducer event=PostToolUse status=delivered bytes=4413 sha256=208576638804
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

w01-c7: verdict is OVERSTATED. The claim's numbers do not survive; its direction does. The 479-minute, 17-of-19 and +127-word statements are all right.

**What I checked**
- The quick and full commands reproduce the author's `c7_summary.txt` and `c7_asks_replay.csv` exactly.
- `git apply --check` passes on `c7-asking-habit.diff`. It touches only `skills/research-loop/references/working_defaults.md` (+127 words, 260 today) and leaves `agents/research-pi.md` alone, which fits the v5 rule "a skill pointer, never a longer PI file".
- The 479 minutes are the human's night: the transcript has no record between 16:25:28Z on 10-18 and the click at 00:24:46Z on 10-19, and 16:25Z is 01:25 JST. The agent's own work after the click was 55 s and 48 s.
- "17 of 19 asks with no subagent running" holds. I recomputed it from the subagent transcript timestamps (asks 0 and 15 are the exceptions).
- The cost arithmetic follows from the inputs, but the inputs were wrong (next section).

**What did not hold**
- `explorer-w01-d/prompts.csv` caps `human_text` at about 420 characters. 19 of the 55 research prompts are cut, and the settling sentence of ask 17 falls past the cut.
- The real user-words file is about 27,500 characters and 4,700 words, not 14,399 and 2,474. Reading it costs 6k to 10k tokens per pass and 117k to 193k over 19 asks, about twice what the head says.
- On full text the settling prompt of ask 17 shares "reflective" with the ask, so it ranks 4th of 55, not 47th. The false-positive maximum is 0.5, not 0.33. The ranks the head quoted sat inside blocks of tied zero-overlap prompts and meant nothing.
- The conclusion "read the last entries, do not search" is firmer after the correction: the settling overlap is 0.17 and non-settling prompts reach 0.5.

**My own call on all 19 asks**
- I agreed on 15 of 19.
- I disagreed on ask 2 (download): the PI had already looked on disk, and only the human knew about the LM Studio folder.
- I disagreed on ask 3 (workshop paper): the SHORTEN verdict was a guess about the PI.
- I disagreed on ask 5 (scheduler): the diff's own first paragraph still makes the PI ask.
- I disagreed on ask 13 (create repo, open roadmap): it is the same build gate the human declined at v1, v2 and v3.
- My totals were REMOVE 2 (asks 1, 17), SHORTEN 4 (10, 11, 13, 16), AT_RISK 2 (2, 14), KEEP 11. The head said 4, 4, 2 and 9.
- Ask 14 (start wave 1) is correctly AT_RISK, because the human's answer added a constraint no earlier word showed. Ask 0 is correctly KEEP.

**Exchange**
- I asked the author about the truncation, asks 13, 2, 5 and 3, and whether to state a range.
- The author withdrew the REMOVE verdicts on asks 2 and 13 and the SHORTEN on ask 3, and moved ask 5 to KEEP. It retracted "shares no content word" and recomputed the finder numbers and token costs on full text.
- I re-ran its corrected `c7_replay.py` in a copy; the output matched its new `c7_summary.txt` and CSV.
- The author's corrected counts match mine.
- It proposes restating the claim as 1 to 2 of 19 asks removed, 2 to 4 of 55 prompts removed, 4 shortened, 2 at risk, and the 479 minutes not recovered. This is proposed, not applied; the head's title and label are unchanged and a "CORRECTIONS AFTER THE EXCHANGE" block sits below them.
- I did not escalate: the author accepted the finding and contested nothing. The restatement has to be filed as a superseding claim and verified again; editing it in place does not replace that. The PI decides.

**Limits that remain**
- No run was ever made with the habit.
- Headless behaviour is UNVERIFIED, as the author says.
- The 6M token budget has no source.
- The diff adds a rule about when to ask, and v5 line 446 asks for a "when to decide what" test on every edit of PI prose. The author argues the existing ask-first rule makes it the same kind; I left that as an open puzzle.

**Files**
- Verdict section: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c7.md`
- Scripts and outputs: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-7/` (`timeline.py`, `wrapups.py`, `wrapups.txt`, `subs.py`, `finder.py`, `fulltext.py`)
- Puzzles (6): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-7.md`
