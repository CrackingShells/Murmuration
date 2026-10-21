"""Times forms of the hooks' sh gate on main-thread and worker payloads of N bytes fed through a socketpair, from the forms listed in FORMS to a median-wall table (stdout); stub python3 that prints STARTED.

Inputs: none (synthetic PostToolUse payloads padded to N bytes; the worker's has `"agent_id"` at byte ~500 as the platform writes it). Output: median wall ms over --n rounds per size, form and thread type, interleaved.
usage: w05c4_gate_forms.py [--n 30] [--sizes 2000,30000,200000,500000]
Purpose (w05-c4): whether the gate can read its stdin in blocks without a process start; `cat` is a start (about 30 to 60 ms here), `$(</dev/stdin)` is a bash feature (read in blocks, no fork).
"""
import json, os, random, socket, statistics as st, sys, tempfile, threading, time
argv = sys.argv[1:]; opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
n = int(opt("--n", 30)); sizes = [int(x) for x in opt("--sizes", "2000,30000,200000,500000").split(",")]
tmp = tempfile.mkdtemp(); stub = os.path.join(tmp, "python3"); open(stub, "w").write('#!/bin/sh\ncat >/dev/null\necho STARTED\n'); os.chmod(stub, 0o755)
env = dict(os.environ, PATH=tmp + ":" + os.environ["PATH"])
TAIL = "case $p in *'\"agent_id\"'*) printf '%s\\n' \"$p\" | python3 -S x.py;; esac"
FORMS = {
 "readloop": "p=; while IFS= read -r l || [ -n \"$l\" ]; do p=$p$l; done; " + TAIL,
 "p=$(cat)": "p=$(cat); " + TAIL,
 "$(</dev/stdin)+loop fallback": "p=$(</dev/stdin); [ -n \"$p\" ] || while IFS= read -r l || [ -n \"$l\" ]; do p=$p$l; done; " + TAIL,
 "sh floor": ":",
}
def run(cmd, data):
    sa, sb = socket.socketpair()
    def feed():
        try:
            sa.sendall(data)
        except OSError:   # a gate that never reads (the floor form) closes first
            pass
        sa.close()
    th = threading.Thread(target=feed); th.start()
    t0 = time.perf_counter(); pid = os.posix_spawn("/bin/sh", ["sh", "-c", cmd], env, file_actions=[(os.POSIX_SPAWN_DUP2, sb.fileno(), 0), (os.POSIX_SPAWN_DUP2, os.open(os.devnull, os.O_WRONLY), 1)])
    os.waitpid(pid, 0); w = (time.perf_counter() - t0) * 1000; sb.close(); th.join(); return w
def payload(size, worker):
    d = {"session_id": "s", "transcript_path": "/x/y.jsonl", "cwd": "/tmp/lab", "scratchpad_dir": "/tmp/sp", "prompt_id": "p", "permission_mode": "auto"}
    if worker: d.update(agent_id="a1b2c3d4e5", agent_type="murmuration:explorer")
    d.update(effort="high", hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}, tool_response={"stdout": "x" * size}, tool_use_id="tu")
    return (json.dumps(d) + "\n").encode()
print("median wall ms, n=%d, stdin a socket; gate form x payload bytes (main thread / worker, the worker one includes the stub)" % n)
for size in sizes:
    for worker in (False, True):
        data = payload(size, worker); res = {k: [] for k in FORMS}
        for _ in range(n):
            for k in random.sample(list(FORMS), len(FORMS)): res[k].append(run(FORMS[k], data))
        print("N=%7d %-6s " % (len(data), "worker" if worker else "main") + "  ".join("%s %6.1f" % (k, st.median(v)) for k, v in res.items()), flush=True)
