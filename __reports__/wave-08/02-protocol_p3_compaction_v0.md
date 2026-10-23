# P3 v0: compact the PI near a registered threshold, with a PreCompact hook that carries the lab's state (registered before any run of this protocol)

registered: 2026-10-24, by author-w08-3, before the first headless run of the PI-like scenario.
Claim: w08-c3. Branch `w08-c3-compaction` (worktree `/private/tmp/murmuration-w08/author-w08-3/wt`). Prior: explorer-w08-e (`__reports__/wave-08/explorer-w08-e/00-findings_v0.md`), explorer-w08-d.

## The change

1. A lab setting `autoCompactWindow: 283000` (compaction fires at window minus 33,000, so near 250,000 tokens) for the PI. Whether the lab writes it (`scripts/lab_init.py`) or the user's project settings carry it is the landing step's; this protocol only measures where it must live and that it works (m6). `scripts/lab_init.py` is not edited here.
2. A new `PreCompact` hook, `scripts/precompact_state.py` with its own row in `hooks/hooks.json` (commit d1af3a4): in an initialized lab it prints the current wave note's path, the user's latest words from `__statera__/user_words.md` verbatim, the workers in flight (a `start` in `__statera__/harness.jsonl` with no later `end` for its agent_id, named by the latest event of that agent_id, with the claim id found in the wave note or the claim files) and the claims of the current wave with their current label. Its stdout is appended to the summarizer's instructions (explorer-w08-e, MEASURED). It never blocks.
3. The existing `resume_brief.py` row (SessionStart `compact`) stays as it is.

## Scale of the PI-like runs (stated before, not fitted after)

Opus runs cost USD 2-4 each when driven to 250k, so the PI-like scenario runs at window 150,000 (compaction near 117,000 tokens), on every arm and model. This tests the mechanism (what the summary and the brief carry, what the PI re-reads) at a smaller size; the cost at 250k is an ESTIMATE from measured parts, never a measurement. A summarizer reading 250k may keep less than one reading 117k; that is not tested.

## Scenario

A scratch lab built by `__instrumenta__/w08_c3_make_lab.py` (seed 11): a wave note of wave 03 (the question, a plan, a table of who is working on which claim, a line `NEXT:`), `user_words.md` with four dated entries (the last one planted), four claim files in different states (`MEASURED` with an OVERSTATED verdict, `THEOREM` with SOUND WITH GAP, an unverified `CHECKED`, a supported `MEASURED`), `harness.jsonl` with six workers of which two are in flight, and 12 reports of about 30,000 characters each. The session is the research-pi agent of the exported branch (`--agent murmuration:research-pi`, the plugin's own `hooks.json` with the Rust-guard rows left in), default permission mode, one process driven turn by turn through `--input-format stream-json`:

- turn 1: orient (read the wave note, user_words, harness log, claims) and say what you will do;
- turns 2-n: "read report k and tell me in one sentence what it adds", k = 1..12, as many turns as the arm needs to pass the threshold and then two more (identical across arms);
- final turn, asked only after the compaction event is in the transcript (compacted arms) or after the same number of turns (control): five questions a PI needs to continue (Q1 the workers in flight, by name and claim id; Q2 the user's latest words, verbatim; Q3 the next step the wave note gives; Q4 the current label of two named claims; Q5 one number from the first report read, prose detail).

Arms: C, no compaction (default window); B0, compaction with neither the new hook nor the brief; B1, compaction with the brief only (the lab as it is); H, compaction with the brief and the new hook (the claim). Opus: H twice, C once, B1 once if the budget allows (stated as extra, not gating). Haiku (same plugin export, `--model haiku`): C, B0, B1, H, three seeds (three lab variants: names, numbers and sentences re-drawn), 12 runs. No `--max-budget-usd`, default permission mode.

## Metrics (all computed by script from the transcript and the debug log; nothing read by hand)

- **m1 outcome:** for each run, items correct out of Q1..Q4 (Q1 counts as correct only if both workers are named with their claim ids and no ended worker is named; Q2 only if the sentence is present verbatim after whitespace normalisation; Q3 only if it names the next action and the claim; Q4 only if both labels are as `lab_status` gives), and Q5 reported apart. Gate and pairing: below.
- **m2 re-reads:** tool calls and tool-result tokens (characters / 2.4) after the compaction boundary and before the final answer (Read, Bash, Glob, Grep), per run, and which files.
- **m3 the compaction request:** uncached input, cache read, cache write, output tokens and seconds of the compaction's forked request (debug log), its USD at the lab's Opus 5.5 list price, the context before and after (`compact_boundary`), the summary's length, the next request's cache write.
- **m4 hook time:** wall time of `precompact_state.py` per compaction (from the debug log) and 10 cold runs on the real lab, median; exit status.
- **m5 spend:** the run's total USD at list price, per arm (MEASURED, a short session); and the net ESTIMATE for the PI's six sessions with `__instrumenta__/w08e_compaction_net.py` at threshold 250k with R set to the measured m2 token count (and to 3x it).
- **m6 where the setting lives:** (a) `autoCompactWindow` in a project `.claude/settings.local.json` of a scratch lab: does a compaction fire at window minus 33,000 (`thresholdSource` in the debug log)? (b) with `--project-config-root <other folder>` and a cwd elsewhere (the Desktop's way, framing and synthesis row 1(d)), is the setting of that folder read? (c) does a session that is running pick up a change of the file between two turns of one process? If (b) or (c) cannot be tested headless, say so.
- **m7 workers:** from the lab's own subagent transcripts, the share of worker sessions and of worker requests whose context passes 150k, 250k, 400k tokens, and the USD that a compaction at that threshold would save or cost them (the same model as m5); plus one haiku subagent cell with the hook logging its payload: does the PreCompact payload identify the subagent, does the hook's stdout reach a subagent summary, does a block skip a proactive compaction there.

## Rules (landing)

Pairing: each arm of a haiku seed shares its lab variant; the sign of H minus B1 and of H minus C is taken per seed. With n = 3 per arm a sign is a sign, not a test; no p-value is reported.

Land the setting and the hook together when all of the following hold (otherwise land the part that passes, and say which):

1. **State survives (m1):** both Opus H runs get Q1..Q4 all correct, and so does the Opus control; on haiku, H gets Q1..Q4 all correct in at least 2 of 3 seeds, and in every seed H's items correct are not below C's minus one.
2. **The hook adds something (m1, m2):** H's items correct are above B1's in at least one seed and below it in none, or equal with strictly fewer post-compaction tool-result tokens in at least 2 of 3 seeds. If not, the brief alone is enough, the hook is not landed, and the setting alone is judged on rule 1 with B1.
3. **Re-reads bounded (m2):** the Opus H runs re-read at most 30,000 tokens after the boundary (the break-even R of a 250k threshold is 103k and the 'workable' limit 22k at 150k; explorer-w08-e).
4. **Cheap (m4):** the hook's median wall time is under 500 ms and its exit status is 0 in every compaction.
5. **Net (m5):** the ESTIMATE at the measured R is at least USD 25 over the six PI sessions (at least 17% of USD 144.47).
6. **Setting (m6):** the file route works in (a); (b) and (c) are reported whatever they give, and a failed (b) means the setting must live in the folder the Desktop treats as the root (the main checkout) and nowhere else.

Workers (decided from m7, stated now): if fewer than 10% of worker requests have a context above the threshold, workers keep the platform's default (no setting for them), because there is nothing to gain, and the hook ends without output when it can tell it runs for a subagent; if more, the threshold of the PI applies to them as well. Blocking a subagent's compaction is chosen only if the subagent cell shows a compacted subagent losing its task state (items correct under C higher than under the compacted cell).

## What each result closes

H passes: the lab may set the threshold for the PI at 250k and print the state at every compaction; scope: synthetic lab, one question family, Opus n = 2, window 150k. Outside it: a real PI session at 250k, the Desktop route if (b) is not shown. H fails rule 1 or 3: the PI keeps the default threshold, and the cause (summary, brief or re-reads) is named from m1 and m2.
