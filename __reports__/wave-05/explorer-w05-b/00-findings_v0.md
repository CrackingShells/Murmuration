---
type: findings
wave: wave-05
author: explorer-w05-b
date: 2026-10-21
version: v0
decision-required: confirm
---

# Where the PI main thread spends its tokens: findings (v0)

Stayed inside the brief. Spend figures (USD) are not quoted; shares are of the PI main thread's list-price total, with the formula stated. Scripts are at the working-tree state of c928bd1 plus uncommitted additions, to be committed together with this report (cite them as `__instrumenta__/<file>@dbff7c7`).

## Result

For the wave-length PI session (wave 4: 114 requests, one Opus model, context 75k to 362k tokens), the cost is structural: cache reads of an ever-present context are 51.9% of list price, cache writes 27.6%, output 20.5% (35% of the output tokens are thinking), uncached input 0.01% [source: `__reports__/wave-05/explorer-w05-b/wave4_summary.txt`] (MEASURED). The three things that stand out are (1) a 74.6k-token base context that the plugin does not control today but could shrink (the PI has no `tools:` allowlist, its workers do) = 21.7% of the PI total, (2) the PI's own output (text, tool calls, briefs) = 35.3% counting generation plus re-reading, and (3) in the long waves 1-3 session two avoidable events that wave 4 mostly escaped: re-injected skill listings (about 16% of that session) and cache expiry over human-idle gaps (about 10%). Tool results the PI reads are not the problem: all 107 tool results of wave 4 together are 219k characters, about the size of the base context.

## Table

All shares are of the session's own list-price total (input, output, cache read, cache write at the rates in `scripts/lab_status.py` PRICES). Context-carry attribution: an item entering the context at request n costs its tokens times (cache-write price at n + cache-read price at every later request until the context shrinks); tokens per item come from the growth of the context between requests, split over the records between them with a non-negative least-squares fit of tokens per character per category (wave 4: R2 = 0.95, 113 requests). For waves 1-3 the same fit has R2 = 0.33, so there the split is by characters only and only the direct measures below are trustworthy.

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Wave 4 PI, per-request token totals | 114 requests; uncached input 274, cache read 27,273,105, cache write 361,773 (all 1-hour), output 107,752 of which thinking 37,457 | MEASURED | `wave4_summary.txt`, `wave4_requests.tsv` |
| Wave 4 PI, list-price shares | cache read 0.519, cache write 0.276, output 0.205, input 0.0001 | MEASURED | `wave4_summary.txt` |
| Wave 4: base context at request 0 | 74,632 tokens = 21.7% of PI total (27.4% of the context-carry part). It is carried by all 113 later requests. Of its characters (218k), tool schemas are 186.6k (85%), system prompt 24.5k, memory/hook/prompt 9k | ESTIMATE: share = base tokens x (write price + 113 x read price) / total; composition from the `prompt_snapshot` record, 0.342 tokens per character | `wave4_categories.tsv`; `prompt_snapshot` attachment at records 25 and 42 of the wave-4 transcript |
| Tool allowlist for research-pi | The five agents in `agents/` all have `tools:` except research-pi. The nine tools the wave-4 PI called have 32.4k characters of schema; the other 154k characters = 52.7k tokens per request. Saving = 52.7k x (113 x read + write) / total = 15% of the wave-4 PI total (half of that if the app injects some tools regardless) | ESTIMATE (the saving); CONJECTURE (that the Desktop app honours `tools:` for a main-thread agent and keeps the lab working: not run) | `agents/*.md` line 5; CITED: https://code.claude.com/docs/en/sub-agents via context7 `/websites/code_claude`: "the main thread itself takes on that subagent's tool restrictions and model" |
| PI own output, wave 4 | text + tool-call arguments: 82.5k tokens entering the context; generation 20.5% + re-reading 14.8% = 35.3% of PI total. By characters of own writing: Bash commands 50.6k (33%), Agent briefs 37.1k (24%, 16 calls, mean 2.3k), assistant text 19.5k, SendMessage 12.6k, heredoc writes 11.3k, Write/Edit of files 12.5k | MEASURED (characters), ESTIMATE (shares) | `wave4_own_writing.tsv`, `wave4_categories.tsv` |
| Thinking | 37,457 of 107,752 output tokens = 7.2% of PI total (0.205 x 0.348) | ESTIMATE | `wave4_summary.txt` |
| Tool results by kind, wave 4 | lab scripts 7.3%, other Bash 6.5%, cat/sed/head/tail 3.7%, heredoc commands that also print 3.1%, ls/find/ps 1.1%, Agent (sync) 0.5%. Sum of all 107 results: 219k characters | ESTIMATE | `per_category_table.tsv`, `wave4_items_top.tsv` |
| Worker traffic into the PI, wave 4 | peer messages 7.0%, task notifications 2.6%, queued hand-backs 1.1%. 24 of 114 requests were woken by a peer message (16.5% of total on those requests that call tools, 3.1% for 5 that only acknowledge) | MEASURED (counts), ESTIMATE (shares) | `wave4_by_trigger.tsv` |
| Re-reads of files | wave 4: 210 characters in total; waves 1-3: 44.7k characters repeated (user_words.md 5 times = 16.7k, reflective_run.md 3 times, wave.md template 2 times, settings.local.json 3 times) = about 15k tokens, below 1% of cache-write tokens | MEASURED | `wave4_rereads.tsv`, `waves123_rereads.tsv` (paths seen through Read and through cat/sed/head/tail/jq in Bash) |
| Skill listing re-entering the context (waves 1-3) | 19 re-entries of the 90-skill listing (29,940 characters) between 02:04 and 02:55 UTC on 2026-10-19, each adding about 10.8k tokens (peer turns with a listing: median growth 13,242 tokens; without: 2,416; n = 16 and 58). Carried to the compaction at request 276: 212k extra tokens = 16.3% of that session's list price. Wave 4: 1 re-entry (request 35, 10,997 tokens) = 2.5% | MEASURED (growth), ESTIMATE (share = extra tokens x (write + carried requests x read) / total) | `waves123_listing_reinjection.tsv`, `wave4_listing_reinjection.tsv` |
| Cache misses over idle gaps (waves 1-3) | 4 gaps of 4163 to 5429 s (over the 1-hour cache life) each rewrote the whole context: 128.6k, 167k, 246k, 266k tokens = 808k tokens = 38% of all cache-write tokens of the session; extra cost over a cache read = 10% of the session's list price. Three of the four follow a `wrap_up` call (the app's "next step" box) with the human away. Wave 4: no gap over 1 hour | MEASURED (gaps, tokens), ESTIMATE (share = sum of rewritten tokens x (1-hour write price - read price) / total) | `waves123_cache_misses.tsv` (rows 305, 355, 364; row 290 is the rewrite after request 289, a `<synthetic>` record with zero usage), `waves123_cw_spikes.tsv` |
| Cache life choice | 5-minute cache write price would save 10% on writes but 20 gaps of 300 to 3600 s would each rewrite the context: net worse (+0.31 of total in wave 4, +0.81 in waves 1-3) | ESTIMATE | computed inline from `*_requests.tsv` (one-line python in the session; not saved as a script) |
| Context growth to 966k tokens (waves 1-3), compaction at request 276 | mean context 496k tokens over 394 requests. Compacting whenever context exceeds 300k tokens (modelled: one read of the context, 15k tokens of summary, rewrite of 91.5k) = net saving 28% of that session; for wave 4 (max 362k) at most 3% | ESTIMATE (assumptions: after-size 91.5k from the one real compaction, summary 15k tokens; quality loss not modelled) | `waves123_compaction_counterfactual.txt`, `wave4_compaction_counterfactual.txt` |
| Time, wave 4 (5300 s between first and last request, two idle gaps included) | waiting for worker messages 47.7%; two idle gaps over 600 s 29.4% (one is a worker wait of 937 s); gap before a request that follows tool calls (tool run plus model start-up) 14%; model time inside requests 8.8% (a lower bound) | MEASURED (timestamps), the model/tool split is approximate | `wave4_time_split.tsv` |
| Time, waves 1-3 | idle over 600 s 65% (13 gaps, human away); worker waits 16%; model time 3.5% | MEASURED | `waves123_time_split.tsv` |

Per-category table as a raw artifact: `__reports__/wave-05/explorer-w05-b/per_category_table.tsv` (wave 4 with the fitted split; waves 1-3 by characters; the "listing/deltas" row of waves 1-3 (24%) is inflated by request 290, where a whole-context rewrite was booked as growth; use the direct 16.3% above).

## Worst-fitting case

1. The story "a few avoidable patterns dominate" fits wave 4 worst. Wave 4's PI session has no cache misses, no compaction, 210 characters of repeated reads, and one skill-listing re-entry. Its biggest tool result (27k characters, a listing of all puzzle files) is the PI reading its colleagues' raw puzzles, which is its job [source: `wave4_items_top.tsv`, transcript record 685]. What is left is structure: each of 114 requests reads about 242k cached tokens (mean context) [source: `wave4_summary.txt`], so each request costs about 0.9% of the PI total whatever it does. The measured avoidable part of wave 4 is small (listing re-entry 2.5%); the larger lever (15%) is an untested ESTIMATE.
2. The long session (waves 1-3) shows the expensive patterns (listing re-entries 16%, idle expiry 10%, 966k-token context) but it ran before the shipped plugin and in a different manner (design plus run in one session); those numbers describe it, not wave-length sessions.
3. CITED: the only outside statement used is the Claude Code documentation on running a main thread as an agent, https://code.claude.com/docs/en/sub-agents, as returned by context7 (`/websites/code_claude`); I did not fetch the page itself.

## Not covered

- Workers' own cost (subagents' base context of platform tools, since their `tools:` lists still leave WebFetch, WebSearch, MCP globs) and waits between author, verifier and exchange: only the PI main thread was asked for. The PI waits for worker messages 48% of wave-4 wall time, which says the critical path is the workers, not the PI.
- No probe was run: whether `tools:` shrinks the base context in the Desktop app, whether the skill-listing re-entry can be avoided, and what causes it (see puzzles). A probe needs one headless run of the PI with and without the allowlist (about 75k tokens of cache write each) and reading `prompt_snapshot`.
- Model-time versus tool-time split is a lower bound (the first assistant record of a request is written when its first block is done).
- The 89 `total_tokens_reminder` items get an implausible fitted 1.97 tokens per character (a 94-character string): their 3.1% share in wave 4 is a fitting artifact; their true carry is well under 1%.

## Steering questions

- [now] Shall a claim be filed to give `agents/research-pi.md` a `tools:` allowlist (Agent, SendMessage, Bash, Read, Write, Edit, Skill, ToolSearch, the two app tools it uses), tested by one headless A/B run reading `prompt_snapshot` and request-0 context size?
- [now] Is a keep-alive worth proposing for the "human away after `wrap_up`" gap (four 70 to 90 minute gaps rewrote 808k tokens; `ScheduleWakeup` is in the tool list but untried), or is the better rule "end the session, resume with the brief"?
- [later] Should the PI session per wave stay one session (wave 4: context never above 362k, compaction not worth it) with a rule to open a new session before 300k?

## Pointers

All in `__reports__/wave-05/explorer-w05-b/`; transcripts read only. Full command per transcript (`T4` = `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4.jsonl`, `T123` = `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl`; quick command = same, about 5 s; no seeds):

- `python3 -I __instrumenta__/w05b_pi_context_cost.py $T4 wave4 <dir>` and `... $T123 waves123 <dir>`: `*_requests.tsv`, `*_categories.tsv`, `*_items_top.tsv`, `*_nnls_tokens_per_char.tsv`, `*_rereads.tsv`, `*_own_writing.tsv`, `*_cw_spikes.tsv`, `*_cache_misses.tsv`, `*_by_trigger.tsv`, `*_summary.txt`.
- `python3 -I __instrumenta__/w05b_listing_reinjection.py $T <label> <dir>`: `*_listing_reinjection.tsv`, `*_listing_summary.txt`.
- `python3 -I __instrumenta__/w05b_pi_time_split.py $T <label> <dir>`: `*_time_split.tsv`.
- `python3 -I __instrumenta__/w05b_compaction_counterfactual.py <dir>/<label>_requests.tsv`: `*_compaction_counterfactual.txt`.
- `per_category_table.tsv`: merge of the two `*_categories.tsv` (inline python, columns as in its header).
- Price table: `scripts/lab_status.py` PRICES (list prices of 2026-10-19, Opus 5.5: 4 / 20 / 0.20 / 5 / 8 USD per Mtok for input / output / cache read / 5-minute write / 1-hour write). The wave-4 total from my table (not quoted here) matches the session's `cost-state` Opus line to the cent.
