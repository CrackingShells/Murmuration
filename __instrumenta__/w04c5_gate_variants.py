"""Times three forms of the sh gate (the read loop of hooks.json, `p=$(cat)`, and a bare `cat >/dev/null`) on main-thread payloads of N bytes fed through a socketpair, with a stub python3 that never runs for main-thread payloads.

Inputs: none (payloads are synthetic: a main-thread PostToolUse shape padded to N bytes). Output: median wall ms of 25 runs per size and variant, interleaved.
Purpose: whether the per-byte `read` of the gate is what costs on large payloads and whether `p=$(cat)` removes it.
"""
import json, os, random, socket, statistics as st, subprocess, tempfile, threading, time
tmp = tempfile.mkdtemp(); stub = os.path.join(tmp, "python3"); open(stub, "w").write('#!/bin/sh\ncat >/dev/null\necho STARTED\n'); os.chmod(stub, 0o755)
env = dict(os.environ, PATH=tmp + ":" + os.environ["PATH"], CLAUDE_PLUGIN_ROOT="/x")
V = {
 "readloop (shipped)": "p=; while IFS= read -r l || [ -n \"$l\" ]; do p=$p$l; done; case $p in *'\"agent_id\"'*) printf '%s\\n' \"$p\" | python3 -S -I x.py;; esac",
 "p=$(cat)": "p=$(cat); case $p in *'\"agent_id\"'*) printf '%s\\n' \"$p\" | python3 -S -I x.py;; esac",
 "cat>/dev/null (floor)": "cat >/dev/null",
}
def run(cmd, data):
    sa, sb = socket.socketpair()
    th = threading.Thread(target=lambda: (sa.sendall(data), sa.close())); th.start()
    t0 = time.perf_counter(); pid = os.posix_spawn("/bin/sh", ["sh", "-c", cmd], env, file_actions=[(os.POSIX_SPAWN_DUP2, sb.fileno(), 0)])
    os.waitpid(pid, 0); w = (time.perf_counter() - t0) * 1000; sb.close(); th.join(); return w
for n in (1000, 30000, 100000, 300000, 1000000):
    data = (json.dumps({"hook_event_name": "PostToolUse", "tool_response": {"stdout": "x" * n}}) + "\n").encode()
    res = {k: [] for k in V}
    for _ in range(25):
        for k in random.sample(list(V), len(V)): res[k].append(run(V[k], data))
    print("N=%8d  " % n + "   ".join("%s %6.1f" % (k, st.median(v)) for k, v in res.items()))
