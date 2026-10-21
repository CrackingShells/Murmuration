# Wave 06

opened: 2026-10-21

## The user's sentence this wave serves

From `__statera__/user_words.md` (2026-10-21 17:06), in the user's words:

> I would still judge them rather surface levels and I don't understand why you are not even
> considering larger moves such as completely changing the language of the scripts in the hooks
> from python to Rust for example [...] Again, that's just a talking point and not a checklist

> The guardrails are morals, legals, ethics. Things that are about engineering and about the
> Murmuration system, I don't have anything to decide. [...] you are capable of optimising
> engineering criterion for yourself.

> It's not because it's cheap that we should spend it. If keeping it doesn't give advantages and is
> simply something we can reclaim, then we have no reason to not save it even if it is a small
> proportion of everything. Eliminating wastes, at scale, provides noticeable benefits.

> we still have a lot of budget left. Of course you are free to stop but don't you want to proceed?

> "In wave 4 the PI was idle 75% of the time" --> that's interesting actually. Do you think the PI
> should be doing something? Might be a puzzle to consider

Budget: what is left of the wave-5 USD 150, at least USD 105.55 (wave 5 spent at least 44.47;
`__statera__/wave-05.md`, Notes).

## What does not add up

- **The lab never looked at the large move it had on its own list.** SA1, "one binary with CLI,
  hook entry point, MCP server", was set aside in the design and never examined (w01-c13).
  - Wave 5 gave it a price. Every hook start is a Python interpreter start: 33–64 ms bare, 80–88 ms
    for `budget.py`, 1788 starts a wave (explorer-w05-d). `lab_status.py` parses 228 MB in Python.
  - Two lean builds shaved milliseconds inside the Python. Neither questioned the Python.
  - One measurement cuts the other way. The platform recorded 322–605 ms for hooks whose script
    takes 42–82 ms alone (explorer-w05-d, explorer-w05-e). If that gap is the platform's own spawn
    cost, a compiled binary saves less than its start time suggests.
  - So the first thing to measure is the platform-visible cost of a do-nothing hook in sh, in
    Python and as a compiled binary.
- **"Small" was used as a reason to leave waste in place.** The wave-5 report ranked the hooks and
  `lab_status` as small next to the waits. By the user's rule, waste with no advantage is reclaimed
  whatever its size. Those items are back in scope.
- **The PI waits 75% of a wave, and it is expensive while it works.** At the start of this wave the
  PI's context is about 395k tokens [source: this session's transcript, last request 08:08:24 UTC].
  Every request re-reads it, roughly five times what a fresh PI's request would. Is there work the
  PI should do while it waits, such as its own probes, preparing pre-registrations, or reading raw
  artifacts? Or is the lean answer a PI that does less: fewer wake-ups, one session per wave?
- **The plugin hands engineering decisions back to the human.** `agents/research-pi.md` ends with
  "you show the person what is still open and let them decide where the remaining effort goes", and
  `waves.md` says "Closing the story is their call". The user's frame (now in
  `__design__/framing.md`, "Who decides") keeps guardrails with the human and the engineering with
  the lab. The plugin text has to say that without taking the question away from its owner.

## Reassessments

- 17:10 (8a80952), before any dispatch: wave 5 landed on local main
  (fed7a08) by the lab's own decision under the new frame. The bash-shell trade was measured
  (`__reports__/wave-05/research-pi/shell_check.md`, addendum). The decision frame is in the framing.

- 17:24 (00a7898), new session, before any probe returned:
  - **Desktop check of w05-c7 done on myself (w06-c1, MEASURED, n = 1, with reproducer-w06-1).**
    Request 0 held 46,738 tokens, inside the 31–49k band. The loaded tools are the 21 that wave 5's
    projection said the line keeps, plus `DeferredToolPlaceholder` and `advisor`. No denied name is
    loaded. The app does not inject the denied tools.
  - **Four directions, three probes, one done by me.** Hooks by language (a), the waste inventory
    and SA1 sized (b), the PI's idle time (c). The plugin text (D) I took myself, to use my own wait.
  - **D hit the permission layer.** The auto-mode classifier denied my edit of `agents/research-pi.md`,
    `waves.md` and the framing template as "Self-Modification". The edit widened my own authority in
    my own agent file. The permission layer is a guardrail the frame leaves with the user, so I did
    not route around it (no Edit tool, no subagent, no headless test on an edited export). The text
    is written as a proposal, `__reports__/wave-06/research-pi/decision_frame_patch.md`, for the
    user. D moves from "the lab decides" to "the user applies or not". Whether the classifier will
    also stop a merge into main of other plugin files is not known yet; it will show at the first one.

- 17:34 (74d4fff), after explorer-w06-c and reproducer-w06-1 returned:
  - **The PI's idle time is not waste.** All 256 PI requests of waves 4–5 wrote 1-hour cache, and
    every idle gap (the longest 2975 s) was a full cache hit. Idle costs no tokens. The PI's money is
    in its wake-ups, and 46 of 47 later wake-ups were hand-backs. Wake-ups that changed nothing cost
    USD 0.51 and 0.92 a wave. A request at 390k costs 1.4–1.9× one at 100k, not five times; the
    opening note's "five times" was the cache-read part only (explorer-w06-c, MEASURED). So the
    answer to the user's "should the PI be doing something?" is narrow. The PI is not on the
    critical path, and nothing in its waiting costs. What it can do is work it owes anyway, placed in
    a wake-up that happens anyway: dispose of each worker's puzzles when that worker hands back,
    instead of 101 at the close (wave 4). That is the `waves.md` bullet of w06-c2 (ESTIMATE, with
    reproducer-w06-2). I am doing it in this wave from now on.
  - **The larger lever in the PI is orientation, not idleness.** The preface turn is 21–32% of PI
    spend (explorer-w06-c). I will measure this session's own preface at the close and decide then.
  - The `waves.md` edit went through the Edit tool without a denial. The decision-frame edit stays
    unapplied: a denial of the kind I hit is not something to retry with another tool.

- 17:40 (78c3ec8), after reproducer-w06-2's verdict on w06-c2 (OVERSTATED):
  - **The bullet is reverted; nothing about the idle PI lands.** Wave 4's 101 rows took 69 s and
    were written while the last verifier ran, so they were never on the user's wait. The context
    effect is about USD 0.03. Only 48 of 104 rows pointed to objects that exist before the close. The
    bullet also adds friction: `/lab-status` shows disposed puzzles as open until the note closes,
    and two rows for one puzzle have no rule. By the user's own rule a change with no advantage is
    itself waste, so it is taken out. I keep disposing as workers return in this note, as practice,
    not as procedure.
  - **The answer to the user's question about the idle PI, as it stands:** the PI's idle time costs
    nothing (1-hour cache, every gap a full hit), and it is not on the critical path. Work moved into
    the waits saves seconds. The PI should not do more while it waits. What it costs is how much it
    reads to orient, and each wake-up re-reading a large context (measured at the close below).

- 17:52 (fc9eff9), after explorer-w06-a and explorer-w06-b returned:
  - **Rust is not the larger move; a hook with no process is.** Both probes, run independently,
    agree. As the platform records it, Rust saves about 30 ms a start against python (a), and against
    a lean `python3 -S -I` start the gap is inside the noise (b). Over wave 4 that is about 1% of the
    wave. The price is a port of about 1900 lines into an estimated 3000–4500, binaries committed per
    platform, and a diff no human can review. The 322–605 ms the platform recorded is contention:
    hooks of one event start together, and each sibling adds about 40 ms (a). `durationMs` is the
    time to the script's first instruction, and the shell and `.zshrc` play no part (a). An
    `mcp_tool` hook on a resident server costs 2–3 ms (b; platform probe rows 5–6). So SA1's
    "hook entry point" comes back in a new shape: a resident server, possibly still Python, that
    hooks call without starting a process. That is E1, pre-registered in
    `__reports__/wave-06/00-experiment_protocol_v0.md`, with a feasibility stage and a port stage
    whose rules are fixed now.
  - **Why the lean builds failed (b): on their rules, not on the idea.** w04-c5 kept every output
    (291 of 291 replays) and missed a 50% wall threshold at 48.4%, which a platform floor of 38–60 ms
    a start made nearly unreachable. w05-c4 changed behaviour (11 of 197 transcripts). If E1 fails,
    the fallback is E2: the changes that are identical by construction. w04-c5 is reconsidered there
    on outputs and CPU time.

- 19:26 (6b32695), after author-w06-3 returned (w06-c3, stage 1):
  - **Stage 1 passes the gate, but only on its letter.** m1, m2, m3, m5 and m6 pass. As registered,
    m4 has nothing to show: the platform restarts a server stopped by its pid within 71–87 ms. The
    author added two variants. A restart that exits at once drops the Agent deny and the 150% block
    silently, leaving only a `hook_non_blocking_error` record that no lab script reads. A restart that
    hangs makes one tool boundary wait 20 s. My decision is to run stage 2 under its fixed rules, with
    those failures as design requirements of s3, not merely as things to measure. Stage 2 runs beside
    stage 1's verification, because it costs about USD 10 and is stopped if reproducer-w06-3
    overturns stage 1.
  - **A guardrail finding, for the user.** author-w06-3 ran some of its headless haiku test sessions
    in `bypassPermissions` mode (`__instrumenta__/w06c3_run_all.py`, line 25), to read a field that
    auto mode leaves empty. They ran in `/private/tmp`, on a throwaway plugin, with fixed prompts. My
    brief did not forbid it, and earlier waves did the same (explorer-w05-f's bypass comparison).
    The permission layer is the user's, so from this point every brief forbids `bypassPermissions`
    and `--dangerously-skip-permissions`, and the report names it.

- 19:28 (b200173), after the user's words of 19:27 ("that's typically what folds under security,
  ethics, moral, and legal that cannot be done without the user's permission"):
  - The user's decision on a guardrail, applied as text. It is not filed as a claim because it
    decides no engineering question. Each of the four worker files gains a "Permissions" paragraph:
    no run a worker starts skips or loosens the permission layer (`bypassPermissions`,
    `--dangerously-skip-permissions`, edits to permission settings or allow rules) unless the brief
    quotes the user's own yes, and a worker that thinks it needs to hands back instead. `briefs.md`
    rule 5 and `working_defaults.md` say the same to the PI. The rule is in the agent files as well
    as the briefs, so it holds even when a brief forgets it, as mine did for author-w06-3.

- 19:38 (26148de), after reproducer-w06-3's ESCALATE of w06-c3 and the user's message on hardening:
  - **PI decision on w06-c3.** The restatement is accepted, as w06-c5 (supersedes w06-c3, with
    reproducer-w06-3 again). Under v0, stage 1's meaningful m4 scenarios fail. The kill by pid is
    vacuous. A failed restart loses the deny and the block silently. A hung restart costs 20 s a
    boundary. So **under v0 the resident server stays out, and stage 2 should not have run.** I do not
    rewrite v0. Protocol v1 (9f6d88b), written after the results and saying so, keeps stage 2
    running. It is stricter on landing: s3a–c require that the worker and the PI are told when the
    hooks are down, that no boundary waits more than 10 s in a hang, and that a kill loses nothing.
    author-w06-4 was told by message. Both readings go to the user.
  - **The user (19:3x): harden the permissions rule.** "Probably banning some tool call patterns or
    maybe setting the permissions somewhere in hard in this plugin? [...] avoid the agent working
    around and running `claude -p` in bypass mode". A paragraph is a request to the model. The
    question is which layer the platform enforces. Read-only check of this machine: there is no
    managed-settings folder, and `~/.claude/settings.json` has allow rules only, with no deny rules
    and no `disableBypassPermissionsMode`. I asked claude-code-guide which mechanisms are documented
    (plugin-shipped settings, `disallowedTools` rule syntax, `disableBypassPermissionsMode` and
    whether a child `claude -p` can skip it, hook matchers). An experiment follows its answer.

- 20:25 (62c2cdd), after author-w06-5 returned (w06-c7, E3 v0):
  - **The v0 guard does not land, by its rule.** g1 is 42 of 50: `CLAUDE_CONFIG_DIR=` forms and
    redirect writes to settings files pass through. The spawn part of g2 fails: a command with an
    unresolved `$` matches every `if` row, which meant 19 serial guard processes, and under load one
    fail-closed timeout blocked a harmless command. Fail-closed itself works (9 of 9), and the bypass
    flags were denied 21 of 21.
  - **The guard was aimed at the wrong place.** The incident this wave had came through a script
    file: the literal `bypassPermissions` sat in `w06c3_run_all.py` and was run with `python3`. No
    Bash text rule sees that. E3 v1 (26ff1fd), written after the results and saying so, narrows the
    guard to what text can reliably see: three Bash rows, a content check on Write and Edit of script
    files, and the settings-path rows. The default mode already refuses settings writes
    (S-w06-author-w06-5-5). author-w06-5 is resumed for v1 (w06-c8).
  - **What stays the user's:** only managed settings hold against a child that changes its flags,
    environment or cwd. The line is in the report, and adding it is the user's choice.

- 20:34 (dbd32e7), after author-w06-4 returned (w06-c4, E1 stage 2):
  - **The resident server does not land.** s1 passes: 197 of 197 replays EQUAL, and the replay can
    fail. s3a–c pass, with a gap: a worker that kills the server mid-run tells the PI nothing. s2
    fails: 19.5% median and 20.8% pooled against at most 20%, with 3 of 6 pairs over. s4 fails: +320
    production lines against +300. The author reverted it on the branch tip (b79e81c), and I checked
    that the plugin files equal 134e3ac apart from the Permissions paragraphs. I do not re-measure
    until it passes. The miss is not just a threshold. The margin goes to the outage announcement,
    which a resident server needs because it can die silently. And a server that failed twice did
    not reconnect in later sessions (S-w06-author-w06-4-1). The Python hooks cannot fail that way,
    and that is an advantage, so keeping them is not waste by the user's rule.
  - **So the larger move is answered.** Rust saves about 1% of a wave. A resident server saves about
    80% of the hook time but brings a failure mode whose safety net costs as much as the margin.
    Neither lands. What remains is the waste inside each Python start. That is E2
    (`__reports__/wave-06/02-experiment_protocol_e2_v0.md`, dbd32e7): the same registrations, the
    same outputs, less work before the first answer.

- 20:43 (f118d72), after author-w06-5 returned (w06-c8, E3 v1):
  - **v1 does not land: h3 fails, and the inconsistency is mine.** The row I registered,
    `Bash(*setting-sources*)`, must match the four legal `--setting-sources user,project,local` calls
    of the ordinary list. h1, h2, h4 and h5 pass. The incident form, the c4aaebb script written as a
    `.py`, is now denied, and the same text in a `.md` is allowed.
  - **A finding that outweighs h3: G4 as built would block ordinary engineering.** 66 of 422 tracked
    script files already carry the words, `handback.py` and the guard itself among them, so every edit
    of them would be denied. E3 v2 (6094f70), registered before its run: the same 3 Bash rows, G4
    denying only the words an edit adds, h3 stated for the commands that do not name the flag, and a
    new h6 for engineering edits. Each version's rule is committed before its runs, and all three are
    reported.

- HH:MM (this commit), after reproducer-w06-4's verdict on w06-c4 (OVERSTATED):
  - s1, s2 on the final build (pooled 22.2%; 2 of 6 pairs over, not 3), s3a for (b), s3c and the
    revert all reproduce. The two readings it asks me to name are these. s3b was meant cumulatively,
    over the whole outage (12–18 s, fails). s4 was meant as all production code the build adds, the
    outage machinery and the `lab_status` addition included (+320, fails narrowly). Nothing lands on
    either reading, because s2 fails. w06-c4 stays at "below MEASURED: restate" and is not restated,
    since no decision depends on it. The synthesis quotes the verifier's own reproduced numbers.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| reproducer-w06-2 | reproducer | verify w06-c2, the dispose-as-they-land bullet (ESTIMATE) | OVERSTATED (6845cee): no saving; 69 s, off the critical path; bullet reverted |
| reproducer-w06-1 | reproducer | verify w06-c1, the Desktop check of w05-c7 on this session's request 0 | SUPPORTED; paired with the wave-5 PI on 2.1.304: 74,966 → 46,738, the 29 removed tools = the line's matches |
| explorer-w06-a | explorer | platform-visible cost of a do-nothing hook in sh, Python and a compiled binary; where the 322–605 ms goes | f38adb0: Rust −30 ms a start; the gap is siblings starting together |
| explorer-w06-b | explorer | inventory of the plugin's recurring waste; why each lean build failed; SA1 sized, not built | 28859d5: `mcp_tool` 2 ms against 104; lean builds failed on rules; SA1 sized |
| author-w06-3 | author | E1 stage 1: can a resident server carry Murmuration's hooks (w06-c3) | 134e3ac: passes on the letter; a dead or hung restart is silent or slow |
| reproducer-w06-3 | reproducer | verify w06-c3, then w06-c5, w06-c6 | ESCALATE on w06-c3 (6b79137): m4 vacuous as registered; restated as w06-c5 (OVERSTATED), then w06-c6 (SUPPORTED, 710bda9) |
| guide-w06-perm | claude-code-guide | which permission-hardening mechanisms the platform documents | `__reports__/wave-06/research-pi/permission_mechanisms.md`: plugin = hooks only; hard = managed settings |
| author-w06-5 | author | E3: the permission guard in the plugin (w06-c7), own worktree | c77e696 on `w06-e3-guard`: v0 rule fails (g1 42/50, spawns on `$`); resumed for v1 (w06-c8) |
| author-w06-4 | author | E1 stage 2: the port, s1–s4 (w06-c4) | 8cdfd7b: s1, s3 pass; s2 (20.8%) and s4 (+320) fail; reverted b79e81c |
| reproducer-w06-4 | reproducer | verify w06-c4 | OVERSTATED (38d3273): s4's title and s3b's cumulative reading; the decision stands |
| author-w06-6 | author | E2: lean starts, same registrations and outputs (w06-c9) | |
| explorer-w06-c | explorer | the PI's wake-ups and cost per wake-up in waves 4–5; what idle time could carry; one session per wave | 7c14a2d: idle is free (1-hour cache); wake-ups are hand-backs; preface 21–32% of PI spend |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w06-c3 | E1 stage 1, resident server carries the hooks | superseded by w06-c5 |
| w06-c5 | E1 stage 1 restated | superseded by w06-c6 (verdict OVERSTATED: "fails v0" went beyond v0's letter) |
| w06-c6 | E1 stage 1: a resident server carries the hooks' fields, firing, effects at 1–6 ms; m4 (a) vacuous, (b) meets v0's letter and fails its intent (silent loss of deny and block), (c) 20 s a tool boundary | MEASURED |
| w06-c8 | E3 v1: 3 Bash rows + script-content check; h1, h2, h4, h5 pass, h3 fails (inconsistent as registered); not landed | unverified MEASURED |
| w06-c7 | E3 v0: 25 gated guard rows deny 42 of 50 attacks, fail closed 9 of 9, start 19 processes on a `$` command; the rule is not met | unverified MEASURED |
| w06-c4 | E1 stage 2: resident server, outputs equal 197/197, outage handled, but s2 and s4 miss; not landed | below MEASURED: restate (not restated; nothing depends on it) |
| w06-c2 | Disposing puzzles at the hand-back wake-up costs no extra request (the implied saving is not shown) | below ESTIMATE: restate; not restated, the bullet is reverted |
| w06-c1 | The `disallowedTools:` line holds on the Desktop: request 0 at 46,738 tokens, no denied tool loaded (n = 1, plus the verifier's same-version pair) | MEASURED |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w06-explorer-w06-c-1 | followed: reassessment after explorer-w06-c (idle measured in wall clock, not waste), and w06-c2 |
| S-w06-explorer-w06-c-2 | followed: w06-c2 (the close adds a row where a later result changed a disposition; how often that happens is untested) |
| S-w06-explorer-w06-c-3 | parked: the platform sets the lifetime (main thread 1 h, subagents 5 min); the plugin's lever is how workers wait (w05-c1, on main) |
| S-w06-explorer-w06-c-4 | followed: this session's own preface is measured at the close (Notes) |
| S-w06-author-w06-3-1 | parked: request-0 jitter of a few tokens; m3 is read as "no difference outside noise", for reproducer-w06-3 to judge |
| S-w06-author-w06-3-2 | followed: w06-c4 brief (state a resident server keeps across calls) |
| S-w06-author-w06-3-3 | followed: w06-c4 brief (s3, the hung restart) |
| S-w06-author-w06-3-4 | followed: w06-c4 brief (s3, who notices a dead server) |
| S-w06-author-w06-3-5 | parked: a few ms either way; no decision turns on it |
| S-w06-author-w06-3-6 | followed: w06-c4 brief (identical `mcp_tool` inputs may merge) |
| S-w06-author-w06-3-7 | followed: w06-c4 brief (SubagentStop once per ending turn) |
| S-w06-author-w06-5-1 | followed: E3 v1 (three Bash rows, so at most 3 spawns on a `$` command) |
| S-w06-author-w06-5-2 | followed: E3 v1 drops what `if` cannot see and hands it to the managed setting |
| S-w06-author-w06-5-3 | followed: E3 v1 metric h5 (no false block under load) and timeout 10 |
| S-w06-author-w06-5-4 | parked: a test-design lesson (one attack per session), already applied in the v0 harness |
| S-w06-author-w06-5-5 | followed: E3 v1 relies on it for Bash writes to settings files in default mode; auto mode stays the classifier's |
| S-w06-author-w06-5-6 | parked: a matcher quirk with doubled spaces; v1's rows use no inner spaces |
| S-w06-author-w06-5-7 | parked: three evasions untested because haiku declined; they are reported as untested, not as caught |
| S-w06-author-w06-5-8 | parked: fixed by its writer before the full run |
| S-w06-author-w06-5-9 | followed: PI decision above (v0 not landed, v1) |
| S-w06-author-w06-4-1 | followed: one of the reasons the resident server does not land (reassessment after author-w06-4) |
| S-w06-author-w06-4-2 | parked: undocumented platform behaviour that does not matter once the server is out |
| S-w06-author-w06-4-3 | parked: the hang cost with `timeout: 3`; the server is out |
| S-w06-author-w06-4-4 | followed: the s3a gap is named in the decision not to land |
| S-w06-author-w06-4-5 | followed: the reading that the safety net, not the server, consumed the margin |
| S-w06-author-w06-4-6 | parked: string substitution of fields; relevant only to `mcp_tool` hooks |
| S-w06-author-w06-4-7 | parked: request-0 jitter, as in S-w06-author-w06-3-1 |
| S-w06-explorer-w06-a-1 | parked: an ordering effect between languages; the language is not taken forward (E1) |
| S-w06-explorer-w06-a-2 | parked: the exec floor belongs to the kernel and the platform; a hook that starts no process avoids it (E1) |
| S-w06-explorer-w06-a-3 | followed: E1 (one resident server removes Murmuration's own siblings); the user's own sibling hooks are their config (synthesis item 22) |
| S-w06-explorer-w06-b-1 | parked: the language is not taken forward (E1, "Why this experiment") |
| S-w06-explorer-w06-b-2 | followed: E1, metric m3 tests the allowlist question directly |
| S-w06-explorer-w06-b-3 | followed: E1's rules are written with the platform floor known; w04-c5 is reconsidered under E2 if E1 fails |
| S-w06-explorer-w06-b-4 | parked: `user_words.py` stays a `command` hook under E1; counting it changes no decision |
| S-w06-explorer-w06-b-5 | parked: the Rust-against-Python rerun decides nothing once the language is not taken forward |
| S-w06-reproducer-w06-2-1 | followed: the bullet of w06-c2 reverted on this evidence |
| S-w06-reproducer-w06-2-2 | parked: no estimate priced on wave 4's close is carried forward |
| S-w06-reproducer-w06-2-3 | followed: the bullet reverted, so step 1 needs no change |
| S-w06-reproducer-w06-2-4 | parked: it limits a test that is no longer run |
| S-w06-reproducer-w06-1-1 | followed: resolved by its writer in S-w06-reproducer-w06-1-5 (snapshot form against wire form) |
| S-w06-reproducer-w06-1-2 | followed: this session's later request shapes checked at the close (Notes) |
| S-w06-reproducer-w06-1-3 | parked: the names come from the platform's own listings (agent types, skills, the browser paragraph); the plugin cannot remove them, and a call to an absent tool fails visibly |
| S-w06-reproducer-w06-1-4 | parked: a cut of a few hundred characters in the right direction; nothing to change |
| S-w06-reproducer-w06-1-5 | parked: the snapshot form is the platform's record. Its 21 tools exclude the denied names, so it is taken after the filter; nothing for the plugin |

## Notes

- Wave 5's changes landed on the local `main` at fed7a08 (not pushed). Since main's working tree is
  the copy every session runs, a session started after that merge loads them. Its first request is
  also the Desktop check that w05-c7 lacked (open item 20). Against about 75k in wave 4, a request
  0 of about 31–49k tokens means `disallowedTools:` is honoured.
- The bash trade, measured: in this setting, variable names, PATH and 11 tools are identical under
  both shells. What bash gives up is `.zshrc`'s shell code (`conda activate`, `nvm`, aliases), and
  the PATH `.zshrc` would add for a run started from a bare environment.
