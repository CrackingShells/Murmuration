# q3 (no regression: same files as main's script except where the origin rule drops; added wall time inside the process, 20 runs) and q4 (failure cases incl. a 50 MB transcript) of w07-c2; inputs: argv[1] = branch user_words.py, argv[2] = main's user_words.py, argv[3] = scratch folder under /private/tmp, `--quick` = 5 timing runs and a 5 MB transcript; output: stdout tables. Seeds: random.Random(7).
import json, sys, os, time, random, statistics, importlib.util, subprocess, tempfile, shutil, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from w07c2_population import population
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
sys.argv[1], sys.argv[2] = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
new, old = load(sys.argv[1], "new"), load(sys.argv[2], "old")
scratch = os.path.abspath(sys.argv[3]); assert scratch.startswith("/private/tmp/"); os.makedirs(scratch, exist_ok=True)
quick = "--quick" in sys.argv; RUNS = 5 if quick else 20; BIG = (5 if quick else 50) * 1000 * 1000
rng = random.Random(7)
# ---- q3a: decisions on recorded payloads and on replayed prompts, both scripts with the write replaced by a recorder
def recorder(mod):
    out = []
    mod.append_words = lambda root, text, when=None: out.append(text) or "x"
    mod.project_root = lambda event: "LAB"
    return out
rn, ro = recorder(new), recorder(old)
payloads = []
LABDIR = os.environ.get("W07C2_LAB", "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/xenodochial-franklin-bc67fb")  # read-only: the recorded payload files live in the lab checkout
for f in sorted(set(glob.glob(os.path.join(HERE, "..", "__reports__", "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(LABDIR, "__reports__", "**", "*.jsonl"), recursive=True))):
    if os.path.basename(f) in ("v1_hook_inputs.jsonl", "hook_inputs.jsonl", "recorded_payloads_rec1.jsonl"):
        for line in open(f, errors="replace"):
            try: d = json.loads(line)
            except ValueError: continue
            if isinstance(d, dict) and isinstance(d.get("payload"), str):
                try: d = json.loads(d["payload"])
                except ValueError: continue
            elif isinstance(d, dict) and isinstance(d.get("input"), dict): d = d["input"]
            if isinstance(d, dict) and isinstance(d.get("prompt"), str): payloads.append(("recorded:" + os.path.basename(f), d))
n_recorded = len(payloads)
pool = []
for path in population():
    for line in open(path, "rb"):
        if b'"user"' not in line: continue
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID") or not d.get("promptId"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list): c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if isinstance(c, str) and c.strip(): pool.append((path, d["promptId"], c, d))
sample = rng.sample(pool, min(600, len(pool)))
# make sure every category is in the sample
seen = set(); extra = []
for path, pid, c, d in pool:
    key = (new.record_mark(d), (d.get("origin") or {}).get("kind") if isinstance(d.get("origin"), dict) else None, d.get("turnOrigin"))
    if key not in seen: seen.add(key); extra.append((path, pid, c, d))
for path, pid, c, d in sample + extra:
    payloads.append(("replay", {"prompt": c, "prompt_id": pid, "transcript_path": path, "cwd": "/x", "hook_event_name": "UserPromptSubmit"}))
same = diff = 0; diffs = []; by = {}
for kind, ev in payloads:
    rn.clear(); ro.clear()
    new.handle(dict(ev)); old.handle(dict(ev))
    stored_new, stored_old = list(rn), list(ro)
    if stored_new == stored_old: same += 1
    else:
        diff += 1
        # a difference is allowed only when old stored and new dropped, and the transcript record marks the prompt as not typed
        ok = stored_new == [] and len(stored_old) == 1 and new.human_prompt(dict(ev), wait=0) is False
        diffs.append((kind, ok))
    by[kind.split(":")[0]] = by.get(kind.split(":")[0], 0) + 1
print("q3a payloads: %d recorded payloads, %d replayed prompts (random sample of 600 with seed 7 plus one per category: %d)" % (n_recorded, len(payloads) - n_recorded, len(extra)))
print("identical stored text: %d; different: %d, of which explained by the origin rule dropping a prompt the record marks as not typed: %d, unexplained: %d" % (same, diff, sum(1 for k, ok in diffs if ok), sum(1 for k, ok in diffs if not ok)))
# ---- q3b: timing of handle() inside the process, real writes into a scratch lab
def timing(mod, ev, runs):
    lab = tempfile.mkdtemp(dir=scratch); os.makedirs(os.path.join(lab, "__statera__"))
    mod.project_root = lambda event, lab=lab: lab
    mod.append_words = load(sys.argv[1], "tmp").append_words
    ts = []
    for _ in range(runs):
        t = time.perf_counter(); mod.handle(dict(ev)); ts.append(time.perf_counter() - t)
    shutil.rmtree(lab); return ts
def mk_transcript(path, size, pid, mark, record_last=True):
    rec = json.dumps({"type": "user", "promptId": pid, "message": {"content": "words"}, **mark}) + "\n"
    with open(path, "w") as fh:
        chunk = json.dumps({"type": "attachment", "pad": "y" * 900}) + "\n"
        n = max(0, size // len(chunk))
        for _ in range(n): fh.write(chunk)
        if record_last: fh.write(rec)
tp_small, tp_big, tp_miss = [os.path.join(scratch, x) for x in ("small.jsonl", "big.jsonl", "miss.jsonl")]
human = {"origin": {"kind": "human"}, "promptSource": "sdk", "turnOrigin": "human", "entrypoint": "claude-desktop"}
mk_transcript(tp_small, 20000, "pid-small", human); mk_transcript(tp_big, BIG, "pid-big", human); mk_transcript(tp_miss, 20000, "pid-miss", human, record_last=False)
cases = [("record in the tail of a 20 KB transcript", tp_small, "pid-small"), ("record in the tail of a %d MB transcript" % (BIG // 1000000), tp_big, "pid-big"),
         ("record not there (the 0.3 s wait runs out)", tp_miss, "pid-miss"), ("no prompt_id", tp_small, None)]
print("\nq3b: handle() wall time inside the process, %d runs each (ms): main median, new median, new minus main at the median, new max" % RUNS)
for name, tp, pid in cases:
    ev = {"prompt": "some words to keep", "cwd": "/x", "transcript_path": tp}
    if pid: ev["prompt_id"] = pid
    to = timing(old, ev, RUNS); tn = timing(new, ev, RUNS)
    print("  %-48s main %7.1f  new %7.1f  delta %+7.1f  new max %7.1f" % (name, 1000 * statistics.median(to), 1000 * statistics.median(tn), 1000 * (statistics.median(tn) - statistics.median(to)), 1000 * max(tn)))
# ---- q4: the branch script as a hook process, each failure case
print("\nq4: the script as a process on a lab with a plain prompt; rc, stderr empty, stored, wall (s)")
def hook(event, tp_setup=None):
    lab = tempfile.mkdtemp(dir=scratch); os.makedirs(os.path.join(lab, "__statera__"))
    env = dict(os.environ); env.pop("CLAUDE_PROJECT_DIR", None)
    ev = dict(event, prompt="plain words here", cwd=lab, hook_event_name="UserPromptSubmit")
    t = time.perf_counter()
    p = subprocess.run([sys.executable, sys.argv[1]], input=json.dumps(ev), capture_output=True, text=True, env=env, cwd=lab, timeout=60)
    wall = time.perf_counter() - t
    f = os.path.join(lab, "__statera__", "user_words.md")
    stored = os.path.exists(f) and "plain words here" in open(f).read()
    shutil.rmtree(lab); return p.returncode, p.stderr == "" and p.stdout == "", stored, wall
peer = {"origin": {"kind": "peer"}, "promptSource": "system", "turnOrigin": "peer"}
unread = os.path.join(scratch, "unreadable.jsonl"); mk_transcript(unread, 1000, "pid-u", peer); os.chmod(unread, 0)
malformed = os.path.join(scratch, "malformed.jsonl"); open(malformed, "w").write('{"type":"user","promptId":"pid-m","origin":{"kind":"pe\n{"type":"user","promptId":"pid-m"\n')
big_miss = os.path.join(scratch, "big_miss.jsonl"); mk_transcript(big_miss, BIG, "pid-bm", peer, record_last=False)
big_peer = os.path.join(scratch, "big_peer.jsonl"); mk_transcript(big_peer, BIG, "pid-bp", peer)
oneline = os.path.join(scratch, "oneline.jsonl")
with open(oneline, "w") as fh: fh.write('{"type":"user","promptId":"pid-ol","pad":"' + "z" * BIG + '"}')
cases = [("unreadable transcript (mode 000)", {"transcript_path": unread, "prompt_id": "pid-u"}, True), ("transcript path is a directory", {"transcript_path": scratch, "prompt_id": "pid-u"}, True),
         ("transcript missing", {"transcript_path": os.path.join(scratch, "nope.jsonl"), "prompt_id": "pid-u"}, True),
         ("missing prompt_id (peer record present)", {"transcript_path": big_peer}, True), ("malformed records", {"transcript_path": malformed, "prompt_id": "pid-m"}, True),
         ("%d MB transcript, record absent" % (BIG // 1000000), {"transcript_path": big_miss, "prompt_id": "pid-bm"}, True),
         ("%d MB transcript, single line, id at its start" % (BIG // 1000000), {"transcript_path": oneline, "prompt_id": "pid-ol"}, True),
         ("%d MB transcript, peer record last (control: must drop)" % (BIG // 1000000), {"transcript_path": big_peer, "prompt_id": "pid-bp"}, False)]
fails = 0
for name, ev, want in cases:
    rc, clean, stored, wall = hook(ev)
    ok = rc == 0 and clean and stored == want and wall < 2.0
    fails += not ok
    print("  %-62s rc=%d clean=%s stored=%s (want %s) wall=%.2f %s" % (name, rc, clean, stored, want, wall, "ok" if ok else "FAIL"))
os.chmod(unread, 0o600)
print("q4 failures:", fails)
