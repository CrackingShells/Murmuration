# Runs hook-event sequences for same-type dispatches (every order of Pre/Post(Agent)/SubagentStart, with and without answers, resumes, lab paths) through scripts/budget.py (fixed-clock shim) and through a `murmuration budget` binary, and checks (a) Python == binary on stdout, exit code, harness.jsonl and the whole lab folder, (b) the start/named lines against ground truth (which agent id belongs to which dispatch), without importing the author's code.
# inputs: --repo (merged tree with scripts/), --bin (testclock build, for the exact pass), --shipped (shipped binary, real clock, times blanked), --scratch DIR; output: counts and the first differences on stdout; exit 1 on any failure. Uses only w08c1_pyshim.py (shared with w08-c1) for the Python clock.
import argparse, itertools, json, os, shutil, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--bin", required=True)
ap.add_argument("--shipped")
ap.add_argument("--scratch", required=True)
ap.add_argument("--shim", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "w08c1_pyshim.py"))
ap.add_argument("--only", default="")
a = ap.parse_args()
T0 = 1792700000.125
XP = "murmuration:explorer"


def lab_files(lab):
    out = {}
    for r, ds, fs in os.walk(lab):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, lab)] = open(p, "rb").read()
    return out


def run(impl, lab, events, blank=False):
    """impl: py | bin | shipped. Returns (list of (rc, stdout, stderr), files)."""
    shutil.rmtree(lab, ignore_errors=True)
    os.makedirs(lab + "/__statera__")
    os.makedirs(lab + "/s/subagents")
    res = []
    for now, which, e in events:
        e = json.loads(json.dumps(e).replace("{LAB}", lab))
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "MURMURATION_NOW")}
        env.update(LC_ALL="en_US.UTF-8", CLAUDE_PLUGIN_ROOT=a.repo, MURMURATION_NOW=repr(now))
        if impl == "py":
            cmd = ["python3", "-S", "-I", a.shim, a.repo + "/scripts", which]
        elif impl == "bin":
            cmd = [a.bin, which]
        else:
            cmd = [a.shipped, which]
        p = subprocess.run(cmd, input=json.dumps(e).encode(), capture_output=True, timeout=60, env=env, cwd="/private/tmp")
        res.append((p.returncode, p.stdout, p.stderr))
    return res, lab_files(lab)


def pre(n, u, t, typ=XP, b="1", tm="9", name=True):
    tin = dict(subagent_type=typ, prompt="Your name is %s.\nBudget: USD %s\nTime: min %s\n" % (n, b, tm))
    if name:
        tin["name"] = n
    return (t, "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", tool_use_id=u, tool_input=tin))


def post(n, u, aid, t, typ=XP):
    return (t, "budget", dict(cwd="{LAB}", hook_event_name="PostToolUse", tool_name="Agent", tool_use_id=u,
                              tool_input=dict(subagent_type=typ, name=n, prompt="Your name is %s.\nBudget: USD 1\nTime: min 9\n" % n),
                              tool_response=dict(status="async_launched", agentId=aid)))


def start(aid, t, typ=XP, cwd="{LAB}"):
    return (t, "budget", dict(cwd=cwd, hook_event_name="SubagentStart", agent_id=aid, agent_type=typ, transcript_path="{LAB}/s.jsonl", permission_mode="default"))


def stop(aid, t, typ=XP):
    return (t, "budget", dict(cwd="{LAB}", hook_event_name="SubagentStop", agent_id=aid, agent_type=typ, transcript_path="{LAB}/s/subagents/agent-%s.jsonl" % aid, permission_mode="default", last_assistant_message="done"))


def order_scenarios(n, same_second):
    """All orders of Pre_i, Post_i (optional), Start_i for n dispatches of one type with the same figures; Pre_i < Post_i, Pre_i < Start_i. Truth: start of x_i belongs to dispatch i."""
    names = ["explorer-w09-%s" % c for c in "efgh"[:n]]
    evs = [("P", i) for i in range(n)] + [("S", i) for i in range(n)]
    out = []
    for withans in itertools.product([True, False], repeat=n):
        items = evs + [("A", i) for i in range(n) if withans[i]]
        for perm in itertools.permutations(items):
            pos = {x: k for k, x in enumerate(perm)}
            if any(pos[("P", i)] > pos[("S", i)] or (("A", i) in pos and pos[("P", i)] > pos[("A", i)]) for i in range(n)):
                continue
            if n > 1 and any(pos[("P", i)] > pos[("P", i + 1)] for i in range(n - 1)):
                continue   # dispatches are issued in index order (the platform emits the Pre events in call order)
            out.append(("n%d%s_%s" % (n, "ss" if same_second else "dt", "".join("%s%d" % x for x in perm) + "_" + "".join("1" if w else "0" for w in withans)), perm, names))
    return out


def to_events(perm, names, same_second):
    ev = []
    for k, (kind, i) in enumerate(perm):
        t = T0 if same_second else T0 + 0.01 * k
        n, u, aid = names[i], "tu%d" % i, "x%d" % i
        ev.append({"P": lambda: pre(n, u, t), "A": lambda: post(n, u, aid, t), "S": lambda: start(aid, t)}[kind]())
    return ev


def log_lines(files):
    return [json.loads(l) for l in files.get("__statera__/harness.jsonl", b"").decode().splitlines() if l.strip()]


def truth_check(perm, names, files):
    """Returns a list of problems in the harness.jsonl start/named lines against ground truth."""
    lines = log_lines(files)
    starts = {l["agent_id"]: l for l in lines if l.get("event") == "start"}
    named = [l for l in lines if l.get("event") == "named"]
    bad = []
    for i, nm in enumerate(names):
        s = starts.get("x%d" % i)
        if s is None:
            bad.append("no start for x%d" % i)
            continue
        if s.get("name_unconfirmed"):
            if nm not in (s.get("name_candidates") or "").split(","):
                bad.append("x%d unconfirmed without its true name in candidates: %r" % (i, s.get("name_candidates")))
            if s.get("name") == nm:
                bad.append("x%d unconfirmed but name set to a dispatch name" % i)
        elif len(names) > 1 and s.get("name") != nm and not str(s.get("name", "")).startswith("murmuration-"):
            bad.append("x%d confirmed with WRONG name %r (true %r)" % (i, s.get("name"), nm))
        elif s.get("name") != nm and len(names) == 1:
            bad.append("single x%d name %r" % (i, s.get("name")))
    for l in named:
        j = int(l["agent_id"][1:])
        if l["name"] != names[j]:
            bad.append("named line wrong: %s -> %s (true %s)" % (l["agent_id"], l["name"], names[j]))
    return bad


def blank(files):
    out = {}
    for k, v in files.items():
        s = v.decode("utf-8", "replace")
        import re
        s = re.sub(r'"(t|ts|time|t0|run_start|last_seen|at)": ?[0-9.e+-]+', '"T": 0', s)
        s = re.sub(r'"(t|ts|time|at|when)": ?"[^"]*"', '"T": ""', s)
        out[re.sub(r"^(.*/)?\d{14}\.\d{3}-", r"\1TIME-", k)] = s
    return out


def extra_scenarios():
    """Hand-made cases: resumed worker, duplicate answer, no answer at all, mixed types, missing tool_use_id, odd agentId, answer to a call inside a subagent."""
    T = T0
    sc = {}
    sc["resumed_after_stop"] = [pre("explorer-w09-e", "u1", T), start("x0", T + 1), stop("x0", T + 5), start("x0", T + 60), stop("x0", T + 70)]
    sc["resumed_with_agent_answer_again"] = [pre("explorer-w09-e", "u1", T), start("x0", T + 1), post("explorer-w09-e", "u1", "x0", T + 5), stop("x0", T + 6),
                                             post("explorer-w09-e", "u9", "x0", T + 60), start("x0", T + 61)]
    sc["no_post_at_all_two"] = [pre("explorer-w09-e", "u1", T), pre("explorer-w09-f", "u2", T), start("x0", T + 1), start("x1", T + 1), stop("x1", T + 9), stop("x0", T + 9)]
    sc["mixed_types_same_second"] = [pre("explorer-w09-e", "u1", T), pre("reproducer-w09-1", "u2", T, typ="murmuration:reproducer"), start("x1", T + 1, typ="murmuration:reproducer"), start("x0", T + 1)]
    sc["mixed_types_swapped_answers"] = [pre("explorer-w09-e", "u1", T), pre("reproducer-w09-1", "u2", T, typ="murmuration:reproducer"),
                                         post("reproducer-w09-1", "u2", "x1", T + 0.5, typ="murmuration:reproducer"), start("x0", T + 1), start("x1", T + 1, typ="murmuration:reproducer"), post("explorer-w09-e", "u1", "x0", T + 2)]
    p = pre("explorer-w09-e", "", T)
    p[2]["tool_use_id"] = None
    q = post("explorer-w09-e", "", "x0", T + 1)
    q[2]["tool_use_id"] = None
    sc["null_tool_use_id"] = [p, q, start("x0", T + 2)]
    odd = post("explorer-w09-e", "u1", "x0", T + 1)
    odd[2]["tool_response"] = dict(agentId=123)
    sc["agentId_int"] = [pre("explorer-w09-e", "u1", T), odd, start("x0", T + 2)]
    odd2 = post("explorer-w09-e", "u1", "x0", T + 1)
    odd2[2]["tool_response"] = dict(agentId="../../etc/x")
    sc["agentId_path_like"] = [pre("explorer-w09-e", "u1", T), odd2, start("x0", T + 2)]
    odd3 = post("explorer-w09-e", "u1", "x0", T + 1)
    odd3[2]["agent_id"] = "inner"
    sc["post_from_inside_subagent"] = [pre("explorer-w09-e", "u1", T), odd3, start("x0", T + 2)]
    sc["same_name_twice_same_second"] = [pre("explorer-w09-e", "u1", T), pre("explorer-w09-e", "u2", T), start("x0", T + 1), start("x1", T + 1), post("explorer-w09-e", "u1", "x1", T + 2), post("explorer-w09-e", "u2", "x0", T + 2)]
    sc["answer_before_pre_arrives"] = [post("explorer-w09-e", "u1", "x0", T), pre("explorer-w09-e", "u1", T + 0.1), start("x0", T + 1)]
    sc["stale_record_then_new_pair"] = [pre("explorer-w09-s", "u0", T), pre("explorer-w09-e", "u1", T + 1000), pre("explorer-w09-f", "u2", T + 1000), start("x0", T + 1001), start("x1", T + 1001)]
    dd = post("explorer-w09-f", "u2", "../x0", T + 3)
    sc["agentId_dotdot_hits_state_file"] = [pre("explorer-w09-e", "u1", T), start("x0", T + 1), pre("explorer-w09-f", "u2", T + 2), dd]
    return sc


def extra_main():
    lab = os.path.join(a.scratch, "lab")
    bad = 0
    for nm, evs in extra_scenarios().items():
        rp, fp = run("py", lab, evs)
        rb, fb = run("bin", lab, evs)
        rs, fs = run("shipped", lab, evs)
        same_pb = rp == rb and fp == fb
        same_ps = [(x[0], x[1].decode(), x[2]) for x in rs] == [(x[0], x[1].decode(), x[2]) for x in rp] and blank(fs) == blank(fp)
        lines = log_lines(fp)
        summ = [(l["event"], l.get("agent_id"), l.get("name"), "UNCONF:" + l["name_candidates"] if l.get("name_unconfirmed") else "", l.get("resumed")) for l in lines if l.get("event") in ("start", "named")]
        print("%-36s py==bin %s py==shipped %s  files=%s" % (nm, same_pb, same_ps, sorted(k for k in fp if k != "__statera__/harness.jsonl")))
        for x in summ:
            print("    ", x)
        if nm.startswith("agentId_dotdot"):
            print("    x0.json after:", fp.get("__statera__/.harness/x0.json", b"")[:160], "| pending left:", sorted(k for k in fp if "pending" in k), "| names:", sorted(k for k in fp if "names" in k))
        bad += (not same_pb) + (not same_ps)
    sys.exit(1 if bad else 0)



def main():
    scen = []
    for n in (1, 2, 3):
        for ss in (True, False):
            if n == 3 and not ss:
                continue
            scen += [(nm, perm, names, ss) for nm, perm, names in order_scenarios(n, ss)]
    scen = [s for s in scen if a.only in s[0]]
    # restrict n=3 to a deterministic stride to bound time
    keep = []
    c3 = 0
    for s in scen:
        if s[0].startswith("n3"):
            c3 += 1
            if c3 % 61:
                continue
        keep.append(s)
    scen = keep
    lab = os.path.join(a.scratch, "lab")
    nd = nt = nsh = 0
    probs = []
    stats = dict(confirmed_start=0, unconfirmed_start=0, named=0)
    for nm, perm, names, ss in scen:
        evs = to_events(perm, names, ss)
        rp, fp = run("py", lab, evs)
        rb, fb = run("bin", lab, evs)
        if rp != rb or fp != fb:
            nd += 1
            probs.append("DIFF py/bin " + nm)
        for p in truth_check(perm, names, fp):
            nt += 1
            probs.append("TRUTH %s: %s" % (nm, p))
        for l in log_lines(fp):
            if l.get("event") == "start":
                stats["unconfirmed_start" if l.get("name_unconfirmed") else "confirmed_start"] += 1
            if l.get("event") == "named":
                stats["named"] += 1
        if a.shipped:
            rs, fs = run("shipped", lab, evs)
            if [(x[0], x[1].decode(), x[2]) for x in rs] != [(x[0], x[1].decode(), x[2]) for x in rp] or blank(fs) != blank(fp):
                nsh += 1
                probs.append("DIFF py/shipped(real clock, times blanked) " + nm)
    print("scenarios %d; py!=bin %d; truth problems %d; py!=shipped %d; %s" % (len(scen), nd, nt, nsh, stats))
    for p in probs[:25]:
        print(p)
    sys.exit(1 if probs else 0)


extra_main() if a.only == "EXTRA" else main()
