#!/usr/bin/env python3
"""Per-agent-run profile rebuilt from Claude Code transcripts (what a SA3 ledger row would hold).

Run:   python3 -I profile_runs.py [--out DIR]
Reads (read-only): ~/.claude/projects/<project>/<session>.jsonl and <session>/subagents/agent-*.jsonl
Writes CSVs into DIR (default: the folder of this script):
    runs.csv          one row per agent run (subagent file) and per main thread (session file)
    tools_by_run.csv  long table: run, tool, calls, errors
    by_role.csv       runs grouped by (group, agent type, model)
    parent_view.csv   what the parent transcript knows about each launched agent (launch, SendMessage,
                      task-notification usage) next to the sub-file totals
    crosschecks.csv   totals against Claude Code's own `cost-state` record and against lab_status.py
    dup_messages.csv  assistant messages present in more than one transcript file

Only the standard library is used. Transcripts are streamed, never printed.
"""
import collections
import csv
import glob
import importlib.util
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, ".claude", "projects")
COMB = "-Users-hacker-Documents-explore-combinatorics-on-binary"
WT = "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e"

# (group, project folder, session id). Order = tie-break for who "owns" a duplicated message.
SESSIONS = [
    ("genesis", COMB, "566fa912-7009-421a-9d79-11145e2b8db9"),
    ("design", COMB, "82e8a947-1a0c-441c-bc39-df8e2e5fa743"),
    ("other-3ccc", COMB, "3ccc590f-0187-4f79-b7af-4955944f1374"),
    ("other-2947", COMB, "2947f9dc-1c3a-452b-97a5-39d4510a1271"),
    ("this_run", WT, "ab96c5ed-ead3-4b36-9671-6076e3914087"),
]
IDLE_GAP_S = 300  # a gap between two records longer than this is not "active" time


def ts(s):
    """ISO timestamp -> seconds since epoch (float)."""
    from datetime import datetime, timezone
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()


def read_jsonl(path):
    bad = 0
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except ValueError:
                bad += 1
    return out, bad


def blocks(rec):
    m = rec.get("message")
    if isinstance(m, dict) and isinstance(m.get("content"), list):
        return m["content"]
    return []


def scan(path):
    """Parse one transcript file into raw per-file structures (no cross-file logic)."""
    recs, bad = read_jsonl(path)
    f = {"path": path, "records": len(recs), "bad_lines": bad, "msgs": {}, "tool_uses": {}, "tool_results": {},
         "stamps": [], "hooks": collections.Counter(), "efforts": collections.Counter(),
         "advisors": collections.Counter(), "attr_agent": collections.Counter(), "attr_skill": collections.Counter(),
         "attr_plugin": collections.Counter(), "user_events": [], "cost_state": None, "agent_setting": None,
         "thinking_ms": 0, "compactions": 0, "sys_hook_errors": 0, "sys_stop_hooks": 0, "task_notifs": [],
         "permission": collections.Counter(), "queue_ops": 0, "versions": collections.Counter(),
         "entry": collections.Counter(), "cwds": collections.Counter(), "queued": collections.Counter(),
         "stopped_wakeups": collections.Counter(), "wakeup_ts": []}
    last_tools = None
    last_assistant_stop = None
    for r in recs:
        t = r.get("type")
        if r.get("timestamp"):
            f["stamps"].append(ts(r["timestamp"]))
        if r.get("version"):
            f["versions"][r["version"]] += 1
        if r.get("entrypoint"):
            f["entry"][r["entrypoint"]] += 1
        if r.get("cwd"):
            f["cwds"][r["cwd"]] += 1
        if t == "cost-state":
            f["cost_state"] = r
        elif t == "agent-setting":
            f["agent_setting"] = r.get("agentSetting")
        elif t == "queue-operation":
            f["queue_ops"] += 1
        elif t == "system":
            if r.get("subtype") == "stop_hook_summary":
                f["sys_stop_hooks"] += 1
                if r.get("hookErrors"):
                    f["sys_hook_errors"] += 1
            if "compact" in str(r.get("subtype")):
                f["compactions"] += 1
        elif t == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") in ("hook_success", "hook_additional_context", "hook_error", "hook_blocking_error"):
                f["hooks"][a.get("hookName") or a.get("type")] += 1
            if a.get("type") == "queued_command":
                kind = (a.get("origin") or {}).get("kind") if isinstance(a.get("origin"), dict) else None
                f["queued"][kind or "?"] += 1
        elif t == "assistant":
            m = r["message"]
            mid = m.get("id") or r.get("uuid")
            e = f["msgs"].setdefault(mid, {"copies": [], "stop": None, "ts": [], "model": m.get("model"),
                                           "requestId": r.get("requestId"), "tool_ids": [], "blocks": []})
            e["copies"].append(m.get("usage") or {})
            e["ts"].append(ts(r["timestamp"]))
            if m.get("stop_reason"):
                e["stop"] = m["stop_reason"]
            if r.get("effort"):
                f["efforts"][r["effort"]] += 1
            if r.get("advisorModel"):
                f["advisors"][r["advisorModel"]] += 1
            if r.get("attributionAgent"):
                f["attr_agent"][r["attributionAgent"]] += 1
            if r.get("attributionSkill"):
                f["attr_skill"][r["attributionSkill"]] += 1
            if r.get("attributionPlugin"):
                f["attr_plugin"][r["attributionPlugin"]] += 1
            f["thinking_ms"] += int(r.get("thinkingDurationMs") or 0)
            for c in blocks(r):
                e["blocks"].append({"type": c.get("type")})
                if c.get("type") == "tool_use":
                    f["tool_uses"][c["id"]] = {"name": c["name"], "ts": ts(r["timestamp"]), "mid": mid,
                                               "input": c.get("input")}
                    e["tool_ids"].append(c["id"])
            last_assistant_stop = m.get("stop_reason")
            last_tools = [c.get("name") for c in blocks(r) if c.get("type") == "tool_use"]
        elif t == "user":
            m = r.get("message") or {}
            content = m.get("content")
            origin = (r.get("origin") or {}).get("kind")
            if origin in ("coordinator", "peer", "task-notification") and last_tools is not None and (not last_tools or "SubagentHandback" in last_tools):
                f["stopped_wakeups"][origin] += 1
                f["wakeup_ts"].append(ts(r["timestamp"]))
            if isinstance(content, str):
                f["user_events"].append({"ts": ts(r["timestamp"]), "origin": origin, "meta": bool(r.get("isMeta")),
                                         "text": content[:200], "after_stop": last_assistant_stop})
                if "<task-notification>" in content:
                    f["task_notifs"].append(content)
            elif isinstance(content, list):
                texts = [c for c in content if c.get("type") == "text"]
                for c in content:
                    if c.get("type") == "tool_result":
                        f["tool_results"][c["tool_use_id"]] = {"ts": ts(r["timestamp"]),
                                                               "error": bool(c.get("is_error")),
                                                               "tur": r.get("toolUseResult")}
                if texts:
                    f["user_events"].append({"ts": ts(r["timestamp"]), "origin": origin, "meta": bool(r.get("isMeta")),
                                             "text": texts[0].get("text", "")[:200], "after_stop": last_assistant_stop})
                    for c in texts:
                        if "<task-notification>" in c.get("text", ""):
                            f["task_notifs"].append(c["text"])
            pd = r.get("permissionDecision")
            if isinstance(pd, dict):
                f["permission"][pd.get("decision", "?") + "/" + pd.get("source", "?")] += 1
    return f


def final_usage(copies):
    """Usage of a message = the last streamed copy (earlier copies carry partial output_tokens)."""
    return copies[-1]


def usage_vec(u):
    cc = u.get("cache_creation") or {}
    return {"in": int(u.get("input_tokens") or 0), "out": int(u.get("output_tokens") or 0),
            "cr": int(u.get("cache_read_input_tokens") or 0), "cw": int(u.get("cache_creation_input_tokens") or 0),
            "cw1h": int(cc.get("ephemeral_1h_input_tokens") or 0)}


def union_len(intervals):
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(intervals):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def main(argv):
    out = os.path.dirname(os.path.abspath(__file__))
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)

    # ---- 1. scan every file
    files = []  # dicts: group, session, kind, run_id, path, meta, scan
    for gi, (group, proj, sid) in enumerate(SESSIONS):
        base = os.path.join(PROJ, proj)
        main_path = os.path.join(base, sid + ".jsonl")
        if not os.path.exists(main_path):
            continue
        files.append({"group": group, "gi": gi, "session": sid, "kind": "main", "run_id": sid, "path": main_path,
                      "meta": {}, "prefix": None})
        for sp in sorted(glob.glob(os.path.join(base, sid, "subagents", "**", "agent-*.jsonl"), recursive=True)):
            run_id = os.path.basename(sp)[len("agent-"):-len(".jsonl")]
            mp = sp[:-len(".jsonl")] + ".meta.json"
            meta = {}
            if os.path.exists(mp):
                meta = json.load(open(mp))
            has_prefix = os.path.exists(sp[:-len(".jsonl")] + ".prefix.json")
            files.append({"group": group, "gi": gi, "session": sid, "kind": "sub", "run_id": run_id, "path": sp,
                          "meta": meta, "has_meta": os.path.exists(mp), "has_prefix": has_prefix})
    for fl in files:
        fl["scan"] = scan(fl["path"])
        fl["first"] = min(fl["scan"]["stamps"]) if fl["scan"]["stamps"] else 0.0

    # ---- 2. global ownership of assistant messages (the same message id can sit in several files)
    order = sorted(range(len(files)), key=lambda i: (files[i]["first"], files[i]["gi"], i))
    owner = {}
    seen_in = collections.defaultdict(list)
    for i in order:
        for mid in files[i]["scan"]["msgs"]:
            owner.setdefault(mid, i)
            seen_in[mid].append(i)
    dup_rows = []
    pair = collections.Counter()
    for mid, lst in seen_in.items():
        if len(lst) > 1:
            key = tuple(sorted({(files[i]["group"], files[i]["kind"], files[i]["run_id"]) for i in lst}))
            pair[key] += 1
    for key, n in sorted(pair.items(), key=lambda kv: -kv[1]):
        dup_rows.append({"messages": n, "files": " | ".join("%s:%s:%s" % k for k in key)})

    # ---- 3. parent-side view of launches (Agent tool) and messages
    parent = {}  # run_id -> dict
    launches = {}  # toolUseId -> {input, agentId}
    for fl in files:
        if fl["kind"] != "main":
            continue
        s = fl["scan"]
        for tid, tu in s["tool_uses"].items():
            if tu["name"] in ("Agent", "Task"):
                res = s["tool_results"].get(tid, {})
                tur = res.get("tur") if isinstance(res.get("tur"), dict) else {}
                aid = tur.get("agentId")
                inp = tu["input"] or {}
                launches[tid] = {"session": fl["session"], "agent_id": aid, "type": inp.get("subagent_type"),
                                 "name": inp.get("name"), "model": inp.get("model"),
                                 "bg": inp.get("run_in_background"), "desc": inp.get("description"),
                                 "maxTurns": inp.get("maxTurns") or inp.get("max_turns"),
                                 "status": tur.get("status"), "resolved": tur.get("resolvedModel"),
                                 "fg_tokens": tur.get("totalTokens"), "fg_tools": tur.get("totalToolUseCount"),
                                 "fg_ms": tur.get("totalDurationMs"), "input_keys": ",".join(sorted(inp))}
                if aid:
                    p = parent.setdefault((fl["session"], aid), collections.defaultdict(int))
                    p["launches"] += 1
        name_to_id = {}
        for tid, l in launches.items():
            if l["agent_id"] and l["name"]:
                name_to_id[l["name"]] = l["agent_id"]
        for tid, tu in s["tool_uses"].items():
            if tu["name"] == "SendMessage":
                to = (tu["input"] or {}).get("to")
                res = s["tool_results"].get(tid, {})
                tur = res.get("tur") if isinstance(res.get("tur"), dict) else {}
                aid = tur.get("resumedAgentId") or tur.get("revivedAgentId") or (tur.get("pin") or {}).get("id") or name_to_id.get(to) or to
                p = parent.setdefault((fl["session"], aid), collections.defaultdict(int))
                p["sendmessage"] += 1
                msg = str(tur.get("message", ""))
                if tur.get("resumedAgentId") or tur.get("revivedAgentId"):
                    p["sendmessage_resumed"] += 1
                elif msg.startswith("Message queued"):
                    p["sendmessage_queued"] += 1
        for text in s["task_notifs"]:
            for blk in re.findall(r"<task-notification>.*?</task-notification>", text, re.S):
                m = re.search(r"<task-id>([^<]+)</task-id>", blk)
                if not m:
                    continue
                p = parent.setdefault((fl["session"], m.group(1)), collections.defaultdict(int))
                p["notifications"] += 1
                u = re.search(r"<usage>(.*?)</usage>", blk, re.S)
                if u:
                    for k, v in re.findall(r"<(\w+)>(\d+)</\1>", u.group(1)):
                        p["notif_last_" + k] = int(v)
                st = re.search(r"<status>([^<]+)</status>", blk)
                if st:
                    p["notif_status_" + st.group(1)] += 1

    # ---- 4. one row per file
    rows, tool_rows = [], []
    for i, fl in enumerate(files):
        s = fl["scan"]
        owned = [mid for mid in s["msgs"] if owner[mid] == i]
        tot = collections.Counter()
        models = collections.Counter()
        partial = 0       # messages whose copies carried different usage
        last_not_max = 0  # messages whose last copy is not the max output_tokens
        for mid in owned:
            e = s["msgs"][mid]
            v = usage_vec(final_usage(e["copies"]))
            for k, x in v.items():
                tot[k] += x
            if e["model"]:
                models[e["model"]] += 1
            outs = [int(c.get("output_tokens") or 0) for c in e["copies"]]
            if len(set(outs)) > 1:
                partial += 1
            if outs[-1] != max(outs):
                last_not_max += 1
        tot_naive = collections.Counter()
        for mid, e in s["msgs"].items():
            for k, x in usage_vec(e["copies"][-1]).items():
                tot_naive[k] += x
        # tools (only for tool_use ids of owned messages)
        calls, errs = collections.Counter(), collections.Counter()
        intervals = []
        for tid, tu in s["tool_uses"].items():
            if owner[tu["mid"]] != i:
                continue
            calls[tu["name"]] += 1
            res = s["tool_results"].get(tid)
            if res:
                if res["error"]:
                    errs[tu["name"]] += 1
                intervals.append((tu["ts"], max(res["ts"], tu["ts"])))
        unanswered = sum(1 for tid, tu in s["tool_uses"].items() if owner[tu["mid"]] == i and tid not in s["tool_results"])
        st = sorted(s["stamps"])
        wall = st[-1] - st[0] if st else 0.0
        active = sum(b - a for a, b in zip(st, st[1:]) if b - a <= IDLE_GAP_S)
        # last assistant message
        last_mid = max(s["msgs"], key=lambda m: s["msgs"][m]["ts"][-1]) if s["msgs"] else None
        last_stop = s["msgs"][last_mid]["stop"] if last_mid else None
        last_has_tool = bool(s["msgs"][last_mid]["tool_ids"]) if last_mid else False
        # segments / resumes: user text events after an end_turn
        deliveries = [u for u in s["user_events"] if u["origin"] in ("coordinator", "peer", "task-notification")]
        agent_type = fl["meta"].get("agentType") or (s["agent_setting"] if fl["kind"] == "main" else None) or ("main" if fl["kind"] == "main" else "(no meta)")
        l = None
        for _, cand in launches.items():
            if cand["agent_id"] == fl["run_id"] and cand["session"] == fl["session"]:
                l = cand
        p = parent.get((fl["session"], fl["run_id"]), {})
        handback = calls.get("SubagentHandback", 0)
        ctx_max = 0
        ctx_last = 0
        for mid in sorted(s["msgs"], key=lambda m: s["msgs"][m]["ts"][-1]):
            u = usage_vec(s["msgs"][mid]["copies"][-1])
            ctx_last = u["in"] + u["cr"] + u["cw"]
            ctx_max = max(ctx_max, ctx_last)
        last_tools_names = [s["tool_uses"][t]["name"] for t in (s["msgs"][last_mid]["tool_ids"] if last_mid else [])]
        last_tool = last_tools_names[-1] if last_tools_names else ""
        last_blocks = s["msgs"][last_mid]["blocks"] if last_mid else []
        if not s["msgs"]:
            ended_by = "no assistant messages"
        elif not last_tools_names:
            ended_by = "final text" if any(c.get("type") == "text" for c in last_blocks) else "thinking only (in flight or cut)"
        elif last_tool == "SubagentHandback":
            ended_by = "handback"
        else:
            ended_by = "tool_use (no reply: still running, killed or cut)"
        row = {
            "group": fl["group"], "session": fl["session"][:8], "kind": fl["kind"], "run_id": fl["run_id"][:12] if fl["kind"] == "sub" else fl["run_id"][:8],
            "agent_type": agent_type, "name": fl["meta"].get("name") or (l or {}).get("name") or "",
            "description": (fl["meta"].get("description") or (l or {}).get("desc") or "")[:60],
            "has_meta_json": fl.get("has_meta", ""), "spawn_depth": fl["meta"].get("spawnDepth", ""),
            "parent_agent": fl["meta"].get("parentAgentId", ""), "shape": fl["meta"].get("requestShape", ""),
            "model_meta": fl["meta"].get("model", ""), "model_resolved": (l or {}).get("resolved", ""),
            "model_used": ";".join("%s*%d" % kv for kv in models.most_common()) if models else ";".join(
                sorted({e["model"] for e in s["msgs"].values() if e["model"]})),
            "effort": ";".join("%s*%d" % kv for kv in s["efforts"].most_common()),
            "advisor": ";".join(sorted(s["advisors"])),
            "start_utc": __import__("datetime").datetime.fromtimestamp(st[0], __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") if st else "",
            "wall_s": round(wall), "active_s": round(active), "idle_s": round(wall - active),
            "tool_wait_s": round(union_len(intervals)), "thinking_s": round(s["thinking_ms"] / 1000),
            "turns_owned": len(owned), "turns_file": len(s["msgs"]),
            "in": tot["in"], "out": tot["out"], "cache_read": tot["cr"], "cache_write": tot["cw"], "cache_write_1h": tot["cw1h"],
            "new_tokens": tot["in"] + tot["cw"] + tot["out"],
            "in_naive_file": tot_naive["in"], "out_naive_file": tot_naive["out"], "cr_naive_file": tot_naive["cr"], "cw_naive_file": tot_naive["cw"],
            "tool_calls": sum(calls.values()), "tool_errors": sum(errs.values()), "tool_unanswered": unanswered,
            "distinct_tools": len(calls),
            "top_tools": ";".join("%s*%d" % kv for kv in calls.most_common(6)),
            "mcp_calls": sum(n for k, n in calls.items() if k.startswith("mcp__")),
            "last_stop_reason": last_stop, "last_msg_has_tool_use": last_has_tool,
            "subagent_handback_calls": handback,
            "handback_calls": handback, "resumes_wakeups_after_stop": sum(s["stopped_wakeups"].values()),
            "wakeups_by_origin": ";".join("%s*%d" % kv for kv in s["stopped_wakeups"].most_common()),
            "midrun_queued_msgs": ";".join("%s*%d" % kv for kv in s["queued"].most_common()),
            "ctx_last": ctx_last, "ctx_max": ctx_max, "last_tool": last_tool, "ended_by": ended_by,
            "parent_sendmessage": p.get("sendmessage", ""), "parent_sendmessage_resumed": p.get("sendmessage_resumed", ""),
            "parent_notifications": p.get("notifications", ""), "notif_last_tokens": p.get("notif_last_subagent_tokens", p.get("notif_last_total_tokens", "")),
            "notif_last_tool_uses": p.get("notif_last_tool_uses", ""), "notif_last_duration_ms": p.get("notif_last_duration_ms", ""),
            "hooks_seen": ";".join("%s*%d" % kv for kv in s["hooks"].most_common(4)),
            "compactions": s["compactions"], "stop_hook_summaries": s["sys_stop_hooks"],
            "permission": ";".join("%s*%d" % kv for kv in s["permission"].most_common()),
            "attr_skill": ";".join(sorted(s["attr_skill"])), "attr_plugin": ";".join(sorted(s["attr_plugin"])),
            "cc_version": ";".join(sorted(s["versions"])), "entrypoint": ";".join(sorted(s["entry"])),
            "cwd": ";".join(sorted(s["cwds"]))[:90],
            "records": s["records"], "bad_lines": s["bad_lines"], "msgs_with_partial_copies": partial,
            "last_copy_not_max_out": last_not_max,
            "msgs_shared_with_other_file": sum(1 for mid in s["msgs"] if len(seen_in[mid]) > 1),
            "msgs_owned_elsewhere": len(s["msgs"]) - len(owned),
            "file_bytes": os.path.getsize(fl["path"]),
        }
        rows.append(row)
        for tname, n in calls.items():
            tool_rows.append({"group": fl["group"], "run_id": row["run_id"], "agent_type": agent_type, "tool": tname,
                              "calls": n, "errors": errs.get(tname, 0)})

    # ---- 4b. USD allocation [assumption]. Claude Code's own `cost-state` record gives USD per session x model.
    # Allocate it to runs pro rata of w = in + 1.25*cw + 0.1*cr + 5*out_adj (relative multipliers are an assumption:
    # list-price ratios for cache write / cache read / output against input; they only decide the SPLIT among runs,
    # the total is Claude Code's own number). Sub-agent output_tokens are unreliable (see report), so for runs in a
    # session x model the cost-state output not seen in the main thread is spread over the sub runs by turn count.
    cs_by = {}
    for fl in files:
        if fl["kind"] == "main" and fl["scan"]["cost_state"]:
            cs_by[fl["session"][:8]] = fl["scan"]["cost_state"]["modelUsage"]
    for r in rows:
        r["out_adj"] = r["out"]
        r["usd_alloc_assumed"] = ""
    groups = collections.defaultdict(list)
    for r in rows:
        mdl = r["model_used"].split("*")[0] if r["model_used"] else ""
        if r["session"] in cs_by and mdl in cs_by[r["session"]] and r["turns_owned"] > 0:
            groups[(r["session"], mdl)].append(r)
    for (sess, mdl), rs in groups.items():
        mu = cs_by[sess][mdl]
        main_out = sum(r["out"] for r in rs if r["kind"] == "main")
        sub_rs = [r for r in rs if r["kind"] == "sub"]
        gap = max(0, mu["outputTokens"] - sum(r["out"] for r in rs))
        sub_turns = sum(r["turns_owned"] for r in sub_rs) or 1
        for r in sub_rs:
            r["out_adj"] = r["out"] + round(gap * r["turns_owned"] / sub_turns)
        wsum = sum(r["in"] + 1.25 * r["cache_write"] + 0.1 * r["cache_read"] + 5 * r["out_adj"] for r in rs)
        for r in rs:
            w = r["in"] + 1.25 * r["cache_write"] + 0.1 * r["cache_read"] + 5 * r["out_adj"]
            r["usd_alloc_assumed"] = round(mu["costUSD"] * w / wsum, 3) if wsum else ""

    # ---- 4c. per-resume segments (a run resumed after it stopped = one ledger row per segment in v5's design)
    seg_rows = []
    for i, fl in enumerate(files):
        s = fl["scan"]
        if not s["wakeup_ts"] or not any(owner[m] == i for m in s["msgs"]):
            continue
        edges = [0.0] + sorted(s["wakeup_ts"]) + [float("inf")]
        for k in range(len(edges) - 1):
            tot = collections.Counter()
            n = 0
            t0, t1 = None, None
            for mid, e in s["msgs"].items():
                if owner[mid] != i:
                    continue
                t = e["ts"][0]
                if edges[k] <= t < edges[k + 1]:
                    n += 1
                    for kk, x in usage_vec(e["copies"][-1]).items():
                        tot[kk] += x
                    t0 = t if t0 is None else min(t0, t)
                    t1 = e["ts"][-1] if t1 is None else max(t1, e["ts"][-1])
            seg_rows.append({"group": fl["group"], "run_id": fl["run_id"][:12], "segment": k + 1, "starts_with": "launch" if k == 0 else "wake-up after stop",
                             "turns": n, "in": tot["in"], "cache_read": tot["cr"], "cache_write": tot["cw"], "out_recorded": tot["out"],
                             "span_s": round((t1 - t0)) if t0 is not None else 0})
    with open(os.path.join(out, "resume_segments.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["group", "run_id", "segment", "starts_with", "turns", "in", "cache_read", "cache_write", "out_recorded", "span_s"])
        w.writeheader()
        w.writerows(seg_rows)

    cols = list(rows[0].keys())
    with open(os.path.join(out, "runs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out, "tools_by_run.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["group", "run_id", "agent_type", "tool", "calls", "errors"])
        w.writeheader()
        w.writerows(tool_rows)
    with open(os.path.join(out, "dup_messages.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["messages", "files"])
        w.writeheader()
        w.writerows(dup_rows)

    # ---- 5. by role
    agg = collections.OrderedDict()
    for r in rows:
        if r["turns_owned"] == 0 and r["kind"] == "sub":
            key = (r["group"], r["agent_type"] + " (copy: all messages owned elsewhere)", "")
        else:
            key = (r["group"], r["agent_type"], r["model_used"].split("*")[0] if r["model_used"] else "")
        a = agg.setdefault(key, collections.defaultdict(float))
        a["runs"] += 1
        for k in ("turns_owned", "in", "out", "cache_read", "cache_write", "new_tokens", "wall_s", "active_s", "tool_calls", "tool_errors"):
            a[k] += r[k]
        a["max_turns"] = max(a["max_turns"], r["turns_owned"])
        a["usd"] += float(r["usd_alloc_assumed"] or 0)
        a.setdefault("tl", []).append(r["turns_owned"]) if False else None
        a["max_wall_s"] = max(a["max_wall_s"], r["wall_s"])
    with open(os.path.join(out, "by_role.csv"), "w", newline="") as fh:
        cols2 = ["group", "agent_type", "model", "runs", "turns_total", "turns_mean", "turns_max", "in", "out", "cache_read", "cache_write", "new_tokens", "wall_s_total", "wall_s_max", "tool_calls", "tool_errors", "usd_alloc_assumed"]
        w = csv.writer(fh)
        w.writerow(cols2)
        for (g, t, m), a in agg.items():
            n = a["runs"]
            w.writerow([g, t, m, int(n), int(a["turns_owned"]), round(a["turns_owned"] / n, 1), int(a["max_turns"]), int(a["in"]), int(a["out"]), int(a["cache_read"]), int(a["cache_write"]), int(a["new_tokens"]), int(a["wall_s"]), int(a["max_wall_s"]), int(a["tool_calls"]), int(a["tool_errors"]), round(a["usd"], 2)])

    # ---- 6. parent view
    with open(os.path.join(out, "parent_view.csv"), "w", newline="") as fh:
        cols3 = ["session", "tool_use_id", "agent_id", "subagent_type", "name", "model_arg", "resolved_model", "background", "status", "input_keys", "maxTurns_arg", "fg_totalTokens", "fg_toolUses", "fg_ms"]
        w = csv.writer(fh)
        w.writerow(cols3)
        for tid, l in launches.items():
            w.writerow([l["session"][:8], tid[-8:], l["agent_id"], l["type"], l["name"], l["model"], l["resolved"], l["bg"], l["status"], l["input_keys"], l["maxTurns"], l["fg_tokens"], l["fg_tools"], l["fg_ms"]])

    # ---- 7. cross checks
    cc = []
    for fl in files:
        if fl["kind"] != "main" or not fl["scan"]["cost_state"]:
            continue
        cs = fl["scan"]["cost_state"]
        sess = fl["session"]
        mine = collections.defaultdict(collections.Counter)
        mine_naive = collections.defaultdict(collections.Counter)
        for i, f2 in enumerate(files):
            if f2["session"] != sess:
                continue
            for mid, e in f2["scan"]["msgs"].items():
                v = usage_vec(e["copies"][-1])
                mdl = e["model"]
                for k, x in v.items():
                    mine_naive[mdl][k] += x
                    if owner[mid] == i:
                        mine[mdl][k] += x
        for mdl, mu in cs["modelUsage"].items():
            m1, m2 = mine.get(mdl, {}), mine_naive.get(mdl, {})
            cc.append({"check": "cost-state vs transcripts", "session": sess[:8], "model": mdl,
                       "cost_state_in": mu["inputTokens"], "cost_state_out": mu["outputTokens"], "cost_state_think": mu.get("thinkingTokens"),
                       "cost_state_cr": mu["cacheReadInputTokens"], "cost_state_cw": mu["cacheCreationInputTokens"], "cost_state_usd": round(mu["costUSD"], 4),
                       "mine_in": m1.get("in", 0), "mine_out": m1.get("out", 0), "mine_cr": m1.get("cr", 0), "mine_cw": m1.get("cw", 0),
                       "mine_all_files_in": m2.get("in", 0), "mine_all_files_out": m2.get("out", 0), "mine_all_files_cr": m2.get("cr", 0), "mine_all_files_cw": m2.get("cw", 0)})
        cc.append({"check": "cost-state totals", "session": sess[:8], "model": "(all)", "cost_state_usd": round(cs["totalCostUSD"], 4),
                   "cost_state_in": cs.get("totalDuration"), "cost_state_out": cs.get("totalAPIDuration"), "cost_state_think": cs.get("totalToolDuration")})
    # lab_status.spend() on three roots
    spec = importlib.util.spec_from_file_location("lab_status", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts", "lab_status.py"))
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    for label, root in (("worktree", os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))),
                        ("main-checkout", "/Users/hacker/Documents/src/CrackingShells/Murmuration"),
                        ("combinatorics", "/Users/hacker/Documents/explore/combinatorics_on_binary")):
        rws, folders, warns = ls.spend(root)
        tot = collections.Counter()
        for r in rws:
            for k in ("messages", "input", "cache_write", "cache_read", "output", "runs"):
                tot[k] += r[k]
        cc.append({"check": "lab_status.spend", "session": label, "model": "(all)", "cost_state_in": len(folders), "cost_state_out": len(warns),
                   "mine_in": tot["input"], "mine_out": tot["output"], "mine_cr": tot["cache_read"], "mine_cw": tot["cache_write"],
                   "mine_all_files_in": tot["messages"], "mine_all_files_out": tot["runs"]})
    cols4 = []
    for r in cc:
        for k in r:
            if k not in cols4:
                cols4.append(k)
    with open(os.path.join(out, "crosschecks.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols4)
        w.writeheader()
        w.writerows(cc)
    print("wrote", out, "rows:", len(rows), "tool rows:", len(tool_rows), "dup groups:", len(dup_rows))


if __name__ == "__main__":
    main(sys.argv[1:])
