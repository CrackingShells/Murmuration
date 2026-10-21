"""Sums a wave's hook starts under five builds (current, sh gate on the main thread, merged hand-back starts, compiled binary, resident mcp_tool) from the starts-per-registration JSON of wave 4 (explorer-w05-d) and per-start medians measured in wave 6 (bare_n60.jsonl-style table, ms wall / ms CPU); output: a markdown table on stdout.

usage: w06b_hook_option_sums.py STARTS.json   (the file `starts_wave4_pi_session.json`; main-thread starts are PostToolUse 104 and PostToolBatch 89 of that file's totals, read from `totals`)
Per-start figures are constants below, with their source; change them to re-price.
"""
import json, sys
d = json.load(open(sys.argv[1])); r = d["starts_by_registration"]; t = d["totals"]
main_calls, batches_main = 104, 89   # counts_wave4_pi_session.json: main thread tool calls and batches
main = main_calls + batches_main     # main-thread PostToolUse + PostToolBatch starts
allst = d["all_starts"]
# per-start (wall ms, cpu ms), explorer-w06-b `bare_n60.jsonl`, n = 60 per cell, load average 4.6 to 5.7
PY = (90, 42)       # budget.py, the shipped Python, main thread / short worker
SHG = (33.7, 3.5)   # sh gate (byte loop) on a main-thread payload
RS = (51, 6)        # compiled Rust binary that reads stdin (std only); hot path of a worker would add the transcript offset read
MCP = (2, 0)        # platform-recorded cost of an mcp_tool hook; the resident server's CPU is not counted here (about 1 ms in-process, ESTIMATE)
merge = r["SubagentStop||handback.py"] + r["PostToolUse|SubagentHandback|handback.py"]   # starts that a single dispatcher would fold into the budget start of the same event
rows = []
def row(name, wall_ms, cpu_ms): rows.append((name, wall_ms / 1000, cpu_ms / 1000))
row("current (every registration starts budget.py / handback.py / ...)", allst * PY[0], allst * PY[1])
row("sh gate on the main thread's PostToolUse and PostToolBatch (193 starts)", (allst - main) * PY[0] + main * SHG[0], (allst - main) * PY[1] + main * SHG[1])
row("... plus one dispatcher for SubagentStop and the hand-back PostToolUse (%d starts folded)" % merge, (allst - main - merge) * PY[0] + main * SHG[0], (allst - main - merge) * PY[1] + main * SHG[1])
row("every start a compiled binary (std only), no gate", allst * RS[0], allst * RS[1])
row("compiled binary, sh gate on the main thread", (allst - main) * RS[0] + main * SHG[0], (allst - main) * RS[1] + main * SHG[1])
row("resident server, every per-call and lifecycle hook an mcp_tool (SessionStart/End stay commands)", allst * MCP[0], allst * MCP[1])
print("| build (wave 4: %d starts, main %d) | serial wall s | CPU s | wall vs current |\n|:--|--:|--:|--:|" % (allst, main))
for n, w, c in rows: print("| %s | %.1f | %.1f | %.2f |" % (n, w, c, w / rows[0][1]))
