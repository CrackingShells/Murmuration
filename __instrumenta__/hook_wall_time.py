"""Median wall time of hook scripts run as subprocesses, before and after a change: from script paths, an event JSON file, a count and a CLAUDE_PROJECT_DIR, to median/min/max milliseconds per script and the median of the paired differences on stdout.

usage: hook_wall_time.py <event.json> <n> <CLAUDE_PROJECT_DIR> <script_before.py> [<script_after.py>]. Runs `python3 <script>` with stdin = the event file,
stdout discarded, one warm-up each, then n rounds in which the scripts run in turn (so machine load hits both alike). For user_words.py the prompt is appended
to the lab at CLAUDE_PROJECT_DIR or the event's cwd, so point it at a scratch lab.
"""
import os, statistics, subprocess, sys, time

event, n, pd = sys.argv[1], int(sys.argv[2]), sys.argv[3]
scripts = sys.argv[4:]
env = dict(os.environ, CLAUDE_PROJECT_DIR=pd)
data = open(event, "rb").read()
run = lambda s: subprocess.run(["python3", s], input=data, stdout=subprocess.DEVNULL, env=env, check=False)
for s in scripts:
    run(s)
ts = {s: [] for s in scripts}
for _ in range(n):
    for s in scripts:
        t = time.perf_counter(); run(s); ts[s].append((time.perf_counter() - t) * 1000)
for s in scripts:
    print("median %.1f ms  min %.1f  max %.1f  (n=%d) %s" % (statistics.median(ts[s]), min(ts[s]), max(ts[s]), n, s))
if len(scripts) == 2:
    d = [b - a for a, b in zip(*ts.values())]
    print("paired difference (second minus first): median %+.1f ms, mean %+.1f ms" % (statistics.median(d), statistics.mean(d)))
