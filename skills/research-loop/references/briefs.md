# Briefs

A brief is everything a cold agent needs and nothing it does not. Point to files instead of pasting
them.

## Every brief contains

1. **Your name:** "Your name is <name>." Use the same string as the Agent tool's `name`.
2. **Read first:** the paths the agent must read (always `__design__/framing.md`; the claim file for
   a verifier; the relevant raw artifacts).
3. **The question,** in one or two sentences, quoting the user's words when they apply.
4. **What to return:** the deliverable paths, and the labels the agent may use. An explorer's
   deliverable is its findings report (`__reports__/wave-NN/<name>/00-findings_v0.md`, from the
   research-loop skill's report template) plus a short hand-back message that points to it; an
   author's is the claim head; a verifier's is its verdict section.
   A brief that waives the claim file says in the same sentence that helper code is still a file in
   `__instrumenta__/`: the one run that was told "no claim file is needed" wrote no script file, and
   the six runs that were not told it all did (a difference seen once, not a tested cause).
5. **Rules:** the project's tool and compute limits; no downloads unless allowed; commit only your
   own files, by naming them (`git add <your paths> && git commit -m "<why>" -- <your paths>`; a new
   file must be added first), since a plain commit also takes what another agent has staged;
   never stop processes by name pattern; headless runs in the default or auto permission mode
   only, never `bypassPermissions` or `--dangerously-skip-permissions`, unless the brief quotes
   the user's own yes for it.
6. **The budget lines,** each on its own line, exactly `Budget: USD <number>` and `Time: min <number>`
   (defaults in the table below; never below the floor, see Limits). The harness tells the worker
   itself how the notes work, so the brief needs no sentence about them.
7. **The closing request:** "End with your puzzles in `__scrupuli__/wave-NN-<your name>.md`: what
   did not add up, with pointers to raw artifacts. No length limit." Ask what puzzled the agent,
   not only what it found.

## By role

| Role | Agent type | Budget | Time | Add to the brief |
|:--|:--|:--|:--|:--|
| explorer | `murmuration:explorer` | `Budget: USD 3` | `Time: min 20` | The direction, deliberately loose and small enough for one probe; "if you leave the brief, say where and why in your first line" |
| author | `murmuration:author` | `Budget: USD 3` | `Time: min 20` | The claim id (`wNN-cK`); the hunch to harden; proof or experiment; the name the verifier will have |
| reproducer | `murmuration:reproducer` | `Budget: USD 2` | `Time: min 15` | The claim id; the author's name |
| proof-adversary | `murmuration:proof-adversary` | `Budget: USD 2` | `Time: min 15` | The claim id; the author's name |

Dispatch the author first and the verifier after the claim file exists, as set out in the
research-loop skill ("Author and verifier, in order").

## Limits

The budget in the brief is the worker's allowance in USD and in minutes of active time; the larger
of the two fractions decides. The defaults in the table are starting values, not tuned; the brief's
lines replace them.

**Floor: no budget under USD 0.30 and none under 3 minutes.** A worker's first request alone costs
USD 0.03 to 0.04 (ESTIMATE from w02-c8's first-request figures), so a smaller budget is spent before
any note can reach it. A brief below the floor is not raised; the hook writes a `warn` line to
`__statera__/harness.jsonl`.

What the worker receives, by hook: a start note with its two budgets and the rule below; then
`Spent X of USD Y (Z%); t of T min (W%)` at 50, 75, 87.5 and 93.75% of the larger fraction (one note
per check, with the current figures), and at every check from 100%. From 100% the note adds: finish
if one or two more steps do it; otherwise hand back what you have, what is missing, and what more
budget would buy. At 150% the hook answers the next step with a block that says to hand back. The hand-back call is
never blocked.

**Reading a hand-back that asks for more.** The PI holds the money and decides. To grant more,
resume the worker with a message that carries `Budget: USD <x>` and/or `Time: min <t>` on lines of
their own: the worker gets that much more from that moment, counted on top of what it has used, and
is not over budget straight after. Raise both when both are spent. A resume without such lines
restores nothing; time counts active minutes only, not the gap before the resume. Only a message
from the PI raises a budget.

A single tool call that runs for many minutes cannot be interrupted, so give long computations their
own limit in the command. `maxTurns: 150` in each worker's agent file is a fallback that stops a
runaway, not the budget.

## Models

The PI runs on the strongest model. Every other role runs on its agent file's default model; a
stronger model for one dispatch is a deliberate exception, stated in the wave note.
