"""Replays worker transcripts through two hook versions like hook_replay_equiv.py (a copy of it), but fires ONE PostToolBatch per assistant request (message id), after the last tool result of that request, as the platform does (w03-c1), instead of one per tool-result record.

Input/output: as hook_replay_equiv.py (flags --old --new --fx --merged --dump, transcripts); one line per transcript, EQUAL or the first difference.
"""
import argparse, datetime, glob, json, os, shutil, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--old")
ap.add_argument("--new")
ap.add_argument("--fx")
ap.add_argument("--child", nargs=3, metavar=("SCRIPTS", "LAB", "EVENTS"))
ap.add_argument("--max-steps", type=int, default=0)
ap.add_argument("--dump", help="write the old and the new snapshot (after normalisation) of each transcript to DIR/<transcript>.old.json and .new.json")
ap.add_argument("--merged", action="store_true", help="w05-c4: the new version has no PostToolBatch registration: it gets no PostToolBatch events, and the answers are compared as the sequence of non-empty answers with the event name normalised (the old version's note at a step's PostToolBatch is the new one's at that step's PostToolUse); `sent` and `ceil_req` are not compared")
ap.add_argument("transcripts", nargs="*")
args = ap.parse_args()


def child(scripts, lab, events_path):
    sys.path.insert(0, scripts)
    try:
        import budget_core as budget, handback_core as handback   # the lean version keeps its code in modules
    except ImportError:
        import budget, handback
    answers = []
    for ev in map(json.loads, open(events_path)):
        if ev.get("write"):
            path, upto, src = ev["write"]
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(src, "rb") as f:
                data = f.read(upto)
            open(path, "wb").write(data)
        dt = datetime.datetime.fromtimestamp(ev["now"], datetime.timezone.utc)
        for script in ev["scripts"]:
            payload = dict(ev["payload"], cwd=lab)
            if script == "budget":
                if os.environ.get("REPLAY_DROP_BATCH") and payload["hook_event_name"] == "PostToolBatch":
                    continue
                ans = budget.handle(payload, now=ev["now"])
            else:
                ans = handback.gate(payload)
                if payload["hook_event_name"] != "PreToolUse":
                    handback.handle(payload, now=dt)
            answers.append([script, payload["hook_event_name"], payload.get("tool_name"), ans, ev["now"]])
    snap = dict(answers=answers)
    snap["log"] = [{k: v for k, v in json.loads(l).items() if k != "t"} for l in open(os.path.join(lab, "__statera__", "harness.jsonl"))] if os.path.exists(os.path.join(lab, "__statera__", "harness.jsonl")) else []
    hb = os.path.join(lab, "__statera__", "handbacks")
    snap["handbacks"] = {n: open(os.path.join(hb, n), "rb").read().decode("utf-8", "replace") for n in sorted(os.listdir(hb))} if os.path.isdir(hb) else {}
    st = os.path.join(lab, "__statera__", ".harness")
    state = {}
    for n in sorted(os.listdir(st)) if os.path.isdir(st) else []:
        if n.endswith(".json"):
            d = json.load(open(os.path.join(st, n)))
            d.pop("sc", None)
            if os.environ.get("REPLAY_DROP_BATCH") or os.environ.get("REPLAY_NORM"):
                d.pop("sent", None), d.pop("ceil_req", None)
            state[n] = d
        elif n.endswith(".denied"):
            state[n] = "marker"
    snap["state"] = state
    print(json.dumps(snap))


if args.child:
    child(*args.child)
    sys.exit(0)


def epoch(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def events_for(tpath, lab_sess):
    """The hook events of one worker run, from its transcript. Returns (events, steps)."""
    meta = json.load(open(tpath[:-6] + ".meta.json")) if os.path.exists(tpath[:-6] + ".meta.json") else {}
    kind = meta.get("agentType") or "murmuration:explorer"
    name = meta.get("name") or "explorer-w03-x"
    aid = os.path.basename(tpath)[len("agent-"):-6]
    tx = os.path.join(lab_sess, "subagents", "agent-%s.jsonl" % aid)
    base = dict(session_id="s", transcript_path=lab_sess + ".jsonl", permission_mode="auto")
    wk = dict(base, agent_id=aid, agent_type=kind)
    raw = open(tpath, "rb").read()
    lines, pos, offs = raw.split(b"\n"), 0, []
    for l in lines:
        pos += len(l) + 1
        offs.append(min(pos, len(raw)))
    recs = [json.loads(l) if l.strip() else {} for l in lines]
    first = next((r for r in recs if r.get("type") == "user"), {})
    brief = first.get("message", {}).get("content")
    brief = brief if isinstance(brief, str) else "".join(b.get("text", "") for b in brief or [] if isinstance(b, dict))
    t0 = epoch(next(r["timestamp"] for r in recs if r.get("timestamp")))
    ev = [dict(now=t0, scripts=["budget"], payload=dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu0",
                                                         tool_input=dict(subagent_type=kind, prompt=brief or "", name=name))),
          dict(now=t0 + 0.5, scripts=["budget"], payload=dict(wk, hook_event_name="SubagentStart"))]
    calls, last_text, steps, t_last = {}, "", 0, t0
    # w05-c4 (reproducer-w05-4): one PostToolBatch per assistant request (message id), fired after the last result of that request
    mid_of, members, got = {}, {}, {}
    has_result = set()
    for r in recs:
        cc0 = (r.get("message") or {}).get("content")
        if r.get("type") == "user" and isinstance(cc0, list):
            has_result |= {b.get("tool_use_id") for b in cc0 if isinstance(b, dict) and b.get("type") == "tool_result"}
    for r in recs:
        mm = r.get("message") or {}
        cc = mm.get("content")
        if r.get("type") == "assistant" and isinstance(cc, list):
            for b in cc:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b["id"] in has_result:
                    mid_of[b["id"]] = mm.get("id") or b["id"]
                    members.setdefault(mid_of[b["id"]], []).append(b["id"])
    for i, r in enumerate(recs):
        ts = epoch(r["timestamp"]) if r.get("timestamp") else t_last
        t_last = max(t_last, ts)
        m = r.get("message") or {}
        c = m.get("content")
        if r.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b["id"]] = (b["name"], b.get("input"))
                    if b["name"] == "SubagentHandback":
                        ev.append(dict(now=t_last, write=[tx, offs[i], tpath], scripts=["handback"], payload=dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback",
                                                                                                                  tool_input=b.get("input"), tool_use_id=b["id"])))
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    last_text = b["text"]
        elif r.get("type") == "user" and isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            ids = [b["tool_use_id"] for b in c if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in calls]
            first_ev = True
            for tid in ids:
                name_, inp = calls[tid]
                ev.append(dict(now=t_last, write=[tx, offs[i], tpath] if first_ev else None, scripts=["budget"] + (["handback"] if name_ == "SubagentHandback" else []),
                               payload=dict(wk, hook_event_name="PostToolUse", tool_name=name_, tool_input=inp, tool_response="ok", tool_use_id=tid)))
                first_ev = False
            done_groups = []
            for t in ids:
                g = mid_of.get(t, t)
                got.setdefault(g, set()).add(t)
                if got[g] == set(members.get(g, [t])) and g not in done_groups:
                    done_groups.append(g)
            for g in done_groups:
                gids = members.get(g, [])
                ev.append(dict(now=t_last, write=None, scripts=["budget"], payload=dict(wk, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name=calls[t][0], tool_use_id=t) for t in gids if t in calls])))
                steps += 1
    ev.append(dict(now=t_last + 1, write=[tx, len(raw), tpath], scripts=["handback", "budget"],
                   payload=dict(wk, hook_event_name="SubagentStop", agent_transcript_path=tx, last_assistant_message=last_text, permission_mode="auto")))
    # the meta file the hand-back name comes from
    return ev, steps, meta, aid


def run_one(tpath, variant_dir, tag):
    if args.merged:
        os.environ.pop("REPLAY_DROP_BATCH", None)
        os.environ["REPLAY_NORM"] = "1"
        if tag == "new":
            os.environ["REPLAY_DROP_BATCH"] = "1"
    fx = os.path.join(os.path.abspath(args.fx), "run")   # one folder name for both versions, rebuilt each time: paths that appear in hand-backs are then equal
    shutil.rmtree(fx, ignore_errors=True)
    lab, sess = os.path.join(fx, "lab"), os.path.join(fx, "sess")
    os.makedirs(os.path.join(lab, "__statera__"))
    os.makedirs(os.path.join(lab, "__reports__"))
    os.makedirs(os.path.join(sess, "subagents"))
    events, steps, meta, aid = events_for(tpath, sess)
    if args.max_steps:
        keep, n = [], 0
        for e in events:
            keep.append(e)
            if e["payload"]["hook_event_name"] == "PostToolBatch":
                n += 1
                if n >= args.max_steps:
                    break
        events = keep + [events[-1]]
    json.dump(meta, open(os.path.join(sess, "subagents", "agent-%s.meta.json" % aid), "w"))
    ep = os.path.join(fx, "events.jsonl")
    open(ep, "w").write("".join(json.dumps(e) + "\n" for e in events))
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", os.path.join(variant_dir, "scripts"), lab, ep], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise SystemExit("child failed: " + p.stderr[-2000:])
    return json.loads(p.stdout), steps


bad = 0
for t in args.transcripts:
    old, steps = run_one(t, args.old, "old")
    new, _ = run_one(t, args.new, "new")
    diff = None
    if args.merged:
        def norm(snap):
            out = []
            for sc, ev_, tool, ans, now in snap["answers"]:
                if ans:
                    ans = json.loads(json.dumps(ans).replace('"hookEventName": "PostToolBatch"', '"hookEventName": "PostToolUse"'))
                    out.append([sc, now, ans])
            return out
        old["answers"], new["answers"] = norm(old), norm(new)
    if args.dump:
        os.makedirs(args.dump, exist_ok=True)
        for tag_, snap_ in (("old", old), ("new", new)):
            json.dump(snap_, open(os.path.join(args.dump, os.path.basename(t) + "." + tag_ + ".json"), "w"), indent=1)
    for key in ("answers", "log", "handbacks", "state"):
        if old[key] != new[key]:
            if isinstance(old[key], list):
                i = next((j for j in range(min(len(old[key]), len(new[key]))) if old[key][j] != new[key][j]), min(len(old[key]), len(new[key])))
                diff = "%s differs at %d: old=%s new=%s" % (key, i, json.dumps(old[key][i:i + 1])[:300], json.dumps(new[key][i:i + 1])[:300])
            else:
                diff = "%s differs: old=%s new=%s" % (key, json.dumps(old[key])[:300], json.dumps(new[key])[:300])
            break
    nans = sum(1 for a in old["answers"] if (a[2] if args.merged else a[3]))
    kinds = sorted({l["event"] for l in old["log"]})
    print("%s | steps=%d answers=%d log=%d (%s) | %s" % (os.path.basename(t), steps, nans, len(old["log"]), ",".join(kinds), "EQUAL" if diff is None else "DIFF " + diff))
    bad += diff is not None
sys.exit(1 if bad else 0)
