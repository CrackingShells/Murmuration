## S-w05-reproducer-w05-6-1
The head says D is "byte-identical to the file at b554266", and `git archive b554266 agents skills scripts hooks .claude-plugin` is not A plus the line: hooks.json (python3 -S, a hook removed) and scripts differ from e0fc3ab. So the exports the runs use (e0fc3ab plus the line) are not any commit of the branch. The m1 delta is unaffected only because hooks and scripts do not enter request 0, which nobody checked. Would a run of the branch tip itself give 15.7k too?
refs: /private/tmp/murmuration-w05/reproducer-w05-6/plugin_A, plugin_E (diff -r against a b554266 archive)

## S-w05-reproducer-w05-6-2
The headless gain comes from six tools (Artifact, ArtifactComments, ArtifactData, Workflow, ReportFindings, ShareOnboardingGuide); six of the twelve entries are never exercised by any run (SuggestSkills, SearchPlugins, SuggestPluginInstall, Claude_Browser wildcard; the Simulator and visualize wildcards only by my dummy-server probe). The Desktop number (25.9k to 42.0k tokens) is almost entirely those unexercised entries, 55k of 123k characters being Artifact, which headless does remove.
refs: /private/tmp/murmuration-w05/reproducer-w05-6/probe/out_A.jsonl, out_E.jsonl; /private/tmp/murmuration-w05/reproducer-w05-6/runs/r6A1/stdout.jsonl

## S-w05-reproducer-w05-6-3
A server named `Claude_Browser` never connected in my probe in either arm (init mcp_servers lists four of five), though the Desktop has a server of that name. Is the name reserved in the CLI, so a `mcp__Claude_Browser__*` wildcard might never be exercised in the CLI, or did my dummy fail on it?
refs: /private/tmp/murmuration-w05/reproducer-w05-6/probe/out_A.jsonl (system init, mcp_servers), err_A.txt

## S-w05-reproducer-w05-6-4
The explorer is asked to "Write no file" and the SubagentHandback hook blocks once demanding a report; explorers answered both ways (declined in r6A1, r6D1, a6A1, a6D1; wrote the file in a6D3). Smoke-task cost and wall time therefore carry an arm-independent explorer-side noise of 0.01 to 0.03 USD and up to 90 s, larger than the 0.0077 USD gain in pair 3. m4 cannot carry weight at n = 3.
refs: /private/tmp/murmuration-w05/author-w05-2/runs/a6D3/stdout.jsonl (73.5 s gap before SubagentHandback), /private/tmp/murmuration-w05/author-w05-2/runs/a6D3/lab/__reports__/explorer-smoke

## S-w05-reproducer-w05-6-5
Request-0 composition: cache_read is 24,463 in A and 8,671 in D in every run, to the token, while cache_write moves by single digits. That reads as a fixed shared prefix cache across runs, not a measurement of the PI's own context. m1 (input + write + read) is still the context size, but "cold" and "warm" cost statements depend on it.
refs: /private/tmp/murmuration-w05/author-w05-2/e6b_table_A_D.tsv columns cache_write, cache_read
