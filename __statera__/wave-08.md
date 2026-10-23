# Wave 08

opened: 2026-10-24

## The user's sentence this wave serves

From `__statera__/user_words.md` (2026-10-24 00:11):

> You can proceed with wave 8 following the results of wave 7 and all other puzzles. The
> overarching goal is to progressively optimize murmuration by using it yourself. You are
> Murmuration and you optimize murmuration. Budget is 150USD; it is currently midnight, you have 6
> hours. Use them.

And the post-close questions of 2026-10-22 (07:53, 08:04, 08:08), which this wave takes up:

> I suppose a parallel question is whether it would become worth it for us to optimize our
> scripts' outputs, then.

> This is almost a textbook example that could be turned into a probabilistic modeling work for
> the sake of deriving choices about when it becomes worth it.

> isn't that exactly an aspect that colgrep is supposed to help us fight against? I note that
> agents often refuse to trust the semantic search and prefer to full read [...]

> Both definitely needs investigating.

Budget: USD 150 and 6 hours (00:11–06:11 JST). Spend baseline at opening: TOTAL USD 373.40 at
least, this checkout 1.30 at least [source: `scripts/lab_status.py --spend`, 00:14].

## What does not add up

- **The lab's largest spender is the PI, and seven waves optimized the workers.** The PI's main
  threads are USD 142.97 of the 309.75 priced per agent, 46% [source: `scripts/lab_status.py
  --spend` agent rows, 00:14; list price]. The PI runs on Opus and re-reads its whole context on
  every request. Item 29 (orientation is 21–32% of PI spend) is the only look at it. This session's
  request 0 was 50,221 tokens and its context reached about 99k before the first dispatch [source:
  this session's transcript, `jq` on `.message.usage`].
- **The lab has a search tool and reads whole documents.** 18 colgrep calls against 343 Read, `cat`
  and `sed` calls in waves 4–6; reading documents made most of the costliest re-read results (items
  38 and 41). Nobody knows whether colgrep answers the lab's own questions well.
- **Whether script output is worth shortening was read off 60 results.** That first look (2% from
  lab scripts) covered workers only and the costliest results only.
- **Cost choices are rules of thumb.** The 1-hour cache for authors was a break-even read from
  medians; the user asks for a decision model with uncertainty (item 40).
- **The hook a worker waits on after every tool call is still Python** (`budget`, 41 ms in exec
  form; item 36), next to a Rust guard that is now live.
- **This is the first Desktop wave on a main with wave 7's landings** (item 37): the installer,
  typed-prompt origin, authors' 1-hour writes. The wave itself is the check.

A rule I apply to myself this wave (item 38's lever the PI controls): briefs name the files and
sections a worker needs and do not ask it to read this note.

## Reassessments

**00:45, explorers c, a, d back.**
- Script output is not the lever: 3.7% of workers' context USD in waves 4–7; a 2,500-token cap
  saves at most 0.5%. Documents are 14.3%; the worker's own earlier turns 41.6% (thinking 22.5%,
  inferred from context growth); cost follows request count [source:
  `__reports__/wave-08/explorer-w08-a/00-findings_v0.md`, ESTIMATE/MEASURED as labelled there].
  rtk's commands hold 2.9% without `cat`, 11.7% with it; the `cat` part is what verifiers read.
  This answers the user's 07:53 question: no.
- The wave-note worry of item 38 does not show in waves 4–7 (0.9%). Dropped as a lever.
- The PI: 56% of its spend is cache reads; compaction past 200–300k tokens is the largest lever
  (USD 35–46 of 144, one real compaction to calibrate); hand-backs capped at 1–3k characters
  USD 6–10; wakes by worker messages 31.7% of PI spend, 82 with no tool call; a 5-minute cache
  would have cost the PI about USD 119 more [source: explorer-w08-d's report, ESTIMATE].
- The cache lifetime: on timed lives (waves 5–7) 1 hour is worth −0.02 ± 0.39 USD per author
  life, a knife-edge; w07-c7's +0.87 rested on untimed wave-4 pauses and a misaligned `tool_s`
  (S-w08-explorer-w08-c-1). All author and reproducer misses follow a hand-back wait set by the
  resumer. The PI keeps 1 hour under every rule [source: explorer-w08-c's report, ESTIMATE].
  I keep authors on 1 hour (minimax regret, and no measured loss); no claim.
- What changes: round 2 goes to the PI's side and to thinking. author-w08-2 (w08-c2, short
  hand-backs, net of the PI reading the report instead), explorer-w08-e (what compaction the
  platform allows and keeps), explorer-w08-f (are thinking blocks billed again; is `effort` a
  lever). Briefs from now ask for a hand-back of at most about 1,500 characters.

**01:05, explorer-w08-b back.**
- colgrep cuts markdown into one unit per file whose snippet is the first lines, and `expand`
  returns the whole file (200 lines by default): for the lab's notes and claims a hit is a path,
  not evidence, so opening the file is the correct reading of what a hit tells. No worker wrote a
  reason; thinking blocks are empty in all 68 transcripts. 65% of whole reads (152 of 175 for
  markdown) are of files the brief names; the unnamed ones are mostly scripts, where colgrep's
  function units save 94% on the one scored case. A search with no `paths` resolves to the main
  checkout, stale by 3 days, so a worker in a worktree cannot find this session's files [source:
  `__reports__/wave-08/explorer-w08-b/00-findings_v0.md`, MEASURED/CONJECTURE as labelled there].
- So the user's "agents refuse to trust the semantic search" reads, on this evidence, as the tool
  giving nothing better for markdown, plus briefs that name whole files. The levers: the PI's
  briefs (mine, applied from wave 8: name sections, not files); a section-level markdown unit in
  colgrep (the user's colgrep-mcp repository, not this plugin); an absolute lab root in the
  search hint workers get at start. Documents are 14.3% of worker context USD, with a by-section
  ceiling of 6.9% (explorer-w08-a), so this is a small lever and I do not open a claim yet.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w08-a | explorer | workers' context USD by source over waves 4–7: are lab scripts' outputs worth shortening; rtk's coverage (item 38, 39) | |
| explorer-w08-d | explorer | the PI's own spend by source and habit, with levers (item 29; 46% of priced spend) | |
| explorer-w08-b | explorer | does colgrep answer the lab's own questions, and why workers full-read (item 41, 11) | |
| explorer-w08-c | explorer | literature and a decision model for the cache lifetime and one more premium-vs-payoff choice (item 40) | |
| author-w08-2 | author | w08-c2: a once-only check that sends back an over-long hand-back, net of the PI reading the report | |
| explorer-w08-e | explorer | what compaction the platform allows, costs and keeps; the PI lever recomputed | |
| explorer-w08-f | explorer | are earlier thinking blocks billed again; `effort` frontmatter as a lever on a fixed task | |
| author-w08-1 | author | w08-c1: `budget` and `handback` as subcommands of the Rust binary, replay-equal, with fallback (item 36) | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- 00:16, five same-second dispatches: names right in every `start` line (item 6's swap did not
  recur); the four explorers' start lines say `B 3.0, T 20.0, source unknown`, because their
  briefs' budgets differed and `budget.py` will not guess which pending record is whose; the
  brief's own lines replace them at the first check (`scripts/budget.py`, `handle_locked`,
  `brief_read`) [source: `__statera__/harness.jsonl` lines 1–5]. By design, not a defect.
- PI request 0 this session: 50,221 tokens, all written to the 1-hour cache (item 20/37's range was
  31–49k) [source: this session's transcript, first assistant record's `usage`].

closed: YYYY-MM-DD
