"""Row-level detector check (answer to reproducer-w02-1 Q2): the `+` of each agent row (label x model) of the shipped
reader against a requestId-grouped, file-by-file rule, over all ended sessions plus combinatorics.
    python3 -I rowcheck.py"""
import collections, glob, importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts", "lab_status.py"))
spec = importlib.util.spec_from_file_location("lab_status", SCRIPT); ls = importlib.util.module_from_spec(spec); spec.loader.exec_module(ls)
WT = os.path.dirname(os.path.dirname(SCRIPT)); COMB = "/Users/hacker/Documents/explore/combinatorics_on_binary"
mains = ls.find_sessions(ls.lab_roots(WT)) + ls.find_sessions(ls.lab_roots(COMB))
# only sessions that have ended, so the open one does not move between the two readings
ended = [p for p in mains if '"cost-state"' in open(p, errors="replace").read()]
sess, copies = ls.load_sessions(ended, [])
mine = collections.Counter()
for s in sess:
    for (label, model), r in s["rows"].items():
        mine[(label, model)] += r["lower"]
ref = collections.Counter()  # per label x model: requests (unique requestId, per file, owner = this file's own) whose last record has no stop_reason
for p in ended:
    sid = os.path.basename(p)[:-6]
    for f in sorted(glob.glob(os.path.join(p[:-6], "subagents", "**", "agent-*.jsonl"), recursive=True)):
        label = ls.agent_label(f); last = {}
        for line in open(f, errors="replace"):
            if '"assistant"' not in line: continue
            try: rec = json.loads(line)
            except ValueError: continue
            m = rec.get("message") if isinstance(rec, dict) else None
            if rec.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("model") != "<synthetic>":
                if rec.get("sessionId") == sid:  # owned by this session, as the shipped reader charges it
                    last[rec.get("requestId") or m.get("id")] = (m.get("model"), bool(m.get("stop_reason")))
        for model, fin in last.values():
            if not fin: ref[(label, model)] += 1
keys = set(mine) | set(ref)
diff = [(k, mine[k], ref[k]) for k in keys if bool(mine[k]) != bool(ref[k])]
cnt = [(k, mine[k], ref[k]) for k in keys if mine[k] != ref[k]]
print("ended sessions %d; rows (agent x model) %d; rows marked + by the shipped reader %d, by requestId rule %d"
      % (len(ended), len(keys), sum(bool(v) for v in mine.values()), sum(bool(v) for v in ref.values())))
print("rows where the mark differs: %d; rows where the count of unfinished requests differs: %d" % (len(diff), len(cnt)))
for k, a, b in cnt[:10]: print("  ", k, "shipped", a, "requestId rule", b)
