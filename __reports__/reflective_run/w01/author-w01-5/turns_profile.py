#!/usr/bin/env python3
"""Claim w01-c5: turn counts, turn-limit stops and resume cost of worker runs.

Run (full):  python3 -I turns_profile.py
Run (quick): python3 -I turns_profile.py --quick      # this run's files only, same code path
Options:     --until ISO   count only records with timestamp <= ISO (default: SNAPSHOT_DEFAULT,
                           so a later re-run reproduces the same numbers although the transcripts grow)
             --out DIR     where the CSVs go (default: folder of this script)

Reads (read-only) ~/.claude/projects/... transcripts. Reuses scan(), usage_vec(), ts() of
explorer-w01-a's profile_runs.py (loaded by path, not modified). Standard library only.

Writes: runs_turns.csv, segments.csv, stops.csv, pi_notice.csv, turn_dist.csv, cost_by_turn.csv,
        first_write.csv, summary.txt
"""
import collections
import csv
import importlib.util
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(HERE, "..", "explorer-w01-a", "profile_runs.py")
SNAPSHOT_DEFAULT = "2026-10-19T02:24:30.000Z"  # frozen when the artifacts were written (UTC)

spec = importlib.util.spec_from_file_location("profile_runs", PROFILE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

# list price, USD per million tokens. Source: claude-api skill model table, cached 2026-10-06
# (Sonnet 5.5 $2 in / $10 out, cache read $0.20; Opus 5.5 $4 in / $20 out, cache read $0.20).
# Cache-write multipliers 1.25 (5m) and 2.0 (1h) are [assumption] (standard Anthropic ratios; not in that table).
PRICE = {"sonnet": dict(i=2.0, o=10.0, cr=0.20, cw5=2.5, cw1h=4.0),
         "opus": dict(i=4.0, o=20.0, cr=0.20, cw5=5.0, cw1h=8.0)}


def fam(model):
    m = model or ""
    return "opus" if "opus" in m else "sonnet"


def usd(u, family, one_hour=False):
    p = PRICE[family]
    cw = p["cw1h"] if one_hour else p["cw5"]
    return (u["in"] * p["i"] + u["out"] * p["o"] + u["cr"] * p["cr"] + u["cw"] * cw) / 1e6


def weighted(u):
    """input-token equivalents: in 1, cache write 1.25, cache read 0.1, output 5 (explorer-w01-a's weights)."""
    return u["in"] + 1.25 * u["cw"] + 0.1 * u["cr"] + 5 * u["out"]


# role analogue of each genesis/design worker, judged from its description only [assumption: by hand].
# E = explorer-like (survey/probe/loose brief), A = author-like (build/derive/experiment toward a claim),
# V = verifier-like (review/reproduce/verify/adversarial), X = other (naming, platform probe with 3-5 turns, counsel)
ROLE = {  # keys: first 8 characters of the agent id
    "a04ebecb": "A", "a200b6a7": "A", "a2f3c738": "A", "a33a82c9": "V", "a3f3fa3f": "A", "a4ad7c71": "A",
    "a5160f9a": "X", "a74632da": "X", "a807fe2b": "V", "a9a74136": "E",
    "a1b61307": "X", "a2e84d18": "V", "a495c3be": "X", "a4a2cf87": "X", "a4b39e78": "X", "a4c12d60": "A",
    "a5073b71": "X", "a58d15f9": "V", "a806faff": "X", "a8322cae": "V", "aab20641": "X", "ac43197c": "V",
    "ac93fc76": "X", "acbce338": "X", "adceb261": "E", "add2d044": "X", "af4a8695": "X", "aff15377": "E",
    "aff72ee6": "A",
}
ROLE_NAME = {"E": "explorer-like", "A": "author-like", "V": "verifier-like", "X": "other"}


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return ""
    k = (len(xs) - 1) * q
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 1)


def main(argv):
    out = HERE
    until = SNAPSHOT_DEFAULT
    quick = "--quick" in argv
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    if "--until" in argv:
        until = argv[argv.index("--until") + 1]
    os.makedirs(out, exist_ok=True)
    T = P.ts(until if until.endswith("Z") and "." in until else until.replace("Z", ".000Z"))

    # ---- scan transcripts (explorer-w01-a's scan) -------------------------------------------------
    sessions = [s for s in P.SESSIONS if (s[0] == "this_run" or not quick)]
    files = []
    for gi, (group, proj, sid) in enumerate(sessions):
        base = os.path.join(P.PROJ, proj)
        mp = os.path.join(base, sid + ".jsonl")
        if not os.path.exists(mp):
            continue
        files.append({"group": group, "gi": gi, "session": sid, "kind": "main", "run_id": sid, "path": mp, "meta": {}})
        import glob
        for sp in sorted(glob.glob(os.path.join(base, sid, "subagents", "**", "agent-*.jsonl"), recursive=True)):
            rid = os.path.basename(sp)[len("agent-"):-len(".jsonl")]
            mj = sp[:-len(".jsonl")] + ".meta.json"
            meta = json.load(open(mj)) if os.path.exists(mj) else {}
            files.append({"group": group, "gi": gi, "session": sid, "kind": "sub", "run_id": rid, "path": sp, "meta": meta})
    for fl in files:
        fl["scan"] = P.scan(fl["path"])
        fl["first"] = min(fl["scan"]["stamps"]) if fl["scan"]["stamps"] else 0.0

    # ownership of a message id: earliest file (same rule as explorer-w01-a); message counted only if first copy <= T
    order = sorted(range(len(files)), key=lambda i: (files[i]["first"], files[i]["gi"], i))
    owner = {}
    for i in order:
        for mid in files[i]["scan"]["msgs"]:
            owner.setdefault(mid, i)

    # ---- parent view: notifications, SendMessage resumes, launches ----------------------------------
    notif = {}      # (session, task_id) -> list of (ts, kind, summary)
    resumes = collections.defaultdict(list)  # (session, agent_id) -> [ts of "Resuming agent" results]
    launched = {}   # (session, agent_id) -> name
    pi_msgs = {}    # session -> list of (ts, usage vec, model, tool names)
    for fl in files:
        if fl["kind"] != "main":
            continue
        s = fl["scan"]
        for tid, tu in s["tool_uses"].items():
            if tu["name"] in ("Agent", "Task"):
                res = s["tool_results"].get(tid, {})
                tur = res.get("tur") if isinstance(res.get("tur"), dict) else {}
                if tur.get("agentId"):
                    launched[(fl["session"], tur["agentId"])] = (tu["input"] or {}).get("name") or (tu["input"] or {}).get("description")
        for tid, res in s["tool_results"].items():
            tur = res.get("tur")
            if isinstance(tur, dict) and (tur.get("resumedAgentId") or tur.get("revivedAgentId")):
                resumes[(fl["session"], tur.get("resumedAgentId") or tur.get("revivedAgentId"))].append(res["ts"])
        pm = []
        for mid, e in s["msgs"].items():
            pm.append((e["ts"][0], P.usage_vec(e["copies"][-1]), e["model"], [s["tool_uses"][t]["name"] for t in e["tool_ids"]]))
        pi_msgs[fl["session"]] = sorted(pm, key=lambda x: x[0])
        # task notifications with timestamps (raw pass; first sighting of a (task, summary) pair)
        seen = set()
        with open(fl["path"], encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "<task-notification>" not in line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                t = P.ts(r["timestamp"]) if r.get("timestamp") else None
                text = json.dumps(r).replace("\\n", " ").replace('\\"', '"')
                for blk in re.findall(r"<task-notification>.*?</task-notification>", text, re.S):
                    m = re.search(r"<task-id>([^<]+)</task-id>", blk)
                    sm = re.search(r"<summary>(.*?)</summary>", blk, re.S)
                    if not m or not sm:
                        continue
                    summ = sm.group(1)
                    kind = "limit" if "turn limit" in summ else ("finished" if "finished" in summ else "other")
                    dm = re.search(r"<duration_ms>(\d+)</duration_ms>", blk)
                    # one notice = (task id, kind, duration_ms): a resumed agent that finishes twice gives two notices,
                    # while the 3 to 4 renderings of one notice (queue record, queued command, user record) share the key
                    key = (fl["session"], m.group(1), kind, dm.group(1) if dm else "")
                    if key in seen:
                        continue
                    seen.add(key)
                    notif.setdefault((fl["session"], m.group(1)), []).append((t, kind, summ[:90]))

    # ---- per-run table ------------------------------------------------------------------------------
    run_rows, seg_rows, stop_rows, notice_rows, fw_rows, cost_rows = [], [], [], [], [], []
    per_run_turns = {}
    for i, fl in enumerate(files):
        if fl["kind"] != "sub":
            continue
        s = fl["scan"]
        mids = [m for m in s["msgs"] if owner[m] == i and s["msgs"][m]["ts"][0] <= T]
        if not mids:
            continue
        mids.sort(key=lambda m: s["msgs"][m]["ts"][0])
        meta = fl["meta"]
        rid = fl["run_id"]
        name = meta.get("name") or launched.get((fl["session"], rid)) or ""
        model = s["msgs"][mids[0]]["model"]
        family = fam(model)
        # wake-ups: user records with a delivery origin (a message from the parent / a notification)
        wakes = sorted(u["ts"] for u in s["user_events"] if u["origin"] in ("coordinator", "peer", "task-notification") and u["ts"] <= T)
        stamps = sorted(x for x in s["stamps"] if x <= T)
        seg_of = lambda t: sum(1 for w in wakes if w <= t)
        segs = collections.defaultdict(list)
        for m in mids:
            segs[seg_of(s["msgs"][m]["ts"][0])].append(m)
        ntool = collections.Counter()
        bash_msgs = 0
        for m in mids:
            names = [s["tool_uses"][t]["name"] for t in s["msgs"][m]["tool_ids"]]
            ntool.update(names)
            if "Bash" in names:
                bash_msgs += 1
        tot = collections.Counter()
        for m in mids:
            for k, x in P.usage_vec(s["msgs"][m]["copies"][-1]).items():
                tot[k] += x
        one_h = tot["cw1h"] > 0
        last_m = mids[-1]
        last_names = [s["tool_uses"][t]["name"] for t in s["msgs"][last_m]["tool_ids"]]
        ended = "handback" if "SubagentHandback" in last_names else ("tool_use" if last_names else "text/thinking")
        lim = [n for n in notif.get((fl["session"], rid), []) if n[1] == "limit" and n[0] <= T]
        fin = [n for n in notif.get((fl["session"], rid), []) if n[1] == "finished" and n[0] <= T]
        role = ROLE.get(rid[:8], "") or ("E" if "explorer" in str(meta.get("agentType")) else "A" if "author" in str(meta.get("agentType")) else "V" if "reproducer" in str(meta.get("agentType")) or "adversary" in str(meta.get("agentType")) else "")
        status = "finished" if (fin or ended == "handback" and len(wakes) == 0 and fl["group"] != "this_run") else ("limit-stopped" if lim else "")
        if fl["group"] == "this_run" and not fin and not lim:
            status = "in flight at snapshot"
        elif fl["group"] == "this_run" and fin:
            status = "finished" if not lim else "limit-stopped, resumed, finished"
        run_rows.append({
            "group": fl["group"], "run_id": rid[:9], "name": name, "agent_type": meta.get("agentType", ""),
            "role_analogue": ROLE_NAME.get(role, ""), "model": model, "turns": len(mids), "segments": len(segs),
            "turns_per_segment": "/".join(str(len(segs[k])) for k in sorted(segs)), "tool_calls": sum(ntool.values()),
            "bash_calls": ntool["Bash"], "bash_msgs": bash_msgs, "status": status, "ended_by": ended,
            "hit_limit_notice": len(lim), "wall_s": round(stamps[-1] - stamps[0]) if stamps else 0,
            "last_record_utc": __import__("datetime").datetime.fromtimestamp(stamps[-1], __import__("datetime").timezone.utc).strftime("%H:%M:%S") if stamps else "",
            "in": tot["in"], "out": tot["out"], "cache_read": tot["cr"], "cache_write": tot["cw"],
            "weighted_in_eq": round(weighted(tot)), "usd_list": round(usd(tot, family, one_h), 3),
        })
        per_run_turns[rid] = (fl, mids)
        # first write of a deliverable: Write/Edit to __scrupuli__ or a report path, or Bash with a heredoc/redirect to them
        first_w, n_w, n_refused = None, 0, 0
        for k, m in enumerate(mids, 1):
            for t in s["msgs"][m]["tool_ids"]:
                tu = s["tool_uses"][t]
                inp = tu["input"] or {}
                hit = False
                if tu["name"] in ("Write", "Edit"):
                    fp = str(inp.get("file_path", ""))
                    hit = ("__scrupuli__" in fp) or os.path.basename(fp).startswith("report")
                elif tu["name"] == "Bash":
                    cmd = str(inp.get("command", ""))
                    hit = "__scrupuli__" in cmd and bool(re.search(r">>?\s*\S*__scrupuli__|tee\s", cmd))
                if hit:
                    n_w += 1
                    res = s["tool_results"].get(t, {})
                    if res.get("error"):
                        n_refused += 1
                    elif first_w is None:
                        first_w = k
        if fl["group"] == "this_run":
            fw_rows.append({"name": name, "turns": len(mids), "first_ok_deliverable_write_turn": first_w or "", "deliverable_write_attempts": n_w, "refused_by_harness": n_refused})
        # turn-by-turn cost (cumulative) for the cost-by-turn table
        cum = 0.0
        for k, m in enumerate(mids, 1):
            u = P.usage_vec(s["msgs"][m]["copies"][-1])
            cum += usd(u, family, one_h)
            cost_rows.append({"group": fl["group"], "run_id": rid[:9], "name": name, "turn": k, "ctx_tokens": u["in"] + u["cr"] + u["cw"],
                              "turn_usd": round(usd(u, family, one_h), 5), "cum_usd": round(cum, 4)})
        # segments and resumes
        cw_med = statistics.median([P.usage_vec(s["msgs"][m]["copies"][-1])["cw"] for m in mids])
        prev_end = None
        for k in sorted(segs):
            ms = segs[k]
            u0 = P.usage_vec(s["msgs"][ms[0]]["copies"][-1])
            agg = collections.Counter()
            for m in ms:
                for kk, x in P.usage_vec(s["msgs"][m]["copies"][-1]).items():
                    agg[kk] += x
            ctx0 = u0["in"] + u0["cr"] + u0["cw"]
            row = {"group": fl["group"], "run_id": rid[:9], "name": name, "segment": k, "turns": len(ms),
                   "cw_all_other_turns_median": round(cw_med)}
            if k == 0:
                row.update({"wake_utc": "", "gap_s": "", "first_turn_cw": u0["cw"], "first_turn_cr": u0["cr"], "ctx_first_turn": ctx0,
                            "first_turn_cw_share_of_ctx": round(u0["cw"] / ctx0, 3) if ctx0 else ""})
            else:
                w = wakes[k - 1]
                before = [x for x in stamps if x < w]
                pe = before[-1] if before else None
                gap = w - pe if pe else None
                extra_cw = max(0, u0["cw"] - cw_med)
                counterfactual_w = 1.15 * extra_cw   # extra weighted in-eq tokens vs a warm-cache first turn (cw 1.25 - cr 0.1)
                extra_usd = extra_cw * (PRICE[family]["cw5"] - PRICE[family]["cr"]) / 1e6
                row.update({"wake_utc": __import__("datetime").datetime.fromtimestamp(w, __import__("datetime").timezone.utc).strftime("%H:%M:%S"),
                            "gap_s": round(gap, 1) if gap is not None else "",
                            "first_turn_cw": u0["cw"], "first_turn_cr": u0["cr"], "ctx_first_turn": ctx0,
                            "first_turn_cw_share_of_ctx": round(u0["cw"] / ctx0, 3) if ctx0 else "",
                            "extra_cw_vs_warm": extra_cw, "extra_weighted_in_eq": round(counterfactual_w),
                            "extra_usd_vs_warm": round(extra_usd, 4),
                            "segment_weighted_in_eq": round(weighted(agg)), "segment_usd": round(usd(agg, family, one_h), 4)})
            seg_rows.append(row)
        # stop (limit) rows
        for (tl, kind, summ) in lim:
            segs_before = [k for k in sorted(segs) if k == 0]
            # resume: the first parent "Resuming agent" result at/after the notice
            rs = sorted(r for r in resumes.get((fl["session"], rid), []) if r >= tl - 1)
            r0 = rs[0] if rs else None
            n_seg1 = len(segs.get(0, []))
            last_seg1_rec = max([x for x in stamps if r0 is None or x < r0 - 1.0] or [stamps[0]])
            stop_rows.append({"name": name, "run_id": rid[:9], "notice_utc": __import__("datetime").datetime.fromtimestamp(tl, __import__("datetime").timezone.utc).strftime("%H:%M:%S.%f")[:-3],
                              "resume_sent_utc": __import__("datetime").datetime.fromtimestamp(r0, __import__("datetime").timezone.utc).strftime("%H:%M:%S.%f")[:-3] if r0 else "none by snapshot",
                              "stranded_s_notice_to_resume": round(r0 - tl, 1) if r0 else "",
                              "last_agent_record_to_resume_s": round(r0 - last_seg1_rec, 1) if r0 else "",
                              "turns_before_stop": n_seg1, "turns_after_resume": len(mids) - n_seg1, "summary": summ})
            # what the PI spent on noticing: PI assistant turns between notice and the resume result
            if r0:
                win = [x for x in pi_msgs[fl["session"]] if tl - 0.5 <= x[0] <= r0 + 0.5]
                agg = collections.Counter()
                for x in win:
                    for kk, v in x[1].items():
                        agg[kk] += v
                notice_rows.append({"name": name, "pi_turns_in_window": len(win), "pi_tools": ";".join(t for x in win for t in x[3]),
                                    "pi_cache_read": agg["cr"], "pi_cache_write": agg["cw"], "pi_out_recorded": agg["out"],
                                    "pi_usd_list_opus_1h": round(usd(agg, "opus", True), 4)})

    # ---- distributions ------------------------------------------------------------------------------
    def grp(r):
        if r["group"] == "this_run":
            at = r["agent_type"].split(":")[-1]
            return "this run: %s (%s)" % (at, "final" if r["status"].startswith(("finished", "limit")) else "in flight at snapshot")
        return "%s: %s workers (%s)" % (r["group"], r["role_analogue"], "sonnet" if "sonnet" in r["model"] else r["model"].replace("claude-", ""))
    buckets = collections.defaultdict(list)
    for r in run_rows:
        buckets[grp(r)].append(r)
    dist_rows = []
    for g in sorted(buckets):
        ts_ = [r["turns"] for r in buckets[g]]
        dist_rows.append({"group": g, "n": len(ts_), "min": min(ts_), "p25": pct(ts_, .25), "median": pct(ts_, .5), "p75": pct(ts_, .75),
                          "p90": pct(ts_, .9), "max": max(ts_), "n_ge_60": sum(t >= 60 for t in ts_), "n_gt_60": sum(t > 60 for t in ts_),
                          "n_ge_80": sum(t >= 80 for t in ts_), "n_ge_100": sum(t >= 100 for t in ts_),
                          "turns_list": " ".join(map(str, sorted(ts_))),
                          "max_single_segment": max(max(int(x) for x in r["turns_per_segment"].split("/")) for r in buckets[g]),
                          "n_runs_with_a_segment_gt_60": sum(max(int(x) for x in r["turns_per_segment"].split("/")) > 60 for r in buckets[g]),
                          "per_segment_lists": " ".join(r["turns_per_segment"] for r in sorted(buckets[g], key=lambda r: r["turns"]))})
    # pooled Sonnet runs without a limit (genesis + design general-purpose, excluding <=6-turn probes)
    pool = [r["turns"] for r in run_rows if r["group"] in ("genesis", "design") and "sonnet" in r["model"] and r["turns"] > 6]
    if pool:
        dist_rows.append({"group": "POOLED genesis+design sonnet workers, >6 turns (no limit)", "n": len(pool), "min": min(pool), "p25": pct(pool, .25),
                          "median": pct(pool, .5), "p75": pct(pool, .75), "p90": pct(pool, .9), "max": max(pool),
                          "n_ge_60": sum(t >= 60 for t in pool), "n_gt_60": sum(t > 60 for t in pool), "n_ge_80": sum(t >= 80 for t in pool),
                          "n_ge_100": sum(t >= 100 for t in pool), "turns_list": " ".join(map(str, sorted(pool)))})

    # share of cost after turn 60 / 80 in the unlimited runs that went past it
    tail_rows = []
    byrun = collections.defaultdict(list)
    for c in cost_rows:
        byrun[(c["group"], c["run_id"], c["name"])].append(c)
    for key, cs in byrun.items():
        n = len(cs)
        tot = cs[-1]["cum_usd"]
        if key[0] != "this_run" and n > 60 and tot > 0:
            at60 = cs[59]["cum_usd"]
            at80 = cs[79]["cum_usd"] if n > 80 else None
            tail_rows.append({"group": key[0], "run_id": key[1], "turns": n, "usd_total": tot, "usd_after_turn_60": round(tot - at60, 3),
                              "share_after_60": round((tot - at60) / tot, 3), "share_after_80": round((tot - at80) / tot, 3) if at80 else ""})

    def dump(name, rows):
        if not rows:
            open(os.path.join(out, name), "w").write("")
            return
        keys = []
        for r in rows:
            for k in r:
                if k not in keys:
                    keys.append(k)
        with open(os.path.join(out, name), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)

    dump("runs_turns.csv", sorted(run_rows, key=lambda r: (r["group"], r["name"], r["run_id"])))
    dump("segments.csv", seg_rows)
    dump("stops.csv", stop_rows)
    dump("pi_notice.csv", notice_rows)
    dump("turn_dist.csv", dist_rows)
    dump("cost_by_turn.csv", cost_rows)
    dump("first_write.csv", fw_rows)
    dump("cost_after_60.csv", tail_rows)

    # ---- resume cost against the gap (all resumed runs) and the cost of each limit stop -----------------------
    rg = [dict(r) for r in seg_rows if r["segment"] != 0 and r.get("gap_s") != ""]
    for r in rg:
        r["gap_s"] = float(r["gap_s"])
        r["cache_state"] = "cold (re-written)" if float(r["first_turn_cw_share_of_ctx"]) > 0.5 else "warm"
    rg.sort(key=lambda r: r["gap_s"])
    cols = ("group", "run_id", "name", "segment", "gap_s", "ctx_first_turn", "first_turn_cw", "first_turn_cr",
            "first_turn_cw_share_of_ctx", "cache_state", "extra_cw_vs_warm", "extra_usd_vs_warm")
    dump("resume_vs_gap.csv", [{k: r.get(k, "") for k in cols} for r in rg])
    runs_by = {r["run_id"]: r for r in run_rows}
    notice_by = {r["name"]: r for r in notice_rows}
    seg_by = {(r["run_id"], r["segment"]): r for r in seg_rows}
    sc = []
    for st in stop_rows:
        rr = runs_by[st["run_id"]]
        sg = seg_by.get((st["run_id"], 1), {})
        nt = notice_by.get(st["name"], {})
        ctx = int(sg.get("ctx_first_turn") or 0)
        sc.append({"name": st["name"], "turns_total": rr["turns"], "run_usd_list": rr["usd_list"],
                   "stranded_s": st["stranded_s_notice_to_resume"],
                   "extra_cache_write_usd_measured": sg.get("extra_usd_vs_warm", ""),
                   "pi_notice_usd_opus_list": nt.get("pi_usd_list_opus_1h", ""),
                   "pi_turns": nt.get("pi_turns_in_window", ""), "wrapup_turns_after_resume": st["turns_after_resume"],
                   "wrapup_segment_usd": sg.get("segment_usd", ""),
                   "exposure_if_cold_usd": round(ctx * (PRICE["sonnet"]["cw5"] - PRICE["sonnet"]["cr"]) / 1e6, 3),
                   "usd_per_extra_turn_at_turn60_ctx": round(ctx * PRICE["sonnet"]["cr"] / 1e6, 3)})
    dump("stop_cost.csv", sc)

    # ---- mean cost of a turn by turn band (Sonnet runs, any group; a run contributes to a band it reached) -----
    bands = [(1, 20), (21, 40), (41, 60), (61, 80), (81, 110)]
    band_rows = []
    sonnet_runs = {(r["group"], r["run_id"]) for r in run_rows if "sonnet" in r["model"] and r["turns"] > 6}
    for lo, hi in bands:
        xs = [c for c in cost_rows if (c["group"], c["run_id"]) in sonnet_runs and lo <= c["turn"] <= hi]
        if xs:
            band_rows.append({"turn_band": "%d-%d" % (lo, hi), "runs_reaching_band": len({(c["group"], c["run_id"]) for c in xs}),
                              "turns": len(xs), "mean_turn_usd": round(sum(c["turn_usd"] for c in xs) / len(xs), 4),
                              "mean_ctx_tokens": round(sum(c["ctx_tokens"] for c in xs) / len(xs))})
    dump("cost_by_turn_band.csv", band_rows)

    # ---- how fast does the PI's main thread react to a worker notification? (first sighting -> next PI assistant message)
    lat = []
    seen_notice = set()   # a forked session repeats the parent's history: count a (task id, kind, timestamp) once, in the earliest session
    for (sess, tid), lst in sorted(notif.items(), key=lambda kv: next(f["gi"] for f in files if f["session"] == kv[0][0] and f["kind"] == "main")):
        for (tn, kind, summ) in lst:
            if tn is None or tn > T:
                continue
            if (tid, kind, round(tn, 1)) in seen_notice:
                continue
            seen_notice.add((tid, kind, round(tn, 1)))
            if (sess, tid) not in launched:   # worker notices only: skip background-shell notices
                continue
            nxt = [x[0] for x in pi_msgs.get(sess, []) if tn + 0.2 < x[0] <= T]   # reaction must also lie inside the snapshot
            if nxt:
                grp_ = next((f["group"] for f in files if f["session"] == sess and f["kind"] == "main"), "")
                lat.append({"group": grp_, "task": tid[:9], "kind": kind, "notice_ts": round(tn, 1),
                            "latency_to_next_pi_message_s": round(nxt[0] - tn, 1)})
    lat.sort(key=lambda r: (r["group"], r["notice_ts"]))
    dump("pi_reaction_latency.csv", lat)
    for g in sorted({r["group"] for r in lat}):
        xs = [r["latency_to_next_pi_message_s"] for r in lat if r["group"] == g]
        print("PI reaction latency", g, "n", len(xs), "median", pct(xs, .5), "p90", pct(xs, .9), "max", max(xs), "n>300s", sum(x > 300 for x in xs))
    with open(os.path.join(out, "summary.txt"), "w") as fh:
        fh.write("snapshot (--until): %s   quick=%s   runs=%d\n" % (until, quick, len(run_rows)))
        for r in dist_rows:
            fh.write(json.dumps(r) + "\n")
    print("snapshot", until, "quick", quick, "runs", len(run_rows), "segments", len(seg_rows), "stops", len(stop_rows), "->", out)


if __name__ == "__main__":
    main(sys.argv[1:])
