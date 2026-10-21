#!/usr/bin/env python3
# Computes, from one PI main-thread transcript (.jsonl), the per-request token table (in/cr/cw/out, gap, context size), the per-category share of context-carry cost (each item priced as cache write at entry plus cache read at every later request until context shrinks), repeated file reads and the PI's own writing; writes <outdir>/<label>_requests.tsv, <label>_categories.tsv, <label>_items_top.tsv and prints a summary. Usage: w05b_pi_context_cost.py TRANSCRIPT LABEL OUTDIR
import json, sys, re, os, collections, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
PRICES = {  # USD per Mtok: in, out, cache read, cache write 5m, cache write 1h  [source: scripts/lab_status.py PRICES]
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5, 4.0),
}


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def blocks_len(content):
    if isinstance(content, str):
        return len(content)
    n = 0
    for b in content:
        if b.get("type") == "text":
            n += len(b["text"])
        elif b.get("type") == "tool_result":
            c = b.get("content")
            n += len(c) if isinstance(c, str) else sum(len(x.get("text", "")) for x in (c or []) if isinstance(x, dict))
        elif b.get("type") == "tool_use":
            n += len(json.dumps(b["input"]))
        elif b.get("type") == "thinking":
            n += 0
    return n


PATH_RE = re.compile(r"(?:cat|sed -n '[^']*'|head(?: -n? ?\d+)?|tail(?: -n? ?\d+)?|wc -l|jq [^|]*?)\s+((?:/|__|scripts/|skills/|agents/|hooks/|\.claude)[^\s|;&<>\"']+)")


def bash_class(cmd):
    c = cmd.strip()
    if re.search(r"lab_status|budget\.py|user_words|resume_brief|handback\.py|lab_init", c):
        return "Bash: lab scripts"
    if re.match(r"(git|gh)\b", c) or " git " in c[:60]:
        return "Bash: git"
    if re.match(r"(cat|sed|head|tail|jq)\b", c) and "<<" not in c.split("\n")[0]:
        return "Bash: file view (cat/sed/head/tail)"
    if "<<" in c or re.match(r"(cat|tee|printf|echo)\b.*>", c):
        return "Bash: write via heredoc"
    if re.match(r"(ls|find|wc|stat|du|ps|pgrep|date|pwd|test|\[)\b", c):
        return "Bash: ls/find/wc/ps"
    if re.match(r"(python3?|uv|claude|node)\b", c):
        return "Bash: python/claude run"
    return "Bash: other"


def main(path, label, outdir):
    os.makedirs(outdir, exist_ok=True)
    recs = []
    for l in open(path, errors="replace"):
        try:
            recs.append(json.loads(l))
        except Exception:
            pass
    # requests: group assistant records by message id, in file order
    req_order, reqs = [], {}
    for i, d in enumerate(recs):
        if d.get("type") == "assistant":
            m = d["message"]
            mid = m.get("id")
            if mid not in reqs:
                reqs[mid] = dict(mid=mid, first=i, last=i, ts0=ts(d["timestamp"]), ts1=ts(d["timestamp"]), model=m.get("model"), usage=m.get("usage") or {}, content=[], sid=d.get("sessionId"))
                req_order.append(mid)
            r = reqs[mid]
            r["last"] = i
            r["ts1"] = ts(d["timestamp"])
            u = m.get("usage") or {}
            if (u.get("output_tokens") or 0) >= (r["usage"].get("output_tokens") or 0):
                r["usage"] = u
            r["content"].extend(m["content"])
    # tool_use index
    tool_name, tool_input = {}, {}
    for r in reqs.values():
        for b in r["content"]:
            if b.get("type") == "tool_use":
                tool_name[b["id"]] = b["name"]
                tool_input[b["id"]] = b["input"]
    # items between requests
    items = []  # dict(req_index_of_entry, cat, chars, desc)
    rows = []
    prev_ctx, prev_last, prev_ts = 0, -1, None
    for n, mid in enumerate(req_order):
        r = reqs[mid]
        u = r["usage"]
        cc = u.get("cache_creation") or {}
        cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
        cw = int(u.get("cache_creation_input_tokens") or 0)
        if cw1 + cw5 != cw:
            cw5 = cw - cw1
        inp, cr, out = int(u.get("input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0), int(u.get("output_tokens") or 0)
        think = int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)
        ctx = inp + cr + cw
        # items since previous request
        its = []
        if n > 0:
            pr = reqs[req_order[n - 1]]
            # assistant output of previous request (text+tool_use; thinking is dropped)
            ach = 0
            for b in pr["content"]:
                if b["type"] == "text":
                    ach += len(b["text"])
                elif b["type"] == "tool_use":
                    ach += len(json.dumps(b["input"])) + len(b["name"]) + 40
            its.append(("PI own output (text + tool calls)", ach, "assistant of request %d" % (n - 1)))
        for j in range(prev_last + 1, r["first"]):
            d = recs[j]
            t = d.get("type")
            if t == "user":
                c = d["message"]["content"]
                if isinstance(c, str):
                    ok = (d.get("origin") or {}).get("kind")
                    its.append(({"peer": "peer message (worker report or reply)", "task-notification": "task notification", "human": "human prompt"}.get(ok, "other user text"), len(c), c[:60].replace("\n", " ")))
                    continue
                for b in c:
                    if b.get("type") == "tool_result":
                        nm = tool_name.get(b.get("tool_use_id"), "?")
                        inp_ = tool_input.get(b.get("tool_use_id"), {})
                        cl = nm
                        desc = nm
                        if nm == "Bash":
                            cl = bash_class(inp_.get("command", ""))
                            desc = inp_.get("command", "")[:90].replace("\n", " ")
                        elif nm in ("Read", "Write", "Edit"):
                            desc = inp_.get("file_path", "")
                            cl = "Read (whole file)" if nm == "Read" else nm
                        elif nm == "Agent":
                            cl = "Agent tool result (sync)"
                            desc = str(inp_.get("name") or inp_.get("description"))
                        elif nm == "SendMessage":
                            desc = str(inp_.get("to"))
                        elif nm == "Skill":
                            desc = str(inp_.get("skill"))
                        cx = blocks_len([b])
                        its.append(("tool result: " + cl, cx, desc))
                    elif b.get("type") == "text":
                        tx = b["text"]
                        if tx.startswith("Base directory for this skill"):
                            its.append(("skill body load", len(tx), tx[:80].replace("\n", " ")))
                        elif "Subagent hand-back" in tx[:400]:
                            its.append(("subagent hand-back (queued)", len(tx), tx[:80].replace("\n", " ")))
                        else:
                            ok = (d.get("origin") or {}).get("kind")
                            cat_ = {"peer": "peer message (worker report or reply)", "task-notification": "task notification", "human": "human prompt"}.get(ok, "other user text")
                            its.append((cat_, len(tx), tx[:60].replace("\n", " ")))
            elif t == "attachment":
                a = d["attachment"]
                at = a.get("type")
                if at == "prompt_snapshot":
                    continue
                s = json.dumps(a)
                if at == "queued_command":
                    p = a.get("prompt", "")
                    if "Subagent hand-back" in p[:600]:
                        cat = "subagent hand-back (queued)"
                    elif "task-notification" in p[:200] or "<task" in p[:100]:
                        cat = "task notification"
                    else:
                        cat = "queued human message/other"
                    its.append((cat, len(p), p[:80].replace("\n", " ")))
                elif at in ("hook_success", "hook_additional_context", "hook_non_blocking_error", "hook_blocking_error"):
                    its.append(("hook notices", len(s), at))
                elif at in ("skill_listing", "deferred_tools_delta", "mcp_instructions_delta", "agent_listing_delta", "deferred_tools_record"):
                    its.append(("listing/deltas (skills, tools, mcp)", len(s), at))
                else:
                    its.append(("other attachments (" + str(at) + ")", len(s), str(at)))
        gap = (r["ts0"] - prev_ts) if prev_ts else 0
        kinds = set()
        for j in range(prev_last + 1, r["first"]):
            d = recs[j]
            if d.get("type") == "user":
                k = (d.get("origin") or {}).get("kind")
                c_ = d["message"]["content"]
                if isinstance(c_, list) and c_ and c_[0].get("type") == "tool_result":
                    kinds.add("tool_result")
                elif k:
                    kinds.add(k)
            elif d.get("type") == "attachment" and d["attachment"].get("type") == "queued_command":
                kinds.add((d["attachment"].get("origin") or {}).get("kind") or "queued")
        trig = "first" if n == 0 else ("tool_result" if "tool_result" in kinds else "+".join(sorted(kinds)) or "none")
        rows.append(dict(trig=trig, n=n, sid=r["sid"], t=r["ts0"], model=r["model"], inp=inp, cr=cr, cw1=cw1, cw5=cw5, out=out, think=think, ctx=ctx, delta=ctx - prev_ctx, gap=gap, nitems=len(its), its=its,
                         tools=[b["name"] for b in r["content"] if b["type"] == "tool_use"]))
        prev_ctx, prev_last, prev_ts = ctx, r["last"], r["ts1"]
    # context resets: ctx falls below 60% of previous, or cache read == 0 after request 0 (fresh cache)
    for n, r in enumerate(rows):
        r["reset"] = n > 0 and (r["ctx"] < 0.6 * rows[n - 1]["ctx"])
    def pr(model):
        return PRICES.get(re.sub(r"-\d{8}$", "", model or ""), PRICES["claude-opus-5-5"])
    reset_at = [n for n, r in enumerate(rows) if r["reset"]] + [len(rows)]

    def allocate(weight):
        allocated = []
        for n, r in enumerate(rows):
            its = r["its"]
            if n == 0:
                allocated.append(dict(entry=0, cat="base context at start (system, tools, memory, skills)", tok=r["ctx"], desc="request 0 context", chars=0))
                continue
            if r["reset"]:
                allocated.append(dict(entry=n, cat="context after reset (compaction/restart)", tok=r["ctx"], desc="ctx %d -> %d" % (rows[n - 1]["ctx"], r["ctx"]), chars=0))
                continue
            ws = [weight(cat, ch) for cat, ch, _ in its]
            tot = sum(ws) or 1
            dl = max(r["delta"], 0)
            for (cat, ch, desc), w_ in zip(its, ws):
                allocated.append(dict(entry=n, cat=cat, tok=dl * w_ / tot, desc=desc, chars=ch))
            if not its and dl:
                allocated.append(dict(entry=n, cat="unattributed", tok=dl, desc="no records between requests", chars=0))
        for a in allocated:
            n = a["entry"]
            end = min([x for x in reset_at if x > n] or [len(rows)])
            r = rows[n]
            p = pr(r["model"])
            w = (r["cw1"] * p[4] + r["cw5"] * p[3]) / max(r["cw1"] + r["cw5"], 1) if (r["cw1"] + r["cw5"]) else p[3]
            a["write_usd"] = a["tok"] * w / 1e6
            a["read_usd"] = sum(rows[m]["cr"] and pr(rows[m]["model"])[2] for m in range(n + 1, end)) * a["tok"] / 1e6
            a["nreads"] = end - n - 1
        return allocated

    # calibration: non-negative least squares of delta_ctx on chars per category (requests without reset)
    import numpy as np
    from scipy.optimize import nnls
    cats = sorted({c for r in rows for c, _, _ in r["its"]})
    X, y = [], []
    for n, r in enumerate(rows):
        if n == 0 or r["reset"] or r["delta"] <= 0:
            continue
        v = collections.defaultdict(float)
        for c, ch, _ in r["its"]:
            v[c] += ch
        X.append([v[c] for c in cats]); y.append(r["delta"])
    coef, resid = nnls(np.array(X), np.array(y, dtype=float))
    coefd = dict(zip(cats, coef))
    with open(os.path.join(outdir, label + "_nnls_tokens_per_char.tsv"), "w") as f:
        f.write("category\ttokens_per_char_nnls\ttotal_chars\n")
        for c in cats:
            f.write("%s\t%.3f\t%d\n" % (c, coefd[c], sum(ch for r in rows for cc, ch, _ in r["its"] if cc == c)))
    pred = np.array(X) @ coef
    r2 = 1 - ((np.array(y) - pred) ** 2).sum() / ((np.array(y) - np.mean(y)) ** 2).sum()
    print(" NNLS fit of delta_ctx on chars per category: n=%d requests, R2=%.3f" % (len(y), r2))
    allocated_prop = allocate(lambda cat, ch: ch)
    use_nnls = r2 > 0.8
    print(" attribution weights: %s" % ("NNLS tokens per char (R2 > 0.8)" if use_nnls else "chars proportional (NNLS R2 too low to trust)"))
    allocated = allocate(lambda cat, ch: ch * coefd.get(cat, 0.4) + 1e-9) if use_nnls else allocated_prop
    prop_by = collections.defaultdict(float)
    ptot = sum(a["write_usd"] + a["read_usd"] for a in allocated_prop) or 1
    for a in allocated_prop:
        prop_by[a["cat"]] += (a["write_usd"] + a["read_usd"]) / ptot
    # sanity: sum of attributed vs actual
    act_cr = sum(r["cr"] * pr(r["model"])[2] for r in rows) / 1e6
    act_cw = sum((r["cw1"] * pr(r["model"])[4] + r["cw5"] * pr(r["model"])[3]) for r in rows) / 1e6
    act_in = sum(r["inp"] * pr(r["model"])[0] for r in rows) / 1e6
    act_out = sum(r["out"] * pr(r["model"])[1] for r in rows) / 1e6
    att_cr = sum(a["read_usd"] for a in allocated)
    att_cw = sum(a["write_usd"] for a in allocated)
    # tables
    with open(os.path.join(outdir, label + "_requests.tsv"), "w") as f:
        f.write("n\tsession\tt_iso\tmodel\tinput\tcache_read\tcache_write_1h\tcache_write_5m\toutput\tthinking\tctx\tdelta_ctx\tgap_s\treset\ttrigger\tcost_usd_list\ttools\n")
        for r in rows:
            f.write("\t".join(map(str, [r["n"], r["sid"][:8], datetime.datetime.fromtimestamp(r["t"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"), r["model"], r["inp"], r["cr"], r["cw1"], r["cw5"], r["out"], r["think"], r["ctx"], r["delta"], int(r["gap"]), int(r["reset"]), r["trig"], "%.4f" % ((r["inp"] * pr(r["model"])[0] + r["out"] * pr(r["model"])[1] + r["cr"] * pr(r["model"])[2] + r["cw1"] * pr(r["model"])[4] + r["cw5"] * pr(r["model"])[3]) / 1e6), ",".join(r["tools"])])) + "\n")
    bycat = collections.defaultdict(lambda: dict(tok=0.0, write=0.0, read=0.0, n=0))
    for a in allocated:
        c = bycat[a["cat"]]
        c["tok"] += a["tok"]; c["write"] += a["write_usd"]; c["read"] += a["read_usd"]; c["n"] += 1
    tot = sum(c["write"] + c["read"] for c in bycat.values()) or 1
    with open(os.path.join(outdir, label + "_categories.tsv"), "w") as f:
        f.write("category\titems\ttokens_entered\tcarry_cost_share\tcache_write_share\tcache_read_share\tcarry_cost_share_if_chars_proportional\tshare_of_total_list_price_incl_output\n")
        for k, c in sorted(bycat.items(), key=lambda kv: -(kv[1]["write"] + kv[1]["read"])):
            f.write("%s\t%d\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n" % (k, c["n"], c["tok"], (c["write"] + c["read"]) / tot, c["write"] / tot, c["read"] / tot, prop_by.get(k, 0), (c["write"] + c["read"]) / (act_cr + act_cw + act_in + act_out) + (act_out / (act_cr + act_cw + act_in + act_out) if k.startswith("PI own output") else 0)))
    top = sorted(allocated, key=lambda a: -(a["write_usd"] + a["read_usd"]))[:40]
    with open(os.path.join(outdir, label + "_items_top.tsv"), "w") as f:
        f.write("entry_request\tcategory\ttokens\tlater_requests_carried\tcarry_cost_share\tdesc\n")
        for a in top:
            f.write("%d\t%s\t%d\t%d\t%.4f\t%s\n" % (a["entry"], a["cat"], a["tok"], a["nreads"], (a["write_usd"] + a["read_usd"]) / tot, a["desc"].replace("\t", " ")))
    # file re-reads
    reads = collections.defaultdict(list)
    for mid in req_order:
        for b in reqs[mid]["content"]:
            if b.get("type") != "tool_use":
                continue
            if b["name"] == "Read":
                reads[b["input"].get("file_path")].append(("Read", b["id"]))
            elif b["name"] == "Bash":
                cmd = b["input"].get("command", "")
                for m in PATH_RE.finditer(cmd):
                    reads[m.group(1)].append(("Bash", b["id"]))
    # result lengths by tool id
    res_len = {}
    for d in recs:
        if d.get("type") == "user" and isinstance(d["message"]["content"], list):
            for b in d["message"]["content"]:
                if b.get("type") == "tool_result":
                    res_len[b["tool_use_id"]] = blocks_len([b])
    with open(os.path.join(outdir, label + "_rereads.tsv"), "w") as f:
        f.write("path\ttimes_viewed\ttotal_result_chars\tchars_of_repeats\n")
        rr = []
        for p, v in reads.items():
            ls = [res_len.get(i, 0) for _, i in v]
            rr.append((p, len(v), sum(ls), sum(ls) - ls[0] if ls else 0))
        for p, k, s, rep in sorted(rr, key=lambda x: -x[3]):
            if k > 1:
                f.write("%s\t%d\t%d\t%d\n" % (p, k, s, rep))
    # own writing
    own = collections.Counter(); ownn = collections.Counter()
    for mid in req_order:
        for b in reqs[mid]["content"]:
            if b["type"] == "text":
                own["assistant text"] += len(b["text"]); ownn["assistant text"] += 1
            elif b["type"] == "tool_use":
                nm, inp_ = b["name"], b["input"]
                if nm in ("Write", "Edit"):
                    k = nm + " (" + ("wave note/synthesis/design" if re.search(r"__statera__|__design__|synthesis", inp_.get("file_path", "")) else "other file") + ")"
                    own[k] += len(inp_.get("content", "")) + len(inp_.get("new_string", "")); ownn[k] += 1
                elif nm == "Bash":
                    cmd = inp_.get("command", "")
                    if bash_class(cmd) == "Bash: write via heredoc":
                        own["Bash heredoc write"] += len(cmd); ownn["Bash heredoc write"] += 1
                    else:
                        own["Bash other commands"] += len(cmd); ownn["Bash other commands"] += 1
                elif nm in ("Agent", "SendMessage"):
                    k = nm + " (brief/message)"
                    own[k] += len(json.dumps(inp_)); ownn[k] += 1
                else:
                    own["other tool calls: " + nm] += len(json.dumps(inp_)); ownn["other tool calls: " + nm] += 1
    with open(os.path.join(outdir, label + "_own_writing.tsv"), "w") as f:
        f.write("kind\tcalls\tchars\n")
        for k, v in own.most_common():
            f.write("%s\t%d\t%d\n" % (k, ownn[k], v))
    # spikes of cache creation
    sp = sorted(rows, key=lambda r: -(r["cw1"] + r["cw5"]))[:12]
    with open(os.path.join(outdir, label + "_cw_spikes.tsv"), "w") as f:
        f.write("n\tt_iso\tcache_write\tcache_read\tctx\tgap_s\treset\tfirst_item\n")
        for r in sp:
            f.write("%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n" % (r["n"], datetime.datetime.fromtimestamp(r["t"], datetime.timezone.utc).strftime("%H:%M:%S"), r["cw1"] + r["cw5"], r["cr"], r["ctx"], r["gap"], r["reset"], (r["its"][1][0] + ": " + r["its"][1][2] if len(r["its"]) > 1 else "")))
    # cache misses: a request whose cache read is under half of the previous context (not request 0)
    misses = []
    for n, r in enumerate(rows):
        if n == 0:
            continue
        if r["cr"] < 0.5 * rows[n - 1]["ctx"]:
            p_ = pr(r["model"])
            rew = min(r["cw1"] + r["cw5"], rows[n - 1]["ctx"])
            wprice = p_[4] if r["cw1"] >= r["cw5"] else p_[3]
            misses.append(dict(n=n, t=r["t"], gap=r["gap"], rew=rew, prevctx=rows[n - 1]["ctx"], reset=r["reset"], extra_usd=rew * (wprice - p_[2]) / 1e6, first=(r["its"][1][0] + ": " + r["its"][1][2]) if len(r["its"]) > 1 else ""))
    with open(os.path.join(outdir, label + "_cache_misses.tsv"), "w") as f:
        f.write("n\tt_utc\tgap_s\tprev_ctx\trewritten_tokens\tis_context_reset\tshare_of_all_cache_write_tokens\tfirst_item\n")
        allcw = sum(r["cw1"] + r["cw5"] for r in rows) or 1
        for m in misses:
            f.write("%d\t%s\t%d\t%d\t%d\t%d\t%.3f\t%s\n" % (m["n"], datetime.datetime.fromtimestamp(m["t"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"), m["gap"], m["prevctx"], m["rew"], m["reset"], m["rew"] / allcw, m["first"][:80].replace("\t", " ")))
    mt = sum(m["extra_usd"] for m in misses if not m["reset"]) / T if False else None
    # cost by trigger and whether the request called tools (a request with no tool call ends the PI's turn)
    grp = collections.defaultdict(lambda: [0, 0.0, 0])
    for r in rows:
        k = (r["trig"], "calls tools" if r["tools"] else "text only (turn ends)")
        c_ = (r["inp"] * pr(r["model"])[0] + r["out"] * pr(r["model"])[1] + r["cr"] * pr(r["model"])[2] + r["cw1"] * pr(r["model"])[4] + r["cw5"] * pr(r["model"])[3]) / 1e6
        grp[k][0] += 1; grp[k][1] += c_; grp[k][2] += len(r["tools"])
    tt = sum(v[1] for v in grp.values()) or 1
    with open(os.path.join(outdir, label + "_by_trigger.tsv"), "w") as f:
        f.write("trigger\trequest_kind\trequests\tshare_of_list_price\ttool_calls\n")
        for k, v in sorted(grp.items(), key=lambda kv: -kv[1][1]):
            f.write("%s\t%s\t%d\t%.4f\t%d\n" % (k[0], k[1], v[0], v[1] / tt, v[2]))
    # summary
    print("== %s: %d requests, %d session ids, %d context resets" % (label, len(rows), len({r["sid"] for r in rows}), sum(r["reset"] for r in rows)))
    for mdl in sorted({r["model"] for r in rows}):
        rs = [r for r in rows if r["model"] == mdl]
        print(" %s: req %d  input %d  cache_read %d  cache_write %d  output %d (thinking %d)" % (mdl, len(rs), sum(r["inp"] for r in rs), sum(r["cr"] for r in rs), sum(r["cw1"] + r["cw5"] for r in rs), sum(r["out"] for r in rs), sum(r["think"] for r in rs)))
    T = act_cr + act_cw + act_in + act_out
    print(" list-price shares: cache_read %.3f  cache_write %.3f  input %.4f  output %.3f  (total %.2f USD list; shares only are reported)" % (act_cr / T, act_cw / T, act_in / T, act_out / T, T))
    print(" attribution check: attributed read %.3f of actual read %.3f ; attributed write %.3f of actual write %.3f (ratio read %.3f write %.3f)" % (att_cr, act_cr, att_cw, act_cw, att_cr / max(act_cr, 1e-9), att_cw / max(act_cw, 1e-9)))
    nr = [m for m in misses if not m["reset"]]
    print(" cache misses (cr < half of previous ctx, excl. context resets): %d, rewritten tokens %d = %.3f of all cache-write tokens; extra cost vs reading = %.3f of list-price total" % (len(nr), sum(m["rew"] for m in nr), sum(m["rew"] for m in nr) / max(sum(r["cw1"] + r["cw5"] for r in rows), 1), sum(m["extra_usd"] for m in nr) / T))
    print(" gaps > 300s: %d ; > 3600s: %d ; requests with cache_read==0: %d" % (sum(r["gap"] > 300 for r in rows), sum(r["gap"] > 3600 for r in rows), sum(r["cr"] == 0 for r in rows)))
    # tokens-per-char calibration
    cal = [r["delta"] / max(sum(c for _, c, _ in r["its"]), 1) for r in rows if r["delta"] > 0 and not r["reset"] and r["its"]]
    cal.sort()
    if cal:
        print(" tokens per char of items (delta/chars): median %.3f p10 %.3f p90 %.3f" % (cal[len(cal) // 2], cal[len(cal) // 10], cal[9 * len(cal) // 10]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
