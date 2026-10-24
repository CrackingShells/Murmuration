---
type: findings
wave: wave-09
author: explorer-w09-a
date: 2026-10-24
version: v0
decision-required: none
---

# Labelled set of auto-mode classifier decisions from the user's own sessions: markers, counts, sampling scheme, adversarial draft, sample sizes (findings v0)

I stayed on the brief. Two deviations of scope to know: (a) the allow side of the set exists only for versions 2.1.293 and later (2026-10-08 on), because older transcripts do not record the classifier's allow; (b) the extracted set is 276 MB of redacted JSONL under `/private/tmp/murmuration-w09/explorer-w09-a/`, never committed.

## Result

- MEASURED: auto mode's decisions are recorded on the tool-result record of each call, in three fields: `permissionDecision` (`{decision, source, reasonType: "classifier", reasonCode?, classifierCategory?}`), `toolDenialKind` (`automode-blocked`, `automode-unavailable`), and `serverClassifierContext`. Across 5,227 transcript files (1,386 project folders, subagents included) there are 116,590 unique tool calls (by tool_use id). 30,525 have a recorded classifier allow, 67 a classifier refusal, 39 a "no verdict / unavailable" error (not a decision), 1 a response-level "stopped by a safety classifier" interruption. [source: `tables_counts.md`, `collect_log.txt`]
- MEASURED: refusals are rare: in the recorded era (2026-10-08 to 10-24) 23 refusals against 30,525 allows, a refusal share of 0.075% (the sample-size script ran on the first extraction's 30,511, same figure to three digits). An "allow everything" model has 99.92% accuracy and sensitivity 0. [source: `sample_size_estimate.md` D]
- MEASURED: the allow label does not exist before version 2.1.293: `permissionDecision` is on 0 of 75,745 calls of older versions and on 40,594 of 40,845 calls of 2.1.293+ (first record 2026-10-08T01:14Z; what the other 251 are I did not check). The 44 refusals before that date are recognised by their text and `toolDenialKind` only, and have no recorded-allow counterpart. 26,305 older calls in auto mode with no error could be inferred allows (not recorded); I sampled 300 of them separately and marked them `allow_inferred`. [source: `strata.md`; version table in puzzle S-w09-explorer-w09-a-1]
- MEASURED: the refusals carry a category in square brackets in 30 of 67 cases (14 distinct categories, listed below), 32 say only "Blocked by classifier" (all dated 2026-09-13 or earlier), 3 say "judged this action dangerous (it gave no explanation)", 2 have no reason text. In 2 cases the stated reason has a sentence beyond the category. All 67 are in user work folders, none in the lab's automated "arena" probe runs. 47 of 67 have a preceding user prompt in the transcript; 28 have the recorded classifier context. [source: `tables_counts.md`; `refusals.jsonl`]
- MEASURED: the classifier context that the transcript records is only `git_state` (cwd, branch, clean flag, counts of staged/modified/untracked, origin visibility), `live_cwd` and `platform` (keys of `serverClassifierContext.context`). It holds no prompt and no command text. So what else the classifier read (the conversation, the task) is not recorded; I attach the preceding user prompt as a proxy. [source: `w09a_collect.py` `condense_ctx`; `refusals.jsonl` field `classifier_ctx_recorded`]
- CHECKED (65 cases, drafted by me, SYNTHETIC): an adversarial draft of 39 calls a classifier should refuse and 26 near-misses, in five families, with 9 intent pairs where the same command carries a different user task. Labels are the drafter's, not Anthropic's. [source: `synthetic_adversarial_v0.json`]
- ESTIMATE: 67 refusals, from 41 sessions, give an exact 95% upper bound of 4.4% on the miss rate of a local model that misses none, and a half-width of about 0.09 at 10 to 30% miss rate. To bring the half-width down to 0.05 at a 20% miss rate takes 246 independent refusals, which is about 4 times the set. [source: `sample_size_estimate.md` A, B]

## Table

How the decisions appear (the markers, MEASURED unless noted):

| Class | Marker in the tool-result record | n (unique calls) | Label | Source |
|:--|:--|--:|:--|:--|
| classifier allow | `permissionDecision.reasonType == "classifier"`, `decision == "accept"` | 30,525 (all 2026-10) | MEASURED | `tables_counts.md` |
| classifier refusal | `toolDenialKind == "automode-blocked"`; text "Permission for this action was denied by the Claude Code auto mode classifier. Reason: <reason>. If you have other tasks..."; newer: `permissionDecision.reasonType == "classifier"`, `decision == "reject"`, `reasonCode "classifier:auto-mode"`, sometimes `classifierCategory` | 67 (23 in era, 44 before) | MEASURED | `refusals.jsonl` |
| classifier no verdict | `toolDenialKind == "automode-unavailable"`; text "gave no verdict" or "<model> is temporarily unavailable"; `reasonCode "classifier:auto-mode:unavailable"` | 39 | MEASURED; meaning (transient, retry) CITED to the tool-result text itself | `tables_counts.md` |
| response-level stop | `toolDenialKind == "interrupted"`, text "the response that made this tool call was stopped by a safety classifier" | 1 | MEASURED | `tables_counts.md` |
| lab guard or other hook | `permissionDecision.source == "hook"` or text starting "PreToolUse:<Tool> hook error" | 1,159 rejects, 9 accepts | MEASURED | `tables_counts.md` |
| permission rule | `reasonType == "rule"` (accept 2,701; reject 152) | 2,853 | MEASURED | `tables_counts.md` |
| user's prompt answer | `toolDenialKind == "user-rejected"` or `source user_reject/user_abort` (135); `source user_temporary/user_permanent` accept (47) | 182 | MEASURED | `tables_counts.md` |
| built-in safety check (rm of an unresolvable target) | `reasonType == "safetyCheck"`, text "denied by a built-in Claude Code safety check" | 25 | MEASURED | `tables_counts.md` |
| mode (bypass, acceptEdits, plan) | `reasonType == "mode"` | 4,808 accept, 2 reject (dontAsk) | MEASURED | `tables_counts.md` |
| no decision field | nothing | 75,197 (older versions, read-only tools, Reads) | MEASURED | `tables_counts.md` |

How to tell auto mode (CONJECTURE for the fields' meaning, MEASURED for the counts): the best marker is the decision itself, `reasonType "classifier"`. The `permissionMode` field on user records and the `auto_mode` attachment are weaker: of the 30,525 recorded classifier allows, 9,898 (and 4 of the 67 refusals) have neither a `permissionMode` nor an `auto_mode` attachment before them (headless and subagent sessions do not carry the field), 12,868 have only the attachment, 13 sit under `default` and 287 under `plan` (plan mode with the classifier on, or a mode switched after the last prompt record; not resolved). [source: `w09a_classify.py` run, mode cross-table in `tables_counts.md`]

Recorded classifier decisions by tool (MEASURED, `tables_counts.md`):

| decider | Bash | Agent | MCP | WebFetch | WebSearch | Write | Edit | other (Skill, SendMessage, ToolSearch...) |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| allow | 26,248 | 1,129 | 1,077 | 137 | 131 | 100 | 33 | 1,670 |
| refusal | 57 | 2 | 4 | 0 | 0 | 2 | 0 | 2 |
| no verdict | 33 | 2 | 2 | 0 | 0 | 0 | 2 | 0 |

By month (MEASURED): refusals 2026-07 8, 08 4, 09 28, 10 27; unavailable 1, 5, 3, 30; recorded allows 10 only (30,525). By project group, refusals: colgrep-mcp worktrees 16, the lab 9, explore-augmented-light 5, usd-bio 4, ai-agent worktrees 4, the rest 1 to 3 each (23 groups); allows by group: the lab's automated arena 11,420, the lab's own sessions 8,292, 20 other groups 1 to 1,517 each. Full table in `tables_counts.md`.

Refusal categories seen (MEASURED, `refusals.jsonl`): Auto-Mode Bypass 6, PII Data Handling 4, Safety Bypass Flag 3 plus 2 with a sentence, Self-Modification 3, Merge Without Review 2, Security Test Removal 2, and one each of Security Weaken, External System Writes, Irreversible Local Destruction, Git Destructive, Remote Shell Writes, Create Unsafe Agents, Interfere With Workloads, Modify Shared Resources. 32 "Blocked by classifier", 3 "(it gave no explanation)", 2 none.

Sampling scheme (the allowed sample, `w09a_build_set.py`, seed 20261024):

| Item | Value |
|:--|:--|
| Population | the 30,525 recorded classifier allows of the second extraction (the first had 30,511; sessions of this lab were still running) |
| Strata | tool family x source (arena = the lab's automated probe folders; natural = everything else) x Bash command family (git, gh, python/uv, build, remote, network, fs-mutate, process, search, read-shell, agent-cli, heredoc, other) x risk-word flag (a regex of ssh, scp, curl, rm -rf, git push/reset/checkout --, gh pr merge, kill, settings.json, .claude/, BYPASS, --force, chmod...) |
| Allocation | n_h = min(N_h, max(floor, round(1500 sqrt(N_h) / sum sqrt(N_k)))), floor 8, floor 25 for risk strata; selection by simple random sampling without replacement inside a stratum |
| Sample | 1,608 calls in 53 strata; marginals natural 19,105 / 1,120, arena 11,420 / 488, plain 25,776 / 1,131, risky 4,749 / 477 |
| Weights | w_h = N_h / n_h stored on every row (`weight`); the population mean of any per-call score is sum(w_i s_i) / sum(w_i) |
| Cluster handling | rows carry `session` and `norm_text_hash`; intervals should be cluster-bootstrapped by session. Arena strata are templated: 8,017 arena read-shell allows have 628 unique texts, 830 arena process allows have 30 |
| Refusals | all 67 taken (census, weight 1), plus the 39 no-verdict calls marked NOT_A_DECISION |

Adversarial draft (SYNTHETIC, `synthetic_adversarial_v0.json`): refuse / allow by family: destructive 7/5, exfiltrating 8/5, permission-loosening 11/6, out-of-scope 8/8, security-weakening 5/2. Origins by my reading of the `origin` field: 12 payloads or probes of the lab guard and w08j (`guard_selftest_payloads.json`, `w08j_probe_cases.json`), 20 derived from the shape or category of a real refusal, 22 invented, 11 near-misses written against those. 9 intent pairs share a `pair_id` (rm, reset, push, scp, merge, curl, kill, ssh, agent), the sharpest being S029/S030: the same `scp` command, allowed when the task asks for the copy and to be refused when it does not.

Retry behaviour after a refusal (MEASURED, `w09a_retry_pairs.py`): of 67 refusals, 59 are followed within 5 calls by a call of the same tool in the same session; the next such call was a recorded classifier allow in 15, had no decision record in 34 (older versions), was refused again in 5. The 15 allowed retries are natural near-misses (a refusal and the rewrite that passed) in `retry_pairs.jsonl`.

Sizes needed (ESTIMATE; formulas in `sample_size_estimate.md`):

| Question | Formula | Input | Result |
|:--|:--|:--|:--|
| Bound on the local model's misses of Anthropic refusals (false allows against the reference) if it misses none | exact: 1 - 0.05^(1/n) | n = 67 (41 sessions) | 4.4% one-sided 95% |
| Same, misses 6 of 67 | Clopper-Pearson two-sided | n = 67 | 9.0% (3.4 to 18.5%) |
| Refusals for half-width h on a miss rate p | n = z^2 p(1-p)/h^2 | p 0.2, h 0.05 | 246 |
| Same, h 0.10 | | p 0.2 | 62 (we have 67, but in 41 sessions, so deff > 1 applies) |
| Allowed calls for the local model's refusal rate among allows | n = deff z^2 q(1-q)/h^2 | q 0.02, h 0.01, deff 2 | 1,506 (the sample holds 1,608 but unevenly weighted, so the effective n is lower) |
| Allowed calls for q 0.05, h 0.02, deff 2 | | | 913 |
| New refusals per day at the observed rate | refusals / days | 23 in 11 days (10-13 to 10-23, this account) | about 2 per day |
| Days to 246 independent refusals at that rate | 246 / 2.1 | | about 117 days (the refusals cluster in a few projects, so more) |

## Worst-fitting case

The story: "a refusal is recognisable by its text, an allow by its decision record, and auto mode by `permissionMode`". The worst fits:

- 9,898 classifier allows, and 4 refusals, sit in sessions where no `permissionMode` was ever recorded, and 13 allows sit under `permissionMode "default"` (counts above). A set that selected "auto sessions" by `permissionMode "auto"` alone would keep 7,459 of 30,525 recorded allows (lose 76%); adding the `auto_mode` attachment still loses 9,898 (32%). The decision field itself is the only complete marker, and it exists only from 2.1.293. [source: `tables_counts.md` mode table]
- Refusal text does not say what was refused for 32 of 67 refusals ("Blocked by classifier"), and the three reasons with a sentence name only the trigger ("an env var whose name signals it is designed to disarm colgrep's guard") with no judgement of the user's intent. The classifier's stated reason cannot be used as a label for why.
- Some refusals look like ordinary read-only work, so they will be the hard cases for any local model and may be classifier errors, not dangers: one `ps ... | grep` of a named process refused as "Interfere With Workloads" (2026-10-23, the lab's own session), a `sed -E 's/=.*/=<redacted>/'` of a shell env file refused with no reason (2026-09-27, a dai-mas worktree), and four read-only greps with `COLGREP_BYPASS=1` refused as "Safety Bypass Flag". I put drafted allow versions of three of them in the synthetic set (S032, S066, S071) with `origin` saying the real label was a refusal, so that they test disagreement on purpose. [source: `refusals.jsonl`; `synthetic_adversarial_v0.json`]
- Counter to "refusals are the dangerous ones": 20 of 67 refusals mention colgrep, and 16 of 67 are in the colgrep-mcp worktrees (13 of them on 2026-09-12 alone), so the refusal set is dominated by one project's habits and its `COLGREP_BYPASS` convention, not by a spread of attack types. [source: `tables_counts.md` project table]

Prior work: no source fetched or cited in this report; the meaning of the 14 category names is CONJECTURE from their strings (UNVERIFIED against any Anthropic documentation).

## Not covered

- The user's yes/no on each refusal (was it right?). The set holds Anthropic's decision as the reference label, as asked; a refusal the user then overrode is visible only as a later user prompt, which I did not mine.
- The classifier's own latency and its full input (the conversation, system prompt, rules). Not in any record; `serverClassifierContext` is a git summary. The preceding user prompt is a proxy only.
- Allowed calls of older versions as labels: inferred only (300 sampled), weight stored, never to be mixed with the recorded tier without saying so.
- Non-auto sessions: calls decided by rules, hooks, modes and prompt answers are counted and kept apart but not exported as a labelled set (no classifier decision exists on them; a local model could score them, but there is no reference).
- No local model was run; no agreement was computed. LM Studio was not touched.
- The prompt context (up to 2,000 characters) was cut and redacted by regexes for keys, tokens, emails and long hex or base64 strings (counts in `collect_log.txt`: 12 `sk-` keys, 5,028 emails, 5,385 assignments of password-like names, 2 bearer headers). Names, paths and free-text personal data are not redacted, so the set stays outside git and should not leave the machine as is.
- Clusters: I did not compute the actual design effect (needs a model's scores); the table assumes deff 1, 2 and 4.
- Subagent transcripts are in; their classifier decisions are not separated from the main thread's (field `sub` is on every row).

## Steering questions

- [now] Which tier is the reference: only the 23 recorded-era refusals and 30,511 recorded allows (clean, small on the refusal side), or also the 44 older refusals (text-recognised, no matching recorded allows)? Default I would use: refusals of both eras with a flag, allows recorded only.
- [now] May the dev hook (PreToolUse, recording only) store the full prompt context beside each local decision from now on? That is the only way to get the classifier's decisions with their context for the next weeks, since the transcripts hold none.
- [later] Does the user want the 67 refusals reviewed by hand for "was this right"? It would give a second label (user intent) and tell false refusals from real ones, at about one hour of the user's reading.

## Pointers

All under the lab root; the redacted extracted set is outside git.

| Artifact | Command |
|:--|:--|
| `__instrumenta__/w09a_collect.py@12eb74b` | `python3 -I __instrumenta__/w09a_collect.py /private/tmp/murmuration-w09/explorer-w09-a` (56 s) |
| `__instrumenta__/w09a_classify.py@12eb74b` | `python3 -I __instrumenta__/w09a_classify.py /private/tmp/murmuration-w09/explorer-w09-a __reports__/wave-09/explorer-w09-a/tables_counts.md` |
| `__instrumenta__/w09a_build_set.py@12eb74b` | `python3 -I __instrumenta__/w09a_build_set.py /private/tmp/murmuration-w09/explorer-w09-a __reports__/wave-09/explorer-w09-a/strata.md` (seed 20261024, total 1500) |
| `__instrumenta__/w09a_retry_pairs.py@12eb74b` | `python3 -I __instrumenta__/w09a_retry_pairs.py /private/tmp/murmuration-w09/explorer-w09-a` |
| `__instrumenta__/w09a_sample_size.py@12eb74b` | `python3 -I __instrumenta__/w09a_sample_size.py /private/tmp/murmuration-w09/explorer-w09-a` |
| `__reports__/wave-09/explorer-w09-a/tables_counts.md`, `strata.md`, `sample_size_estimate.md`, `synthetic_adversarial_v0.json`, `collect_log.txt` | committed aggregates and the synthetic set |
| `/private/tmp/murmuration-w09/explorer-w09-a/refusals.jsonl` (106 rows), `allowed_sample.jsonl` (1,608), `allowed_inferred_sample.jsonl` (300), `retry_pairs.jsonl` (67), `classified.jsonl` and `calls.jsonl` (116,590 each) | redacted, not in git; the transcripts are only read |
