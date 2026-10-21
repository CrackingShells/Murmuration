"""Runs headless `claude -p` (haiku) on eight fixed Bash commands under several permission cells (mode, allow rules, hooks, shell, MCP), interleaved over reps, and writes per-Bash-call rows: permission decision time and tool run time from the --debug-file log, the command and first-call shell-snapshot time, plus run cost and token counts.

usage: auto_mode_probe.py WORKDIR(outside any lab) --reps 5 [--jobs 3] [--cells a,b,...] [--out rows.jsonl] [--keep-debug DIR]
Inputs: the claude CLI on PATH, the user's settings (read only; per-run --settings/env only). Cost about USD 0.01 per run. Output: one JSON line per Bash call {cell, rep, session, tool_id, cmd, n_in_run, perm_ms, run_ms, snapshot_s, cost, cache_read, cache_create, input, output} and one per run {cell, rep, run: true, ...}; then a median table (perm_ms of calls 2..n, i.e. first call excluded).
Source of the numbers: lines `[Stall] tool_dispatch_start ... permissionDecisionMs=N` and `tool_dispatch_end ... durationMs=N` of the debug log, `Creating shell snapshot` / `Shell snapshot created` timestamps. Never run from inside a lab folder (w01-c14); debug logs hold account identifiers, keep them out of git.
"""
import json, os, random, re, subprocess, sys, statistics as st, glob, datetime as dt
from concurrent.futures import ThreadPoolExecutor
A = sys.argv
wd = os.path.abspath(A[1]); arg = lambda k, d=None: A[A.index(k) + 1] if k in A else d
reps = int(arg("--reps", 5)); jobs = int(arg("--jobs", 3)); out = arg("--out"); keep = arg("--keep-debug", os.path.join(wd, "dbg"))
os.makedirs(keep, exist_ok=True)
SET = arg("--set", "basic")  # basic: eight trivial commands; lab: commands shaped like the lab's (needs hello.py in WORKDIR)
CMDS = {"basic": ["true", "pwd", "ls", "cat /etc/hosts", "echo hi", "git status", "python3 -c pass", "date"],
        "lab": ["python3 -I ./hello.py a", "python3 ./hello.py b", "git log --oneline -3", "ls -la", "wc -l hello.py", "sleep 1", "grep -c print hello.py", "command -v python3; echo $SHELL"]}[SET]
PROMPT = "Call the Bash tool once per command, one call per turn, in this order, each command exactly as written, then stop. Write no other text. Commands: " + "; ".join("`%s`" % c for c in CMDS)
EXACT = ["Bash(%s)" % c for c in CMDS]
LABR = ["Bash(python3 -I ./hello.py *)", "Bash(git log *)", "Bash(git status*)", "Bash(ls *)", "Bash(wc *)", "Bash(sleep *)", "Bash(grep *)", "Bash(command -v *)"]
GLOB = ["Bash(ls *)", "Bash(cat *)", "Bash(echo *)", "Bash(git status*)", "Bash(pwd)", "Bash(date)", "Bash(true)", "Bash(python3 -c *)"]
# cell: (permission mode, extra args, settings dict, env, use real MCP servers)
CELLS = {
 "auto": ("auto", [], {}, {}, False),
 "auto+blanketBash": ("auto", ["--allowedTools", "Bash"], {}, {}, False),
 "auto+exactallow": ("auto", [], {"permissions": {"allow": EXACT}}, {}, False),
 "auto+globallow": ("auto", [], {"permissions": {"allow": GLOB}}, {}, False),
 "auto+nohooks": ("auto", [], {"disableAllHooks": True}, {}, False),
 "bypass": ("bypassPermissions", [], {}, {}, False),
 "auto+bashshell": ("auto", [], {}, {"CLAUDE_CODE_SHELL": "/bin/bash"}, False),
 "auto+labrules": ("auto", [], {"permissions": {"allow": LABR}}, {}, False),
 "auto+pywild": ("auto", [], {"permissions": {"allow": ["Bash(python3 *)"]}}, {}, False),
 "auto+flagrules": ("auto", ["--allowedTools", "Bash(python3 -I ./hello.py *)", "Bash(ls *)", "Bash(wc *)", "Bash(grep *)", "Bash(sleep *)", "Bash(git log *)", "Bash(command -v *)"], {}, {}, False),
 "auto+mcp": ("auto", [], {}, {}, True),
}
only = arg("--cells").split(",") if arg("--cells") else list(CELLS)
plan = []
for r in range(reps):
    for c in random.sample(only, len(only)): plan.append((c, r))
ts = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def one(item):
    c, rep = item; mode, extra, settings, env, mcp = CELLS[c]
    dbg = os.path.join(keep, "%s_%d.log" % (c.replace("+", "_"), rep))
    cmd = ["claude", "-p", PROMPT, "--model", "haiku", "--permission-mode", mode, "--output-format", "json", "--max-budget-usd", "0.2", "--debug-file", dbg] + extra
    if not mcp: cmd += ["--strict-mcp-config"]
    if settings: cmd += ["--settings", json.dumps(settings)]
    e = dict(os.environ); e.update(env)
    try: r = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=240, env=e); j = json.loads(r.stdout)
    except Exception as ex: return [{"cell": c, "rep": rep, "run": True, "error": str(ex)[:200]}]
    sid = j.get("session_id"); u = j.get("usage", {})
    perm, dend, snap = {}, {}, None; order = []
    s0 = s1 = None; ok = None
    for line in open(dbg, errors="replace"):
        m = re.search(r"^(\S+) .*tool_dispatch_start tool=Bash toolUseId=(\S+) permissionDecisionMs=(\d+)", line)
        if m: perm[m.group(2)] = int(m.group(3)); order.append(m.group(2)); continue
        m = re.search(r"tool_dispatch_end tool=Bash toolUseId=(\S+) outcome=(\S+) durationMs=(\d+)", line)
        if m: dend[m.group(1)] = int(m.group(3)); continue
        if "Creating shell snapshot for" in line: s0 = ts(line.split()[0])
        elif "Shell snapshot created successfully" in line: s1 = ts(line.split()[0]); ok = True
        elif "Shell snapshot creation failed" in line: s1 = ts(line.split()[0]); ok = False
    if s0 and s1: snap = round(s1 - s0, 2)
    cmds = {}
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid)):
        for line in open(f):
            rec = json.loads(line); m = rec.get("message")
            if rec.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash": cmds[b["id"]] = b["input"].get("command", "")
    base = {"cell": c, "rep": rep, "session": sid}
    rows = [dict(base, run=True, cost=j.get("total_cost_usd"), cache_read=u.get("cache_read_input_tokens"), cache_create=u.get("cache_creation_input_tokens"), input=u.get("input_tokens"), output=u.get("output_tokens"), turns=j.get("num_turns"), duration_ms=j.get("duration_ms"), api_ms=j.get("duration_api_ms"), snapshot_s=snap, snapshot_ok=ok, n_bash=len(order), models=list(j.get("modelUsage", {})))]
    for i, t in enumerate(order): rows.append(dict(base, tool_id=t, n_in_run=i + 1, cmd=cmds.get(t), perm_ms=perm[t], run_ms=dend.get(t)))
    return rows

rows = []
with ThreadPoolExecutor(jobs) as ex:
    for rs in ex.map(one, plan):
        rows += rs; print(rs[0], flush=True)
if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
print("| cell | runs | calls 2..n | perm ms median | min | max | run ms median | snapshot s median | cost USD median |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
for c in CELLS:
    calls = [x for x in rows if x["cell"] == c and "perm_ms" in x and x["n_in_run"] > 1]; runs = [x for x in rows if x["cell"] == c and x.get("run") and "error" not in x]
    if calls: print("| %s | %d | %d | %d | %d | %d | %d | %s | %.4f |" % (c, len(runs), len(calls), st.median(x["perm_ms"] for x in calls), min(x["perm_ms"] for x in calls), max(x["perm_ms"] for x in calls), st.median(x["run_ms"] or 0 for x in calls), st.median([x["snapshot_s"] for x in runs if x["snapshot_s"]] or [0]), st.median(x["cost"] for x in runs)))
