# Runs the w08c1 replay (Python reference through the fixed-clock shim against the Rust binary, same scenario folders, compared after every step: stdout, exit code, stderr, whole lab folder) with extra scenarios for w08-c5 added to its list: dispatch records and starts of one agent type in every order (PreToolUse, PostToolUse answers with agentId, SubagentStart), odd answers, nested and slashed cwd, pre-made records with odd names or pool, and a seeded fuzz of such sequences.
# usage: python3 -I w08_c5_replay_extra.py <the arguments of w08c1_replay.py: --repo WT --rust BIN --scratch DIR --out DIR [--exact|--realclock] [--quick] [--jobs N] [--only c5_] ...>; --c5fuzz N (default 300, 40 with --quick) and --c5seed S are read here first. Output: as w08c1_replay.py (replay_<mode>.json and diff files in --out); exit 1 on any difference.
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08c1_replay as r

NOW0, Scn, ev = r.NOW0, r.Scn, r.ev
XP = "murmuration:explorer"


def pre(n, u, now, name=..., b="1", t="9", typ=XP, tool="Agent", prompt=None):
    p = prompt if prompt is not None else ("Your name is %s.\nBudget: USD %s\nTime: min %s\n" % (n, b, t))
    tin = dict(subagent_type=typ, prompt=p)
    if name is not ...:
        tin["name"] = name
    return ("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name=tool, tool_use_id=u, tool_input=tin), now)


def post(n, u, aid, now, typ=XP, tool="Agent", resp=..., name=..., cwd="{LAB}", **kw):
    tin = dict(subagent_type=typ, prompt="Your name is %s.\nBudget: USD 1\nTime: min 9\n" % n)
    if name is not ...:
        tin["name"] = name
    d = dict(cwd=cwd, hook_event_name="PostToolUse", tool_name=tool, tool_use_id=u, tool_input=tin, tool_response=dict(status="async_launched", agentId=aid) if resp is ... else resp)
    d.update(kw)
    return ("ev", "budget", d, now)


def start(aid, now, typ=XP, **kw):
    return ev("budget", "SubagentStart", now, aid=aid, atype=typ, mode=None, **kw)


def fixed():
    out = []
    # names differ, same figures, no answer before the starts: unconfirmed; the answers come later (foreground)
    out.append(Scn("c5_noans", [pre("explorer-w09-e", "u1", NOW0, name="explorer-w09-e"), pre("explorer-w09-f", "u2", NOW0 + 0.05, name="explorer-w09-f"), start("x1", NOW0 + 1), start("x2", NOW0 + 1.1),
                                post("explorer-w09-f", "u2", "x1", NOW0 + 5, name="explorer-w09-f"), post("explorer-w09-e", "u1", "x2", NOW0 + 5.1, name="explorer-w09-e")]))
    # the answers first (background), starts swapped
    out.append(Scn("c5_bg", [pre("g", "u3", NOW0, name="explorer-w09-g"), pre("h", "u4", NOW0 + 0.05, name="explorer-w09-h"), post("g", "u3", "x3", NOW0 + 0.1, name="explorer-w09-g"),
                             post("h", "u4", "x4", NOW0 + 0.15, name="explorer-w09-h"), start("x4", NOW0 + 1), start("x3", NOW0 + 1.1)]))
    # one answer before its start, the other after: the second start is alone in the pool
    out.append(Scn("c5_half", [pre("g", "u3", NOW0, name="g"), pre("h", "u4", NOW0 + 0.05, name="h"), post("g", "u3", "x3", NOW0 + 0.1, name="g"), start("x3", NOW0 + 1), start("x4", NOW0 + 1.1),
                               post("h", "u4", "x4", NOW0 + 2, name="h")]))
    # different figures and names: source unknown and name unconfirmed; an answer for one of them in between
    out.append(Scn("c5_mixed", [pre("g", "u3", NOW0, name="g", b="2", t="10"), pre("h", "u4", NOW0 + 0.05, name="h", b="3", t="20"), start("x3", NOW0 + 1), post("h", "u4", "x4", NOW0 + 1.5, name="h"),
                                start("x4", NOW0 + 2), post("g", "u3", "x3", NOW0 + 3, name="g")]))
    # three of one type and one of another; names from the brief (no name field); a duplicated name; starts fewer than dispatches
    out.append(Scn("c5_three", [pre("a1", "u1", NOW0), pre("a2", "u2", NOW0 + 0.01), pre("a3", "u3", NOW0 + 0.02), pre("r1", "u4", NOW0 + 0.03, typ="murmuration:reproducer"), start("y1", NOW0 + 1), start("y2", NOW0 + 1.01),
                                post("a3", "u3", "y3", NOW0 + 1.5, name=...), start("y3", NOW0 + 2), post("a1", "u1", "y1", NOW0 + 3)]))
    out.append(Scn("c5_dupname", [pre("a1", "u1", NOW0, name="same"), pre("a1", "u2", NOW0 + 0.01, name="same"), start("y1", NOW0 + 1), start("y2", NOW0 + 1.1)]))
    out.append(Scn("c5_noname", [pre("a1", "u1", NOW0, name=..., prompt="no name line\n"), pre("a2", "u2", NOW0 + 0.01, name=..., prompt="Budget: USD 1\nTime: min 9\n"), start("y1", NOW0 + 1), start("y2", NOW0 + 1.1)]))
    # Task tool, a resumed agent (start twice), a stop
    out.append(Scn("c5_task_resume", [pre("a1", "u1", NOW0, name="n1", tool="Task"), post("a1", "u1", "y1", NOW0 + 0.5, name="n1", tool="Task"), start("y1", NOW0 + 1), start("y1", NOW0 + 50),
                                      ev("budget", "SubagentStop", NOW0 + 60, aid="y1", atype=XP), post("a1", "u1", "y1", NOW0 + 70, name="n1", tool="Task")]))
    # the answer of an agent that has not started and has no record; of another type; from inside a subagent; without an id
    out.append(Scn("c5_post_odd", [post("a1", "u1", "y1", NOW0), post("a1", "u2", "y2", NOW0 + 1, typ="general-purpose"), post("a1", "u3", "y3", NOW0 + 2, agent_id="zz", agent_type=XP),
                                   post("a1", "u4", "y4", NOW0 + 3, resp="done"), post("a1", "u5", "y5", NOW0 + 4, resp=dict(agentId=5)), post("a1", "u6", "y6", NOW0 + 5, resp=dict(agentId="")),
                                   post("a1", "u7", "y7", NOW0 + 6, resp=[1]), post("a1", "u8", "y8", NOW0 + 7, resp=None), post("a1", "", "y9", NOW0 + 8), post("a1", "u10", "y10", NOW0 + 9, typ=5),
                                   post("a1", "u11", "y11", NOW0 + 10, tool_input=None), post("a1", "u12", "y12", NOW0 + 11, name=["x"]), start("y1", NOW0 + 12)]))
    # a lab reached from a nested cwd, and from a cwd with a trailing slash
    out.append(Scn("c5_cwd", [pre("a1", "u1", NOW0, name="n1"), start("y1", NOW0 + 1, cwd="{LAB}/a/b"), pre("a2", "u2", NOW0 + 2, name="n2"), start("y2", NOW0 + 3, cwd="{LAB}/"),
                              pre("a3", "u3", NOW0 + 4, name="n3"), start("y3", NOW0 + 5, cwd="{LAB}/./a/../")]))
    # pre-made records: odd names, a pool, an ambiguous flag, a name that is not a string, a stale record
    rec = lambda n, **k: json.dumps(dict(type=XP, B=1.0, T=9.0, b_set=True, t_set=True, t=NOW0, name=n, **k))
    for i, (r1, r2) in enumerate([(rec("a"), rec("b")), (rec("a", pool="a,b"), rec("b")), (rec("a"), rec("b", pool="zz")), (rec("a", ambiguous=True), rec("a")), (rec("a"), rec(5)), (rec(5), rec(5)),
                                  (rec("a", pool=5), rec("b")), (rec("a", pool=""), rec("b")), (rec("é"), rec("a\u0000b")), (rec("b"), rec("a")), (rec("a", ambiguous=False), rec("b", pool=[1])),
                                  (rec(None), rec("a")), (rec("a"), json.dumps(dict(type=XP, B=1.0, T=9.0, b_set=True, t_set=True, t=NOW0)))]):
        out.append(Scn("c5_rec%d" % i, [("file", ".harness/pending/%014.3f-p1.json" % NOW0, r1), ("file", ".harness/pending/%014.3f-p2.json" % (NOW0 + 0.001), r2), start("y1", NOW0 + 1), start("y2", NOW0 + 1.1)]))
    # an answer binding a pre-made record, and a pre-made binding file
    out.append(Scn("c5_names_file", [("file", ".harness/names/y1.json", rec("bound")), ("file", ".harness/names/y2.json", "[1]"), ("file", ".harness/names/y3.json", "{"), start("y1", NOW0 + 1), start("y2", NOW0 + 1.1), start("y3", NOW0 + 1.2)]))
    out.append(Scn("c5_bind_premade", [("file", ".harness/pending/%014.3f-u1.json" % NOW0, rec("bound")), ("file", ".harness/pending/%014.3f-u1.json" % (NOW0 + 1), rec("later")), post("x", "u1", "y1", NOW0 + 2), start("y1", NOW0 + 3), start("y2", NOW0 + 4)]))
    return out


def fuzz(n, seed):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        k = rnd.randint(1, 4)
        names = [rnd.choice(["explorer-w09-e", "explorer-w09-f", "author-w09-1", "same"]) for _ in range(k)]
        fig = [rnd.choice([("1", "9"), ("2", "10")]) for _ in range(k)] if rnd.random() < 0.3 else [("1", "9")] * k
        steps, t = [], NOW0
        for j in range(k):
            steps.append(pre(names[j], "u%d" % j, t, name=names[j] if rnd.random() < 0.8 else ..., b=fig[j][0], t=fig[j][1], typ=rnd.choice([XP, XP, "murmuration:author"])))
            t += rnd.choice([0.001, 0.05, 1])
        todo = [("s", j) for j in range(k)] + [("p", j) for j in range(k) if rnd.random() < 0.8]
        rnd.shuffle(todo)
        for kind, j in todo:
            t += rnd.choice([0.001, 0.05, 1])
            aid = "x%d" % rnd.choice([j, j, j, (j + 1) % k])
            steps.append(start(aid, t, typ=rnd.choice([XP, XP, "murmuration:author"])) if kind == "s" else post(names[j], "u%d" % j, aid, t, name=names[j], typ=rnd.choice([XP, XP, "murmuration:author"])))
        out.append(Scn("c5_fuzz%d" % i, steps, group="c5fuzz"))
    return out


def main():
    argv = sys.argv[1:]
    n = int(argv[argv.index("--c5fuzz") + 1]) if "--c5fuzz" in argv else (40 if "--quick" in argv else 300)
    seed = int(argv[argv.index("--c5seed") + 1]) if "--c5seed" in argv else 0
    for opt in ("--c5fuzz", "--c5seed"):
        if opt in argv:
            i = argv.index(opt)
            del argv[i:i + 2]
    sys.argv = [sys.argv[0]] + argv
    orig = r.real_scns
    r.real_scns = lambda *a: orig(*a) + fixed() + fuzz(n, seed)
    return r.main()


if __name__ == "__main__":
    sys.exit(main())
