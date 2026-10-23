# Replays odd and malformed PreToolUse(SubagentHandback) events through the plugin's hook start as hooks.json runs it (`python3 -S -I scripts/run_hook.py handback`, stdin = the event) in a scratch lab, and times the start; inputs: the plugin export folder (scripts/), an output folder; outputs: OUT/offline_cases.tsv (case, exit code, stdout kind, stderr empty, deny lines added, markers added) and OUT/offline_time.tsv (median of 50 starts per payload kind).
# usage: w08_c2_offline.py PLUGIN_DIR OUTDIR
import json, os, subprocess, sys, tempfile, time, statistics as st, threading

plugin, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
LONG = 5000
HOOK = [sys.executable, "-S", "-I", os.path.join(plugin, "scripts", "run_hook.py"), "handback"]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}


def run(cwd, stdin):
    t0 = time.perf_counter()
    p = subprocess.run(HOOK, input=stdin, capture_output=True, text=True, cwd=cwd, env=env, timeout=30)
    return p, (time.perf_counter() - t0) * 1000


def ev(cwd, **kw):
    return json.dumps(dict(dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id="a1", agent_type="murmuration:author", cwd=cwd,
                                tool_input={"message": "x" * (LONG + 1)}), **kw))


rows = [["case", "exit", "stdout", "stderr_empty", "deny_lines_added", "markers_added"]]
with tempfile.TemporaryDirectory() as tmp:
    lab = os.path.join(tmp, "lab")
    os.makedirs(os.path.join(lab, "__statera__"))
    n = [0]

    def case(label, stdin, cwd=lab, expect_deny=None):
        n[0] += 1
        log = os.path.join(lab, "__statera__", "harness.jsonl")
        mk = os.path.join(lab, "__statera__", ".harness")
        before_l = len(open(log).read().splitlines()) if os.path.exists(log) else 0
        before_m = set(os.listdir(mk)) if os.path.isdir(mk) else set()
        p, _ = run(cwd, stdin)
        kind = "empty"
        if p.stdout.strip():
            try:
                o = json.loads(p.stdout)
                kind = "deny-json" if o["hookSpecificOutput"]["permissionDecision"] == "deny" else "other-json"
            except Exception:
                kind = "INVALID"
        after_l = len(open(log).read().splitlines()) if os.path.exists(log) else 0
        after_m = set(os.listdir(mk)) if os.path.isdir(mk) else set()
        rows.append([label, p.returncode, kind, int(p.stderr == ""), after_l - before_l, len(after_m - before_m - {".gitignore"})])
        return kind

    aid = [0]

    def fresh():
        aid[0] += 1
        return "o%d" % aid[0]
    msg = lambda m: {"message": m}
    case("not JSON", "not json")
    case("empty stdin", "")
    case("JSON list", "[1,2]")
    case("JSON string", '"x"')
    case("tool_input missing", json.dumps(dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id=fresh(), agent_type="murmuration:author", cwd=lab)))
    for label, ti in (("tool_input is a list", ["x" * (LONG + 1)]), ("tool_input is a string", "x" * (LONG + 1)), ("tool_input is null", None), ("message is a number", msg(7)), ("message is null", msg(None)),
                      ("message is a list", msg(["x" * (LONG + 1)])), ("message is an object", msg({"a": "x" * (LONG + 1)})), ("message key absent", {"msg": "x" * (LONG + 1)}), ("message empty", msg(""))):
        case(label, ev(lab, agent_id=fresh(), tool_input=ti))
    case("agent_id missing", json.dumps(dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_type="murmuration:author", cwd=lab, tool_input=msg("x" * (LONG + 1)))))
    case("agent_id is a number", ev(lab, agent_id=5))
    case("agent_type missing", json.dumps(dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id=fresh(), cwd=lab, tool_input=msg("x" * (LONG + 1)))))
    case("agent_type general-purpose", ev(lab, agent_id=fresh(), agent_type="general-purpose"))
    case("agent_type is a list", ev(lab, agent_id=fresh(), agent_type=["murmuration:author"]))
    case("another tool", ev(lab, agent_id=fresh(), tool_name="Bash"))
    case("cwd missing", json.dumps(dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id=fresh(), agent_type="murmuration:author", tool_input=msg("x" * (LONG + 1)))), cwd=tmp)
    case("no lab above cwd", ev(tmp, agent_id=fresh()), cwd=tmp)
    case("message exactly N characters", ev(lab, agent_id=fresh(), tool_input=msg("x" * LONG)))
    case("message N characters, bytes over N", ev(lab, agent_id=fresh(), tool_input=msg("é" * LONG)))
    case("message with a lone surrogate, N+1", ev(lab, agent_id=fresh(), tool_input=msg("\ud800" * (LONG + 1))))
    case("message of 2 million characters", ev(lab, agent_id=fresh(), tool_input=msg("x" * 2000000)))
    case("message N+1, author (expect deny)", ev(lab, agent_id=fresh(), tool_input=msg("x" * (LONG + 1))))
    case("message N+1, reproducer (expect deny)", ev(lab, agent_id=fresh(), agent_type="murmuration:reproducer"))
    case("message N+1, proof-adversary (expect deny)", ev(lab, agent_id=fresh(), agent_type="murmuration:proof-adversary"))
    case("message N+1, explorer, no report (expect one deny)", ev(lab, agent_id=fresh(), agent_type="murmuration:explorer"))
    one = fresh()
    case("same author, first over-long (expect deny)", ev(lab, agent_id=one))
    case("same author, second over-long (expect pass)", ev(lab, agent_id=one))
    # 12 concurrent starts of one agent
    cc = fresh()
    outs = []
    th = [threading.Thread(target=lambda: outs.append(run(lab, ev(lab, agent_id=cc))[0].stdout)) for _ in range(12)]
    [t.start() for t in th]
    [t.join() for t in th]
    rows.append(["12 concurrent over-long starts of one agent: denies", 0, "%d of 12" % sum(1 for o in outs if o.strip()), 1, "", ""])
    # time: median of 50 starts per payload kind (reported, not gated)
    tt = [["payload", "n", "median_ms", "p90_ms"]]
    for label, mk in (("over-long (deny path, fresh agent each time)", lambda i: ev(lab, agent_id="t%d" % i)),
                      ("over-long, already denied (pass path)", lambda i: ev(lab, agent_id=one)),
                      ("short message (nothing to say)", lambda i: ev(lab, agent_id="s%d" % i, tool_input=msg("short"))),
                      ("other tool (PostToolUse-like no-op)", lambda i: ev(lab, agent_id="z%d" % i, tool_name="Bash"))):
        ms = [run(lab, mk(i))[1] for i in range(50)]
        tt.append([label, 50, "%.1f" % st.median(ms), "%.1f" % sorted(ms)[44]])
open(os.path.join(out, "offline_cases.tsv"), "w").write("\n".join("\t".join(str(x) for x in r) for r in rows) + "\n")
open(os.path.join(out, "offline_time.tsv"), "w").write("\n".join("\t".join(str(x) for x in r) for r in tt) + "\n")
print("\n".join("\t".join(str(x) for x in r) for r in rows))
print("\n".join("\t".join(str(x) for x in r) for r in tt))
