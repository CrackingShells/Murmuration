# Times `python3 -S -I run_hook.py budget|handback` against the shipped Rust binary `budget|handback` on the same hook event (a wave-8 worker transcript), interleaved pairs with the order flipped each round, posix_spawn + wait4 for wall and CPU; prints per-event medians and sign counts of (Python - Rust).
# inputs: author's worktree, one transcript, number of rounds; outputs: a JSONL of rows (arm, kind, round, wall_ms, cpu_ms) and a summary on stdout.
# usage: python3 -I w08_v1_pair_time.py WT TRANSCRIPT SCRATCH ROUNDS OUT.jsonl
import json, os, resource, statistics, sys, time, shutil

wt, tr, scratch, rounds, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
py = sys.executable
binpath = os.path.join(wt, "bin", "aarch64-apple-darwin", "murmuration")
run_hook = os.path.join(wt, "scripts", "run_hook.py")
env = dict(os.environ, LC_ALL="en_US.UTF-8", CLAUDE_PLUGIN_ROOT=wt)
env.pop("MURMURATION_NOW", None)


def mk(arm):
    base = os.path.join(scratch, arm)
    shutil.rmtree(base, ignore_errors=True)
    lab = os.path.join(base, "lab")
    os.makedirs(os.path.join(base, "sess", "subagents"))
    os.makedirs(os.path.join(lab, "__statera__"))
    shutil.copy(tr, os.path.join(base, "sess", "subagents", "agent-t1.jsonl"))
    ev = lambda kind, **kw: dict(dict(cwd=lab, hook_event_name=kind, transcript_path=os.path.join(base, "sess", "x.jsonl"), agent_id="t1", agent_type="murmuration:author", permission_mode="auto"), **kw)
    files = {}
    for kind, kw in (("start", dict(k="SubagentStart")), ("batch", dict(k="PostToolBatch", tool_calls=[{"tool_name": "Bash", "tool_use_id": "t"}])), ("post", dict(k="PostToolUse", tool_name="Bash")), ("stop", dict(k="SubagentStop"))):
        k = kw.pop("k")
        p = os.path.join(base, "%s.json" % kind)
        json.dump(ev(k, **kw), open(p, "w"))
        files[kind] = p
    return files


F = {"py": mk("py"), "rs": mk("rs")}
CMD = {"py": [py, "-S", "-I", run_hook, "budget"], "rs": [binpath, "budget"]}


def run(arm, kind):
    fd = os.open(F[arm][kind], os.O_RDONLY)
    devnull = os.open(os.devnull, os.O_WRONLY)
    fa = [(os.POSIX_SPAWN_DUP2, 0, 0) if False else (os.POSIX_SPAWN_DUP2, fd, 0), (os.POSIX_SPAWN_DUP2, devnull, 1), (os.POSIX_SPAWN_DUP2, devnull, 2)]
    t0 = time.perf_counter_ns()
    pid = os.posix_spawn(CMD[arm][0], CMD[arm], env, file_actions=fa)
    _, st, ru = os.wait4(pid, 0)
    t1 = time.perf_counter_ns()
    os.close(fd); os.close(devnull)
    return (t1 - t0) / 1e6, (ru.ru_utime + ru.ru_stime) * 1e3, st


rows = []
kinds = ["start", "batch", "post"]
for kind in kinds:
    run("py", "start"), run("rs", "start")   # warm
for r in range(rounds):
    for kind in kinds:
        order = ("py", "rs") if r % 2 == 0 else ("rs", "py")
        for arm in order:
            w, c, st = run(arm, kind)
            rows.append(dict(arm=arm, kind=kind, round=r, wall_ms=w, cpu_ms=c, status=st, load1=os.getloadavg()[0]))
with open(out, "w") as fh:
    for x in rows:
        fh.write(json.dumps(x) + "\n")
for kind in kinds:
    pw = {x["round"]: x for x in rows if x["kind"] == kind and x["arm"] == "py"}
    rw = {x["round"]: x for x in rows if x["kind"] == kind and x["arm"] == "rs"}
    dw = [pw[i]["wall_ms"] - rw[i]["wall_ms"] for i in pw]
    dc = [pw[i]["cpu_ms"] - rw[i]["cpu_ms"] for i in pw]
    q = lambda v, p: sorted(v)[int(p * (len(v) - 1))]
    print("%-6s n=%d wall py-rs median %.1f [p10 %.1f, p90 %.1f] py>rs %d | cpu median %.1f py>rs %d | py wall med %.1f rs wall med %.1f | status nonzero %d" % (
        kind, len(dw), statistics.median(dw), q(dw, .1), q(dw, .9), sum(d > 0 for d in dw), statistics.median(dc), sum(d > 0 for d in dc),
        statistics.median(x["wall_ms"] for x in pw.values()), statistics.median(x["wall_ms"] for x in rw.values()), sum(1 for x in rows if x["status"] != 0)))
print("load1 median", statistics.median(x["load1"] for x in rows))
