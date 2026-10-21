"""Measures, per transcript, the wall time of Bash tool calls that start a headless `claude -p` run (tool_use timestamp to its tool_result timestamp) against the transcript's own first-to-last timestamp, from a file list to a table of the biggest agents and a total on stdout.

usage: w07d_headless_cells.py FILES.txt [top N]
A call counts when its command contains `claude -p` or `claude --print`, or runs one of the lab's *_full.sh / w06c*_run*.py drivers. Calls whose command carries `&`, `xargs -P`, `parallel` or a `_full.sh` name are marked `par` (they fan out inside one call); the rest are `ser`. Read-only on transcripts.
"""
import sys, json, re, datetime, collections
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
HEAD = re.compile(r"claude\s+(-p|--print)\b|_full\.sh|w06c\d+_(?:run|e3)\w*\.py|w06c3_run_all")
FAN = re.compile(r"(?<![&>])&(?![&>])\s*(?:$|\n|;)|xargs\s+-P|parallel|_full\.sh|wait\b")
files = [l for l in open(sys.argv[1]).read().split("\n") if l]
rows = []; tot = collections.Counter()
for f in files:
    if "subagents" not in f and False: continue
    first = last = None; calls = {}; res = {}
    with open(f, "rb") as fh:
        for line in fh:
            if b'"timestamp"' not in line: continue
            if b'"tool_use"' not in line and b'"tool_result"' not in line:
                # still counts for first/last
                m = re.search(rb'"timestamp":"([^"]+)"', line)
                if m:
                    t = ts(m.group(1).decode()); first = t if first is None else min(first, t); last = t if last is None else max(last, t)
                continue
            try: r = json.loads(line)
            except ValueError: continue
            t = ts(r["timestamp"]) if r.get("timestamp") else None
            if t: first = t if first is None else min(first, t); last = t if last is None else max(last, t)
            c = (r.get("message") or {}).get("content")
            if not isinstance(c, list): continue
            for b in c:
                if not isinstance(b, dict): continue
                if b.get("type") == "tool_use" and b.get("name") == "Bash":
                    cmd = (b.get("input") or {}).get("command") or ""
                    if HEAD.search(cmd): calls.setdefault(b["id"], (t, cmd))
                elif b.get("type") == "tool_result" and t:
                    res.setdefault(b.get("tool_use_id"), t)
    if not calls or first is None: continue
    ser = par = 0.0; n_ser = n_par = 0
    for i, (t0, cmd) in calls.items():
        if i in res and t0:
            d = res[i] - t0
            if FAN.search(cmd): par += d; n_par += 1
            else: ser += d; n_ser += 1
    rows.append((ser + par, last - first, ser, par, n_ser, n_par, f.split("/")[-1][:24]))
    tot["wall"] += last - first; tot["ser"] += ser; tot["par"] += par; tot["n_ser"] += n_ser; tot["n_par"] += n_par; tot["files"] += 1
rows.sort(reverse=True)
print("files with headless calls: %d; their summed own wall %.0f s; time inside ser calls %.0f s (%d calls), inside par calls %.0f s (%d calls)" % (tot["files"], tot["wall"], tot["ser"], tot["n_ser"], tot["par"], tot["n_par"]))
print("agent file                 own wall s   headless-call s   ser s (n)      par s (n)")
for tt, w, s, p, ns, np_, name in rows[: int(sys.argv[2]) if len(sys.argv) > 2 else 12]:
    print("%-26s %8.0f   %8.0f          %6.0f (%d)   %6.0f (%d)" % (name, w, tt, s, ns, p, np_))
