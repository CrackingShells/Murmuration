# w06-c9 verifier: runs the real hooks.json commands (`sh -c`, payload on stdin) of two plugin trees over events derived from recorded worker transcripts and compares exit code, stdout, stderr, log, hand-back files, state; inputs: --old ROOT --new ROOT --work DIR (scratch), transcripts; output: one line per transcript, EQUAL or the first difference; written independently of the author's w06c9_e2e_commands.py
import argparse, json, os, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True); ap.add_argument("--new", required=True); ap.add_argument("--work", required=True)
ap.add_argument("--jobs", type=int, default=3)
ap.add_argument("--env", action="append", default=[], help="K=V added to the environment of every command (e.g. LC_ALL=C)")
ap.add_argument("--unset", action="append", default=[])
ap.add_argument("transcripts", nargs="+")
a = ap.parse_args()
EXTRA = dict(kv.split("=", 1) for kv in a.env)


def rows(root, event, tool):
    out = []
    for g in json.load(open(root + "/hooks/hooks.json"))["hooks"].get(event, []):
        m = g.get("matcher")
        if m is None or re.fullmatch(m, tool or ""):
            for h in g["hooks"]:
                if h.get("type") == "command" and ("budget" in h["command"] or "handback" in h["command"]):
                    out.append(h["command"].replace("${CLAUDE_PLUGIN_ROOT}", root))
    return out


def build_events(tpath, sess):
    meta_p = tpath[:-6] + ".meta.json"
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    kind = meta.get("agentType") or "murmuration:explorer"
    aid = os.path.basename(tpath)[6:-6]
    tx = "%s/subagents/agent-%s.jsonl" % (sess, aid)
    raw = open(tpath, "rb").read()
    lines = raw.split(b"\n")
    offs, pos = [], 0
    for l in lines:
        pos += len(l) + 1
        offs.append(min(pos, len(raw)))
    recs = [json.loads(l) if l.strip() else {} for l in lines]
    brief = ""
    for r in recs:
        if r.get("type") == "user":
            c = r["message"]["content"]
            brief = c if isinstance(c, str) else "".join(b.get("text", "") for b in c if isinstance(b, dict))
            break
    base = dict(session_id="s", transcript_path=sess + ".jsonl", permission_mode="auto")
    wk = dict(base, agent_id=aid, agent_type=kind)
    ev = [(None, dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu0", tool_input=dict(subagent_type=kind, prompt=brief, name=meta.get("name", "explorer-w03-x")))),
          (None, dict(wk, hook_event_name="SubagentStart"))]
    calls, owner, need, got, last, fired = {}, {}, {}, {}, "", set()
    for i, r in enumerate(recs):
        m, c = r.get("message") or {}, (r.get("message") or {}).get("content")
        if r.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b["id"]] = (b["name"], b.get("input"))
                    owner[b["id"]] = m.get("id") or b["id"]
                    need.setdefault(owner[b["id"]], set()).add(b["id"])
                    if b["name"] == "SubagentHandback":
                        ev.append((offs[i], dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback", tool_input=b.get("input"), tool_use_id=b["id"])))
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    last = b["text"]
        elif r.get("type") == "user" and isinstance(c, list):
            ids = [b["tool_use_id"] for b in c if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in calls]
            for k, t in enumerate(ids):
                ev.append((offs[i] if k == 0 else None, dict(wk, hook_event_name="PostToolUse", tool_name=calls[t][0], tool_input=calls[t][1], tool_response="ok", tool_use_id=t)))
            for t in ids:
                g = owner[t]
                if g in fired:
                    continue
                got.setdefault(g, set()).add(t)
                if got[g] == need[g]:
                    ev.append((None, dict(wk, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name=calls[x][0], tool_use_id=x) for x in sorted(need[g])])))
                    fired.add(g)
    ev.append((len(raw), dict(wk, hook_event_name="SubagentStop", agent_transcript_path=tx, last_assistant_message=last)))
    return ev, meta, aid, tx, raw


NORM = re.compile(r"[0-9.]+ of ([0-9.]+) min \([0-9]+%\)")


def run_arm(tpath, root, tag, idx):
    d = "%s/%s/%d/run" % (os.path.abspath(a.work), tag, idx)
    shutil.rmtree(d, ignore_errors=True)
    lab, sess = d + "/lab", d + "/sess"
    os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__"); os.makedirs(sess + "/subagents")
    ev, meta, aid, tx, raw = build_events(tpath, sess)
    json.dump(meta, open("%s/subagents/agent-%s.meta.json" % (sess, aid), "w"))
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR" and k not in a.unset}
    env.update(EXTRA, CLAUDE_PLUGIN_ROOT=root)
    out = []
    for upto, payload in ev:
        if upto is not None:
            open(tx, "wb").write(raw[:upto])
        payload = dict(payload, cwd=lab)
        for c in rows(root, payload["hook_event_name"], payload.get("tool_name")):
            p = subprocess.run(["sh", "-c", c], input=json.dumps(payload), capture_output=True, text=True, cwd=lab, env=env)
            norm = lambda s: NORM.sub(r"T of \1 min", s.replace(d, "<D>"))
            out.append((payload["hook_event_name"], payload.get("tool_name"), p.returncode, norm(p.stdout), norm(p.stderr)))
    snap = {"log": [], "hb": {}, "state": {}}
    lg = lab + "/__statera__/harness.jsonl"
    if os.path.exists(lg):
        snap["log"] = [json.dumps({k: v for k, v in json.loads(l).items() if k not in ("t", "active_s", "t_frac")}, sort_keys=True) for l in open(lg)]
    hb = lab + "/__statera__/handbacks"
    if os.path.isdir(hb):
        snap["hb"] = {n: [l for l in open(hb + "/" + n, encoding="utf-8", errors="replace").read().splitlines() if not l.startswith("## hand-back")] for n in sorted(os.listdir(hb))}
    st = lab + "/__statera__/.harness"
    for n in sorted(os.listdir(st)) if os.path.isdir(st) else []:
        if n.endswith(".json"):
            dd = json.load(open(st + "/" + n))
            snap["state"][n] = {k: v for k, v in dd.items() if k not in ("sc",) and not isinstance(v, float) or k in ("B", "T", "used")}
        else:
            snap["state"][n] = "file"
    shutil.rmtree(d, ignore_errors=True)
    return out, snap


def one(args):
    idx, t = args
    o, so = run_arm(t, os.path.abspath(a.old), "old", idx)
    n, sn = run_arm(t, os.path.abspath(a.new), "new", idx)
    diff = None
    if len(o) != len(n):
        diff = "command starts %d / %d" % (len(o), len(n))
    else:
        for i, (x, y) in enumerate(zip(o, n)):
            if x != y:
                diff = "start %d %s/%s old=%r new=%r" % (i, x[0], x[1], x[2:], y[2:]); break
    if diff is None:
        for k in ("log", "hb", "state"):
            if so[k] != sn[k]:
                if isinstance(so[k], list):
                    j = next((q for q in range(min(len(so[k]), len(sn[k]))) if so[k][q] != sn[k][q]), min(len(so[k]), len(sn[k])))
                    diff = "%s differs at %d of %d/%d: old=%s new=%s" % (k, j, len(so[k]), len(sn[k]), so[k][j:j + 1], sn[k][j:j + 1])
                else:
                    diff = "%s differs old=%s new=%s" % (k, json.dumps(so[k])[:400], json.dumps(sn[k])[:400])
                break
    blocks = sum('"decision": "block"' in x[3] for x in o)
    nonempty = sum(bool(x[3]) for x in o)
    denies = sum("permissionDecision" in x[3] and "deny" in x[3] for x in o)
    return "%s | starts=%d nonempty=%d block=%d deny=%d | %s" % (os.path.basename(t), len(o), nonempty, blocks, denies, "EQUAL" if diff is None else "DIFF " + diff), diff is None


bad = 0
with ThreadPoolExecutor(a.jobs) as ex:
    for line, ok in ex.map(one, list(enumerate(a.transcripts))):
        print(line, flush=True)
        bad += not ok
sys.exit(1 if bad else 0)
