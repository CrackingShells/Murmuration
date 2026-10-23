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

**Explorers c, a, d back (note committed 00:29, 40ff7b7).**
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
  life, a knife-edge; w07-c7's +0.87 rested largely on untimed wave-4 pauses
  (S-w08-explorer-w08-c-1). [Corrected after S-w08-explorer-w08-i-2: the misaligned `tool_s` is
  in my wave-7 addendum `__instrumenta__/w07_ttl_by_type.py` (cost map 3b), not in w07-c7's own
  script, whose verifier had already found the sign undetermined.] All author and reproducer misses follow a hand-back wait set by the
  resumer. The PI keeps 1 hour under every rule [source: explorer-w08-c's report, ESTIMATE].
  I keep authors on 1 hour (minimax regret, and no measured loss); no claim.
- What changes: round 2 goes to the PI's side and to thinking. author-w08-2 (w08-c2, short
  hand-backs, net of the PI reading the report instead), explorer-w08-e (what compaction the
  platform allows and keeps), explorer-w08-f (are thinking blocks billed again; is `effort` a
  lever). Briefs from now ask for a hand-back of at most about 1,500 characters.

**explorer-w08-b back (note committed 00:32, 1730b71; the earlier "00:45" and "01:05" were my estimates, corrected).**
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

**explorer-w08-e back (00:52, 1c44fee).**
- The PI's auto-compact default on a 1M model is about 967k; `autoCompactWindow` (settings),
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW` or `--autocompact` set it, 100k–1M, firing at window minus
  33k; it reaches subagents too. PreCompact can block and its stdout reaches the summary. A
  compaction costs about USD 0.13 at 170k (haiku runs re-priced at Opus) and leaves 24k + 40k,
  30k of it the re-sent listings. Codes and user facts survived (28/28), prose detail did not
  (0/10). Net over the PI history near 250k: USD 31–45, if the PI re-reads under about 45k per
  compaction [source: explorer-w08-e's report, CITED/MEASURED/ESTIMATE as labelled there].
- Idle compaction never fired in six Desktop PI sessions; two paid USD 3.4–3.8 re-writes after an
  hour's pause (S-w08-explorer-w08-e-1).
- Decision: the largest lever of the wave goes to a claim, w08-c3 (author-w08-3), with a
  PreCompact hook that writes the lab state into the summary and a PI-like Opus run through a
  compaction. If it holds, I land it and run on it myself for the rest of the wave.

**explorer-w08-f back (59720e6).**
- Thinking blocks are billed again on every later request of a tool loop: context growth equals
  the previous output with thinking, coefficient 0.997 (0.98–1.01), 168 pairs; about 19% of
  worker context USD in waves 4–7 by its signature fit [source: explorer-w08-f's report, MEASURED
  and ESTIMATE as labelled]. So explorer-w08-a's and explorer-w08-d's residual was real.
- `effort` in agent frontmatter works for subagents (thinking 467 low, 501 default, 613 high,
  2,711 max), but the default already behaves like low or medium, and on two planted-error
  verifier tasks (30 runs) every arm got the verdict and cost the same within noise; max cost
  7–8x. Effort stays out as a lever: nothing to save below the default.
- Hand-back length, a natural experiment of this wave: the four explorers with no length line
  handed back about 2,500–5,000 characters; e and f, told "at most about 1,500", handed back
  about 1,700–1,900 [source: the hand-back messages in this session, character counts by eye,
  not measured]. w08-c2 measures it properly.
- What changes: the worker side's lever is now its request count. explorer-w08-g measures what
  merging independent calls would save in money and whether one agent-file line gets workers to do
  it.

**author-w08-2 back (w08-c2 filed at 3318c4c; `date` 01:07).**
- The gate works (7 of 7 over-long cells denied once, 5 of 5 with a file shortened, under-N
  untouched) but the money is small: USD 0.9–2.8 net over 180 past hand-backs at N = 5,000,
  1–2% of PI spend, and negative if the PI then opens the worker's file in more than 20–62% of
  fired cases; in the past it opened the named file after 19 of 26 explorer hand-backs [source:
  `__pondus__/w08-c2.md`, ESTIMATE for USD]. explorer-w08-d's USD 6–10 was gross.
- Decision: w08-c2 does not land and gets no verifier (USD 2–3 to verify a change I would not
  land). Reason: the best case is 1–2%, its sign rests on the PI's own reading, and the PI's rule
  is to open at least one raw artifact per returning agent. The brief's own line ("at most about
  1,500 characters"), which costs nothing, stays as my practice; it goes into the PI-practice
  claim at the close.

**author-w08-1 back (w08-c1 filed; claim commits deef5e3, 96a80b4, 5cb807c).**
- Equality strong: 0 differences byte for byte in 3,821 replayed events, 0 of the 2,250 built on
  150 real transcripts handed to Python (587 fuzz and odd-state events are, by design); 19 of 19
  fall-back cases. Time small and only partly inside the registered rules: 7–15 ms a start, about
  15 ms a tool batch; wall rule met in 11 of 14 payload-runs; in-platform PostToolBatch 9 of 12
  [source: `__pondus__/w08-c1.md`, unverified MEASURED].
- My reading of the size: at about 1,000 tool batches a wave that is seconds of worker wall per
  wave [assumption: request counts from explorer-w08-a, 3,685 worker requests over four waves].
  The case for landing is the user's "saving that 1% if we know we can save it" and a risk the
  fall-back makes small: an edit to `budget.py` makes the installer fall back to Python, so a
  stale port costs speed, not correctness. Against: a second implementation of 1,300 lines of
  logic, one `unsafe` call, three clippy lints. reproducer-w08-1 dispatched; I decide at its
  verdict.

**explorer-w08-g, author-w08-3, reproducer-w08-1 back.**
- Batching is not a lever: unchanged Sonnet subagents already send independent Reads together (8
  of 8, 16 of 16); the one-line nudge changed nothing; merges that past workers missed are worth
  0.2–2% of worker USD [source: explorer-w08-g's report, MEASURED/ESTIMATE]. With f's effort
  result, the worker side is near its floor: what a worker pays for is dependent
  run-read-fix steps, which is the work.
- w08-c3: compaction with the existing resume brief kept what a PI-like session needed (Opus 1
  of 1, haiku 3 of 3, at a 150k window on a small lab); the PreCompact hook added nothing and
  does not land; only the main checkout's `.claude/settings*.json` load under the Desktop's
  `--project-config-root`, and the guard (G3) refuses writes to them, correctly [source:
  `__pondus__/w08-c3.md`, unverified MEASURED]. So the landing is a setting in a file the
  permission layer guards: the user's to write. reproducer-w08-3 dispatched.
- Name swaps in `start` lines on same-second dispatches of one agent type are real (00:29:22:
  `a09a86b0…` started as explorer-w08-e and is explorer-w08-f; S-w08-author-w08-3-2); later lines
  carry the right name. Item 6, still open.
- w08-c1, ESCALATE: equality reproduced on the verifier's own 651 live wave-8 events, all through
  the port; 12–13 ms saved per start by its pairs; the title omits the 587 hand-offs and the
  in-platform miss. Decision: the narrower wording is filed as w08-c4 (supersedes w08-c1),
  checked by the same verifier; I land on w08-c4 if it holds.

**reproducer-w08-3 back: w08-c3 SUPPORTED (73febd1).**
- Re-scored 17 runs partly blind (15 of 17 at 5/5; the two Q2 misses are the hook arm and the
  no-brief arm), four fresh seed-5 runs all 5/5, compaction about USD 0.45 on Opus with its
  post-write, the net model reproduced (USD 44.65 to 32.29 for R 2.5k to 45k). 200k and 250k are
  equal within the model; 283,000 came from my brief [source: `__pondus__/w08-c3.md`].
- Decision: the setting is the change, and it lives in the main checkout's
  `.claude/settings.local.json`, which the guard protects and the framing leaves to the user. I
  put it to the user at the close as a one-line edit, a window of 250,000 (compaction near 217k),
  with the live check being the next wave's PI. The PreCompact hook stays out.
- PI-practice claims filed: w08-c6 (hand-back length line, sections in briefs) and w08-c7 (times
  from a tool, landing steps), on branch `w08-c6-pi-practice`; reproducer-w08-6 checks both.
  author-w08-5 (w08-c5) fixes the start note's colgrep path and the start-line names in both
  implementations, and measures what the second implementation costs a change.

**reproducer-w08-6 back: w08-c6 SUPPORTED, w08-c7 OVERSTATED, w08-c8 SUPPORTED; both landed.**
- Spend at 01:31: this checkout USD 39.13 (lower bound, open), headless 21.22 exact, so about 59 of
  the 150 for this wave [source: `scripts/lab_status.py --spend`, both projects].
- The cost side is now mapped down to its floor: the worker side's levers are all under 2–7%
  (scripts' output, documents, rtk, batching, effort, the hand-back gate), the PI's compaction is
  24–32% of PI spend and the user's to set. Two probes on the other half of the user's purpose,
  a team that works alone and stays trustworthy: explorer-w08-i audits what verification bought
  across waves 1–8 (two verified things were wrong this wave); explorer-w08-j freezes a labelled
  replay set of guard decisions (item 26), now that the Rust guard decides every Bash call.

**explorer-w08-h and explorer-w08-i back.**
- The cost map after wave 8 exists, with a 16-lever ladder
  (`__reports__/wave-08/explorer-w08-h/lab_cost_map.html`, 465c229); it is refreshed at the close.
- What verification bought, waves 1–8: 38 of 76 verified claims SUPPORTED first time, 25
  OVERSTATED, 13 ESCALATE (8 of them overstated on evidence alone); verification about 8% of
  spend, USD 0.45 a claim against 1.42 for an author [source: explorer-w08-i's report,
  MEASURED/ESTIMATE]. So a third of claims arrive stated above their evidence, and the verifier is
  what brings them down: it pays. What it missed: `budget.py --selftest` failed at two merges
  (wave 7's 5e16a53 too, recorded then, no step added); w08-c8's landing step answers it.
- The decision record is a gap: 9 claims the PI decided still read "escalated: PI decides", and
  11 stand on PI restatements no verifier re-read. author-w08-9 (w08-c9) makes `lab_status.py`
  read a PI decision section; I append the sections once it stands.

**explorer-w08-j back (7834635).**
- The two guards agree on all 739 frozen cases and 20,896 recorded calls. False denials: 113 of
  623 negatives in the set; in live use 17 of 19 denials in waves 6–8 were false, none stopped a
  worker loosening anything. False allows: 24, and two holes reproduced: a bypass flag after
  `"$(cat f)"`, and `env -u VAR claude … --setting-sources project`; eight real explorer calls in
  waves 1–6 had that shape [source: explorer-w08-j's report and puzzle 1, MEASURED].
- Decision: close the holes (w08-c10, author-w08-10), in both implementations, as a tightening
  only. The offline variants that cut false denials from 113 to 77 lose one true case: they stay
  out. A guardrail's false denials cost a worker a detour (17 live in three waves); a false allow
  costs the user's permission layer.

**w08-c5 and w08-c9 back from their verifiers (`date` 02:23).**
- w08-c9 ESCALATE: the title was false for w02-c7 and w02-c8 (their notes say "below MEASURED:
  restate"), the ref check matched substrings, and a restatement over OVERSTATED could show the
  refused label; fixed at d24f3c0 and re-verified. Decision: restated as w08-c11 (supersedes
  w08-c9; 9 escalations; fenced headings and missing supersede targets fixed at e815afd), back to
  reproducer-w08-9. Of the 9 decided escalations, only 4 have a wave-note line naming the label
  (w01-c2, w01-c8, w02-c10, w05-c1): I append sections for those 4 only; w03-c2, w04-c4, w04-c7,
  w04-c10 and w07-c7 stay "escalated: PI decides" and are listed in the synthesis.
- w08-c5 OVERSTATED: the absolute path is right everywhere; the name binding is right for one or
  two same-type dispatches and wrong in 4 of 58 orders with three, once as a confirmed wrong name.
  The author narrowed the head twice during verification (item 5 again). Decision: no landing of
  a binding that can be confidently wrong; author-w08-5 fixes it in both implementations and files
  w08-c12 (supersedes w08-c5), proven by exhaustive orders for 1–4 dispatches.
- Spend: this checkout 57.10 (lower bound), headless 21.27: about USD 77 of the 150 by 02:23.

**w08-c12 and w08-c13 SUPPORTED and landed; the last round (`date` 04:05).**
- Both landed with w08-c8's steps; the guard refused my own Write and a Bash note quoting a hole
  form, both rightly, and the notes went through the Edit tool.
- This PI session so far: USD 15.18 over 167 requests, context 406k tokens, no compaction; carried
  worker hand-backs 7.1% of what the PI re-reads [source: `__instrumenta__/w08d_pi_context.py` on
  this session, output in `/private/tmp/murmuration-w08/research-pi/pi_self/`, ESTIMATE
  attribution]. The session is itself the case for item 42.
- With two hours left: author-w08-14 (w08-c14) closes the older combined-`-c` hole the guard's
  verifier found (S-w08-reproducer-w08-10-5); explorer-w08-k drafts the evidence for the five
  escalations no note decided (item 45), which I decide. explorer-w08-h refreshes the cost map.

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
| author-w08-3 | author | w08-c3: a PI compaction threshold with a PreCompact hook carrying the lab state; Opus PI-like run through it | |
| explorer-w08-g | explorer | worker requests that could have been merged: USD, and one agent-file line tested | |
| reproducer-w08-1 | reproducer | verify w08-c1 with its own replay set from wave-8 events, the fall-back, `localtime_r`, the title against e3/e4 | |
| reproducer-w08-3 | reproducer | verify w08-c3: re-score blind, a fresh pair, the settings-location statement, transfer to a real PI | |
| explorer-w08-h | explorer | the cost map after wave 8, with a lever ladder | |
| author-w08-5 | author | w08-c5: the start note's colgrep path absolute, start-line names by identity, in Python and Rust; the cost of two implementations | |
| reproducer-w08-6 | reproducer | verify the PI's w08-c6 and w08-c7 | |
| explorer-w08-i | explorer | what verification bought: verdicts, later corrections of standing claims, cost per catch, waves 1–8 | |
| explorer-w08-j | explorer | a frozen labelled replay set of guard decisions; false denials and allows by rule (item 26) | |
| author-w08-9 | author | w08-c9: a PI decision section in claim files, read by `lab_status.py` | |
| author-w08-10 | author | w08-c10: close the guard's two holes in Python and Rust, tightening only | |
| reproducer-w08-5 | reproducer | verify w08-c5, then w08-c12 | OVERSTATED; then SUPPORTED |
| reproducer-w08-9 | reproducer | verify w08-c9, then w08-c11 | ESCALATE; then SUPPORTED |
| reproducer-w08-10 | reproducer | verify w08-c10, then w08-c13 | OVERSTATED; then SUPPORTED |
| author-w08-14 | author | w08-c14: combined shell `-c` options read as `-c`, Python and Rust | |
| explorer-w08-k | explorer | evidence and proposed decision sections for the five undecided escalations | |
| author-w08-1 | author | w08-c1: `budget` and `handback` as subcommands of the Rust binary, replay-equal, with fallback (item 36) | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w08-c1 | `budget` and `handback` as Rust subcommands (first statement; title overstated) | superseded by w08-c4 |
| w08-c2 | A once-only gate on hand-backs over 5,000 characters: works; nets USD 0.9–2.8, negative if the PI opens the file | unverified MEASURED / ESTIMATE (not landed) |
| w08-c3 | Compaction with the existing resume brief keeps what a PI-like session needs; the PreCompact hook adds nothing; about USD 0.45 a compaction on Opus | MEASURED (the setting is the user's) |
| w08-c4 | `budget` and `handback` in the Rust binary: byte-equal on 3,821 events (587 handed to Python), 7–13 ms a start outside the platform | MEASURED (landed 1e0a81d) |
| w08-c5 | Start note path and name binding (binding wrong with three dispatches) | superseded by w08-c12 |
| w08-c6 | Briefs ask for a hand-back of at most about 1,500 characters and name sections; first hand-backs about halved (n = 6 each) | MEASURED (landed 16b05a8) |
| w08-c7 | Landing steps (title bundled unsupported steps) | superseded by w08-c8 |
| w08-c8 | Times from a tool; every selftest on the merged tree; install before the main merge; smoke run | CONJECTURE (landed 16b05a8) |
| w08-c9 | PI decision sections read by `lab_status.py` (11 claims; two wrong) | superseded by w08-c11 |
| w08-c10 | Two guard holes closed (missed three forms, a new false denial) | superseded by w08-c13 |
| w08-c11 | PI decision sections, capped, read by `lab_status.py` | MEASURED (landed dc74371) |
| w08-c12 | Absolute search path in the start note; a start named only when unambiguous | MEASURED (landed 3d5147a) |
| w08-c13 | The guard's two holes closed in Python and Rust, tightening only | MEASURED (landed 1511545) |
| w08-c14 | `-`-prefixed shell option clusters with c read as -c (title said every cluster) | superseded by w08-c15 |
| w08-c15 | `-`-prefixed clusters with c read as -c for five shells, 0 of 20,282 variants allowed against 8,098 on the base; `+c` and zsh/ksh option misreadings still pass | MEASURED (landed 92a853f) |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w08-author-w08-1-1 | parked: a ceiling measured under load does not carry across loads; w08-c4 gated on signs, which held |
| S-w08-author-w08-1-2 | followed: w08-c4 (the title states the rule met in 11 of 14) |
| S-w08-author-w08-1-3 | parked: a harness artefact, fixed and reported both ways in w08-c4 |
| S-w08-author-w08-1-4 | parked: the port copies Python's numeric quirks on purpose; recorded in the claim |
| S-w08-author-w08-1-5 | followed: w08-c4 (587 hand-offs stated in the title) |
| S-w08-author-w08-1-6 | parked: a miscount in the protocol, corrected in its amendments |
| S-w08-author-w08-1-7 | parked: one `unsafe` call, checked over 15 zones by reproducer-w08-1 |
| S-w08-author-w08-1-8 | parked: the worker path in the platform needs a plugin data folder of the running session; the smoke run covered the installed path |
| S-w08-author-w08-1-9 | parked: an extra note line in one interleaving, in both implementations' race; no torn lines |
| S-w08-author-w08-1-10 | parked: Linux, DST inside a scenario and glob characters in a lab path are untested; noted in the synthesis |
| S-w08-author-w08-1-11 | followed: w08-c5 (author-w08-5 touches the same crate; clippy lints in its scope) |
| S-w08-author-w08-1-12 | followed: w08-c4 (the drift is in the title) |
| S-w08-author-w08-2-1 | followed: w08-c2 (net, not gross, in the title) |
| S-w08-author-w08-2-2 | followed: PI decision, w08-c2 does not land (wave note) |
| S-w08-author-w08-2-3 | parked: the gate's detail-kept test could not separate cause; w08-c2 does not land |
| S-w08-author-w08-2-4 | parked: default mode never calls SubagentHandback; w08-c2 does not land |
| S-w08-author-w08-2-5 | parked: haiku compliance; w08-c2 does not land |
| S-w08-author-w08-2-6 | parked: pair noise in a gate that does not land |
| S-w08-author-w08-2-7 | parked: the harness frame of about 1,276 characters per hand-back is the platform's |
| S-w08-author-w08-2-8 | parked: two unclean runs, reported in the claim |
| S-w08-author-w08-3-1 | parked: one Opus run in the hook arm, which does not land |
| S-w08-author-w08-3-2 | followed: w08-c5 (start-line names by identity) |
| S-w08-author-w08-3-3 | followed: the setting goes to the user; the guard's refusal is correct |
| S-w08-author-w08-3-4 | followed: open item on the live check of w08-c3 at a real PI's 91k floor |
| S-w08-author-w08-3-5 | parked: a PreCompact hook cannot tell a subagent; the hook does not land |
| S-w08-author-w08-3-6 | parked: prose kept in 17 of 17 at a small lab; the transfer question is the open live check |
| S-w08-author-w08-3-7 | parked: a no-brief arm; the lab always has the resume brief |
| S-w08-author-w08-5-1 | followed: w08-c12 (the installer's self-test fixed; a clean install is now a landing step, w08-c8) |
| S-w08-author-w08-5-2 | parked: the Desktop's own dispatch concurrency is untested; w08-c12 is right for any arrival order |
| S-w08-author-w08-5-3 | followed: w08-c12 (the second divergence fixed; the first is unreachable from the platform); the lesson is in the report: equality is not correctness |
| S-w08-author-w08-5-4 | followed: w08-c12 (binding does not rely on the answer arriving first) |
| S-w08-author-w08-5-5 | parked: briefs.md already says each budget line goes on its own line |
| S-w08-author-w08-5-6 | followed: synthesis item 36 (the second implementation's cost, as measured, with its stamp caveat) |
| S-w08-author-w08-9-1 | followed: w08-c11 (w02-c7 and w02-c8 dropped; a decision over OVERSTATED must name a lower label) |
| S-w08-author-w08-9-2 | parked: a superseded claim shows its successor, which is the state a reader needs |
| S-w08-author-w08-9-3 | parked: `ref:` line numbers drift when a note is edited; closed notes are not edited, and the open note's refs are written at close |
| S-w08-author-w08-9-4 | followed: synthesis item 45 (w07-c7 left for a PI decision) |
| S-w08-author-w08-9-5 | parked: one older PI note inside a claim file, before the decision section existed |
| S-w08-author-w08-9-6 | parked: a wave-2 note's wording; w02-c8 shows its verdict correctly |
| S-w08-author-w08-9-7 | parked: amending in a shared branch is unsafe; the skill already says commit by naming paths, and the author restored the commit |
| S-w08-author-w08-10-1 | followed: synthesis item 26 (the three remaining false allows listed) |
| S-w08-author-w08-10-2 | parked: a false denial that fails closed; item 26 keeps the count |
| S-w08-author-w08-10-3 | parked: the recorded-call count differs by collection folder, not by decision |
| S-w08-author-w08-10-4 | parked: a PI heredoc quoting a hole form is a fail-closed false denial; the PI's notes go through the Edit tool |
| S-w08-author-w08-10-5 | parked: a G3 denial of data naming a settings file; counted in the frozen set (item 26) |
| S-w08-author-w08-10-6 | followed: synthesis item 26 (wrapper option tables from memory, untested against man pages) |
| S-w08-author-w08-10-7 | followed: w08-c13 (process substitution covered) |
| S-w08-author-w08-10-8 | followed: w08-c13 (all three fixed after the verifier found them) |
| S-w08-author-w08-10-9 | followed: synthesis item 26 (out-of-scope launchers listed) |
| S-w08-author-w08-14-1 | parked: the frozen set holds no such form, so it shows only that nothing else moved; the generated and verifier cases carry the claim |
| S-w08-author-w08-14-2 | parked: a counting slip in the author's first run, corrected before filing |
| S-w08-author-w08-14-3 | parked: a 25-minute full case run; the quick subset is the landing check |
| S-w08-author-w08-14-4 | followed: reproducer-w08-14 ran real shells (its 10,200 forms); the misreadings it found are open item 26 |
| S-w08-explorer-w08-a-1 | followed: explorer-w08-f (thinking is billed again, coefficient 0.997) |
| S-w08-explorer-w08-a-2 | parked: inline code is the worker's own analysis; its call text is counted once whether it lives in a heredoc or a Write, so moving it to a file saves nothing measurable |
| S-w08-explorer-w08-a-3 | followed: w08-c6 (briefs name sections; the wave-note lever is 0.9% and dropped) |
| S-w08-explorer-w08-a-4 | parked: the classifier's limits move shares by a point or two, not the ranking; no decision rests on them |
| S-w08-explorer-w08-a-5 | parked: rtk's safe part is 2.9% of worker context USD and installing it is the user's (synthesis item 39) |
| S-w08-explorer-w08-b-1 | followed: synthesis item 41 restated (markdown is one unit per file; a section-level unit belongs to the user's colgrep-mcp repository) |
| S-w08-explorer-w08-b-2 | parked: the search-policy hook is the colgrep-mcp plugin's, not this plugin's; reported to the user |
| S-w08-explorer-w08-b-3 | followed: explorer-w08-j (frozen labelled replay set of guard decisions) |
| S-w08-explorer-w08-b-4 | parked: the stale main index is refreshed by the first search; a 40 s first call is the colgrep plugin's behaviour, reported to the user |
| S-w08-explorer-w08-b-5 | parked: wording sensitivity of colgrep ranks is the tool's; no lab decision rests on it |
| S-w08-explorer-w08-b-6 | parked: whether the 41 unnamed script reads were reads to edit or to find is not separable from transcripts; scripts are the one place colgrep already helps |
| S-w08-explorer-w08-c-1 | followed: the synthesis restates w07-c7's money on timed lives (explorer-w08-c), not the +0.87 |
| S-w08-explorer-w08-c-2 | parked: two hits over the TTL in 2,536 pauses do not change any choice; shared-prefix refresh is a platform question |
| S-w08-explorer-w08-c-3 | parked: the hand-back wait is set by the resumer; the 1-hour author cache stays (minimax regret) and no platform control for a per-phase TTL exists |
| S-w08-explorer-w08-c-4 | followed: explorer-w08-d (PI spend over six sessions; the PI keeps 1 hour under every rule) |
| S-w08-explorer-w08-d-1 | parked: one double re-write in 1,116 PI requests (USD 0.64); not a pattern |
| S-w08-explorer-w08-d-2 | parked: one hit after 86 minutes; same question as S-w08-explorer-w08-c-2, a platform one |
| S-w08-explorer-w08-d-3 | followed: explorer-w08-f (thinking carried, measured) |
| S-w08-explorer-w08-d-4 | followed: w08-c2 (the hand-back gate) and w08-c3 (compaction makes each wake cheaper); wakes themselves are the platform's |
| S-w08-explorer-w08-d-5 | followed: synthesis item 29 restated with both readings |
| S-w08-explorer-w08-e-1 | parked: idle compaction is not offered in the Desktop entrypoint; an explicit window (w08-c3) makes it matter less; reported to the user |
| S-w08-explorer-w08-e-2 | parked: the post-compaction preamble is the platform's re-send; the skill listing was tried in w07-c1 and did not land |
| S-w08-explorer-w08-e-3 | followed: w08-c3 (PI-like runs through a compaction; prose kept in 17 of 17) |
| S-w08-explorer-w08-e-4 | parked: 3 of 8 against 2 of 2 'ok' endings cannot separate compaction from chance; w08-c3's runs showed no such ending |
| S-w08-explorer-w08-f-1 | parked: the PI's effort is the session's, not the agent file's; effort stays out as a lever |
| S-w08-explorer-w08-f-2 | parked: workers run near the model default; nothing to save below it |
| S-w08-explorer-w08-f-3 | parked: a constant 30-60 tokens per request; no decision rests on it |
| S-w08-explorer-w08-f-4 | parked: the two fits agree on the mean (0.84x); per-block accuracy decides nothing here |
| S-w08-explorer-w08-f-5 | followed: explorer-w08-g interleaved its arms and kept the prefix warm |
| S-w08-explorer-w08-g-1 | parked: 92% single-call requests are dependent run-read-fix steps; batching is not a lever (explorer-w08-g) |
| S-w08-explorer-w08-g-2 | parked: two runs that counted with Grep instead of reading are a valid shortcut; no decision rests on it |
| S-w08-explorer-w08-g-3 | parked: one wrong answer in 41 runs, in the lever arm; the lever stays out |
| S-w08-explorer-w08-g-4 | parked: the thinking part of an upper bound already under 2% |
| S-w08-explorer-w08-g-5 | parked: numeric dependence would lower the count further; the lever stays out either way |
| S-w08-explorer-w08-h-1 | followed: the synthesis's cost section states PI spend per wave to the close and per session, both |
| S-w08-explorer-w08-h-2 | followed: the synthesis states both figures with their scope (three sessions net; six sessions counterfactual) |
| S-w08-explorer-w08-h-3 | followed: the synthesis takes explorer-w08-c's timed figures over wave 7's map |
| S-w08-explorer-w08-h-4 | parked: a count of rules in a report's prose against its table; the table stands |
| S-w08-explorer-w08-h-5 | followed: the synthesis gives the thinking share as 19–22.5% with both sources |
| S-w08-explorer-w08-h-6 | parked: the ladder's bases differ by design (each lever's own pool); the map says so |
| S-w08-explorer-w08-h-7 | followed: the synthesis gives the PI's share with its denominator |
| S-w08-explorer-w08-h-8 | parked: headless spend was the price of this wave's probes (compaction and effort on Sonnet/Opus); stated in the cost section |
| S-w08-explorer-w08-h-9 | parked: the map gives the platform figure with w08-c4's drift caveat |
| S-w08-explorer-w08-h-10 | followed: the wave note records its close time and the spend at close; the synthesis gives the PI's wave-8 figure to the close |
| S-w08-explorer-w08-h-11 | followed: the synthesis states verification's share with its denominator (about 8% of USD 411.93, waves 1-8 at explorer-w08-i's cut) |
| S-w08-explorer-w08-i-1 | followed: w08-c8 (selftests on the merged tree) |
| S-w08-explorer-w08-i-2 | followed: wave-note correction and synthesis (the misaligned column is the PI's addendum, not w07-c7's evidence) |
| S-w08-explorer-w08-i-3 | followed: w08-c11 (decision sections; four appended, five listed as item 45) |
| S-w08-explorer-w08-i-4 | followed: synthesis item 46 |
| S-w08-explorer-w08-i-5 | parked: wave-7 verifier spend is an inference; the 8% figure is stated as an ESTIMATE |
| S-w08-explorer-w08-j-1 | followed: w08-c13 |
| S-w08-explorer-w08-j-2 | followed: synthesis item 26 (live false denials counted; the false-denial variants stay out) |
| S-w08-explorer-w08-j-3 | parked: G4 compares with files on disk, so a frozen set cannot freeze it; stated with the set |
| S-w08-explorer-w08-j-4 | parked: one labeller; a second labeller is a check for a later wave |
| S-w08-explorer-w08-k-1 | parked: the state says 'restated, not re-verified', which is what a reader should see for a head the PI edited |
| S-w08-explorer-w08-k-2 | followed: w07-c7's decision statement says c4 is an ESTIMATE of undetermined sign, with wave 8's timed figure |
| S-w08-explorer-w08-k-3 | parked: the narrowed block's Grep result rests on the author's one probe; stated in the decision's reason |
| S-w08-reproducer-w08-1-1 | parked: machine state moves a 10 ms saving by 2-5 ms; the sign held |
| S-w08-reproducer-w08-1-2 | followed: w08-c5 (what SubagentStart carries) |
| S-w08-reproducer-w08-1-3 | parked: real spend under the first threshold; seeded scenarios cover the notes |
| S-w08-reproducer-w08-1-4 | parked: the machine cannot make a bit-identical build (w07-c6); the manifest pins what ships |
| S-w08-reproducer-w08-3-1 | followed: the synthesis uses the real post-compaction context (about 49k), not post_tokens |
| S-w08-reproducer-w08-3-2 | followed: the user is offered a window of 250,000, any of 200-250k being equal in the model |
| S-w08-reproducer-w08-3-3 | parked: haiku compaction cost varies 0.10-0.29; Opus is the PI's |
| S-w08-reproducer-w08-3-4 | followed: open item on the live check of w08-c3 (a real PI's wave is the harder test) |
| S-w08-reproducer-w08-3-5 | followed: the setting's location is stated to the user (the main checkout's local settings) |
| S-w08-reproducer-w08-5-1 | followed: w08-c12 |
| S-w08-reproducer-w08-5-2 | followed: w08-c12 |
| S-w08-reproducer-w08-5-3 | followed: w08-c12 (unsafe agentId ignored) |
| S-w08-reproducer-w08-5-4 | parked: a vanished enumeration process; the verdict rests on the reruns |
| S-w08-reproducer-w08-5-5 | followed: w08-c12 (the lab path is escaped) |
| S-w08-reproducer-w08-6-1 | parked: the medians are corrected in the verdict; the title's ranges hold |
| S-w08-reproducer-w08-6-2 | parked: the limit is an ask; it halves the message, which is what the skill text says it does |
| S-w08-reproducer-w08-6-3 | followed: w08-c8 (the reason now cites the old binary's exit 2) |
| S-w08-reproducer-w08-6-4 | parked: a selftest that reads ../hooks/hooks.json needs the whole tree; noted, harmless on a checkout |
| S-w08-reproducer-w08-9-1 | followed: w08-c11 |
| S-w08-reproducer-w08-9-2 | followed: synthesis item 45 (only four sections appended, where the note names the label) |
| S-w08-reproducer-w08-9-3 | followed: w08-c11 (fenced blocks are text) |
| S-w08-reproducer-w08-9-4 | parked: a G2 denial of a script naming a config variable; fail-closed, counted with item 26 |
| S-w08-reproducer-w08-9-5 | parked: a count in the head that ages as claims are added |
| S-w08-reproducer-w08-10-1 | parked: one registered list reads 3 of 6 for the verifier and 2 of 6 for the author, unchanged before and after |
| S-w08-reproducer-w08-10-2 | followed: w08-c13 (joined `env -S` expanded) |
| S-w08-reproducer-w08-10-3 | followed: synthesis item 26 (the Python fall-back's quadratic case) |
| S-w08-reproducer-w08-10-4 | followed: the report's lesson for briefs (put flag strings in data files, not scripts); G4 is right to refuse a script |
| S-w08-reproducer-w08-10-5 | followed: synthesis item 26 (`bash -lc` with a combined flag is an older hole, added) |
| S-w08-reproducer-w08-10-6 | parked: the cap's boundary is at nesting depth about 1,700, still far beyond ordinary use; stated in the verdict |
| S-w08-reproducer-w08-10-7 | parked: an intermediate commit with the old binary; the landed tree was checked and the installer's manifest check covers it |
| S-w08-reproducer-w08-14-1 | followed: synthesis item 26 (`+c` clusters still pass) |
| S-w08-reproducer-w08-14-2 | followed: synthesis item 26 (zsh `-O` and ksh `-o` misread) |
| S-w08-reproducer-w08-14-3 | parked: the 19 true cases still allowed are of other causes, already in item 26 |
| S-w08-reproducer-w08-14-4 | parked: a labelling slip in the verifier's own harness, fixed before its verdict |
| S-w08-research-pi-1 | followed: w08-c8 (times from a tool) |
| S-w08-research-pi-2 | followed: w08-c8 (selftests on the merged tree) |

## Notes

- **Close (`date` 05:07).** w08-c15 landed on the local `main` at 92a853f (lab merge 29551d8);
  smoke run from main's tree: 0 guard denials over the worker's 7 Bash calls, `bash -lc 'echo hi'`
  among them. Five more PI decision sections appended at the close (w03-c2, w04-c4, w04-c7,
  w04-c10, w07-c7), on explorer-w08-k's evidence: no claim reads "escalated: PI decides".
- **Spend at close (05:07):** this checkout USD 76.19 at list price against 1.30 at opening, so
  74.89 for this wave, a lower bound because the session is open; headless under
  `/private/tmp/murmuration-w08/` 21.54, exact. So **at least USD 96.43 of the 150** [source:
  `scripts/lab_status.py --spend` and `--project /private/tmp/murmuration-w08 --spend`].
- Models: every worker ran on its agent file's default (Sonnet); headless cells on haiku, except
  explorer-w08-f's effort arms (Sonnet), author-w08-3's and reproducer-w08-3's PI-like runs (Opus).
- Report: `__reports__/wave-08/research-pi/00-wave08_report_v0.md`; cost map
  `__reports__/wave-08/explorer-w08-h/lab_cost_map.html`; synthesis section "Wave 8", open items
  42–48.
- Branches of this wave: `w08-c1-rustbudget`, `w08-c2-shorthandback` (not merged), `w08-c3-compaction`
  (not merged; the hook stays out), `w08-c5-startnote` and `w08-c12-names`, `w08-c6-pi-practice`,
  `w08-c9-decisions`, `w08-c10-guardholes`, `w08-c14-shellc`; worktrees under
  `/private/tmp/murmuration-w08/*/wt` can be removed.
- **w08-c13 landed on the local `main` at 1511545** (lab merge fc2c2ca; binaries rebuilt from the
  merged sources with w08-c12 at 68ac4c1): selftests pass, a clean install gives the binary, the new
  binary went into this session's data folder before the main merge; smoke run from main's tree
  with ordinary commands (`ls`, `git status`, `$(date)`, a heredoc writing a file): all allowed,
  the file written. The guard refused my own Write of a test script holding the bypass flag (G4)
  and a Bash edit whose prose quoted a hole form (G2, one of the two prose denials w08-c13
  records); I did not route around either: the hole forms rest on reproducer-w08-10's offline
  cases, and these notes were made with the Edit tool, as the framing says.
- **w08-c11 landed on the local `main` at dc74371**, with PI decision sections appended to w01-c2,
  w01-c8, w02-c10 and w05-c1 (the four whose wave note names the label); `lab_status.py` shows them
  as `MEASURED (PI decided: restated, not re-verified)`.
- **w08-c12 landed on the local `main` at 3d5147a** (lab merge 1db2329): all selftests pass; a
  clean `git archive` installs the binary; the new binary installed into this session's data
  folder before the main merge (w08-c8's step). Smoke run from main's tree, two same-type
  explorers in one message with different budgets: each `start` line carries its own name and its
  own brief's budget (s1 USD 0.4 / 3 min, s2 0.5 / 4 min), consistent with its `end` line
  [source: `/private/tmp/murmuration-w08/research-pi/smoke2/lab/__statera__/harness.jsonl`]. In
  round 1 the same shape gave `source unknown` and the defaults.
- **w08-c6 and w08-c8 landed on the local `main` at 16b05a8** (not pushed): the brief items on
  sections and the hand-back limit, the skill's report-file line, and in `waves.md` the clock rule
  and the landing steps. w08-c7 was OVERSTATED (its title bundled two steps no failure supported)
  and is superseded by w08-c8 (SUPPORTED); the install step now cites the old binary's exit 2 on
  `budget` (`__reports__/wave-08/research-pi/old_binary_budget.txt`). Selftests pass on both trees.
- **w08-c4 landed on the local `main` at 1e0a81d** (not pushed), after reproducer-w08-1's
  SUPPORTED. The first merge (15d4c94) failed `budget.py --selftest` (S-w08-research-pi-2);
  author-w08-1 fixed the selftest only (d0ef374, manifest rebuilt for `budget.py`'s hash), merged
  at the second merge; all selftests pass on the lab branch and on main (budget, handback,
  lab_status, guard: 50 attacks denied, 28 ordinary allowed). Before merging to main I installed
  the new binary into this session's data folder (`~/.claude/plugins/data/murmuration-murmuration-local`,
  byte-equal to `bin/aarch64-apple-darwin/murmuration`; the old one kept at
  `/private/tmp/murmuration-w08/research-pi/murmuration.before-w08c4`). Smoke run from main's tree
  (`--plugin-dir` main, haiku, one explorer): start from the brief (B 0.5, T 3), the explorer
  report check denied once (item 8, as before), end with frac 0.13; the installer put the new
  binary, not the launcher, in `murmuration-inline` [source: `/private/tmp/murmuration-w08/research-pi/smoke/lab/__statera__/harness.jsonl`, `.verified`].
- 00:16, five same-second dispatches: names right in every `start` line (item 6's swap did not
  recur); the four explorers' start lines say `B 3.0, T 20.0, source unknown`, because their
  briefs' budgets differed and `budget.py` will not guess which pending record is whose; the
  brief's own lines replace them at the first check (`scripts/budget.py`, `handle_locked`,
  `brief_read`) [source: `__statera__/harness.jsonl` lines 1–5]. By design, not a defect.
- PI request 0 this session: 50,221 tokens, all written to the 1-hour cache (item 20/37's range was
  31–49k) [source: this session's transcript, first assistant record's `usage`].

closed: 2026-10-24
