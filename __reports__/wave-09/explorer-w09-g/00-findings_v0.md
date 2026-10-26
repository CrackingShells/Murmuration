---
type: findings
wave: wave-09
author: explorer-w09-g
date: 2026-10-26
version: v0
decision-required: confirm
---

# How the 41 non-hand-back transcript ends ended: findings (v0)

Left the brief in three places, each stated where it matters: (1) the population is 40 rows now, not 41 (rows below); (2) I also scanned the lab folders that f's glob leaves out, because the maxTurns losses item 15 is about are there; (3) I did not read the PI transcript around each end in waves 3-9, because the scans found no loss there to look up.

## Result
- MEASURED: of f's 41, 37 had ended and 3 are live workers of this wave (explorer-w09-c, -g, -h; harness.jsonl has a `start`, no `end`); f's 41 was taken while c, d, e and f itself were still running (CONJECTURE for the exact four: d and e ended on a hand-back at 14:47:40Z and 14:50:48Z, f's own file at 14:38:51Z) [source: __reports__/wave-09/explorer-w09-g/41-rows.md; __statera__/harness.jsonl].
- MEASURED: the 37 ended rows split into: 27 probe workers (agent types without a SubagentHandback tool) that finished on a final text the platform delivered; 2 lab workers that had already handed back and then ended on trailing text; 7 explorers ended by the budget hook's `continue: false`; 1 explorer ended by the headless print-mode 10-minute wait ceiling. Hit `maxTurns`: 0. API error: 0. Budget `decision: block`: 0. Stopped by the PI or the user: 0 (the one `[Request interrupted by user for tool use]` is the platform's ceiling, row 31) [source: 41-rows.md; f_all.tsv].
- MEASURED: 8 of the 37 lost their hand-back message (7 + 1). All 8 are 2026-10-19 headless experiment cells of wave 2 (explorers run in scratch labs under a budget design later replaced); none is a worker of waves 3 to 9 [source: 41-rows.md rows 28-35; __pondus__/w02-c3.md R5, CITED]. Of those 8 the report file existed on disk for 6 (b2, g2, h1, h2, h3, s3), not for 2 (s2 `ab92f515`, explorer-w02-a) [source: transcripts, Write/Bash of `00-findings_v0.md` with a non-error result].
- MEASURED: the PI-side parents noticed 7 of the 8 through the platform's notice ("ended without delivering a report through SubagentHandback"); the 8th (explorer-w02-a) got no notice, the parent session had already ended. The PI session logged the headless ceiling as S-w02-research-pi-2 at 04:23:22Z, as the loss of the arm's ending, not as a lost explorer report [source: notices.tsv; ab96c5ed.jsonl 04:22:41 to 04:23:28; __scrupuli__/wave-02-research-pi.md].
- MEASURED (wider scan, not asked): over the whole lab population (1,188 subagent files in lab projects, 575 of them typed `murmuration:*`) 24 agents received a platform notice "stopped at its N-turn limit" or "ended without delivering a report": 14 were resumed and delivered, 10 were not (the 7 budget-stop explorers, 1 wave-2 `worker`, and 2 explorers `ux-c1`, `ux-c2` that reached 150 tool calls). After 2026-10-20T01:18Z no parent session contains such a notice [source: __reports__/wave-09/explorer-w09-g/notices.tsv; `__instrumenta__/w09g_notices.py`].
- MEASURED: maxTurns losses in the lab are 6 events: four explorers at the old 60-turn limit (explorer-w01-b, -c, -d, explorer-w02-b; all resumed by SendMessage and delivered within 67 to 108 s of the notice) and two at 150 (`ux-c1`, `ux-c2`, wave-4 cells with a 150-file, one-`cat`-per-call task; not recovered). Item 15's "no trace" is half right: the lab's own files have none (CITED, w04-c3), the platform's notice and the transcript do (last record is the 150th tool result; 150 tool-use messages) [source: notices.tsv; transcripts `a9a115dc`, `a6c3cbe7` in `-private-tmp-murmuration-w04-author-w04-2-runs-ux-c{1,2}-lab`].

## Table
Per-class summary; the row-by-row table is `__reports__/wave-09/explorer-w09-g/41-rows.md`.

| Class | n | Evidence in the transcript | Delivered? | Deliverable lost? | PI or parent noticed? | Label |
|:--|--:|:--|:--|:--|:--|:--|
| final text, agent type without SubagentHandback (w02 probes: `worker`, `w02b:*`) | 27 | last record assistant text, `stop_reason: end_turn`; parent's tool result starts "[Subagent hand-back] The text below is the final report" (or the task notification, quoted by the parent) | yes | no | n/a | MEASURED |
| final text after an earlier delivered hand-back (author-w04-4 `ab28dda4`, reproducer-w08-5 `ac542562`) | 2 | harness.jsonl `end` lines at each stop; handbacks file ends on a `status=draft` section; parent notice "This agent's report was delivered to you ... not repeated here" | the content, yes (SendMessage and earlier hand-back); the trailing text, no | no | n/a (nothing missing); the reproducer's addendum reached `main` as an agent message at 20:20:47Z | MEASURED; "content duplicates the SendMessage" CHECKED for author-w04-4 draft 2 only |
| budget `continue: false` at 1.0 B (wave-2 first design) | 7 | `hook_stopped_continuation` attachment after the last tool result ("your USD 0.06 budget is used ... the run ends here"); 6 of 7 had a hand-back attempt denied by the report check just before (`hbres = denied-by-hook`) | no | hand-back message: 7 of 7; report file: 1 of 7 (s2) | parent: yes ("no report came back"), author-w02-3: yes (w02-c3 R5, "6 of 8 lost"), the shipped stop became `decision: block` | MEASURED |
| print-mode wait ceiling (explorer-w02-a `a209ed43`) | 1 | Bash `timeout: 600000` rejected "The user doesn't want to proceed", then `[Request interrupted by user for tool use]`, 10 min after the headless parent's last turn | no | yes, nothing on disk | arm ending yes; the explorer's loss no | MEASURED |
| live (explorer-w09-c, -g, -h) | 3 | no `end` in harness.jsonl; file written within minutes | not ended | not ended | n/a | MEASURED |
| maxTurns (not in the 41; wave-4 cells ux-c1, ux-c2) | 2 | 150 tool-use messages, last record the 150th tool result, platform notice "stopped at its 150-turn limit" | no | yes (nothing on disk; task was a list) | parent yes ("hit its 150-turn limit"); w04-c3 uses it only exploratorily | MEASURED |

Why "last tool call" misleads (MEASURED): the metric reads the last `tool_use` anywhere, not the last record. It calls 27 clean final-text ends "non-hand-back" because those agent types have no hand-back tool, and it calls 14 agents (13 in f's glob) "hand-back" that the platform had stopped at a limit and the PI then resumed (all 2026-10-19, rows in notices.tsv with `later_handback_delivered = yes`) [source: `__instrumenta__/w09g_classify.py` with `all`; notices.tsv].

Hand-back files, all six worktrees (MEASURED, grep of `status=` in `__statera__/handbacks/`): 173 delivered, 16 `draft`; 12 drafts are followed by a delivered section of the same agent (the author called SubagentHandback again within 7 to 13 s), 4 are not, and those 4 are the two agents above (author-w04-4 drafts 2 and 3, reproducer-w08-5 drafts 3 and 4). Every `start` in harness.jsonl of the five finished worktrees has an `end`; the open starts are the 3 live rows [source: `__statera__/harness.jsonl` and the five sibling worktrees].

## Worst-fitting case
The story: nothing in the lab proper was lost, and what was lost was seen. The row that fits it worst is **explorer-w02-a, `a209ed43`** (row 31): it ended with no platform notice at all, because the headless parent had already finished; its last tool result says "The user doesn't want to proceed with this tool use", which reads like a human refusal and is the platform stopping background work at the 10-minute ceiling (the PI's puzzle S-w02-research-pi-2 quotes the ceiling message from the arm's stderr, not from this transcript). It had written no report file. The PI recorded the ceiling as the lab's lost synthesis, not this explorer's lost output.
The second-worst is the 7 budget-stopped explorers: the parent said "no report came back" for all 7, yet the report file sat on disk for 6 of them (b2 wrote `00-findings_v0.md` by Bash after the report check's deny, then the hook ended the run). The PI-side belief of loss was wrong for 6 of 7 until someone listed the folder. The typical row, for contrast: any of the 27 probe workers, whose last text reached the parent verbatim.
For item 15 specifically the worst case is `ux-c1`/`ux-c2`: n = 2, a task built to overrun (150 files, one `cat` each), no on-disk trace in the lab.

## Not covered
- The PI transcripts of waves 3 to 9 were not read around each end: the scans (notices, harness `start`/`end`, handbacks `status=`) found no loss there to look up. A loss that leaves none of those three traces (a platform notice worded differently in 2.1.30x, a parent session outside the lab project folders) would not appear. [assumption: the notice wording seen on 2.1.302 is the one later versions use; no later notice of any kind was found to check against.]
- The 1,236 subagent files of non-lab projects, and parents whose session file I did not match (`no-trace` in the classifier's parent column: the column is best effort and is not used for any count above).
- Whether the trailing drafts of reproducer-w08-5 carried content that was not also sent by message (checked only author-w04-4 draft 2 and reproducer draft 4 by reading).
- f's "306": I get 312 transcripts with f's glob (`*Murmuration-murmuration-*`, excluding `---reports`), i.e. 6 more than f, plausibly the workers started since f counted; not resolved.
- No `claude` run, no maxTurns probe: what a worker does at turn 150 in the shipped plugin today is untested here.

## Steering questions
- [now] Item 15 asks for "a fix, then a check". The evidence says the lab-side trace is missing only for a stop at a limit, and that in the 6 maxTurns events 4 were resumed. Is a `SubagentStop` or notice-reading line in harness.jsonl wanted, or is the platform notice enough for the PI?
- [now] Should the 7 budget-stop rows be quoted in w02-c5's "hand-back lost in 6 of 8" as "6 of 7 report files survived"? The claims say "5 of 6"; I count 6 of 7 with s3.

## Pointers
All paths under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-research-wave-9-a25ae6/`.
- `__reports__/wave-09/explorer-w09-g/41-rows.md` : 40-row table; `python3 -I __instrumenta__/w09g_classify.py f all > f_all.tsv; python3 -I __instrumenta__/w09g_table.py f_all.tsv > 41-rows.md`
- `__reports__/wave-09/explorer-w09-g/f_all.tsv` : classifier output, f's 312 files; `wide_all.tsv` : the other 876 lab-project files (`... wide all`)
- `__reports__/wave-09/explorer-w09-g/notices.tsv` : every platform notice "turn limit" / "without delivering" in lab parents, with later hand-back; `python3 -I __instrumenta__/w09g_notices.py > notices.tsv`
- `__instrumenta__/w09g_tails.py@3905c79` (last records per transcript), `w09g_classify.py@3905c79`, `w09g_notices.py@3905c79`, `w09g_table.py@3905c79`.
- Evidence read by hand: PI transcript `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl` 04:20 to 04:34Z (arm A ceiling); wave-4 session `c533f1c6` at 01:54:50Z and wave-8 session `ad75be4f` at 20:20:40Z (notices "report was delivered ... not repeated here").
