# Splits one agent's session cost and time by phase: reads its subagent transcript and a phase log (`<epoch seconds> <label>` per line, the moment each phase began), prices each phase's requests with scripts/budget.py's own scan (the lab's list-price table; output tokens as the hook counts them), and prints a markdown table of wall minutes, requests and USD per phase, then the groups given on the command line.
# usage: python3 -I w08_c5_cost_split.py REPO TRANSCRIPT PHASES.log END_EPOCH [GROUP=label1,label2 ...] > table.md   (a phase runs from its stamp to the next stamp; the first phase from the transcript's first record; the last to END_EPOCH)
import datetime, json, os, sys, tempfile
repo, tx, log, end = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
groups = [a.split("=", 1) for a in sys.argv[5:]]
sys.path.insert(0, os.path.join(repo, "scripts"))
import budget
recs = [json.loads(l) for l in open(tx) if l.strip()]
ts = lambda r: datetime.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).timestamp() if r.get("timestamp") else None
first = next(ts(r) for r in recs if ts(r))
stamps = [(first, "start")] + [(float(a), b) for a, b in (l.split(None, 1) for l in open(log).read().splitlines() if l.strip())]
stamps = sorted(set(stamps))
bounds = [(stamps[i][1], stamps[i][0], stamps[i + 1][0] if i + 1 < len(stamps) else end) for i in range(len(stamps))]
brief = [r for r in recs if r.get("type") == "user"][:1]
rows = {}
for label, a, b in bounds:
    part = [r for r in recs if r.get("type") == "assistant" and ts(r) and a <= ts(r) < b]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        for r in brief + part:
            fh.write(json.dumps(r) + "\n")
    got = budget.scan(fh.name)
    os.unlink(fh.name)
    mins, reqs, usd = (b - a) / 60.0, got["requests"], got["usd"]
    old = rows.get(label, (0, 0, 0))
    rows[label] = (old[0] + mins, old[1] + reqs, old[2] + usd)
print("| phase | wall minutes | requests | USD (list price) |\n|:--|--:|--:|--:|")
for k, (m, q, u) in rows.items():
    print("| %s | %.1f | %d | %.3f |" % (k, m, q, u))
print("| total | %.1f | %d | %.3f |" % tuple(sum(v[i] for v in rows.values()) for i in range(3)))
if groups:
    print("\n| group | phases | wall minutes | requests | USD |\n|:--|:--|--:|--:|--:|")
    for name, labels in groups:
        ls = labels.split(",")
        print("| %s | %s | %.1f | %d | %.3f |" % ((name, labels) + tuple(sum(rows[l][i] for l in ls if l in rows) for i in range(3))))
