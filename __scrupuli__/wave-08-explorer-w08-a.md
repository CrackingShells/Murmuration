## symbols
none new. "context USD" = input-side USD of a worker's requests (cache read + write + uncached input), list price; output tokens excluded.

## S-w08-explorer-w08-a-1
Nearly half of worker context USD (41.6%) is the worker's own earlier turns: thinking blocks 22.5% and tool-call text 19.0%, against 3.7% for lab-script output. The thinking text is redacted in the transcripts; its size comes from a fit of context growth on signature characters (R2 0.989), so I never saw a token count for it directly. Does a thinking block really stay in the context for later requests, and is this 22.5% a billing fact or a fit artefact? A probe with a known thinking length would settle it. The costliest workers (author-w06-5 USD 9.09 over 241 requests, 67% own turns) say cost follows request count, which no cap on outputs touches.
refs: __reports__/wave-08/explorer-w08-a/tables.md section 1; check.txt (fit line); items.tsv rows with cls=asst

## S-w08-explorer-w08-a-2
Inline python (heredoc or `python3 -c`) is the single costliest "script" row: 947 results, USD 6.32 (7.6%) as output, and the same code sits again in the call text (inside the 19.0% of tool-call text). Workers write their own analysis code in the call instead of a file in `__instrumenta__/`; the lab's rule asks for scripts in files. Unknown: how much of the 19.0% is heredoc code (I did not split call text by what the call was).
refs: __reports__/wave-08/explorer-w08-a/top_refs.tsv (first row); bash_by_command.tsv; items.tsv cls=asst kind "tool calls"

## S-w08-explorer-w08-a-3
The briefs of wave 7 asked 14 of 21 workers to read the wave note (my count of brief mentions), 12 workers' calls touch it, and my classifier finds only 16 workers across waves 4-7 with a wave-note result; the wave notes then cost USD 0.79 (0.9%). The item 38 worry (a 52 KB wave note read by every worker) is therefore not visible in waves 4-7 (notes averaged 3,840 tokens when read); the data cannot say what wave 8 costs. Also: 0 of 117 Reads of documents used offset or limit, while 71% of document USD entered in the first four requests.
refs: __reports__/wave-08/explorer-w08-a/tables.md sections 2 and 6; items.tsv rows kind "wave note"

## S-w08-explorer-w08-a-4
Classifier limits that I could not close: a Bash command that reads several files takes the kind of its first path (one wave-07 report is filed as "claim file"; `top_refs.tsv`), variables such as `$S/file` carry no lab path so those reads fall into "scratch/data file", and "bash/python other" (230 results, USD 1.25) are python calls whose target I could not read. The shares move by a point or two, not by the ranking. A per-call manual audit of 30 rows (as explorer-w07-b did for merges) was not done.
refs: __instrumenta__/w08a_items.py (classify_bash); __reports__/wave-08/explorer-w08-a/items.tsv rows kind "bash/python other"

## S-w08-explorer-w08-a-5
rtk: the page, read through a fetch summary, says nothing about unlisted commands, about whether `rtk read` is lossy, or about recovering hidden output. For the lab the question that decides is `cat` of claim files and reports by verifiers (USD 4.15 of `cat` documents), where a compressed view could hide the line a verifier needs. The git, grep, find, ls part that carries no such risk is 2.9% of context USD. Nothing was run, so the hook's own cost per call and the compression on lab output are unmeasured.
refs: __reports__/wave-08/explorer-w08-a/bash_by_command.tsv; 00-findings_v0.md "rtk" section
