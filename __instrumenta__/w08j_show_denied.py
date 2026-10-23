# w08-j: prints the calls a guard denies from the collected-calls JSONL, one per line, with the rule, reason and a window of the command text around the matched words; inputs: calls.jsonl (w08j_collect_calls.py), replay_all.jsonl (w08j_replay.py), a stratum, a rule group; output: stdout (for hand labelling). Usage: python3 -I w08j_show_denied.py CALLS REPLAY STRATUM GROUP [START END]
import json, re, sys
calls = {}
for l in open(sys.argv[1]):
    c = json.loads(l); calls[c["id"]] = c
rep = [json.loads(l) for l in open(sys.argv[2])]
stratum, grp = sys.argv[3], sys.argv[4]
a, b = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (0, 10**9)
KEY = re.compile(r"(?i)bypassPermissions|bypass|dangerously\S*|CLAUDE_CONFIG_DIR|--setting-sources\S*|--bare|--safe-mode|disableAllHooks|managed-settings\S*|settings(?:\.local)?\.json")
sel = sorted([(calls[r["id"]], r) for r in rep if r["py"] == grp and calls[r["id"]]["stratum"] == stratum], key=lambda x: x[0]["ts"])
for n, (c, r) in enumerate(sel):
    if not (a <= n < b): continue
    i = c["input"]
    t = i.get("command") or json.dumps({k: (v if len(str(v)) < 400 else str(v)[:200] + "...") for k, v in i.items()})
    t1 = t.replace("\n", " ⏎ ")
    ms = [m.start() for m in KEY.finditer(t1)][:2]
    w = " || ".join("..." + t1[max(0, s - 70):s + 70] + "..." for s in ms) if len(t1) > 260 else t1
    print("#%d %s %s %s live=%s %s | %s" % (n, c["session"], c["ts"][5:16], c["tool"], c["live"], r["py"], t1[:80] if len(t1) > 260 else ""))
    print("    " + w)
