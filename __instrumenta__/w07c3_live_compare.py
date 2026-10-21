# w07-c3: x2 live half: compares the hook effects recorded in two headless runs (arm A, arm B) of one scenario: worker start note, budget notes at a threshold, harness.jsonl event sequence, hand-back file, guard log decisions, the guard's tool results for the attack calls, stub.log, user_words.md; inputs: RUN_A_DIR RUN_B_DIR; output: markdown table on stdout, exit 1 on a difference
"""usage: w07c3_live_compare.py RUN_A RUN_B
Numbers that depend on the clock or the model (spend, minutes, ids, dates) are masked as `#` before comparing; every other character must match. Rows: start note (worker transcript, `hook_additional_context` that begins `Budget:`);
graded budget notes (`Spent X of USD Y (Z%); t of T min (W%)` lines in the worker transcript: the sequence of the `which`-independent shape after masking, and the number of notes); harness.jsonl events in order (event, which, mode);
hand-back file lines; guard.log (tool, decision, group per line, in order); the tool_result texts of the main transcript that came from the guard (`permission_guard`); stub.log line count; user_words.md lines."""
import glob, json, os, re, sys

RN = [""]
mask = lambda s: re.sub(r"\d+(\.\d+)?", "#", s.replace(RN[0], "RUN") if RN[0] else s)


def collect(d):
    r = {}
    RN[0] = os.path.basename(d.rstrip("/"))
    tr = glob.glob(d + "/transcripts/agent-*.jsonl")
    texts = []
    for f in tr:
        for l in open(f):
            j = json.loads(l)
            a = j.get("attachment") or {}
            if a.get("type") == "hook_additional_context":
                texts += [t for t in (a.get("content") or []) if isinstance(t, str)]
    r["start note"] = [mask(t) for t in texts if t.startswith("Budget:")]
    notes = []
    for t in texts:
        notes += re.findall(r"Spent [\d.]+ of USD [\d.]+ \(\d+%\); [\d.]+ of [\d.]+ min \(\d+%\)[^\n]*", t)
    r["graded notes (masked)"] = sorted(set(mask(n) for n in notes))
    r["graded notes (count)"] = [str(len(notes))]
    # a note can also arrive as a PostToolBatch hook_success stdout inside tool results; look at the raw transcript text as a fallback
    raw = "".join(open(f).read() for f in tr)
    r["Spent-lines anywhere in worker transcript"] = [str(len(re.findall(r"Spent [\d.]+ of USD", raw)))]
    h = []
    p = d + "/lab/__statera__/harness.jsonl"
    if os.path.exists(p):
        for l in open(p):
            j = json.loads(l)
            h.append("%s which=%s mode=%s" % (j.get("event"), j.get("which"), j.get("mode")))
    r["harness.jsonl events"] = h
    hb = glob.glob(d + "/lab/__statera__/handbacks/*.md")
    # the model writes the message text, so only the lab's own lines and whether the message begins with `done` are compared
    hbl = [l for f in hb for l in open(f).read().splitlines() if not l.startswith("## hand-back")]
    r["hand-back file (lab's own lines; message starts with done; sections)"] = [mask(l) for l in hbl[:7]] + ["message starts with done: %s" % any(l.startswith("done") for l in hbl), "sections: %d" % sum(1 for f in hb for l in open(f) if l.startswith("## "))] if hb else ["(none)"]
    g = []
    if os.path.exists(d + "/guard.log"):
        for l in open(d + "/guard.log"):
            j = json.loads(l)
            w = j.get("what", "")
            if j.get("decision") == "deny" or j.get("tool") != "Bash" or w.split(" ")[0] in ("echo", "claude", "sleep", "until"):   # the model's own extra commands (mkdir, ls) vary by run
                g.append("%s %s %s %s" % (j.get("tool"), j.get("decision"), j.get("group"), mask(w)[:40]))
    r["guard.log (tool decision group what)"] = g
    res = []
    for l in open(d + "/transcripts/main.jsonl"):
        j = json.loads(l)
        m = j.get("message")
        if j.get("type") == "user" and isinstance(m, dict) and isinstance(m.get("content"), list):
            for b in m["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content"); c = c if isinstance(c, str) else json.dumps(c)
                    if "permission_guard" in c or "hook error" in c:
                        res.append(c.replace(RN[0], "RUN")[:160])
    r["guard tool_results in main transcript"] = res
    r["stub.log lines"] = [str(len(open(d + "/stub.log").read().splitlines())) if os.path.exists(d + "/stub.log") else "0"]
    uw = d + "/lab/__statera__/user_words.md"
    r["user_words.md"] = [mask(l) for l in open(uw).read().splitlines() if l.strip()] if os.path.exists(uw) else ["(none)"]
    r["files made by denied calls"] = sorted(os.path.relpath(x, d + "/lab") for x in glob.glob(d + "/lab/probe/**", recursive=True) if os.path.isfile(x)) or ["(none)"]
    return r


a, b = collect(sys.argv[1]), collect(sys.argv[2])
bad = 0
print("| item | A | B | equal |\n|:--|:--|:--|:--|")
for k in a:
    same = a[k] == b[k]
    bad += not same
    f = lambda v: "<br>".join(x.replace("|", "/").replace("\n", " ")[:150] for x in v[:8]) + (" ... (+%d)" % (len(v) - 8) if len(v) > 8 else "") if v else "(empty)"
    print("| %s | %s | %s | %s |" % (k, f(a[k]), f(b[k]), "EQUAL" if same else "DIFF"))
print("\ndifferences: %d" % bad)
sys.exit(1 if bad else 0)
