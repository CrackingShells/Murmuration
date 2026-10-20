## S-w04-author-w04-3-1
The rule says "search that folder once with colgrep `search`"; the start note of arm S says it again with the exact tool names. In 15 runs (6 of them with the note) no worker called `search`, and one (st2r3) loaded `find_files` by ToolSearch and then listed with `ls`. Workers did the search the rule wants, with a tool the rule names only as a fallback ("without colgrep, Glob"). I do not know whether `ls` is chosen because 46 descriptive names fit one screen (1,240 characters) or because it is the habit of the first call (it sits beside `ls` of `__design__`, `__pondus__`, `__scrupuli__`). Arm X (opaque names) used colgrep in 1 of 6; a lab of 300 scripts would tell.
refs: __reports__/reflective_run/w04/author-w04-3/runs_table.tsv (colgrep_calls), s_measure.json (st2r3 sequence), x_measure.json (xt2r1)

## S-w04-author-w04-3-2
Glob is absent in every headless session of these runs (st2r1: "No such tool available: Glob"; the init record's tool list has no Glob and no Grep). The agent files' fallback ("without colgrep, Glob the folder and read the first lines") cannot be followed there, and st2r1 did not try another tool after the failed call and wrote a new script without seeing the folder. Same observation as S-w03-author-w03-2-10. The plugin's `scripts/lab_init.py` message for a missing colgrep also says "Glob".
refs: __reports__/reflective_run/w04/author-w04-3/s_measure.json (st2r1, tool_errors), /private/tmp/murmuration-w04/author-w04-3/runs/st2r1/run.jsonl (raw)

## S-w04-author-w04-3-3
xt2r1 printed its result record after 190 s, but its `claude -p` process stayed alive for 10 minutes with the whole MCP process tree, with `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` set. The worker had started a Python job in the background and polled it with `sleep 60; cat <task output>`. I stopped it by its PID (a handle of my own Popen, checked with `lsof` on its cwd) and changed the runner to do that 30 s after the result record. I do not know whether the ceiling variable covers a background Bash job of a main-agent worker.
refs: /private/tmp/murmuration-w04/author-w04-3/runs/xt2r1/run.jsonl (raw); __instrumenta__/e3_run_workers.py

## S-w04-author-w04-3-4
xt2r2 (opaque names) ran `ls __instrumenta__ ... | head -30`, saw u01..u26 only, took u27 for the next free name and overwrote `jsonl_field_counter.py` with its new script, then committed. Nothing in the agent file says to pick a name that is not in the listing; with descriptive names a collision is unlikely, with numbered names it is the natural guess. The same truncation (`head -30`, `head -40`, `head -50`) appears in the first call of 18 of 21 runs.
refs: __reports__/reflective_run/w04/author-w04-3/runs_table.tsv (xt2r2 note), x_measure.json

## S-w04-author-w04-3-5
st2r2 handed back with the message "placeholder" (its claim file and puzzle file were written before). The hand-back copy in `__statera__/handbacks/` therefore holds one word. I do not know why the model sent it; the hook did not deny it (harness.jsonl has only `start` and `end`). A real PI would get a hand-back with nothing in it.
refs: /private/tmp/murmuration-w04/author-w04-3/runs/st2r2/lab/__statera__/ (raw), s_measure.json (st2r2 sequence, last call)

## S-w04-author-w04-3-6
Without the paragraph, workers put their scripts outside `__instrumenta__/` in 3 of 6 runs (`exp/`, `w04-c9/` twice, ct1r2's cross-check in the claim folder), and one (ct1r1) read the plugin export's `skills/research-loop/SKILL.md` by its absolute path, which no brief gave. Where it learned the path I did not trace. This agrees with w03-c2's "where scripts go" figure, now at n = 6, but it is not part of E3's metrics.
refs: __reports__/reflective_run/w04/author-w04-3/c_measure.json (ct1r1, ct1r2, ct2r2, ct2r3 sequences)

## S-w04-author-w04-3-7
A first launch of 9 parallel runs had one (t3r3) return "Not logged in · Please run /login" after 1.7 s, zero tool calls, while the other 8 ran. The same launch succeeded on a rerun. Transient, but at a PI's parallel dispatch it would look like a worker that did nothing. I did not look for the cause.
refs: /private/tmp/murmuration-w04/author-w04-3/runs/ (the failed run was overwritten by the rerun; the pilot and the first-batch record are in the table of costs: USD 0)

## S-w04-author-w04-3-8
What the near-fit tasks showed: not one of 9 near-fit runs in arms M and S edited the near-fit script in place except t3r3; 7 copied it into a new file and changed it, leaving the original to answer its old question. If the PI's wish is "extend the one that almost does", the sentence leaves open whether that means in place or by copy; the protocol's "extended" does the same. The strict and the loose reading give 7 of 15 and 14 of 15 on rule E3, so the verdict of the rule depends on it. The PI should choose before the verifier does.
refs: __pondus__/w04-c4.md (scope item 2), __reports__/reflective_run/w04/author-w04-3/runs_table.tsv (s2_reuse)

## symbols
none new.
