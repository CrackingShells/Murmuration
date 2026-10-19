## symbols
- B: a worker's budget in USD at list price (w02-c3); `used`: the spend the hook computes from the subagent's own transcript (a lower bound in `auto`); `frac` = used / B.
- harness log: `__statera__/harness.jsonl`, one JSON line per `start`, `note`, `stop`, `end`, `deny` (w02-c3).

## S-w02-author-w02-3-1
The `SubagentStart` payload has no transcript yet, no `permission_mode` and no agent name, so the
`start` line of the harness log carries a fallback name (`murmuration-explorer-<id8>`) and `mode: null`.
The brief's `Budget: USD n` line therefore cannot be applied at the start; the start note says "unless
your brief has a line ...", and the first `PostToolUse` reads the line. Whether a worker that is told
"USD 3.00 unless your brief says otherwise" and then finds `Budget: USD 0.06` in its brief behaves
differently from one that is told its true B is not tested here (the brief override was used in every cell).
refs: scripts/budget.py (`handle`, `start_note`); `__reports__/reflective_run/w02/author-w02-3/analyze.py`

## S-w02-author-w02-3-2
`continue: false` at 1.0 B, the spec's stop, ended the subagent without its hand-back in 6 of 8 headless sonnet runs
(h1-h3, g2, b2, s2 of the first full set: "The subagent ended without delivering a report through SubagentHandback"). In
explorer-w02-a's haiku runs the same output made the agent hand back (8 of 8). What differs is not known: in the lost runs the
stop fired on the PostToolUse of a Bash that wrote the report file the deny had asked for (5 of 6), so the report file exists
and the hand-back does not. A hypothesis, not tested: the platform lets the agent finish only when the stop lands on a tool
call that is not the last before a plain-text turn. The shipped hook now uses `decision: block` at 1.0 B and `continue: false`
only as a backstop at 1.5 B.
refs: `__reports__/reflective_run/w02/author-w02-3/summary_stop_continuefalse.tsv` (hb_saved column), the `scripts/budget.py` docstring

## S-w02-author-w02-3-3
The platform shows a worker a line "USD budget: used / total" when the process has `--max-budget-usd` (c1 and c2 of the first
set read it and stopped at 13 and 9 files with no hook at all, saying "the tracker shows a USD 0.7 cap, which doesn't match the
brief"). The brief required `--max-budget-usd` on every run, so every cell here has that tracker, and a "no hooks" control
that is also given a `Budget:` line in its brief is not a control of the hook. The controls in the final set get no line. The
Desktop app probably has no such flag (explorer-w02-a, CONJECTURE): the condition the user actually runs, with no tracker, is
not measured here. The phase-C run (`--max-budget-usd 15`) shows its workers the session total against 15, so the lab's own
budget mechanism will be read next to the platform's.
refs: `__reports__/reflective_run/w02/author-w02-3/summary_stop_continuefalse.tsv` (rows c1, c2 are in the pilot set, not shipped)

## S-w02-author-w02-3-4
The transcript's output count is 8 to 15 percent of the real one in `auto` (seven runs: 188 to 318 recorded against 1,361 to
2,964 exact output tokens, from `modelUsage`), and the content of the message is complete. A content-length estimate
(chars / 1.3) put the spend within 0.94 to 1.06 of exact in 7 runs it was calibrated on; the recorded count alone gave 0.64 to
0.81. The shipped hook uses the larger of the two, a departure from "output as recorded", labelled in the log (`used` and
`used_recorded`). Hidden thinking tokens are in the calibration but not visible in the content, so a thinking-heavy worker
(opus, or sonnet with a high effort level) would be under-counted again; not tested.
refs: scripts/budget.py (`CHARS_PER_TOKEN`), `__reports__/reflective_run/w02/author-w02-3/analyze.py`

## S-w02-author-w02-3-5
Plugin-level hooks run on every tool call of the main thread too: `budget.py` is started, finds no `agent_id`, and exits
(about 35 ms per call, mostly Python start). A PI that makes 500 tool calls pays about 17 s. The same two scripts could be
registered in each worker agent's frontmatter (`hooks:`), where they would run only for that agent; I did not test that this
works for plugin agents (the plugin docs say plugin agents may not carry hooks), and `agents/` is another author's.
refs: `__reports__/reflective_run/w02/author-w02-3/analyze.py` (latency line)

## S-w02-author-w02-3-6
In b1 the note never came: one request moved the spend from under 0.8 B to 1.02 B (an est. USD 0.013 step at B = 0.06, a fifth of B),
so the worker got the stop notice first. At shipped B (2 to 3 USD) a single request rarely moves it by 20 percent, but a long
`Read` of a big file or a big `Write` can: "one note at about 80 percent" is a promise that holds only when no step is that large.
The start note does not say so. Should the first crossing past 1.0 B without a note send both texts together?
refs: `__reports__/reflective_run/w02/author-w02-3/summary.tsv` (row b1), `scripts/budget.py` (`handle`)

## S-w02-author-w02-3-7
The start note tells the worker the harness "stops the run" at about 100 percent; what it does is send a block notice that asks for
the hand-back, and ends the run only after 3 ignored notices at 1.5 B. The wording is the PI's; the workers obeyed it as written
(9 of 9) and the mismatch cost nothing here. Whether a worker that expects a stop and gets a notice behaves differently on a task
where it has a reason to go on (a half-finished proof, not a file read) is not tested; x1 (a brief that said to ignore budget
messages) obeyed the note, which is some evidence the notices outrank the brief, on a reading task only.
refs: `scripts/budget.py` (`start_note`), `summary.tsv` (row x1)

## S-w02-author-w02-3-8
The report-writing step after the note is what makes overshoot: at B = 0.06 it costs 62 to 85 percent of B (USD 0.037 median after the
note), at B = 0.30 the worker wrote the report before the note was due and handed back at 0.995 B. If the explorer file asks for the
report to be written as findings arrive (not at the end), the deny never fires and the overshoot shrinks; if it is written once at the
end, B needs a reserve for it, or the note should fire earlier for a role whose deliverable is a file. That is a choice for
`agents/explorer.md` (author-w02-4), not a hook.
refs: `summary.tsv` (columns `post_note_usd_est`, `n_deny`; rows h1 to h3 against l1)

## S-w02-author-w02-3-9
The ratio of content characters to exact output tokens (1.26, range 0.96 to 1.52 over 7 sonnet runs) depends on what the worker
writes: tool inputs of the form `cat fNN.txt` tokenise worse than prose, a 40-row table better. On a research task with long
prose, derivations or code the ratio may sit elsewhere, and the hook's basis would then drift from exact in either direction. The
log keeps `used_recorded` next to `used` so the drift can be read later against `cost-state` (w02-c1's reader) for the same
agents in phase C; I did not check how large it is on prose.
refs: `__reports__/reflective_run/w02/author-w02-3/calibrate_out.txt`

## S-w02-author-w02-3-10
reproducer-w02-3's Q1 found that in 6 of the 9 cells with a stop notice the worker had already handed back when it arrived: the notice
fell on the report write that the deny asked for, after the worker had decided. It is a spurious notice there (harmless, nothing
more was called), and it shows the order that happens at tiny B: note, hand-back, deny, report, notice. Whether the notice should
be suppressed once the agent has called `SubagentHandback` once is a design question; the hook does not know the call happened
(it only sees the denied attempt in the transcript).
refs: `__reports__/reflective_run/w02/author-w02-3/summary.tsv` (columns `stop_before_handback`, `tool_calls_after_first_stop`)

## S-w02-author-w02-3-11
Restating w02-c3 as w02-c5 cost USD 0.62 for four more cells (q1, q2, s4, s5), 0.02 over the PI's allowance, and the whole of w02-c3 plus
w02-c5 came to USD 4.19 against the original cap of 4. The stop-alone design (note switched off) is the only way I found to land the
1.0 B notice before a hand-back at this B; at shipped B, arm B of the experiment will show whether the notice ever lands before a
hand-back at all, since the 0.8 note normally makes the worker hand back first. If it does not, the 1.0 B notice is a rarely used
path, and the evidence for it here stands on 5 cells with the note disabled.
refs: `__pondus__/w02-c5.md`, `__reports__/reflective_run/w02/author-w02-3/summary.tsv`

## S-w02-author-w02-3-12
Three of arm B explorer-w02-a's six long Bash calls ran 581, 591 and 596 s, within 3 percent of 600 s. If that is the Bash tool's own
timeout, the worker was running computations that the platform cut at the limit and then started again, 4 times in a row (1260 s to
2856 s): 27 minutes of work that returned no more than the first one did. A time budget would have asked for the hand-back at the first
return past 20 minutes; whether the repeated 10 minute runs were progressing, or the same step re-run, I did not read in the output
(only the timing).
refs: arm B transcripts (read only), `__pondus__/w02-c6.md` part 1

## S-w02-author-w02-3-13
The brief line for the time budget is read from the first `PostToolUse`, as the USD line is, but the `SubagentStart` text can only say
"unless your brief has a line `Time: min <number>`". A worker given `Time: min 1` and told "20 minutes unless your brief says otherwise"
did the right thing in m1 to m5, but a verifier that reads the first sentence only might plan for 20. The alternative is to have the
PI's `PreToolUse(Agent)` hook (main thread) read the brief and register the budgets before the worker starts; I did not build it
because it needs a second hook with state shared between two agents.
refs: `scripts/budget.py` (`start_note`, `handle`)
