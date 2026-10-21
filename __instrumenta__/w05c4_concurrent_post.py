"""Times N simultaneous starts of the PostToolUse hook command of two plugin roots (old and new), for main-thread payloads and for N distinct workers, from recorded payloads to a per-process wall table.

usage: w05c4_concurrent_post.py --old DIR --new DIR --payloads recorded_payloads_rec1.jsonl --transcript worker.jsonl --fx DIR [--n 1,3,5,8] [--reps 8] [--seed 1]
Each rep launches N `sh -c 'cd LAB && <PostToolUse command of the variant's hooks.json>'` at once (posix_spawn, one thread per child, payload through a socketpair), waits for all, and records each one's wall; the variants and the N values are interleaved in random order.
Main case: the recorded main-thread payload (no agent_id). Worker case: N workers `cN_i`, each seeded through the variant's own SubagentStart (unmeasured), each with its own copy of the transcript, B and T raised so the check is the quiet one; one unmeasured check first.
Output: markdown table: case, N, per-process wall median and slowest-of-batch median, by variant. Purpose (w05-c4): the platform records hook durations 3 to 7 times the bare ones, partly because the starts of a moment are concurrent (explorer-w05-d); this is the PostToolUse start under that load.
"""
import argparse, json, os, random, re, shutil, socket, statistics as st, threading, time
ap = argparse.ArgumentParser()
for k in ("--old", "--new", "--payloads", "--transcript", "--fx"):
    ap.add_argument(k, required=True)
ap.add_argument("--n", default="1,3,5,8"); ap.add_argument("--reps", type=int, default=8); ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args(); random.seed(a.seed)
NS = [int(x) for x in a.n.split(",")]; V = {"old": os.path.abspath(a.old), "new": os.path.abspath(a.new)}
FX = os.path.abspath(a.fx); shutil.rmtree(FX, ignore_errors=True); os.makedirs(FX)
rows = [json.loads(l) for l in open(a.payloads)]
def pick(label, agent):
    return next(json.loads(r["payload"]) for r in rows if r["label"] == label and bool(json.loads(r["payload"]).get("agent_id")) == agent)
P = dict(main=pick("PostToolUse||budget.py", False), post=pick("PostToolUse||budget.py", True), start=pick("SubagentStart||budget.py", True))
LAB, SESS = {}, {}
for v in V:
    LAB[v] = os.path.join(FX, v, "lab"); SESS[v] = os.path.join(FX, v, "sess")
    os.makedirs(os.path.join(LAB[v], "__statera__")); os.makedirs(os.path.join(SESS[v], "subagents")); open(SESS[v] + ".jsonl", "w").close()
def command(v, event):
    h = json.load(open(os.path.join(V[v], "hooks", "hooks.json")))["hooks"][event]
    return [x["command"] for g in h if g.get("matcher") is None for x in g["hooks"] if "budget.py" in x["command"]][0]
def spawn(v, cmd, payload, out, i):
    sa, sb = socket.socketpair()
    th = threading.Thread(target=lambda: (sa.sendall(payload), sa.close())); th.start()
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=V[v]); env.pop("CLAUDE_PROJECT_DIR", None)
    t0 = time.perf_counter()
    pid = os.posix_spawn("/bin/sh", ["sh", "-c", 'cd "%s" && %s' % (LAB[v], cmd)], env, file_actions=[(os.POSIX_SPAWN_DUP2, sb.fileno(), 0), (os.POSIX_SPAWN_DUP2, os.open(os.devnull, os.O_WRONLY), 1)])
    os.waitpid(pid, 0); out[i] = (time.perf_counter() - t0) * 1000; sb.close(); th.join()
def body(v, kind, agent=None):
    p = dict(P[kind], cwd=LAB[v], transcript_path=SESS[v] + ".jsonl")
    if agent: p.update(agent_id=agent, agent_type="murmuration:explorer")
    return (json.dumps(p) + "\n").encode()
WORKERS = ["c%d" % i for i in range(max(NS))]
for v in V:
    for w in WORKERS:
        shutil.copy(a.transcript, os.path.join(SESS[v], "subagents", "agent-%s.jsonl" % w))
        json.dump({"name": "explorer-w05-%s" % w, "agentType": "murmuration:explorer"}, open(os.path.join(SESS[v], "subagents", "agent-%s.meta.json" % w), "w"))
        spawn(v, command(v, "SubagentStart") if False else json.load(open(os.path.join(V[v], "hooks", "hooks.json")))["hooks"]["SubagentStart"][0]["hooks"][0]["command"], body(v, "start", w), [0], 0)
        sp = os.path.join(LAB[v], "__statera__", ".harness", w + ".json"); s = json.load(open(sp)); s.update(B=1e6, T=1e6, brief_read=True, warned=True); json.dump(s, open(sp, "w"))
        spawn(v, command(v, "PostToolUse"), body(v, "post", w), [0], 0)
        s = json.load(open(sp)); s.update(B=1e6, T=1e6); json.dump(s, open(sp, "w"))
res = {}
plan = [(c, n, v) for _ in range(a.reps + 1) for c in ("main", "worker") for n in NS for v in V]
random.shuffle(plan)
for k, (case, n, v) in enumerate(plan):
    out = [None] * n
    ths = [threading.Thread(target=spawn, args=(v, command(v, "PostToolUse"), body(v, "main") if case == "main" else body(v, "post", WORKERS[i]), out, i)) for i in range(n)]
    [t.start() for t in ths]; [t.join() for t in ths]
    if k >= len(NS) * 4:   # the first rounds are unmeasured
        res.setdefault((case, n, v), []).append(out)
print("| case | N at once | old: per-process median ms (slowest median) | new: per-process median ms (slowest median) | new/old |\n|:--|--:|--:|--:|--:|")
for case in ("main", "worker"):
    for n in NS:
        cells = {v: res.get((case, n, v), []) for v in V}
        m = {v: (st.median(x for o in cells[v] for x in o), st.median(max(o) for o in cells[v])) for v in V if cells[v]}
        print("| %s | %d | %.1f (%.1f) | %.1f (%.1f) | %.2f |" % (case, n, *m["old"], *m["new"], m["new"][0] / m["old"][0]))
