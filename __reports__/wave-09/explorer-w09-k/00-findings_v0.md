---
type: findings
wave: wave-09
author: explorer-w09-k
date: 2026-10-26
version: v0
decision-required: none
---

# How the PI takes in its team's work: a metric for agent systems (v0)

Scope note (first line, as asked): I stayed inside the brief. Two additions it did not name: a second-coder marker in Figure 1 (the verifier's rule R2, re-run by my script) and a by-role split of the banner comparison, which `w09-c5` says it does not cover (Section 6).

A reader new to the lab can start here. The metric is simple: when a worker agent hands its report back to the lead agent (the PI), does the lead open any of the worker's files, or does it act on the message alone? Everything below counts that, from transcripts, with scripts that run in a few seconds and cost no API calls. Labels follow the research-loop skill. Numbers carry a source. Where a number is in `__pondus__/w09-c5.md` (MEASURED, verifier reproducer-w09-2 SUPPORTED) I say so; everything else I computed is "script output, in no claim, unverified" and may not be read above that.

## Result

- **What is measured.** In the PI's main-thread transcripts of waves 5-8, a hand-back from an explorer was followed by a raw open of an artifact in the same PI turn in 18 of 27 wakes as coded (21 of 27 with a known classifier defect masked); from an author in 10 of 57 (11 of 57); from a verifier in 5 of 35 (6 of 35). A second coder with its own rule found 20 of 27, 11 of 58, 7 of 35. The ordering explorer above author and verifier holds on every reading; the exact shares do not [MEASURED, `__pondus__/w09-c5.md` (a); second coder CITED to the verifier's section of `__pondus__/w09-c2.md`, and re-run by me: Figure 1].
- **Over waves 1-8 pooled, the share of hand-back wakes with a raw open rose from about 1 in 5 (waves 1-3) to about 2 in 5 (waves 7-8), and part of the rise is who handed back** (explorers were 0 of 24 in wave 4, 13 of 36 in wave 8). Inside each role the intervals overlap widely [script output, in no claim: Figure 2].
- **Escalated claims were decided without opening the claim file in 12 of 14 cases checked, and in 10 of 10 reproducer wakes** (w09-c5 (c), MEASURED). Whether the decision would have differed is an explorer's CONJECTURE: 0 of 13 (explorer-w09-h). 9 of 14 decisions were restated in place, 5 were superseded by a new claim, 0 reversed [explorer-w09-h's table: an explorer's report, not a verified claim; Figure 3].
- **The platform's banner on a hand-back did not move the pooled raw-open rate** (9 of 35 against 40 of 178, p = 0.66; MEASURED, w09-c5 (e)). By role it is not uniform: explorers 7 of 7 with the banner against 16 of 29 without (Fisher p = 0.03 as coded, 0.15 masked); authors 1 of 15 against 17 of 93; verifiers 1 of 12 against 7 of 56 [script output, in no claim, six comparisons, uncorrected: CONJECTURE; Figure 4].

## 1. What the words mean

**The lab.** A PI agent (the main session) dispatches worker agents: *explorers* (gather material, write a findings report), *authors* (write a claim file) and *verifiers* (here: reproducers; check a claim independently and may *escalate* to the PI). Workers write files; they return a final message to the PI. Skill text for the PI says to open at least one raw artifact for every agent that returns [CITED: `skills/research-loop/references/waves.md`, as quoted by explorer-w09-d; explorer-w09-d dates the sentence in `waves.md` to 10-19; the string "raw artifact" first enters `skills/` at commit 00db307, 10-19 00:46, by `git log -S'raw artifact' -- skills` as I ran it].

**Hand-back.** The worker's final report delivered to the PI as a message. In the transcript it is a user-type record with `origin.kind = "peer"`, `origin.name` = the worker's name (for example `reproducer-w08-6`) and a body that begins `[Subagent hand-back] The text below is the final report of a subagent ...` followed by the report with every line indented [CHECKED on one record of the wave-8 transcript; same frame as `FRAME_END` in `__instrumenta__/w09d_turns.py`]. Newer records also carry `handback: true` and the plain report text in `handbackReportText` (seen on that one record only). Six peer messages that open "Another Claude session sent a message" (questions and verdict notes, not final reports; reproducer 0 of 6 raw opens) are left out (w09-c5 scope).

**Wake.** The PI turn that a hand-back starts: every record from the hand-back to the next user record that is not just tool results. Only wakes with at least one assistant request are counted (a hand-back queued behind other input can produce none). Role comes from the sender's name prefix: explorer, author, reproducer (called "verifier" in my figures; no proof-adversary appears in these transcripts).

**Raw open, coding rule 1 ("as coded", explorer-w09-d, rule `raw_here` in `__instrumenta__/w09d_turns.py@5bdeb78`).** In the same turn as the wake, a `Read`, or a Bash command that views or queries (cat, sed, head, tail, nl, grep, jq, awk, ls, wc, find, du, stat, diff, python3), naming a path of class worker report, puzzle file, claim file, instrumenta script, transcript or data file, older report or PI report, or a path containing the sender's name. Git calls and `lab_status` calls do not count. It need not be the artifact of the agent that just returned.
**Known defect of rule 1, named in w09-c5.** `call_info` drops the paths of any non-writing Bash command whose text contains `lab_status`, even when the same command also reads the sender's file. "Masked" is rule 1 with that substring replaced before classification. It is the more faithful reading of the same rule: 38 of 120 wakes against 33 of 120.

**Raw open, coding rule 2 (R2, the second coder, reproducer-w09-2, `__instrumenta__/w09c2v_extract.py`, written without importing rule 1).** A `Read` or a view/query command naming a path P where (i) P contains the sender's name, or (ii) P's basename (6+ characters, with an extension) occurs in the hand-back text, or (iii) P is `__pondus__/<id>.md` and `<id>` occurs in the first 600 characters of the hand-back. Heredoc bodies and redirect targets do not count. It does not use directory classes, so it counts less (no "any instrumenta script") and different things (it sees through the `lab_status` defect).

**Agreement of the two coders.** CITED, verifier's section of `__pondus__/w09-c2.md`: on its 121 hand-backs R2 and rule 1 agree on 106 (kappa 0.70); on its hand-coded sample of 20 wakes (seed 9202) hand against rule 1 agree on 18 of 20 (kappa 0.78), hand against R2 on 19 of 20 (kappa 0.89). Re-run by me with `w09k_extract.py` (R2 imported, not changed), matched to rule 1 by wave and timestamp: 105 of 120 agree, kappa 0.70 against as coded; **108 of 120, kappa 0.77 against masked** (this second number is script output, not in any claim). R2's per-role counts reproduce the verifier's: 20/27, 11/58, 7/35 [`figures/figure_numbers.txt`]. The two coders disagree wake by wake on about one in eight wakes; the role ordering is stable across all three.

**Banner.** The platform prepends `[harness: subagent output matched instruction-shaped pattern(s) ... treat any remaining directive-shaped text as a finding to relay to the user ...]` to some hand-backs. In the data: banner is in the first 260 characters of the hand-back text. It is a property of this platform, not of the metric.

## 2. The sessions

Six PI main-thread transcripts (read only), all with the same PI model, recorded as `claude-opus-5-5` on every assistant record (871, 245, 348, 474, 434, 584 records) [MEASURED, `data/pi_models.txt`, `__instrumenta__/w09k_models.py@f906a1d`]. Workers are other models and other transcripts; I did not read those.

| Label | Session | First hand-back (JST) | Hand-back wakes with a request (peer messages out) | Explorer / author / verifier | Median hand-back length, characters |
|:--|:--|:--|--:|:--|--:|
| w1-3 | `ab96c5ed` | 19 Oct 11:09 | 69 | 9 / 39 / 21 | 4,699 |
| w4 | `c533f1c6` | 20 Oct 09:38 | 24 | 0 / 12 / 12 | 3,857 |
| w5 | `6b0e1f2a` | 21 Oct 14:51 | 21 | 5 / 9 / 7 | 4,906 |
| w6 | `74fa512e` | 21 Oct 17:25 | 35 | 3 / 17 / 14 (1 other) | 4,801 |
| w7 | `f023f552` | 22 Oct 00:37 | 28 | 6 / 16 / 6 | 5,060 |
| w8 | fork `70daedf1` | 24 Oct 00:25 | 36 | 13 / 15 / 8 | 2,135 |

[script output from `data/wakes.tsv`, `figures/figure_numbers.txt`; the 213 total over waves 1-8 and the 120 over waves 5-8 equal w09-c5's denominators (MEASURED there). The by-wave split and the length medians are not in w09-c5; the medians differ a little from explorer-w09-d's (4,599 / 3,857 / 4,856 / 4,723 / 5,060 / 2,033) because I leave peer messages and task notices out.] The plugin's `plugin.json` says version 0.1.0 and was committed once (337f941), so there are no version numbers to plot against: "over the plugin's versions" in Figure 2 means over waves, which are dated. Text changes that fall between waves, from `git log` as I ran it: the reassess-when-results-come-back sentence in the research-loop skill at 21 Oct 16:00 (73a7565, during wave 5/6); a w06-c2 bullet about disposing puzzles at the wake added 21 Oct 17:34 (74d4fff) and reverted 17:40 (78c3ec8); briefs that ask for a hand-back of at most about 1,500 characters at 24 Oct 01:26 (c868be4, an hour into wave 8). Whether a PI session read any of these texts is not tested.

## 3. Figures

Every figure is regenerated by `python3 -I __instrumenta__/w09k_figures.py <data> <escalation_table.md> <ranges.tsv> <out>` (commands under Pointers); bars are exact 95% Clopper-Pearson intervals that treat wakes as independent (they are not: one PI, eight sessions, so the true uncertainty is larger). Palette: Okabe-Ito, with a different marker shape per role so print and colour-blind readers lose nothing.

### Figure 1. By sender role, waves 5-8, both codings and the second coder

![Figure 1](figures/fig1_rawopen_by_role.png)

*Caption. Share of hand-back wakes in which the PI opened a raw artifact in the same turn, waves 5-8, by who handed back. Filled: as coded; open: `lab_status` masked; grey diamond: the second coder's rule R2 on its own cut. Bars: 95% Clopper-Pearson. n = 27 explorer, 57 author (58 for R2), 35 verifier hand-backs; 120 in all. As coded and masked: MEASURED (w09-c5 (a)); R2 counts CITED to the verifier and reproduced by my script; the intervals are script output.* Explorer 18/27 = 67% [46, 84]; author 10/57 = 18% [9, 30]; verifier 5/35 = 14% [5, 30] (as coded). The explorer interval does not meet the author or verifier intervals under any of the three codings; author and verifier intervals overlap almost completely.

### Figure 2. By wave, so the change over time is visible

![Figure 2](figures/fig2_rawopen_by_wave.png)

*Caption. The same rate by wave (w1-3 is one session of three waves, 19 Oct), pooled and by role; filled as coded, open masked; numbers above the points are as-coded opens over wakes. Peer messages out. n per point as printed; explorers in wave 4 are none (that wave was an unattended night). Script output from `data/wakes.tsv`; it is in no claim (w09-c5 does not cover the pre-wave-5 per-role split), so it stands as unverified.*
Pooled, as coded: 14/69 (20%), 2/24 (8%), 4/21 (19%), 5/35 (14%), 10/28 (36%), 14/36 (39%). By role in wave 5 against wave 8: explorer 4/5 and 7/13, author 0/9 and 3/15, verifier 0/7 and 4/8. CONJECTURE: the pooled rise is in part composition (explorers made up 0 of 24 wakes in wave 4 and 13 of 36 in wave 8) and in part a rise among authors in wave 7 (5/16) and verifiers in wave 8 (4/8); no per-role change is outside the overlap of its intervals, so I do not claim a trend. I did not test whether the sentences added to the plugin between waves caused anything.

### Figure 3. Escalations

![Figure 3](figures/fig3_escalations.png)

*Caption. The 14 claims whose verifier ended with ESCALATE. Per claim: the hand-back as the PI received it (circle), the verifier's exchange section (triangle) and its whole section (square) in characters; right column: whether the PI read the claim file in the wake and what became of the decision. Background shows the fate: restated in place (9) or superseded by a new claim (5); reversed: 0. n = 14 claims (13 with a hand-back length; w01-c8's wake was not located). Source: explorer-w09-h's `01-escalation_table.md` and `out/ranges.tsv`, an explorer's report, not a verified claim.*
Read in the wake: no 12, yes 1 (w01-c5: the verdict section, lines cut at 500 characters, 2 s after the hand-back), not checked 1 (w01-c8). Medians: hand-back 4,476 characters (13), whole section 6,929, exchange 2,621 [explorer-w09-h MEASURED for sizes; my median of 13 differs from its 4,458 of the 10 delivered as messages because I include the three queued hand-backs]. w09-c5 (c), MEASURED: 10 of 10 reproducer hand-backs delivered as messages, decision stated in the wake turn, 0 of 10 claim files read before or at the wake. Explorer-w09-h's judgement that a read would have changed the decision label in 0 of 13 and the wording or follow-up in 3 of 13 (w04-c4, w07-c7, w08-c9) is an explorer's CONJECTURE and is not drawn here. Four of the 14 are not wake-checked by w09-c5 (w01-c5, w01-c8, w05-c1, w08-c1; they arrived queued or unplaced).

### Figure 4. Banner against no banner, by role

![Figure 4](figures/fig4_banner_by_role.png)

*Caption. Raw-open share in the wake, hand-backs with the platform banner (filled) against without (open), by role, waves 1-8, as coded; bars 95% Clopper-Pearson. n (banner / none): explorer 7 / 29, author 15 / 93, verifier 12 / 56, all roles 35 / 178. The all-roles row is MEASURED (w09-c5 (e): 9/35 against 40/178, Fisher p = 0.66; masked 11/35 against 44/178, p = 0.40). The by-role rows are script output in no claim (w09-c5 says it does not cover the by-role banner split); Fisher p (as coded / masked): explorer 0.03 / 0.15, author 0.46 / 0.46, verifier 1.00 / 0.36.*
Pooling mixes roles with different base rates and banners are unevenly spread (7 of 36 explorer hand-backs carried one, 15 of 108 author, 12 of 68 verifier): the pooled null result is therefore not the by-role answer. CONJECTURE: no effect on authors or verifiers (one open in each of the two bannered groups, intervals up to 32 and 39 percent); an explorer effect is possible but 7 of 7 against a base rate of 55 to 66 percent rests on seven wakes, and a masked-rule p of 0.15 and six uncorrected comparisons weaken it.

### Figure 5. One wave in time: wave 8

![Figure 5](figures/fig5_wave8_timeline.png)

*Caption. Wave 8 (session `70daedf1`, 24 Oct 2026, JST), hours since the first hand-back. Top lane: one grey bar per PI turn. Three lanes: hand-back arrivals by sender role, filled when the PI opened a raw artifact in that wake turn (masked reading), open when not. Four lanes: each raw open by the PI, bold when inside a hand-back wake turn, pale otherwise, by class of the file. n = 36 hand-backs (13 explorer, 15 author, 8 verifier), 34 raw opens. The axis is broken between 5.2 and 13.2 h, where no turn took place. Script output from `data/arrivals.tsv`, `turns.tsv`, `opens.tsv`; in no claim.*
What the picture shows: explorers returned in two early bursts (the first 1.5 h, then 3.6 h) and twice near hour 14; authors from 0.7 to 4.7 h, almost all without a raw open; verifiers from 1.1 to 4.7 h; raw opens of puzzle files, claim files and worker reports all fall in hand-back wake turns (17 of 17), only "other raw" files (older reports, PI reports, scripts, data) are also opened outside wakes (9 of 17). Raw opens in wake turns by sender: explorer 8 of 13, author 3 of 15, verifier 4 of 8 (masked; 15 of 36, as coded 14 of 36). No hand-back arrived while the PI was mid-turn in this session (0 of 36). The turn that ends the break at about 13.4 h is a human prompt (CHECKED on `turns.tsv`); that the user was away during the gap is my reading [CONJECTURE].

## 4. What is not known

- **Why.** The counts say nothing about the PI's reasons, and whether an opened artifact changed a decision. Explorer-w09-d's reading of the PI's visible text is CONJECTURE (about 9 of 72 sampled wakes changed by a hand-back or artifact; hand-coded, stratified sample, not rates).
- **Opens in an earlier turn.** A report or claim read before the wake does not count here; only the escalation claim files were checked for it (0 of 10 read before or at the wake; `ls` and `grep -c` are not reads).
- **Whether not opening was harmful.** Explorer-w09-h judged 0 of 13 label changes from a read; it read 7 of the 14 files in full and used overlap proxies for the rest, and the judgement is one reader's.
- **Whether results were stated before a worker returned.** 0 confirmed in waves 1-8 (w09-c5 (d), MEASURED count), but the detectors see only hex tokens, worker names in result-like sentences and notification-shaped text; one known case detected, so their recall is untested.
- **Independence.** All sessions have one PI model and one lab design; the intervals in the figures treat wakes as independent when they are not.
- **Causes of rate differences by role.** Explorers hand back a report folder, authors a claim file the PI wrote the brief for; "who handed back" is confounded with artifact type, brief length, hand-back length (wave 8's median halved) and wave.
- **The platform's own effects.** The banner is one; hand-back delivery as queued attachments (4 escalations) is another that the parser of `w09d_turns.py` does not turn into a wake.

## 5. How the same metric would be measured on another agent system or model

**Definitions that travel (none depends on this platform):**
1. *Hand-back*: a worker's final report delivered to the lead as an input of its own, distinguishable from a human prompt, a tool result and a status notice.
2. *Wake*: the lead's turn that this input starts: everything the lead does until the next non-tool input.
3. *Raw open*: in the wake, a tool call that brings the content of a file the worker produced or a record of its work into the lead's context. Portable form: R2 (the path contains the worker's identifier, or the path appears in the hand-back, or the id of the artifact in the first 600 characters of it), because it needs no directory convention beyond naming. Rule 1's path classes are specific to this lab's folders.
4. *Role*: from the worker's identifier or its brief; the rate is always reported per role with an exact interval and n.
5. *Same turn* is a choice: also report same-or-next turn (explorer-w09-d: 38, 17, 23, 29, 46, 54% by wave against 22, 8, 18, 16, 36, 36% same turn, as it coded with peers in).

**Transcript fields needed** (names are this platform's; any other needs an equivalent):
| Need | Field here |
|:--|:--|
| a timestamp per record | `timestamp` |
| record type, user or assistant, and one id per model message (streaming splits it across records) | `type`, `message.id` |
| who sent an input and of what kind | `origin.kind` (`peer`, `human`, `task-notification`), `origin.name`, `origin.from`, `origin.body` |
| the hand-back text itself, for banners and for path or id matches | `origin.body`, `handbackReportText` |
| the lead's tool calls: tool name and its arguments | assistant `content[]` blocks of type `tool_use`: `name`, `input` (`file_path`, `command`) |
| whether the lead's turn ended | `message.stop_reason` |
| which model is the lead | `message.model` |
| inputs queued behind other work | `attachment` of type `queued_command` |

**What must be rebuilt for another tool set.** A classification of the lead's tools into view, query, write and other; a shell-command parser that survives compound commands, heredocs and redirects (this lab's rule 1 lost 3 explorer opens of 27 to one substring, and R2 over-split awk programs until fixed: both coders needed a second version); a way to see queued deliveries (the w09d parser has no turn for a queued hand-back).

**What to hold fixed and what to report, to compare models.** Same lab protocol and skill text, same briefs, same worker roles and sizes; vary the lead model only; run each lead on the same task set. Report per-role rate with exact intervals, the role mix, hand-back length and the share of wakes with no tool call, plus the escalation measure (claim file or equivalent read before a decision on a worker's verdict). Sample size is the constraint: with 27 explorer wakes the interval is 46 to 84 percent. ESTIMATE (two-proportion normal approximation, alpha 0.05 two-sided, power 0.8, p1 = 0.2, p2 = 0.4): about 80 wakes per group to separate 20 from 40 percent; inputs and formula are the only evidence, nothing was run to check them. The per-wave table in this report shows 20 to 70 wakes per session, so one wave per model is not enough for a per-role comparison.
Hand coding: take a seeded sample (the verifier used seed 9202, n = 20) and report kappa against the automatic rule before trusting the rule.

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Hand-back wakes with a request, waves 1-8 / 5-8 | 213 / 120 (peer messages out) | MEASURED (w09-c5) | `figures/figure_numbers.txt`; `__pondus__/w09-c5.md` |
| Raw open in wake, waves 5-8, as coded | explorer 18/27, author 10/57, verifier 5/35, all 33/120 | MEASURED | `__pondus__/w09-c5.md` (a); reproduced by `w09k_extract.py` |
| Same, `lab_status` masked | 21/27, 11/57, 6/35, 38/120 | MEASURED | same |
| Same, second coder R2 | 20/27, 11/58, 7/35 | CITED (verifier) and reproduced by my script | `data/r2.tsv`; `__pondus__/w09-c2.md` verdict |
| Agreement R2 against rule 1 (as coded / masked) | 105/120 kappa 0.70 / 108/120 kappa 0.77 | script output (first number equals the verifier's 106/121, kappa 0.70) | `figures/figure_numbers.txt` |
| Verifier's hand sample (n = 20, seed 9202) | hand vs rule 1 18/20 kappa 0.78; hand vs R2 19/20 kappa 0.89 | CITED | `__pondus__/w09-c5.md` (a) |
| Pooled by wave, as coded | 14/69, 2/24, 4/21, 5/35, 10/28, 14/36 | script output, in no claim | `figures/figure_numbers.txt` |
| Escalation wakes, reproducer, claim file read before or at the wake | 0 of 10 (decision stated in 10 of 10) | MEASURED | `__pondus__/w09-c5.md` (c) |
| 14 escalated claims: read in wake / not read / not checked | 1 / 12 / 1 | explorer's report (not verified) | `01-escalation_table.md` of explorer-w09-h |
| Fate of the 14 decisions | restated 9, superseded 5, reversed 0 | explorer's MEASURED, not a verified claim | explorer-w09-h; `python3 -I scripts/lab_status.py` |
| Would a read have changed the decision label | 0 of 13 | CONJECTURE (explorer-w09-h) | `01-escalation_table.md` |
| Banner against none, pooled | 9/35 vs 40/178 (p 0.66); masked 11/35 vs 44/178 (p 0.40) | MEASURED | `__pondus__/w09-c5.md` (e) |
| Banner against none, by role | explorer 7/7 vs 16/29; author 1/15 vs 17/93; verifier 1/12 vs 7/56 | CONJECTURE (script output, six uncorrected tests) | `figures/figure_numbers.txt` |
| Wave 8 timeline | 36 hand-backs; 34 raw opens; raw opens in wake turns 15/36 masked | script output, in no claim | `figures/figure_numbers.txt` |
| PI model | `claude-opus-5-5` in all six transcripts | MEASURED | `data/pi_models.txt` |

## Worst-fitting case

The story is: explorers' hand-backs get opened, authors' and verifiers' mostly do not. The case that fits worst is **verifier hand-backs in wave 8: 4 of 8 opened (50%)**, far above the verifier rate of every other wave (0 to 14 percent) and in the same wave as 7 of 13 for explorers; and, within explorers, **wave 8 (7 of 13, 54%) sits below waves 5 and 7 (4 of 5 and 5 of 6)**. Both are inside the overlap of the intervals, so I read them as noise, not as a change. The single case that fits the "banner does not matter" reading worst is the explorer row of Figure 4 (7 of 7 with the banner). The typical case is an author hand-back answered by a dispatch or a wave-note line without a file open (Figure 5's open squares). For escalations, the typical case is w02-c10 or w04-c10 (the hand-back already carries the verifier's content; explorer-w09-h) and the worst-fitting is w07-c7, where the hand-back said the result held only for the 6-tool headless author and the PI landed it by its registered rule anyway; the decision section written two to five days later narrowed it (explorer-w09-h's CONJECTURE).

## Not covered

- Which results hold at other PI models: there is one (`claude-opus-5-5`), so the metric is described for comparison, not compared.
- Waves 1-4 per-role comparisons beyond Figure 2 and the banner by role: unverified script output, no verifier has read them.
- Worker transcripts, the hand-back text beyond its first 260 characters (banner detection and lengths only), claim-file content.
- Reads that are not of the returning worker's artifacts: re-reads (item (b) of w09-c4 was dropped by the verifier) and orientation reads are not in this report.
- Plugin version effects: the plugin has one version string; I list dated text changes only.
- Wave 7 and wave 6 timelines: only wave 8 drawn.
- Cost and spend: none computed.
- The hand-back wakes with no assistant request (3 of 226 arrivals) and the peer messages are out of every rate.

## Steering questions

- [now] Should the five by-role cuts (by wave and role, banner by role, R2 against masked) go into a claim so a verifier reads them, given the figures lean on them?
- [now] The metric is defined for "same turn". Do you want "same or next turn" as a second headline rate (about 1.5 times higher in wave 8)?
- [later] For a cross-model comparison, should the lab fix a task set and run each candidate PI model for at least 80 wakes per role, or accept a pooled rate with the role mix reported?

## Pointers

Commit of scripts, tables and figures: `f906a1d`. All commands from the worktree root; `sessions.sh` sets `$PAIRS` (the six `label=path` pairs of `__pondus__/w09-c2.md`, "method").
- Tables: `sh -c '. __reports__/wave-09/explorer-w09-k/data/sessions.sh; python3 -I __instrumenta__/w09k_extract.py __reports__/wave-09/explorer-w09-k/data $PAIRS'` → `data/wakes.tsv`, `arrivals.tsv`, `turns.tsv`, `opens.tsv`, `r2.tsv` (about 4 s; read-only on the transcripts; deterministic, no seed). Script: `__instrumenta__/w09k_extract.py@f906a1d` (imports `w09d_turns.py@5bdeb78` and `w09c2v_extract.py`).
- Figures and every number behind them: `python3 -I __instrumenta__/w09k_figures.py __reports__/wave-09/explorer-w09-k/data __reports__/wave-09/explorer-w09-h/01-escalation_table.md __reports__/wave-09/explorer-w09-h/out/ranges.tsv __reports__/wave-09/explorer-w09-k/figures` → `figures/fig1..fig5` (PNG and PDF), `figures/figure_numbers.txt`. Script: `__instrumenta__/w09k_figures.py@f906a1d`. Quick check of the key numbers: `grep -E 'explorer, as coded|author, as coded|verifier, as coded' figures/figure_numbers.txt` (18/27, 10/57, 5/35).
- PI model: `sh -c '. .../sessions.sh; python3 -I __instrumenta__/w09k_models.py $PAIRS'` → `data/pi_models.txt`. Script: `__instrumenta__/w09k_models.py@f906a1d`.
- Inputs not mine: `__pondus__/w09-c5.md`, `w09-c2.md`, `w09-c4.md`; `__reports__/wave-09/explorer-w09-d/`, `explorer-w09-h/`, `author-w09-2/`.
- Puzzles: `__scrupuli__/wave-09-explorer-w09-k.md`.
