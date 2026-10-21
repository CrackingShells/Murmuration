# Turns the 16 headless sessions of explorer-w07-g (debug logs + run JSON + transcripts) into one JSON row per tool call (tool phase from the transcript, hook ms, classifier-wait ms and run ms from the debug log) and one row per session; inputs: <S>/dbg/<label>.log, <S>/runs/<label>.json, ~/.claude/projects/-private-tmp-murmuration-w07-explorer-w07-g-work/<session>.jsonl (read only); outputs: <out>/calls.jsonl and <out>/sessions.jsonl (no ids, no tokens).
# usage: w07g_parse.py S OUT_DIR   (label 'trial' = cell A0; its run JSON is runs/trial.json, its log dbg/trial.log)
import json, os, re, sys, glob, datetime

S, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
PROJ = os.path.expanduser("~/.claude/projects/-private-tmp-murmuration-w07-explorer-w07-g-work")
CELL = {"A": ("auto", "on", "none"), "B": ("auto", "off", "none"), "C": ("auto", "on", "lab"), "D": ("auto", "off", "lab"), "F": ("default+allow", "off", "none"),
        "W": ("auto", "off", "none"), "L": ("auto", "off", "none")}


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


HOOK = re.compile(r"^(\S+) \[DEBUG\] Hooks: (PreToolUse|PostToolUse|PostToolBatch|UserPromptSubmit|SessionStart|Stop|SubagentStart):?(\S*) \[(.*?)\](?: \(plugin (\S+)\))? finished with status (\d+) \((\d+)ms\)")
DSTART = re.compile(r"^(\S+) \[INFO\] \[Stall\] tool_dispatch_start tool=(\S+) toolUseId=(\S+) permissionDecisionMs=(\d+)")
DEND = re.compile(r"^(\S+) \[INFO\] \[Stall\] tool_dispatch_end tool=(\S+) toolUseId=(\S+) outcome=(\S+) durationMs=(\d+)")
APIREQ = re.compile(r"^(\S+) \[DEBUG\] \[API REQUEST\] .* source=(\S+)")
FIRSTBYTE = re.compile(r"^(\S+) \[DEBUG\] \[API:timing\] first byte after (\d+)ms")


def short(cmd):
    m = re.findall(r"([\w.-]+\.(?:py|sh))", cmd)
    return m[-1] if m else cmd[:40]


def parse_log(path):
    hooks, ds, de, api, fb = [], {}, {}, [], []
    for line in open(path, errors="replace"):
        if "Hooks:" in line and "finished" in line:
            m = HOOK.match(line)
            if m:
                hooks.append(dict(ts=ts(m.group(1)), event=m.group(2), tool=m.group(3), script=short(m.group(4)), plugin=m.group(5) or "settings", ms=int(m.group(7))))
            continue
        if "tool_dispatch_" in line:
            m = DSTART.match(line)
            if m:
                ds[m.group(3)] = dict(ts=ts(m.group(1)), tool=m.group(2), perm_ms=int(m.group(4)))
                continue
            m = DEND.match(line)
            if m:
                de[m.group(3)] = dict(ts=ts(m.group(1)), run_ms=int(m.group(5)), outcome=m.group(4))
            continue
        if "[API REQUEST]" in line:
            m = APIREQ.match(line)
            if m:
                api.append((ts(m.group(1)), m.group(2)))
        elif "first byte after" in line:
            m = FIRSTBYTE.match(line)
            if m:
                fb.append((ts(m.group(1)), int(m.group(2))))
    return hooks, ds, de, api, fb


def parse_transcript(sid):
    f = os.path.join(PROJ, sid + ".jsonl")
    calls, order, results, asst_ts, user_ts = {}, [], {}, [], None
    for line in open(f):
        r = json.loads(line)
        t = r.get("type")
        if t == "user" and user_ts is None and isinstance(r.get("message", {}).get("content"), str):
            user_ts = ts(r["timestamp"])
        if t == "assistant":
            asst_ts.append(ts(r["timestamp"]))
            for b in r["message"].get("content", []):
                if b.get("type") == "tool_use":
                    u = r["message"].get("usage") or {}
                    calls[b["id"]] = dict(tool=b["name"], ts=ts(r["timestamp"]), cmd=json.dumps(b["input"])[:120], msg=r["message"].get("id"),
                                          ctx=(u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0))
                    order.append(b["id"])
        if t == "user" and isinstance(r.get("message", {}).get("content"), list):
            for b in r["message"]["content"]:
                if b.get("type") == "tool_result":
                    pd = r.get("permissionDecision") or {}
                    results[b["tool_use_id"]] = dict(ts=ts(r["timestamp"]), reason=pd.get("reasonType"), decision=pd.get("decision"), err=bool(b.get("is_error")),
                                                     out_chars=len(json.dumps(b.get("content"))))
    return calls, order, results, asst_ts, user_ts


calls_out, sess_out = [], []
for jf in sorted(glob.glob(os.path.join(S, "runs", "*.json"))):
    label = os.path.basename(jf)[:-5]
    j = json.load(open(jf))
    sid = j["session_id"]
    key = "A" if label == "trial" else label[0]
    mode, colgrep, plug = CELL[key]
    hooks, ds, de, api, fb = parse_log(os.path.join(S, "dbg", label + ".log"))
    calls, order, results, asst_ts, user_ts = parse_transcript(sid)
    pre = sorted([h for h in hooks if h["event"] == "PreToolUse"], key=lambda h: h["ts"])
    post = sorted([h for h in hooks if h["event"] == "PostToolUse"], key=lambda h: h["ts"])
    main_api = [a for a in api if a[1] == "sdk"]
    n_calls = 0
    for i, tid in enumerate(order):
        c, res, d1, d2 = calls[tid], results.get(tid), ds.get(tid), de.get(tid)
        if not (res and d1 and d2):
            continue
        # PreToolUse hooks that finished between the tool_use record and this dispatch start, matching tool
        mine = [h for h in pre if c["ts"] - 0.05 <= h["ts"] <= d1["ts"] + 0.01 and h["tool"] == c["tool"]]
        # the permission wait starts when the last PreToolUse hook is done (checked on the trial log)
        phase = res["ts"] - c["ts"]
        pre_ms = max([h["ms"] for h in mine] or [0])
        postm = [h for h in post if d2["ts"] - 0.05 <= h["ts"] <= res["ts"] + 0.3 and h["tool"] == c["tool"]]
        n_calls += 1
        calls_out.append(dict(label=label, cell=key, mode=mode, colgrep=colgrep, plugin=plug, n_in_run=i + 1, msg=c["msg"], tool=c["tool"], cmd=c["cmd"],
                              ctx_tokens=c["ctx"], phase_ms=round(phase * 1000), pre_ms=pre_ms, pre=[(h["script"], h["ms"]) for h in mine], perm_ms=d1["perm_ms"], run_ms=d2["run_ms"],
                              post=[(h["script"], h["ms"]) for h in postm], reason=res["reason"], err=res["err"], out_chars=res["out_chars"],
                              disp_to_end_ms=round((d2["ts"] - d1["ts"]) * 1000), asst_to_disp_ms=round((d1["ts"] - c["ts"]) * 1000),
                              end_to_result_ms=round((res["ts"] - d2["ts"]) * 1000)))
    sess_out.append(dict(label=label, cell=key, mode=mode, colgrep=colgrep, plugin=plug, session=sid[:8], duration_ms=j.get("duration_ms"), api_ms=j.get("duration_api_ms"),
                         turns=j.get("num_turns"), cost=round(j.get("total_cost_usd") or 0, 4), main_requests=len(main_api), side_queries=len(api) - len(main_api), n_calls=n_calls,
                         n_tool_use=len(order), n_classifier_results=sum(1 for t in order if results.get(t, {}).get("reason") == "classifier"),
                         prompt_to_last_assistant_s=round(max(asst_ts) - user_ts, 2) if user_ts and asst_ts else None,
                         first_call_to_last_result_s=round(max(results[t]["ts"] for t in results) - min(calls[t]["ts"] for t in order), 2) if order and results else None,
                         pre_hooks=sorted({(h["script"], h["plugin"]) for h in pre}), post_hooks=sorted({(h["script"], h["plugin"]) for h in post}),
                         pre_hook_ms_list=[h["ms"] for h in pre], post_hook_ms_list=[h["ms"] for h in post],
                         all_hooks=[(h["event"], h["tool"], h["script"], h["plugin"], h["ms"]) for h in hooks]))
with open(os.path.join(OUT, "calls.jsonl"), "w") as f:
    f.write("".join(json.dumps(x) + "\n" for x in calls_out))
with open(os.path.join(OUT, "sessions.jsonl"), "w") as f:
    f.write("".join(json.dumps(x) + "\n" for x in sess_out))
print(len(calls_out), "calls,", len(sess_out), "sessions")
