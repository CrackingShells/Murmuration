"""Probes whether lab_status.py's parse cache can print a different figure than the uncached run, on a small synthetic config dir, from a lab_status.py path and a scratch dir to printed spend lines for each scenario.

usage: w05c5_repro_stale_probe.py LAB_STATUS.py SCRATCH
Scenarios: S1 a message id copied in a second file (merge_usage mutates the first file's cached usage), then the second file removed; S2 growth of a transcript; S3 same size and mtime, other bytes; S4 corrupt cache variants; S5 concurrent cold runs.
"""
import json, os, shutil, subprocess, sys, time
script, scr = sys.argv[1:3]
shutil.rmtree(scr, ignore_errors=True); os.makedirs(scr)
proj = os.path.join(scr, "proj"); os.makedirs(os.path.join(proj, "__statera__"))
cfg = os.path.join(scr, "cfg")
enc = "".join(c if c.isalnum() else "-" for c in os.path.realpath(proj))
pdir = os.path.join(cfg, "projects", enc); os.makedirs(pdir)
cache = os.path.join(scr, "cache.json")
def rec(sid, mid, out, stop=True, inp=100):
    return json.dumps({"type": "assistant", "sessionId": sid, "cwd": os.path.realpath(proj), "timestamp": "2026-10-20T10:00:00Z",
        "message": {"id": mid, "model": "claude-sonnet-4-5", "stop_reason": "end_turn" if stop else None,
                    "usage": {"input_tokens": inp, "output_tokens": out}}}) + "\n"
def w(name, text, mode="w"):
    open(os.path.join(pdir, name), mode).write(text)
def run(cache_val, extra=()):
    env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, LAB_STATUS_CACHE=cache_val)
    p = subprocess.run([sys.executable, script, "--spend", "--project", proj, *extra], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr
def total(o):
    return [l for l in o.splitlines() if "TOTAL" in l or "main thread" in l][:3]
def cmp(label):
    a, b = run(cache), run("off")
    print("%-40s %s" % (label, "SAME" if a[:2] == b[:2] else "DIFFERENT"), "rc", a[0], b[0])
    if a[:2] != b[:2]:
        print("   cached  :", total(a[1]), a[2][-200:]); print("   uncached:", total(b[1]), b[2][-200:])
# S1
w("s1.jsonl", rec("s1", "m1", 10) + rec("s1", "m2", 5))
w("s2.jsonl", rec("s1", "m1", 5000, inp=9000))   # a copy of m1 in another file, with larger numbers
cmp("S1a cold, copy in two files")
c = json.load(open(cache))
print("   cached usage of m1 in s1.jsonl:", [m for k, m in [e for e in c["files"][os.path.join(pdir, "s1.jsonl")][2]] if k == "m1"][0]["usage"])
cmp("S1b warm")
os.unlink(os.path.join(pdir, "s2.jsonl"))
cmp("S1c second file removed, s1.jsonl untouched")
# S2 growth
w("s1.jsonl", rec("s1", "m3", 77), "a"); cmp("S2 appended a record")
w("s1.jsonl", rec("s1", "m4", 1), "a"); cmp("S2 appended again")
# S3 same size, same mtime
p = os.path.join(pdir, "s1.jsonl"); st = os.stat(p); data = open(p).read()
open(p, "w").write(data.replace('"output_tokens": 77', '"output_tokens": 78')); os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
print("   size same:", os.path.getsize(p) == st.st_size); cmp("S3 same size and mtime_ns, other bytes")
os.unlink(cache) if os.path.exists(cache) else None
# S4 corrupt
run(cache)
good = open(cache).read()
def corrupt(label, text):
    open(cache, "w").write(text); cmp("S4 " + label); 
corrupt("truncated at half", good[:len(good) // 2])
corrupt("empty file", "")
corrupt("binary junk", "\x00\xff" * 50)
g = json.loads(good); k = next(iter(g["files"])); e = g["files"][k]
def entry(label, ne):
    g2 = json.loads(good); g2["files"][k] = ne; corrupt(label, json.dumps(g2))
entry("entry msgs=5, right stamp", e[:2] + [5, None, None])
entry("entry msgs=[[1]], right stamp", e[:2] + [[[1]], None, None])
entry("entry msg not dict", e[:2] + [[["m1", 7]], None, None])
entry("entry msg lacks keys", e[:2] + [[["m1", {}]], None, None])
entry("entry usage null", e[:2] + [[["m1", {"model": "x", "usage": None, "ts": None, "sid": "s1", "final": True}]], None, None])
# S5 concurrent cold
procs = []
for _ in range(8):
    if os.path.exists(cache): os.unlink(cache)
    break
env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, LAB_STATUS_CACHE=cache)
procs = [subprocess.Popen([sys.executable, script, "--spend", "--project", proj], stdout=subprocess.PIPE, env=env) for _ in range(8)]
outs = [p.communicate()[0] for p in procs]
ref = run("off")[1].encode()
print("S5 8 concurrent cold runs: outputs equal to uncached:", sum(o == ref for o in outs), "of 8;", "cache valid JSON:", bool(json.load(open(cache))), "; leftover tmp:", [f for f in os.listdir(scr) if f.endswith(".tmp")])
