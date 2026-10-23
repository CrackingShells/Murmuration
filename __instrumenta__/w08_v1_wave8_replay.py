# Replays hook events built from this wave's own live worker transcripts (subagents/agent-*.jsonl of the wave-8 project folder, real timestamps, real briefs, real last messages and hand-back messages) through the Python scripts (fixed-clock shim) and through the Rust test build, comparing stdout, exit code, stderr and the whole lab folder after every event; counts events handled by the port and events delegated to Python.
# inputs: author's worktree (scripts, shim), a Rust test build (--features testclock), the wave-8 transcripts (copied first, read only); outputs: a JSON summary and a diff file in --out. Written by the verifier without importing the author's replay code.
# usage: python3 -I w08_v1_wave8_replay.py --repo WT --rust BIN --projdir DIR --scratch DIR --out DIR [--modes none,auto,default]
import argparse, glob, json, os, shutil, subprocess, sys, datetime, collections


def ts_epoch(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def load(path):
    recs = []
    for l in open(path, "rb").read().splitlines():
        try:
            recs.append((l, json.loads(l)))
        except Exception:
            recs.append((l, None))
    return recs


def last_text(recs):
    for _, r in reversed(recs):
        if r and r.get("type") == "assistant":
            c = r.get("message", {}).get("content")
            if isinstance(c, list):
                t = "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
                if t:
                    return t
    return None


def handback_msgs(recs):
    out = []
    for _, r in recs:
        if r and r.get("type") == "assistant":
            c = r.get("message", {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                        out.append(b.get("input"))
    return out


def snap(lab):
    out = {}
    for root, dirs, files in os.walk(lab):
        for d in dirs:
            out[os.path.relpath(os.path.join(root, d), lab) + "/"] = b""
        for f in files:
            p = os.path.join(root, f)
            out[os.path.relpath(p, lab)] = open(p, "rb").read()
    return out


def run(cmd, raw, now, dlog, repo):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "MURMURATION_NOW")}
    env.update(LC_ALL="en_US.UTF-8", CLAUDE_PLUGIN_ROOT=repo, MURMURATION_NOW=repr(now), MURMURATION_DELEGATE_LOG=dlog,
               MURMURATION_DELEGATE_SHIM=os.path.join(repo, "__instrumenta__", "w08c1_pyshim.py"))
    p = subprocess.run(cmd, input=raw, capture_output=True, timeout=60, env=env, cwd="/private/tmp")
    return p.returncode, p.stdout, p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rust", required=True)
    ap.add_argument("--projdir", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--modes", default="none,auto,default")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frozen = os.path.join(a.scratch, "frozen")
    os.makedirs(frozen, exist_ok=True)
    for p in glob.glob(os.path.join(a.projdir, "*", "subagents", "agent-*.*")):
        shutil.copy(p, frozen)
    agents = sorted(glob.glob(os.path.join(frozen, "agent-*.jsonl")))
    tot = collections.Counter()
    bykind = collections.Counter()
    diffs = []
    for tp in agents:
        aid = os.path.basename(tp)[6:-6]
        meta = {}
        try:
            meta = json.load(open(tp[:-6] + ".meta.json"))
        except Exception:
            pass
        atype = meta.get("agentType") or "murmuration:explorer"
        recs = load(tp)
        recs = [x for x in recs if x[1] is not None]
        n = len(recs)
        if n < 3:
            continue
        times = [ts_epoch(r["timestamp"]) for _, r in recs if isinstance(r.get("timestamp"), str)]
        if not times:
            continue
        hb = handback_msgs(recs)
        lt = last_text(recs)
        for mode in a.modes.split(","):
            impl_res = {}
            for impl in ("py", "rs"):
                base = os.path.join(a.scratch, "run", "%s-%s" % (aid, mode))   # same path for both implementations
                shutil.rmtree(base, ignore_errors=True)
                lab, sess = os.path.join(base, "lab"), os.path.join(base, "sess")
                os.makedirs(os.path.join(sess, "subagents"))
                os.makedirs(os.path.join(lab, "__statera__"))
                dlog = os.path.join(base, "delegate.log")
                if os.path.exists(tp[:-6] + ".meta.json"):
                    shutil.copy(tp[:-6] + ".meta.json", os.path.join(sess, "subagents", "agent-%s.meta.json" % aid))
                steps = []
                pm = None if mode == "none" else mode

                def ev(which, kind, now, **kw):
                    d = dict(cwd=lab, hook_event_name=kind, transcript_path=os.path.join(sess, "x.jsonl"), agent_id=aid, agent_type=atype)
                    if pm:
                        d["permission_mode"] = pm
                    d.update(kw)
                    steps.append((which, now, json.dumps(d).encode()))
                tw = lambda k: os.path.join(sess, "subagents", "agent-%s.jsonl" % aid)
                cuts = sorted(set([max(2, int(n * f)) for f in (0.1, 0.25, 0.5, 0.75, 1.0)]))
                steps.append(("tx", cuts[0], None))
                ev("budget", "SubagentStart", times[0])
                for c in cuts:
                    t_c = max(ts_epoch(r["timestamp"]) for _, r in recs[:c] if isinstance(r.get("timestamp"), str)) if any(isinstance(r.get("timestamp"), str) for _, r in recs[:c]) else times[0]
                    steps.append(("tx", c, None))
                    ev("budget", "PostToolBatch", t_c, tool_calls=[dict(tool_name="Bash", tool_use_id="t")])
                    ev("budget", "PostToolUse", t_c + 0.01, tool_name="Bash", tool_use_id="t")
                    ev("handback", "PreToolUse", t_c + 0.02, tool_name="SubagentHandback", tool_input={"message": "m"})
                ev("budget", "PostToolBatch", times[-1] + 1, tool_calls=[dict(tool_name="SubagentHandback")])
                for m in hb[:2]:
                    ev("handback", "PostToolUse", times[-1] + 2, tool_name="SubagentHandback", tool_input=m if isinstance(m, dict) else {"message": str(m)})
                kw = dict(agent_transcript_path=tw(0))
                if lt is not None:
                    kw["last_assistant_message"] = lt
                ev("handback", "SubagentStop", times[-1] + 3, **kw)
                ev("budget", "SubagentStop", times[-1] + 3.01, **kw)
                res = []
                for st in steps:
                    if st[0] == "tx":
                        open(tw(0), "wb").write(b"\n".join(l for l, _ in recs[:st[1]]) + b"\n")
                        continue
                    which, now, raw = st
                    cmd = ([sys.executable, "-S", "-I", os.path.join(a.repo, "__instrumenta__", "w08c1_pyshim.py"), os.path.join(a.repo, "scripts"), which]
                           if impl == "py" else [a.rust, which])
                    o = run(cmd, raw, now, dlog, a.repo)
                    res.append((which, o, snap(lab)))
                impl_res[impl] = (res, len(open(dlog).read().split()) if os.path.exists(dlog) else 0)
            (ra, _), (rb, dele) = impl_res["py"], impl_res["rs"]
            for i, ((w, oa, sa), (_, ob, sb)) in enumerate(zip(ra, rb)):
                tot["events"] += 1
                bykind[w] += 1
                bad = oa != ob or sa != sb
                if bad:
                    tot["differing"] += 1
                    diffs.append((aid, mode, i, w, oa[0], ob[0], oa[1][:200], ob[1][:200], [k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)]))
            tot["delegated"] += dele
            tot["scenarios"] += 1
    res = dict(agents=len(agents), **tot, by_hook=dict(bykind))
    json.dump(res, open(os.path.join(a.out, "wave8_replay.json"), "w"), indent=1)
    open(os.path.join(a.out, "wave8_replay_diffs.txt"), "w").write("\n".join(repr(d) for d in diffs))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
