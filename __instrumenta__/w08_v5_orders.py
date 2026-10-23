# Checks, in process through scripts/budget.py handle(), every arrival order (or a seeded sample) of n same-type dispatches (events P_i, A_i optional, S_i; P_i before S_i and A_i; P in index order) against ground truth (start of agent x_i belongs to dispatch i): each start line is confirmed with its true name or says name_unconfirmed with the true name among name_candidates, and each named line is true; schemes: names distinct, figures alternating, names shared in pairs.
# inputs: --repo (tree with scripts/), --n 3,4, --sample N (0 = all), --seed; output: counts of orders and violations and the first violations on stdout; exit 1 on a violation. Independent of the author's enumerator.
import argparse, itertools, json, os, random, sys, tempfile
ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--n", default="3")
ap.add_argument("--sample", type=int, default=0)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
sys.path.insert(0, a.repo + "/scripts")
import budget
XP = "murmuration:explorer"


def orders(n, rnd, sample):
    base = [("P", i) for i in range(n)] + [("S", i) for i in range(n)]
    def ok(perm, present):
        pos = {x: k for k, x in enumerate(perm)}
        return all(pos[("P", i)] < pos[("S", i)] and (("A", i) not in pos or pos[("P", i)] < pos[("A", i)]) for i in range(n)) and all(pos[("P", i)] < pos[("P", i + 1)] for i in range(n - 1))
    if sample:
        for _ in range(sample):
            present = [rnd.random() < 0.6 for _ in range(n)]
            items = base + [("A", i) for i in range(n) if present[i]]
            while True:
                rnd.shuffle(items)
                if ok(items, present):
                    break
            yield list(items)
    else:
        for present in itertools.product([True, False], repeat=n):
            items = base + [("A", i) for i in range(n) if present[i]]
            for perm in itertools.permutations(items):
                if ok(perm, present):
                    yield list(perm)


def run_order(perm, n, scheme):
    names = ["w-%s" % c for c in "abcdef"[:n]]
    if scheme == "dup":
        names = ["w-%s" % c for c in "aabbcc"[:n]]
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(tmp + "/__statera__")
        base = dict(cwd=tmp, transcript_path=tmp + "/s.jsonl")
        for k, (kind, i) in enumerate(perm):
            t = 1000.0 + 0.001 * k
            nm, u = names[i], "u%d" % i
            fig = (i % 2) + 1 if scheme == "figs" else 1
            tin = dict(subagent_type=XP, name=nm, prompt="Your name is %s.\nBudget: USD %d\nTime: min 9\n" % (nm, fig))
            if kind == "P":
                budget.handle(dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id=u, tool_input=tin), now=t)
            elif kind == "A":
                budget.handle(dict(base, hook_event_name="PostToolUse", tool_name="Agent", tool_use_id=u, tool_input=tin, tool_response=dict(status="async_launched", agentId="x%d" % i)), now=t)
            else:
                budget.handle(dict(base, hook_event_name="SubagentStart", agent_id="x%d" % i, agent_type=XP), now=t)
        lines = [json.loads(l) for l in open(tmp + "/__statera__/harness.jsonl")]
    bad = []
    st = {l["agent_id"]: l for l in lines if l["event"] == "start"}
    for i, nm in enumerate(names):
        s = st.get("x%d" % i)
        if not s:
            bad.append("no start x%d" % i); continue
        if s.get("name_unconfirmed"):
            if nm not in s.get("name_candidates", "").split(","):
                bad.append("x%d candidates %r lack %s" % (i, s.get("name_candidates"), nm))
        elif s.get("name") != nm:
            bad.append("x%d confirmed wrong %r (true %s)" % (i, s.get("name"), nm))
    for l in lines:
        if l["event"] == "named" and l["name"] != names[int(l["agent_id"][1:])]:
            bad.append("named wrong " + str(l))
    return bad


tot = 0
fail = 0
for n in map(int, a.n.split(",")):
    for scheme in ("distinct", "figs", "dup"):
        rnd = random.Random(a.seed)
        c = f = 0
        for perm in orders(n, rnd, a.sample):
            c += 1
            b = run_order(perm, n, scheme)
            if b:
                f += 1
                if f <= 3:
                    print("VIOLATION n=%d %s %s: %s" % (n, scheme, " ".join("%s%d" % x for x in perm), b))
        print("n=%d %-8s orders %d violations %d" % (n, scheme, c, f))
        tot += c; fail += f
sys.exit(1 if fail else 0)
