---
name: lab-status
description: Show the state of the Murmuration research lab in the current project: open puzzles, the current state of every claim, and spend in USD. Run it as `/lab-status`.
user-invocable: true
allowed-tools: Bash(python3 *lab_status.py*)
---

# /lab-status

Prints what is open in the lab, what each claim currently stands at, and what the work has cost
so far in USD. It only reads files; it changes nothing.

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
| `escalated: PI decides` | A verifier escalated and the claim file holds no decision section yet; the PI reads the claim file and decides |
| `disputed: PI decides` | Two standing verdicts disagree; the PI resolves it by a further check or a stated decision |
| `superseded by <id>` | A later claim restates this one |
| `<LABEL> (PI decided)` | The PI wrote a `## decision: research-pi` section `stands at <LABEL>` in the claim file; its `ref:` shows after the verdicts |
| `<LABEL> (PI decided: restated, not re-verified)` | The decision restated the claim at `<LABEL>` on the verifier's own figures; no verifier has read the restated wording |
| `withdrawn (PI decided)`, `superseded by <id> (PI decided)` | The PI withdrew the claim, or named the claim that replaces it |

No note, report or synthesis states a claim above its current state.

**Warnings** are lines starting with `!`. They mean the script could not read something as
specified, and what it could not read is not counted: a puzzle heading that is not an id
(`S-wNN-<agent name>-<n>`, characters `a-z 0-9 -`), a duplicate puzzle id, a verdict section with
no `verdict:` line or with a value outside the verdict vocabulary, a claim with no `label:`, a
`supersedes:` that names no claim, a PI decision section that is malformed or cannot be applied, a transcript that could not be read. Fix the file named in
the warning, or tell the user; do not ignore it.

**Spend** is read from Claude Code's transcripts and is in USD. The sessions counted are those
that ran in the project folder, below it, or in another git worktree of the same repository
(without `git`, only the project folder). A session that has ended is counted at the cost Claude
Code recorded for it (`exact`). A session still open is counted at list price from its
transcript (`at least`: helper-model calls are left out). The `where` table groups the sessions;
the agent table prices each agent's messages at list price, and a `+` after a figure means at
least: some of that subagent's output tokens are stored at their start-of-stream value, so
the figure is a lower bound. No `+` means every request of that agent was stored in full. If no
transcripts are found the output says so; do not estimate. `--spend [--project DIR]` prints only
this section, for a folder that is not a lab.

If the project has no `__statera__/` folder the script says there is no lab; tell the user to
start one with `/lab <question>`.
