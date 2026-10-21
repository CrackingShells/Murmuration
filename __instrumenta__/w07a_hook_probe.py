"""Measures what the platform records for do-nothing PostToolUse hooks of different command forms, and where inside that time the hook's main() starts, from headless `claude -p` haiku sessions (default permission mode; the model calls Read on small files, one per turn) with --debug-file; every variant is registered with `if: Read(**/f_<variant>.txt)` so all share a session's load; inputs: workdir (outside any lab), bindir (c_noop, rs_*, stamp_hook), --sessions K, --calls per variant per session, --variants, --seed, --reparse (re-read existing logs); output: JSONL rows {variant, session, idx, dur_ms (platform 'finished (N ms)'), issue_ms (debug-log time of the line before 'finished'), fin_ms, main_ms (stamp_hook only: hook main() start, realtime ms), load1} and a markdown table on stdout. Run with CLAUDE_CODE_SHELL=/bin/bash, never from inside a lab/plugin folder."""
import json, os, random, re, subprocess, sys, statistics as st, datetime
a = sys.argv[1:]
arg = lambda k, d: a[a.index(k) + 1] if k in a else d
wd, bd = os.path.abspath(a[0]), os.path.abspath(a[1])
K, per, seed = int(arg("--sessions", 1)), int(arg("--calls", 8)), int(arg("--seed", 1))
random.seed(seed)
SF = "%s/stamps.txt" % wd
V = {
 "colon": ":",
 "true": "/usr/bin/true",
 "cnoop": "%s/c_noop" % bd,
 "execcnoop": "exec %s/c_noop" % bd,
 "rsnostd": "%s/rs_nostd" % bd,
 "rsrelease": "%s/rs_release" % bd,
 "pysi": "python3 -S -I -c pass",
 "shc": "/bin/sh -c :",
 "stamp": "%s/stamp_hook %s stamp" % (bd, SF),
 "execstamp": "exec %s/stamp_hook %s execstamp" % (bd, SF),
 "shellprobe": 'ps -o pid=,ppid=,command= -p $$ -p $PPID >> %s/shellprobe.txt; echo "0=$0 BASH_VERSION=$BASH_VERSION ZSH_VERSION=$ZSH_VERSION SHELL=$SHELL" >> %s/shellprobe.txt' % (wd, wd),
}
for _v in ("colon", "cnoop", "execcnoop", "stamp", "shellprobe"): V[_v + "_bash"] = V[_v] + " #b"  # same command text plus a comment, registered with "shell": "bash" (the hook's own shell field)
V["stamp_bash"] = "%s/stamp_hook %s stampb #b" % (bd, SF)
only = arg("--variants", ",".join(V)).split(",")
os.makedirs(wd, exist_ok=True)
for v in only: open("%s/f_%s.txt" % (wd, v), "w").write("x\n")
hooks = [dict({"type": "command", "command": V[v], "if": "Read(**/f_%s.txt)" % v}, **({"shell": "bash"} if v.endswith("_bash") else {})) for v in only]
settings = {"hooks": {"PostToolUse": [{"matcher": "Read", "hooks": hooks}]}}
TS = re.compile(r"^(\d{4}-\d\d-\d\dT[\d:.]+)Z ")
def ms(line):
    m = TS.match(line)
    if not m: return None
    return datetime.datetime.fromisoformat(m.group(1) + "+00:00").timestamp() * 1000
FIN = re.compile(r"Hooks: PostToolUse:Read \[(.*)\] finished with status (\d+) \((\d+)ms\)")
rows = []
for k in range(K):
    d = "%s/s%02d" % (wd, k); os.makedirs(d, exist_ok=True)
    order = [v for v in only for _ in range(per)]; random.shuffle(order)
    prompt = "Call the Read tool once per turn, one call per turn, never several in one message, on exactly these files in this order, no other text:\n" + "\n".join("%s/f_%s.txt" % (wd, v) for v in order)
    cmd = ["claude", "-p", prompt, "--model", "haiku", "--settings", json.dumps(settings), "--debug-file", d + "/dbg.log", "--output-format", "json", "--add-dir", wd]
    la = os.getloadavg()[0]
    if "--reparse" in a: r = type("R", (), {"stdout": ""})()  # re-read existing s*/dbg.log, no new session
    else:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900, env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
        open(d + "/stdout.json", "w").write(r.stdout)
    lines = open(d + "/dbg.log", errors="replace").read().split("\n")
    idx = 0
    for i, line in enumerate(lines):
        m = FIN.search(line)
        if not m: continue
        cmdtxt = m.group(1)
        for v in only:
            if V[v] == cmdtxt:
                prev = next((ms(lines[j]) for j in range(i - 1, max(i - 8, 0), -1) if ms(lines[j])), None)
                rows.append({"variant": v, "session": k, "idx": idx, "dur_ms": int(m.group(3)), "issue_ms": prev, "fin_ms": ms(line), "load1": la}); idx += 1; break
    print("session", k, "hook rows", idx, "stdout bytes", len(r.stdout), flush=True)
# join stamps (variant tag + order within variant) to rows
if os.path.exists(SF):
    st_rows = {}
    for l in open(SF):
        t, pid, ppid, a0, b0 = l.split(); st_rows.setdefault(t, []).append((int(pid), int(ppid), int(a0) / 1e6, int(b0) / 1e6))
    seen = {}
    for r in sorted(rows, key=lambda r: (r["session"], r["idx"])):
        t = {"stamp": "stamp", "execstamp": "execstamp", "stamp_bash": "stampb"}.get(r["variant"])
        if t and t in st_rows:
            n = seen.get(t, 0); seen[t] = n + 1
            if n < len(st_rows[t]): r["main_ms"] = st_rows[t][n][2]; r["hook_ppid"] = st_rows[t][n][1]
out = arg("--out", None)
if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
print("| variant | n | platform ms median | p90 | min | max |\n|:--|--:|--:|--:|--:|--:|")
for v in only:
    x = [r["dur_ms"] for r in rows if r["variant"] == v]
    if x: print("| %s | %d | %.0f | %.0f | %d | %d |" % (v, len(x), st.median(x), q(x, .9), min(x), max(x)))
