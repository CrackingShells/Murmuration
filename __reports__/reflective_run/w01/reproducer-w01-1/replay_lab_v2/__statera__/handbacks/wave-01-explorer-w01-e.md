# Hand-backs of wave-01-explorer-w01-e

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T12:00:11+09:00 | agent_id=a53e063b007b7a428 type=murmuration:explorer event=PostToolUse status=delivered bytes=6389 sha256=9e0235f4f6ec
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

explorer-w01-e: I stayed inside the brief. The one extension is a 25-line prototype digest (`digest.py`), built to test whether the four-question view can be derived from files that already exist.

Everything is read-only on the transcripts. Scripts and derived JSON are in the report folder.

**Files**
- Report: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/explorer-w01-e/report.md`
- Scripts and extracts, same folder: `humans2.py`, `wrapups.py`, `chatshape.py`, `digest.py`, `prompts_*.json`
- Puzzles: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-explorer-w01-e.md` (S-w01-explorer-w01-e-1..7, plus a `## symbols` entry defining "CCD tools")

**What I found (MEASURED unless stated; line refs are `<session8>:<jsonl line>`)**
1. **The human works through chat, quote-replies and platform buttons, not through lab files.**
   - In the design session (82e8a947), 10 of 28 human prompts were clicks on action buttons of the Desktop tool `mcp__ccd_turn__wrap_up`. The recap text is capped near 50 words.
   - The genesis session (566fa912) had 5 clicks in 36 entries, and 11 prompts across the two sessions were quote-replies.
   - The shipped plugin never mentions this surface. A grep of `agents/ skills/ scripts/ hooks/ README.md` finds nothing.
   - This run's PI already uses `update_plan` and `mark_chapter` unprompted.
2. **The human's complaints were never about file layout or length.**
   - Jargon in a hand-back (3ccc590f:439): he wanted "proper explanation in the chat, no new reports", pitched at fourth-year bachelor level.
   - A name that clashed with a field (566:441).
   - A slide headline that misled (2947f9dc:1254).
   - A mermaid diagram that did not render (2947f9dc:1769).
   - "No meta-discourse" in shipped prose (82e8a947:1759).
   - Over-built hooks (82e8a947:1744).
   - A rewrite for outside readers (2947f9dc:1656). The genesis `reference_coding` folder holds 14 files and 144 kB; the current consolidated pair is 24.5 kB.
3. **A human cannot answer "what needs me" or "what did it cost" from this lab today.**
   - No file or status field marks a pending human decision.
   - `/lab-status` shows spend as 8 columns of tokens. Cache-read, 8,983,984, dominates.
   - `wave-01.md` has the Returned column blank for all 6 dispatches.
   - The explorer report paths are not linked from anywhere.
   - The human's own cost units are USD per session (82e8a947:1601) and hours of his attention (566:2029, where the PI had to propose a proxy).
   - `framing.md` has 17 `SA<n>` ids in 1083 words, and the PI's chat message at ab96c5ed:223 says "SA1–SA17" with no gloss.
4. **The best status board either project has is the genesis roadmap README** (3.7 kB, mermaid graph plus node table). v6 dropped it.
5. **Prototype:** `digest.py` derives team, working/returned state, minutes, output tokens and report path from the subagent `.meta.json` files plus `lab_status.py`. State is inferred from last-event age and a report-path convention, and I have not verified that inference. The "needs you" line and USD cannot be derived.

**Established UX, from the pages I fetched (CITED; URLs and the UNVERIFIED sources are in report section 5)**
- Inspect AI log viewer, Langfuse and LangSmith traces: low fit and more alien. They are developer tools that need structured logs or an OpenTelemetry server.
- ELN template (CASRAI): high fit on form and almost free. `closed`, `supersedes` and `changed_by` already encode amendment and linkage. A reviewer sign-off bound to the version is missing.
- GitHub PR review: medium fit, and familiar. A `## verdict: <human>` section already parses.
- Claude Code status line: exposes `cost.total_cost_usd` and `cost.total_duration_ms`, about 10 lines to use. Whether it counts subagent cost, and whether the Desktop GUI renders it, are UNVERIFIED.
- Notification hooks (`agent_needs_input`, `agent_completed`): low to medium fit. The user called hooks the most over-engineered part.
- Desktop surfaces (`wrap_up`, `AskUserQuestion`, `update_plan`, artifacts with inline comments): best fit, zero code, Desktop-only. I could not fetch their tool descriptions.
- Alert-fatigue and "execute with notification" claims come from search snippets only (marked UNVERIFIED).

**Worst-fitting cases (report section 4)**
- The human read dense reports and 400–700 word hand-backs without complaint. The only jargon complaint came from a fork where he said he is not a specialist.
- He chose the Latin store names himself (82e8a947:1189), so "alien names" is not supported by the evidence.
- "More revisions" was clicked three times in a row, so buttons sometimes carried no decision.
- Free text overrode the `AskUserQuestion` options in 2 of 4 asks.
- He asked the system to be more verbose and basic, which pulls against leanness.
- No human has ever been observed reading a claim, puzzle or wave file, so my four-question table is my own walk-through, not his words. I flagged this as a puzzle.

**Proposals (CONJECTURE; each would still need to be filed as a claim; report section 6)**
- P1: a short `research-pi.md` paragraph telling the PI to end each wave or decision with a `wrap_up` that carries the pending ask. It would also have the PI gloss ids such as `SA<n>` on first use.
- P2: reorder `/lab-status` to Doing / Found / Cost / Needs you, with minutes and output tokens.
- P3: a `## For you` section in the wave template.
- P4: fill the Returned column with the report path.
- P5: a generated status board. Mermaid has a known failure at 2947f9dc:1769.
- P6: a consolidated "current" report with no history as the PI's closing artifact.
- P7: human attention minutes derived from prompt timestamps.
- Left out unless the human asks: dashboards, trace viewers, external observability servers, alert hooks.

**Puzzles I would look at next (details in the puzzle file)**
- -2 and -5: no human-reader evidence exists for lab files, and reader level is topic-dependent. Neither `framing.md` nor the lab records it.
- -1 and -4: the button/`wrap_up` channel is Desktop-only and undocumented in the plugin, and I have not measured how much decision content a click carries.
- -7: claim `scope:` is not carried into chat summaries or outsider artifacts (the slide-headline case).
