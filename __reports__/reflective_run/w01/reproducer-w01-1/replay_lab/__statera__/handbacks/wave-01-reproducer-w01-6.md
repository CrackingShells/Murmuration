# Hand-backs of wave-01-reproducer-w01-6

Final messages, verbatim, appended by the lab's hook. Read it; never edit it.

## hand-back 1 | 2026-10-19T11:48:52+09:00 | agent_id=af203d6362eab4e3f type=murmuration:reproducer event=PostToolUse bytes=3848 sha256=8958afac659d

verdict: OVERSTATED
reason: The mechanics, counts and cost arithmetic reproduce and the diff applies cleanly. But the claim as filed ("6 of 55", "1 clearly", "and no more", 190 words) says more than the replay shows. My re-rating gives at most 3 prompts at a wave close (5 if the voice sentence applies to every message) and none clearly. The author accepts this.

My section is appended to `__pondus__/w01-c6.md` under `## verdict: reproducer-w01-6`, with the exchange logged. My puzzles are in `__scrupuli__/wave-01-reproducer-w01-6.md` (5 puzzles). Scripts are in `__reports__/reflective_run/w01/reproducer-w01-6/`. Plugin files are untouched, nothing was applied or committed, and the transcripts were read only.

**Independent result**
- **Quick command and counts.** `c6_replay.py --quick` reproduces N 49 / P 5 / Y 1. I recounted the quote-reply numbers from `prompts.csv` with my own code: 55 prompts, 12 start with ">", 13 contain a quote, and 6 and 7 of the 9 corrections. All match.
- **Re-rating (seed 6).** I rated 14 prompts: all 6 pre-empted ones plus 8 random from the 49 N. I read each human prompt and the PI message it reacted to. Agreement with the author was 12/14 (86%), or 11/14 if the conditional case counts as a miss. I had read the author's table first, so this is not blind; I say so in the file.
  - d10ebf86: author Y, me P. The human reacted to the report file `00-findings_v0.md`, not to a chat message. The diff regulates the chat close and the wave note, not report files or claim heads.
  - 3959fc84: author P, me N. A scope sentence would reveal the missing shotgun read, not prevent the complaint.
  - 8af30fe6: P only if the research-pi.md voice sentence applies to every message. The message it reacted to was a mid-wave reply, not a close.
  - All 8 random N prompts agreed. That is a small sample (95% upper bound on misses about 31%).
- **Close vs reply.** Only about 3 of the 6 reacted-to messages are wave-close or hand-back messages. The claim's scope sentence covers closes only.
- **Factual statements.**
  - `prompts.csv` truncates `human_text` near 420 characters for 18–19 of 55 prompts, and the author's regexes ran on the truncated text. On the full transcript text, 6 prompts name a cost word (not 4). "Never tokens" and "0 plugin labels" still hold.
  - "Waiting for your approval" appears 7 times, not 6.
  - The headline "0 of 12 plugin files contain hypothes" is really 0 of 19 tracked files.
  - The headless probe used `--strict-mcp-config` with no servers, so the missing `mcp__ccd_*` tools followed from the flag.
- **Cost.** The diff adds 111 + 37 + 42 = 190 words. The token and percentage arithmetic is consistent. It ignores the cost of writing longer messages in place of shorter ones.
- **Design rule.** The first clause of the research-pi.md sentence (voice) passes. The second clause ("question first, then findings, then what you need") is an ordered procedure that duplicates `waves.md` step 4, so I asked for it to be dropped.

**Exchange**
- The author accepted all five corrections and dropped the second clause of the research-pi.md sentence.
- It re-rated d10ebf86 to P and 3959fc84 to N, and re-ran the counts on full text.
- It re-ran the headless probe with default MCP: 132 tools, 99 of them MCP, no `mcp__ccd_*`, no AskUserQuestion. I checked this file myself. A Desktop-spawned background session stays unverified.
- `c6-contract.diff` is now +168 words (111 / 37 / 20 by my own count), and `git apply --check` passes.
- The author's head still carries the old title and numbers, plus a "CORRECTIONS AFTER THE EXCHANGE" block. The proposed restatement is "3 of 55 at wave close, 5 under the broad reading, none clearly".
- I did not escalate: the exchange converged on my findings. The author should file the restated claim at CONJECTURE with `supersedes: w01-c6`.
