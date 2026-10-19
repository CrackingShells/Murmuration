# explorer-w01-e: human review UX (axis 3)

Left the brief: no. One extension: I built a 25-line prototype (`digest.py`) to test whether a
four-question digest is derivable from existing lab files, since that decides what "cost" a digest
proposal has. All scripts are in this folder, run with `python3 -I`, read-only on transcripts.

Labels: MEASURED (ran, numbers below), CONJECTURE, CITED (URL actually fetched), UNVERIFIED.
Transcript refs are `<session8>:<jsonl line>`. Sessions: 566=genesis 566fa912, 82e=design 82e8a947,
3cc=3ccc590f, 294=2947f9dc (all under `~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/`).
Derived files (user prompts, filtered): `prompts_<session8>.json` here.

## 0. Headline (short)

1. The human talks to the team through **chat prose, quote-replies and platform buttons**, not
   through lab files. In the design session 10 of 28 typed-or-clicked prompts were clicks on
   `wrap_up` action buttons (MEASURED, 1). The shipped plugin never mentions that surface (MEASURED, 6).
2. What the human objected to was **never layout or file format**. It was: (a) undefined jargon in a
   hand-back (3cc:439), (b) a name that clashed with a field (566:441), (c) a headline that
   misled (294:1254), (d) a diagram that did not render (294:1769), (e) "no meta-discourse" in
   shipped prose (82e:1759), (f) over-built hooks (82e:1744). The user *chose* the Latin store names
   (82e:1189), so "alien names" is not what the evidence shows.
3. Today a human cannot answer "what needs me" or "what did it cost" from the lab: no file or
   status field exists for the first, and the second is shown as 8 columns of tokens (MEASURED, 5).
4. Cheapest candidate with the best fit to the evidence: **use the platform's `wrap_up`/`AskUserQuestion`
   surfaces from the PI file (zero scripts), plus one derived `digest` view** (prototype 25 lines).
   Heavier established UX (trace viewer, dashboard) fits the *reviewer* role less than it fits a developer.
   Everything below is a proposal input, not a claim.

## 1. What the human read, asked for, asked to rewrite, complained about (in-repo evidence)

### 1.1 Volume and channel (MEASURED)

`humans2.py` (extracts `type=user` entries with system-reminders, task notifications and tool results
stripped; scans `queue-operation` for typed-while-running prompts) and `wrapups.py`.

| session | human entries | median words | quote-replies (start `>`) | clicks on `wrap_up` buttons | `AskUserQuestion` asks |
|:--|--:|--:|--:|--:|--:|
| 566 genesis (21 h wall) | 36 | 64 | 8 | 5 | 0 |
| 82e design (~22 h wall incl. overnight gap) | 28 | 38 | 3 | 10 | 0 |
| 3cc explanation fork | 5 | n/a | 0 | 0 | 0 |
| 294 anamnesis work | ~7 (+5 cron check-ins, 5 artifact comments) | n/a | 0 | 0 | 4 asked, 2 answered with free text overriding the options |

Click detection: a prompt text equal to an `actions[].message` of an earlier `mcp__ccd_turn__wrap_up`
call (`wrapups.py`, second block). Examples (82e): "I have more revisions to architecture v1/v2/v3"
(clicks, lines 1097/1209/1321), "Use the Latin weighing set" (1189), "Name the repository Murmuration" (1384),
"Reflective run first" (2255). 82e: 25 wrap_ups, 13 with an `ask`; recap words median 39, max 51
(the platform caps the recap near 50 words, MEASURED over 64 calls, all four sessions).

**Reading:** the platform already provides a human modality (button decisions, <=50-word recap, plan
checklist via `update_plan`, session chapters via `mark_chapter`, session link chips
`[title](#local_<id>)` in 566:2068). The PI in *this* run uses `update_plan` and `mark_chapter`
(ab96c5ed lines 34, 184) with no instruction from the plugin. `grep -ri "wrap_up|update_plan|AskUser|recap" agents skills scripts hooks README.md` returns nothing (MEASURED).

### 1.2 Every prompt that asked to see, to rewrite, or complained (verbatim fragments)

| ref | what the human said | category |
|:--|:--|:--|
| 566:201 (queued 03:29) | "I'm reading the problem framing, and generally you got it right" | read a file |
| 3cc:439 | "there are many notions here that I'm not familiar with ... Champernowne completion ... complete sequences ... LZ77 ... superstrings or de Bruijn path covers ... I will need proper explanation in the chat, **no new reports** ... as if I was a fourth year bachelor" | jargon; wants chat, not files; gives a level knob |
| 3cc:454 | "this level of details is good for me to get an overview" | calibrated: accepted |
| 566:441 | "Scroll is a bit too close to Turing machines. Consult the skill for coining neologism" | name clash |
| 82e:907 | quotes a hand-back paragraph and challenges it ("hasn't this been fixed...") | quote-reply to verify a claim |
| 82e:945 | "Honestly I am disappointed by your suggestion. Because you are trying to establish a rule..." | PI behaviour, not format |
| 82e:970 | quotes "> So the change is about attention, not procedure:" and says "i think this is getting somewhere" | quote-reply to endorse |
| 82e:1017 | "the sequence diagrams should have a loop box somewhere in relations to the arrow ..." ; "human-side utility to easily trigger/dispatch everything to a session that has a research-pi as the default ... this type of LLM-based agent system UX elements"; "consolidates the system to avoid ending up with a beast we can't understand" | read a diagram closely; asks for UX; fears opacity |
| 82e:1105 | "What do each entry contain? Are this file stores or true databases? How efficiently can you make them readable, writtable in parallel?" | asks what the stores are |
| 82e:1744 | "The things I find most overengineered are the hooks ... We are still engineering for a purpose, not for universality" | over-building |
| 82e:1759 | "no meta-discourse. We do not want the skills or agent files ... contaminated with context that is only relevant to the design" | prose hygiene |
| 82e:2360 | "understood, but I can always disable it for normal sessions" (reply to the PI's warning about the `agent` setting) | warning he did not need |
| 294:1254 | "the content is misleading for now, no? You are advertising lower values but 'NEXT' to the base" | headline overstated vs scope (slide) |
| 294:1656 | "less about the 'wow effect' and more about exactly what this means in terms of implementation ... the maintainer will need coherent findings reports he and its coding agents can read" | rewrite for an outside reader |
| 294:1769 | "`11-architecture_anamnesis_delta_v0.md` has mermaid syntax issues breaking rendering" | diagram failed to render |
| 566:1814-2029 | tracks his own time in another system (`/scheduling-work`): "it took 5h of my attention. But I wouldn't know how to divide" | human cost unit = attention hours |
| 82e:1601 | "run the remaining model-backed probes (... <=0.60 USD per session)" | human cost unit = USD per session |

The human read: the problem framing, the knowledge-transfer report, the sequence diagrams, the PI's
chat paragraphs (quoted 11 times), slides (inline comments through the Artifact surface, 294:1213-1769).
The human never wrote about the shape of a claim file, a puzzle file, or a wave note (none existed yet in
those sessions, so this is absence of evidence about v6 files, CONJECTURE).

### 1.3 Chat shape the human accepted (MEASURED, `chatshape.py`)

| session | PI messages | median words | p90 words | messages >250 words |
|:--|--:|--:|--:|--:|
| 566 | 90 | 69 | 407 | 19 |
| 82e | 98 | 52 | 454 | 19 |
| 3cc (human asked for explanation) | 15 | 251 | 1970 | 8 |
| 294 | 63 | 28 | 266 | 8 |

Bimodal: status pings (about 30-70 words) and hand-back digests (400-700 words, bullets plus bold lead
terms). The human did not complain about length in any of the four sessions (the only length-related
request is 3cc:439, and it asked for *more*, in chat). A good digest exemplar from 566:2080/2106:
"given the BF16 file, the 12.67 GB Q8_0 version stores in 95.6 MB ... That number should be read
carefully ... It is not evidence that two different model versions share information." One number, one
caveat, links as chips. The same session repeats "The ledger split is still waiting for your approval"
6 times in a row (566:2068-2125), which is a pending-decision line surfaced as a refrain.

## 2. Try it myself: what a human opens today

### 2.1 This lab, now (MEASURED, 2026-10-19 ~11:10; `python3 scripts/lab_status.py` takes 0.06 s)

| question | what I had to open | what I got | missing |
|:--|:--|:--|:--|
| What is the team doing? | `__statera__/wave-01.md` (58 lines), 6 dispatch rows, "Returned" column empty; then `/lab-status` (`runs=6` explorers) | which agents exist | no running/returned state, no wall time, no pointer to each agent's report. The Desktop agent panel is the only live view |
| What has it found? | `ls __pondus__` (empty), `__scrupuli__/wave-01-research-pi.md` (4 puzzles, 29 lines) | puzzles, no claims | explorer reports live in `__reports__/reflective_run/w01/<name>/report.md`; no file points to them |
| What did it cost? | `/lab-status` Spend table | 8 columns: msgs, input, cache-write 786,166, cache-read 8,983,984, output 31,363 | no USD, no minutes; cache-read dominates and means nothing to a person; PI vs explorer split is shown, per-wave is not |
| What needs me? | nothing | nothing | no file, field or status line. In this run the only item (budget) went through chat; the human replied by quote-reply, recorded in `user_words.md` 11:04 |
| What do the words mean? | `README.md`, `ls` | `__statera__`, `__pondus__`, `__scrupuli__` appear in the README 3 times, glossed by what they hold, never by what the Latin means | `framing.md` has 17 `SA<n>` ids in 1083 words, `wave-01.md` has 13 in 546; the PI's chat message (ab96c5ed:223) says "SA1-SA17" with no gloss |

4 steps (wave note, status, puzzle file, `ls reports`) to a partial answer for 2 of 4 questions.

### 2.2 Genesis study files, now (MEASURED)

`/Users/hacker/Documents/explore/combinatorics_on_binary`: 56 markdown reports, 658 kB in `__reports__/`,
plus a 70 kB notebook rendition `notebook/imbrication.md`.
- What is the team doing: `__roadmap__/swc/README.md` (3.7 kB): a coloured mermaid status graph and a
  nodes table, all nodes done. This is the best single status board in either project. v6 dropped it
  (the lab has no roadmap), replaced by `wave-NN.md` tables that nobody keeps current.
- What has it found: 10 per-topic READMEs (20 kB), e.g. `reference_coding/README.md` (735 words, 15 `H<n>`
  ids, 12 "rounds", each marked "superseded by"/"latest"). The human's own fix at 294:1656 was to ask
  for `11-findings_consolidated_v0.md` "No internal history" (11.6 kB). `reference_coding/` has 14 files,
  144 kB; the current pair is 24.5 kB (17%).
- What did it cost: nowhere in the project files; only in the transcripts (`cost-state`).
- What needs me: `pi_decisions/` (3 files, 5 kB) lists decisions the PI took; nothing lists decisions
  awaiting the human.

### 2.3 Prototype: the four-question digest from existing files (MEASURED)

`digest.py` (25 lines, imports `scripts/lab_status.py` read-only plus subagent `.meta.json`):
```
TEAM
  explorer-w01-c   working     5 min  wrote  8,042 tokens  Tools and MCP usage probe
  ...
OPEN PUZZLES 5   CLAIMS 0
NEEDS YOU: (no field for this exists in lab files today; the PI would have to write it)
```
Feasible: agent name, description, start/last event time, output tokens come from
`subagents/agent-*.meta.json` (`name`, `description`, `agentType`) and the transcripts. Not derivable: a
state field (I infer "working" from last-event age, "returned" from a report file at a convention path;
both heuristics are UNVERIFIED), USD (needs a cited price table; not applied), and anything under NEEDS YOU.

## 3. Established UX, per tool: cost here, alien or less alien

Fetched sources are listed in section 5. "Cost" in lines of code / tokens / platform dependence.

| UX | What it is (CITED) | Cost here | Alien to the human? | Fit to evidence |
|:--|:--|:--|:--|:--|
| Inspect AI log viewer | `inspect view` local web app: log history, live view of samples, info panel (git rev, token usage), per-sample messages/scoring/metadata, filter by score | A viewer needs a structured log (SA2 JSONL) or a transcript adapter; weeks of code or a dependency. Inspect logs are its own format | More alien: a developer tool, per-sample, not per-claim | Low. The human reads prose and quotes it |
| Langfuse / LangSmith traces | nested runs with timing, tokens, cost, scores, dashboards, alerts; LangSmith "trajectory" = flat deduplicated message list without nesting | Needs OpenTelemetry export plus a server (SA3, SA11); platform dependence high | More alien for a research reader; but "trajectory" (flat list, no nesting) is the shape the PI hand-backs already have | Low for review, medium for cost totals (axis 2, not mine) |
| Electronic lab notebook conventions (CASRAI template) | entry = objective written before results, methods, timestamped procedure log, raw data, observations, deviations, conclusion; amend by linked dated addendum, never overwrite; author and reviewer signatures bound to the exact version; witness should actually read it | Almost free: `closed:`/`supersedes:`/`changed_by:` already encode amendment and linkage. Missing: the objective-before-result field and a reviewer sign-off | Less alien: it is the form a scientist already knows | High on form, and v6 already agrees (hypothesis-before-result is `## What does not add up`; verdict sections are witness-like). Reviewer "bound to version" = verdict records the claim commit (not present) |
| PR-review style (GitHub) | per-file "Viewed" collapse with progress bar, un-viewed on change; line comments; pending review; Comment/Approve/Request changes with summary; author cannot approve own PR | A human verdict section in claim files: `## verdict: <human>` already parses (the format is open to any name; the verdict vocabulary is not). "Viewed" needs state (a file or a hook): small | Less alien, familiar to every developer | Medium. The human did review by quote-reply and click, which maps to Comment and Approve. "Request changes" = the existing button/free text |
| Dashboard (static HTML page of digest) | Langfuse custom dashboards; any BI page | One generator script plus the Artifact surface the human already used (294: 14 `Artifact` calls, inline comments came back as `artifact-view-context` prompts) | Neutral; fails if stale | Medium. The human used Artifacts for slides and commented in place; the platform returns the comments to the agent (294:1213) |
| Notifications / digests (hooks) | `Notification` hook matchers include `agent_needs_input`, `agent_completed`; `SubagentStop`; `systemMessage`, `terminalSequence` (desktop notification) outputs | ~15 lines per hook, platform-dependent; hooks are what the user called most over-engineered (82e:1744). Confirmation/alert fatigue is a documented risk (search snippets only, see UNVERIFIED) | Neutral if rare, alien if frequent | Low-medium. The human is in the GUI and the PI already answers on return |
| Claude Code status line | shell script on stdin JSON, shows e.g. `cost.total_cost_usd`, `cost.total_duration_ms`, lines added, rate-limit percentages; re-run on events, 300 ms debounce, optional `refreshInterval` | ~10 lines of script and one setting in `.claude/settings.local.json` (which `/lab` already writes). Whether it counts subagent cost: UNVERIFIED (session-level fields only seen) | Less alien: always visible, USD, no files to open. But the Desktop app (the GUI the user prefers, 82e:2309) may not render a TUI status line: UNVERIFIED | Medium for the cost question; zero for "needs me" |
| `/` commands | `/lab`, `/lab-status` exist | A `/lab-status` view reordered to the four questions; changes the script output, not the data | Neutral | High, cheapest, already the human's entry point |
| Desktop surfaces: `wrap_up` (recap <=50 words + ask + buttons), `AskUserQuestion` (options, recommended, free text), `update_plan`, `mark_chapter`, Artifacts with inline comments | observed in transcripts (MEASURED); tool names `mcp__ccd_turn__wrap_up` etc.; their descriptions CITED nowhere I could fetch | Zero code: instruct the PI to end a wave with a `wrap_up` carrying the "needs you" ask. Platform dependence: Desktop only; absent in plain CLI or `claude -p` (UNVERIFIED how the tool list differs) | Least alien: it is the interface the user already uses | **Best fit.** 10/28 of the design-session prompts were button clicks |
| Human-in-the-loop research systems (Magentic-UI) | co-planning, co-tasking, multi-tasking, action guards, long-term memory (arXiv 2507.22358, abstract) | Design vocabulary, no code | n/a | co-planning matches "Tell me if you want a different figure" / quote-reply on the budget; action guards match `AskUserQuestion` on downloads (294:112) |

## 4. Worst-fitting cases (next to the typical)

Typical (fits the emerging story "channel = chat plus buttons; cost unit = USD and attention minutes; lab files are for the PI"):
566:2034-2125 plus 82e wrap_up clicks.

Worst fits:
1. **The human did read dense files without complaint.** "I'm reading the problem framing" (566:201), and
   a 658 kB report tree plus a 70 kB notebook rendition were produced and accepted; the only length/jargon
   complaint (3cc:439) came from a fork where the human said he is "not a specialist". So jargon may be a
   function of the *topic* (combinatorics), not of Murmuration's files. The lab files themselves
   (claims, puzzles, waves) have **no human reader evidence at all**. My story about them is CONJECTURE.
2. **The human chose the Latin names** (82e:1189, button "Latin weighing set"), (the options he was shown are in the wrap_up at 82e:1185; I did not read whether plain-English alternatives were offered). The cold review (`__reports__/cold_review/00-findings_v0.md` row 24) only checked
   that names matched files, never whether a human found them opaque.
3. **Buttons were also used to defer**: "More revisions" was clicked 3 times in a row (v1, v2, v3,
   82e:1097/1209/1321), i.e. the structured surface sometimes carried "no decision". A "needs you" list
   would not have captured that.
4. **Free text beat the options** in 2 of 4 `AskUserQuestion` calls (294:794, 870: "check out the /banyan
   skills ... don't only use the run_command escape hatch"; "This rsync stuff is a nightmare"). Structured
   asks under-fit the human when the situation is outside the PI's model.
5. The 3cc fork shows the human *asking the system to be more verbose and more basic* (the opposite of the
   "leanness" priority). Leanness (axis 1) and reviewability (axis 3) conflict there.

## 5. Sources fetched (CITED)

- Inspect AI log viewer: https://inspect.aisi.org.uk/log-viewer.html (fetched)
- Claude Code status line: https://code.claude.com/docs/en/statusline (fetched, 65.8 kB; JSON fields grep-checked in the saved result: `cost.total_cost_usd`, `cost.total_duration_ms`, `rate_limits.*`, `refreshInterval`, 300 ms debounce)
- Claude Code hooks: https://code.claude.com/docs/en/hooks (fetched, first 100 000 of 273 658 chars; Notification matchers, `systemMessage`, `terminalSequence`)
- Langfuse overview: https://langfuse.com/docs/observability/overview (fetched; answer limited to what the page shows)
- LangSmith concepts: https://docs.langchain.com/langsmith/observability-concepts (fetched via redirect from docs.smith.langchain.com)
- ELN template: https://casrai.org/guides/electronic-lab-notebook-template (fetched; labfolder/labii vendor pages seen as search results only: UNVERIFIED)
- GitHub PR review: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request (fetched)
- Magentic-UI: https://arxiv.org/abs/2507.22358 (fetched, abstract only)
- UNVERIFIED (search result snippets, pages not fetched): alert/confirmation fatigue and "execute with notification" tiers (parallelhq.com/blog/ai-agent-ux-design, agenticwire.news/article/agent-ux-design-patterns, geosurge.ai corpus); EU AI Act Art. 14 date claim; health-tech "tripled adoption" anecdote.
- The tool descriptions of `mcp__ccd_*` (wrap_up, update_plan, mark_chapter) were not available to me; their behaviour is read from the PI's calls in the transcripts only.

## 6. Proposals as inputs (CONJECTURE; each would be a claim, none is made here)

| Idea | Touches | Cost | Fits |
|:--|:--|:--|:--|
| P1 One paragraph in `research-pi.md`: end each wave and each decision with a `wrap_up` that names the pending ask and gives 2 buttons; keep the human's own words; gloss any `SA`/`S-w` id on first use in chat | `agents/research-pi.md` | ~6 lines; Desktop dependence | 10/28 click evidence; ab96c5ed:223 jargon |
| P2 Reorder `/lab-status` output to four headings (Doing / Found / Cost / Needs you) and show output tokens + minutes beside the raw columns; USD only with a cited price flag | `scripts/lab_status.py`, `skills/lab-status/SKILL.md` | ~40 lines; no new data | section 2.1 table |
| P3 A `## For you` section in the wave template (pending decisions, one line each, with the default if ignored) | `templates/wave.md` | 3 lines | no file marks "needs me" |
| P4 `Returned` column filled with the report path (or an SubagentStop hook that fills it) | wave template / hook | 1 line / ~20 lines | wave-01.md empty column |
| P5 Keep a status board: one `status.md` generated from lab files with a mermaid graph of waves and claims (the genesis roadmap README shape) | new script | ~60 lines; mermaid breakage seen at 294:1769 | genesis 3.7 kB README |
| P6 Consolidated "current" report per question, with no history, as the PI's closing artefact | `waves.md` closing step | 0 lines of code | 294:1656; reference_coding 144 kB vs 24.5 kB current |
| P7 Human attention minutes: record from timestamps of human prompts per wave; show beside tokens | a hook or lab_status | ~30 lines | 566:1814-2034 (the PI proposed "words you wrote" as proxy) |

Stays out unless the human asks: dashboards, trace viewer, external observability servers, alert hooks.
