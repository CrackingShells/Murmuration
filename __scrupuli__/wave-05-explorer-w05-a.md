## S-w05-explorer-w05-a-1
Two chains ended 5.4 min apart (C12 at 10:53:38, C5 at 10:48:13) and the third 12 min earlier, all starting at the same dispatch. The PI sized each author's budget and time box (T 60, 60, 60 min at the start), and author-w04-4 ended at 90% of its 60-min box while author-w04-2 and author-w04-3 sat at 82% and 55%. Either the chains are balanced because the box sets the length (authors expand to fill it), or by chance. I could not tell from one wave; the harness `t_frac` at each end is the only evidence.
refs: `__reports__/wave-05/explorer-w05-a/chain_ends.txt`; `murmuration-wave-4-3417be/__statera__/harness.jsonl` (end events of author-w04-2/3/4)

## S-w05-explorer-w05-a-2
Author-w04-2's cells never ran more than 9 at once and no stage had more than 9 cells, including a 12-cell experiment split 9 + 3. Nobody wrote down why 9. The only nearby evidence is "Not logged in" on 4 of 12 parallel launches in author-w04-3's runs. If 9 is a real ceiling the lab's headless experiments are batch-bound; if it is a habit, one stage per experiment is 4 to 10 min of that chain. The launch scripts are trashed with the run folders; only `meta.json` survived.
refs: `__reports__/wave-05/explorer-w05-a/headless_cells.tsv` (author-w04-2 rows); `__scrupuli__/wave-04-author-w04-3.md` (puzzles 7 and 12)

## S-w05-explorer-w05-a-3
The PI trashed the wave-4 raw runs at 10:54 as account-identifier hygiene, yet the wave's timing record (cell start and end, per-request model time of headless workers) lives only in those folders. I read only `meta.json` from the Trash. The headless workers' own transcripts (`~/.claude/projects/*-runs-*-lab/`) were not read; they would split API latency from tool time inside each 5-min cell. What is the lab's rule for keeping timing without keeping identifiers?
refs: `~/.Trash/murmuration-w04-raw-runs-2026-10-20/author-w04-2/runs/*/meta.json`; `__statera__/wave-04.md` Notes (spend at close)

## S-w05-explorer-w05-a-4
A queued message waits for the recipient's next tool round, and a recipient inside a 5 to 9 min blocking `until` loop (author-w04-2, 10:26:52 to 10:32:35) cannot read it; the reproducers asked at 10:28:02 and 10:28:32 and polled `tail -f /dev/null` in growing chunks (50, 90, 120, 150 s), reading the answer 98 to 151 s after it arrived. The same tool is documented elsewhere in this lab as unreliable for waiting (`sleep` blocked, Monitor used once). Off the critical path this time. Would it be on the critical path if a verifier's exchange were the last step of a wave (reproducer-w04-8's second exchange was 24 s, so not tested)?
refs: `python3 -I __instrumenta__/wave_worker_events.py` on agent-a525c6e495f3b557f.jsonl (reproducer-w04-3) and agent-a6cf7547d02f40c00.jsonl (reproducer-w04-2), from 10:28:00

## S-w05-explorer-w05-a-5
At 10:54:56 author-w04-4 was resumed for 4 s, after the PI killed a leftover `until ... sleep` loop by PID, and its final `end` event (10:55:00) is the latest in the harness log. A naive "wave end = last harness end" puts C5 at 80.2 min and the critical chain on the wrong author. A stray background job in a worker made the harness log lie about which chain was last. Is that resume counted in the spend and the dispatch tables?
refs: `murmuration-wave-4-3417be/__statera__/harness.jsonl` lines for 10:45:38 to 10:55:00 (author-w04-4); `__reports__/wave-05/explorer-w05-a/pi_events.txt` at 10:54:38 to 10:55:00

## S-w05-explorer-w05-a-6
The 4.1 min of PI probing before the first dispatch was item 1 (where the hook's lab root comes from). Its answer ended up as CONJECTURE ("strongly supported; not dumped") and the probes (hook in settings, probe subagent) did not work, since the running session did not pick them up. Seven minutes before the first dispatch bought a measured negative. Was that the right trade for the lab, or would a time box ("probe for 2 min, then dispatch") have kept the answer and saved 2 min?
refs: `__reports__/wave-05/explorer-w05-a/pi_events.txt` 09:28:30 to 09:32:34; `__statera__/wave-04.md` Item 1 section
