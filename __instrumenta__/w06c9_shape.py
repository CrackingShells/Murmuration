# w06-c9: metric e3: compares hooks/hooks.json of two plugin trees (events, matchers, rows, types, timeouts: all but each row's command string) and lists the commands that changed; inputs: two plugin roots (main, build); output: SAME SHAPE or the first difference, then the changed commands, on stdout; exit 1 on a difference
import json, sys

a, b = (json.load(open(r + "/hooks/hooks.json"))["hooks"] for r in sys.argv[1:3])


def shape(h):
    return {ev: [dict(matcher=g.get("matcher"), rows=[{k: v for k, v in r.items() if k != "command"} for r in g["hooks"]]) for g in groups] for ev, groups in h.items()}


rows = lambda h: sum(len(g["hooks"]) for groups in h.values() for g in groups)
same = shape(a) == shape(b)
print("SAME SHAPE" if same else "DIFFERENT SHAPE", "- events %d / %d, groups %d / %d, rows %d / %d" % (len(a), len(b), sum(map(len, a.values())), sum(map(len, b.values())), rows(a), rows(b)))
for ev in a:
    for ga, gb in zip(a[ev], b.get(ev, [])):
        for ra, rb in zip(ga["hooks"], gb["hooks"]):
            if ra["command"] != rb["command"]:
                print("%s [%s]:\n  main  %s\n  build %s" % (ev, ga.get("matcher"), ra["command"], rb["command"]))
sys.exit(0 if same else 1)
