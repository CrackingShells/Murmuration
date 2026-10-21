# E5 (w05-c1) runner: from a repo commit and a run root, builds plugin exports A and B (B = A + the waiting paragraph in the four worker agent files), builds one lab per run with an 8-part reference (about 120k tokens) and a 9-minute job, launches headless author workers side by side, samples each run's process tree, and writes per-run metrics m1..m7 (JSON, CSV of requests) from the stream and the transcript.
"""usage:
  python3 -I w05c1_wait_arms.py export ROOT COMMIT          -> ROOT/plugin_A, ROOT/plugin_B, ROOT/export_commit.txt
  python3 -I w05c1_wait_arms.py run ROOT COMMIT SECS ID...  ID = <arm><n> or pilot-<arm><n>, e.g. A1 B1 pilot-A1; SECS = job length in seconds (540 for E5)
  python3 -I w05c1_wait_arms.py table ROOT OUTDIR ID...     -> OUTDIR/metrics.json, metrics.md, requests_<id>.csv (no account identifiers)
  python3 -I w05c1_wait_arms.py apply AGENTS_DIR            -> inserts the paragraph into the four agent files in AGENTS_DIR (the same insertion arm B uses)
The model samples; there is no seed (the job seed is fixed per id: 20261100 + n). Stdlib only. Quick check: `run ROOT COMMIT 60 pilot-B1` (job of 60 s), about USD 0.7.
"""
import csv, glob, json, os, re, shutil, subprocess, sys, time, hashlib, threading

H = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(H)

PARAGRAPH = ("Waiting: no tool call waits more than 4 minutes (a longer one loses the prompt cache and leaves your messages unread). "
             "Start a long job in the background and note its pid (`cmd > log 2>&1 & echo $! > job.pid`), then poll with "
             "`timeout 240 sh -c 'until <check>; do sleep 5; done'` (Bash `timeout: 270000`); a bare `sleep` of 30 s or more is blocked. "
             "Before you hand back, `kill` each background job you started, by its pid, and check that it is gone.\n\n")
ANCHORS = {"author.md": "Use the notation of `__design__/framing.md`", "explorer.md": "Use the project's notation from",
           "reproducer.md": "End with your puzzles in", "proof-adversary.md": "End with your puzzles in"}
K_CONST = 13
REF_PARTS = 8
REF_PART_BYTES = 60000


def apply_paragraph(agents_dir):
    for name, anchor in ANCHORS.items():
        p = os.path.join(agents_dir, name)
        s = open(p).read()
        if PARAGRAPH in s:
            continue
        i = s.rfind(anchor)
        assert i > 0 and s.count(anchor) == 1, (name, s.count(anchor))
        open(p, "w").write(s[:i] + PARAGRAPH + s[i:])


def export(root, commit):
    for d in ("plugin_A", "plugin_B"):
        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
    os.makedirs(os.path.join(root, "plugin_A"))
    arc = subprocess.run(["git", "archive", commit, "agents", "skills", "scripts", "hooks", ".claude-plugin"], cwd=REPO, check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", os.path.join(root, "plugin_A")], input=arc, check=True)
    shutil.copytree(os.path.join(root, "plugin_A"), os.path.join(root, "plugin_B"))
    apply_paragraph(os.path.join(root, "plugin_B", "agents"))
    for d in glob.glob(os.path.join(root, "plugin_*", "**", "__pycache__"), recursive=True):
        shutil.rmtree(d, ignore_errors=True)
    open(os.path.join(root, "export_commit.txt"), "w").write(commit + "\n")


JOB = '''# job9.py: a provided job. Runs about 9 minutes (E5_JOB_SECONDS, default 540), logs a line every 30 s, then writes job/result.txt with one number; writes its pid to job/job.pid.
import argparse, hashlib, os, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, required=True); a = ap.parse_args()
d = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(d, "job.pid"), "w").write(str(os.getpid()) + "\\n")
secs = float(os.environ.get("E5_JOB_SECONDS", "540")); n = int(secs // 30); t0 = time.time(); h = str(a.seed).encode()
for k in range(1, n + 1):
    h = hashlib.sha256(h).digest()
    time.sleep(max(0, t0 + 30 * k - time.time()))
    print("tick", k, "of", n, flush=True)
open(os.path.join(d, "result.txt"), "w").write("RESULT %d\\n" % (int.from_bytes(h[:4], "big") % 100000))
print("done", flush=True)
'''


def expected(seed, secs):
    h = str(seed).encode()
    for _ in range(int(secs // 30)):
        h = hashlib.sha256(h).digest()
    return int.from_bytes(h[:4], "big") % 100000


def ref_files(commit):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit], cwd=REPO, check=True, capture_output=True, text=True).stdout.split("\n")
    keep = [f for f in sorted(out) if f.endswith(".md") and (f.startswith("__reports__/genesis/") or f.startswith("validation/runs/") or f.startswith("__pondus__/w01-"))]
    return keep


def build_refs(commit, dest):
    os.makedirs(dest, exist_ok=True)
    text = ""
    for f in ref_files(commit):
        text += "\n\n# SOURCE: %s\n\n" % f + subprocess.run(["git", "show", "%s:%s" % (commit, f)], cwd=REPO, check=True, capture_output=True, text=True).stdout
        if len(text) > REF_PARTS * REF_PART_BYTES + 5000:
            break
    parts, cur = [], ""
    for line in text.splitlines(keepends=True):
        cur += line
        if len(cur) >= REF_PART_BYTES and len(parts) < REF_PARTS - 1:
            parts.append(cur); cur = ""
    parts.append(cur)
    parts[-1] += "\n\n## Lab constant\n\nThe lab's scaling constant for the wave-5 job figure is K = %d.\n" % K_CONST
    for i, p in enumerate(parts, 1):
        open(os.path.join(dest, "part%d.md" % i), "w").write("# Reference, part %d of %d\n\n" % (i, len(parts)) + p)
    return len(parts)


def seed_of(rid):
    return 20261100 + int(re.search(r"(\d+)$", rid).group(1))


def brief(rid, secs):
    return ("Your name is author-w05-1-%s. Claim id: w05-c9. Your verifier will be reproducer-w05-9.\n"
            "Hunch, from the principal investigator: the provided job `job/job9.py` (seed %d) yields one number; file that number with one derived figure, "
            "the number multiplied by the lab constant K. Work by experiment.\n"
            "Steps: (1) read the lab's reference, `ref/part1.md` to `ref/part%d.md`, every part whole with the Read tool; it holds the lab's background and the constant K. "
            "(2) run the job with `python3 job/job9.py --seed %d` from the lab folder; it takes about 9 minutes and writes `job/result.txt`; do not reimplement it. "
            "(3) file the claim head in `__pondus__/w05-c9.md` with the number and the derived figure, labelled by what you ran.\n"
            "Budget: USD 3.00\nTime: min 25" % (rid, seed_of(rid), REF_PARTS, seed_of(rid)))


def dispatch_prompt(rid, secs):
    """The worker is a subagent (as in wave 4: a main-thread headless worker gets a 1-hour cache TTL, a subagent a 5-minute one); a cheap haiku main thread dispatches it."""
    return ("Dispatch one worker with the Agent tool: subagent_type murmuration:author, and as its prompt exactly the text between the two lines of dashes, unchanged. "
            "When it hands back, stop; do not do its work yourself.\n---\n%s\n---" % brief(rid, secs))


def snapshot_tree(root_pid):
    out = subprocess.run(["ps", "-ax", "-o", "pid=,ppid=,lstart=,command="], capture_output=True, text=True).stdout
    rows = {}
    for l in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\w{3} \w{3}\s+\d+ [\d:]+ \d{4})\s+(.*)", l)
        if m:
            rows[int(m.group(1))] = (int(m.group(2)), m.group(3), m.group(4))
    kids, frontier = set(), {root_pid}
    while frontier:
        nxt = {p for p, (pp, _, _) in rows.items() if pp in frontier and p not in kids}
        kids |= nxt; frontier = nxt
    return {p: (rows[p][1], rows[p][2][:100]) for p in kids}


def final_result_seen(path):
    """True when a `result` record follows the first completion notice of the dispatched agent (the first `result` is the dispatcher's own, printed while the worker still runs)."""
    seen_done = False
    for l in open(path):
        if '"subtype":"task_notification"' in l and '"handback"' in l:
            seen_done = True
        elif seen_done and '"type":"result"' in l:
            return True
    return False


def run(root, commit, secs, ids):
    export(root, commit)
    refs = os.path.join(root, "refs"); n = build_refs(commit, refs)
    assert n == REF_PARTS
    procs = {}
    for rid in ids:
        arm = re.search(r"([AB])\d+$", rid).group(1)
        plugin = os.path.join(root, "plugin_" + arm)
        base = os.path.join(root, "runs", rid); shutil.rmtree(base, ignore_errors=True)
        lab = os.path.join(base, "lab"); os.makedirs(os.path.join(lab, "ref")); os.makedirs(os.path.join(lab, "job"))
        for f in os.listdir(refs):
            shutil.copy(os.path.join(refs, f), os.path.join(lab, "ref", f))
        open(os.path.join(lab, "job", "job9.py"), "w").write(JOB)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        env.update(COLGREP_DATA_DIR=os.path.join(base, "colgrep"), CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0", E5_JOB_SECONDS=str(secs))
        subprocess.run(["git", "init", "-q", "."], cwd=lab, check=True)
        subprocess.run([sys.executable, os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab], input="What does a worker do while a long job runs? (E5 test lab)",
                       text=True, capture_output=True, env=env, cwd=lab, timeout=300, check=True)
        open(os.path.join(lab, ".gitignore"), "a").write(".claude/settings.local.json\n.colgrep/\nref/\njob/\n")
        open(os.path.join(base, "brief.txt"), "w").write(brief(rid, secs))
        cfg = os.path.join(lab, ".claude", "settings.local.json")
        if os.path.exists(cfg):                      # lab_init sets "agent": research-pi; the dispatcher must be the plain cheap main thread
            c = json.load(open(cfg)); c.pop("agent", None); json.dump(c, open(cfg, "w"), indent=1)
        cmd = ["claude", "-p", "--plugin-dir", plugin, "--model", "haiku", "--permission-mode", "auto", "--output-format", "stream-json", "--verbose", dispatch_prompt(rid, secs)]
        t0 = time.time()
        p = subprocess.Popen(cmd, cwd=lab, env=env, stdin=subprocess.DEVNULL, stdout=open(os.path.join(base, "run.jsonl"), "w"), stderr=open(os.path.join(base, "run.err"), "w"))
        procs[rid] = dict(p=p, t0=t0, seen={}, result_at=None, base=base)
        print(rid, "launched", p.pid, flush=True)
        time.sleep(2.5)
    alive = set(ids)
    while alive:
        for rid in list(alive):
            r = procs[rid]; p = r["p"]
            for pid, v in snapshot_tree(p.pid).items():
                r["seen"].setdefault(pid, v)
            if r["result_at"] is None and final_result_seen(os.path.join(r["base"], "run.jsonl")):
                r["result_at"] = time.time()
            done = p.poll() is not None
            if r["result_at"] is None and done:
                r["result_at"] = time.time()
            if r["result_at"] is not None and time.time() - r["result_at"] > 30:
                still = {}
                now = subprocess.run(["ps", "-ax", "-o", "pid=,lstart="], capture_output=True, text=True).stdout
                live = {}
                for l in now.splitlines():
                    m = re.match(r"\s*(\d+)\s+(.*)", l)
                    if m:
                        live[int(m.group(1))] = m.group(2)[:100].strip()
                for pid, (ls, cmdl) in r["seen"].items():
                    if live.get(pid, "").strip() == ls.strip():
                        still[pid] = cmdl
                if p.poll() is None:
                    p.terminate()                # this run's own claude process, by its handle
                json.dump(dict(id=rid, claude_pid=p.pid, t0=r["t0"], result_at=r["result_at"], ended=time.time(), exit=p.poll(), seen=len(r["seen"]),
                               alive_30s_after_result={str(k): v for k, v in still.items()}), open(os.path.join(r["base"], "proc.json"), "w"), indent=1)
                alive.discard(rid)
                print(rid, "ended; alive after 30 s:", len(still), flush=True)
            elif time.time() - r["t0"] > 1800:
                p.terminate(); r["result_at"] = time.time() - 31
        time.sleep(3)


def load_transcript(session):
    c = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % session))
    return c[0] if c else None


def ts(s):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def metrics(root, rid, secs):
    base = os.path.join(root, "runs", rid)
    res = None; session = None
    for l in open(os.path.join(base, "run.jsonl")):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get("type") == "result":
            res = d
        session = d.get("session_id", session)
    tp = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % session)), key=os.path.getsize)[-1]
    reqs, calls, order = {}, {}, []
    for l in open(tp):
        d = json.loads(l); m = d.get("message") if isinstance(d.get("message"), dict) else None
        if not m or "timestamp" not in d:
            continue
        t = ts(d["timestamp"])
        if d.get("type") == "assistant":
            mid = m.get("id"); u = m.get("usage", {})
            if mid not in reqs:
                reqs[mid] = dict(t=t, ctx=0, cr=0, cw=0, inp=0, out=0); order.append(mid)
            r = reqs[mid]
            r["ctx"] = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            r["cr"] = u.get("cache_read_input_tokens", 0); r["cw"] = u.get("cache_creation_input_tokens", 0); r["inp"] = u.get("input_tokens", 0); r["out"] = max(r["out"], u.get("output_tokens", 0))
            for c in m.get("content", []):
                if c.get("type") == "tool_use":
                    calls[c["id"]] = dict(t0=t, name=c["name"], inp=json.dumps(c.get("input"))[:160], dur=None, err=False, text="")
        elif d.get("type") == "user" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in calls:
                    k = calls[c["tool_use_id"]]; k["dur"] = t - k["t0"]
                    tx = c.get("content"); tx = tx if isinstance(tx, str) else " ".join(x.get("text", "") for x in tx if isinstance(x, dict))
                    k["err"] = bool(c.get("is_error")); k["text"] = tx[:200]
    rows = []
    prev = None
    cold = 0
    for mid in order:
        r = reqs[mid]
        gap = None if prev is None else r["t"] - reqs[prev]["t"]
        is_cold = gap is not None and gap > 300 and r["cr"] < 0.5 * r["ctx"]
        cold += is_cold
        rows.append(dict(i=len(rows), t=round(r["t"] - reqs[order[0]]["t"], 1), gap_s=None if gap is None else round(gap, 1), ctx=r["ctx"], cache_read=r["cr"], cache_write=r["cw"], cold=int(is_cold)))
        prev = mid
    bash_calls = [k for k in calls.values() if k["name"] == "Bash"]
    durs = [(k["dur"] or 0, k["name"], k["inp"]) for k in calls.values()]
    longest = max(durs) if durs else (0, "", "")
    blocked = [k for k in calls.values() if k["err"] and (k["text"].startswith("Blocked") or "No such tool" in k["text"] or "<tool_use_error>Blocked" in k["text"])]
    blocked += [k for k in calls.values() if not k["err"] and k["text"].startswith("Blocked")]
    lab = os.path.join(base, "lab")
    claim = os.path.join(lab, "__pondus__", "w05-c9.md")
    ctext = open(claim).read() if os.path.exists(claim) else ""
    seed = seed_of(rid) if not rid.startswith("pilot") or True else None
    exp = expected(seed, secs); exp2 = exp * K_CONST
    nums = set(re.findall(r"\d+", ctext.replace(",", "")))
    m5 = str(exp) in nums and str(exp2) in nums
    proc = json.load(open(os.path.join(base, "proc.json"))) if os.path.exists(os.path.join(base, "proc.json")) else {}
    out = dict(id=rid, requests=len(order), max_ctx=max(r["ctx"] for r in reqs.values()),
               ctx_at_first_wait=next((rows[i]["ctx"] for i, mid in enumerate(order) if i + 1 < len(rows) and (rows[i + 1]["gap_s"] or 0) > 60), None),
               m1_cold_midrun=cold, m2_longest_tool_s=round(longest[0], 1), m2_longest_tool=longest[1] + " " + longest[2][:100],
               max_gap_between_requests_s=max([r["gap_s"] or 0 for r in rows]),
               m3_cost_usd=res.get("total_cost_usd") if res else None, m4_wall_s=round(proc.get("ended", 0) - proc.get("t0", 0), 1) if proc else None,
               m4_to_result_s=round(proc.get("result_at", 0) - proc.get("t0", 0), 1) if proc else None,
               m5_correct=m5, expected=exp, expected_derived=exp2, claim_filed=bool(ctext),
               m6_alive_30s=len(proc.get("alive_30s_after_result", {})), m6_alive_detail=proc.get("alive_30s_after_result", {}),
               m7_blocked_or_failed_waits=len(blocked), m7_texts=[k["text"][:90] for k in blocked],
               bash_calls=len(bash_calls), bg_calls=sum(1 for k in bash_calls if "run_in_background" in k["inp"]), backgrounded_by_timeout=sum(1 for k in calls.values() if "moved to the background" in k["text"]))
    return out, rows


def table(root, outdir, ids):
    os.makedirs(outdir, exist_ok=True)
    allm = []
    for rid in ids:
        secs = 60 if False else int(open(os.path.join(root, "runs", rid, "brief.txt")).read() and json.load(open(os.path.join(root, "secs.json")))[rid])
        m, rows = metrics(root, rid, secs)
        allm.append(m)
        with open(os.path.join(outdir, "requests_%s.csv" % rid), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(allm, open(os.path.join(outdir, "metrics.json"), "w"), indent=1)
    keys = ["id", "requests", "max_ctx", "ctx_at_first_wait", "m1_cold_midrun", "m2_longest_tool_s", "max_gap_between_requests_s", "m3_cost_usd", "m4_wall_s", "m5_correct", "m6_alive_30s", "m7_blocked_or_failed_waits", "bash_calls", "bg_calls", "backgrounded_by_timeout"]
    with open(os.path.join(outdir, "metrics.md"), "w") as fh:
        fh.write("| " + " | ".join(keys) + " |\n|" + "|".join(":--" for _ in keys) + "|\n")
        for m in allm:
            fh.write("| " + " | ".join(str(m[k]) for k in keys) + " |\n")
    print(open(os.path.join(outdir, "metrics.md")).read())


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "export":
        export(a[1], a[2])
    elif a[0] == "run":
        root, commit, secs, ids = a[1], a[2], int(a[3]), a[4:]
        os.makedirs(root, exist_ok=True)
        sj = os.path.join(root, "secs.json"); cur = json.load(open(sj)) if os.path.exists(sj) else {}
        cur.update({i: secs for i in ids}); json.dump(cur, open(sj, "w"))
        run(root, commit, secs, ids)
    elif a[0] == "table":
        table(a[1], a[2], a[3:])
    elif a[0] == "apply":
        apply_paragraph(a[1])
