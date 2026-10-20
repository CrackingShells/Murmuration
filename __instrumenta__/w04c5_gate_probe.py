"""Runs the sh gate command of hooks/hooks.json (PostToolUse entry) on payload shapes with a stub `python3` that prints STARTED, and times the gate on payloads of growing size with stdin as a pipe and as a file.

Inputs: --root PLUGIN_ROOT (reads hooks/hooks.json), --payloads recorded_payloads_rec1.jsonl. Output on stdout: one line per shape (STARTED or not), then wall ms of the gate (median of 15) per size and stdin kind.
Stub python3 lives in a temp dir first on PATH, so the real script never runs: only the decision of the gate is observed.
"""
import argparse, json, os, statistics as st, subprocess, tempfile, time
ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--payloads", required=True); a = ap.parse_args()
cmd = json.load(open(os.path.join(a.root, "hooks", "hooks.json")))["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
tmp = tempfile.mkdtemp(); stub = os.path.join(tmp, "python3")
open(stub, "w").write('#!/bin/sh\ncat >/dev/null\necho STARTED\n'); os.chmod(stub, 0o755)
env = dict(os.environ, PATH=tmp + ":" + os.environ["PATH"], CLAUDE_PLUGIN_ROOT=a.root)
def gate(data, pipe=True):
    if pipe:
        r = subprocess.run(["/bin/sh", "-c", cmd], input=data, capture_output=True, env=env)
    else:
        f = os.path.join(tmp, "in"); open(f, "wb").write(data)
        with open(f, "rb") as fh: r = subprocess.run(["/bin/sh", "-c", cmd], stdin=fh, capture_output=True, env=env)
    return b"STARTED" in r.stdout
rows = [json.loads(l) for l in open(a.payloads)]
def pick(label, agent, tool=None):
    for r in rows:
        p = json.loads(r["payload"])
        if r["label"] == label and bool(p.get("agent_id")) == agent and (tool is None or p.get("tool_name") == tool): return p
W = pick("PostToolUse||budget.py", True, "Bash"); M = pick("PostToolUse||budget.py", False, "Bash")
def js(p, **kw): return (json.dumps(p, **kw) + "\n").encode()
shapes = {
 "worker compact": (js(W, separators=(",", ":")), True),
 "worker default separators": (js(W), True),
 "worker pretty-printed (multi-line)": (js(W, indent=2), True),
 "worker no trailing newline": (js(W).rstrip(b"\n"), True),
 "worker CRLF pretty": (js(W, indent=2).replace(b"\n", b"\r\n"), True),
 "worker agent_id key first": (js(dict([("agent_id", W["agent_id"])] + [(k, v) for k, v in W.items() if k != "agent_id"])), True),
 "worker agent_id key last": (js({**{k: v for k, v in W.items() if k != "agent_id"}, "agent_id": W["agent_id"]}), True),
 "worker agent_id absent": (js({k: v for k, v in W.items() if k != "agent_id"}), False),
 "worker key spelled agentId": (js({("agentId" if k == "agent_id" else k): v for k, v in W.items()}), False),
 "worker key unicode-escaped agent\\u005fid": (js(W).replace(b'"agent_id"', b'"agent\\u005fid"'), False),
 "worker agent_id null": (js(dict(W, agent_id=None)), True),
 "worker agent_id empty string": (js(dict(W, agent_id="")), True),
 "main thread": (js(M), False),
 "main, text 'agent_id' inside tool_input string": (js(dict(M, tool_input={"command": 'grep "agent_id" x.json'})), False),
 "main, tool_response string holding a JSON object with agent_id": (js(dict(M, tool_response={"stdout": json.dumps({"agent_id": "a1"})})), False),
 "main, tool_input OBJECT with key agent_id": (js(dict(M, tool_input={"agent_id": "a1"})), True),
 "main, tool_response OBJECT with key agent_id": (js(dict(M, tool_response={"agent_id": "a1"})), True),
 "main, tool_response nested {'x':{'agent_id':..}}": (js(dict(M, tool_response={"x": {"agent_id": "a1"}})), True),
 "main, bare agent_id (no quotes) in a string": (js(dict(M, tool_response={"stdout": "agent_id=3"})), False),
 "empty stdin": (b"", False),
 "garbage not json": (b"hello\n", False),
}
print("shape | STARTED | as expected for a worker-iff-key reading")
for k, (data, want) in shapes.items():
    got = gate(data); print("%-62s %-7s %s" % (k, got, "ok" if got == want else "DIFFERS (expected %s)" % want))
print("\ngate wall ms, median of 15, payload = main-thread PostToolUse whose tool_response is one string of N bytes (no agent_id): stdin pipe vs file")
for n in (1000, 20000, 200000, 1000000, 4000000):
    d = js(dict(M, tool_response={"stdout": "x" * n}))
    out = []
    for pipe in (True, False):
        ts = []
        for _ in range(15):
            t0 = time.perf_counter(); gate(d, pipe); ts.append((time.perf_counter() - t0) * 1000)
        out.append(st.median(ts))
    print("N=%8d  pipe %8.1f ms   file %8.1f ms" % (n, out[0], out[1]))
