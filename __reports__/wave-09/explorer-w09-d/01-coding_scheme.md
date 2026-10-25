# Coding scheme: what the PI reads and how it reacts to its team (explorer-w09-d)

Written and committed before any turn was coded. Data: PI main-thread transcripts of waves 1-3, 4, 5, 6, 7, 8
(`/private/tmp/murmuration-w09/explorer-w09-d/sessions.sh` lists the paths; transcripts are read only and not copied).
Wave 8 has two files, 70daedf1 (a fork that holds 1,204 of ad75be4f's 1,220 record ids and runs 43 minutes longer);
the wave-8 PI is read from 70daedf1.

## Units

**Step** = one PI request: one assistant message id with its text and tool calls (thinking is empty in the transcripts).

**Turn** = a trigger and everything the PI does until the next trigger. Triggers:

| code | trigger | how it shows in the transcript |
|:--|:--|:--|
| H | human prompt | user record, `origin.kind` human (or a command message) |
| B | worker hand-back | user record `origin.kind` peer, body "[Subagent hand-back]"; its task notice (attachment `queued_command`, same agent id) comes with it and is not a second trigger |
| N | task notice alone | user record `origin.kind` task-notification (agent id `a...` = an agent; `b...` = a background shell job) |
| X | other injected input | session-note system reminders, cross-session messages, compaction summaries |
| S | session start | the first turn; its length up to the first Agent dispatch is the **orientation stretch** |

A trigger is an *idle wake* when the previous turn ended in `end_turn`; otherwise it is *mid-turn* (it arrived while the PI worked and is absorbed).
A turn *ends with no action* when it holds no tool call (item 47's "82 requests without a tool call").

## Codes for every read (a PI call that brings text into its context)

| field | values |
|:--|:--|
| tool | Read-whole (no offset/limit), Read-part, Bash-view (`cat`/`sed -n`/`head`/`tail`), Bash-query (`jq`, `grep`, a script run over a file), lab_status, search (colgrep/Glob), git, ToolSearch |
| object | wave note, synthesis, framing, skill or reference, agent file, worker report, puzzle file, claim file, instrumenta script, plugin source, transcript or data, other |
| reason | `stated` (the PI's text in that step or the one before names why), `routine` (an orientation read the skill or agent file asks for), `unstated` |
| use (auto, proxy U1) | the path's file name appears later in the PI's own writes, dispatches or text; `none` otherwise |
| use (hand, sample only) | `acted` (a later dispatch, note, correction or decision depends on it), `echoed` (its content is only narrated back), `none` |
| repeat | path read before in the session, with or without a PI write to it in between |

## Codes for every hand-back wake (B) and notice (N)

A turn may carry several. Raw artifact = a file the worker produced or a record about its work (its report, puzzle file, claim file, data table, script, a transcript), not the hand-back text.

| code | meaning |
|:--|:--|
| H0 | no action: no tool call in the turn |
| H1 | opened a raw artifact in this turn |
| H1n | opened one in the next turn only (a delayed open) |
| H2 | wrote or edited a reassessment or wave-note entry |
| H3 | dispatched (Agent) |
| H4 | corrected or questioned the sender (SendMessage to it) |
| H5 | disposed of a puzzle in words (followed or set aside, with a reason) |
| H6 | status or spend check only (`lab_status`, `budget`) |
| H7 | told the user (text addressed to the user) |
| H8 | committed files |
| W | **taken at its word**: the PI dispatched, wrote a note, or decided from the hand-back and opened no raw artifact in this turn or the next |
| P | **raw changed the plan**: after a raw artifact the PI's next action or stated reading differs from the one the hand-back alone gave (hand-coded; quote the sentence) |
| Q | the PI narrows, doubts or contradicts something the hand-back states (quote) |

## Measured and conjectured

Counts over all turns of a session come from `__instrumenta__/w09d_turns.py` and are MEASURED (proxies named above).
Codes on the hand-read sample are MEASURED counts of my own coding; the reading of intent behind them is CONJECTURE.
Thinking is empty, so "why" comes only from the PI's visible text and from what it does next.

## Sample (target about 110 turns)

Stratified over waves 5-8 (about 25 each) with a few from waves 1-4: for each session the orientation stretch; all human prompts (up to 4);
hand-back wakes drawn to cover (a) no-action wakes, (b) wakes with a raw open, (c) wakes with a dispatch and no open, (d) the long wakes
(most steps), (e) a spread over the session's time; a few N wakes. Turns are extracted as summaries by script; the PI's text is cut at 500 characters a step.
