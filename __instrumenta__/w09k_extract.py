# Cuts the six PI main-thread transcripts of waves 1-8 (read only) into tables for the w09k figures: one row per hand-back wake with raw-open flags under two codings of w09d_turns.py (as coded; "lab_status" substring masked) and under the second coder's rule R2 of w09c2v_extract.py, one row per hand-back arrival, one row per PI turn, one row per raw-artifact open; writes <outdir>/{wakes,arrivals,turns,opens,r2}.tsv.
# usage: python3 -I w09k_extract.py <outdir> <label>=<transcript.jsonl> [...]   (the six pairs of __pondus__/w09-c2.md "method"; nothing is written outside <outdir>)
import sys, os, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w09d_turns as W
import w09c2v_extract as R

BANNER = "[harness: subagent output matched"
PEER = "Another Claude session sent a message"
READ_KINDS = ("read-whole", "read-part", "bash-view", "bash-query")
orig_call_info = W.call_info


def masked_call_info(name, inp):
    if name == "Bash" and "lab_status" in (inp.get("command") or ""):
        inp = dict(inp)
        inp["command"] = inp["command"].replace("lab_status", "lab_stat_us")
    return orig_call_info(name, inp)


def role_of(nm):
    m = re.match(r"(explorer|author|reproducer|proof-adversary)-w\d\d", nm or "")
    if not m:
        return "other"
    return "verifier" if m.group(1) in ("reproducer", "proof-adversary") else m.group(1)


def jst(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    pairs = [a.split("=", 1) for a in sys.argv[2:]]
    wakes = {}
    arrivals, turnrows, opens = [], [], []
    for mask in (False, True):
        W.call_info = masked_call_info if mask else orig_call_info
        for label, path in pairs:
            turns = W.parse(label, path)[0]
            W.analyse(turns)
            for tn in turns:
                tg = tn["triggers"][0]
                key = (label, tn["n"])
                if tg["kind"] == "B" and tn["n_steps"] > 0:
                    head = tg.get("head") or ""
                    row = wakes.setdefault(key, dict(label=label, turn=tn["n"], epoch=tg["t"], time_jst=jst(tg["t"]), sender=tg.get("agent") or "",
                                                     role=role_of(tg.get("agent")), peer=int(head.startswith(PEER)), banner=int(BANNER in head),
                                                     hb_chars=tg.get("chars", 0), n_steps=tn["n_steps"], n_calls=tn["n_calls"]))
                    row["raw_masked" if mask else "raw_coded"] = int(tn["raw_here"])
                    row["rawnext_masked" if mask else "rawnext_coded"] = int(tn["raw_next"])
                if mask:
                    continue
                turnrows.append((label, tn["n"], tn["t0"], tn["t1"], "+".join(x["kind"] for x in tn["triggers"]), tn["n_steps"], tn["n_calls"]))
                for x in tn["triggers"]:
                    if x["kind"] == "B":
                        arrivals.append((label, x["t"], role_of(x.get("agent")), x.get("agent") or "", x.get("chars", 0), int(x is tg), int((x.get("head") or "").startswith(PEER))))
            if mask:  # raw opens (masked reading, so compound lab_status commands keep their paths), for the timeline
                for tn in turns:
                    senders = {x.get("agent") for x in tn["triggers"] if x["kind"] in ("B", "N") and x.get("agent")}
                    first = tn["triggers"][0]["kind"]
                    for st in tn["steps"]:
                        for c in st["calls"]:
                            if c["kind"] not in READ_KINDS:
                                continue
                            for p in c["paths"]:
                                cl = W.obj_class(p)
                                if cl in W.RAW or any(s and s in p for s in senders):
                                    opens.append((label, tn["n"], st["t"], c["kind"], cl, os.path.basename(p), first))
                                    break
    W.call_info = orig_call_info
    cols = ["label", "turn", "epoch", "time_jst", "sender", "role", "peer", "banner", "hb_chars", "n_steps", "n_calls", "raw_coded", "raw_masked", "rawnext_coded", "rawnext_masked"]
    with open(os.path.join(out, "wakes.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for k in sorted(wakes, key=lambda k: (k[0], k[1])):
            f.write("\t".join(str(wakes[k][c]) for c in cols) + "\n")
    with open(os.path.join(out, "arrivals.tsv"), "w") as f:
        f.write("label\tepoch\trole\tsender\thb_chars\tleads_turn\tpeer\n")
        for r in arrivals:
            f.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(out, "turns.tsv"), "w") as f:
        f.write("label\tturn\tt0\tt1\ttrig\tn_steps\tn_calls\n")
        for r in turnrows:
            f.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(out, "opens.tsv"), "w") as f:
        f.write("label\tturn\tepoch\tkind\tclass\tbasename\tturn_trigger\n")
        for r in opens:
            f.write("\t".join(str(x) for x in r) + "\n")
    # second coder's rule R2 on its own cut (peer-origin "[Subagent hand-back]" records only)
    n2 = 0
    with open(os.path.join(out, "r2.tsv"), "w") as f:
        f.write("label\tepoch\tsender\trole\tn_asst\topen\topen_strict\n")
        for label, path in pairs:
            for w in R.analyse(label, path):
                R.code(w)
                t = datetime.datetime.fromisoformat(w["ts"].replace("Z", "+00:00")).timestamp()
                f.write("\t".join(str(x) for x in (label, t, w["sender"], "verifier" if w["role"] == "reproducer" else w["role"], w["n_asst"], int(w["open"]), int(w["open_strict"]))) + "\n")
                n2 += 1
    print("wake rows %d, arrivals %d, turns %d, opens %d, r2 rows %d" % (len(wakes), len(arrivals), len(turnrows), len(opens), n2))


if __name__ == "__main__":
    main()
