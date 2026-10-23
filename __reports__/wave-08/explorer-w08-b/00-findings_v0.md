---
type: findings
wave: wave-08
author: explorer-w08-b
date: 2026-10-24
version: v0
decision-required: intervene
---

# Does colgrep answer the lab's own questions, and why do workers read whole files instead (findings v0)

Stayed inside the brief. Two departures of method, both for fidelity: (a) the question set was scored through the `colgrep search --json` command line that the MCP server wraps, with the server's own span correction (`locate.py`) re-applied, because the command line's raw spans are wrong for Python units; five questions were spot-checked through the MCP tool itself (same hits, same order within one place). (b) No worker's reasoning is available: every thinking block in the 68 worker transcripts is empty (2,905 blocks, 0 characters), and workers wrote 105 text blocks in all, one mentioning colgrep. So item 2 of the brief is answered from behaviour and from the text workers were given, not from stated reasons.

## Result
1. **Where it can be answered (CHECKED, 23 questions, one wording each of two).** With a plain-language query the file holding the answer is in the top 1 / 3 / 10 hits in 6 / 10 / 15 of 23 questions and the needed section in 4 / 8 / 11; with an identifier-rich query 9 / 13 / 17 and 8 / 12 / 16. Python scripts are cut into functions (a hit costs 0.9–4.4k characters against a 22–64k-character file); **markdown is one unit per file** (17 of 17 markdown questions: unit = the whole document), and the hit snippet is the first lines of that file, never the matching section. So "search, then expand the unit" on a note, claim or report returns the whole file, at most its first 200 lines (`expand` default), and a listing of 10 hits (median 10.3k characters; 5 hits 4.9k) costs about as much as the median file (19k) or more for files under 10k.
2. **Why workers do not use it (MEASURED on 68 workers, waves 4–7).** 51 never called colgrep (75%); 17 did, in 24 calls, **all 24 aimed at scripts or code** (20 with `paths` = `__instrumenta__`, as the agent files tell them to, 4 elsewhere in the lab, by the query text still about code), none at a note, claim or report. Of the 17, 2 later read a hit file whole, 9 ran, wrote or part-read a hit, 6 touched no hit file. 65% of whole reads (182 of 280) name a file the worker's own brief names; for markdown 87% (152 of 175). The one place where search could replace a read is unnamed scripts: 41 whole reads, 286k characters.
3. **The policy text does not push toward `cat` and `sed` by denial** (MEASURED): its own wording blesses reading "a known file's contents", and the recursive-grep denial barely fired (below). The lab has no recorded case of a worker distrusting a hit.

## Table
| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Main-checkout index, this session | 3,605 units at the first status call (last build 3 days earlier); a first search re-indexed to 5,833 units in 35.5 s | MEASURED | colgrep `index_status` x2, first `search` elapsed_ms 35451 |
| Worktree index | none before this run (`indexed:false`); default `search`/`index_status` with no `paths` resolves to the main checkout `/Users/hacker/Documents/src/CrackingShells/Murmuration`, not the worktree. I built one for this worktree by a search with an explicit path (5.5 s, 1 call) and one for `__reports__/wave-08`, which I cleared again | MEASURED | `index_status` (resolved root), `search` paths=[worktree] elapsed 5452 ms |
| New file written this session | invisible to a default search (searches main); found within 5.5 s when `paths` names the worktree (my new scripts hit at ranks 1–3 by their first-line comment); `.tsv` files are not indexed at all (0 hits for a token that exists in `questions.tsv`) | MEASURED | two `search` calls, one `pattern` search |
| Relative `paths` (item 11) | 8 of 24 real worker calls used `__instrumenta__` relatively (waves 4–5): 2 returned nothing (275 ms), 6 searched the plugin's own folder; all 16 calls from wave 5 on that used absolute paths searched the lab. From wave 6 every call is absolute | MEASURED | `colgrep_calls_latency.tsv` |
| Worker colgrep latency | tool time median 4.6 s (n 24; min 0.8, max 72.6); 16 calls re-indexed first (`index_updated:true`), 6 did not (0.8–1.3 s), 2 were the empty relative-path errors; a direct search on a warm index is 0.7 s | MEASURED | `colgrep_calls_latency.tsv`; `results_cli_main.tsv` column wall_s (median 0.75 s) |
| Separate sub-indexes | a `paths` subfolder creates its own index; `list_indexes` shows 11 for Murmuration worktrees (5–60 MB each, 1.98 GB for all 120 on the machine) and returns 37k characters | MEASURED | `list_indexes` (one call) |
| Question set A (plain language), top 1/3/10, file | 6 / 10 / 15 of 23 (Q24 dropped: no anchor line) | CHECKED | `results_cli_main.tsv` |
| Question set A, top 1/3/10, section (unit contains the answer line) | 4 / 8 / 11 of 23 | CHECKED | same |
| Question set B (identifiers in the query), file | 9 / 13 / 17 of 23 | CHECKED | `results_cli_main_kw.tsv` |
| Question set B, section | 8 / 12 / 16 of 23 | CHECKED | same |
| Noise | mean 3.3 of the top 10 hits are copies or run output under `__reports__/reflective_run`, `/runs/`, `replay_lab`, `/scratch/` or `/probes/`; 13 of 23 questions have 3 or more | CHECKED | column noise10 |
| Unit size when it hits: script | Q03 `gate`: 1.3k characters against 21.8k for the file | CHECKED | Q03 row |
| Unit size when it hits: markdown | unit = file in 13 of 13 hits (0.9k to 52k characters) | CHECKED | `results_cli_main.tsv` unit_chars vs file_chars |
| `expand` default cap | 200 lines. On wave-07.md (603 lines, 52k characters) it returned lines 1–200 (about 14k characters, `truncated:true`) by MCP; the answer to Q07 (line 470) is out of reach without `max_lines` | MEASURED | `expand` call; `results_cli_main.tsv` Q07, Q01 (answer line 411, unit 506 lines) |
| Listing size from the MCP tool | 10 hits 7.2–9.5k characters (JSON repeats the path 3 times per hit); 3 hits 2.3–3.8k | MEASURED | own transcript, `colgrep_calls_latency.tsv` rows `me` |
| Tool calls waves 4–7, 68 workers | Read whole 138, Read with offset/limit 4, `cat` as a read 166, `sed` as a read 199, `head` 50, shell `grep` 203, colgrep `search` 24, `expand` 0, `find_files` 0 (waves 4–6 alone: 18 search, 105 Read) | MEASURED | `calls_heads.tsv` |
| Workers by colgrep use | never 51; used and no later touch of a hit file 6; used, then ran/wrote/part-read a hit 9; used, then read a hit whole 2 | MEASURED | `worker_classes.tsv` |
| Whole reads named in the worker's brief | 182 of 280 (65%), 1.95M of 2.66M characters (73%); markdown 152 of 175; scripts 25 of 66 | MEASURED | `whole_reads_brief.tsv` |
| Search policy delivered | the same 1,085-character block in all 68 workers' start context (and the PI's) | MEASURED | `w08b_policy_text.py` output |
| Recursive-grep forms that ran | about 30 `grep -r`-style calls ran fine in waves 4–7; 4 transcripts carry the block message, 3 of those from a heredoc or a python body that merely contained the words; today `grep -rn "def usd_of" scripts` also ran | MEASURED | `w08b_policy_denials.py`; one test call |
| Colgrep policy hook cost | PreToolUse hook on every Bash call: reported by explorer-w07-c as median 431 ms (n 10, load 9) and by the wave-5 non-model-overhead worker as 119 ms against 72 ms for a bare interpreter | CITED from worker hand-backs, UNVERIFIED here | hand-back text in the wave-5 and wave-7 transcripts |

Per-question rows: `results_cli_main.tsv` (set A), `results_cli_main_kw.tsv` (set B). The questions come from files workers read whole (hooks.json 11 reads, budget.py 5, wave-07.md 6, claim files, protocols, reports, agent files, SKILL.md, framing.md 44); the "need" is my reading of the next calls and of the file, not a worker's statement [assumption: no text or thinking was recorded]. Q24 had no usable anchor and is dropped.

Predictions (CONJECTURE, not tested): the wordings below. They are candidates for the PI's item 41; I did not edit agent files.

**Candidate wording 1, for the agent files (replaces the helper-script sentence):** "To find a script, function or note whose name you do not know: colgrep `search` with an absolute `paths`, `limit: 5`, then `expand` the hit; for a script the hit is the function. For a document you know by path, `grep -n` its headings, then `sed -n 'a,bp'`; do not Read or `cat` a file over 8 KB whole unless this brief names it." Predicts: unnamed whole reads of scripts (41 reads, 286k characters in waves 4–7) fall by about half; whole reads of named markdown do not move; colgrep calls rise from 24 in 68 workers to roughly one per worker, nearly all aimed at scripts.

**Candidate wording 2, for the brief (the PI writes it, since 65% of whole reads are of files the brief names):** "Read whole: <list>. For every other file: search or `grep -n` first, then read the lines you need." Predicts: the 182 named whole reads become a short list the PI controls; the cost per worker falls only if the list is shorter than today's (the median brief names 2–4 files; framing.md alone is read whole by 44 workers). Measured as re-read USD per worker, as item 41 asks.

**Candidate wording 3, a tool-side line in the search policy (the plugin is another repository's):** "colgrep cuts code into functions but a markdown file is one hit; for notes and claims use `find_files`, then `grep -n` in the file." Predicts: fewer `search` calls that return the whole note and are then re-read; no change in whole reads. The real lever for notes is a section-level markdown unit in colgrep (CONJECTURE: not tested; the index here cuts one unit per file for `.md`).

## Worst-fitting case
The story "colgrep cannot serve the lab's documents" fits worst on **Q03** (`gate` in `scripts/handback.py`): rank 1, a 20-line unit of 1,319 characters against the 21,774-character file, 94% smaller, in 0.7 s. The story "workers distrust it" fits worst on its own premise: **no worker wrote a reason**, and of the 17 who used it only 2 read a hit file whole, one of them a verifier who had to re-run that script. The typical row is the opposite: **Q09/Q10** (claim files, answer in the last lines) rank 16 and 26 with the plain wording (rank 1 and 3 with identifiers), hits of 20k characters each. The user's observation (agents prefer full reads) is true of the behaviour (97% of Reads are whole, 280 whole reads against 24 searches); what the data do not show is distrust as the cause.

## Not covered
- Workers' reasons: none are recorded (empty thinking blocks). A probe could ask a headless worker, but that measures what it says, not what it did.
- The re-read USD per worker and the effect of any wording (item 41's last question): not run. The wordings are predictions.
- Waves 1–3 (44 workers, `ab96c5ed`) and the PI's own reads; the PI's transcripts were not classified.
- Latency was timed outside the MCP server for the 23 questions (command line, warm index, 0.7 s median); inside the MCP the same call costs 0.7–1.6 s plus 1–2 s of harness time, and 2.8–72 s when the index had to be updated first.
- Whether a section-level markdown cut exists in colgrep (a configuration or version): I looked at behaviour only (version 1.6.2, server 0.5.2), not at the colgrep source.
- Why the recursive-grep guard blocks some forms and not others (puzzle S-w08-explorer-w08-b-2).
- The scoring takes the first matching unit as "the needed section"; for scripts neighbouring functions may answer as well (Q04 `is_lab_command`, Q05), so the script section figures are strict (1 of 5 at top-1).

## Steering questions
- [now] Which of the three wordings do you want tested for item 41, and is the test a worker brief change (the PI controls it) or an agent-file change (all workers)?
- [now] Do you want the lab to ask the colgrep-mcp plugin's owner for a section-level markdown unit and a 10-character-per-hit listing, or does the lab work around it (notes stay read by `grep -n` and `sed -n`)?
- [now] The default search root is the main checkout, not the worktree: a worker in a worktree that omits `paths` searches a stale copy, and nothing it wrote this session. Should the agent files say "absolute path of your working directory" in the line itself (they already do for `__instrumenta__`) for every search?

## Pointers
All under `__reports__/wave-08/explorer-w08-b/` unless noted; scripts at commit 799f543.
- `calls_heads.tsv`: one row per tool call of the 68 workers (class, target path, result characters, error flag, no command text). `python3 -I __instrumenta__/w08b_calls.py <scratch>/calls` (`__instrumenta__/w08b_calls.py@799f543`; also writes a private file of commands, not committed).
- `worker_classes.tsv`: `python3 -I __instrumenta__/w08b_worker_classes.py <scratch>/calls` (`w08b_worker_classes.py@799f543`).
- `whole_reads_brief.tsv`: `python3 -I __instrumenta__/w08b_brief_named.py <scratch>/calls` (`w08b_brief_named.py@799f543`); also prints the colgrep mentions in briefs (15 of 68) and in the start context (68 of 68).
- `colgrep_calls_latency.tsv`: `python3 -I __instrumenta__/w08b_colgrep_latency.py` (`w08b_colgrep_latency.py@799f543`).
- `questions.tsv`, `questions_kw.tsv`, `results_cli_main.tsv`, `results_cli_main_kw.tsv`: `python3 -I __instrumenta__/w08b_questions_cli.py <questions.tsv> /Users/hacker/Documents/src/CrackingShells/Murmuration <results.tsv> 30` (`w08b_questions_cli.py@799f543`; ran against the main checkout's index at HEAD 4f60595; no seed, deterministic apart from index refresh).
- `w08b_policy_text.py`, `w08b_policy_denials.py`, `w08b_colgrep_mentions.py`, `w08b_candidates.py` (the last two write private transcript text to the scratchpad, not committed).
- Puzzles: `__scrupuli__/wave-08-explorer-w08-b.md`.
