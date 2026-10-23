# Joins, per PI session, each worker hand-back the PI received (peer record with handback=True) to its USD cost in the PI context (explorer-w08-d's items tsv, paired in order and checked on characters) and to what the PI did next with the file the hand-back names (Read, or Bash cat/sed/head/tail/grep on that path, before the same sender's next message or within 80 tool calls); inputs: OUTDIR LABEL=PI_JSONL=ITEMS_TSV=REQUESTS_TSV [...]; output: OUTDIR/pi_side.tsv (no text: lengths, USD, flags).
# usage: w08_c2_pi_side.py OUTDIR LABEL=PI_JSONL=ITEMS_TSV=REQUESTS_TSV ...
import json, sys, os, re, csv
SKIP = ('{"type": "api-request', '{"type":"api-request')
PATHRE = re.compile(r"(?:__reports__|__pondus__|__scrupuli__)/[A-Za-z0-9_./@-]*[A-Za-z0-9_]")
READERS = ("cat", "sed", "head", "tail", "nl", "grep", "less", "rg", "awk", "bat", "rtk", "jq", "python3")
out = [["session", "name", "role", "wave", "kind", "order", "hb_chars", "pi_chars", "step", "n_reads", "usd_item", "usd_per_char", "next_request_read_usd", "n_paths", "pi_read", "pi_read_chars", "pi_read_calls", "pi_read_tool"]]
for spec in sys.argv[2:]:
    label, pi, itp, rqp = spec.split("=")
    items = [r for r in csv.DictReader(open(itp), delimiter="\t") if r["cat"].startswith("worker hand-back")]   # every peer message (hand-back or not)
    reqs = {int(r["k"]): r for r in csv.DictReader(open(rqp), delimiter="\t")}
    events, results, tools = [], {}, {}
    n_tool = 0
    for line in open(pi, encoding="utf-8", errors="replace"):
        if line.startswith(SKIP):
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        t = r.get("type")
        if t == "assistant" and isinstance(r.get("message"), dict):
            c = r["message"].get("content")
            for b in c if isinstance(c, list) else []:
                if b.get("type") == "tool_use":
                    seen = tools.setdefault(b["id"], None)
                    if seen is None:
                        n_tool += 1
                        tools[b["id"]] = (b["name"], json.dumps(b.get("input") or {}), n_tool)
                        events.append(("T", b["id"]))
        elif t == "user":
            o = r.get("origin") or {}
            c = (r.get("message") or {}).get("content")
            if isinstance(o, dict) and o.get("kind") == "peer":
                s = c if isinstance(c, str) else "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
                events.append(("P", dict(frm=o.get("from") or o.get("name") or "", hb=bool(o.get("handback")), chars=len(s), text=o.get("handbackReportText") or "", n_tool=n_tool)))
            elif isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        x = b.get("content")
                        results[b.get("tool_use_id")] = len(x) if isinstance(x, str) else sum(len(y.get("text", "")) for y in x or [] if isinstance(y, dict))
    peers = [(i, e[1]) for i, e in enumerate(events) if e[0] == "P"]
    k = 0
    bad = 0
    for pos, (i, p) in enumerate(peers):
        it = items[pos] if pos < len(items) else None   # the items tsv holds every peer message, hand-back or not, in file order
        if not p["hb"]:
            continue
        k += 1
        if it is not None and abs(int(it["chars"]) - p["chars"]) > 2:
            bad += 1
            it = None
        usd = (float(it["usd_write_fresh"]) + float(it["usd_read"]) + float(it["usd_rewrite"])) if it else ""
        step = int(it["step"]) if it else ""
        nxt = reqs.get(step) if it else None
        paths = sorted(set(m.rstrip(".") for m in PATHRE.findall(p["text"])))
        tails = [x for x in paths if re.search(r"\.[a-z]{1,4}$", x)]
        endn = p["n_tool"] + 80
        for j, p2 in peers[pos + 1:]:
            if p2["frm"] == p["frm"]:
                endn = min(endn, p2["n_tool"])
                break
        first, calls, kind = None, 0, ""
        for e in events[i + 1:]:
            if e[0] != "T":
                continue
            nm, inp, nt = tools[e[1]]
            if nt > endn:
                break
            if nm not in ("Read", "Bash") or not any(x in inp for x in tails):
                continue
            if nm == "Bash":
                cmd = json.loads(inp).get("command", "")
                w = re.split(r"\s+", cmd.strip())[0] if cmd.strip() else ""
                if w not in READERS:
                    continue
            calls += 1
            if first is None:
                first, kind = results.get(e[1], 0), nm
        name = p["frm"]
        role = (re.match(r"([a-z]+)-w", name) or [None, "?"])[1]
        wave = (re.search(r"-w(\d+)-", name) or [None, ""])[1]
        out.append([label, name, role, wave, "handback", k, len(p["text"]), p["chars"], step, it["n_reads"] if it else "", "%.5f" % usd if it else "", "%.3e" % (usd / p["chars"]) if it else "",
                    "%.5f" % float(nxt["usd_read"]) if nxt else "", len(tails), int(first is not None), first if first is not None else "", calls, kind])
    print(label, "handbacks", k, "items", len(items), "unpaired (chars differ)", bad)
with open(os.path.join(sys.argv[1], "pi_side.tsv"), "w") as fh:
    fh.write("\n".join("\t".join(str(x) for x in r) for r in out) + "\n")
