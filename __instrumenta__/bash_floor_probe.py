"""Runs headless `claude -p` (haiku) on six trivial Bash calls under four cells (permission mode auto|bypassPermissions x user hooks on|disabled by --settings disableAllHooks; optional cell auto+allow-Bash+hooks = auto with --allowedTools Bash, chosen by --cells), interleaved over reps, and reports each Bash call's duration from the session transcript.

usage: bash_floor_probe.py WORKDIR(outside any lab) --reps 2 [--out results.jsonl]. Cost: about USD 0.03 per run (haiku, the prompt is one line). Duration = tool_result record timestamp minus tool_use record timestamp, as in tool_time_split.py; also prints the run's total_cost_usd from the JSON output.
Output: one JSON line per run (cell, rep, session, durations list, cost) and a median table. Never run from inside a lab folder: runs below a plugin's folder register it in the user's installed_plugins.json (w01-c14).
"""
import json, os, random, subprocess, sys, statistics as st, datetime as dt, glob
wd = os.path.abspath(sys.argv[1]); reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 2
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
ts = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
PROMPT = "Call the Bash tool six times in a row, one call per turn, each with the command `true`. Write no other text."
cells = {"auto+hooks": ("auto", False), "auto+nohooks": ("auto", True), "bypass+hooks": ("bypassPermissions", False), "bypass+nohooks": ("bypassPermissions", True), "auto+allow-Bash+hooks": ("auto", False)}
only = sys.argv[sys.argv.index("--cells") + 1].split(",") if "--cells" in sys.argv else [c for c in cells if "allow" not in c]
plan = [c for _ in range(reps) for c in random.sample(only, len(only))]
rows = []
for rep, c in enumerate(plan):
    mode, nohooks = cells[c]
    cmd = ["claude", "-p", PROMPT, "--model", "haiku", "--permission-mode", mode, "--output-format", "json", "--max-budget-usd", "0.2"]
    if "allow" in c: cmd += ["--allowedTools", "Bash"]
    if nohooks: cmd += ["--settings", json.dumps({"disableAllHooks": True})]
    r = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=300)
    try: j = json.loads(r.stdout)
    except ValueError: rows.append({"cell": c, "error": (r.stdout + r.stderr)[:200]}); continue
    sid = j.get("session_id"); durs = []
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid)):
        uses, res = {}, {}
        for line in open(f):
            rec = json.loads(line); m = rec.get("message"); t = rec.get("timestamp")
            if not t or not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
            for b in m["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash" and rec["type"] == "assistant": uses.setdefault(b["id"], ts(t))
                elif isinstance(b, dict) and b.get("type") == "tool_result": res.setdefault(b["tool_use_id"], ts(t))
        durs = [round(res[i] - uses[i], 2) for i in uses if i in res]
    rows.append({"cell": c, "rep": rep, "session": sid, "durs": durs, "cost": j.get("total_cost_usd"), "turns": j.get("num_turns"), "duration_ms": j.get("duration_ms")})
    print(rows[-1], flush=True)
if out: open(out, "w").write("".join(json.dumps(x) + "\n" for x in rows))
print("| cell | runs | Bash calls | median s | min s | max s |\n|:--|--:|--:|--:|--:|--:|")
for c in cells:
    d = [x for r in rows if r["cell"] == c for x in r.get("durs", [])]
    if d: print("| %s | %d | %d | %.2f | %.2f | %.2f |" % (c, sum(r["cell"] == c for r in rows), len(d), st.median(d), min(d), max(d)))
