# Enumerates the arrival orders of n same-type dispatches (events P_i: the Agent call's PreToolUse, S_i: the agent's SubagentStart, A_i: the Agent call's PostToolUse answer carrying agentId; P_i before S_i and before A_i) and runs each order through scripts/budget.py in a temporary lab (in process, fixed clock) and, optionally, through the Rust test binary (same events, one process each), then checks (1) every `start` line is confirmed with its true name or `name_unconfirmed` with candidates that include it, every `named` line names its agent, (2) with --rust: Python and Rust agree on every event's stdout, on the harness log without its time field, and on every file under .harness (names, bytes).
# The dispatches are relabelled in the order of their P events (the algorithm sees them only through the order of their records), so P_0 < P_1 < ... is fixed: that loses no order up to renaming. Schemes: `distinct` (n names, one set of figures), `figs` (distinct names, figures alternate), `dup` (names shared in pairs, one set of figures). `--absent` also drops the answers of every subset of dispatches.
# usage: python3 -I w08_c12_orders.py --repo DIR [--rust BIN] --n 1,2,3 [--absent] [--sample K --seed S] [--jobs J]   (--repo: a tree with scripts/budget.py; a tree at an older revision shows the checks can fail). Output: one line per (n, scheme): orders, start lines, violations, Rust differences; first 3 violations printed.
import argparse, itertools, json, multiprocessing as mp, os, random, shutil, subprocess, sys, tempfile

NOW0 = 1792700000.125


def orders(n, answers):
    """All interleavings of the chains P_i < {S_i, A_i} (A_i only for i in answers) with P_0 < P_1 < ...; as lists of (letter, i)."""
    evs = [("P", i) for i in range(n)] + [("S", i) for i in range(n)] + [("A", i) for i in answers]
    def rec(done, seq):
        if len(seq) == len(evs):
            yield list(seq)
            return
        for e in evs:
            if e in done:
                continue
            k, i = e
            if k == "P" and i > 0 and ("P", i - 1) not in done:
                continue
            if k != "P" and ("P", i) not in done:
                continue
            done.add(e); seq.append(e)
            yield from rec(done, seq)
            seq.pop(); done.discard(e)
    yield from rec(set(), [])


def scheme_of(n, scheme):
    names = ["explorer-w09-%s" % chr(97 + (i // 2 if scheme == "dup" else i)) for i in range(n)]
    figs = [("1", "9") if (scheme != "figs" or i % 2 == 0) else ("2", "10") for i in range(n)]
    return names, figs


def events_of(order, n, scheme, lab):
    names, figs = scheme_of(n, scheme)
    out = []
    for step, (k, i) in enumerate(order):
        now = NOW0 + 0.01 * (step + 1)
        call = dict(subagent_type="murmuration:explorer", name=names[i], prompt="Your name is %s.\nBudget: USD %s\nTime: min %s\n" % (names[i], figs[i][0], figs[i][1]))
        base = dict(cwd=lab, transcript_path=os.path.join(lab, "s.jsonl"))
        if k == "P":
            ev = dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="u%d" % i, tool_input=call)
        elif k == "A":
            ev = dict(base, hook_event_name="PostToolUse", tool_name="Agent", tool_use_id="u%d" % i, tool_input=call, tool_response=dict(status="async_launched", agentId="x%d" % i))
        else:
            ev = dict(base, hook_event_name="SubagentStart", agent_id="x%d" % i, agent_type="murmuration:explorer", permission_mode="default")
        out.append((ev, now))
    return out


def snap(lab):
    h = os.path.join(lab, "__statera__", ".harness")
    files = {}
    for dp, _, fs in os.walk(h):
        for f in fs:
            if f.endswith(".lock") or f == ".gitignore":
                continue
            p = os.path.join(dp, f)
            files[os.path.relpath(p, h)] = open(p, "rb").read()
    log = []
    lp = os.path.join(lab, "__statera__", "harness.jsonl")
    if os.path.exists(lp):
        for l in open(lp):
            d = json.loads(l); d.pop("t", None); log.append(d)
    return files, log


def run_py(budget, evs, lab):
    outs = []
    for ev, now in evs:
        outs.append(json.dumps(budget.handle(ev, now=now), sort_keys=True))
    return outs


def run_rs(rust, evs, lab, repo):
    outs = []
    for ev, now in evs:
        env = dict(os.environ, MURMURATION_NOW=repr(now), CLAUDE_PLUGIN_ROOT=repo, LC_ALL="en_US.UTF-8")
        env.pop("CLAUDE_PROJECT_DIR", None)
        env["MURMURATION_DELEGATE_LOG"] = os.path.join(lab, "delegate.log")
        env["MURMURATION_DELEGATE_SHIM"] = os.path.join(repo, "__instrumenta__", "w08c1_pyshim.py")
        p = subprocess.run([rust, "budget"], input=json.dumps(ev).encode(), capture_output=True, env=env, cwd="/private/tmp")
        outs.append(json.dumps(json.loads(p.stdout), sort_keys=True) if p.stdout.strip() else json.dumps(None))
    return outs


def check(log, n, scheme):
    names, _ = scheme_of(n, scheme)
    bad = []
    for x in log:
        if x["event"] == "start":
            true = names[int(x["agent_id"][1:])]
            ok = (x["name"] == true and not x.get("name_unconfirmed")) or (x.get("name_unconfirmed") and true in x["name_candidates"].split(","))
            if not ok:
                bad.append(("start", x["agent_id"], x["name"], x.get("name_candidates")))
        elif x["event"] == "named":
            if x["name"] != names[int(x["agent_id"][1:])]:
                bad.append(("named", x["agent_id"], x["name"]))
    return bad


def work(job):
    repo, rust, n, scheme, order = job
    sys.path.insert(0, os.path.join(repo, "scripts"))
    import budget, handback
    res = {"starts": 0, "bad": None, "diff": None}
    with tempfile.TemporaryDirectory() as d:
        labs = {}
        for who in ("py", "rs") if rust else ("py",):
            lab = os.path.join(d, who); os.makedirs(lab + "/__statera__"); labs[who] = lab
        evs = events_of(order, n, scheme, labs["py"])
        py_out = run_py(budget, evs, labs["py"])
        files_p, log_p = snap(labs["py"])
        res["starts"] = sum(1 for x in log_p if x["event"] == "start")
        bad = check(log_p, n, scheme)
        res["bad"] = (order, bad) if bad else None
        if rust:
            evs2 = events_of(order, n, scheme, labs["rs"])
            rs_out = run_rs(rust, evs2, labs["rs"], repo)
            files_r, log_r = snap(labs["rs"])
            norm = lambda s: s.replace(labs["py"], "<LAB>").replace(labs["rs"], "<LAB>")
            if [norm(o) for o in py_out] != [norm(o) for o in rs_out] or files_p != files_r or log_p != log_r:
                res["diff"] = order
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--rust"); ap.add_argument("--n", default="1,2,3"); ap.add_argument("--absent", action="store_true")
    ap.add_argument("--sample", type=int, default=0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--jobs", type=int, default=os.cpu_count()); ap.add_argument("--shard", default="0/1", help="i/k: run every k-th job from i (jobs 1 runs serially; start k processes for a Rust comparison, where a pool of workers that each spawn processes stalled)")
    a = ap.parse_args()
    for n in [int(x) for x in a.n.split(",")]:
        for scheme in (["distinct"] if n == 1 else ["distinct", "figs", "dup"]):
            subsets = [tuple(c) for k in range(n + 1) for c in itertools.combinations(range(n), k)] if a.absent else [tuple(range(n))]
            jobs = []
            if a.sample:
                rnd = random.Random(a.seed * 1000 + n)
                for _ in range(a.sample):
                    ans = rnd.choice(subsets) if a.absent else subsets[0]
                    ev = [("P", i) for i in range(n)] + [("S", i) for i in range(n)] + [("A", i) for i in ans]
                    # a random linear extension: pick at random among the events whose predecessors are done
                    order = []
                    rem = list(ev)
                    done = set()
                    while rem:
                        cand = [e for e in rem if (e[0] == "P" and (e[1] == 0 or ("P", e[1] - 1) in done)) or (e[0] != "P" and ("P", e[1]) in done)]
                        e = rnd.choice(cand); order.append(e); done.add(e); rem.remove(e)
                    jobs.append((a.repo, a.rust, n, scheme, order))
            else:
                for ans in subsets:
                    jobs += [(a.repo, a.rust, n, scheme, o) for o in orders(n, ans)]
            si, sk = [int(x) for x in a.shard.split("/")]
            jobs = jobs[si::sk]
            if a.jobs == 1:
                rs = [work(j) for j in jobs]
            else:
                with mp.Pool(a.jobs) as pool:
                    rs = pool.map(work, jobs, chunksize=64)
            bad = [r["bad"] for r in rs if r["bad"]]
            dif = [r["diff"] for r in rs if r["diff"]]
            print("n=%d scheme=%-8s orders=%d starts=%d violations=%d%s" % (n, scheme, len(rs), sum(r["starts"] for r in rs), len(bad), (" rust_differences=%d" % len(dif)) if a.rust else ""), flush=True)
            for b in bad[:3]:
                print("   violation:", " ".join("%s%d" % e for e in b[0]), b[1][:2])
            for d in dif[:3]:
                print("   rust differs:", " ".join("%s%d" % e for e in d))


if __name__ == "__main__":
    main()
