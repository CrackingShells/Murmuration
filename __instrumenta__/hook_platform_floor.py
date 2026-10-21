"""Measures what the PLATFORM records for one do-nothing PostToolUse hook per run variant (sh `:`, python3, python3 -S -I, Rust binaries, budget.py, an mcp_tool call), from headless `claude -p` haiku runs of N Bash `true` calls with `--debug-file`; inputs: a work dir outside any lab, the bin dir with noop/drain/gate (rustc -O) and noop_mcp.py; output: JSONL of every `Hooks: PostToolUse:Bash [..] finished with status S (N ms)` line and a median table on stdout (kind=hook: the platform's own `finished (Nms)` line of our hook, absent for mcp_tool; kind=event: `classic.PostToolUse settled in`, the whole PostToolUse event of a call, the only figure an mcp_tool hook has).

usage: hook_platform_floor.py WORKDIR BINDIR PLUGDIR --reps 3 --calls 12 [--variants a,b] [--out rows.jsonl] [--interleaved]  (with --interleaved: reps = sessions, calls = calls per variant per session, all variants in one session)
Run with CLAUDE_CODE_SHELL=/bin/bash. Never run from inside a lab or plugin folder (runs below one register it in installed_plugins.json). One variant per run, so hooks of different variants never compete for the CPU; variants are shuffled within each rep.
"""
import json, os, random, re, subprocess, sys, statistics as st
wd, bd, pd = (os.path.abspath(a) for a in sys.argv[1:4])
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
reps, calls = int(arg("--reps", 3)), int(arg("--calls", 12))
bi = "%s/noop_mcp.py" % bd
V = {
 "sh-colon": {"type": "command", "command": ":"},
 "python3-pass": {"type": "command", "command": "python3 -c pass"},
 "python3-SI-pass": {"type": "command", "command": "python3 -S -I -c pass"},
 "rust-noop": {"type": "command", "command": "%s/noop" % bd},
 "rust-drain": {"type": "command", "command": "%s/drain" % bd},
 "rust-gate": {"type": "command", "command": "%s/gate" % bd},
 "budget.py": {"type": "command", "command": 'CLAUDE_PLUGIN_ROOT="%s" python3 "%s/scripts/budget.py"' % (pd, pd)},
 "sh-gate-lean": {"type": "command", "command": """p=; while IFS= read -r l || [ -n "$l" ]; do p=$p$l; done; case $p in *'"agent_id"'*) echo x;; esac"""},
 "mcp_tool": {"type": "mcp_tool", "server": "noop", "tool": "nop", "input": {"text": "${tool_name}"}},
}
only = arg("--variants", ",".join(V)).split(",")
LINE = re.compile(r"Hooks: PostToolUse:Bash \[(.*?)\] finished with status (\d+) \((\d+)ms\)")
SETTLED = re.compile(r"classic\.PostToolUse settled in ([\d.]+)ms")
rows = []
if "--interleaved" in sys.argv:
    # one session, every variant registered with `if: Bash(echo <variant>)`; the model runs `echo <variant>` in a shuffled order, so a variant's hook fires only on its own calls and all variants share the session's load
    per = int(arg("--calls", 8)); order = [v for v in only for _ in range(per)]; random.shuffle(order)
    hooks = []
    for v in only:
        h = dict(V[v]); h["if"] = "Bash(echo %s)" % v.replace(".", "-"); hooks.append(h)
    names = {v: v.replace(".", "-") for v in only}
    for k in range(reps):
        d = "%s/inter%02d" % (wd, k); os.makedirs(d, exist_ok=True)
        random.shuffle(order)
        s = {"hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": hooks}]}}
        prompt = "Call the Bash tool once per turn, one call per turn, with exactly these commands in this order, no other text:\n" + "\n".join("echo " + names[v] for v in order)
        cmd = ["claude", "-p", prompt, "--model", "haiku", "--permission-mode", "bypassPermissions", "--settings", json.dumps(s), "--debug-file", d + "/dbg.log", "--output-format", "json", "--max-budget-usd", "0.6"]
        if "mcp_tool" in only: cmd += ["--mcp-config", json.dumps({"mcpServers": {"noop": {"command": "python3", "args": [bi]}}})]
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=280, env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
        lines = open(d + "/dbg.log", errors="replace").read().split("\n")
        # attribute each `finished` line to its variant by the hook command text; mcp_tool by the order of `mcp_tool calling` lines vs the settled lines that follow
        nxt = None
        for i, line in enumerate(lines):
            m = LINE.search(line)
            if m:
                cmdtxt = m.group(1)
                for v in only:
                    if v != "mcp_tool" and V[v]["command"][:60] == cmdtxt[:60]:
                        rows.append({"variant": v, "run": k, "kind": "hook", "ms": int(m.group(3))}); break
            if "Hooks: mcp_tool calling noop/nop" in line:
                for l2 in lines[i + 1:i + 12]:
                    mm = SETTLED.search(l2)
                    if mm: rows.append({"variant": "mcp_tool", "run": k, "kind": "hook", "ms": float(mm.group(1))}); break
        print("inter run", k, "rows so far", len(rows), flush=True)
    out = arg("--out", None)
    if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
    print("| variant | n | median ms | p90 ms | min | max |\n|:--|--:|--:|--:|--:|--:|")
    for v in only:
        x = sorted(r["ms"] for r in rows if r["variant"] == v)
        if x: print("| %s | %d | %.0f | %.0f | %.0f | %.0f |" % (v, len(x), st.median(x), x[int(.9 * (len(x) - 1))], x[0], x[-1]))
    sys.exit(0)
plan = [v for _ in range(reps) for v in random.sample(only, len(only))]
for k, v in enumerate(plan):
    d = "%s/run%02d-%s" % (wd, k, v); os.makedirs(d, exist_ok=True)
    s = {"hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [V[v]]}]}}
    cmd = ["claude", "-p", "Call the Bash tool %d times in a row, one call per turn, each with the command `true`. Write no other text." % calls, "--model", "haiku",
           "--permission-mode", "bypassPermissions", "--settings", json.dumps(s), "--debug-file", d + "/dbg.log", "--output-format", "json", "--max-budget-usd", "0.3"]
    if v == "mcp_tool": cmd += ["--mcp-config", json.dumps({"mcpServers": {"noop": {"command": "python3", "args": [bi]}}})]
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=280, env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
    try: j = json.loads(r.stdout)
    except ValueError: j = {}
    n = 0
    for line in open(d + "/dbg.log", errors="replace"):
        m = LINE.search(line)
        if m:
            rows.append({"variant": v, "run": k, "kind": "hook", "ms": int(m.group(3)), "status": int(m.group(2))}); n += 1
        mm = SETTLED.search(line)
        if mm:  # the platform's wrapper time of the whole PostToolUse event for this tool call (all hooks of the event; here only ours plus the platform's own)
            rows.append({"variant": v, "run": k, "kind": "event", "ms": float(mm.group(1))})
    print(v, "run", k, "hook lines", n, "cost", j.get("total_cost_usd"), flush=True)
out = arg("--out", None)
if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
print("| variant | kind | n | median ms | p90 ms | min | max |\n|:--|:--|--:|--:|--:|--:|--:|")
for v in only:
    for kd in ("hook", "event"):
        x = sorted(r["ms"] for r in rows if r["variant"] == v and r["kind"] == kd)
        if x: print("| %s | %s | %d | %.0f | %.0f | %.0f | %.0f |" % (v, kd, len(x), st.median(x), x[int(.9 * (len(x) - 1))], x[0], x[-1]))
