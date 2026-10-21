"""For replay dumps (hook_replay_equiv.py --merged --dump DIR) of transcripts that differ, tests whether the old version's extra messages are all repeats on a request count already messaged.

Input: DIR with <transcript>.old.json / .new.json snapshots. Output: one line per differing transcript: how many old messages (note, stop, halt) repeat the request count of the previous message, and whether the log, the answers (script and answer, time ignored) and the hand-backs of the two versions are equal once those repeats are dropped from the old one.
Why (w05-c4): the replay fires one PostToolBatch per tool-result record, so two parallel calls of one request (two records) make the old version message twice for one request; the platform fires one PostToolBatch per batch (w03-c1), and the new version messages once per request.
"""
import glob, json, sys
for f in sorted(glob.glob(sys.argv[1].rstrip("/") + "/*.old.json")):
    o, n = json.load(open(f)), json.load(open(f.replace(".old.json", ".new.json")))
    if o["answers"] == n["answers"] and o["log"] == n["log"]:
        continue
    msgs = [i for i, l in enumerate(o["log"]) if l["event"] in ("note", "stop", "halt")]
    last, drop, log = None, set(), []
    for i, l in enumerate(o["log"]):
        if l["event"] in ("note", "stop", "halt"):
            if l["requests"] == last:
                drop.add(msgs.index(i)); continue
            last = l["requests"]
        log.append(l)
    answers = [a for k, a in enumerate(o["answers"]) if k not in drop]
    print("%s repeats=%d log_equal=%s answers_equal=%s handbacks_equal=%s" % (f.split("/")[-1][:-9], len(drop), log == n["log"], [[a[0], a[2]] for a in answers] == [[a[0], a[2]] for a in n["answers"]], o["handbacks"] == n["handbacks"]))
