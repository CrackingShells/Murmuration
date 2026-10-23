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

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w08-a | explorer | workers' context USD by source over waves 4–7: are lab scripts' outputs worth shortening; rtk's coverage (item 38, 39) | |
| explorer-w08-d | explorer | the PI's own spend by source and habit, with levers (item 29; 46% of priced spend) | |
| explorer-w08-b | explorer | does colgrep answer the lab's own questions, and why workers full-read (item 41, 11) | |
| explorer-w08-c | explorer | literature and a decision model for the cache lifetime and one more premium-vs-payoff choice (item 40) | |
| author-w08-1 | author | w08-c1: `budget` and `handback` as subcommands of the Rust binary, replay-equal, with fallback (item 36) | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

closed: YYYY-MM-DD
