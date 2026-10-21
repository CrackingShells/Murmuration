#!/usr/bin/env python3
# Computes, from one PI main-thread transcript (.jsonl) and its subagents folder, the PI's per-request table (time, context, cache read/write 5m/1h, output, list-price USD, what woke it), the per-turn (wake-up) table (trigger, requests, USD, state-changing actions, outcome class), the idle gaps, and each subagent's span and list-price USD; writes <outdir>/<label>_req.tsv, _turns.tsv, _gaps.tsv, _workers.tsv. Usage: w06c_pi_wakeups.py TRANSCRIPT SUBAGENT_DIR LABEL OUTDIR
import json, sys, re, os, datetime, collections, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import lab_status as L  # PRICES and message_usd (list price table of the lab)

WRITE_BASH = re.compile(r"(?<![0-9&>])>>?(?![&>])\s*(?!/dev/null)\S|\bgit (commit|merge|add|mv|rm|checkout -b|branch)\b|\bsed -i\b|\bmkdir\b|\btee\b|\bmv\b|\bcp\b")


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def text_of(c):
    if isinstance(c, str):
        return c
    out = []
    for b in c or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                x = b.get("content")
                out.append(x if isinstance(x, str) else " ".join(y.get("text", "") for y in (x or []) if isinstance(y, dict)))
    return "\n".join(out)


def load_workers(subdir):
    """{agent id: dict(name, type, t0, t1, usd, requests)} from the subagent transcripts (list price)."""
    ws = {}
    for f in sorted(glob.glob(os.path.join(subdir, "agent-*.jsonl"))):
        aid = os.path.basename(f)[6:-6]
        meta = {}
        try:
            meta = json.load(open(f[:-6] + ".meta.json"))
        except Exception:
            pass
        msgs, t0, t1 = {}, None, None
        for l in open(f, errors="replace"):
            if '"timestamp"' not in l:
                continue
            try:
                d = json.loads(l)
            except Exception:
                continue
            t = d.get("timestamp")
            if t:
                t = ts(t)
                t0 = t if t0 is None else min(t0, t)
                t1 = t if t1 is None else max(t1, t)
            if d.get("type") == "assistant":
                m = d["message"]
                mid = m.get("id")
                u = m.get("usage") or {}
                cur = msgs.setdefault(mid, dict(model=m.get("model"), usage={}))
                L.merge_usage(cur["usage"], u)
                for k in ("speed", "server_tool_use"):
                    if u.get(k):
                        cur["usage"][k] = u[k]
        usd = 0.0
        for m in msgs.values():
            v = L.message_usd(m["model"] or "", m["usage"])
            usd += v or 0.0
        ws[aid] = dict(id=aid, name=meta.get("name") or meta.get("description") or aid, type=meta.get("agentType", ""), t0=t0, t1=t1, usd=usd, requests=len(msgs))
    return ws


def main(path, subdir, label, outdir):
    os.makedirs(outdir, exist_ok=True)
    recs = []
    for l in open(path, errors="replace"):
        try:
            recs.append(json.loads(l))
        except Exception:
            pass
    workers = load_workers(subdir) if os.path.isdir(subdir) else {}
    wname = {k: v["name"] for k, v in workers.items()}
    # requests
    order, reqs = [], {}
    for i, d in enumerate(recs):
        if d.get("type") == "assistant":
            m = d["message"]
            mid = m.get("id")
            if mid not in reqs:
                reqs[mid] = dict(first=i, last=i, t0=ts(d["timestamp"]), t1=ts(d["timestamp"]), model=m.get("model"), usage={}, content=[])
                order.append(mid)
            r = reqs[mid]
            r["last"] = i
            r["t1"] = ts(d["timestamp"])
            L.merge_usage(r["usage"], m.get("usage") or {})
            u = m.get("usage") or {}
            for k in ("speed", "server_tool_use"):
                if u.get(k):
                    r["usage"][k] = u[k]
            r["content"].extend(m["content"])
    tool_name = {}
    for r in reqs.values():
        for b in r["content"]:
            if b.get("type") == "tool_use":
                tool_name[b["id"]] = b["name"]
    rows = []
    prev_last, prev_t1, prev_ctx = -1, None, 0
    for n, mid in enumerate(order):
        r = reqs[mid]
        u = r["usage"]
        cc = u.get("cache_creation") if isinstance(u.get("cache_creation"), dict) else {}
        cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
        cw = int(u.get("cache_creation_input_tokens") or 0)
        cw5 += max(0, cw - cw1 - cw5)
        inp, cr, out = int(u.get("input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0), int(u.get("output_tokens") or 0)
        ctx = inp + cr + cw1 + cw5
        usd = L.message_usd(r["model"] or "", u) or 0.0
        # what arrived since the previous request
        trig, msgs = set(), []
        for j in range(prev_last + 1, r["first"]):
            d = recs[j]
            if d.get("type") == "user":
                c = d["message"]["content"]
                k = (d.get("origin") or {}).get("kind")
                if isinstance(c, list) and c and isinstance(c[0], dict) and c[0].get("type") == "tool_result":
                    for b in c:
                        if b.get("type") == "tool_result":
                            trig.add("tool_result:" + tool_name.get(b.get("tool_use_id"), "?"))
                elif k:
                    tx = text_of(c)
                    trig.add(k)
                    msgs.append((k, tx))
            elif d.get("type") == "attachment" and d["attachment"].get("type") == "queued_command":
                a = d["attachment"]
                k = (a.get("origin") or {}).get("kind") or "queued"
                trig.add(k + "(queued)")
                msgs.append((k + "(queued)", a.get("prompt", "")))
        senders = []
        for k, tx in msgs:
            if k.startswith("peer"):
                m = re.search(r'from="([^"]+)"', tx)
                kind = "hand-back" if "Subagent hand-back" in tx[:600] else "reply"
                senders.append("%s:%s" % (m.group(1) if m else "?", kind))
            elif k.startswith("task-notification"):
                m = re.search(r"<task-id>([^<]+)</task-id>", tx)
                st = re.search(r"<status>([^<]+)</status>", tx)
                senders.append("done:%s%s" % (wname.get(m.group(1), m.group(1)) if m else "?", "(" + st.group(1) + ")" if st else ""))
            elif k.startswith("human"):
                senders.append("human")
        # actions of this request
        acts = collections.Counter()
        detail = []
        textlen = 0
        for b in r["content"]:
            if b.get("type") == "text":
                textlen += len(b["text"])
            if b.get("type") != "tool_use":
                continue
            nm, inp_ = b["name"], b.get("input") or {}
            if nm == "Agent":
                acts["Agent"] += 1
                detail.append("Agent:" + str(inp_.get("name") or inp_.get("subagent_type")))
            elif nm == "SendMessage":
                acts["SendMessage"] += 1
                detail.append("SendMessage:" + str(inp_.get("to")))
            elif nm in ("Write", "Edit", "NotebookEdit"):
                acts["Write"] += 1
                detail.append(nm + ":" + os.path.basename(str(inp_.get("file_path"))))
            elif nm == "Bash":
                cmd = inp_.get("command", "")
                if WRITE_BASH.search(cmd):
                    acts["BashWrite"] += 1
                    detail.append("BashWrite:" + cmd[:60].replace("\n", " ").replace("\t", " "))
                else:
                    acts["BashRead"] += 1
            else:
                acts["Other:" + nm] += 1
        rows.append(dict(n=n, t0=r["t0"], t1=r["t1"], ts_prev_end=prev_t1, gap=(r["t0"] - prev_t1) if prev_t1 else 0, model=r["model"], inp=inp, cr=cr, cw1=cw1, cw5=cw5, out=out,
                         ctx=ctx, delta=ctx - prev_ctx, usd=usd, trig=sorted(trig), senders=senders, acts=acts, detail=detail, textlen=textlen,
                         has_tool=any(b.get("type") == "tool_use" for b in r["content"]), stop=None))
        prev_last, prev_t1, prev_ctx = r["last"], r["t1"], ctx
    # tool-run time: the PI is "in a turn" from first request of a turn to its last request end
    # turns: a turn starts at request 0 or at a request whose trigger has no tool_result
    turns = []
    for r in rows:
        woke = r["n"] == 0 or not any(t.startswith("tool_result") for t in r["trig"])
        if woke:
            turns.append(dict(reqs=[r]))
        else:
            turns[-1]["reqs"].append(r)
    with open(os.path.join(outdir, label + "_req.tsv"), "w") as f:
        f.write("n\tt_utc\tgap_s\tctx\tcache_read\tcache_write_1h\tcache_write_5m\toutput\tusd_list\ttrigger\tsenders\tactions\n")
        for r in rows:
            f.write("\t".join(map(str, [r["n"], iso(r["t0"]), "%.0f" % r["gap"], r["ctx"], r["cr"], r["cw1"], r["cw5"], r["out"], "%.4f" % r["usd"], "+".join(r["trig"]) or "first", ",".join(r["senders"]), ",".join("%s=%d" % kv for kv in sorted(r["acts"].items()))])) + "\n")
    # outcome of a turn
    with open(os.path.join(outdir, label + "_turns.tsv"), "w") as f:
        f.write("turn\tt_start_utc\tidle_before_s\tturn_s\tn_req\tctx_start\tusd_list\ttrigger\tsenders\tcls\tn_agent\tn_sendmsg\tn_write\tn_bashwrite\tn_bashread\tfinal_text_chars\tdetail\n")
        for k, t in enumerate(turns):
            rs = t["reqs"]
            acts = collections.Counter()
            det = []
            for r in rs:
                acts.update(r["acts"])
                det += r["detail"]
            if acts["Agent"]:
                cls = "dispatch"
            elif acts["SendMessage"]:
                cls = "message"
            elif acts["Write"] or acts["BashWrite"]:
                cls = "file-or-commit"
            elif sum(v for kk, v in acts.items() if kk != "Agent") > 0:
                cls = "read-only"
            else:
                cls = "text-only"
            first = rs[0]
            trig = first["trig"][0] if first["trig"] else "first"
            idle = first["gap"]
            turn_s = rs[-1]["t1"] - first["t0"]
            f.write("\t".join(map(str, [k, iso(first["t0"]), "%.0f" % idle, "%.0f" % turn_s, len(rs), first["ctx"], "%.4f" % sum(r["usd"] for r in rs), "+".join(first["trig"]) or "first",
                                        ",".join(first["senders"]), cls, acts["Agent"], acts["SendMessage"], acts["Write"], acts["BashWrite"], acts["BashRead"], rs[-1]["textlen"], "|".join(det)[:400]])) + "\n")
    with open(os.path.join(outdir, label + "_gaps.tsv"), "w") as f:
        f.write("t_utc\tgap_s\tprev_ctx\tcache_read\tcache_write_1h\tcache_write_5m\tctx\n")
        for r in rows:
            if r["gap"] > 300:
                f.write("\t".join(map(str, [iso(r["t0"]), "%.0f" % r["gap"], r["ctx"] - r["delta"], r["cr"], r["cw1"], r["cw5"], r["ctx"]])) + "\n")
    with open(os.path.join(outdir, label + "_workers.tsv"), "w") as f:
        f.write("name\ttype\tt0_utc\tt1_utc\tspan_s\trequests\tusd_list\n")
        for w in sorted(workers.values(), key=lambda w: w["t0"] or 0):
            f.write("\t".join(map(str, [w["name"], w["type"], iso(w["t0"]), iso(w["t1"]), "%.0f" % (w["t1"] - w["t0"]), w["requests"], "%.4f" % w["usd"]])) + "\n")
    print("requests", len(rows), "turns", len(turns), "workers", len(workers), "PI usd %.2f" % sum(r["usd"] for r in rows), "workers usd %.2f" % sum(w["usd"] for w in workers.values()))


if __name__ == "__main__":
    main(*sys.argv[1:5])
