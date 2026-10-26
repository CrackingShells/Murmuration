# Cuts PI main-thread transcripts (.jsonl) into turns (a trigger and what the PI does until the next trigger), codes reads and hand-back reactions by rule, scans for results stated before a worker returned; reads <label>=<transcript> pairs, writes <outdir>/<label>_turns.jsonl (one turn per line, summaries with short PI text), <outdir>/turn_table.tsv (one row per turn), <outdir>/read_table.tsv (one row per read), <outdir>/fabrication_scan.tsv (flags).
# usage: python3 -I w09d_turns.py <outdir> <label>=<transcript.jsonl> [...]
# Rules are those of __reports__/wave-09/explorer-w09-d/01-coding_scheme.md; the "use" of a read is a string proxy (file name appears in a later PI write, dispatch or text), not a reading of intent.
import json, sys, os, re, datetime

SKIP = ('{"type":"api-request', '{"type": "api-request')
NAME_RE = re.compile(r"\b(explorer|author|reproducer|proof-adversary)-w\d\d-[a-z0-9]+\b")
LOOSE_RE = re.compile(r"\b(?:(explorer|author|reproducer|proof-adversary)[- ])?(w\d\d-[a-z0-9]{1,2})\b", re.I)
HEX_RE = re.compile(r"(?<![0-9A-Za-z_/.-])[0-9a-f]{7,40}(?![0-9A-Za-z_-])")
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
FRAME_END = "The report follows:"


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def hhmm(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=9))).strftime("%d %H:%M:%S")


def text_of(c):
    if isinstance(c, str):
        return c
    out = []
    for b in c or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                out.append(text_of(b.get("content")))
    return "\n".join(out)


def unesc(s):
    return s.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ").replace('\\"', " ")


def one(s, n):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n] + "~"


PATH_RE = re.compile(r"(?:(?:/Users/[^\s'\"`;|&<>)]+)|(?:[\w.\-]+/)+[\w.\-]+|\b[\w\-]+\.(?:md|py|json|jsonl|tsv|csv|txt|rs|sh|toml|yaml|yml)\b)")


def paths_of_cmd(cmd):
    out = []
    for m in PATH_RE.findall(cmd or ""):
        m = m.rstrip(",.:")
        if len(m) > 4 and not m.startswith(("http", "-")):
            out.append(m)
    return out


def obj_class(p):
    q = p or ""
    if "__statera__/synthesis" in q:
        return "synthesis"
    if re.search(r"__statera__/wave-\d", q):
        return "wave note"
    if "__statera__/" in q:
        return "statera other"
    if "framing.md" in q:
        return "framing"
    if "/skills/" in q or q.startswith("skills/") or "SKILL.md" in q:
        return "skill/reference"
    if re.search(r"(^|/)agents/[\w\-]+\.md", q):
        return "agent file"
    m = re.search(r"__reports__/wave-\d\d/([\w\-]+)/", q)
    if m:
        return "PI report" if m.group(1) == "research-pi" else "worker report"
    if "__reports__/" in q:
        return "report (older/other)"
    if "__scrupuli__" in q:
        return "puzzle file"
    if "__pondus__" in q:
        return "claim file"
    if "__instrumenta__" in q:
        return "instrumenta script"
    if re.search(r"(^|/)(scripts|hooks)/", q) or q.endswith((".rs",)) and "/src/" in q:
        return "plugin source"
    if q.endswith(".jsonl") or "/private/tmp" in q or "/.claude/projects/" in q or "tool-results" in q:
        return "transcript/data"
    if q.endswith((".tsv", ".csv", ".json")):
        return "transcript/data"
    if q.endswith((".py", ".sh")):
        return "code other"
    if q.endswith(".md"):
        return "other md"
    return "other"


RAW = {"worker report", "puzzle file", "claim file", "instrumenta script", "transcript/data", "report (older/other)", "PI report"}


def call_info(name, inp):
    """-> dict(kind, paths, key) ; kind in read-whole, read-part, bash-view, bash-query, lab_status, search, git, tool-search, write, dispatch, message, bash-other, other"""
    if name == "Read":
        p = inp.get("file_path", "")
        part = ("offset" in inp) or ("limit" in inp)
        return {"kind": "read-part" if part else "read-whole", "paths": [p], "key": p + ((" off=%s lim=%s" % (inp.get("offset"), inp.get("limit"))) if part else "")}
    if name == "Bash":
        c = (inp.get("command") or "").strip()
        c1 = re.sub(r"^(cd\s+\S+\s*(&&|;)\s*)+", "", c)
        head = c1.split("|")[0]
        ps = paths_of_cmd(c1)
        w0 = (re.split(r"\s+", head.strip()) or [""])[0]
        c2 = re.sub(r"\d?>\s*/dev/null|\d?>&\d|&>\s*/dev/null", "", c1)
        wr = bool(re.search(r"(>>?\s*[\w./~\-$\"']+|\bcat\s*>|\btee\b|\bsed\s+-i|\bgit\s+(add|commit|merge|mv|rm|checkout|worktree)|\bmkdir\b|\bcp\b|\bmv\b|\brm\b|open\([^)]*['\"][wa]['\"]|write_text)", c2))
        vw = bool(re.search(r"(^|[;&|(]\s*|\s)(cat|head|tail|nl)\s+(-\w+\s+)*[^|;&<>\s]*[/.][^|;&\s]*|\bsed\s+-n\b|\bjq\b[^|]*\s[\w./~\-]+\.json|\bgrep\b[^|]*\s[\w./~\-]+\.(md|py|json|jsonl|tsv|txt)", c2))
        if "lab_status" in c1 and not wr:
            return {"kind": "lab_status", "paths": [], "key": one(c1, 120)}
        if wr:
            return {"kind": "write", "paths": ps, "key": one(c1, 160), "cmd": c1, "reads_too": vw}
        if vw:
            return {"kind": "bash-view", "paths": ps, "key": one(c1, 140)}
        if re.match(r"git\s", c1):
            return {"kind": "git", "paths": ps, "key": one(c1, 120)}
        if w0 in ("cat", "sed", "head", "tail", "nl", "less", "bat"):
            return {"kind": "bash-view", "paths": ps, "key": one(c1, 140)}
        if w0 in ("jq", "grep", "rg", "awk", "ls", "wc", "find", "stat", "python3", "python", "diff", "comm", "sort", "uv", "ps", "date", "du"):
            return {"kind": "bash-query" if ps else "bash-other", "paths": ps, "key": one(c1, 140)}
        return {"kind": "bash-other", "paths": ps, "key": one(c1, 140)}
    if name in ("Write", "Edit", "NotebookEdit"):
        p = inp.get("file_path", "")
        return {"kind": "write", "paths": [p], "key": p, "cmd": json.dumps(inp)}
    if name in ("Agent", "Task"):
        return {"kind": "dispatch", "paths": [], "key": one(inp.get("description", ""), 80)}
    if name == "SendMessage":
        return {"kind": "message", "paths": [], "key": "to=%s" % inp.get("to")}
    if name == "ToolSearch":
        return {"kind": "tool-search", "paths": [], "key": one(inp.get("query", ""), 60)}
    if name in ("Glob", "Grep") or name.startswith("mcp__plugin_colgrep"):
        return {"kind": "search", "paths": [], "key": one(json.dumps(inp), 100)}
    return {"kind": "other", "paths": [], "key": name}


def parse(label, path):
    steps = {}          # mid -> step dict
    order = []
    turns = []
    cur = None
    toolinfo = {}       # tool_use id -> (step, call)
    agent_name = {}     # agent id -> name
    pending_dispatch = {}   # tool_use id -> name
    carrier = set()     # 7-char prefixes of hex tokens seen outside PI-authored content (a short hash matches a longer one)
    carrier_ctx = {}
    open_since = {}     # agent name -> time of open
    fab = []
    d1_checked = [0]
    returned_ids = set()
    think_nonempty = 0
    think_blocks = 0
    nlines = 0

    def new_turn(kind, t, info):
        nonlocal cur
        idle = True
        if cur is not None and cur["steps"]:
            last = cur["steps"][-1]
            idle = last.get("stop") == "end_turn"
        elif cur is not None and cur["triggers"]:
            idle = False if cur["steps"] == [] and (t - cur["t0"]) < 2 else True
        if cur is not None and not idle and kind != "H":
            cur["triggers"].append(dict(kind=kind, t=t, idle=False, **info))
            return cur
        cur = {"label": label, "n": len(turns), "t0": t, "triggers": [dict(kind=kind, t=t, idle=idle, **info)], "steps": [], "t1": t}
        turns.append(cur)
        return cur

    def agent_of(task_id):
        return agent_name.get(task_id) or task_id

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            nlines += 1
            if line.startswith(SKIP):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t = r.get("type")
            tt = ts(r["timestamp"]) if r.get("timestamp") else None
            if t == "assistant" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("model") == "<synthetic>":
                    continue
                mid = m.get("id")
                if cur is None:
                    new_turn("S", tt, {"info": "start"})
                st = steps.get(mid)
                if st is None:
                    st = steps[mid] = {"mid": mid, "t": tt, "text": [], "think": [], "calls": [], "stop": None, "gap": None}
                    cur["steps"].append(st)
                    order.append(mid)
                st["stop"] = m.get("stop_reason") or st["stop"]
                cur["t1"] = tt
                authored = []
                for b in m.get("content") or []:
                    bt = b.get("type")
                    if bt == "text":
                        st["text"].append(b.get("text") or "")
                        authored.append(b.get("text") or "")
                    elif bt == "thinking":
                        think_blocks += 1
                        th = b.get("thinking") or ""
                        if th.strip():
                            think_nonempty += 1
                            st["think"].append(th)
                            authored.append(th)
                    elif bt == "tool_use":
                        inp = b.get("input") or {}
                        ci = call_info(b["name"], inp)
                        ci.update({"name": b["name"], "id": b["id"], "res_chars": None, "err": False})
                        st["calls"].append(ci)
                        toolinfo[b["id"]] = (st, ci)
                        authored.append(json.dumps(inp))
                        if b["name"] in ("Agent", "Task"):
                            mm = re.search(r"Your name is ([a-z0-9\-]+)", inp.get("prompt", "")) or NAME_RE.search(inp.get("description", ""))
                            nm = mm.group(1) if mm and mm.lastindex else (mm.group(0) if mm else inp.get("description", "")[:30])
                            pending_dispatch[b["id"]] = nm
                            ci["agent_name"] = nm
                            open_since[nm] = tt
                        if b["name"] == "SendMessage":
                            to = str(inp.get("to"))
                            nm = agent_name.get(to, to)
                            ci["agent_name"] = nm
                            open_since[nm] = tt
                # fabrication scan on PI-authored content
                atxt = "\n".join(authored)
                for h in set(HEX_RE.findall(unesc(UUID_RE.sub("", atxt)))):
                    if re.search(r"\d", h) and re.search(r"[a-f]", h):
                        d1_checked[0] += 1
                    if re.search(r"\d", h) and re.search(r"[a-f]", h) and h[:7] not in carrier:
                        i = atxt.find(h)
                        fab.append({"label": label, "turn": cur["n"], "t": tt, "detector": "D1 hex token with no earlier carrier", "token": h, "ctx": one(atxt[max(0, i - 90):i + 90], 190)})
                        carrier.add(h[:7])   # report a token once
                vis = "\n".join(b.get("text") or "" for b in m.get("content") or [] if b.get("type") == "text") + "\n" + "\n".join(b.get("thinking") or "" for b in m.get("content") or [] if b.get("type") == "thinking")
                if re.search(r"Agent '[^']{3,80}' (completed|finished)|<task-notification", vis):
                    fab.append({"label": label, "turn": cur["n"], "t": tt, "detector": "D3 notification-shaped text authored by PI", "token": "", "ctx": one(vis, 190)})
                # D2: result-like sentence naming a worker that is open (dispatched/resumed, not yet returned)
                for blk in [b.get("text") or "" for b in m.get("content") or [] if b.get("type") == "text"] + [b.get("thinking") or "" for b in m.get("content") or [] if b.get("type") == "thinking"]:
                    for sent in re.split(r"(?<=[.!?:])\s+|\n+", blk):
                        cand = set(x.group(0).lower() for x in NAME_RE.finditer(sent))
                        for x in LOOSE_RE.finditer(sent):
                            short = x.group(2).lower()
                            cand |= {k for k in open_since if k.endswith(short)}
                        for nm in cand:
                            if nm in open_since and not (tt - open_since[nm] < 0):
                                if re.search(r"\b(found|shows?|showed|came back|returned|is in|are in|reports?|reported|verdict|SUPPORTED|OVERSTATED|UNSUPPORTED|ESCALATE|measured|finished|completed|handed back|hand-back|result)\b", sent) and not re.search(r"\b(will|waiting|wait for|when|once|until|expect|to report|should|going to|sent|dispatch|dispatched|running|asked|brief|resum|if |whether|before|pending|still)\b", sent, re.I):
                                    fab.append({"label": label, "turn": cur["n"], "t": tt, "detector": "D2 result-like sentence about an open worker", "token": nm, "ctx": one(sent, 230)})
            elif t == "user":
                m = r.get("message") or {}
                c = m.get("content")
                origin = r.get("origin") or {}
                kind = origin.get("kind") if isinstance(origin, dict) else None
                raw = unesc(UUID_RE.sub("", line))
                if isinstance(c, str):
                    s = c
                    if kind == "peer" or s.startswith("Another Claude session sent a message") and "[Subagent hand-back]" in s[:600]:
                        mm = re.search(r'from="([a-z0-9]+)"', s)
                        aid = mm.group(1) if mm else origin.get("from")
                        body = s.split(FRAME_END, 1)[-1] if FRAME_END in s else s
                        returned_ids.add(aid)
                        nm = agent_of(aid)
                        open_since.pop(nm, None)
                        new_turn("B", tt, {"agent": nm, "aid": aid, "atype": origin.get("name"), "chars": len(body), "head": one(body, 260), "body": body})
                    elif kind == "task-notification" or s.lstrip().startswith("<task-notification"):
                        mm = re.search(r"<task-id>([a-z0-9]+)</task-id>", s)
                        aid = mm.group(1) if mm else ""
                        mm2 = re.search(r"<summary>(.*?)</summary>", s, re.S)
                        new_turn("N", tt, {"agent": agent_of(aid), "aid": aid, "chars": len(s), "head": one(mm2.group(1) if mm2 else s, 200), "bg": not aid.startswith("a")})
                        if aid.startswith("a"):
                            open_since.pop(agent_of(aid), None)
                    elif kind == "human" or s.lstrip().startswith(("<command-name>", "<command-message>")):
                        new_turn("H", tt, {"head": one(s, 400), "chars": len(s)})
                    else:
                        new_turn("X", tt, {"head": one(s, 240), "chars": len(s)})
                    for h in set(HEX_RE.findall(raw)) | set(x[:8] for x in re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-", line)):
                        carrier.add(h[:7])
                elif isinstance(c, list):
                    kinds = [b.get("type") for b in c if isinstance(b, dict)]
                    for b in c:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_result":
                            txt = text_of(b.get("content"))
                            st_ci = toolinfo.get(b.get("tool_use_id"))
                            if st_ci:
                                st_ci[1]["res_chars"] = len(txt)
                                st_ci[1]["err"] = bool(b.get("is_error"))
                            tur = r.get("toolUseResult")
                            if isinstance(tur, dict) and tur.get("agentId") and b.get("tool_use_id") in pending_dispatch:
                                agent_name[tur["agentId"]] = pending_dispatch[b["tool_use_id"]]
                        elif b.get("type") == "text" and "tool_result" not in kinds:
                            s = b.get("text", "")
                            if kind == "human" or (cur is None):
                                new_turn("H" if kind == "human" else "S", tt, {"head": one(s, 400), "chars": len(s)})
                            elif s.startswith("Base directory for this skill"):
                                pass
                            else:
                                new_turn("X", tt, {"head": one(s, 240), "chars": len(s)})
                    for h in set(HEX_RE.findall(raw)) | set(x[:8] for x in re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-", line)):
                        carrier.add(h[:7])
            elif t == "attachment":
                a = r.get("attachment") or {}
                if a.get("type") == "queued_command":
                    p = a.get("prompt")
                    p = p if isinstance(p, str) else json.dumps(p)
                    mm = re.search(r"<task-id>([a-z0-9]+)</task-id>", p)
                    if cur is not None and mm:
                        cur.setdefault("notices", []).append(mm.group(1))
                        if mm.group(1).startswith("a"):
                            open_since.pop(agent_of(mm.group(1)), None)
                for h in set(HEX_RE.findall(unesc(UUID_RE.sub("", line)))):
                    carrier.add(h[:7])
            elif t in ("system", "queue-operation"):
                for h in set(HEX_RE.findall(unesc(UUID_RE.sub("", line)))):
                    carrier.add(h[:7])
    fab.append({"label": label, "turn": -1, "t": None, "detector": "D1 tokens checked", "token": str(d1_checked[0]), "ctx": ""})
    return turns, think_blocks, think_nonempty, fab, agent_name


def analyse(turns):
    """add auto codes to every turn; returns read rows"""
    reads = []
    seen_read = {}
    last_written = {}
    # flatten later authored content for use proxy
    flat = []   # (turn idx, step idx, authored text, kind-of-call-for-this-text)
    for ti, tn in enumerate(turns):
        for si, st in enumerate(tn["steps"]):
            txt = "\n".join(st["text"])
            for c in st["calls"]:
                if c["kind"] in ("write", "dispatch", "message"):
                    txt += "\n" + c.get("cmd", "") + c.get("key", "")
            flat.append((ti, si, txt))
    # index of authored text by position
    pos = {(a, b): i for i, (a, b, _) in enumerate(flat)}
    for ti, tn in enumerate(turns):
        tn["n_steps"] = len(tn["steps"])
        tn["n_calls"] = sum(len(s["calls"]) for s in tn["steps"])
        tn["agents_dispatched"] = [c.get("agent_name") for s in tn["steps"] for c in s["calls"] if c["kind"] == "dispatch"]
        for si, st in enumerate(tn["steps"]):
            for c in st["calls"]:
                if c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query", "search", "lab_status", "git") or c.get("reads_too"):
                    ps = c["paths"] or [""]
                    cls = obj_class(ps[0]) if c["paths"] else ("lab_status" if c["kind"] == "lab_status" else c["kind"])
                    for p in ps[:3]:
                        base = os.path.basename(p) if p else ""
                        used_turn = used_later = False
                        if len(base) >= 6:
                            for (a, b, tx) in flat[pos[(ti, si)] + 1:]:
                                if base in tx:
                                    used_later = True
                                    if a == ti:
                                        used_turn = True
                                    break
                        kb = os.path.basename(p) if p else ""
                        prev = seen_read.get(kb) if kb else None
                        reads.append({"label": tn["label"], "turn": ti, "trig": tn["triggers"][0]["kind"], "kind": c["kind"], "path": p, "class": obj_class(p) if p else cls,
                                      "chars": (c["res_chars"] or 0) // max(1, len(ps[:3])) if c["res_chars"] is not None else None, "whole": c["kind"] in ("read-whole", "bash-view") and "sed -n" not in c["key"] and "head" not in c["key"].split()[0:2],
                                      "used_later": used_later, "used_same_turn": used_turn,
                                      "repeat": prev is not None, "repeat_after_own_write": bool(prev is not None and last_written.get(kb, -1) > prev),
                                      "key": c["key"]})
                        if kb:
                            seen_read[kb] = ti
                if c["kind"] == "write":
                    for p in c["paths"][:4]:
                        last_written[os.path.basename(p)] = ti
    # hand-back codes
    for ti, tn in enumerate(turns):
        trig = tn["triggers"]
        isB = any(x["kind"] == "B" for x in trig)
        isN = any(x["kind"] == "N" for x in trig)
        calls = [c for s in tn["steps"] for c in s["calls"]]
        codes = []
        if not calls:
            codes.append("H0")
        senders = set()
        for x in trig:
            if x["kind"] in ("B", "N") and x.get("agent"):
                senders.add(x["agent"])
        def is_raw(c):
            if c["kind"] not in ("read-whole", "read-part", "bash-view", "bash-query"):
                return False
            for p in c["paths"]:
                if obj_class(p) in RAW:
                    return True
                if any(s and s in p for s in senders):
                    return True
            return False
        raw_here = any(is_raw(c) for c in calls)
        nxt = turns[ti + 1] if ti + 1 < len(turns) else None
        raw_next = bool(nxt) and any(is_raw(c) for s in nxt["steps"] for c in s["calls"])
        if raw_here:
            codes.append("H1")
        elif raw_next:
            codes.append("H1n")
        wave_note_write = any(c["kind"] == "write" and any("__statera__/wave-" in p for p in c["paths"]) for c in calls)
        if wave_note_write:
            codes.append("H2")
        if any(c["kind"] == "dispatch" for c in calls):
            codes.append("H3")
        if any(c["kind"] == "message" and (c.get("agent_name") in senders or any(c["key"].endswith(a) for a in [x.get("aid") for x in trig if x.get("aid")])) for c in calls):
            codes.append("H4")
        elif any(c["kind"] == "message" for c in calls):
            codes.append("H4o")
        if calls and all(c["kind"] in ("lab_status",) for c in calls):
            codes.append("H6")
        if any(c["kind"] == "write" and re.search(r"git\s+commit", c.get("cmd", "")) for c in calls):
            codes.append("H8")
        if (wave_note_write or any(c["kind"] in ("dispatch", "message") for c in calls)) and not raw_here and not raw_next:
            codes.append("W")
        tn["codes"] = codes
        tn["is_handback"] = isB or isN
        tn["raw_here"] = raw_here
        tn["raw_next"] = raw_next
    return reads


def summary(tn, maxtext=420):
    tg = tn["triggers"][0]
    L = []
    hd = "[%s T%03d %s +%ds] trig=%s%s" % (tn["label"], tn["n"], hhmm(tn["t0"]), tn["t1"] - tn["t0"], "+".join(x["kind"] + ("" if x.get("idle", True) else "~mid") for x in tn["triggers"]), "")
    if tg["kind"] in ("B", "N"):
        hd += " from=%s (%s%s) hb=%dch" % (tg.get("agent"), tg.get("atype") or "", ",bg" if tg.get("bg") else "", tg.get("chars", 0))
        L.append(hd)
        L.append("  HB: " + (tg.get("head") or "")[:260])
        for x in tn["triggers"][1:]:
            L.append("  +%s mid-turn from=%s hb=%dch" % (x["kind"], x.get("agent"), x.get("chars", 0)))
    else:
        L.append(hd)
        L.append("  TRIG: " + (tg.get("head") or "")[:300])
    for si, st in enumerate(tn["steps"]):
        tx = one(" ".join(st["text"]), maxtext)
        cs = []
        for c in st["calls"]:
            if c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query", "search", "lab_status", "git") or c.get("reads_too"):
                cs.append("%s%s[%s %sch]" % (c["kind"], "+view" if c.get("reads_too") else "", one(c["key"], 100), c["res_chars"]))
            elif c["kind"] in ("write", "dispatch", "message", "bash-other", "tool-search", "other"):
                cs.append("%s[%s]" % (c["kind"], one(c["key"], 90)))
        L.append("  s%d%s %s %s" % (si, " TXT:" + tx if tx else "", "" if not st["think"] else "THINK:" + one(" ".join(st["think"]), 200), " ; ".join(cs)))
    L.append("  AUTO: codes=%s steps=%d calls=%d" % (",".join(tn.get("codes", [])), tn["n_steps"], tn["n_calls"]))
    return "\n".join(L)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    allfab, tt_rows, rr_rows = [], [], []
    for arg in sys.argv[2:]:
        label, path = arg.split("=", 1)
        turns, tb, tne, fab, an = parse(label, path)
        reads = analyse(turns)
        with open(os.path.join(out, label + "_turns.jsonl"), "w") as f:
            for tn in turns:
                tn2 = dict(tn)
                tn2["summary"] = summary(tn)
                # keep the raw hand-back body out of the file except its head
                for x in tn2["triggers"]:
                    x.pop("body", None)
                tn2["steps"] = [{"t": s["t"], "text": [one(x, 700) for x in s["text"]], "think": [one(x, 500) for x in s["think"]], "stop": s["stop"], "calls": s["calls"]} for s in tn["steps"]]
                f.write(json.dumps(tn2) + "\n")
        for tn in turns:
            tg = tn["triggers"][0]
            tt_rows.append([tn["label"], tn["n"], hhmm(tn["t0"]), "+".join(x["kind"] for x in tn["triggers"]), "idle" if tg.get("idle", True) else "mid", tg.get("agent", ""), tg.get("chars", ""), tn["n_steps"], tn["n_calls"], int(tn["t1"] - tn["t0"]), ",".join(tn["codes"])])
        for rd in reads:
            rr_rows.append(rd)
        for x in fab:
            x["t"] = hhmm(x["t"]) if x["t"] else ""
            allfab.append(x)
        print("%s: %d turns, %d reads, thinking blocks %d (non-empty %d), fab flags %d, agents named %d" % (label, len(turns), len(reads), tb, tne, len(fab), len(an)))
    with open(os.path.join(out, "turn_table.tsv"), "w") as f:
        f.write("label\tturn\ttime_jst\ttrig\tarrival\tfrom\thb_chars\tsteps\tcalls\tsecs\tcodes\n")
        for r in tt_rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    cols = ["label", "turn", "trig", "kind", "class", "path", "chars", "whole", "used_later", "used_same_turn", "repeat", "repeat_after_own_write", "key"]
    with open(os.path.join(out, "read_table.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rr_rows:
            f.write("\t".join(str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    with open(os.path.join(out, "fabrication_scan.tsv"), "w") as f:
        f.write("label\tturn\ttime_jst\tdetector\ttoken\tcontext\n")
        for x in allfab:
            f.write("\t".join(str(x[k]).replace("\t", " ").replace("\n", " ") for k in ("label", "turn", "t", "detector", "token", "ctx")) + "\n")


if __name__ == "__main__":
    main()
