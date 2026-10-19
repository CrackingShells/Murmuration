#!/usr/bin/env python3
"""explorer-w01-b: rebuild SendMessage threads (pair and coordinator messages) from transcripts alone.
Sender side: SendMessage tool_use in the sender's own transcript (main or subagent file).
Receiver side: a user message in the receiver's transcript, 'Another Claude session sent a message ...
<agent-message from="X">body</agent-message>' (peer) or 'The coordinator sent a message while you were
working:\n<body>' (main thread).  Join on (sender, receiver, body).
Usage: python3 -I pair_thread.py MAIN_JSONL SUBAGENT_DIR [more MAIN SUB pairs...]  > threads
"""
import csv, glob, json, os, re, sys

def blocks(d):
    m = d.get("message")
    if isinstance(m, dict):
        c = m.get("content")
        if isinstance(c, list): return c
        if isinstance(c, str): return [{"type": "text", "text": c}]
    return []

def run(main, subdir):
    ids, names = {}, {}
    metas = {}
    for f in glob.glob(subdir + "/agent-*.meta.json"):
        a = os.path.basename(f)[6:-10]
        try: m = json.load(open(f))
        except Exception: continue
        metas[a] = m
        if m.get("name"): names[m["name"]] = a
    files = {"main": main}
    for f in glob.glob(subdir + "/agent-*.jsonl"):
        files[os.path.basename(f)[6:-6]] = f
    sends, recvs = [], []
    seen_ids = set()
    for who, f in files.items():
        for i, line in enumerate(open(f), 1):
            try: d = json.loads(line)
            except Exception: continue
            for b in blocks(d):
                if b.get("type") == "tool_use" and b["name"] == "SendMessage":
                    if b["id"] in seen_ids:
                        continue
                    seen_ids.add(b["id"])
                    inp = b["input"]
                    sends.append(dict(ts=d.get("timestamp"), frm=who, to_raw=inp.get("to"), msg=(inp.get("message") or "").strip(), src=f"{os.path.basename(f)}:{i}"))
                if b.get("type") == "text" and d.get("type") == "user":
                    t = b["text"]
                    for m in re.finditer(r'<agent-message from="([^"]+)">\n?(.*?)\n?</agent-message>', t, re.S):
                        recvs.append(dict(ts=d.get("timestamp"), to=who, frm_raw=m.group(1), msg=m.group(2).strip(), src=f"{os.path.basename(f)}:{i}"))
                    m = re.match(r"The coordinator sent a message while you were working:\n(.*?)\n\nAddress this", t, re.S)
                    if m:
                        recvs.append(dict(ts=d.get("timestamp"), to=who, frm_raw="main", msg=m.group(1).strip(), src=f"{os.path.basename(f)}:{i}"))
    for who, f in files.items():
        for i, line in enumerate(open(f), 1):
            if '"queued_command"' not in line:
                continue
            try: d = json.loads(line)
            except Exception: continue
            a = d.get("attachment", {})
            if a.get("type") == "queued_command" and isinstance(a.get("prompt"), str) and not a["prompt"].startswith("<task-notification"):
                recvs.append(dict(ts=d.get("timestamp"), to=who, frm_raw="?", msg=a["prompt"].strip(), src=f"{os.path.basename(f)}:{i}", form="queued_command"))
    for r in recvs:
        r.setdefault("form", "agent-message/coordinator")
        r["msg"] = r["msg"].replace("<\\", "<")
    for s_ in sends:
        s_["msg"] = s_["msg"].replace("<\\", "<")
    def res(x): return names.get(x, x)
    rows, used = [], set()
    for s in sorted(sends, key=lambda r: r["ts"] or ""):
        to = res(s["to_raw"])
        hit = None
        for k, r in enumerate(recvs):
            if k in used: continue
            if r["to"] == to and (r["frm_raw"] == "?" or res(r["frm_raw"]) == s["frm"]) and r["msg"] == s["msg"]:
                hit = k; break
        if hit is not None: used.add(hit)
        r = recvs[hit] if hit is not None else None
        rows.append(dict(ts_send=s["ts"], frm=s["frm"], frm_name=metas.get(s["frm"], {}).get("name", ""), to=to, to_name=metas.get(to, {}).get("name", ""),
                         chars=len(s["msg"]), delivered=("yes" if r else "NO RECEIPT FOUND"), ts_recv=(r["ts"] if r else ""), form=(r["form"] if r else ""), text=s["msg"][:120].replace("\n", " "),
                         src_send=s["src"], src_recv=(r["src"] if r else "")))
    orphans = [r for k, r in enumerate(recvs) if k not in used]
    return rows, orphans

if __name__ == "__main__":
    a = sys.argv[1:]
    w = csv.writer(sys.stdout)
    first = True
    for main, sub in zip(a[0::2], a[1::2]):
        rows, orphans = run(main, sub)
        if first and rows:
            w.writerow(list(rows[0].keys()) + ["session"]); first = False
        for r in rows: w.writerow(list(r.values()) + [os.path.basename(main)[:8]])
        hb = [o for o in orphans if o["msg"].startswith("[Subagent hand-back]")]
        rest = [o for o in orphans if not o["msg"].startswith("[Subagent hand-back]")]
        sys.stderr.write("%s: sends=%d matched=%d  receipts without a send: hand-backs=%d other=%d\n" % (os.path.basename(main)[:8], len(rows), sum(1 for r in rows if r["delivered"]=="yes"), len(hb), len(rest)))
        for o in rest:
            sys.stderr.write("  ORPHAN: %s\n" % json.dumps(o)[:260])
