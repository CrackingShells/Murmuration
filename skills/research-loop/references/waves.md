# Waves

A wave is one round of exploration and hardening. Plan only the current wave; the next one comes
from what this one finds.

## Opening a wave

Write `__statera__/wave-NN.md` from the wave template (its full path is listed in the
research-loop skill, under "For the PI"). The first wave note already exists after `/lab`; replace
its placeholder text. A note opens with the sentence of the user's
(quoted from `__statera__/user_words.md`) that this wave serves, then what does not add up and why
it is worth this wave: the reason for the wave in plain words, not a task list.

## During a wave

- **Explore with a portfolio.** When you cannot tell which direction is promising, send several
  explorers in parallel with small, well-scoped briefs rather than one large bet. Give each a
  unique name (`explorer-w03-a`, `explorer-w03-b`, …). An explorer that reaches its budget
  hands back what it covered, what it did not, and what more budget would buy. Read that request:
  you hold the money, and you decide whether to resume the worker with a raise (`Budget:` and
  `Time:` lines in the message; see `briefs.md`) or to let the hand-back stand.
- **Reassess when results come back.** Each time a batch of agents returns, write one entry under
  the wave note's "Reassessments": what came back, what it changes, and what you drop. A plan that
  no result has changed by mid-wave is a sign that you are following a list, not the evidence.
- **Read raw material yourself.** For every agent that returns, open at least one raw artifact it
  points to (a figure, a table, a log, its puzzle file), not only its summary.
- **Turn a hunch into a claim** when you judge it worth hardening. Assign the claim id
  (`wNN-cK`), dispatch the author, then the verifier, in the order given in the research-loop
  skill ("Author and verifier, in order"). You do not relay their conversation; it is logged in
  the claim file.
- **Use warm agents for corrections, fresh agents for checks.** Send a correction to the agent that
  did the work (`SendMessage` to its name). A check always goes to an agent that did not do the
  work.
- **Your own facts are claims.** When your note states a result, a number or what an earlier wave
  established, file it as a claim (`wNN-cK`, `author: research-pi`) with its source. Give it to a
  verifier when later work depends on it.

## Closing a wave

1. Run `/lab-status` and read the open puzzles: every puzzle raised so far that no closed wave
   has disposed of.
2. In the wave note's disposition table, give each one a disposition:
   - `followed: <brief or claim id>` when it changed what the team does next;
   - `parked: <reason>` when you set it aside, with the reason in a sentence.
   Write the puzzle id followed by `followed:` or `parked:`; any other wording leaves the puzzle
   open. Mentioning a puzzle is not following it.
3. List the claims of the wave with their current labels from `/lab-status`.
4. End the note with the line `closed: YYYY-MM-DD`, using the real date (replace the template's
   placeholder line if the note still has one). A note counts as closed only when that line
   carries a real date; `/lab-status` treats any other note as still
   open. Closed notes are not edited again; corrections go into the next wave's note.

## Before the final synthesis

Show the user the open puzzles and what budget remains, and ask where the remaining effort should
go. Closing the story is their call. Then write `__statera__/synthesis.md`: the answer to the
user's question, every claim at its current label (never above it), and the puzzles still open.
