# w08-j: lists the recorded lab calls that BOTH guards allow although their text names a trigger word (a regex read from w08j_trigger_words.txt), for hand labelling of false allows; inputs: calls.jsonl (w08j_collect_calls.py), replay_all.jsonl (w08j_replay.py), argv[3] a mode "claude" (Bash naming claude and a flag word) or "other"; output: stdout, one line per call with a window around the first flag word. Usage: python3 -I w08j_list_allowed_triggers.py CALLS REPLAY MODE
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = re.compile(open(HERE + "/w08j_trigger_words.txt").read().strip())
FLAG = re.compile(r"bypass|dangerously|CONFIG_DIR|setting-sources|--bare|safe-mode|disableAllHooks")
CLW = re.compile(r"(?<![\w./-])claude(?![\w./-])")
calls = {}
for l in open(sys.argv[1]):
    c = json.loads(l); calls[c["id"]] = c
rep = {}
for l in open(sys.argv[2]):
    r = json.loads(l); rep[r["id"]] = r
al = [c for i, c in calls.items() if c["stratum"] == "lab" and not rep[i]["py"] and not rep[i]["rs"] and not c["live"] and KEY.search(json.dumps(c["input"]))]
x = [c for c in al if c["tool"] == "Bash" and CLW.search(c["input"]["command"]) and FLAG.search(c["input"]["command"])]
print(len(al), "lab allowed calls naming a trigger word;", collections.Counter(c["tool"] for c in al), len(x), "Bash naming claude and a flag word")
rows = x if sys.argv[3] == "claude" else [c for c in al if c not in x]
for n, c in enumerate(sorted(rows, key=lambda c: c["ts"])):
    t = json.dumps(c["input"]) if c["tool"] != "Bash" else c["input"]["command"]
    t = t.replace("\n", " ⏎ ")
    m = FLAG.search(t) or KEY.search(t)
    print("#%d %s %s %s |%s|| %s" % (n, c["session"], c["ts"][5:16], c["tool"], t[:50], t[max(0, m.start() - 70):m.start() + 70]))
