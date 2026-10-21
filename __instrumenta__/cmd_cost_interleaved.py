"""Times shell commands in interleaved rounds (cells shuffled each round), wall and CPU per start, from a JSON case file to a JSONL of runs and a median/p90 table.

usage: cmd_cost_interleaved.py CASES.json --n N [--warm 2] [--seed S] [--out runs.jsonl] [--cwd DIR]
CASES.json: [{"name": str, "sh": "command run as `sh -c`", "stdin": "text or null", "env": {optional extra env}}, ...]. Start = os.posix_spawn of /bin/sh -c (as the platform starts a hook), stdout and stderr to /dev/null,
stdin from a temp file (hooks get a socket on fd 0, see w04-c5 verdict: small payloads are the same); wall = perf_counter around spawn..wait4, CPU = user+sys from wait4's rusage.
"""
import json, os, random, resource, statistics as st, sys, tempfile, time
argv = sys.argv[1:]
opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
cases = json.load(open(argv[0])); n = int(opt("--n", 30)); warm = int(opt("--warm", 2)); random.seed(int(opt("--seed", 20261021)))
out = opt("--out"); cwd = opt("--cwd", os.getcwd())
tmp = tempfile.mkdtemp(prefix="cci-")
for i, c in enumerate(cases):
    p = os.path.join(tmp, "in%d" % i); open(p, "w").write(c.get("stdin") or ""); c["_in"] = p
def run(c):
    fa = [(os.POSIX_SPAWN_OPEN, 0, c["_in"], os.O_RDONLY, 0), (os.POSIX_SPAWN_OPEN, 1, os.devnull, os.O_WRONLY, 0), (os.POSIX_SPAWN_OPEN, 2, os.devnull, os.O_WRONLY, 0)]
    env = dict(os.environ, **(c.get("env") or {}))
    t = time.perf_counter()
    pid = os.posix_spawn("/bin/sh", ["sh", "-c", "cd %s && %s" % (cwd, c["sh"])], env, file_actions=fa)
    _, status, ru = os.wait4(pid, 0)
    return (time.perf_counter() - t) * 1000, (ru.ru_utime + ru.ru_stime) * 1000, os.waitstatus_to_exitcode(status)
rows = []
for r in range(-warm, n):
    order = cases[:]; random.shuffle(order)
    for c in order:
        w, cpu, rc = run(c)
        if r >= 0: rows.append({"name": c["name"], "round": r, "wall_ms": w, "cpu_ms": cpu, "rc": rc})
if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
print("| case | n | wall median ms | wall p90 ms | cpu median ms | rc != 0 |\n|:--|--:|--:|--:|--:|--:|")
for c in cases:
    v = [x for x in rows if x["name"] == c["name"]]; w = sorted(x["wall_ms"] for x in v)
    print("| %s | %d | %.1f | %.1f | %.1f | %d |" % (c["name"], len(v), st.median(w), w[int(.9 * (len(w) - 1))], st.median(x["cpu_ms"] for x in v), sum(x["rc"] != 0 for x in v)))
