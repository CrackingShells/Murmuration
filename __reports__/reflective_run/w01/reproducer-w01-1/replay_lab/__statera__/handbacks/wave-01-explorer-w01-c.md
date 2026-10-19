# Hand-backs of wave-01-explorer-w01-c

Final messages, verbatim, appended by the lab's hook. Read it; never edit it.

## hand-back 1 | 2026-10-19T11:48:51+09:00 | agent_id=a1f4458ce75dacdec type=murmuration:explorer event=PostToolUse bytes=16166 sha256=dcc9c3a0f022

# explorer-w01-c hand-back

The Write tool refused `__reports__/reflective_run/w01/explorer-w01-c/report.md` twice with "Subagents should return findings as text, not write report files". I did not work around it through Bash, so the report is below and not on disk. Please write it to that path yourself if you want it there.

Everything else is on disk:
- Scripts, CSVs and `run_all.sh` are in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/explorer-w01-c/`. `run_all.sh` rebuilds all tables in about 20 s.
- Puzzles (5, including your request about what used my turns) are in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-explorer-w01-c.md`.

I stayed inside the brief. I also read two of the user's own answers in session 2947f9dc and the README "Tools by role" table, because they are the only first-hand statements about MCP servers.

Snapshot: 2026-10-19, repository HEAD 9368eb2. This run's six explorers were still running when I took it (299 calls so far).
Labels: MEASURED (script in `run_all.sh`), CONJECTURE, CITED. Unfinished items are in section 8.

## 0. Data, and a trap in it

| Item | Value | Source |
|:--|:--|:--|
| Transcripts parsed | 55 files (5 main sessions, 50 subagent files) | `agents.csv` |
| Tool calls, raw | 3,468 | `tool_calls.csv` |
| Tool calls, unique by `tool_use_id` | 2,361 | `calls_dedup_classified.csv` |

**Trap (MEASURED).** Forked sessions copy their parent's history. 722 raw `tool_use_id`s occur in 2 or 3 files. The design session and 3ccc590f replay genesis calls, and ten genesis subagents reappear. Counting files inflates every number by about 47 percent. All tables deduplicate by id and credit a call to the first session in the order genesis, design, 3ccc590f, 2947f9dc, this run.

| Agent kind | n | Tools announced | Source |
|:--|--:|:--|:--|
| genesis and design subagents (`general-purpose`) | 28 | about 375 deferred names, 36 MCP servers | `agent_context.csv` |
| shipped `murmuration:explorer` (this run) | 6 | 32 deferred names, 4 servers (Wolfram 15, colgrep 9, arxiv 4, context7 2) plus WebSearch, WebFetch | `agent_context.csv` |

The wildcard `tools:` lines work as filters on the deferred list (MEASURED, n=6).

## 1. What each kind of agent called (MEASURED; `t1_*`, `t10_*`)

| Group | Calls | builtin | Wolfram | arxiv | ddg | colgrep | context7 | other MCP |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| genesis PI (Opus) | 280 | 201 | 4 | 3 | 3 | 2 | 0 | 67 |
| genesis workers (10) | 688 | 466 | 89 | 60 | 62 | 11 | 0 | 0 |
| design PI | 192 | 160 | 0 | 0 | 0 | 1 | 0 | 31 |
| design workers (18) | 596 | 493 | 0 | 43 | 46 | 4 | 8 | 2 |
| 2947f9dc PI (banyan work) | 272 | 237 | 0 | 2 | 0 | 0 | 0 | 33 |
| this run, PI | 34 | 31 | 0 | 0 | 0 | 0 | 0 | 3 |
| this run, 6 shipped explorers | 299 | 299 | 0 | 0 | 0 | 0 | 0 | 0 |

1. Worker MCP use is three families: Wolfram (89), literature search (arxiv 103, ddg 108) and colgrep (15).
   - Wolfram is concentrated in two workers whose brief names it. "Build final Wolfram notebook" made 67 of its 107 calls on Wolfram, and "Foundations ... with Wolfram" made 16 of 51.
   - The other eight genesis workers made 6 Wolfram calls together. Use follows the brief, not the allowlist.
2. The six shipped explorers made 299 calls and none were MCP.
   - Bash 252 (168 invoking python), WebFetch 21, Read 14, Write 5, Edit 2, ToolSearch 2, WebSearch 2.
   - The work was transcript parsing, and no allowlisted server fits it.
3. Python over Wolfram (the user's question of 10-18 06:20): genesis workers ran python in Bash 181 times against 85 `WolframLanguageEvaluator` calls. The per-worker table shows the split follows the brief. The Bash kind classifier is first-match, so 181 is a lower bound.
4. Glob and Grep were called 0 times in 2,361 calls, and they are in none of the 29 surviving subagent `prefix.json` tool lists (`t8_prefix_toolnames.csv`).
   - My own tool list is Read, Bash, Write, Edit, Skill, ToolSearch, SubagentHandback, and the session records `auto_mode.bashFirst: true`.
   - So `Glob, Grep` in `agents/*.md` are inert here. The absence is MEASURED; the cause is CONJECTURE.

## 2. Failures and causes (MEASURED; `t2_*`; rules in `analyze.py:outcome`)

| Server or tool | n | ok | Failure classes |
|:--|--:|--:|:--|
| arxiv `read_paper` | 10 | 2 | result over the size cap, saved to file: 6; read before download: 2 |
| arxiv `search_papers` | 84 | 71 | HTTP 429: 10 (one worker, one burst); oversize: 3 |
| ddg `search` | 91 | 68 | "No results were found": 23 (25 percent) |
| ddg `fetch_content` | 20 | 18 | HTTP 403: 2 |
| Wolfram evaluator | 88 | 87 | timeout: 1 |
| colgrep | 16 | 16 | none |
| context7 | 8 | 8 | none |
| banyan-hpc | 4 | 1 | host dependency "rsync version (2.6.9) is less than the required 3.0.0": 3 |
| WebFetch (this run's explorers) | 21 | 17 | oversize "Output too large": 3; invalid URL (no scheme): 1 |

Not seen in 2,361 calls (pattern scan of the first 400 characters of every result):
- "No such tool".
- A deferred tool called before ToolSearch.
- A refusal of an allowlisted tool.
- "not connected" at call time.

Causes by class:

| Class | Count |
|:--|--:|
| result over the size cap | 21 |
| empty result | 23 |
| upstream limit or block | 12 |
| host or PATH dependency | 3 |
| `sleep` blocked by the platform | 5 |
| PreToolUse hook block (colgrep corpus-search, worktree guard) | 3 |
| auto-mode classifier denial | 2 |

Bash non-zero exits (56) are not counted as tool failures.

**Consequence for SA8.** Of 59 MCP and web failures outside Bash, 52 arrive with `is_error: false` and 7 with `true`. If `PostToolUseFailure` fires only on errored results (not tested on 2.1.302; CONJECTURE), a friction hook on it sees 12 percent of this friction. A `PostToolUse` result-text classifier would be needed for the rest.

## 3. Discovery overhead (MEASURED; `t3_*`, `t7_*`, `agent_context.csv`)

| Item | Value |
|:--|:--|
| ToolSearch calls | 44 of 2,361 (1.9 percent) |
| `select:` form / keyword form | 38 / 6 |
| ToolSearch that returned nothing | 0 of 44 |
| Calls to a nonexistent tool name | 0 |
| Context growth to next assistant turn per ToolSearch | median about 3,100 tokens, range 0 to 58,000 (n=43; an upper bound, confounded by same-turn results) |

The "wrong prefix" cost that the machine CLAUDE.md warns about is absent from these transcripts. Every `select:` used a full name from the injected deferred list, and the keyword queries (+arxiv, +ddg, +banyan) all matched. Its price may have been paid in sessions I was not given (CONJECTURE).

The visible cost is the size of the initial listing:

| Agent | Deferred names | First-turn input tokens (median) |
|:--|--:|--:|
| genesis `general-purpose` (n=10) | 375 | 58,280 |
| shipped explorer (n=6) | 32 | 23,531 |

- The 35 k-token difference per spawn is the clearest measured gain of the explicit `tools:` lines.
- The name list alone is 31.5 k against 2.6 k characters, about 7 k tokens at 4 characters per token (an assumption).
- The rest I cannot attribute. CONJECTURE: eager schemas of non-deferred servers that the general-purpose agent carried; `t8` shows 42 loaded names.

## 4. Against the shipped allowlists (counts MEASURED; the role mapping is my assumption; `t4_*`)

| Not in the role's allowlist | Calls | By | Shipped replacement |
|:--|--:|:--|:--|
| ddg search and fetch | 88 + 20 | explorer-like workers | WebSearch (10 calls in history, all returned results), WebFetch |
| Monitor | 14 + 3 | explorer-like and reproducer-like | none; `run_in_background` on Bash |
| SendMessage | 3 | explorer-like probes | none, by design |
| Agent | 5 | review workers | none, by design |
| context7 for an author | 3 | one counsel worker | explorer has it, author does not |

- The platform blocked five `sleep N; ...` commands (agents a33a82, a3f3fa, a4ad7c, a807fe, 10-18 04:05 to 04:51) and told them to use Monitor or `run_in_background`. Whether `run_in_background` suffices for a shipped reproducer is untested (CONJECTURE).
- README says servers "are used when present and skipped when absent". Neither `scripts/lab_init.py` nor the agent files check for a server, so the claim is untested, not false.
- The design documents already say ddg was "flaky here" (`__reports__/genesis/03-architecture_v0.md` l.181), and the data agrees (25 percent empty searches).

## 5. The user's environment (MEASURED; `t11_server_inventory.csv`)

| Session | Connected servers | Failed to connect |
|:--|--:|:--|
| genesis, design, 3ccc590f, 2947f9dc | 36 | arangodb (ENOENT `mamba`), mcp-python-ingestion (ENOENT `mamba`), scientific-skills (CONNECTION_CLOSED) |
| this run | 35 | mcp-python-ingestion, scientific-skills (CONNECTION_CLOSED); arangodb now connected (46 tools) |

Three of about 40 user servers failed at every start, and one changed state overnight. None was allowlisted. Wolfram, arxiv, context7 and colgrep connected 5 of 5.

CITED to `~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl`, AskUserQuestion answers 2026-10-18 13:31:07 and 13:42:52:

> "check_out the /banyan skills. We have an MCP server to standardize how we intereact with it (and if possible don't only use the `run_command` escape hatch) ..."

> "This rsync stuff is a nightmare. There is in fact an initialization race when spawning new sessions in Claude Code. it doesn't always fail and it's terrible to find a systemic fix for it that works across all OS and installs without locally altering the plugin's auto install config"

Sequence in that session:
- `get_resources` fails at 13:29:56. `fs_ls` fails at 13:40:58 and again at 14:53:49.
- The PI reads the plugin's `.mcp.json` (cache `lbc-llm-agents/banyan/0.4.1`, launched via `uv tool run`) and asks to edit the cache. The user declines.
- The work then ran as 23 `ssh/scp/rsync` Bash commands. The server was called 4 times and 3 failed.

CITED to `__reports__/platform_probes/01-findings_v1.md` row 25 (not re-run): `mcpServers` frontmatter is ignored for plugin agents. A plugin can therefore ship servers only through a plugin-level `.mcp.json`.

Tool names follow `mcp__plugin_<plugin>_<server>__<tool>`. I saw this for colgrep, banyan and the probe stub `mcp__plugin_probe_stub__record`. A Murmuration-bundled colgrep would therefore be `mcp__plugin_murmuration_colgrep__*`. The four agent files' `mcp__plugin_colgrep-mcp_colgrep__*` wildcards would then match nothing. CHECKED by the naming rule on three servers; the match behaviour itself was not run.

## 6. SA15: for, against, other shapes (a reading of the tables, not a verdict)

| Position | For | Against |
|:--|:--|:--|
| Bundle servers (SA15) | The user wants typed servers over the escape hatch. The explicit allowlist saves about 35 k first-turn tokens per spawn. | Shipped explorers made 0 MCP calls out of 299. The only plugin-bundled server in a real session failed 3 of 4 calls on a host dependency and lost to `ssh`. Wolfram needs a local licence, colgrep and arxiv are already installed, and bundling renames them. Existing servers failed for environment reasons (mamba PATH, init race) at 5 of 5 starts. |
| Allowlist by server | Already by server (`mcp__X__*`); the weak point is the prefix, not the granularity. | Untested whether `mcp__plugin_*_colgrep__*` matches. |
| Capability check at `/lab` time | README promises present-or-skipped and nothing checks. Servers change state between days. The harness already prints a "failed to connect" block. | The costliest failures (oversize, 429, empty search, rsync PATH) are not connection failures. banyan `get_facility` passed and `get_resources` failed 2 s later. |
| Server contracts as instructions | `read_paper` returned inline for 2 of 10 calls. A brief line (download first, results arrive as a file) addresses 8 of 10. | Costs words only; not tested (CONJECTURE). |

The shape I would look at first (CONJECTURE, none run):
- an allowlist by server with the plugin-qualified prefix;
- a short per-server contract line in the research-loop skill;
- a `/lab` check that reads the "failed to connect" block rather than probing.

## 7. Best-fit and worst-fit cases

| | Case | Why |
|:--|:--|:--|
| Best fit | genesis worker `a2f3c738`, "Build final Wolfram notebook": 107 calls, 67 Wolfram, 0 failures | A named, local server whose output (the notebook) Bash could not produce. |
| Worst fit, for "the allowlist is enough" | session 2947f9dc, banyan | A user-requested, typed MCP server was unusable for a reason outside any allowlist. The PI fell back to Bash `ssh`, the escape hatch the user said not to rely on. |
| Worst fit, for "MCP matters to the shipped team" | this run's six explorers | 299 of 299 calls built-in; the question had no MCP-shaped part. |

## 8. Unfinished and limits

Unfinished:
- No probe of whether a wildcard like `mcp__plugin_*_colgrep__*` matches.
- No test of `PostToolUseFailure` on `is_error:false` results.
- No test of `run_in_background` as a Monitor substitute.
- `claude mcp list` was not run (I wanted no side effects).

Limits:
- This run's explorer rows are a snapshot. The PI row is Opus with all tools.
- Genesis workers were `general-purpose`, so "would have been blocked" is a counterfactual that uses my role mapping.
- `res_head` keeps 400 characters. Wolfram language-level errors inside a successful result count as ok.
- The user-level TOOL ROUTING POLICY hook tells agents to ToolSearch per domain before the first Bash call. Five of six explorers never did (puzzle 3).

## 9. Puzzles (full text in `__scrupuli__/wave-01-explorer-w01-c.md`)

1. The user blames an "initialization race", but banyan failed deterministically on all three calls over 85 minutes with the same rsync/PATH message. If one fault shows two ways, a bundled `.mcp.json` inherits the nondeterminism and a `/lab` capability check would pass or fail at random.
2. 52 of 59 MCP and web failures are `is_error:false`. A friction hook on `PostToolUseFailure` would miss 88 percent of the friction that is about server interfaces.
3. The user-level routing hook and the plugin's `tools:` lines both govern the same choice. In this run neither moved behaviour (196+ Bash calls, 0 MCP), and I cannot tell which was in force. `Glob` and `Grep` are listed in the agent files but are never offered.
4. The Write tool refused `report.md` (twice). The report is in this message only.
5. What used my 60 turns:
   - about 6 turns on learning the JSONL format;
   - about 10 on the extractor and on repairing the outcome classifier;
   - about 8 on user-word and banyan-episode reading;
   - about 6 on my own tool errors (BSD `sed -i`, a missing CSV column, a `grep -r` blocked by the colgrep hook, a regex that kept a stray `n`);
   - the rest on tables.
   The probe was turn-hungry because the data has no "tool failure" field, so every class needed a pattern and a check. Outputs also had to stay short, so one question took two or three calls. A per-call outcome table would have saved about half the turns.

## Files

All in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/explorer-w01-c/`:
- `run_all.sh`.
- Scripts: `extract_calls.py`, `analyze.py`, `extra.py`, `per_agent_mcp.py`, `agent_context.py`, `inventory.py`.
- Raw tables: `tool_calls.csv`, `calls_dedup_classified.csv`, `agents.csv`, `agent_context.csv`.
- Derived tables: `t1_calls_by_group_server.csv`, `t1b_calls_by_group_tool.csv`, `t2_outcomes_by_server.csv`, `t2b_outcomes_by_mcp_tool.csv`, `t3_toolsearch_per_agent.csv`, `t3b_toolsearch_queries.csv`, `t4_allowlist_gap_workers.csv`, `t4b_pi_mcp_use.csv`, `t5_allowlisted_server_use.csv`, `t6_bash_commands.csv`, `t7_toolsearch_context_delta.csv`, `t8_prefix_toolnames.csv`, `t9_bash_shell_search.csv`, `t10_per_agent_tool_families.csv`, `t11_server_inventory.csv`.
- Puzzles: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-explorer-w01-c.md`.

