# q1 of w07-c2, offline: over every text user record of the lab's transcripts (default: the w07c2_population list), checks that the branch's decision (record_mark directly, and a replay of the hook-time tail lookup on the file prefix ending at the prompt's first record) keeps the human-origin and sdk-cli prompts and drops the peer, task-notification, scheduled and Desktop-sdk ones; inputs: user_words.py path (argv[1]), optional transcript paths; output: stdout tables (counts per category and decision, errors, disagreements between text rule and origin rule, prompt ids whose records disagree).
import json, sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w07c2_population import population
spec = importlib.util.spec_from_file_location("uw", os.path.abspath(sys.argv[1])); uw = importlib.util.module_from_spec(spec); spec.loader.exec_module(uw)
paths = sys.argv[2:] or population()
def category(d):
    """Ground-truth label from the platform's fields alone (the explorer's table), independent of record_mark's branching."""
    o = d.get("origin"); k = o.get("kind") if isinstance(o, dict) else None
    if k == "human": return "human"
    if k == "peer": return "peer"
    if k == "task-notification": return "task-notification"
    if d.get("turnOrigin") == "scheduled": return "scheduled"
    if d.get("turnOrigin") == "peer": return "peer"  # added after the first run: a peer turn's continuation summary carries no origin object
    if d.get("turnOrigin") == "human": return "human"
    if d.get("promptSource") == "sdk" or d.get("turnOrigin") == "sdk":
        return "sdk-cli" if d.get("entrypoint") == "sdk-cli" else "sdk-desktop"
    return "other"
EXPECT = {"human": True, "sdk-cli": True, "peer": False, "task-notification": False, "scheduled": False, "sdk-desktop": False, "other": None}
def stored(text):
    p = uw.strip_leading(text)
    if not uw.is_genuine(p) or not p.strip() or uw.is_lab_command(p) or uw.is_bare_command(p): return False
    return bool(uw.unwrap_pasted(p).strip())
tab = collections.Counter(); rep = collections.Counter(); errors = []; both = collections.Counter(); conflicts = []; nfiles = nrec = 0
for path in paths:
    try: data = open(path, "rb").read()
    except OSError: continue
    nfiles += 1; pos = 0; first = {}; marks = collections.defaultdict(set)
    for line in data.split(b"\n"):
        end = pos + len(line) + 1; start = pos; pos = end
        if b'"user"' not in line: continue
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list): c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if not isinstance(c, str) or not c.strip(): continue
        nrec += 1
        cat = category(d); direct = uw.record_mark(d)
        tab[(cat, direct, stored(c))] += 1
        if direct != EXPECT[cat]: errors.append((path.split("/")[-1][:8], d.get("timestamp"), cat, direct))
        pid = d.get("promptId")
        if pid: marks[pid].add(direct)
        if pid and pid not in first:
            first[pid] = 1
            prefix = data[:end]  # what the file holds when the hook of this prompt runs, if the record is on disk by then
            verdict = None
            for w in uw.TAIL_BYTES:
                buf = prefix[-w:]; whole = len(prefix) <= w
                verdict, cut = uw.scan_tail(buf, pid, whole)
                if verdict is not None or not cut: break
            rep[(cat, verdict)] += 1
            if verdict != direct: errors.append(("replay", path.split("/")[-1][:8], d.get("timestamp"), cat, direct, verdict))
    for pid, m in marks.items():
        if {True, False} <= m: conflicts.append((path.split("/")[-1][:8], pid[:8]))
print("transcripts %d, text user records %d" % (nfiles, nrec))
print("\n(category from fields, record_mark, text rule stores) -> n")
for k, n in sorted(tab.items(), key=lambda x: -x[1]): print(n, k)
print("\nhook-time replay at each prompt's first record: (category, verdict of tail lookup) -> n")
for k, n in sorted(rep.items(), key=lambda x: -x[1]): print(n, k)
print("\nexpected by rule: human True, sdk-cli True, peer/task-notification/scheduled/sdk-desktop False, other None (text rule decides)")
print("errors (decision differs from expected, or replay differs from direct):", len(errors))
for e in errors[:20]: print("  ", e)
print("prompt ids whose records disagree (True and False both marked):", len(conflicts), conflicts[:10])
drop_new = sum(n for (cat, dm, st), n in tab.items() if st and dm is False)
keep_typed = sum(n for (cat, dm, st), n in tab.items() if cat == "human" and dm is True and st)
print("text rule stores %d records; the origin rule additionally drops %d of them; human-origin records stored by both: %d, human-origin records dropped by the new rule: %d" % (sum(n for (c, d_, st), n in tab.items() if st), drop_new, keep_typed, sum(n for (c, dm, st), n in tab.items() if c == "human" and dm is False)))
