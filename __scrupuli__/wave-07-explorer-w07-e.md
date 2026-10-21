## S-w07-explorer-w07-e-1
`${CLAUDE_PLUGIN_ROOT}` is substituted when the Skill tool delivers SKILL.md and in an agent body, but not when the agent Reads SKILL.md: lines 99 and 176-179 stay literal. The PI without the Skill tool therefore holds a text whose reference table it cannot follow unless it resolves the variable itself. v6 never followed a reference, so nobody has seen it resolve (or fail). Until it is tested, "the PI still gets research-loop" is true of the file's text, not of its references.
refs: `__reports__/wave-07/explorer-w07-e/cells/v6_pluginroot_path/summary.json`; transcripts of base and v6 (search `references/working_defaults.md`); `skills/research-loop/SKILL.md` lines 99, 176-179

## S-w07-explorer-w07-e-2
The tokens removed by denying `Skill` (about 11.8k) are 0.37 tokens per character of the 31,834 characters (listing 29,957 plus Skill schema 1,877), above the 0.21-0.34 band of w05-c3. Either the haiku tokeniser or this kind of text (names, short descriptions, many paths) is denser than the earlier fits, or the removed block is larger than the listing text I counted (a wrapper, or a changed deferred-name list between cells). The deferred-name delta counts differ between replicates (209, 265, 262) while request 0 differs by under 330 tokens, so the delta is not simply part of request 0. I did not resolve which block carries the missing tokens.
refs: `__reports__/wave-07/explorer-w07-e/pi_table.md` (deferred names column); `cells/base*/summary.json`, `cells/v1_deny_skill/summary.json`

## S-w07-explorer-w07-e-3
`skills: [research-loop]` in the frontmatter of `research-pi` does nothing for the PI (v1 vs v2, and the SKILL.md text appears only after the first assistant record) but injects 9,974 characters into every worker before its first request, and the docs page is silent on the `--agent` case. Which of the two does the Desktop session (the real PI) do? If Desktop preloads, the PI pays for the skill twice (injection and a Skill call), and `Skill` denied would be a double saving; I could not tell because I ran headless only.
refs: `__reports__/wave-07/explorer-w07-e/cells/v1_deny_skill/`, `cells/v2_deny_skill_nofm/`; `agents/research-pi.md` lines 7-8; `worker_req0.tsv`; `__reports__/wave-06/research-pi/request0_breakdown.md`

## S-w07-explorer-w07-e-4
Four things in the lab behave as if the allowlist were not closed: `Monitor` was called by 9 wave workers and `Skill` by one author, none listed in a `tools:` line; and 61 of 72 reproducer/author subagents spend an early request on `ToolSearch select:SendMessage` because SendMessage is deferred. The second is a recurring, countable cost (a request over a cache of 14k tokens per worker) that no one has priced; the first says an allowlist may not be what bounds a worker.
refs: `__reports__/wave-07/explorer-w07-e/worker_subagents.tsv`, `worker_tool_calls.tsv`, `toolsearch_results.tsv`

## S-w07-explorer-w07-e-5
Plugin disabling is the only lever that shrank the listing (86 -> 41 skills, -2.3k tokens), `skillOverrides` reached only 32 non-plugin skills (-1.9k), and `Skill(name)` deny rules reached none. Yet 41 skills remain after disabling 19 plugins: bundled and synced ones (`anthropic-skills:*`, `batch`, `loop`, `verify`, ...). Nothing in the docs I read removes those other than denying the Skill tool whole. Is the 41 floor a platform constant for a user with claude.ai skills synced (`syncClaudeAiSkills: false` untested)?
refs: `__reports__/wave-07/explorer-w07-e/cells/v5_plugins_off/init_lists.json`, `cells/v3_overrides_off/init_lists.json`, `cfg_plugins_off_keep_colgrep.json`
