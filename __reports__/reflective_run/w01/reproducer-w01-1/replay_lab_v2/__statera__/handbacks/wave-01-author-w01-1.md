# Hand-backs of wave-01-author-w01-1

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T12:00:12+09:00 | agent_id=ab6cc558229bad0e3 type=murmuration:author event=PostToolUse status=delivered bytes=8543 sha256=9a9ad95005eb
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

author-w01-1, claim w01-c1 is filed. The hook captured every subagent hand-back verbatim, in default and auto mode, on both binaries I could run. Nothing is committed. reproducer-w01-1 will message me.

## What the claim states (MEASURED)
A hook script of 69 executable lines (177 with docstrings and selftest) plus 2 hook entries (27 lines of JSON) saves each subagent's hand-back, byte for byte, to `__statera__/handbacks/wave-NN-<agent name>.md`. It uses `SubagentStop` and `PostToolUse` with matcher `SubagentHandback`. It does nothing outside a lab. The Write refusal covers only a narrow set of file names, and `__pondus__/w01-c1.md` and puzzle files are not affected.

- **Scope:** headless `claude -p --model haiku` runs of a scratch plugin with named subagents, on the installed CLI 2.1.302 and on the Desktop 2.1.299 binary run headless.
- **Not covered:** a live Desktop GUI session with the hook installed, and a hand-back that auto mode withholds.

**What would differ if the claim were false, and where I showed it:**

| If false | What I observed |
|:--|:--|
| The hook wrote nothing or altered the text | The file equals the raw hook payload in 7 of 7 runs that produced a hand-back, and also equals the platform's own subagent transcript. This includes a text with a forged `## hand-back` header line, `<task-notification>` and `<agent-message>` tags, `✓`, Japanese, a backslash and trailing spaces, and a 9 KB message. |
| One route would suffice for both modes | In auto mode `SubagentStop` carries no text; it is in `PostToolUse(SubagentHandback).tool_input.message`. Loading only the `SubagentStop` route (p6) leaves a loud `MISSING` section and no text. |
| The hook fired outside a lab | In p7, with no `__statera__/` and outside this worktree, no file and no folder were created. |
| A resumed agent lost its first hand-back | Two sections appeared in one file, in default and auto mode, on both binaries. |

## 1. What the Write refusal covers
- **The rule:** it is in the Write tool's `validateInput` in 2.1.295, 2.1.299 and 2.1.302. For a subagent, a Write whose basename matches `/^(REPORT|SUMMARY|FINDINGS|ANALYSIS).*\.md$/i` is refused. I read the regex from the binary with `grep -a -b -o -F "Subagents should return findings"` plus `dd`.
- **Scope of the rule:**
  - It applies to the Write tool only. Edit and Bash heredocs are not covered.
  - It tests the basename, so `notes/report.md` is refused.
  - It is anchored at the start of the basename, so `reports.md` and `report_head.md` are refused and `my_report.md` is allowed.
- **In this run's subagent transcripts:** 16 Write calls, 6 refused, 6 with a matching basename, no mismatch. That is six refusals, not five: d's `report_head.md` is the extra one, and c's `report.md` was refused twice. Agent e made no Write attempt on a report.
- **Headless test with 13 names:** the same on both binaries. Refused: `REPORT.md`, `report_head.md`, `Summary-notes.md`, `findings.md`, `ANALYSIS_2.md`, `FINDINGS.MD`, `reports.md`, `notes/report.md`. Allowed: `my_report.md`, `w01-c1.md`, `wave-01-author-w99-3.md`, `report.txt`, `analysis.py`. An Edit of an existing `REPORT-old.md` and a Bash heredoc to `REPORT-bash.md` both worked. The main thread wrote the same names with 0 refused.
- **Side effect:** in my first test a haiku subagent stopped at its first refusal and made none of its other calls (puzzle 1).

## 2. The hook
- **Where the text sits:** in default and bypass mode it is `SubagentStop.last_assistant_message`. In auto mode `PostToolUse(SubagentHandback)` fires first and carries `tool_input.message`; the later `SubagentStop` has no text.
- **File format:**
  - Each hand-back is a section `## hand-back <n> | <time> | agent_id=… type=… event=… bytes=N sha256=…`, so a reader can slice the text exactly.
  - One `os.write` per section means two agents never interleave.
  - The wave comes from the `-wNN-` in the agent name.
- **Agent name:** `.meta.json` `name`, then the brief's "Your name is X", then `<type>-<id>`. Both of the first two routes ran live.
- **Failure behaviour:** the same text twice in a row is written once. A `SubagentStop` with no text and no section written in the last 30 s writes a `MISSING` section. The script never blocks and always exits 0.
- **Replay of this run's 7 real hand-backs:** all 7 reach the lab file verbatim, with correct file names.
- **Against the PI's saved reports:**
  - 5 of 5 saved reports end with 652 or 807 characters that are not the agent's, starting at the closing `</agent-message>`.
  - 3 of 5 (b, d, f) contain 7, 4 and 8 neutralised `<\` tags where the agent wrote `<`, even though their header says "Text unchanged".
  - The neutralisation is lossy, so the agent's text cannot be recovered from those files.

## 3. Cost
- **Code:** 69 executable lines (177 with docstrings and selftest), no dependencies, no tokens.
- **Process cost:** about 43 ms per invocation. There are 2 invocations per hand-back in auto mode and 1 in default mode, so tens per study (30 hand-backs in the genesis and design sessions, 7 so far in this run).
- **Platform dependence:**
  - `SubagentStop.last_assistant_message` is documented, and I did not re-fetch the page.
  - The tool `SubagentHandback`, `tool_input.message` and `.meta.json` `name` are undocumented; the binary marks the hand-back machinery `@internal`.
- **If a field disappears:**
  - Text field gone from `SubagentStop`, or the tool renamed: a `MISSING` section per hand-back, so the loss is visible.
  - `SubagentStop` itself stops firing: nothing is written and nothing says so. Not tested.

## 4. How to run it
- **Full command** (12 headless haiku runs, about 4 minutes, USD 0.0768 by `total_cost_usd` in `results/summary.json`; about USD 0.10 more went on earlier exploratory runs that this command supersedes):
  `cd /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/author-w01-1 && ./run_all.sh > run_all.log 2>&1`
- **Quick command** (selftest plus two runs, about 1 minute, about USD 0.012):
  same folder, `./run_all.sh quick`
- **Seeds:** none exist for a model run. The checks compare the file against the hook's raw payload and the platform's transcript, never against expected model text.

## Against my own hunch
- **What the hook adds:** the PI already receives the hand-back in context, so the file adds verbatim fidelity and a durable copy, not new information.
- **Cheaper alternative for the refusal problem:** briefs can ask for a differently named file such as `<name>-notes.md`. I propose wording in the claim and did not apply it.
- **Risk:** the file holds unfiltered model output without the harness's "not a user message" frame. The harness also routes auto-mode hand-backs through a review with states `send`, `flagged` and `withheld`. The hook sees an identical `tool_response` for all of them, so it could store text the PI never received (puzzle 3).

## Files
- Claim head: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c1.md`
- Puzzles (9, none with new symbols): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-author-w01-1.md`
- Artifacts folder: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/author-w01-1/`
  - Prototype: `plugin/scripts/handback.py` (sha256 f6589f03c7dc) and `plugin/hooks/hooks.json`
  - Run drivers: `run_all.sh`, `run_probe.sh`, `collect.py`
  - Checkers: `check_handbacks.py`, `write_attempts.py`, `replay_run.py`
  - Results: `results/`, `replay_results.tsv`, `write_attempts.tsv`
  - Raw runs: `scratch/<run>/`, with `RAWLOG` holding the raw hook payloads and `out.json` the cost

## Puzzles
The three I would look at first:
- **S-w01-author-w01-1-3:** `SubagentHandback` goes through auto mode's review. The hook cannot tell a delivered report from a withheld one, and the file lacks the harness's frame.
- **S-w01-author-w01-1-4:** which directory a plugin hook gets in the Desktop app when it opened a worktree (`cwd` or `CLAUDE_PROJECT_DIR`). My script walks up parents to find a lab, which is also why the "not a lab" run had to sit outside this worktree.
- **S-w01-author-w01-1-8:** my own transcript holds 17 re-injections of the 63 KB skill listing in 226 records. By my estimate that is about 120 k tokens of repeated listing in a run that spent about 330 k tokens.

## hand-back 2 | 2026-10-19T12:00:12+09:00 | agent_id=ab6cc558229bad0e3 type=murmuration:author event=PostToolUse status=delivered bytes=3535 sha256=3a9b96ad4e0d
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

author-w01-1 on w01-c1, update after reproducer-w01-1's questions Q1-Q5. I answered them by message. I fixed the hook for Q1 and Q2, reran the full command, and updated the head of the claim and my puzzle file. Nothing is committed.

- **Q1 (drafts):**
  - The verifier's three-section case is real. In auto mode a resumed agent can end a turn in plain text, so `SubagentStop` carries text. The harness answers "[handback-send-enforce] Your report has not been delivered", and the agent then calls `SubagentHandback`.
  - My rerun produced the same sequence in p8_d299_auto_two (2.1.299). I had not seen it in about 40 earlier runs.
  - The hook now stores that text as `status=draft` and never counts it as a delivery. The file holds deliveries, plus drafts and gaps marked as such.
  - My first checker could not see this, because it compared the file only with the payloads the hook itself received.
- **Q2 (hook bugs):** both defects were real.
  - A hand-back that quoted a header line made the hook drop the next genuine one and misnumber. The hook now reads the file by hopping over each body with its `bytes=N`.
  - A lone surrogate made the write fail silently. It is now escaped and marked `delivered-escaped`.
  - The selftest has new cases for both.
- **Q3 (plugin registration):**
  - Runs under the worktree register `murmuration@murmuration-local` in `~/.claude/plugins/installed_plugins.json`. The cause is the worktree's `.claude/settings.local.json`, which `--setting-sources project` still finds from the scratch folders.
  - The real plugin did not take part. A stream-json run with hook events lists only my scratch plugin and the built-in `cc-plugin-*`, with `agent` None. A run outside the worktree leaves no entry.
  - I did not edit the file. This is now puzzle 10.
- **Q4 (title and scope):** I did not change what the claim states, since that is for the PI to decide through the verifier. I sent a restated title that names "headless" and the undocumented fields (`SubagentHandback`, `tool_input.message`, `meta.json` name). I updated only the numbers in the head.
- **Q5 (safety):**
  - Each section now carries a frame line saying it is model output to be read as data, and the file header says the same.
  - The harness's flag cannot be recorded, because the hook receives an identical `tool_response` in every case I could produce.
  - This is a mitigation, not a fix, and I did not test whether a model reading the file respects the frame.

**Revised evidence**
- The full command ran again on the revised hook: 12 runs, USD 0.0770 by `total_cost_usd`.
- The file equals the hook payloads in 7 of 7 runs that produced text. p8_d299_auto_two has 3 sections, one of them a draft.
- The replay over this run's real hand-backs now covers 35, all in the lab file verbatim.
- The hook is now 88 executable lines (212 with docstrings and selftest), sha256 e79dc3e0d970. The first version is kept as `handback_v1_f6589f03c7dc.py`.
- I asked reproducer-w01-1 to re-run `./run_all.sh quick` from the new files before any verdict.

**Not fixed:** any other exception inside the hook still loses a hand-back silently, for example a read-only folder or a permission error. I did not add a fallback log or test those cases.

Files, under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`:
- `__pondus__/w01-c1.md`
- `__scrupuli__/wave-01-author-w01-1.md` (puzzles 10 and 11 added)
- `__reports__/reflective_run/w01/author-w01-1/` (hook at `plugin/scripts/handback.py`)
