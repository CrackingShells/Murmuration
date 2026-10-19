## S-w01-research-pi-1
The `UserPromptSubmit` hook (`scripts/user_words.py`) stored a `<system-reminder>` block, injected
by the desktop app to say the session runs in a git worktree, as part of the user's verbatim words.
The pasted-content wrapper `<pasted_content id=…>` was stored too. The file that promises "prompts
as the user typed them" now holds platform text the user never typed.
refs: __statera__/user_words.md (entry 2026-10-19 10:56, first five lines); scripts/user_words.py

## S-w01-research-pi-2
This session was opened by the desktop app in a worktree on `main` (9ecbc6a), which has no lab; the
lab lives on branch `roadmap/reflective_run` in the main checkout. The hook nevertheless appended
the prompt to the main checkout's `__statera__/user_words.md`, and the app then refused my writes to
the main checkout. I fast-forwarded the worktree branch to `roadmap/reflective_run` and copied the
hook's entry over. The lab state is git-tracked files in one checkout; a session started anywhere
else (worktree, other branch) does not see it, and nothing told me. Also: `__scrupuli__/` and
`__pondus__/` did not exist after checkout, because git does not track empty directories.
refs: git log of claude/murmuration-system-optimization-8cff9e (ff to 79fb6cf); main checkout `git diff __statera__/user_words.md`

## S-w01-research-pi-3
`/lab-status` reported "no usage records" for spend: `scripts/lab_status.py` reads transcripts from
`~/.claude/projects/-Users-hacker-Documents-src-CrackingShells-Murmuration`, while this session's
transcript is under the worktree's project folder `-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e`.
Cost tracking keyed on the project path misses every worktree session.
refs: output of `python3 scripts/lab_status.py` at 2026-10-19 ~11:00; scripts/lab_status.py

## S-w01-research-pi-4
Only `explorer` sets `maxTurns` (60). Author, reproducer and proof-adversary have none, although
v5 listed `maxTurns` as the pair-loop backstop ("Pair loops never converge → the verifier owns
termination; maxTurns").
refs: agents/*.md frontmatter; __reports__/genesis/12-architecture_v5.md §Risks

## S-w01-research-pi-5
The second prompt of this run (11:04, the user confirming the budget) was again appended to the
**main checkout's** `__statera__/user_words.md`, not to this worktree's lab. So the hook resolves
the project as `CLAUDE_PROJECT_DIR` (the repository the app was opened on), not the session's
worktree: in a desktop-app worktree session the lab's record of the user's words never reaches the
lab that is running. The 11:04 entry also quotes my own sentence back (`> I set a working budget…`),
which the user's reply-to-quote UI inserted; it is stored as the user's words.
refs: /Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md (entry 2026-10-19 11:04); scripts/user_words.py `project_root`

## S-w01-research-pi-6
The platform already hands the PI a per-run ledger line: the task-notification for explorer-w01-e
carried `subagent_tokens 219458, tool_uses 57, duration_ms 467684`. That is most of v5's
`__expensa__` run event (SA3), delivered to the main thread for free, yet the lab writes it nowhere
and `/lab-status` re-derives spend from transcripts by a path that misses worktree sessions
(S-w01-research-pi-3). Is the notification's `usage` block also visible to a hook
(PostToolUse on the Agent tool, SubagentStop), so it could be appended without the PI's help?
refs: this run's transcript, task-notification for task a53e063b007b7a428 (explorer-w01-e)

## S-w01-research-pi-7
My quick count of non-sidechain user entries in 82e8a947 (filtering only the obvious wrappers) gives
69; explorer-w01-e reports 28 human prompts. The difference is what counts as "the human's words",
the same question as S-w01-research-pi-1. explorer-w01-d is counting independently; compare.
refs: inline script in this run (PI, ~11:15); __reports__/reflective_run/w01/explorer-w01-e/prompts_82e8a947.json

## S-w01-research-pi-8
explorer-w01-c hit `maxTurns: 60` after 62 tool uses, 281k tokens and 10.4 minutes, and returned
nothing: no report, no puzzle file; the platform said only "stopped at its 60-turn limit". The
turn limit is a hard stop with no wrap-up turn, so the work is stranded until the PI notices and
resumes it. This is exactly the case v5's SubagentStop presence gate (SA6) targeted, but in a
different shape: the missing thing is not a label or a puzzle but the whole deliverable. Does
SubagentStop fire at a maxTurns stop, and can a hook there (or the brief) make an agent write as it
goes, so a limit stop leaves a usable partial report?
refs: this run's transcript, task-notification for task a1f4458ce75dacdec (explorer-w01-c); agents/explorer.md `maxTurns: 60`

## S-w01-research-pi-9
author-w01-5 found that 43–64% of each explorer's cache writes come in 7–13 spikes of more than 8k
tokens, lined up one for one with `skill_listing` attachments in explorer-w01-c (about 0.35 of its
2.92 USD), a larger line than any resume. explorer-w01-b measured the skill listing at about 30k
characters in every worker's start context, ten times the brief. This user has about 100 skills
installed; the workers need one (`research-loop`, preloaded). If the listing is re-injected mid-run
(why? new skills appearing as MCP servers connect?), leanness is decided by the user's skill count,
not by the plugin. Is there a per-agent way to suppress or shorten the listing for workers?
refs: __reports__/reflective_run/w01/author-w01-5/cw_spikes.txt; __reports__/reflective_run/w01/explorer-w01-b/startctx.csv

## S-w01-research-pi-10
Every headless `claude -p` run the team launched inside this repository added a local-scope install
entry for `murmuration@murmuration-local` to the user's `~/.claude/plugins/installed_plugins.json`:
at 11:4x there were 90 entries for that plugin, about 85 of them pointing at scratch `work/`
folders of explorer-w01-f, author-w01-1 and author-w01-2 (file now 61,863 bytes). The study's own
verification method (tiny headless runs) writes into the user's global plugin state, outside the
project, and nothing in the plugin or the briefs warns about it. The PI has not edited the file:
cleaning it is the user's call. Why does a run in a subfolder register a new local install, and
does the registry ever get pruned?
refs: ~/.claude/plugins/installed_plugins.json (read-only inspection, key murmuration@murmuration-local); __scrupuli__/wave-01-author-w01-4.md puzzle 2

## S-w01-research-pi-11
author-w01-3 edited the head of w01-c3 (title scope, a removed sentence, the TOTAL line) while
reproducer-w01-3 was mid-exchange, and asked the verifier to escalate if that counts as changing
the statement. The claim file is plain markdown with no history inside the lab, so a verifier's
"independent result" can end up attached to a statement it never saw. The rule "a verdict changes
only by pointing to a new artifact" has no twin for the author's side. The PI only committed the
first snapshot of `__pondus__/` after this happened (commit following b497813), so the pre-edit
text of w01-c3 is not recoverable from git.
refs: __pondus__/w01-c3.md; author-w01-3's second hand-back; git log -- __pondus__/

## S-w01-research-pi-12
explorer-w01-d's `prompts.csv` caps `human_text` near 420 characters (18 of 55 prompts cut), and
author-w01-6 built its word checks, rank figures and token estimates on that column before both of
its verifiers caught it. A derived table that silently truncates its main text field was passed
from explorer to author as evidence, and the author's corrected counts fell by half or more (w01-c6
"clearly pre-empted" 1 → 0; w01-c7 asks removed 4 → 1–2, prompts removed 5 → 2). Raw-artifact
pointers in briefs should say which columns are lossy; nothing in the brief template asks
explorers to state that.
refs: __reports__/reflective_run/w01/explorer-w01-d/prompts.csv (column human_text); __reports__/reflective_run/w01/author-w01-6/fulltext.py, full_text_check.txt

## S-w01-research-pi-13
author-w01-1 found that the four reports the PI "saved verbatim" with `save_handback.py`
(a, b, c, f) are not the agents' text: each ends with 652–807 characters of harness frame after
`</agent-message>`, and b, d, f contain 4–8 control tags the harness rewrote `<` → `<\`, which is
lossy. The header line the PI wrote says "Text unchanged". So the PI's own provenance statement on
those files is wrong, and the files cannot be used to re-derive exact agent text. The PI's fix
(longest rendering wins) traded one defect for another without checking the result against the
subagent's own transcript. Corrective: a note in the wave note, and the files' headers should say
"harness rendering of the hand-back", not "text unchanged".
refs: __reports__/reflective_run/w01/explorer-w01-{a,b,c,f}/report.md (first line); __reports__/reflective_run/tools/save_handback.py; author-w01-1 §2 "Against the PI's saved reports"

## S-w01-research-pi-14
reproducer-w01-10 asks for a fact that does not move when an agent's shell `cd`s: both the shipped
rule (CLAUDE_PROJECT_DIR first) and the proposed one (payload `cwd` first) fail one worktree case.
A candidate the team has not tried: the hook payload's documented `transcript_path`. Its project
folder name encodes the directory the session was launched in (this run:
`-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e`,
the worktree), and it does not change when the shell moves. Matching it against `git worktree list`
would pick the session's own checkout. CONJECTURE: the encoding is lossy (`/` and `.` both become
`-`) and undocumented; untested on the Desktop, which is exactly the case in question.
refs: this run's transcript path; __reports__/reflective_run/w01/reproducer-w01-10/rule_check.py; __pondus__/w01-c10.md

## S-w01-research-pi-15
For a claim the PI authors, the verifier's questions to "main" are queued until the PI's turn ends.
reproducer-w01-11 closed its verdict on w01-c11 with "no answer" seconds before the PI's reply was
delivered, and was then resumed with that reply. The protocol says "if a message cannot be
delivered or gets no answer, log 'no answer'", but a busy main thread is neither undelivered nor
silent; it is just late. So PI claims get a weaker exchange than worker claims by construction.
refs: __pondus__/w01-c11.md (verdict section: "no answer"); this run's transcript, the PI's SendMessage to reproducer-w01-11

## S-w01-research-pi-16
The PI's snapshot commits staged `__reports__/reflective_run/` wholesale, including author-w01-2's
raw headless-run folders (422 files holding the user's email and organization id) before anyone
looked inside them; author-w01-2 redacted the working copies only after the commit. The PI rebuilt
the two local commits without those folders (now 8ffd44e on top of b497813; nothing was pushed);
the superseded objects remain in the local reflog until garbage collection. Raw platform outputs
(hook payload snapshots, OTLP bodies, init events) carry account identifiers by default, and
nothing in the briefs or the lab tells workers that.
refs: git reflog (efb8948, 892ec7e, 8c46b00 superseded); __reports__/reflective_run/w01/author-w01-2/.gitignore
