---
name: research-loop
description: Working procedures of a Murmuration research team — roles and agent types, how to name agents and identifiers, the formats of claims, verdicts, puzzles and wave notes, the claim labels and what each verdict does to them, and the order in which an author and a verifier work. Load at the start of every session in a Murmuration lab project, and before writing a brief, a claim, a verdict, a puzzle or a wave note.
---

# Research loop

A Murmuration team works in waves inside a lab project. The principal investigator (PI) explores
and decides which hunches become claims. Authors turn hunches into labelled claims. Verifiers
check claims independently, then question their author directly. Everyone records what puzzles
them. All files are plain markdown, one file per writer, so several agents can work at once without
touching each other's files.

## Roles

| Role | Agent type (for the Agent tool) | Writes |
|:--|:--|:--|
| PI | the main session (`murmuration:research-pi`) | `__design__/framing.md`, wave notes, its own claims and puzzles, the synthesis |
| explorer | `murmuration:explorer` | its findings report and the raw artifacts beside it; its puzzle file |
| author | `murmuration:author` | the head of a claim file; its puzzle file |
| verifier of empirical claims | `murmuration:reproducer` | its verdict section in a claim file; its puzzle file |
| verifier of proofs and exact claims | `murmuration:proof-adversary` | its verdict section in a claim file; its puzzle file |

## Names and identifiers

Every dispatch gets a unique name, passed as the Agent tool's `name` and stated in the brief ("Your
name is …"). Use the characters `a-z`, `0-9` and `-` only.

| Identifier | Form | Example |
|:--|:--|:--|
| agent name | `<role>-wNN-<letter or number>` | `explorer-w03-b`, `author-w03-2`, `reproducer-w03-2` |
| wave | `wave-NN` | `wave-03` |
| claim | `wNN-cK`, assigned by the PI, numbered within the wave (the PI's own claims too) | `w03-c2` |
| puzzle | `S-wNN-<agent name>-<n>`, numbered by its writer | `S-w03-explorer-w03-b-1` |

## Files

| Path | Holds |
|:--|:--|
| `__design__/framing.md` | The question, notation, scope and rules for the team |
| `__statera__/user_words.md` | The user's prompts, verbatim and dated. Written automatically; agents never edit it |
| `__statera__/wave-NN.md` | One note per wave, written by the PI |
| `__statera__/synthesis.md` | The final synthesis, written by the PI |
| `__reports__/wave-NN/<agent name>/NN-<type>_vN.md` | An explorer's findings report (`NN-findings_vN.md`, from `templates/report_findings.md`), with its scripts and raw artifacts in the same folder |
| `__pondus__/<claim-id>.md` | One file per claim: the author's head, then one section per verifier |
| `__scrupuli__/wave-NN-<agent name>.md` | That agent's puzzles for that wave |

Add to your own files; never edit another writer's file or section.

### Claim file

```markdown
# w03-c2: <the statement, one sentence>

label: MEASURED
scope: <what this claim covers, in one sentence; and one thing it does not>
evidence: code/run_all.py@3f2a1c9, data/derived/results.csv@3f2a1c9
method: <proof: path or inline argument | experiment: full command, quick command, seeds, cost>
author: author-w03-2
supersedes: <claim id, only when this claim restates an earlier one>

## verdict: reproducer-w03-2

### independent result
<what the verifier found before any exchange with the author>

### exchange
- Q: <question to the author> — A: <the author's answer, or "no answer">

verdict: OVERSTATED
reason: <one or two sentences>
changed_by: <path of a new artifact, only if the verdict changed after the exchange>
```

The author writes everything above the first `## verdict:` heading. A verifier appends its section
with a shell append (`cat >> __pondus__/<claim-id>.md <<'EOF'` … `EOF`), so it never rewrites the
author's part or another verifier's. Each verifier writes one
section that starts with `## verdict: <its name>` and uses `###` subheadings only. The last line
of the section that starts with `verdict:` is the verdict (a revision adds a new `verdict:` line and a
`changed_by:` line below the earlier one), so no line under `### exchange` may start with `verdict:`.

### Puzzle file

```markdown
## S-w03-explorer-w03-b-1
<what did not add up, in plain words>
refs: <paths to the raw artifacts: figure, table rows, log lines>
```

Number your puzzles in order within the file; when you are resumed, continue after your last
number. Dispositions are not written here; the PI records them in the wave note when the wave
closes.

### Report file

An explorer's deliverable is one findings report plus a short hand-back message that points to it
(the path, then what is not covered). Copy the template
`${CLAUDE_PLUGIN_ROOT}/skills/research-loop/templates/report_findings.md`, drop its first comment
line, and save it as `__reports__/wave-NN/<your name>/NN-findings_vN.md`, for example
`__reports__/wave-03/explorer-w03-c/00-findings_v0.md`. `NN` counts your reports from `00`; `vN`
counts rewrites of one report. The name must start with digits: the platform refuses a Write to a
file whose name starts with `REPORT`, `SUMMARY`, `FINDINGS` or `ANALYSIS`. The report uses the
labels below. Claims remain the author's deliverable and verdicts the verifier's; neither is a
report.

## Labels

Label by what was run, not by what is believed.

| Label | Means | Requires |
|:--|:--|:--|
| THEOREM | Proved | The proof, every step checkable (`method:`) |
| CHECKED | Verified exhaustively or numerically, not proved | The instance sizes |
| MEASURED | A number produced by code that ran end to end on data | The full and quick commands, seeds, commit |
| ESTIMATE | A formula evaluated on data; not an achieved result | The formula and its inputs |
| CONJECTURE | A pattern seen, not proved | What was observed, at which sizes |
| CITED | A statement of prior work | The identifier actually fetched, or `UNVERIFIED` |

CITED statements are not given to a verifier: they stand as cited, with their identifier or marked
UNVERIFIED. Every factual statement in a note or report carries a source (`[source: path@commit]`)
or a declared assumption (`[assumption: why]`).
A spend figure shown to a worker is the whole session's, not its own, so a worker does not report spend or
budget use; those come from `__statera__/harness.jsonl` or `/lab-status`. A worker that hands back past
its budget says what it has, what is missing and what more budget would buy; the PI reads that request
and decides whether to resume it with a raise (`briefs.md`, Limits).

### Verdicts and the current label

| Verifier | Verdicts |
|:--|:--|
| reproducer | SUPPORTED · OVERSTATED (true but stated more strongly than the evidence) · UNSUPPORTED · ESCALATE |
| proof-adversary | SOUND · SOUND WITH GAP · WRONG · LABEL TOO STRONG · LABEL TOO WEAK · ESCALATE |

Each verifier's latest verdict is its standing verdict. The current label of a claim, as
`/lab-status` shows it:

| State | When |
|:--|:--|
| `unverified <LABEL>` | No verdict yet |
| `cited (not verified)` | A CITED claim; it stands on its identifier |
| `<LABEL>` | Every standing verdict is SUPPORTED or SOUND |
| `<LABEL> (gap)` | SOUND WITH GAP |
| `below <LABEL>: restate` | OVERSTATED or LABEL TOO STRONG. The claim may not be used at its label; the author files a new claim at a lower label with `supersedes:`, and it is verified again |
| `<LABEL> (may restate higher)` | LABEL TOO WEAK. The author may file a superseding claim at the higher label |
| `withdrawn` | UNSUPPORTED or WRONG |
| `escalated: PI decides` | Any standing ESCALATE, whatever the other verdicts. The PI reads the claim file, including its exchange, and decides |
| `disputed: PI decides` | Two standing verdicts disagree. LABEL TOO WEAK next to SUPPORTED or SOUND is not a disagreement |
| `superseded by <id>` | A later claim restates this one |

No note, report or synthesis states a claim above its current label.

## Author and verifier, in order

1. The PI dispatches the author (`murmuration:author`, named, for example `author-w03-2`) with the
   hunch, the claim id to use, and the verifier's future name.
2. The author files the claim head, then finishes. It can be resumed later by a message.
3. The PI dispatches the verifier (`murmuration:reproducer` or `murmuration:proof-adversary`,
   named, for example `reproducer-w03-2`) with the claim id and the author's name.
4. The verifier reads only the claim head and the evidence it points to, writes its
   `### independent result`, and only then questions the author with `SendMessage` (to the
   author's name). Each message resumes the author, and the author answers the same way.
5. The verifier logs each question and answer under `### exchange`, then closes with its verdict.
   A verdict changes after the exchange only by pointing to a new artifact (`changed_by:`).
6. The verifier escalates when the author wants to change what the claim states, or when the
   exchange stops converging.

When the author is the PI (`author: research-pi`), the verifier sends its questions to `main`.
If a message cannot be delivered or gets no answer, the verifier logs the question with "no answer"
and gives the verdict the evidence supports.

## For the PI

| When | Read |
|:--|:--|
| At the start of every session | `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/references/working_defaults.md` |
| Planning, running or closing a wave | `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/references/waves.md`, and the template `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/templates/wave.md` |
| Writing a brief | `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/references/briefs.md` |
| Filling the framing | `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/templates/framing.md` |
