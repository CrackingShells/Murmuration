## symbols
- CCD tools: the Claude Code Desktop tools `mcp__ccd_turn__wrap_up` (recap, ask, action buttons), `mcp__ccd_turn__update_plan`, `mcp__ccd_session__mark_chapter`, seen in transcripts; not defined in the framing. Used only in this file and the report.

## S-w01-explorer-w01-e-1
The plugin ships no instruction about how the PI speaks to the human, yet in the design session 10 of 28 human prompts were clicks on `wrap_up` buttons, and this run's PI already uses `update_plan` and `mark_chapter` unprompted. So the human-facing surface is whatever the PI model improvises plus Desktop-only tools. I could not read the tool descriptions, so I do not know what the CLI or `claude -p` PI does instead; if a lab is run headless, the whole button channel is absent and the "needs you" ask has nowhere to go.
refs: __reports__/reflective_run/w01/explorer-w01-e/wrapups.py (output in report.md section 1.1); `grep -ri "wrap_up|update_plan|AskUser|recap" agents skills scripts hooks README.md` returns nothing; ab96c5ed transcript lines 34 and 184

## S-w01-explorer-w01-e-2
There is zero evidence of a human reading a claim file, puzzle file or wave note, because none existed in the four sessions. Every complaint I found concerns chat prose, names, a slide headline and a mermaid render. I wrote the four-question table (doing, found, cost, needs me) from my own walk through the lab, not from anything the human said. The risk: the digest proposals fit me, not him. The one observed lab-file reading is the user's reply to the PI's budget sentence (user_words.md 11:04), which came through chat.
refs: __reports__/reflective_run/w01/explorer-w01-e/prompts_82e8a947.json; __statera__/user_words.md (11:04 entry)

## S-w01-explorer-w01-e-3
The human's own cost units are USD per session ("<=0.60 USD per session", 82e:1601) and hours of his attention ("5h ... I wouldn't know how to divide", 566:2029); the lab reports neither (tokens only, 8 columns, cache-read 8,983,984 dominating). The PI in 566 had to propose "words you wrote in each task's window" as a proxy for attention. Human prompt timestamps are in the transcripts and in `user_words.md` headings, so an attention proxy is derivable, but nobody has checked that it correlates with attention. And a USD column needs a price table I could not cite from a fetched source.
refs: __reports__/reflective_run/w01/explorer-w01-e/report.md sections 1.2, 2.1; 566fa912 lines 2029-2034; output of python3 scripts/lab_status.py (Spend table)

## S-w01-explorer-w01-e-4
"More revisions" was clicked on architecture v1, v2 and v3 in a row (82e:1097, 1209, 1321), and `AskUserQuestion` was overridden by free text in 2 of 4 calls (294:794, 870). Structured asks look cheap to the human but may carry little decision content; yet the design session still progressed through them. I have not measured whether a button click corresponds to less thought than a typed prompt, or whether the PI acted differently after a click. This bears on whether SA13 (soft/hard questions) should be a plugin feature or left to the platform.
refs: __reports__/reflective_run/w01/explorer-w01-e/wrapups.py; 82e8a947 lines 1093-1097, 1205-1209, 1317-1321; 2947f9dc lines 793-794, 865-870

## S-w01-explorer-w01-e-5
The only jargon complaint (3cc:439) arose where the human said he is not a specialist of combinatorics, and it asked for MORE explanation in chat, no report. That is evidence that the review problem is topic-dependent and that leanness (axis 1) can conflict with reviewability (axis 3). How would the PI tell, in a new lab, which level the human is at? The 3cc prompt gave a level knob ("fourth year bachelor", "I will raise the bar to master"); nothing in the lab captures it, and `framing.md` has no reader-level line.
refs: 3ccc590f lines 439, 454 (prompts_3ccc590f.json); __design__/framing.md (no reader field)

## S-w01-explorer-w01-e-6
The genesis roadmap README (3.7 kB: coloured mermaid status graph and node table) answered "what is the team doing" in one open; v6 dropped `__roadmap__` from the lab and `wave-NN.md` tables take its place, but the "Returned" column of `wave-01.md` is blank for all 6 dispatches (it is a manual field nobody fills). And the human reported a mermaid file that did not render (294:1769), so a mermaid status board would carry a known failure mode. Which is worse: a board that goes stale, or a diagram that breaks?
refs: /Users/hacker/Documents/explore/combinatorics_on_binary/__roadmap__/swc/README.md; __statera__/wave-01.md (Dispatches table); 2947f9dc line 1769

## S-w01-explorer-w01-e-7
The human-facing headline can overstate scope while every claim-level label is honest: the slide advertised "-46-64%" for storing a fine-tune against its base, and the human caught that the saving only holds when the base is stored next to it (294:1254). Murmuration's labels (MEASURED, CONJECTURE, ...) protect claim files, but nothing carries scope into the PI's chat summaries or into artifacts made for outsiders. The `scope:` field exists in claim heads and is not shown by `/lab-status`.
refs: 2947f9dc line 1254 (prompts_2947f9dc.json); skills/research-loop/SKILL.md claim format; skills/lab-status/SKILL.md (output has no scope)
