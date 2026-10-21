# w06-c4 verifier: recomputes s2 (platform-recorded hook time of budget/handback/outage hooks per run, command hooks from dbg.log 'finished with status (N ms)', mcp_tool hooks from transcript hook_success durationMs) for the s2 pairs under /private/tmp/murmuration-w06/author-w06-4/runs; output: per pair ratio and pooled ratios; written independently of w06c4_measure.py
import glob, json, os, re, sys
S = "/private/tmp/murmuration-w06/author-w06-4/runs"
H = os.path.expanduser("~")
def total(name):
    cmd = mcp = 0
    pat = re.compile(r'/scripts/(budget|handback|outage)\.py"?[^\]]*\].*finished with status \d+ \((\d+)ms\)')
    for l in open(f"{S}/{name}/dbg.log", errors="replace"):
        m = pat.search(l)
        if m and "Hooks:" in l:
            cmd += int(m.group(2))
    sid = json.load(open(f"{S}/{name}/run.json"))["session_id"]
    d = glob.glob(f"{H}/.claude/projects/*author-w06-4-runs-{name.replace('_','-')}-lab")[0]
    files = [f"{d}/{sid}.jsonl"] + glob.glob(f"{d}/{sid}/subagents/agent-*.jsonl")
    n = 0
    for f in files:
        for line in open(f, errors="replace"):
            if "hook_success" in line and "plugin:murmuration:hooks/hook" in line:
                try: a = json.loads(line).get("attachment") or {}
                except ValueError: continue
                if a.get("type") == "hook_success" and a.get("command") == "plugin:murmuration:hooks/hook":
                    mcp += a.get("durationMs", 0); n += 1
    return cmd, mcp, n
tm = tn = 0
for pre in ("s2_", "f_s2_", "g_s2_"):
    pm = pn = 0
    for i in range(3):
        try:
            m = total(f"{pre}main_{i}"); n = total(f"{pre}new_{i}")
        except Exception as e:
            print(pre, i, "missing", e); continue
        mt, nt = m[0] + m[1], n[0] + n[1]
        print(f"{pre}{i}: main {mt} (cmd {m[0]}, mcp {m[1]}) new {nt} (cmd {n[0]}, mcp {n[1]}, {n[2]} calls) ratio {nt/mt:.3f}")
        pm += mt; pn += nt
    print(f"  pooled {pre}: {pn}/{pm} = {pn/pm:.3f}"); tm += pm; tn += pn
print(f"pooled all: {tn}/{tm} = {tn/tm:.3f}")
