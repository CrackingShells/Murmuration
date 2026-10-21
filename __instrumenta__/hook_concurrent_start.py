"""Times N simultaneous starts of one hook command (budget.py SubagentStart from a recorded payload, distinct agent_id each) and reports per-process wall time by N, to test whether starts serialize (a lock, or the machine).

usage: hook_concurrent_start.py PLUGIN_ROOT LAB_DIR PAYLOADS.jsonl --n 1,3,5,8 --reps 8 [--script budget.py]. Each rep launches N `sh -c 'cd LAB && python3 PLUGIN/scripts/budget.py'` at once (posix_spawn, payload file on stdin), waits for all, records each one's wall (spawn to wait4 completion, via a thread per child) and the batch wall. Reps interleave the N values in random order.
Output: markdown table: N, reps, per-process wall median and max-of-batch median, batch wall median.
"""
import json, os, random, statistics as st, sys, tempfile, threading, time
argv = sys.argv[1:]
plugin, lab, payloads = argv[0], argv[1], argv[2]
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
ns = [int(x) for x in opt("--n", "1,3,5,8").split(",")]; reps = int(opt("--reps", 8)); script = opt("--script", "budget.py")
rows = [json.loads(l) for l in open(payloads)]
pay = next(json.loads(r["payload"]) for r in rows if r["label"].startswith("SubagentStart"))
tmp = tempfile.mkdtemp(prefix="chs-")
def one(i, rep, N, out):
    p = dict(pay, agent_id="c%d_%d_%d_%s" % (N, rep, i, os.urandom(3).hex()), cwd=lab)
    f = os.path.join(tmp, "p_%d_%d_%d" % (N, rep, i)); open(f, "w").write(json.dumps(p) + "\n")
    fa = [(os.POSIX_SPAWN_OPEN, 0, f, os.O_RDONLY, 0), (os.POSIX_SPAWN_OPEN, 1, os.devnull, os.O_WRONLY, 0), (os.POSIX_SPAWN_OPEN, 2, os.devnull, os.O_WRONLY, 0)]
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin); env.pop("CLAUDE_PROJECT_DIR", None)
    t = time.perf_counter()
    pid = os.posix_spawn("/bin/sh", ["sh", "-c", 'cd "%s" && python3 "%s/scripts/%s"' % (lab, plugin, script)], env, file_actions=fa)
    os.waitpid(pid, 0); out[i] = (time.perf_counter() - t) * 1000
res = {n: [] for n in ns}
plan = [n for _ in range(reps + 1) for n in random.sample(ns, len(ns))]
for k, N in enumerate(plan):
    out = [None] * N; ths = [threading.Thread(target=one, args=(i, k, N, out)) for i in range(N)]
    t = time.perf_counter(); [x.start() for x in ths]; [x.join() for x in ths]; batch = (time.perf_counter() - t) * 1000
    if k >= len(ns): res[N].append((out, batch))
print("| N at once | reps | per-process wall median ms | slowest-of-batch median ms | batch wall median ms |\n|--:|--:|--:|--:|--:|")
for N in ns:
    allw = [w for o, b in res[N] for w in o]
    print("| %d | %d | %.0f | %.0f | %.0f |" % (N, len(res[N]), st.median(allw), st.median(max(o) for o, b in res[N]), st.median(b for o, b in res[N])))
