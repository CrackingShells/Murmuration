# Runs one PI-like headless session (research-pi agent of an exported plugin, one process, stream-json turns) through a compaction on a scratch lab of wave 03, from ARM, MODEL and SEED to S/runs/NAME/{stream.jsonl,debug.log,stderr.txt,meta.json,truth.json,lab/}.
"""usage: w08_c3_run.py S NAME --arm C|B0|B1|H --model haiku|opus --seed N --export DIR [--window 150000] [--turns N] [--max-reports 12]
S = scratch folder outside the repo; DIR = a `git archive` export of the branch (plugin root). Arms (protocol P3 v0): C no compaction (default window; reads N=--turns reports); B0 window set, neither the brief row nor the PreCompact row;
B1 window set, brief row only; H window set, brief row and PreCompact row (the full hooks.json minus the user_words row, so the scratch user_words.md stays as built). Compacted arms read reports until a compact_boundary
event has been seen, then 2 more, then ask the five questions; if none is seen after --max-reports reports they ask anyway (meta.json says so). One process, `--input-format stream-json`, default permission mode, no budget flag.
Env: CLAUDE_CODE_SHELL=/bin/bash; CLAUDE_CODE_AUTO_COMPACT_WINDOW=<window> for the compacted arms. Cost per run: haiku about USD 0.3-0.6, opus about USD 2-4."""
import json, os, shutil, subprocess, sys, threading, time, queue

args = sys.argv[1:]
S, NAME = os.path.abspath(args[0]), args[1]
opt = dict(zip(args[2::2], args[3::2]))
ARM, MODEL, SEED, EXPORT = opt["--arm"], opt["--model"], int(opt["--seed"]), os.path.abspath(opt["--export"])
WINDOW, NTURNS, MAXR = int(opt.get("--window", 150000)), int(opt.get("--turns", 0)), int(opt.get("--max-reports", 12))
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(S, "runs", NAME); LAB = os.path.join(RUN, "lab"); PL = os.path.join(RUN, "plugin")
shutil.rmtree(RUN, ignore_errors=True); os.makedirs(RUN)
subprocess.run([sys.executable, os.path.join(HERE, "w08_c3_make_lab.py"), LAB, str(SEED)], check=True, capture_output=True)
shutil.move(os.path.join(LAB, "truth.json"), os.path.join(RUN, "truth.json"))
truth = json.load(open(os.path.join(RUN, "truth.json")))
shutil.copytree(EXPORT, PL, ignore=shutil.ignore_patterns("__reports__", "__roadmap__", "rust", "probes", "validation", ".git", "__pondus__", "__statera__", "__scrupuli__", "__instrumenta__"))
hp = os.path.join(PL, "hooks", "hooks.json"); h = json.load(open(hp))["hooks"]
h.pop("UserPromptSubmit", None)
if ARM in ("B0", "B1"): h.pop("PreCompact", None)
if ARM == "B0": h["SessionStart"] = [r for r in h["SessionStart"] if r.get("matcher") != "resume|compact"]
json.dump({"hooks": h}, open(hp, "w"), indent=1)

env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
for k in list(env):
    if k.startswith("CLAUDE_AUTOCOMPACT") or k.startswith("CLAUDE_CODE_AUTO_COMPACT") or k in ("DISABLE_AUTO_COMPACT", "DISABLE_COMPACT", "CLAUDE_PROJECT_DIR"): env.pop(k)
if ARM != "C": env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = str(WINDOW)
cmd = ["claude", "-p", "--agent", "murmuration:research-pi", "--model", MODEL, "--plugin-dir", PL, "--permission-mode", "default",
       "--allowedTools", "Read", "Glob", "Grep", "Bash(cat:*)", "Bash(head:*)", "Bash(sed:*)", "Bash(jq:*)", "Bash(ls:*)", "Bash(wc:*)", "Bash(grep:*)", "Bash(tail:*)",
       "--disallowedTools", "Agent", "Task", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch",
       "--input-format", "stream-json", "--output-format", "stream-json", "--verbose", "--debug-file", os.path.join(RUN, "debug.log")]
T1 = ("Start of session. You are the PI of the lab in this folder. My instruction for this session: %s Orient yourself as you would at the start of a session: read the current wave note, "
      "the user's words, the harness log and the claim files. Do not dispatch workers and do not write files. Then say in three lines where the wave stands.")
TK = "Read %s in full and tell me in one sentence what it adds."
FINAL = ("I am back. Before we go on, answer from where you are, as briefly as you can: (1) which workers are in flight right now, by name, and on which claim; "
         "(2) the instruction I gave you at the start of this session, quoted exactly; (3) what the wave note says to do next; (4) the current label of %s and of %s, as the lab's rules give it (not the author's label); "
         "(5) in the first report you read after orientation, the largest gap and its k. If you need a tool to be sure of any answer, use it.")
q4 = list(truth["labels"])
T1 = T1 % truth["sentence"]
msg = lambda t: json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": t}]}}) + "\n"

p = subprocess.Popen(cmd, cwd=LAB, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(os.path.join(RUN, "stderr.txt"), "w"), text=True, bufsize=1)
events = queue.Queue(); out = open(os.path.join(RUN, "stream.jsonl"), "w")
def reader():
    for line in p.stdout:
        out.write(line); out.flush(); events.put(line)
    events.put(None)
threading.Thread(target=reader, daemon=True).start()
t0 = time.time(); nreports = 0; sent_final = False; boundaries = 0; after_boundary = None; turn_log = []
def send(text):
    p.stdin.write(msg(text)); p.stdin.flush(); turn_log.append((round(time.time() - t0, 1), text[:60]))
send(T1)
done = False
while not done:
    line = events.get()
    if line is None: break
    try: d = json.loads(line)
    except ValueError: continue
    if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
        boundaries += 1
        if after_boundary is None: after_boundary = nreports
    if d.get("type") == "result":
        if sent_final: break
        if ARM == "C": ask = nreports >= NTURNS
        else: ask = (after_boundary is not None and nreports >= after_boundary + 2) or nreports >= MAXR
        if ask:
            sent_final = True; send(FINAL % tuple(q4))
        else:
            send(TK % truth["reports"][nreports]); nreports += 1
try: p.stdin.close()
except Exception: pass
try: p.wait(timeout=60)
except subprocess.TimeoutExpired: p.terminate()
json.dump(dict(name=NAME, arm=ARM, model=MODEL, seed=SEED, window=WINDOW if ARM != "C" else None, reports_read=nreports, boundaries=boundaries, after_boundary_at_report=after_boundary,
               asked_without_boundary=(ARM != "C" and after_boundary is None), final_sent=sent_final, wall_s=round(time.time() - t0, 1), rc=p.returncode, export=EXPORT, turns=turn_log),
          open(os.path.join(RUN, "meta.json"), "w"), indent=1)
print(NAME, "arm", ARM, "reports", nreports, "boundaries", boundaries, "final", sent_final, "wall", round(time.time() - t0, 1))
