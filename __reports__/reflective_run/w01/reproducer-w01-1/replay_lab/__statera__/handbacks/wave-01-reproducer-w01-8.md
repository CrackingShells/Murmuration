# Hand-backs of wave-01-reproducer-w01-8

Final messages, verbatim, appended by the lab's hook. Read it; never edit it.

## hand-back 1 | 2026-10-19T11:48:51+09:00 | agent_id=a1fc18c8a5d480043 type=murmuration:reproducer event=PostToolUse bytes=4053 sha256=ff9b0e4896f4

reproducer-w01-8 on w01-c8: verdict ESCALATE (PI decides). The substance reproduces. The approved title does not: "0 of 32" is the wrong count and "exactly when the gap was 425 seconds or longer" reads as a threshold. The author may not change the title and asked me to escalate its restatement.

verdict: ESCALATE
reason: The substance reproduces, but the PI-approved title carries a wrong count (0 of 32; the count is 38), a 425 s figure that is not a threshold, and a 5-minute window stated as fact. The author may not change the title and has put a proposed restatement in the claim head, so the PI decides.

**What I did.** I wrote my own `python3 -I` scripts, without importing the author's code, in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-8/`:
- `latency.py` counts the PI-reaction notices.
- `resume.py` computes the warm/cold split.

I also ran the author's full command into scratch to compare tables. I did not run the quick command separately, and I did not read w01-c5.

**(1) PI-reaction latency (worker notices only, up to the `--until` snapshot).**
- I get 9 / 14 / 15 (38 in total), not 9 / 11 / 22 (42). None of them is over 300 s.
- The 22 and 42 came from an old script version that counted genesis notices a second time under design (forked history). The 32 came from a de-duplication key that dropped a resumed agent's second finish.
- In 3ccc the one wait of 584.5 s is a notice copied from genesis, so 3ccc is a fork, not "unrelated".
- The author confirmed all of this and now stands behind 38 (9 / 14 / 15). The claim body carries it.

| session | worker notices | over 300 s |
|:--|--:|--:|
| this run | 9 | 0 |
| genesis | 14 | 0 |
| design (own notices only) | 15 | 0 |
| `3ccc590f` (own notices only) | 2 | 0 |

**(2) Warm/cold split.**
- Inside the snapshot I find the same 12 resumes, with the same gaps, context sizes and cache writes.
- The 5 with gap ≥ 425.4 s have a cache-write share of 0.81 to 0.87; the 7 below have 0.004 to 0.015.
- I checked more than the 4 required: b, c, d, genesis a04ebecba, design aff153770 and all five cold ones. The 60 turns before each stop also reproduce.
- After the snapshot there are 5 more resumes in this run. Two are cold at gaps of 284.9 s and 319.7 s, and one is warm at 282.0 s. So 425 s is only the shortest cold gap of the 12, not a threshold.
- That boundary sits just under 300 s, which fits a 5-minute TTL. The TTL itself is still a CONJECTURE.
- The author's `later/resume_vs_gap.csv` (17 resumes) matches mine.

**(3) Labels and arithmetic.**
- The USD exposure rows (0.694 / 0.647 / 0.683) reproduce as context × 2.30 / 1e6 and are labelled ESTIMATE. The per-role limits (75 / 120 / 80 / 80) are labelled CONJECTURE.
- The "95% upper bound" on 0 of n is the rule of three, 3/n. The exact one-sided bound is 1 − 0.05^(1/n). They give 7.1% and 6.9% at n=42, 7.9% and 7.6% at n=38, and 9.4% and 9.0% at n=32. Both treat notices as independent draws from one PI, which is untested.
- The title states the "5-minute subagent cache window" as fact while the body labels the TTL CONJECTURE. The author agreed the title must carry the label.

**Exchange and proposed title.** The author accepted all four points. In the claim head it added a "Restatement pending" paragraph with a proposed title:
- 17 resumes, re-written in all 7 with a gap of 284.9 s or more and in none of the 10 with 282.0 s or less.
- The window marked as probably 5 minutes, CONJECTURE.
- 0 of 38 distinct worker notices over 300 s.

**Files** (all under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`):
- `__pondus__/w01-c8.md` — my verdict section is appended at line 128; the verdict line is at line 165.
- `__scrupuli__/wave-01-reproducer-w01-8.md` — 4 puzzles: quoted tables drifting from code, fork de-duplication, TTL bracketing, notice kind detection.
- `__reports__/reflective_run/w01/reproducer-w01-8/latency.py` and `resume.py`.
