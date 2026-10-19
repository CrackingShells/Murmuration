#!/usr/bin/env python3
"""Claim w01-c3, checks I1-I3: the run-index alternative, simulated.

I1 fire-cost: run index_hook.py 50 times on a synthetic SubagentStart input and time it.
I2 replay: build the hook inputs this run WOULD have produced (one SessionStart for the main session, one
   SubagentStart per agent file; ASSUMPTION: the hook fires for each and its input carries the fields of the probe
   report), run them through index_hook.py into a temporary lab, and read the spend through that index.
I3 compare with the scan: sessions and USD found by the index vs by the scan (live data, same moment).
Writes index_test.txt. Run: python3 -I index_test.py"""
import glob, json, os, subprocess, sys, tempfile, time, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import lab_spend as L
out = []
def say(*a):
    out.append(" ".join(str(x) for x in a)); print(out[-1])

tmp = tempfile.mkdtemp(prefix="w01c3-lab-")
os.makedirs(os.path.join(tmp, "__statera__"))
hook = os.path.join(HERE, "index_hook.py")
# I1
payload = json.dumps({"hook_event_name": "SubagentStart", "session_id": "s", "transcript_path": "/x/s.jsonl", "cwd": tmp + "/sub",
                      "agent_id": "a1", "agent_type": "murmuration:explorer"})
ts = []
for _ in range(50):
    t = time.perf_counter(); subprocess.run([sys.executable, "-I", hook], input=payload, text=True); ts.append(time.perf_counter() - t)
say("I1 hook fire: median %.1f ms, max %.1f ms over 50 runs (python3 -I start-up included)" % (1000 * statistics.median(ts), 1000 * max(ts)))
os.remove(os.path.join(tmp, "__expensa__", "runs.jsonl"))
# I2: replay this run's starts
main_sessions = L.find_ids([L.encode(REPO)])   # the worktree's own folder: the PI session
n = 0
for m in main_sessions:
    sid = os.path.basename(m)[:-6]
    cwd = L.first_cwd(m)
    evs = [{"hook_event_name": "SessionStart", "session_id": sid, "transcript_path": m, "cwd": cwd}]
    for af in L.agent_files(m):
        evs.append({"hook_event_name": "SubagentStart", "session_id": sid, "transcript_path": m, "cwd": cwd,
                    "agent_id": os.path.basename(af)[6:-6], "agent_type": L.meta_of(af).get("agentType")})
    for e in evs:
        subprocess.run([sys.executable, "-I", hook, "--lab", tmp], input=json.dumps(e), text=True); n += 1
idx = os.path.join(tmp, "__expensa__", "runs.jsonl")
say("I2 replayed %d hook inputs -> %d index lines, %d bytes" % (n, sum(1 for _ in open(idx)), os.path.getsize(idx)))
# I3
t = time.perf_counter(); text_i, s_i = L.report(REPO, "index", index=idx); ti = time.perf_counter() - t
t = time.perf_counter(); text_s, s_s = L.report(REPO, "scan"); ts_ = time.perf_counter() - t
say("I3 through the index: %d sessions, USD %.2f to %.2f, %.2f s" % (s_i["sessions"], s_i["low"], s_i["high"], ti))
say("I3 through the scan : %d sessions, USD %.2f to %.2f, %.2f s" % (s_s["sessions"], s_s["low"], s_s["high"], ts_))
say("   sessions only the scan finds: %d, USD %.2f to %.2f (%.1f%% of the scan's low figure)"
    % (s_s["sessions"] - s_i["sessions"], s_s["low"] - s_i["low"], s_s["high"] - s_i["high"], 100 * (s_s["low"] - s_i["low"]) / s_s["low"]))
for k, g in s_s["groups"].items():
    say("   scan group %-45s sessions %3d  USD %.2f to %.2f" % (k, g["n"], g["lo"], g["hi"]))
open(os.path.join(HERE, "index_test.txt"), "w").write("\n".join(out) + "\n")
