# Alternating pairs of headless haiku sessions, arm A (budget/handback rows: python3 -S -I run_hook.py, exec form) against arm B (the same rows: exec of the Rust binary from the data folder), default permission mode with an allow list, the same six Bash calls in a lab folder; records per session the platform's own durations of the hooks (the --debug-file lines "Hooks: <Event>:<tool> [...] (plugin w08c1-x@inline) finished with status N (T ms)").
# inputs: scratch folder S (exp_A, exp_B from w08c1_make_exports.py; work/ is created as a lab), number of pairs; outputs: S/runs/rows.jsonl (one row per session: durations by hook event), S/dbg/pairNN_<arm>.log.
# usage: python3 -I w08c1_session_pairs.py S NPAIRS [--start K]   (pair i has order A,B when i is even, B,A when odd)
import json, os, re, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); NP = int(sys.argv[2]); START = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0
WORK = S + "/work"
os.makedirs(WORK + "/__statera__", exist_ok=True)
open(WORK + "/a.txt", "w").write("alpha\nbeta\ngamma\n"); open(WORK + "/b.txt", "w").write("one\ntwo\nthree\n")
CMDS = ["ls", "cat a.txt", "head -n 2 b.txt", "pwd", "wc -l a.txt", "echo hi"]
PROMPT = "Call the Bash tool once per command, one call per turn, in this order, each command exactly as written, then stop. Write no other text. Commands: " + "; ".join("`%s`" % c for c in CMDS)
ALLOW = ",".join("Bash(%s *)" % c for c in ["ls", "cat", "head", "wc", "echo"]) + ",Bash(pwd),Bash(ls)"
LINE = re.compile(r"Hooks: (\w+(?::\w+)?) \[(.*?)\] \(plugin (w08c1-[a-z]+)@inline\) finished with status (\d+) \((\d+)ms\)")
os.makedirs(S + "/runs", exist_ok=True); os.makedirs(S + "/dbg", exist_ok=True)
fails = 0
for i in range(START, NP):
    for arm in (("A", "B") if i % 2 == 0 else ("B", "A")):
        tag = "pair%02d_%s" % (i, arm)
        dbg = "%s/dbg/%s.log" % (S, tag)
        cmd = ["claude", "-p", PROMPT, "--model", "haiku", "--permission-mode", "default", "--allowedTools", ALLOW, "--output-format", "json", "--debug-file", dbg, "--plugin-dir", "%s/exp_%s" % (S, arm)]
        env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash")
        la0 = os.getloadavg(); t0 = time.time()
        r = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, timeout=300, env=env)
        t1 = time.time()
        by = {}
        for l in open(dbg, errors="replace"):
            m = LINE.search(l)
            if m and m.group(3) == "w08c1-" + arm.lower():
                by.setdefault(m.group(1), []).append((int(m.group(5)), int(m.group(4))))
        try: j = json.loads(r.stdout)
        except ValueError: j = {}
        row = dict(pair=i, arm=arm, rc=r.returncode, wall_s=round(t1 - t0, 2), load1_before=la0[0], cost_usd=j.get("total_cost_usd"), is_error=j.get("is_error"), ms={k: [d for d, _ in v] for k, v in by.items()}, status={k: [s for _, s in v] for k, v in by.items()})
        open(S + "/runs/rows.jsonl", "a").write(json.dumps(row) + "\n")
        print(tag, "rc", r.returncode, "%.1fs" % (t1 - t0), {k: (len(v), sorted(d for d, _ in v)[len(v) // 2]) for k, v in by.items()}, "cost", j.get("total_cost_usd"), flush=True)
        fails = fails + 1 if (r.returncode != 0 or not by) else 0
        if fails >= 3: sys.exit("three failed sessions in a row, stopping")
