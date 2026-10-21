"""Times every hook registration of one or more plugin variants on recorded payloads, interleaved, and writes one JSON line per run.

Inputs: --variant NAME=PLUGIN_ROOT (repeatable; the root holds hooks/hooks.json and scripts/), --payloads payloads.jsonl (raw hook payloads recorded by
hook_record_wrap.py in a headless run), --transcripts short=PATH,long=PATH (real worker transcripts), --reports-src DIR (a `__reports__` tree for the
report check), --fx DIR (scratch folder outside the repository, rebuilt), --n N runs per cell, --out results.jsonl, --seed.
Output: results.jsonl, one line per run (case, variant, hook, wall_ms, cpu_ms, rc, out_len, out_md5); `hook_cost_summary.py` turns it into the tables.
Each run starts the hook's command exactly as the platform does (`sh -c <command from hooks.json>`, CLAUDE_PLUGIN_ROOT set, payload on stdin, cwd = the lab);
cells are shuffled in every round so that load on the machine falls on all variants alike. Floors (`sh :`, `python3 -c pass`, ...) are cells of the same loop.
Stdlib only; seed fixed (default 20261020).
"""
import argparse, hashlib, json, os, random, re, resource, shutil, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--variant", action="append", required=True)
ap.add_argument("--payloads", required=True)
ap.add_argument("--transcripts", required=True)
ap.add_argument("--reports-src", required=True)
ap.add_argument("--fx", required=True)
ap.add_argument("--n", type=int, default=40)
ap.add_argument("--out", required=True)
ap.add_argument("--seed", type=int, default=20261020)
ap.add_argument("--only", default="", help="substring filter on case ids")
ap.add_argument("--no-floors", action="store_true")
ap.add_argument("--paired", action="store_true", help="w05-c4: the variants of one case run back to back (random order inside the pair), cases shuffled between pairs, so that a ratio is a ratio of neighbours in time")
ap.add_argument("--stdin", choices=("file", "sock"), default="file", help="sock: the payload goes through a socketpair, as the platform feeds a hook (measured, w04-c5)")
ap.add_argument("--pad", type=int, default=0, help="a tool_response string of this many bytes in every payload that has one")
ap.add_argument("--spawn", choices=("popen", "posix"), default="popen", help="popen: subprocess.Popen (forks this Python); posix: os.posix_spawn of `sh -c 'cd LAB && COMMAND'`, a lighter start whose own overhead is smaller")
args = ap.parse_args()

FX = os.path.abspath(args.fx)
variants = dict(v.split("=", 1) for v in args.variant)
trans = dict(t.split("=", 1) for t in args.transcripts.split(","))
rows = [json.loads(l) for l in open(args.payloads)]


def recorded(label, agent, tool=None):
    for r in rows:
        p = json.loads(r["payload"])
        if r["label"] == label and bool(p.get("agent_id")) == agent and (tool is None or p.get("tool_name") == tool):
            return p
    raise KeyError((label, agent, tool))


BASE = dict(
    user=recorded("UserPromptSubmit||user_words.py", False),
    dispatch=recorded("PreToolUse|Agent|Task|budget.py", False, "Agent"),
    main_post=recorded("PostToolUse||budget.py", False, "Bash"),
    main_batch=recorded("PostToolBatch||budget.py", False),
    start=recorded("SubagentStart||budget.py", True),
    a_post=recorded("PostToolUse||budget.py", True, "Bash"),
    a_batch=recorded("PostToolBatch||budget.py", True),
    stop=recorded("SubagentStop||budget.py", True),
    pre_hb=recorded("PreToolUse|SubagentHandback|handback.py", True, "SubagentHandback"),
    post_hb=recorded("PostToolUse|SubagentHandback|handback.py", True, "SubagentHandback"),
)

# ---- fixture: one lab per variant, the same transcripts in each
LABS = {}
for name in variants:
    lab = os.path.join(FX, name, "lab")
    shutil.rmtree(os.path.join(FX, name), ignore_errors=True)
    os.makedirs(os.path.join(lab, "__statera__"))
    shutil.copytree(args.reports_src, os.path.join(lab, "__reports__"))
    for d in ("__pondus__", "__scrupuli__"):
        src = os.path.join(os.path.dirname(args.reports_src), d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(lab, d))
    for f in ("wave-04.md", "wave-03.md"):
        src = os.path.join(os.path.dirname(args.reports_src), "__statera__", f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(lab, "__statera__", f))
    sess = os.path.join(FX, name, "sess")
    os.makedirs(os.path.join(sess, "subagents"))
    LABS[name] = dict(lab=lab, sess=sess)
    for k, path in trans.items():
        shutil.copy(path, os.path.join(sess, "subagents", "agent-%s.jsonl" % k))
        json.dump({"name": "explorer-w04-%s" % k, "agentType": "murmuration:explorer"}, open(os.path.join(sess, "subagents", "agent-%s.meta.json" % k), "w"))
    open(sess + ".jsonl", "w").write("")


def payload(name, kind, agent=None, **over):
    p = dict(BASE[kind])
    L = LABS[name]
    p["cwd"] = L["lab"]
    p["transcript_path"] = L["sess"] + ".jsonl"
    if agent:
        p["agent_id"] = agent
        p["agent_type"] = "murmuration:explorer"
        if "agent_transcript_path" in p:
            p["agent_transcript_path"] = os.path.join(L["sess"], "subagents", "agent-%s.jsonl" % agent)
    p.update(over)
    if args.pad and "tool_response" in p:
        p["tool_response"] = {"stdout": "x" * args.pad}
    return json.dumps(p) + "\n"


def hooks_of(name, event, tool=None, source=None):
    """The (script, command) pairs the platform would start for this event in this variant."""
    h = json.load(open(os.path.join(variants[name], "hooks", "hooks.json")))["hooks"].get(event, [])
    out = []
    for g in h:
        m = g.get("matcher")
        if m is not None and not re.fullmatch(m, tool or source or ""):
            continue
        for hk in g["hooks"]:
            out.append((re.search(r"(\w+)\.py", hk["command"]).group(1), hk["command"]))
    return out


def run_cmd(name, command, stdin_text, extra_env=None):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=variants[name])
    env.pop("CLAUDE_PROJECT_DIR", None)
    inp = os.path.join(FX, "stdin.json")
    feeder = None
    if args.stdin == "sock":
        import socket, threading
        sa, fh = socket.socketpair()

        def feed():
            try:
                sa.sendall(stdin_text.encode())
            except OSError:
                pass
            sa.close()
        feeder = threading.Thread(target=feed)
        feeder.start()
    else:
        open(inp, "w").write(stdin_text)
        fh = open(inp)
    if args.spawn == "posix":
        r_out, w_out = os.pipe()
        r_err, w_err = os.pipe()
        fa = [(os.POSIX_SPAWN_DUP2, fh.fileno(), 0), (os.POSIX_SPAWN_DUP2, w_out, 1), (os.POSIX_SPAWN_DUP2, w_err, 2),
              (os.POSIX_SPAWN_CLOSE, r_out), (os.POSIX_SPAWN_CLOSE, r_err), (os.POSIX_SPAWN_CLOSE, w_out), (os.POSIX_SPAWN_CLOSE, w_err)]
        t0 = time.perf_counter()
        pid = os.posix_spawn("/bin/sh", ["sh", "-c", 'cd "%s" && %s' % (LABS[name]["lab"], command)], env, file_actions=fa)
        os.close(w_out)
        os.close(w_err)
        out = b""
        while True:
            chunk = os.read(r_out, 65536)
            if not chunk:
                break
            out += chunk
        err = os.read(r_err, 65536)
        _, status, ru = os.wait4(pid, 0)
        wall = (time.perf_counter() - t0) * 1000
        os.close(r_out)
        os.close(r_err)
        fh.close()
        if feeder:
            feeder.join()
        return wall, (ru.ru_utime + ru.ru_stime) * 1000, os.waitstatus_to_exitcode(status), out, err
    t0 = time.perf_counter()
    p = subprocess.Popen(["/bin/sh", "-c", command], stdin=fh, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LABS[name]["lab"], env=env)
    out = p.stdout.read()
    err = p.stderr.read()
    _, status, ru = os.wait4(p.pid, 0)
    wall = (time.perf_counter() - t0) * 1000
    p.returncode = 0
    fh.close()
    return wall, (ru.ru_utime + ru.ru_stime) * 1000, os.waitstatus_to_exitcode(status), out, err


# ---- cases: id -> (event, tool, source, kind, agent, prepare-function name)
def reset_state(name, agent):
    st = os.path.join(LABS[name]["lab"], "__statera__", ".harness")
    for ext in (".json", ".lock", ".denied"):
        try:
            os.unlink(os.path.join(st, agent + ext))
        except OSError:
            pass


def seed_worker(name, agent):
    """A running worker with a huge budget, so that the check is the quiet one: SubagentStart through the variant's own hook, then B and T raised in the state."""
    reset_state(name, agent)
    for script, cmd in hooks_of(name, "SubagentStart", source="murmuration:explorer"):
        if script == "budget":
            run_cmd(name, cmd, payload(name, "start", agent))
    path = os.path.join(LABS[name]["lab"], "__statera__", ".harness", agent + ".json")
    st = json.load(open(path))
    st.update(B=1e6, T=1e6, brief_read=True, warned=True)
    json.dump(st, open(path, "w"))
    # one unmeasured check: the transcript's raises are applied once, and the page cache is warm
    check = ("PostToolBatch", "a_batch") if hooks_of(name, "PostToolBatch") else ("PostToolUse", "a_post")   # w05-c4: a variant without a PostToolBatch registration checks at PostToolUse
    for script, cmd in hooks_of(name, check[0]):
        run_cmd(name, cmd, payload(name, check[1], agent))
    st = json.load(open(path))
    st.update(B=1e6, T=1e6)
    json.dump(st, open(path, "w"))


CASES = []
for k in trans:
    agent = k
    CASES += [("post_tool_use:worker-%s" % k, "PostToolUse", "Bash", None, "a_post", agent),
              ("post_tool_batch:worker-%s" % k, "PostToolBatch", None, None, "a_batch", agent),
              ("subagent_stop:worker-%s" % k, "SubagentStop", None, None, "stop", agent)]
CASES += [("post_tool_use:main", "PostToolUse", "Bash", None, "main_post", None),
          ("post_tool_batch:main", "PostToolBatch", None, None, "main_batch", None),
          ("pre_tool_use:dispatch", "PreToolUse", "Agent", None, "dispatch", None),
          ("user_prompt_submit:main", "UserPromptSubmit", None, None, "user", None),
          ("subagent_start:worker", "SubagentStart", None, "murmuration:explorer", "start", "startA"),
          ("pre_tool_use:handback-explorer-no-report", "PreToolUse", "SubagentHandback", None, "pre_hb", "hbA"),
          ("post_tool_use:handback", "PostToolUse", "SubagentHandback", None, "post_hb", list(trans)[0])]
CASES = [c for c in CASES if args.only in c[0]]

for name in variants:
    for k in trans:
        seed_worker(name, k)
    # the report check walks `__reports__`: a marker per agent so that the deny is not written again and again; the explorer's name is one with no report
    h = os.path.join(LABS[name]["lab"], "__statera__", ".harness")
    os.makedirs(h, exist_ok=True)
    open(os.path.join(h, "hbA.denied"), "w").close()


def prepare(name, case):
    cid, event, tool, source, kind, agent = case
    if cid.startswith("subagent_start"):
        reset_state(name, agent)
        shutil.rmtree(os.path.join(LABS[name]["lab"], "__statera__", ".harness", "pending"), ignore_errors=True)
    elif cid == "pre_tool_use:dispatch":
        shutil.rmtree(os.path.join(LABS[name]["lab"], "__statera__", ".harness", "pending"), ignore_errors=True)
    elif cid == "post_tool_use:handback":
        shutil.rmtree(os.path.join(LABS[name]["lab"], "__statera__", "handbacks"), ignore_errors=True)
    elif cid.startswith("subagent_stop"):
        # a stop closes the run; reopen it so that each timed stop does the same work
        path = os.path.join(LABS[name]["lab"], "__statera__", ".harness", agent + ".json")
        st = json.load(open(path))
        st.update(run_open=True)
        json.dump(st, open(path, "w"))
        shutil.rmtree(os.path.join(LABS[name]["lab"], "__statera__", "handbacks"), ignore_errors=True)


# floors: no payload, no variant
FLOORS = {"floor:sh-noop": ":", "floor:python3-c-pass": "python3 -c pass", "floor:python3-S-I-c-pass": "python3 -S -I -c pass",
          "floor:python3-S-I-import-json-os-sys": "python3 -S -I -c 'import json,os,sys'"}

cells = []
for case in CASES:
    for name in variants:
        for script, cmd in hooks_of(name, case[1], case[2], case[3]):
            cells.append(dict(kind="hook", case=case, variant=name, script=script, cmd=cmd))
if not args.no_floors and not args.only:
    for fid, fcmd in FLOORS.items():
        cells.append(dict(kind="floor", case=(fid,), variant="-", script="-", cmd=fcmd))

rnd = random.Random(args.seed)
out = open(args.out, "w")
WARM = 2
for rnd_i in range(-WARM, args.n):
    order = list(cells)
    rnd.shuffle(order)
    if args.paired:   # neighbours in time: group the cells of one case, floors stay where the shuffle put them
        ids = sorted({c["case"][0] for c in order if c["kind"] == "hook"}); rnd.shuffle(ids)
        grouped = []
        for i in ids:
            g = [c for c in order if c["kind"] == "hook" and c["case"][0] == i]
            rnd.shuffle(g)
            grouped += g
        order = grouped + [c for c in order if c["kind"] == "floor"]
    for c in order:
        if c["kind"] == "floor":
            fh = open(os.path.join(FX, "stdin.json"), "w")
            fh.write("{}\n")
            fh.close()
            wall, cpu, rc, o, e = run_cmd(next(iter(variants)), c["cmd"], "{}\n")
        else:
            case, name = c["case"], c["variant"]
            prepare(name, case)
            text = payload(name, case[4], case[5])
            wall, cpu, rc, o, e = run_cmd(name, c["cmd"], text)
        if rnd_i >= 0:
            out.write(json.dumps(dict(case=c["case"][0], variant=c["variant"], script=c["script"], round=rnd_i, wall_ms=round(wall, 3), cpu_ms=round(cpu, 3), rc=rc,
                                      out_len=len(o), err_len=len(e), out_md5=hashlib.md5(o).hexdigest()[:8])) + "\n")
            out.flush()
out.close()
