"""Measures per-call latency of `http` hooks as the platform's debug log shows it: the time from the 'HTTP hook POST to URL' line to the next 'HTTP hook response status' / 'HTTP hook error' / 'timed out' line, and the server's own handling time (server.log t_reply_ns - ts_ns); inputs: w07-c run directories (debug log dbg.log, server.log); output: table per run and path: n, median, p90, max in ms (only the /ok, /ctx, /deny, /block paths: answered at once).
"""
import re, sys, os, json, statistics as st, collections
from datetime import datetime
def T(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() * 1000
rows = collections.defaultdict(list); srv = collections.defaultdict(list)
for d in sys.argv[1:]:
    pend = None
    for l in open(os.path.join(d, "dbg.log")):
        m = re.match(r"(\S+) \[\w+\] Hooks: HTTP hook POST to http://127.0.0.1:\d+(/\w+)", l)
        if m: pend = (T(m.group(1)), m.group(2)); continue
        m = re.match(r"(\S+) \[\w+\] Hooks: HTTP hook response status (\d+)", l)
        if m and pend:
            rows[pend[1]].append(T(m.group(1)) - pend[0]); pend = None
    for l in open(os.path.join(d, "server.log")):
        r = json.loads(l)
        if "t_reply_ns" in r: srv[r["path"]].append((r["t_reply_ns"] - r["ts_ns"]) / 1e6)
print("| path | n (platform POST to response line) | median ms | p90 | max | server handling median ms |\n|:--|--:|--:|--:|--:|--:|")
allx = []
for p in ("/ok", "/ctx", "/deny", "/block", "/blockonce"):
    x = sorted(rows.get(p, []))
    if not x: continue
    allx += x
    print("| %s | %d | %.0f | %.0f | %.0f | %.2f |" % (p, len(x), st.median(x), x[int(.9 * (len(x) - 1))], x[-1], st.median(srv[p])))
allx.sort(); print("| all fast paths | %d | %.0f | %.0f | %.0f | |" % (len(allx), st.median(allx), allx[int(.9 * (len(allx) - 1))], allx[-1]))
