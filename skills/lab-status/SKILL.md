---
name: lab-status
description: Show the state of the Murmuration research lab in the current project: open puzzles, the current state of every claim, and token spend per agent and model. Run it as `/lab-status`.
user-invocable: true
allowed-tools: Bash(python3 *lab_status.py*)
---

# /lab-status

Prints what is open in the lab, what each claim currently stands at, and what the work has cost
so far. It only reads files; it changes nothing.

Run it from the project folder (the one that holds `__statera__/`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lab_status.py"
```

Show the output to the user as it is. Then add at most a few lines of your own: how many puzzles
are open and which, which claims need a decision, and anything printed on a `!` line.

## Reading the output

**Open puzzles** are puzzles raised in `__scrupuli__/` that no closed wave note has disposed of.
A closed wave note disposes of a puzzle when its id is followed by `followed:` or `parked:`.

**Claims** show one state each, the weakest of the verifiers' latest verdicts:

| State | Meaning |
|:--|:--|
| `unverified <LABEL>` | No verifier has given a verdict yet |
| `cited (not verified)` | A statement of prior work; CITED claims are not given to verifiers |
| `<LABEL>` | Every standing verdict is SUPPORTED or SOUND |
| `<LABEL> (gap)` | SOUND WITH GAP |
| `below <LABEL>: restate` | OVERSTATED or LABEL TOO STRONG: the claim may not be used at its label; the author files a new claim at a lower label with `supersedes:` and it is verified again |
| `<LABEL> (may restate higher)` | LABEL TOO WEAK: the author may file a superseding claim at the higher label |
| `withdrawn` | UNSUPPORTED or WRONG |
| `escalated: PI decides` | A verifier escalated; the PI reads the claim file and decides |
| `disputed: PI decides` | Two standing verdicts disagree; the PI resolves it by a further check or a stated decision |
| `superseded by <id>` | A later claim restates this one |

No note, report or synthesis states a claim above its current state.

**Warnings** are lines starting with `!`. They mean the script could not read something as
specified, and what it could not read is not counted: a puzzle heading that is not an id
(`S-wNN-<agent name>-<n>`, characters `a-z 0-9 -`), a duplicate puzzle id, a verdict section with
no `verdict:` line or with a value outside the verdict vocabulary, a claim with no `label:`, a
`supersedes:` that names no claim, a transcript that could not be read. Fix the file named in
the warning, or tell the user; do not ignore it.

**Spend** is read from Claude Code's transcripts for this project: tokens per agent and model,
with no prices applied. The `read:` line names the transcript folders used. If no transcripts
are found the output says so; do not estimate.

If the project has no `__statera__/` folder the script says there is no lab; tell the user to
start one with `/lab <question>`.
