# Waves

A wave is one round of exploration and hardening. Plan only the current wave; the next one comes
from what this one finds.

## Opening a wave

Write `__statera__/wave-NN.md` from [`../templates/wave.md`](../templates/wave.md). It opens with
the sentence of the user's (quoted from `user_words.md`) that this wave serves, then what does not
add up and why it is worth this wave. That is the reason for the wave, in plain words, not a task
list.

## During a wave

- **Explore with a portfolio.** When you cannot tell which direction is promising, send several
  explorers with loose briefs and small turn limits, in parallel, rather than one large bet.
- **Read raw material yourself.** For every agent that returns, open at least one of the raw
  artifacts it points to (a figure, a table, a log, its puzzle file), not only its summary.
- **Turn a hunch into a claim** when you judge it worth hardening. Dispatch an author and a
  verifier as a pair (see [`briefs.md`](briefs.md)): name both, tell each the other's name, and
  give both the claim id. The verifier works independently first, then they talk directly; you do
  not relay.
- **Use warm agents for corrections, fresh agents for checks.** Send a correction to the agent that
  did the work (`SendMessage`), since it has the context. A check always goes to an agent that did
  not do the work.
- **Your own facts are claims.** When your note states a result, a number or what an earlier wave
  established, give it a claim id and a source like any other claim.

## Closing a wave

1. Read the open puzzles (`/lab-status`): every puzzle raised so far that no closed wave has
   disposed of.
2. In the wave note, give each one a disposition:
   - `followed: <brief or claim id>` when it changed what the team does next;
   - `parked: <reason>` when you set it aside, with the reason in a sentence.
   Mentioning a puzzle is not following it.
3. List the claims of the wave with their current labels.
4. Mark the note `closed:` with the date. Closed notes are not edited again; corrections go into
   the next wave's note.

## Before the final synthesis

Show the user the open puzzles and what budget remains, and ask where the remaining effort should
go. Closing the story is their call. Then write the synthesis with every claim at its current
label, never above it.
