"""Times old vs new hook commands as strictly interleaved pairs (order within a pair randomised), wall and CPU, from two plugin roots and recorded payloads, to a JSONL and a median-paired-ratio table with a bootstrap interval.

Inputs: --old DIR --new DIR (plugin roots: hooks/hooks.json + scripts/), --payloads recorded_payloads_rec1.jsonl, --long TRANSCRIPT (a worker transcript, copied into each lab), --fx DIR (scratch), --n pairs per case, --seed.
Output: <fx>/pairs.jsonl (case, i, order, wall_old, wall_new, cpu_old, cpu_new, len_old, len_new) and a table on stdout: median wall/CPU of each, median of paired ratios new/old with a 95% bootstrap interval over pairs.
Each start is `sh -c 'cd LAB && <command of hooks.json>'` via os.posix_spawn, payload on stdin, CLAUDE_PLUGIN_ROOT set, CLAUDE_PROJECT_DIR unset, as the platform runs a hook. Written independently of hook_cost_time.py.
--stdin sock feeds the payload through a socketpair (as the platform does: measured fstat of fd 0 in a headless run = socket) instead of a file; --pad N makes every payload carry a tool_response string of N bytes (real PostToolUse payloads hold the tool output).
--grow adds, before each pair, the same fresh request (new id) to both lab transcripts so the new version reads a real delta instead of nothing.
"""
import argparse, json, os, random, re, shutil, statistics as st, time

ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True); ap.add_argument("--new", required=True)
ap.add_argument("--payloads", required=True); ap.add_argument("--long", required=True)
ap.add_argument("--fx", required=True); ap.add_argument("--n", type=int, default=60)
ap.add_argument("--seed", type=int, default=1); ap.add_argument("--grow", action="store_true")
ap.add_argument("--strip-sc", action="store_true", help="before each spawn of the second arm ('new') delete the `sc` key of the worker state, so that its transcript is read from the start (ablation of the offset read)")
ap.add_argument("--stdin", default="file"); ap.add_argument("--pad", type=int, default=0)
ap.add_argument("--cases", default="main_post,main_batch,long_post,long_batch")
a = ap.parse_args()
random.seed(a.seed)
VARS = {"old": os.path.abspath(a.old), "new": os.path.abspath(a.new)}
FX = os.path.abspath(a.fx); shutil.rmtree(FX, ignore_errors=True); os.makedirs(FX)
rows = [json.loads(l) for l in open(a.payloads)]
def pick(label, agent, tool=None):
    for r in rows:
        p = json.loads(r["payload"])
        if r["label"] == label and bool(p.get("agent_id")) == agent and (tool is None or p.get("tool_name") == tool):
            return p
B = dict(main_post=pick("PostToolUse||budget.py", False, "Bash"), main_batch=pick("PostToolBatch||budget.py", False),
         start=pick("SubagentStart||budget.py", True), a_post=pick("PostToolUse||budget.py", True, "Bash"),
         a_batch=pick("PostToolBatch||budget.py", True))
AG = "alongw05"
LAB, SESS = {}, {}
for v in VARS:
    lab = os.path.join(FX, v, "lab"); sess = os.path.join(FX, v, "sess")
    os.makedirs(os.path.join(lab, "__statera__")); os.makedirs(os.path.join(sess, "subagents"))
    shutil.copy(a.long, os.path.join(sess, "subagents", "agent-%s.jsonl" % AG))
    json.dump({"name": "explorer-w05-long", "agentType": "murmuration:explorer"}, open(os.path.join(sess, "subagents", "agent-%s.meta.json" % AG), "w"))
    open(sess + ".jsonl", "w").close(); LAB[v] = lab; SESS[v] = sess

def pl(v, kind, agent=None):
    p = dict(B[kind]); p["cwd"] = LAB[v]; p["transcript_path"] = SESS[v] + ".jsonl"
    if agent:
        p["agent_id"] = agent; p["agent_type"] = "murmuration:explorer"
    if a.pad: p["tool_response"] = {"stdout": "x" * a.pad}
    return (json.dumps(p) + "\n").encode()

def cmd(v, event, tool=None, source=None):
    h = json.load(open(os.path.join(VARS[v], "hooks", "hooks.json")))["hooks"][event]
    out = []
    for g in h:
        m = g.get("matcher")
        if m is not None and not re.fullmatch(m, tool or source or ""):
            continue
        out += [x["command"] for x in g["hooks"]]
    return out

def spawn(v, command, data):
    import socket, threading
    if a.stdin == "sock":
        sa, sb = socket.socketpair(); fh = sb
        def feed():
            sa.sendall(data); sa.close()
        th = threading.Thread(target=feed); th.start()
    else:
        ip = os.path.join(FX, "stdin_%s.json" % v); open(ip, "wb").write(data); fh = open(ip, "rb")
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=VARS[v]); env.pop("CLAUDE_PROJECT_DIR", None)
    ro, wo = os.pipe(); re_, we = os.pipe()
    fa = [(os.POSIX_SPAWN_DUP2, fh.fileno(), 0), (os.POSIX_SPAWN_DUP2, wo, 1), (os.POSIX_SPAWN_DUP2, we, 2),
          (os.POSIX_SPAWN_CLOSE, ro), (os.POSIX_SPAWN_CLOSE, re_), (os.POSIX_SPAWN_CLOSE, wo), (os.POSIX_SPAWN_CLOSE, we)]
    t0 = time.perf_counter()
    pid = os.posix_spawn("/bin/sh", ["sh", "-c", 'cd "%s" && %s' % (LAB[v], command)], env, file_actions=fa)
    os.close(wo); os.close(we); out = b""
    while True:
        c = os.read(ro, 65536)
        if not c: break
        out += c
    err = os.read(re_, 65536)
    _, status, ru = os.wait4(pid, 0); wall = (time.perf_counter() - t0) * 1000
    os.close(ro); os.close(re_); fh.close()
    if a.stdin == "sock": th.join()
    return wall, (ru.ru_utime + ru.ru_stime) * 1000, len(out), os.waitstatus_to_exitcode(status), err

# seed the long worker through each version's own SubagentStart, raise B and T so the check is the quiet one, one unmeasured check
for v in VARS:
    for c in cmd(v, "SubagentStart", source="murmuration:explorer"):
        if "budget" in c: spawn(v, c, pl(v, "start", AG))
    sp = os.path.join(LAB[v], "__statera__", ".harness", AG + ".json"); s = json.load(open(sp))
    s.update(B=1e6, T=1e6, brief_read=True, warned=True); json.dump(s, open(sp, "w"))
    for c in cmd(v, "PostToolBatch"): spawn(v, c, pl(v, "a_batch", AG))
    s = json.load(open(sp)); s.update(B=1e6, T=1e6); json.dump(s, open(sp, "w"))

def grow(i):
    """append one fresh assistant request (unique id, usage) and one user tool_result line to both transcripts"""
    for v in VARS:
        p = os.path.join(SESS[v], "subagents", "agent-%s.jsonl" % AG)
        a1 = {"type": "assistant", "requestId": "req_w05_%d" % i, "timestamp": "2026-10-19T19:%02d:%02d.000Z" % (50 + i // 3600 % 9, i % 60),
              "message": {"id": "msg_w05_%d" % i, "role": "assistant", "model": "claude-sonnet-4-5", "content": [{"type": "text", "text": "x" * 400}],
                          "usage": {"input_tokens": 5, "output_tokens": 200, "cache_read_input_tokens": 30000, "cache_creation_input_tokens": 800}}}
        u1 = {"type": "user", "timestamp": "2026-10-19T19:%02d:%02d.500Z" % (50 + i // 3600 % 9, i % 60), "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t%d" % i, "content": "y" * 2000}]}}
        with open(p, "a") as f:
            f.write(json.dumps(a1) + "\n" + json.dumps(u1) + "\n")

CASES = {"main_post": ("PostToolUse", "main_post", None, "Bash"), "main_batch": ("PostToolBatch", "main_batch", None, None),
         "long_post": ("PostToolUse", "a_post", AG, "Bash"), "long_batch": ("PostToolBatch", "a_batch", AG, None)}
cases = a.cases.split(",")
out = open(os.path.join(FX, "pairs.jsonl"), "w"); res = {c: [] for c in cases}
for i in range(-2, a.n):           # two unmeasured rounds
    if a.grow and i >= 0: grow(i)
    for c in random.sample(cases, len(cases)):
        ev, kind, ag, tool = CASES[c]
        order = random.sample(["old", "new"], 2); m = {}
        for v in order:
            if a.strip_sc and v == "new" and ag:
                sp = os.path.join(LAB[v], "__statera__", ".harness", ag + ".json"); s_ = json.load(open(sp)); s_.pop("sc", None); json.dump(s_, open(sp, "w"))
            cm = cmd(v, ev, tool=tool)
            assert len(cm) == 1, (v, ev, cm)
            m[v] = spawn(v, cm[0], pl(v, kind, ag))
        if i < 0: continue
        r = dict(case=c, i=i, order=order, wall_old=m["old"][0], wall_new=m["new"][0], cpu_old=m["old"][1], cpu_new=m["new"][1],
                 len_old=m["old"][2], len_new=m["new"][2], rc_old=m["old"][3], rc_new=m["new"][3], err_old=len(m["old"][4]), err_new=len(m["new"][4]))
        out.write(json.dumps(r) + "\n"); res[c].append(r)
def boot(xs, k=4000):
    n = len(xs); ms = sorted(st.median(random.choices(xs, k=n)) for _ in range(k)); return ms[int(.025 * k)], ms[int(.975 * k)]
print("case          n  wall_old wall_new  ratio(med paired) 95%CI        cpu_old cpu_new ratio 95%CI       outlen o/n")
for c in cases:
    R = res[c]; w = [r["wall_new"] / r["wall_old"] for r in R]; q = [r["cpu_new"] / r["cpu_old"] for r in R]
    lo, hi = boot(w); clo, chi = boot(q)
    print("%-12s %3d %8.1f %8.1f   %.3f  (%.3f-%.3f)   %7.1f %7.1f  %.3f (%.3f-%.3f)  %d/%d" % (c, len(R), st.median(r["wall_old"] for r in R), st.median(r["wall_new"] for r in R), st.median(w), lo, hi,
          st.median(r["cpu_old"] for r in R), st.median(r["cpu_new"] for r in R), st.median(q), clo, chi, R[-1]["len_old"], R[-1]["len_new"]))
