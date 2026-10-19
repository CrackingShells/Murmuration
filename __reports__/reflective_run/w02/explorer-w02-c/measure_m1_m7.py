#!/usr/bin/env python3
"""Wave 2, phase C: measure M1-M7 of __reports__/reflective_run/w02/00-experiment_protocol_v0.md for both arms.

Read-only on all data. Run:  python3 -I measure_m1_m7.py [SCRATCH_DIR] > output_table.md
SCRATCH_DIR holds A/ and B/ (default: the PI's scratchpad, w02/expC). Transcripts are read from ~/.claude/projects.
Prints markdown tables only; no transcript text is copied (only counts, ids of the lab's own agents, and lab file names).
Why plain python: the objects are JSONL transcripts and small text files; nothing needs a library.
"""
import ast
import collections
import datetime
import glob
import importlib.util
import itertools
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else (
    "/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/"
    "ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/w02/expC")
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
CHARS_PER_TOKEN = 1.3   # budget.py's estimate of content characters per output token

spec = importlib.util.spec_from_file_location("lab_status_mod", os.path.join(WT, "scripts", "lab_status.py"))
LS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LS)   # PRICES and message_usd: the prices lab_status.py uses


def out(s=""):
    print(s)


def table(header, rows):
    out("| " + " | ".join(header) + " |")
    out("|" + "|".join(":--" if i == 0 else "--:" if all(isinstance(r[i], (int, float)) for r in rows) else ":--"
                      for i in range(len(header))) + "|")
    for r in rows:
        out("| " + " | ".join(fmt(x) for x in r) + " |")
    out()


def fmt(x):
    if isinstance(x, float):
        return "%.4f" % x if abs(x) < 10 else "%.2f" % x
    return str(x)


def iso(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def jl(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except ValueError:
                    pass


# ------------------------------------------------------------------ arm loading
def load_arm(arm):
    lab = os.path.join(SCRATCH, arm, "lab")
    tdir = glob.glob(os.path.join(PROJECTS, "*expC-%s-lab" % arm))
    assert len(tdir) == 1, tdir
    tdir = tdir[0]
    mains = [p for p in glob.glob(os.path.join(tdir, "*.jsonl"))]
    assert len(mains) == 1
    a = dict(arm=arm, lab=lab, plugin=os.path.join(SCRATCH, arm, "plugin"), main=mains[0], tdir=tdir,
             start=int(open(os.path.join(SCRATCH, arm, "start.txt")).read()),
             end=int(open(os.path.join(SCRATCH, arm, "end.txt")).read()),
             exit=open(os.path.join(SCRATCH, arm, "exit.txt")).read().strip(),
             stdout=os.path.join(SCRATCH, arm, "stdout.jsonl"), stderr=open(os.path.join(SCRATCH, arm, "stderr.txt")).read())
    a["agents"] = []
    for p in sorted(glob.glob(os.path.join(tdir, "*", "subagents", "agent-*.jsonl"))):
        meta = json.load(open(p[:-6] + ".meta.json"))
        a["agents"].append(dict(path=p, aid=os.path.basename(p)[6:-6], type=meta.get("agentType"),
                                name=meta.get("name") or ("%s-%s" % (meta.get("agentType"), os.path.basename(p)[6:14])),
                                finished=meta.get("finished"), desc=meta.get("description")))
    return a


def att(e):
    """The attachment dict of a transcript record (a dict in the file; parsed if a string)."""
    a = e.get("attachment")
    if isinstance(a, str):
        try:
            a = ast.literal_eval(a)
        except Exception:
            a = {}
    return a if isinstance(a, dict) else {}


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def block_text(b):
    return json.dumps(b["input"], sort_keys=True) if "input" in b else str(b.get("text") or b.get("thinking") or "")


def scan_agent(ag):
    """One subagent transcript: requests in order, hand-back points, writes, errors, first request, times."""
    reqs, order = {}, []
    hb_points, hb_msgs, writes, errs, times, write_t, mention_t = [], [], [], [], [], [], []
    uses, brief, first_req = {}, None, None
    n_user_text = 0
    for e in jl(ag["path"]):
        if e.get("timestamp"):
            times.append(iso(e["timestamp"]))
        if e["type"] == "user":
            c = e["message"].get("content")
            if brief is None and not e.get("isMeta"):
                brief = text_of(c)
            if isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_result" and b.get("is_error"):
                        errs.append((uses.get(b["tool_use_id"], ("?", ""))[0], str(b.get("content"))[:80].replace("\n", " ")))
        if e["type"] != "assistant":
            continue
        m = e["message"]
        use = m.get("usage")
        if not isinstance(use, dict):
            continue
        key = e.get("requestId") or m.get("id") or e.get("uuid")
        if key not in reqs:
            reqs[key] = dict(model=m.get("model"), use={}, blocks=set(), t=iso(e["timestamp"]))
            order.append(key)
        r = reqs[key]
        LS.merge_usage(r["use"], use)
        for f in ("cache_creation",):
            if isinstance(use.get(f), dict):
                r["use"][f] = use[f]
        r["blocks"].update(block_text(b) for b in m.get("content") or [] if isinstance(b, dict))
        for b in m.get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                uses[b["id"]] = (b["name"], b["input"])
                if b["name"] == "SubagentHandback":
                    hb_points.append((key, iso(e["timestamp"])))
                    hb_msgs.append(len(str((b["input"] or {}).get("message", ""))))
                if b["name"] != "Read" and "findings_v0" in json.dumps(b["input"]):
                    mention_t.append((iso(e["timestamp"]), b["name"]))
                if b["name"] in ("Write", "Edit"):
                    writes.append(b["input"].get("file_path", ""))
                    write_t.append((iso(e["timestamp"]), b["input"].get("file_path", ""), b["name"]))
                if b["name"] == "Bash":
                    for mm in re.finditer(r"(?:>>?|tee)\s+(\S+\.(?:md|c|py|txt|csv|json|sh))", b["input"].get("command", "")):
                        writes.append("bash>" + mm.group(1))
                        write_t.append((iso(e["timestamp"]), mm.group(1), "Bash"))
    if order:
        k0 = order[0]
        u = reqs[k0]["use"]
        first_req = (int(u.get("input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0),
                     int(u.get("cache_creation_input_tokens") or 0))
    ag.update(mention_t=mention_t, write_t=write_t, reqs=reqs, order=order, hb_points=hb_points, hb_msgs=hb_msgs, writes=writes, errs=errs, brief=brief or "",
              first_req=first_req, t0=min(times) if times else None, t1=max(times) if times else None)
    return ag


def usd_upto(ag, upto_idx, estimate):
    """USD at list price of requests order[0..upto_idx] (inclusive); output as recorded or max(recorded, chars/1.3)."""
    tot = 0.0
    for k in ag["order"][:upto_idx + 1]:
        r = ag["reqs"][k]
        use = dict(r["use"])
        if estimate:
            est = int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN)
            use["output_tokens"] = max(int(use.get("output_tokens") or 0), est)
        v = LS.message_usd(r["model"], use)
        tot += v or 0.0
    return tot


def runs_of(ag):
    """Per hand-back run: cumulative-spend differences. Returns list of dict(rec, est, out_rec, out_est)."""
    idx = {k: i for i, k in enumerate(ag["order"])}
    res, prev_rec, prev_est = [], 0.0, 0.0
    for (k, t), nbytes in zip(ag["hb_points"], ag["hb_msgs"]):
        i = idx[k]
        rec, est = usd_upto(ag, i, False), usd_upto(ag, i, True)
        res.append(dict(rec=rec - prev_rec, est=est - prev_est, t=t, bytes=nbytes))
        prev_rec, prev_est = rec, est
    return res


def recorded_output_tokens(ags):
    return sum(int(r["use"].get("output_tokens") or 0) for ag in ags for r in ag["reqs"].values())


def est_output_tokens(ags):
    return sum(max(int(r["use"].get("output_tokens") or 0), int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN))
               for ag in ags for r in ag["reqs"].values())


# ------------------------------------------------------------------ main thread
def main_info(a):
    cost, last_ts, first_ts, n_asst = None, 0, None, 0
    for e in jl(a["main"]):
        if e.get("type") == "cost-state":
            cost = e
        if e.get("timestamp"):
            t = iso(e["timestamp"])
            first_ts = first_ts or t
            last_ts = max(last_ts, t)
        if e.get("type") == "assistant":
            n_asst += 1
    res = [e for e in jl(a["stdout"]) if e.get("type") == "result" and e.get("total_cost_usd") is not None]
    a.update(cost_state=cost, result_events=res, main_first=first_ts, main_last=last_ts)
    return a


def lab_status_text(a, *flags):
    r = subprocess.run([sys.executable, "-I", os.path.join(WT, "scripts", "lab_status.py"), *flags, "--project", a["lab"]],
                       capture_output=True, text=True, cwd=WT)
    return r.stdout


# ------------------------------------------------------------------ M6 brute force
def brute(nmax):
    """For n <= nmax: max distinct non-empty substrings, count of maximisers, list of maximisers (n <= 14),
    and each string's D(s). Returns dict n -> (max, count, dict s->D) (strings kept as ints for n<=nmax)."""
    res = {}
    for n in range(1, nmax + 1):
        Ds = {}
        best, cnt = -1, 0
        for v in range(1 << n):
            s = format(v, "0%db" % n)
            seen = set()
            for i in range(n):
                for j in range(i + 1, n + 1):
                    seen.add(s[i:j])
            d = len(seen)
            Ds[s] = d
            if d > best:
                best, cnt = d, 1
            elif d == best:
                cnt += 1
        res[n] = (best, cnt, Ds)
    return res


def F_sum(n):
    # for k > 60, 2^k exceeds any n used here, so the term is n-k+1 (an arithmetic series)
    head = sum(min(2 ** k, n - k + 1) for k in range(1, min(n, 60) + 1))
    tail = sum(n - k + 1 for k in range(61, n + 1)) if n > 60 else 0
    return head + tail


def K_of_A(n):   # w01-c1 of arm A: K = min{k >= 1 : 2^k >= n-k+1}
    k = 1
    while 2 ** k < n - k + 1:
        k += 1
    return k


def m_of_B(n):   # synthesis of arm B: m = largest k >= 0 with 2^k + k - 1 <= n
    k = 0
    while 2 ** (k + 1) + (k + 1) - 1 <= n:
        k += 1
    return k


def B_closed(n):
    m = m_of_B(n)
    return 2 ** (m + 1) - 2 + (n - m) * (n - m + 1) // 2


def windows_distinct(s, L):
    w = [s[i:i + L] for i in range(len(s) - L + 1)]
    return len(set(w)) == len(w)


def all_words(s, L):
    return len({s[i:i + L] for i in range(len(s) - L + 1)}) == 2 ** L


def crit_A(s):
    n = len(s)
    K = K_of_A(n)
    return all_words(s, K - 1) and windows_distinct(s, K)


def crit_B(s):
    n = len(s)
    m = m_of_B(n)
    return all_words(s, m) and windows_distinct(s, m + 1)


# ------------------------------------------------------------------ B2-specific
def run_intervals(ag):
    """(start, hand-back time) of each run: a run starts at the first record, or at the first text user message after a hand-back."""
    out_, start, pending = [], None, False
    for e in jl(ag["path"]):
        if not e.get("timestamp"):
            continue
        t = iso(e["timestamp"])
        if start is None:
            start = t
        if e["type"] == "user" and pending and not e.get("isMeta"):
            c = e["message"].get("content")
            if isinstance(c, str) or any(isinstance(b, dict) and b.get("type") != "tool_result" for b in c or []):
                start, pending = t, False
        if e["type"] == "assistant":
            for b in e["message"].get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b["name"] == "SubagentHandback":
                    out_.append((start, t))
                    pending = True
    return out_


def pi_gaps(a):
    """PI turn ends in the main transcript (assistant message without a tool call) and the idle time until the next PI message,
    with the worker runs active at the end of the turn and 600 s later."""
    msgs = {}
    for e in jl(a["main"]):
        if e["type"] == "assistant" and e.get("timestamp"):
            m = e["message"]
            cur = msgs.setdefault(m.get("id") or e["uuid"], dict(t=iso(e["timestamp"]), tool=False, t0=iso(e["timestamp"])))
            cur["t"] = max(cur["t"], iso(e["timestamp"]))
            cur["tool"] = cur["tool"] or any(isinstance(b, dict) and b.get("type") == "tool_use" for b in m.get("content") or [])
    seq = sorted(msgs.values(), key=lambda x: x["t0"])
    runs = []
    for g in a["workers"]:
        if g["hb_points"]:
            runs += run_intervals(g)
        else:
            runs.append((g["t0"], g["t1"] if g["finished"] else float("inf")))
    gaps = []
    for i, m in enumerate(seq):
        if m["tool"]:
            continue
        nxt = seq[i + 1]["t0"] if i + 1 < len(seq) else float(a["end"])
        gap = nxt - m["t"]
        alive0 = sum(1 for (s0, s1) in runs if s0 <= m["t"] < s1)
        alive600 = sum(1 for (s0, s1) in runs if s0 <= m["t"] + 600 < s1) if gap >= 600 else None
        gaps.append(dict(t=m["t"] - a["start"], gap=gap, alive0=alive0, alive600=alive600, last=i + 1 >= len(seq)))
    return gaps


def b2_section(A, B, B2, bf, ev):
    out("## Arm B2 (candidate plus time budget; `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` per the protocol addendum [assumption: the variable is not recorded in any file I can read])")
    out()
    hp = os.path.join(B2["lab"], "__statera__", "harness.jsonl")
    H = [json.loads(l) for l in open(hp) if l.strip()]
    ev2 = collections.Counter(h["event"] for h in H)
    out("B2 harness log events: %s. Events of kind note/stop/halt/deny: %d. stderr.txt: %r; exit code %s." % (
        dict(ev2), sum(ev2.get(k, 0) for k in ("note", "stop", "halt", "deny")), B2["stderr"], B2["exit"]))
    out()
    # M3 for B2 explorers
    tpl = open(os.path.join(B2["plugin"], "skills", "research-loop", "templates", "report_findings.md")).read()
    tpl_h2 = re.findall(r"^## (.+)$", tpl, re.M)
    tpl_keys = re.findall(r"^([a-z-]+): ", tpl.split("---")[1], re.M)
    rows = []
    for ag in sorted(B2["workers"], key=lambda g: g["t0"]):
        if B2["role"][ag["aid"]] != "explorer":
            continue
        wave = re.sub(r"^.*?-w0(\d)-.*$", r"wave-0\1", ag["name"])
        path = os.path.join("__reports__", wave, ag["name"], "00-findings_v0.md")
        full = os.path.join(B2["lab"], path)
        if not os.path.exists(full):
            rows.append((ag["name"], path, "MISSING", "-", "-", "-"))
            continue
        txt = open(full).read()
        fm = re.match(r"---\n(.*?)\n---\n", txt, re.S)
        keys = re.findall(r"^([a-z-]+):", fm.group(1), re.M) if fm else []
        h2 = re.findall(r"^## (.+)$", txt, re.M)
        it = iter(h2)
        in_order = all(any(x == h for h in it) for x in tpl_h2)
        extras_ = [h for h in h2 if h not in tpl_h2]
        first_hb = ag["hb_points"][0][1] if ag["hb_points"] else None
        m0 = ag["mention_t"][0][0] if ag["mention_t"] else None
        rows.append((ag["name"], path, "yes", "yes" if keys == tpl_keys else "NO %s" % keys,
                     "exact" if h2 == tpl_h2 else ("in order, extra: %s" % extras_ if in_order else "NOT in order"),
                     "%.1f s before the hand-back" % (first_hb - m0) if m0 and first_hb else "no tool call naming findings_v0 before the hand-back"))
    table(("B2 explorer", "path", "at convention path", "front-matter keys as template", "six h2 headings", "report written"), rows)
    # hand-backs saved
    HEAD = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) status=(\S+) bytes=(\d+)", re.M)
    sec = collections.defaultdict(list)
    for p in glob.glob(os.path.join(B2["lab"], "__statera__", "handbacks", "*.md")):
        for mm in HEAD.finditer(open(p, "rb").read()):
            sec[mm.group(3).decode()].append(mm.group(6).decode())
    out("B2 hand-back calls (murmuration workers) %d, (all agents) %d; sections saved %d; statuses %s." % (
        sum(len(g["hb_points"]) for g in B2["workers"]), sum(len(g["hb_points"]) for g in B2["agents"]),
        sum(len(v) for v in sec.values()), dict(collections.Counter(itertools.chain(*sec.values())))))
    out()
    # M4 with t_frac
    out("### M4 for B2: USD and time fractions at hand-back (log values; `which` is the budget that decided)")
    out()
    BRIEF = re.compile(r"^Budget: USD (\d+(?:\.\d+)?)[ \t]*$", re.M)
    TLINE = re.compile(r"^Time: min (\d+(?:\.\d+)?)[ \t]*$", re.M)
    ags = {g["aid"]: g for g in B2["agents"]}
    ends = [h for h in H if h["event"] == "end"]
    rows = []
    for aid in {h["agent_id"] for h in ends}:
        hs = [h for h in ends if h["agent_id"] == aid]
        ag = ags[aid]
        runs, iv = runs_of(ag), run_intervals(ag)
        bl, tl = BRIEF.search(ag["brief"]), TLINE.search(ag["brief"])
        for i, (h, r, (t0_, t1_)) in enumerate(zip(hs, runs, iv)):
            rows.append((h["name"], h["type"].split(":")[1], i + 1, h["B"], bl.group(1) if bl else "-", h["T"], tl.group(1) if tl else "-",
                         h["frac"], r["est"] / h["B"], h["t_frac"], (t1_ - t0_) / 60.0 / h["T"], h["elapsed_s"], h["which"], h["noted"], h["stops"]))
    rows.sort(key=lambda x: -x[9])
    table(("agent", "role", "run", "B USD", "brief Budget line", "T min", "brief Time line", "frac (USD, log)", "frac (own, est. output)",
           "t_frac (log)", "t_frac (own, first record to hand-back)", "elapsed_s (log)", "which", "noted", "stops"), rows)
    out("Max over runs: USD frac %.3f, t_frac %.3f (note at 0.8, notice at 1.0). Runs %d; start lines %d; end lines %d. Notes/stops: none." % (
        max(r[7] for r in rows), max(r[9] for r in rows), len(rows), ev2.get("start", 0), ev2.get("end", 0)))
    n_start_time = 0
    for g in B2["agents"]:
        for e in jl(g["path"]):
            if e["type"] == "attachment":
                at = att(e)
                if at.get("type") == "hook_additional_context" and any("your budget for this run" in str(c) and "minutes of wall time" in str(c) for c in at.get("content", [])):
                    n_start_time += 1
                    break
    out("Start notes that name both budgets (USD and minutes): %d of %d B2 agent files (the other is the built-in web-fetch agent)." % (n_start_time, len(B2["agents"])))
    out()
    out("Counterfactual: wall time of each run (first record to hand-back, minutes) in A and B against the default T (explorer/author 20, reproducer/proof-adversary 15), runs above 0.5 T:")
    out()
    rows = []
    for a in (A, B, B2):
        for g in a["workers"]:
            role = a["role"][g["aid"]]
            T = 20.0 if role in ("explorer", "author") else 15.0
            ivs = run_intervals(g) if g["hb_points"] else [(g["t0"], g["t1"])]
            for i, (s0, s1) in enumerate(ivs):
                if (s1 - s0) / 60.0 / T >= 0.5:
                    rows.append((a["arm"], g["name"], i + 1, round((s1 - s0) / 60.0, 1), T, round((s1 - s0) / 60.0 / T, 2), "yes" if g["hb_points"] else "no hand-back (killed)"))
    table(("arm", "agent", "run", "minutes", "default T", "minutes / T", "handed back"), rows)

    out("### Ceiling: was any worker still running 10 minutes after a PI turn ended?")
    out()
    rows = []
    for a in (A, B, B2):
        gaps = pi_gaps(a)
        long_ = [g for g in gaps if g["gap"] >= 600]
        needed = [g for g in long_ if g["alive600"]]
        top = sorted(gaps, key=lambda g: -g["gap"])[:3]
        nbg = sum(1 for e in jl(a["stdout"]) if e.get("type") == "system" and e.get("subtype") == "task_started"
                  and e.get("task_type") == "local_bash" and e.get("is_backgrounded"))
        rows.append((a["arm"], len(gaps), nbg, "; ".join("%.0f s at %.0f s (%d workers active at turn end)" % (g["gap"], g["t"], g["alive0"]) for g in top),
                     len(long_), len(needed), "Background tasks still running 10m" in a["stderr"]))
    table(("arm", "PI turn ends", "PI background shell tasks (task_started local_bash, backgrounded)", "three longest idle gaps (turn end to next PI message or process exit)", "gaps >= 600 s",
           "gaps >= 600 s with a worker run still active 600 s after the turn end", "stderr has the 'stopping them' line"), rows)
    out("Reading: a worker is 'running' from its first record (or the first message after a hand-back) to its hand-back; no PI message inside the gap means no wake-up (a finished worker wakes the PI). Background shell commands of the PI are not counted as workers.")
    out()
    # per-turn-end list for B2
    rows = [(round(g["t"]), round(g["gap"]), g["alive0"], g["alive600"] if g["alive600"] is not None else "-", "final" if g["last"] else "") for g in pi_gaps(B2)]
    out("All B2 PI turn ends (seconds after start, idle gap to the next PI message, workers active at the turn end):")
    out()
    table(("turn end s", "idle gap s", "workers active", "active 600 s later", "note"), rows)


# ------------------------------------------------------------------ report
def main():
    A, B, B2 = load_arm("A"), load_arm("B"), load_arm("B2")
    arms = (A, B, B2)
    for a in arms:
        main_info(a)
        a["agents"] = [scan_agent(ag) for ag in a["agents"]]
        a["workers"] = [ag for ag in a["agents"] if (ag["type"] or "").startswith("murmuration:")]
        a["role"] = {ag["aid"]: ag["type"].split(":")[1] for ag in a["workers"]}

    out("# Wave 2, phase C: M1-M7 for arms A (shipped), B (candidate) and B2 (candidate plus time budget, ceiling setting)")
    out()
    out("Generated by `python3 -I measure_m1_m7.py`. Data read only. n = 1 per arm. Sections below cover A and B (and B2 where the loops run over all arms); section \"Arm B2\" at the end holds what is specific to B2. In sections written before B2 existed, \"B\" in a column header means arm B.")
    out()

    # ---------------------------------------------------------------- M1
    out("## M1: total USD")
    out()
    rows = []
    for a in arms:
        cs = a["cost_state"]
        resu = a["result_events"]
        rows.append((a["arm"], cs["totalCostUSD"] if cs else None, resu[-1]["total_cost_usd"] if resu else None,
                     len(resu), "yes" if cs and abs(cs["totalCostUSD"] - resu[-1]["total_cost_usd"]) < 1e-9 else "NO"))
    table(("arm", "cost-state totalCostUSD", "result event total_cost_usd (last)", "result events", "equal"), rows)
    rows = []
    for a in arms:
        for mdl, v in a["cost_state"]["modelUsage"].items():
            rows.append((a["arm"], mdl, v["costUSD"], v["inputTokens"], v["outputTokens"], v["cacheReadInputTokens"],
                         v["cacheCreationInputTokens"]))
    table(("arm", "model", "cost-state costUSD", "input", "output", "cache read", "cache write"), rows)

    out("### `lab_status.py --spend --project <lab>` against cost-state (script: this worktree's `scripts/lab_status.py` at HEAD, for all three arms")
    out()
    rows = []
    for a in arms:
        txt = lab_status_text(a, "--spend")
        tot = re.search(r"^TOTAL\s+USD ([\d.]+)\s+\((.*?)\)", txt, re.M)
        add = re.search(r"add up to ([\d.]+) of the ([\d.]+) total", txt)
        main_row = re.search(r"research-pi \(main thread\)\s+(\S+)\s+(\d+)\s+([\d.]+)", txt)
        # own per-agent list price (recorded output), all agents, to name the ones beyond the printed top 11
        own = {ag["name"]: usd_upto(ag, len(ag["order"]) - 1, False) for ag in a["agents"]}
        own_est = {ag["name"]: usd_upto(ag, len(ag["order"]) - 1, True) for ag in a["agents"]}
        a["own"], a["own_est"] = own, own_est
        printed = {}
        for mm in re.finditer(r"^(\S+)\s+sonnet-5-5\s+(\d+)\s+([\d.]+)\+?\s", txt, re.M):
            printed[mm.group(1)] = float(mm.group(3))
        a["printed"] = printed
        sub_sum = float(add.group(1)) - float(main_row.group(3)) if add else None
        cs = a["cost_state"]["modelUsage"]
        non_main = cs["claude-sonnet-5-5"]["costUSD"] + cs["claude-haiku-5-5"]["costUSD"]
        rows.append((a["arm"], tot.group(1), tot.group(2), main_row.group(3), cs["claude-opus-5-5"]["costUSD"],
                     float(add.group(1)), float(add.group(2)), sub_sum, non_main,
                     (non_main - sub_sum) if sub_sum is not None else None))
    table(("arm", "lab_status TOTAL", "basis", "main row (list)", "cost-state opus", "agent rows add up to", "of total",
           "subagent rows (list)", "cost-state sonnet+haiku", "gap"), rows)
    rows = []
    for a in arms:
        ags = a["agents"]
        sonnet_rec = recorded_output_tokens([g for g in ags])
        cs = a["cost_state"]["modelUsage"]
        gap_out = (cs["claude-sonnet-5-5"]["outputTokens"] - sonnet_rec)
        rows.append((a["arm"], cs["claude-sonnet-5-5"]["outputTokens"], sonnet_rec, est_output_tokens(ags),
                     gap_out, gap_out * LS.PRICES["claude-sonnet-5-5"][1] / 1e6, cs["claude-haiku-5-5"]["costUSD"],
                     sum(a["own"].values()), sum(a["own_est"].values())))
    table(("arm", "sonnet output tokens, exact (cost-state)", "recorded in agent transcripts", "estimate chars/1.3",
           "exact minus recorded", "USD of that gap at $10/M", "haiku helper USD (web-fetch/search; no transcript rows)",
           "own sum of agent USD (recorded output)", "own sum (estimated output)"), rows)

    # ---------------------------------------------------------------- M7 (part: workers & wall) is printed later; M2 first
    out("## M2: worker runs without a deliverable")
    out()
    harness = []
    hp = os.path.join(B["lab"], "__statera__", "harness.jsonl")
    if os.path.exists(hp):
        harness = [json.loads(l) for l in open(hp) if l.strip()]
    ev = collections.Counter(h["event"] for h in harness)
    out("B harness log events: %s" % dict(ev))
    out()

    def claim_heads(lab):
        heads = {}
        for p in glob.glob(os.path.join(lab, "__pondus__", "*.md")):
            txt = open(p).read()
            cid = os.path.basename(p)[:-3]
            heads[cid] = dict(author=(re.search(r"^author: (\S+)", txt, re.M) or [None, None])[1],
                              verdicts=re.findall(r"^## verdict: (\S+)", txt, re.M))
        return heads

    handback_sections = collections.Counter()
    hdir = os.path.join(B["lab"], "__statera__", "handbacks")
    HEAD = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) status=(\S+) bytes=(\d+)", re.M)
    sec_status = collections.defaultdict(list)
    if os.path.isdir(hdir):
        for p in glob.glob(os.path.join(hdir, "*.md")):
            for mm in HEAD.finditer(open(p, "rb").read()):
                sec_status[mm.group(3).decode()].append(mm.group(6).decode())
    rows = []
    for a in arms:
        heads = claim_heads(a["lab"])
        a["heads"] = heads
        for ag in sorted(a["workers"], key=lambda g: g["t0"]):
            role = a["role"][ag["aid"]]
            nhb = len(ag["hb_points"])
            if role == "author":
                deliv = any(h["author"] == ag["name"] for h in heads.values())
            elif role in ("proof-adversary", "reproducer"):
                deliv = any(ag["name"] in h["verdicts"] for h in heads.values())
            else:
                deliv = None
            if role == "explorer":
                if a["arm"] != "A":
                    deliv = os.path.exists(os.path.join(a["lab"], "__reports__", re.sub(r"^.*?-w0(\d)-.*$", r"wave-0\1", ag["name"]),
                                                       ag["name"], "00-findings_v0.md"))
                else:
                    deliv = bool(nhb)
            reason = ""
            if nhb == 0:
                if ag["finished"]:
                    reason = "no hand-back although finished"
                else:
                    reason = "unfinished at exit"
                    if "Background tasks still running 10m" in a["stderr"] and ag["desc"] and ag["desc"] in a["stderr"]:
                        reason = "killed by the 10-minute background ceiling (stderr.txt names its description)"
            n_asst = len(ag["order"])
            mt = re.search(r"^maxTurns: (\d+)", open(os.path.join(a["plugin"], "agents", role + ".md")).read(), re.M)
            maxturns = mt[1] if mt else "none set"
            refused_write = [e for e in ag["errs"] if e[0] in ("Write", "Edit")]
            refused_other = [e for e in ag["errs"] if "doesn't want to proceed" in e[1] or "Blocked:" in e[1] or "denied" in e[1].lower()]
            rows.append((a["arm"], ag["name"], role, nhb, "yes" if deliv else "NO" if deliv is not None else "n/a",
                         "%d/%s" % (n_asst, maxturns), len(refused_write), len(refused_other), reason or "-"))
    table(("arm", "agent", "role", "hand-backs", "deliverable in lab files", "requests/maxTurns", "refused Write/Edit",
           "other blocked/rejected tool calls", "why no deliverable"), rows)

    for a in arms:
        ids = {g["aid"] for g in a["agents"]}
        c = collections.Counter()
        for e in jl(a["stdout"]):
            if e.get("type") == "system" and e.get("subtype") == "task_notification" and e.get("task_id") in ids:
                c[e.get("status")] += 1
        out("Arm %s: agent task notifications seen by the PI's process (stdout.jsonl), by status: %s (agent files %d)." % (a["arm"], dict(c), len(ids)))
    out()
    out("Hand-back sections saved by the B hook (status per agent id) against hand-back calls in the transcripts:")
    out()
    rows = []
    for ag in sorted(B["agents"], key=lambda g: g["t0"]):
        rows.append((ag["name"], ag["type"], len(ag["hb_points"]), len(sec_status.get(ag["aid"], [])),
                     ",".join(sec_status.get(ag["aid"], [])) or "-"))
    table(("agent", "type", "SubagentHandback calls", "sections in handbacks/", "section statuses"), rows)
    out("Total B hand-back calls: %d (murmuration %d); sections saved: %d; statuses: %s" % (
        sum(len(g["hb_points"]) for g in B["agents"]), sum(len(g["hb_points"]) for g in B["workers"]),
        sum(len(v) for v in sec_status.values()), dict(collections.Counter(itertools.chain(*sec_status.values())))))
    out()

    # ---------------------------------------------------------------- M3
    out("## M3: explorer deliverables")
    out()
    tpl = open(os.path.join(B["plugin"], "skills", "research-loop", "templates", "report_findings.md")).read()
    tpl_h2 = re.findall(r"^## (.+)$", tpl, re.M)
    tpl_keys = re.findall(r"^([a-z-]+): ", tpl.split("---")[1], re.M)
    out("Template headings (in order): %s. Front-matter keys: %s." % (tpl_h2, tpl_keys))
    out()
    rows = []
    for ag in sorted(B["workers"], key=lambda g: g["t0"]):
        if B["role"][ag["aid"]] != "explorer":
            continue
        wave = re.sub(r"^.*?-w0(\d)-.*$", r"wave-0\1", ag["name"])
        path = os.path.join("__reports__", wave, ag["name"], "00-findings_v0.md")
        full = os.path.join(B["lab"], path)
        if not os.path.exists(full):
            rows.append((ag["name"], path, "MISSING", "-", "-", "-", "-"))
            continue
        txt = open(full).read()
        fm = re.match(r"---\n(.*?)\n---\n", txt, re.S)
        keys = re.findall(r"^([a-z-]+):", fm.group(1), re.M) if fm else []
        vals = dict(re.findall(r"^([a-z-]+): (.*)$", fm.group(1), re.M)) if fm else {}
        h2 = re.findall(r"^## (.+)$", txt, re.M)
        it = iter(h2)
        in_order = all(any(x == h for h in it) for x in tpl_h2)
        extras = [h for h in h2 if h not in tpl_h2]
        vals_ok = (vals.get("type") == "findings" and vals.get("wave") == wave and vals.get("author") == ag["name"]
                   and vals.get("version") == "v0" and vals.get("decision-required") in ("none", "confirm", "intervene"))
        rows.append((ag["name"], path, "yes", "yes" if keys == tpl_keys else "NO %s" % keys, vals_ok,
                     "exact" if h2 == tpl_h2 else ("in order, extra: %s" % extras if in_order else "NOT in order"),
                     "yes" if re.search(r"^# .+: findings \(v0\)$", txt, re.M) else "no"))
    table(("explorer (B)", "path", "at convention path", "front-matter keys as template", "values valid", "six h2 headings",
           "title line shape"), rows)
    out("Where explorers of arm A put their output (Write/Edit/redirect targets in the transcript; no template, no convention path in A's explorer file):")
    out()
    rows = []
    for ag in sorted(A["workers"], key=lambda g: g["t0"]):
        if A["role"][ag["aid"]] != "explorer":
            continue
        lab_rel = [w.replace(A["lab"] + "/", "") for w in ag["writes"]]
        rows.append((ag["name"], len(ag["hb_points"]), ", ".join(sorted(set(lab_rel))) or "-"))
    table(("explorer (A)", "hand-backs", "files written"), rows)
    out("A: `__reports__/` exists in lab: %s; B: %s." % (os.path.isdir(os.path.join(A["lab"], "__reports__")),
                                                         os.path.isdir(os.path.join(B["lab"], "__reports__"))))
    out()

    # ---------------------------------------------------------------- M4
    out("## M4: budget notes, stops, denies (arm B only)")
    out()
    out("Defaults in `budget.py` (B per role): explorer 3.0, author 3.0, reproducer 2.0, proof-adversary 2.0 USD; note at 0.8, stop at 1.0, halt at 1.5 after 3 notices. "
        "Harness log events by kind: %s. Events of kind note/stop/halt/deny: %d." % (dict(ev), sum(ev.get(k, 0) for k in ("note", "stop", "halt", "deny"))))
    out()
    rows = []
    ends = [h for h in harness if h["event"] == "end"]
    starts = [h for h in harness if h["event"] == "start"]
    by_agent_ends = collections.defaultdict(list)
    for h in ends:
        by_agent_ends[h["agent_id"]].append(h)
    ag_by_id = {g["aid"]: g for g in B["agents"]}
    BRIEF = re.compile(r"^Budget: USD (\d+(?:\.\d+)?)[ \t]*$", re.M)
    for aid, hs in by_agent_ends.items():
        ag = ag_by_id[aid]
        runs = runs_of(ag)
        bl = BRIEF.search(ag["brief"])
        for i, (h, r) in enumerate(zip(hs, runs)):
            rows.append((h["name"], h["type"].split(":")[1], i + 1, h["B"], bl.group(1) if bl else "none (default)", h["noted"], h["stops"],
                         r["rec"], r["rec"] / h["B"], r["est"], r["est"] / h["B"], h["used_recorded"], h["used"], h["frac"],
                         "n/a (no note or stop fired)"))
    rows.sort(key=lambda x: -x[10])
    table(("agent", "role", "run", "B in the log (USD)", "`Budget: USD` line in the first user message", "noted", "stops",
           "USD at hand-back, recorded output (own, transcript)", "fraction of B", "USD with output estimated chars/1.3 (own)",
           "fraction of B", "harness used_recorded", "harness used", "harness frac", "handed back after the note"), rows)
    out("Max fraction at hand-back: own recorded %.3f, own estimated %.3f, harness %.3f. Runs: %d (harness end lines %d, start lines %d, hand-back calls of murmuration workers %d)."
        % (max(r[8] for r in rows), max(r[10] for r in rows), max(h["frac"] for h in ends), len(rows), len(ends), len(starts),
           sum(len(g["hb_points"]) for g in B["workers"])))
    out()
    exact_out = B["cost_state"]["modelUsage"]["claude-sonnet-5-5"]["outputTokens"]
    out("Output truncation (B, murmuration workers, all on sonnet): output tokens recorded in the worker transcripts %d; estimate chars/1.3 %d; "
        "exact figure (cost-state, sonnet, session level only) %d. Recorded is %.1f%% of exact; the estimate is %.1f%% of exact. "
        "Per-agent exact output is not available anywhere; input and cache tokens per agent are exact."
        % (recorded_output_tokens(B["workers"]), est_output_tokens(B["workers"]), exact_out,
           100.0 * recorded_output_tokens(B["workers"]) / exact_out, 100.0 * est_output_tokens(B["workers"]) / exact_out))
    out()
    n_bl = sum(1 for g in A["workers"] if BRIEF.search(g["brief"]))
    out("Counterfactual for arm A (no hook ran there; %d of %d A briefs carry a `Budget: USD` line, so the hook's role defaults are used): "
        "the same B against A workers' whole-agent-file spend (own, estimated output), six largest:" % (n_bl, len(A["workers"])))
    out()
    rows = []
    for ag in sorted(A["workers"], key=lambda g: -usd_upto(g, len(g["order"]) - 1, True)):
        role = A["role"][ag["aid"]]
        Bd = {"explorer": 3.0, "author": 3.0, "reproducer": 2.0, "proof-adversary": 2.0}[role]
        u = usd_upto(ag, len(ag["order"]) - 1, True)
        rows.append((ag["name"], role, Bd, usd_upto(ag, len(ag["order"]) - 1, False), u, u / Bd))
    table(("A agent", "role", "default B", "USD recorded", "USD estimated", "fraction of B (whole agent file, resumes included)"), rows[:6])
    out("Denies (handback.py) logged in B: %d. Hook-blocking attachments in B transcripts: see below." % ev.get("deny", 0))
    out()
    cnt, notes, start_notes = collections.Counter(), 0, 0
    for ag in B["agents"] + [dict(path=B["main"])]:
        got = False
        for e in jl(ag["path"]):
            if e["type"] == "attachment":
                at = att(e)
                cnt[(("main" if "aid" not in ag else "sub"), at.get("type"))] += 1
                if at.get("type") == "hook_additional_context" and any("your budget for this run" in str(c) for c in at.get("content", [])):
                    got = True
                if at.get("type") == "hook_additional_context" and any("Lab harness note (genuine" in str(c) or "Lab harness (genuine" in str(c) or "Lab harness: your USD" in str(c) for c in at.get("content", [])):
                    notes += 1
        start_notes += got
    out("Hook-decision attachments in B transcripts (hook_blocking_error, hook_stopped_continuation, hook_non_blocking_error, hook_cancelled; main and subagents): %s."
        % ({k: v for k, v in cnt.items() if k[1] in ("hook_blocking_error", "hook_stopped_continuation", "hook_non_blocking_error", "hook_cancelled")} or "none"))
    out("Start notes (`Budget: your budget for this run is ...`) delivered as SubagentStart additional context: %d of %d B agent files (the other file is the built-in web-fetch agent, not a murmuration worker). 80%%-note, stop or halt texts found as additional context in any B transcript: %d." % (
        start_notes, len(B["agents"]), notes))
    out()
    # report written before the first hand-back, per B explorer (deny-once check)
    rows = []
    for ag in sorted(B["workers"], key=lambda g: g["t0"]):
        if B["role"][ag["aid"]] != "explorer":
            continue
        rep_w = ag["mention_t"]
        first_hb = ag["hb_points"][0][1] if ag["hb_points"] else None
        rows.append((ag["name"], len(rep_w), rep_w[0][1] if rep_w else "-", "%.1f" % (first_hb - rep_w[0][0]) if rep_w and first_hb else "-",
                     "yes" if rep_w and first_hb and rep_w[0][0] < first_hb else "NO", len(ag["hb_points"]), ev.get("deny", 0)))
    table(("B explorer", "tool calls (not Read) naming findings_v0", "first via", "seconds from first such call to first hand-back",
           "report existed before the first hand-back (so the pre-hand-back check had nothing to deny)", "hand-back calls", "deny lines in harness.jsonl"), rows)

    # ---------------------------------------------------------------- M5
    out("## M5: the user's words")
    out()
    rows = []
    for a in arms:
        txt = open(os.path.join(a["lab"], "__statera__", "user_words.md")).read()
        entries = re.split(r"^## (?=\d{4}-\d{2}-\d{2} \d{2}:\d{2})", txt, flags=re.M)[1:]
        plat = re.compile(r"<[a-zA-Z/][^>]*>|system-reminder|Base directory for this skill|command-name|hook_|<!--")
        bodies = [e.split("\n", 1)[1].strip() for e in entries]
        rows.append((a["arm"], len(entries), [len(b) for b in bodies], sum(1 for b in bodies if plat.search(b)),
                     "yes" if len(bodies) == 2 and bodies[1].startswith(bodies[0]) else "no"))
    table(("arm", "entries", "chars per entry", "entries with platform text", "entry 2 starts with entry 1 (question repeated)"), rows)

    # ---------------------------------------------------------------- M6
    out("## M6: correctness against brute force, claims, synthesis")
    out()
    NMAX = 16
    bf = brute(NMAX)
    rows = []
    mism = collections.defaultdict(lambda: collections.Counter())
    for n in range(1, NMAX + 1):
        best, cnt, Ds = bf[n]
        ma = mb = 0
        for s, d in Ds.items():
            is_max = d == best
            if crit_A(s) != is_max:
                ma += 1
            if crit_B(s) != is_max:
                mb += 1
        rows.append((n, best, F_sum(n), B_closed(n), "yes" if best == F_sum(n) == B_closed(n) else "NO", cnt,
                     K_of_A(n), ma, m_of_B(n), mb))
    table(("n", "brute-force max D", "sum_k min(2^k,n-k+1)", "B closed form 2^(m+1)-2+(n-m)(n-m+1)/2", "all equal",
           "brute-force N(n) (#maximisers)", "A: K", "A criterion mismatches (over all 2^n strings)", "B: m",
           "B criterion mismatches"), rows)
    out("Mismatch totals for n <= 14 (the protocol's range): A %d, B %d; for n <= 16: A %d, B %d." % (
        sum(r[7] for r in rows if r[0] <= 14), sum(r[9] for r in rows if r[0] <= 14), sum(r[7] for r in rows), sum(r[9] for r in rows)))
    ok = all(B_closed(n) == F_sum(n) for n in range(1, 3001))
    out("B's closed form equals the sum for every n in 1..3000: %s." % ok)
    out()

    # tables of N(n)
    out("Maximiser counts N(n) each arm states, against brute force (n <= %d):" % NMAX)
    out()
    # A: data/exhaustive_w01c3.csv  (n,M,F,A,mismatches)
    a_tab = {}
    for l in open(os.path.join(A["lab"], "data", "exhaustive_w01c3.csv")).read().split("\n")[1:]:
        if l.strip():
            p = l.split(",")
            a_tab[int(p[0])] = (int(p[1]), int(p[3]))
    # B: synthesis list for n = 1..24, and data/derived/exhaustive.csv
    syn = open(os.path.join(B["lab"], "__statera__", "synthesis.md")).read() if os.path.exists(os.path.join(B["lab"], "__statera__", "synthesis.md")) else ""
    mlist = re.search(r"N\(n\) for n = 1\.\.24 \(CHECKED, w01-c2, exhaustive\):\s*\n([\d, \n]+)\.", syn)
    b_syn = [int(x) for x in re.findall(r"\d+", mlist.group(1))] if mlist else []
    mlist2 = re.search(r"First values \(n = 1\.\.24.*?\):\s*\n([\d, \n]+)\.", syn)
    b_syn_M = [int(x) for x in re.findall(r"\d+", mlist2.group(1))] if mlist2 else []
    b_csv = {}
    bp = os.path.join(B["lab"], "data", "derived", "exhaustive.csv")
    hdr = open(bp).read().split("\n")[0]
    for l in open(bp).read().split("\n")[1:]:
        if l.strip():
            p = l.split(",")
            b_csv[int(p[0])] = p
    rows = []
    for n in range(1, NMAX + 1):
        best, cnt, _ = bf[n]
        rows.append((n, cnt, a_tab.get(n, (None, None))[1], b_syn[n - 1] if n <= len(b_syn) else None,
                     b_syn_M[n - 1] if n <= len(b_syn_M) else None, best,
                     "ok" if a_tab.get(n, (0, None))[1] == cnt and (n > len(b_syn) or b_syn[n - 1] == cnt) and (n > len(b_syn_M) or b_syn_M[n - 1] == best) else "DIFF"))
    syn2p = os.path.join(B2["lab"], "__statera__", "synthesis.md")
    syn2 = open(syn2p).read() if os.path.exists(syn2p) else ""
    m2 = re.search(r"The values for n = 1\.\.28 are ([\d, \n]+)\.", syn2)
    n2 = re.search(r"OEIS A134457, CITED\):\s*\n\s*\n([\d, \n]+)\.", syn2)
    b2_M = [int(x) for x in re.findall(r"\d+", m2.group(1))] if m2 else []
    b2_N = [int(x) for x in re.findall(r"\d+", n2.group(1))] if n2 else []
    rows = [r + (b2_N[r[0] - 1] if r[0] <= len(b2_N) else None, b2_M[r[0] - 1] if r[0] <= len(b2_M) else None,
                 "ok" if (r[0] > len(b2_N) or b2_N[r[0] - 1] == r[1]) and (r[0] > len(b2_M) or b2_M[r[0] - 1] == r[5]) else "DIFF") for r in rows]
    table(("n", "brute N(n)", "A data/exhaustive_w01c3.csv N", "B synthesis N list", "B synthesis M list", "brute M", "agree (A, B)",
           "B2 synthesis N list", "B2 synthesis M list", "agree (B2)"), rows)
    out("B2 synthesis lists: N %d values (n = 1..%d), M %d values; its n = 29..48 list is not brute-forced here." % (len(b2_N), len(b2_N), len(b2_M)))
    out("B data/derived/exhaustive.csv header: `%s`; rows %d; A csv rows %d; B synthesis lists: N %d values, M %d values." % (
        hdr, len(b_csv), len(a_tab), len(b_syn), len(b_syn_M)))
    out()
    out("Special-length counts claimed (both arms state them): N(2^m+m-1) = 2^(2^(m-1)) at n = 2, 5, 10; N(2^(m+1)+m-1) = (3*2^(m+1)-4)*c(m+1), "
        "c(k) = 2^(2^(k-1)-k), at n = 1, 4, 9 (arm A files it as w01-c5 at n = 2^m+m-2, m = 2, 3):")
    out()
    rows = []
    for n, claimed in ((2, 2), (5, 4), (10, 16), (1, 2), (4, 8), (9, 40)):
        rows.append((n, claimed, bf[n][1], "ok" if bf[n][1] == claimed else "DIFF"))
    table(("n", "formula value", "brute N(n)", "agree"), rows)

    out("### Claims and synthesis (`lab_status.py --project <lab>`)")
    out()
    rows = []
    for a in arms:
        txt = lab_status_text(a)
        head = re.search(r"^## Claims \((\d+), (\d+) disputed, (\d+) warnings\)", txt, re.M)
        lines = re.findall(r"^- (w\d\d-c\d)  (.*)$", txt, re.M)
        verified = [l for l in lines if "<-" in l[1]]
        lab_cnt = collections.Counter(l[1].split("  <-")[0] for l in lines)
        syn_exists = os.path.exists(os.path.join(a["lab"], "__statera__", "synthesis.md"))
        rows.append((a["arm"], "%s (%s warnings; %d heads without a label line)" % (head.group(1), head.group(3), sum(1 for l in lines if "no label" in l[1])) if head else None, len(verified), dict(lab_cnt), syn_exists,
                     "; ".join("%s %s" % l for l in lines)))
    table(("arm", "claims filed", "with a verifier verdict", "labels", "synthesis.md exists", "claim lines"), rows)
    # where each arm states the formula
    rows = []
    for a in arms:
        hits = []
        for p in sorted(glob.glob(os.path.join(a["lab"], "__statera__", "*.md")) + glob.glob(os.path.join(a["lab"], "__pondus__", "*.md"))
                        + glob.glob(os.path.join(a["lab"], "data", "*.md"))):
            t = open(p).read()
            if re.search(r"min\(2\^k,\s*n\s*[-−]\s*k\s*\+\s*1\)|Σ min|sum min|sum_\{k=1\}\^n min", t):
                hits.append(os.path.relpath(p, a["lab"]))
        rows.append((a["arm"], ", ".join(hits)))
    table(("arm", "lab files that state the sum formula min(2^k, n-k+1)"), rows)

    # ---------------------------------------------------------------- M7
    out("## M7: wall time, worker runs, first-turn context")
    out()
    rows = []
    for a in arms:
        cs = a["cost_state"]
        runs = sum(max(1, len(g["hb_points"])) for g in a["workers"])
        rows.append((a["arm"], a["end"] - a["start"], cs["totalDuration"] / 1000, cs["totalAPIDuration"] / 1000,
                     cs["totalToolDuration"] / 1000, (a["end"] - a["main_last"] if False else a["end"] - a["main_last"]),
                     len(a["workers"]), runs, a["exit"]))
    table(("arm", "wall s (end-start)", "cost-state totalDuration s", "totalAPIDuration s", "totalToolDuration s",
           "end minus last main-thread record (s)", "worker agent files", "worker runs (hand-backs, 1 if none)", "exit code"), rows)
    out("Last main-thread record to process exit: A %.0f s (stderr says the 10-minute background wait was hit: %s); B %.0f s." % (
        A["end"] - A["main_last"], "Background tasks still running 10m" in A["stderr"], B["end"] - B["main_last"]))
    out()
    rows = []
    for role in ("explorer", "author", "reproducer", "proof-adversary"):
        for a in arms:
            ags = [g for g in a["workers"] if a["role"][g["aid"]] == role]
            hb_runs = sum(max(1, len(g["hb_points"])) for g in ags)
            rows.append((role, a["arm"], len(ags), hb_runs))
    table(("role", "arm", "agent files", "runs"), rows)
    out("Timeline of agent files (seconds after process start; duration = first to last record of the file; resumed agents span the gap between runs):")
    out()
    rows = []
    for a in arms:
        for g in sorted(a["agents"], key=lambda g: g["t0"]):
            rows.append((a["arm"], g["name"], round(g["t0"] - a["start"]), round(g["t1"] - a["start"]), round(g["t1"] - g["t0"]), len(g["hb_points"])))
    rows.sort(key=lambda r: (r[0], -r[4]))
    table(("arm", "agent", "first record s", "last record s", "span s", "hand-backs"), rows[:8] + [r for r in rows if r[0] == "B"][:8])
    out("First request of each worker transcript: input + cache read + cache write tokens (all prompt tokens of request 1). Brief = first user message in characters.")
    out()
    rows = []
    summ = collections.defaultdict(dict)
    for a in arms:
        for g in sorted(a["workers"], key=lambda g: g["name"]):
            role = a["role"][g["aid"]]
            i, cr, cw = g["first_req"]
            tot = i + cr + cw
            rows.append((role, a["arm"], g["name"], tot, i, cr, cw, len(g["brief"])))
            summ[(role, a["arm"])].setdefault("tot", []).append(tot)
            summ[(role, a["arm"])].setdefault("brief", []).append(len(g["brief"]))
    table(("role", "arm", "agent", "first-request prompt tokens", "input", "cache read", "cache write", "brief chars"), rows)
    out("By role (mean, min, max of first-request prompt tokens; mean brief chars):")
    out()
    rows = []
    for role in ("explorer", "author", "reproducer", "proof-adversary"):
        r = [role]
        for a in arms:
            v = summ[(role, a["arm"])]["tot"]
            r += ["%d (%d-%d), n=%d" % (sum(v) / len(v), min(v), max(v), len(v)), "%d" % (sum(summ[(role, a["arm"])]["brief"]) / len(v))]
        ma, mb = sum(summ[(role, "A")]["tot"]) / len(summ[(role, "A")]["tot"]), sum(summ[(role, "B")]["tot"]) / len(summ[(role, "B")]["tot"])
        r += ["%.0f (%.0f%%)" % (mb - ma, 100 * (mb - ma) / ma)]
        rows.append(tuple(r))
    table(("role", "A tokens", "A brief chars", "B tokens", "B brief chars", "B minus A"), rows)
    rows = []
    for role in ("explorer", "author", "reproducer", "proof-adversary"):
        v = summ[(role, "B2")]["tot"]
        ma = sum(summ[(role, "A")]["tot"]) / len(summ[(role, "A")]["tot"])
        mb = sum(summ[(role, "B")]["tot"]) / len(summ[(role, "B")]["tot"])
        m2 = sum(v) / len(v)
        rows.append((role, "%d (%d-%d), n=%d" % (m2, min(v), max(v), len(v)), "%d" % (sum(summ[(role, "B2")]["brief"]) / len(v)),
                     "%.0f (%.0f%%)" % (m2 - ma, 100 * (m2 - ma) / ma), "%.0f" % (m2 - mb)))
    out("B2 by role:")
    out()
    table(("role", "B2 tokens", "B2 brief chars", "B2 minus A", "B2 minus B"), rows)
    # skills listing present in subagents
    for a in arms:
        n_list = 0
        for g in a["workers"]:
            for e in jl(g["path"]):
                if e["type"] == "attachment" and att(e).get("type") == "skill_listing":
                    n_list += 1
                    break
        sizes = [len(json.dumps(att(e))) for g in a["workers"][:1] for e in jl(g["path"]) if e["type"] == "attachment" and att(e).get("type") == "skill_listing"]
        out("Arm %s: size of the first worker's `skill_listing` attachment: %s chars. Workers whose transcript holds a `skill_listing` attachment: %d of %d. Agent-file `tools:` lists `Skill`: %s." % (
            a["arm"], sizes[0] if sizes else "none", n_list, len(a["workers"]),
            all("Skill" in re.search(r"^tools: (.*)$", open(os.path.join(a["plugin"], "agents", r + ".md")).read(), re.M)[1].split(", ")
                for r in ("explorer", "author", "reproducer", "proof-adversary"))))
    out()
    out("Per-agent spend (own, list price): rows beyond the top 11 that lab_status.py does not name.")
    out()
    rows = []
    for a in arms:
        for name, v in sorted(a["own"].items(), key=lambda kv: -kv[1]):
            rows.append((a["arm"], name, v, a["own_est"][name], a["printed"].get(name)))
    table(("arm", "agent", "own USD (recorded output)", "own USD (estimated output)", "printed by lab_status.py (top 11)"), rows)
    b2_section(A, B, B2, bf, ev)


if __name__ == "__main__":
    main()
