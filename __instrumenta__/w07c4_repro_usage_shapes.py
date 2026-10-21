"""Prices synthetic one-message sessions whose usage carries `speed` / `server_tool_use` in many shapes, under two lab_status.py copies run as processes (HOME points at a scratch config dir), from A.py B.py and a scratch folder to one row per shape (expected USD, A, B, exit status) on stdout; own code, imports nothing from the author.

usage: w07c4_repro_usage_shapes.py A.py B.py SCRATCH
Each shape is its own session in a scratch project folder, one assistant message of claude-opus-5-5 with 1,000,000 output tokens (list price USD 20 at USD 20 per million), so a price of 40 is fast mode and +0.01 a web search. Expected values are written down here from the stated rates, not computed by the script under test. Runs `--spend --project PROJ` with LAB_STATUS_CACHE=off, then again with a cache file (cold, warm) for B.
"""
import json, os, re, shutil, subprocess, sys

A, B, S = sys.argv[1:4]
shutil.rmtree(S, ignore_errors=True)
PROJ = os.path.realpath(os.path.join(S, "proj")); os.makedirs(PROJ)
HOME = os.path.join(S, "home")
folder = os.path.join(HOME, ".claude", "projects", re.sub(r"[^A-Za-z0-9]", "-", PROJ)); os.makedirs(folder)
BASE = {"input_tokens": 0, "output_tokens": 1000000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
INF = "__INF__"
SHAPES = [  # name, extra usage fields, expected USD
    ("plain", {}, 20.0),
    ("fast", {"speed": "fast"}, 40.0),
    ("speed standard", {"speed": "standard"}, 20.0),
    ("speed null", {"speed": None}, 20.0),
    ("speed number", {"speed": 1}, 20.0),
    ("speed FAST upper", {"speed": "FAST"}, 20.0),
    ("web 3", {"server_tool_use": {"web_search_requests": 3}}, 20.03),
    ("web key missing", {"server_tool_use": {"web_fetch_requests": 4}}, 20.0),
    ("stu empty dict", {"server_tool_use": {}}, 20.0),
    ("stu null", {"server_tool_use": None}, 20.0),
    ("stu list", {"server_tool_use": [1]}, 20.0),
    ("stu string", {"server_tool_use": "3"}, 20.0),
    ("web null", {"server_tool_use": {"web_search_requests": None}}, 20.0),
    ("web string '2'", {"server_tool_use": {"web_search_requests": "2"}}, 20.02),
    ("web string 'abc'", {"server_tool_use": {"web_search_requests": "abc"}}, 20.0),
    ("web float 1.5", {"server_tool_use": {"web_search_requests": 1.5}}, 20.01),
    ("web negative -4", {"server_tool_use": {"web_search_requests": -4}}, 20.0),
    ("web true", {"server_tool_use": {"web_search_requests": True}}, 20.01),
    ("web list", {"server_tool_use": {"web_search_requests": [1]}}, 20.0),
    ("web Infinity", {"server_tool_use": {"web_search_requests": INF}}, 20.0),
    ("fast + web 2", {"speed": "fast", "server_tool_use": {"web_search_requests": 2}}, 40.02),
]
sessions = []
for i, (name, extra, exp) in enumerate(SHAPES):
    sid = "sess%02d" % i
    usage = dict(BASE, **extra)
    rec = {"type": "assistant", "sessionId": sid, "timestamp": "2026-10-22T10:%02d:00Z" % i, "cwd": PROJ, "requestId": "r%d" % i,
           "message": {"id": "m%d" % i, "model": "claude-opus-5-5", "stop_reason": "end_turn", "usage": usage}}
    text = json.dumps(rec).replace('"%s"' % INF, "Infinity")
    with open(os.path.join(folder, sid + ".jsonl"), "w") as fh:
        fh.write(json.dumps({"type": "user", "sessionId": sid, "cwd": PROJ, "timestamp": "2026-10-22T09:59:00Z"}) + "\n" + text + "\n")


def run(script, cache, only=None):
    """USD of the opus row for the whole project, plus exit status; `only` leaves out the shapes not in it (a crash in one shape hides the rest)."""
    env = dict(os.environ, HOME=HOME, LAB_STATUS_CACHE=cache)
    p = subprocess.run([sys.executable, "-I", script, "--spend", "--project", PROJ], capture_output=True, text=True, env=env)
    row = [l for l in p.stdout.splitlines() if "opus-5-5" in l]
    return p.returncode, (float(row[0].split()[-2]) if row else None), p.stderr.strip().splitlines()[-1:] 


# each shape alone: move the other files away, so that one crash or odd value shows on its own row
files = sorted(os.listdir(folder)); hold = os.path.join(S, "hold"); os.makedirs(hold)
print("%-18s %9s | %-26s | %-34s" % ("shape", "expected", "A (rc, usd)", "B (rc, usd, last stderr line)"))
bad = 0
for i, (name, extra, exp) in enumerate(SHAPES):
    for f in files:
        os.replace(os.path.join(folder, f) if f.startswith("sess%02d" % i) is False else os.path.join(hold, f), os.path.join(hold, f)) if False else None
    for f in os.listdir(folder): os.replace(os.path.join(folder, f), os.path.join(hold, f))
    os.replace(os.path.join(hold, "sess%02d.jsonl" % i), os.path.join(folder, "sess%02d.jsonl" % i))
    a = run(A, "off"); b = run(B, "off")
    cache = os.path.join(S, "c%d.json" % i)
    b1 = run(B, cache); b2 = run(B, cache)
    flag = "" if (b[1] is not None and abs(b[1] - exp) < 0.0051 and b == b1 == b2[:2] + b[2:] or (b[0] == 0 and b[1] is not None and abs(b[1] - exp) < 0.0051 and b[1] == b1[1] == b2[1])) else "   <-- B differs from expected"
    if flag: bad += 1
    print("%-18s %9.2f | rc %s usd %-17s | rc %s usd %-8s warm %-8s %s%s" % (name, exp, a[0], a[1], b[0], b[1], b2[1], b[2] if b[0] else "", flag))
    os.replace(os.path.join(folder, "sess%02d.jsonl" % i), os.path.join(hold, "sess%02d.jsonl" % i))
print("shapes where B does not give the expected figure: %d" % bad)
