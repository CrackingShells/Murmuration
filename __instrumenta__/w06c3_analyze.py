# w06-c3: derives the stage-1 metric tables (m1 fields, m2 firing, m3 request-0 tokens, m5 hook durations) from run directories (server.jsonl, truth.jsonl, run.json) and the session transcripts under ~/.claude/projects; inputs: subcommand (m1|m2|m3|m5) and run dirs; outputs: markdown tables on stdout
import collections, datetime, glob, hashlib, json, os, re, statistics as st, sys

PROJ = os.path.expanduser("~/.claude/projects")


def jl(path):
    out = []
    for l in open(path, errors="replace"):
        if l.strip():
            try: out.append(json.loads(l))
            except ValueError: pass
    return out


def session_files(rd):
    """(main transcript path, {agent_id: subagent transcript path}) of the run in directory rd."""
    r = json.load(open(os.path.join(rd, "run.json")))
    sid = r["session_id"]
    for f in glob.glob(os.path.join(PROJ, "*", sid + ".jsonl")):
        subs = {os.path.basename(p)[6:-6]: p for p in glob.glob(f[:-6] + "/subagents/agent-*.jsonl")}
        return f, subs
    raise SystemExit("no transcript for " + rd)


def resolve(obj, path):
    for k in path.split("."):
        if not isinstance(obj, dict) or k not in obj: return None
        obj = obj[k]
    return obj


def templates(plug):
    """event arg -> {arg name: payload path} from the plugin's hooks.json"""
    h = json.load(open(os.path.join(plug, "hooks", "hooks.json")))["hooks"]
    out = {}
    for groups in h.values():
        for g in groups:
            for x in g["hooks"]:
                if x["type"] == "mcp_tool":
                    out[x["input"]["event"]] = {k: v[2:-1] for k, v in x["input"].items() if k != "event"}
    return out


def same(want, got):
    if want is None: return got == ""
    if isinstance(want, str): return got == want
    try: return json.loads(got) == want
    except (ValueError, TypeError): return False


def m1(rds, plug):
    T = templates(plug)
    tab = collections.defaultdict(lambda: dict(calls=0, ok=0, derived_n=0, bad=[], fields=collections.Counter(), empty=collections.Counter()))
    for rd in rds:
        S, tr = jl(os.path.join(rd, "server.jsonl")), jl(os.path.join(rd, "truth.jsonl"))
        used = [False] * len(tr)
        for s in S:
            a = s["args"]; ev = a["event"]; row = tab[ev]; row["calls"] += 1
            tp = T[ev]; best = None
            for i, t in sorted(enumerate(tr), key=lambda it: used[it[0]]):   # unused truth records first; a used one may serve again (the platform runs one command hook for two registrations with the same command text)
                if t.get("hook_event_name") != (ev.split(":")[0]) or (":" in ev and t.get("tool_name") not in (ev.split(":")[1], "Task")) or (t.get("agent_id") or "") != a.get("agent_id", ""): continue
                bad = [k for k, p in tp.items() if not same(resolve(t, p), a.get(k, ""))]
                if not bad: best = (i, []); break
                if best is None or len(bad) < len(best[1]): best = (i, bad)
            if best and not best[1]:
                used[best[0]] = True; row["ok"] += 1
                tid = a.get("agent_id", "")
                if tid:
                    row["derived_n"] += 1
                    dv = os.path.join(a["transcript_path"][:-6], "subagents", "agent-%s.jsonl" % tid)
                    row["derived"] = row.get("derived", 0) + os.path.exists(dv)
                for k, p in tp.items():
                    row["fields"][k] += 1
                    if a.get(k, "") == "": row["empty"][k] += 1
            else:
                row["bad"].append(best[1] if best else "no truth record")
    print("| event | server calls | all fields equal to the platform's stdin | fields requested | requested fields empty on every call | derived subagent transcript path exists |\n|:--|--:|--:|:--|:--|:--|")
    for ev, r in tab.items():
        always_empty = [k for k in r["fields"] if r["empty"][k] == r["fields"][k]]
        print("| %s | %d | %d | %s | %s | %s |" % (ev, r["calls"], r["ok"], ", ".join(sorted(T[ev])), ", ".join(always_empty) or "-", ("%d of %d" % (r["derived"], r["derived_n"])) if r["derived_n"] else "-"))
        if r["bad"]: print("  mismatches:", r["bad"][:5])


def expected(path):
    """events the transcript implies: dict(pre_agent, post, batch, handback)"""
    recs = jl(path)
    calls, results, batches, ends = [], {}, set(), set()
    for r in recs:
        if r.get("type") == "assistant":
            tu = [b for b in (r["message"].get("content") or []) if isinstance(b, dict) and b.get("type") == "tool_use"]
            if tu: batches.add(r.get("requestId") or r["message"].get("id"))
            calls += [(b["id"], b["name"]) for b in tu]
        elif r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "hook_success" and r["attachment"].get("hookEvent") == "SubagentStop" and r["attachment"].get("command") == "plugin:wt:res/hook":
            ends.add(r["attachment"].get("toolUseID"))   # SubagentStop has no tool call in the transcript: the platform's own hook record of the run is the reference (a worker's stops: one, plus one per draft turn in auto mode)
        elif r.get("type") == "user" and isinstance(r.get("message", {}).get("content"), list):
            for b in r["message"]["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_result": results[b["tool_use_id"]] = json.dumps(b.get("content"))
    denied = [i for i, n in calls if "WT-DENY" in results.get(i, "") or "hook error: WT-DENY" in results.get(i, "")]
    names = collections.Counter(n for _, n in calls)
    return dict(pre_agent=names["Agent"] + names["Task"], post=len(calls) - len(denied), batch=len(batches), handback=names["SubagentHandback"], denied=len(denied), ends=len(ends))


def m2(rds):
    print("| run | agent | event | server log | transcript implies | equal |\n|:--|:--|:--|--:|--:|:--|")
    tot = collections.Counter(); bad = 0
    for rd in rds:
        main, subs = session_files(rd)
        S = [s["args"] for s in jl(os.path.join(rd, "server.jsonl"))]
        who = [("main", "", main)] + [("worker", aid, p) for aid, p in subs.items()]
        for kind, aid, p in who:
            c = collections.Counter(a["event"] for a in S if a.get("agent_id", "") == (aid if kind == "worker" else ""))
            e = expected(p)
            rows = [("PostToolUse", c["PostToolUse"], e["post"]), ("PostToolBatch", c["PostToolBatch"], e["batch"])]
            if kind == "main": rows.append(("PreToolUse:Agent", c["PreToolUse:Agent"], e["pre_agent"]))
            else: rows += [("SubagentStart", c["SubagentStart"], 1), ("SubagentStop", c["SubagentStop"], e["ends"]), ("PreToolUse:SubagentHandback", c["PreToolUse:SubagentHandback"], e["handback"]), ("PostToolUse:SubagentHandback", c["PostToolUse:SubagentHandback"], e["handback"])]
            for ev, got, want in rows:
                ok = got == want; bad += not ok; tot[ev, kind] += got
                print("| %s | %s %s | %s | %d | %d | %s |" % (os.path.basename(rd.rstrip("/")), kind, aid[:6], ev, got, want, "yes" if ok else "NO"))
    print("\nrows not equal: %d; fired totals: %s" % (bad, dict(tot)))


def usage0(path):
    """input tokens of the first model request of a transcript: in + cache read + cache write (max over its records), plus the shape hash and tool names"""
    recs = jl(path); first = None; use = None; shape = None; brief = None
    for r in recs:
        if r.get("type") == "api-request-shape" and shape is None: shape = r
        if r.get("type") == "user" and brief is None and not r.get("isMeta"):
            c = r["message"]["content"]; brief = hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()[:8]
        if r.get("type") == "assistant" and r["message"].get("usage"):
            rid = r.get("requestId") or r["message"].get("id")
            if first is None: first = rid
            if rid == first:
                u = r["message"]["usage"]; cur = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                use = max(use or 0, cur)
            else: break
    tl = (shape or {}).get("shape", {}).get("tools") or []
    tools = [x.get("name") for x in tl] if isinstance(tl, list) else re.findall(r"'name': '([^']+)'", str(tl))
    # the server's tool named anywhere in the request's tool list or in the deferred-tool listing attachments of the transcript
    named = any("plugin_wt_res" in json.dumps(r.get("attachment") or {}) for r in recs if r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "deferred_tools_delta") or any("plugin_wt_res" in str(x) for x in tools)
    tools = tools + (["<wt_res tool named>"] if named else [])
    return use, (shape or {}).get("shapeHash"), tools, brief


def m3(arms):
    """arms: label=dir,dir,... ; prints request-0 tokens per run for main and each worker"""
    print("| arm | run | thread | request-0 input tokens | shapeHash[:10] | tools in request | first user message sha[:8] |\n|:--|:--|:--|--:|:--|--:|:--|")
    for arm in arms:
        label, dirs = arm.split("=")
        for rd in dirs.split(","):
            main, subs = session_files(rd)
            u, h, t, b = usage0(main); print("| %s | %s | main | %s | %s | %d | %s |" % (label, os.path.basename(rd), u, (h or "")[:10], len(t), b))
            for aid, p in sorted(subs.items()):
                u, h, t, b = usage0(p); print("| %s | %s | worker %s | %s | %s | %d | %s |" % (label, os.path.basename(rd), aid[:6], u, (h or "")[:10], len(t), b))


def m5(rds):
    d = collections.defaultdict(list)
    for rd in rds:
        main, subs = session_files(rd)
        for p in [main] + list(subs.values()):
            for r in jl(p):
                a = r.get("attachment") or {}
                if a.get("type") == "hook_success" and a.get("command") == "plugin:wt:res/hook":
                    d[a["hookName"]].append(a.get("durationMs", -1))
    print("| hook (event:tool) | n | median ms | p90 ms | max ms |\n|:--|--:|--:|--:|--:|")
    allv = []
    for k in sorted(d):
        v = sorted(d[k]); allv += v
        print("| %s | %d | %.1f | %d | %d |" % (k, len(v), st.median(v), v[int(.9 * (len(v) - 1))], v[-1]))
    allv.sort(); print("| all (transcript durationMs) | %d | %.1f | %d | %d |" % (len(allv), st.median(allv), allv[int(.9 * (len(allv) - 1))], allv[-1]))
    # debug-log cross-check: from the `mcp_tool calling` line to the platform's next line about that hook's output (1 ms resolution; SubagentStart has no durationMs in the transcript)
    ts = lambda l: datetime.datetime.strptime(l[:23], "%Y-%m-%dT%H:%M:%S.%f").timestamp()
    pooled, start = [], []
    for rd in rds:
        lines = open(os.path.join(rd, "dbg.log"), errors="replace").read().split("\n")
        for i, l in enumerate(lines):
            if "Hooks: mcp_tool calling plugin:wt:res/hook" in l:
                for l2 in lines[i + 1:i + 40]:
                    if "Hook output does not start with {" in l2 or "Successfully parsed and validated hook JSON output" in l2 or "mcp_tool hook error" in l2:
                        dt = (ts(l2) - ts(l)) * 1000
                        pooled.append(dt)
                        if any("Hook SubagentStart (plugin:wt:res/hook) provided additionalContext" in x for x in lines[i + 1:i + 60]) and "with 8 arg(s)" in l: start.append(dt)
                        break
    for name, v in (("all mcp_tool calls (debug log)", pooled), ("SubagentStart (debug log)", start)):
        v = sorted(v)
        if v: print("| %s | %d | %.1f | %d | %d |" % (name, len(v), st.median(v), v[int(.9 * (len(v) - 1))], v[-1]))


def m6(rds):
    """effects: for each nonce the server issued (inject, deny, block), is it in a transcript record the model received, and does the model's own text quote it"""
    print("| run | effect | nonce | in the record that carries it to the model | quoted by the model in a later message |\n|:--|:--|:--|:--|:--|")
    for rd in rds:
        main, subs = session_files(rd)
        texts = {}
        for who, p in [("main", main)] + [("worker", q) for q in subs.values()]:
            texts[p] = (who, jl(p))
        for s in jl(os.path.join(rd, "server.jsonl")):
            kind, _, nonce = s["tag"].partition(":")
            if kind not in ("inject", "deny", "block"): continue
            aid = s["args"].get("agent_id", "")
            carrier, quoted = [], []
            for p, (who, recs) in texts.items():
                for r in recs:
                    a = r.get("attachment") or {}
                    blob = json.dumps(a)
                    if nonce in blob and a.get("type") in ("hook_additional_context", "hook_blocking_error"): carrier.append("%s:%s" % (who, a["type"]))
                    if r.get("type") == "user" and nonce in json.dumps(r.get("message")) and "tool_result" in json.dumps(r.get("message"))[:400]: carrier.append("%s:tool_result" % who)
                    if r.get("type") == "assistant" and nonce in json.dumps(r["message"].get("content")) : quoted.append(who)
            print("| %s | %s (%s) | %s | %s | %s |" % (os.path.basename(rd), kind, s["args"]["event"], nonce, ", ".join(sorted(set(carrier))) or "NONE", ", ".join(sorted(set(quoted))) or "no"))
        # a refused Agent call starts no worker
        denied = [x for x in jl(os.path.join(rd, "server.jsonl")) if x["tag"].startswith("deny")]
        started = sum(1 for p, (w, recs) in texts.items() if w == "worker" and any("DENYME" in json.dumps(r.get("message", "")) for r in recs[:6]))
        if denied: print("|  | refused call started a worker | | %d workers whose brief holds DENYME (want 0) | |" % started)


def m4(rds):
    """outage: server restarts, hook records by type in the transcripts, what the model saw, whether the refusal held, the platform's own wait per event (`classic.<Event> settled in`)"""
    print("| run | server starts | server calls | hook_success / non_blocking_error / cancelled(timedOut) records | waits >= 1 s: event settled in (s) | refused Agent call: refusal seen / worker started | model's final text mentions a hook failure |\n|:--|--:|--:|:--|:--|:--|:--|")
    for rd in rds:
        main, subs = session_files(rd)
        c = collections.Counter(); seen_deny = False; started = 0; mentions = False
        for p in [main] + list(subs.values()):
            recs = jl(p)
            if p != main and any("DENYME" in json.dumps(r.get("message", "")) for r in recs[:6]): started += 1
            for r in recs:
                a = r.get("attachment") or {}
                if a.get("type") == "hook_success" and a.get("command") == "plugin:wt:res/hook": c["ok"] += 1
                elif a.get("type") == "hook_non_blocking_error" and "plugin:wt:res" in json.dumps(a): c["err"] += 1
                elif a.get("type") == "hook_cancelled" and a.get("timedOut"): c["cancel"] += 1
                if p == main and r.get("type") == "user" and "WT-DENY" in json.dumps(r.get("message")): seen_deny = True
        res = json.load(open(os.path.join(rd, "run.json"))).get("result", "")
        mentions = any(w in res.lower() for w in ("not connected", "hook error", "hook failed", "timed out"))
        waits = []
        for l in open(os.path.join(rd, "dbg.log"), errors="replace"):
            m = re.search(r"classic\.(\w+) settled in ([\d.]+)ms", l)
            if m and float(m.group(2)) >= 1000 and m.group(1).startswith("Post") : waits.append("%s %.1f" % (m.group(1), float(m.group(2)) / 1000))
        ns = open(os.path.join(rd, "server.starts")).read().count("pid")
        print("| %s | %d | %d | %d / %d / %d | %s | %s / %d | %s |" % (os.path.basename(rd), ns, len(jl(os.path.join(rd, "server.jsonl"))), c["ok"], c["err"], c["cancel"], "; ".join(waits) or "-", "yes" if seen_deny else "no", started, "yes" if mentions else "no"))


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    {"m1": lambda: m1(a[1:], a[0]), "m2": lambda: m2(a), "m3": lambda: m3(a), "m5": lambda: m5(a), "m6": lambda: m6(a), "m4": lambda: m4(a)}[c]()
