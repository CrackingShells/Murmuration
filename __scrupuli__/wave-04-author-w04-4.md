## S-w04-author-w04-4-1
The floor of the timer moves with the way it starts a process. `sh -c :` through `subprocess.Popen` cost 67.6 ms (CPU 8 ms) in the first full run, and was slower than `python3 -S -I -c pass` (58 ms); with `os.posix_spawn` the same `:` is 30.4 ms (CPU 3.3 ms). So about 30 ms of every wall figure in the popen runs is the timer forking a large Python, and the ratios new/old are pulled towards 1 by it. Which of the two is the better stand-in for how Claude Code (Node) starts a hook is not known: the platform's own spawn cost was not measured, and it sits in front of every figure here.
refs: __reports__/reflective_run/w04/author-w04-4/derived/timing_popen_n40.jsonl (cases `floor:*`), derived/timing_final_posix_n60.jsonl

## S-w04-author-w04-4-2
Wall ratios of the long worker ran from 0.47 to 0.78 over six runs of the same code (quick run at n = 8 under load average 8: 0.69 and 0.78) while the CPU ratio stayed at 0.21 to 0.22. The pre-registered rule is on wall time, and wall time here is mostly the load other agents put on the machine (load average 5 to 15 during my runs, from their headless runs). A decision rule on wall time on a shared machine has an error bar that is as wide as the threshold; E4 would have been better stated on CPU time, or on wall time at a stated load.
refs: derived/timing_final_bootstrap.md, derived/timing_posix_n40_load15.jsonl, derived/timing_popen_n40.jsonl, /private/tmp/murmuration-w04/author-w04-4/quick_cmd.jsonl (not kept)

## S-w04-author-w04-4-3
`PYTHONDONTWRITEBYTECODE=1` is in the environment of this Desktop session, so every hook process inherits it: no import of `handback` is ever cached, and `python3 -I` (which I now use) ignores it, so my version writes `scripts/__pycache__` in the plugin folder that the user's variable says not to write. I did not find where the variable is set (shell profile or app). Whether to honour it (and pay about 6 ms of CPU per start) is a choice for the user, not a measurement.
refs: `env | grep PYTHON` in the session; scripts/__pycache__ after the first run of the lean version

## S-w04-author-w04-4-4
`python3 -c pass` costs 23 ms of CPU and `python3 -S -I -c pass` 11.4 ms on this machine: `site` alone is 11.6 ms, 8.7 of it an `__editable___hatchling_0_4_2_finder` that imports `pathlib`, `urllib.parse`, `ipaddress`. A development install in the user's conda base makes every Python start (hooks included) slower on this machine than on any other; the `-S` flag removes it, but the same leak slows every other Python the user starts. Not an issue of the plugin; it inflates the old figures here and not on a clean machine.
refs: `python3 -X importtime -c "import sys; sys.path.insert(0,'scripts'); import budget"` on 41c75ea (site 11578 us)

## S-w04-author-w04-4-5
The 5.56 MB and 4.86 MB wave-3 worker transcripts are mostly `api-request-blob` and `api-request` records (151 of 949 records; the blobs are the request bodies). Our scan reads every line that contains `usage`, `user` or `origin` and these blobs contain all three, which is where the old 31 ms of CPU on the long transcript went. I did not find what turns on these records (a debug variable of the headless runs, or the 2.1.302 build); a transcript of an ordinary Desktop worker (2.6 MB, 44 workers of the design session) has none. If they are an artifact of how the e-runs were made, the "long transcript" of E4 is an unusual one and the saving from reading only the new bytes is larger there than in a real long run.
refs: ~/.claude/projects/-private-tmp-reproducer-w03-1-s2-runs-r1-lab/e08e7434-4338-497d-b7c1-339f5856ef4e/subagents/agent-a50b3982ac2a64503.jsonl (record types: attachment 323, assistant 166, user 157, api-request-blob 151, api-request 151)

## S-w04-author-w04-4-6
The brief says the wave-3 transcripts are under `~/.claude/projects/` for the worktree and for the main checkout; the folder of the main checkout (`-Users-hacker-Documents-src-CrackingShells-Murmuration`) holds only `memory/`. All 44 workers and the main thread are under the worktree folder; the largest worker transcript there is 2.6 MB, so no real worker of the design session reaches the 5 MB of E4's class (c). I used the 5.56 MB headless-run worker of wave 3 and say so.
refs: ls ~/.claude/projects/-Users-hacker-Documents-src-CrackingShells-Murmuration; derived/counts_session_ab96c5ed.json (`bytes` per worker)

## S-w04-author-w04-4-7
UserPromptSubmit fires for queued background-task notifications too (the recorded run has 2 UserPromptSubmit payloads for 1 typed prompt); the transcript shows the notification as a `queue-operation` record, not a `user` one. My count of `user_words.py` starts from transcripts is therefore a lower bound. Also: PostToolUse fires for `Agent` and `SubagentHandback` calls (budget.py starts for them and acts for none).
refs: derived/recorded_payloads_rec1.jsonl (labels `UserPromptSubmit||user_words.py`, second line), `hook_count_invocations.py` docstring

## S-w04-author-w04-4-8
The first replay run showed 11 "differences" in hand-back files. They were the path of the transcript written into a `status=missing` section (the replay's folder was named `old` or `new`). Nothing in the hook was wrong, but it shows a hand-back file carries an absolute path of the agent's transcript: the file is then not reproducible between machines, and a replayed or copied lab keeps the old path.
refs: derived/replay_equivalence_291.txt (final, equal); the first run's output was /private/tmp/murmuration-w04/author-w04-4/replay_all.txt (not kept)

## S-w04-author-w04-4-9
`__reports__/reflective_run/w03/author-w03-1/mutants.py` (29 mutants of the old `scripts/budget.py`) works by editing that file's text; after the split into `budget.py` and `budget_core.py` its targets are in another file. I did not re-run it. It was part of the wave-3 evidence for the budget hook; the equivalent for the lean version is the random-transcript check in `budget_selftest.py` (check 2b) and two mutants I tried by hand, which that check catches.
refs: __reports__/reflective_run/w03/author-w03-1/mutants.py; scripts/budget_selftest.py

## S-w04-author-w04-4-10
One idea that would halve the starts per tool call and that I did not build because it changes what the hook sends: PostToolUse acts only from 1.5 of the budget (once per worker, if ever), yet pays a start at every tool call. If the ceiling were decided at PostToolBatch from the previous request's spend, the PostToolUse registration could go; the block would then arrive one request later. How often a worker passes 1.5 at all: the 291 replayed runs hold 14 `stop` and 11 `halt` lines, in a minority of runs. A claim of its own would need to show that a block one request late loses nothing.
refs: derived/replay_equivalence_291.txt (log event counts); scripts/budget_core.py `handle_locked`
