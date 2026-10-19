## S-w01-reproducer-w01-5-1
The head of w01-c5 promises that `--until` makes a later re-run give the same numbers. It did not hold for `pi_reaction_latency.csv`: `--until` bounded the notices but not the reaction messages, so the this-run row changed from n 9 to n 11 once the PI's next message (02:27:54) existed. The author fixed it after my question. Which other joins in `turns_profile.py` and in explorer-w01-a's helpers (`scan`, ownership of a message id across files) have the same one-sided cut, and could change when the transcripts grow? A test that runs each script once now and once an hour later and diffs the tables would catch it.
refs: __reports__/reflective_run/w01/author-w01-5/turns_profile.py, __reports__/reflective_run/w01/author-w01-5/run_log.txt

## S-w01-reproducer-w01-5-2
The genesis and design sessions share forked history, so the same worker notice (same task id and timestamp) appears in both groups of `pi_reaction_latency.csv`: 11 genesis notices are a subset of the 22 design ones. "0 of 42 worker notices" counts them twice; the distinct number is 32. The same overlap may affect other pooled counts (the 18 pooled Sonnet runs seem safe, since I got the same 18 with ownership by earliest file). Does the wave have one agreed way to de-duplicate across the two sessions, or does each analysis redo it?
refs: __reports__/reflective_run/w01/author-w01-5/pi_reaction_latency.csv, __reports__/reflective_run/w01/reproducer-w01-5/my_dist.py

## S-w01-reproducer-w01-5-3
Where the stranding comes from. For explorer-w01-d, 25 of the 31.9 s between the notice and the resume were the PI finishing a dispatch turn that began 22 s before the notice. The PI cannot react to a notice mid-turn, so the stranding time is a lower bound on how long a notice waits when the PI runs long turns (five parallel `Agent` calls with long prompts took 45 s). In an autonomous run with a busy PI the tail may be longer than the 9 notices show. Is the delay a property of turn length rather than of PI attention? The claim does not separate them.
refs: ab96c5ed transcript 02:16:43 to 02:17:37, __reports__/reflective_run/w01/reproducer-w01-5/my_pi.py

## S-w01-reproducer-w01-5-4
The 5-minute TTL is inferred from `ephemeral_5m` and a gap between 238.9 s and 425.4 s, with all five cold resumes from the interactive genesis and design sessions and no cold resume in this run. Is there a way to bracket it tighter from existing transcripts, for example resumes of the PI's own main thread (1-hour writes) or other subagents with gaps between 240 and 420 s? If none exist, one deliberate resume at about 330 s on a throwaway agent would close it for a few cents. Nothing in the claim depends on that, but the title does say "5-minute".
refs: __reports__/reflective_run/w01/author-w01-5/resume_vs_gap.csv, __reports__/reflective_run/w01/reproducer-w01-5/my_gap.py

## S-w01-reproducer-w01-5-5
The skill file cited for the cache-write multipliers does state them (1.25 for 5 minutes, 2 for 1 hour, in `claude-api` `shared/cost-optimization.md`), while the claim calls them an assumption "not in that table". Small, but it suggests the author did not open the second file, and the cache-read rate of $0.20 for Opus 5.5 (which looks low next to $4 input, yet is what the skill's model table says) is worth one line of explanation wherever USD per PI turn is quoted.
refs: /Users/hacker/.claude/plugins/marketplaces/anthropic-agent-skills/skills/claude-api/shared/cost-optimization.md line 25, shared/models.md line 79
