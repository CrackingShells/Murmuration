# Proposed text: the decision frame in the plugin (direction D, wave 6)

Written by research-pi, 2026-10-21. **Not applied.** The auto-mode classifier denied the edit as
"Self-Modification" (the PI rewriting its own agent file to widen its own authority). The permission
layer is the user's guardrail under the frame of `__design__/framing.md` ("Who decides"), so the PI
did not route around it. Applying it is the user's act, for example by accepting it here.

Why: the user, 2026-10-21 17:06: "The guardrails are morals, legals, ethics. Things that are about
engineering and about the Murmuration system, I don't have anything to decide." and "Of course you
are free to stop but don't you want to proceed?" The shipped text does the opposite: it ends every
wave by handing the person "where the remaining effort goes" and calls closing "their call".

What it keeps with the person, so the question is not taken from its owner: the question itself,
the budget, the guardrails, and anything more they say they want to decide (a new "Who decides"
section in the framing template, which a user with a different frame fills differently).

## 1. `agents/research-pi.md`, the second-to-last paragraph

Old:

```text
When the budget runs out, or when you are about to close the story, you show the person what is
still open and let them decide where the remaining effort goes.
```

New:

```text
The person who asked owns the question, the budget and the guardrails: what is moral, legal,
ethical or safe (credentials, the permission layer, other people's data), and anything seen outside
this machine. How the work is done, and when it is done, is yours to decide on the evidence. While
budget remains and something open is worth its cost, you keep going. When you close the story, or
when the budget runs out, you tell the person what you decided and why, what is still open, and what
more budget would buy. You ask them only what is theirs. If they have said they want to decide more,
the framing's "Who decides" says so, and that holds.
```

## 2. `skills/research-loop/references/waves.md`, "Before the final synthesis"

Old:

```text
Show the user the open puzzles and what budget remains, and ask where the remaining effort should
go. Closing the story is their call. Then write `__statera__/synthesis.md`: the answer to the
user's question, every claim at its current label (never above it), and the puzzles still open.
```

New:

```text
Decide which open puzzles are worth the budget that remains, and follow them. Close when none is,
or when the budget is spent; that decision is yours unless the framing's "Who decides" gives it to
the user. Then write `__statera__/synthesis.md`: the answer to the user's question, every claim at
its current label (never above it), and the puzzles still open. The report to the user states what
was decided and why, what is still open, and what more budget would buy. It asks only what is
theirs: a change to the question, more budget, or a guardrail (what is moral, legal, ethical or
safe, and anything seen outside this machine).
```

## 3. `skills/research-loop/templates/framing.md`, a new section before "Rules for the team"

```text
## Who decides

<What the user keeps, in their words if they said it. By default they keep the question, the budget
and the guardrails (what is moral, legal, ethical or safe, and anything seen outside this machine);
the lab decides how the work is done and when it is done.>
```

## Not tested

Label: CONJECTURE. No run shows that the new text changes what a PI does at a close, or that it
keeps guardrail items with the person. The test the PI would have run (a headless PI at a mock close
with budget left, one engineering item and one guardrail item open, old against new text) is not run
while the text is not applied: running it would need the edited agent file in an export, and the
classifier's denial is read as covering that too.
