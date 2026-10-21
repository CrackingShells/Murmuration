"""Compares the JSON bodies an `http` hook received (server.log.bodies.jsonl) with the stdin of a command hook on the same event (truth.jsonl) in w07-c run directories; inputs: one or more run directories; output: per event, n pairs matched (same event and tool_use_id when the body has one, else nearest timestamp within 3 s; one-to-one; command-hook bodies with no http twin, e.g. dead-server calls, stay unpaired), keys only in http, keys only in command, keys whose values differ (with an example), and the count of pairs that are fully equal.
"""
import json, sys, os, collections
for d in sys.argv[1:]:
    tr = [json.loads(l) for l in open(os.path.join(d, "truth.jsonl"))]
    sv = [json.loads(l) for l in open(os.path.join(d, "server.log.bodies.jsonl"))]
    sv = [s for s in sv if s["body"]]
    print("##", os.path.basename(d), "command-hook bodies", len(tr), "http bodies", len(sv))
    used = set(); stats = collections.defaultdict(lambda: dict(n=0, eq=0, only_http=set(), only_cmd=set(), diff=collections.Counter(), ex={}))
    for t in tr:
        ev = t["body"].get("hook_event_name")
        cands = [(abs(s["ts_ns"] - t["ts_ns"]), i) for i, s in enumerate(sv) if i not in used and s["body"].get("hook_event_name") == ev and abs(s["ts_ns"] - t["ts_ns"]) < 3e9 and (not t["body"].get("tool_use_id") or t["body"]["tool_use_id"] == s["body"].get("tool_use_id"))]
        if not cands: continue
        _, i = min(cands); used.add(i); h = sv[i]["body"]; c = t["body"]; st = stats[ev]; st["n"] += 1
        st["only_http"] |= set(h) - set(c); st["only_cmd"] |= set(c) - set(h)
        bad = [k for k in set(h) & set(c) if h[k] != c[k]]
        for k in bad: st["diff"][k] += 1; st["ex"].setdefault(k, (str(c[k])[:60], str(h[k])[:60]))
        if not bad and set(h) == set(c): st["eq"] += 1
    for ev, st in sorted(stats.items()):
        print("| %s | pairs %d | fully equal %d | only http %s | only command %s | differing %s |" % (ev, st["n"], st["eq"], sorted(st["only_http"]), sorted(st["only_cmd"]), dict(st["diff"])))
        for k, (a, b) in st["ex"].items(): print("    e.g.", k, "cmd=", a, "http=", b)
