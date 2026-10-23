# Wave 8: where Murmuration's money goes, and what verification buys (v0)

opened 2026-10-24 00:11 · closed PLACEHOLDER_CLOSE · PI: research-pi (Opus) · workers on Sonnet,
headless cells on haiku (two probes on Sonnet and Opus, stated in their reports)

> "The overarching goal is to progressively optimize murmuration by using it yourself. You are
> Murmuration and you optimize murmuration." (2026-10-24 00:11)

## Result

- **Your 07:53 question, whether to optimize the scripts' outputs: no.** Lab-script output is
  3.7% of what workers pay to carry context; capping it saves at most 0.5% (ESTIMATE). The largest
  block is the worker's own earlier turns (41.6%), and its thinking is billed again on every later
  request (MEASURED). Every worker-side lever we tested is under 7%: documents by section, rtk,
  batching (workers already batch), effort (already near its floor), a hand-back gate. **The
  worker side is near its floor.**
- **The money is in the PI.** USD 148 of the lab's 405 are the PI's main threads, 56% of it
  re-reading context it already holds. The platform compacts a 1M-token session only near 967k.
  A compaction window near 200–250k kept what a PI-like session needed (w08-c3 · MEASURED, verified)
  and is estimated to save USD 31–45 over the lab's history, about a quarter of PI spend. It is one
  line in a settings file the guard keeps agents out of: **yours** (below).
- **colgrep (your 08:04 observation):** no sign of distrust. colgrep indexes a markdown file as one
  unit whose snippet is its first lines, so for the lab's notes a hit is only a path; and 65% of
  whole reads were of files the PI's own brief named. Briefs now name sections (w08-c6), and the
  start note's search path now points at the lab instead of the main checkout (w08-c12). A
  section-level unit for markdown would be a change to your colgrep-mcp repository.
- **Decisions under uncertainty (your 08:04 suggestion):** literature fetched and a per-agent
  pause model built: 1 hour of cache for the PI under every rule, 5 minutes for reproducers and
  explorers, authors a knife-edge (−0.02 ± 0.39 USD per life) that only a risk attitude decides;
  wave 7's +0.87 for authors did not survive timed data.
- **Verification pays, and has a blind spot.** Over eight waves a third of claims arrived stated
  above their evidence and the verifier brought them down, for about 8% of spend. What it misses
  is what nobody is asked to run: a selftest failed at two merges, wave 7's and this wave's. The
  landing steps now include it (w08-c8); this wave it caught w08-c4's first merge before main.
- **The guard had two holes**, found by building a frozen labelled replay set of its decisions:
  a bypass flag after `"$(cat f)"`, and `env -u VAR claude … --setting-sources`. PLACEHOLDER_C13

## What the wave taught about the system's money

1. **Cost follows what is carried and how often it is re-read.** A token entering a context early
   is paid on every later request. That is why the PI (long-lived, Opus, woken by every worker) is
   the large spender, why a worker's own thinking is a fifth of its cost, and why script output,
   read once and early, is small.
2. **Most "levers" are ceilings under 7%.** The lab measured eleven this wave; the only one above
   10% acts on the PI's context, not on any tool or script.
3. **A second implementation has a running cost.** The Rust port saves 7–13 ms a hook start; its
   first follow-up change cost about 4 times the USD and 17 times the minutes on the Rust side, and
   its first merge broke a selftest. The installer's fall-back makes a stale port slow, not wrong.
4. **Equality is not correctness.** w08-c5's name binding was byte-equal in Python and Rust on
   5,948 events and confidently wrong in 4 of 58 orders of three same-type dispatches; only an
   enumeration of orders by its verifier showed it.

## What was decided, and why

| Claim | Decision | Why |
|:--|:--|:--|
| w08-c4 (supersedes w08-c1) | landed | equal on 3,821 + 651 events, fall-back safe; small saving, asked for by you |
| w08-c6, w08-c8 (supersedes w08-c7) | landed | briefs: hand-back limit, sections; notes: times from a tool; landing steps |
| w08-c11 (supersedes w08-c9) | landed, four decision sections appended | a human reading `/lab-status` saw decided escalations as undecided |
| w08-c12 (supersedes w08-c5) | landed | names right or marked unconfirmed, never confidently wrong |
| PLACEHOLDER_C13ROW |  |  |
| w08-c3 | the setting is yours; the PreCompact hook stays out | the hook added nothing; the file is guarded |
| w08-c2 | not landed | 1–2% at best, negative if the PI opens the file, which its rules say to do |
| effort, batching, rtk, script caps | stay out | measured at or near zero for this lab |

## Worst-fitting case

w08-c5: a change that passed every equality test the lab knows how to run, and would have written
confidently wrong names into the log a human reads. The lab's tests check that two implementations
agree; they cannot check that both are right. The verifier found it only by enumerating arrival
orders of three dispatches, a property test the author had not written.

## For you

- **The compaction window**: add `"autoCompactWindow": 250000` to
  `/Users/hacker/Documents/src/CrackingShells/Murmuration/.claude/settings.local.json`. The next
  wave's PI is the live check.
- **Your colgrep-mcp repository**: a section-level markdown unit; the search-policy hook's
  inconsistent denials; a 35–72 s first search on a stale index.
- As before: the managed setting (`/status`), the pre-commit hook for the Rust binary, your own
  hooks' cost.

## Not covered

A real PI session through a compaction; the Desktop's own dispatch concurrency for the name
binding; Linux and Windows; the colgrep change; any measure of research quality beyond what the
verifiers' verdicts show.

## Pointers

Wave note `__statera__/wave-08.md`; synthesis "Wave 8" and open items 42–48; claims
`__pondus__/w08-c1.md`–`w08-c13.md`; explorer reports `__reports__/wave-08/explorer-w08-*/`; the
cost map `__reports__/wave-08/explorer-w08-h/lab_cost_map.html`.
