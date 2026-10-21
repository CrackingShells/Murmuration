# Runs alternating pairs of headless haiku sessions, arm A (guard rows: python3 -S -I permission_guard.py, exec form) against arm B (guard rows: exec of the Rust binary from the data folder), default permission mode with an allow list, the same eight Bash calls; and records per session the platform's own durations of the guard rows (the --debug-file line "Hooks: PreToolUse:Bash [...] (plugin w07c6-x@inline) finished with status N (T ms)").
# inputs: scratch folder S (with exp_A, exp_B from w07c6_make_exports.py and work/ with a.txt b.txt), number of pairs, seed for the order of arms; outputs: S/runs/pairNN_<arm>.json (claude's JSON), S/dbg/pairNN_<arm>.log, S/runs/g4_rows.jsonl (one row per session), S/runs/loadavg.tsv.
# usage: python3 -I __instrumenta__/w07c6_session_pairs.py S NPAIRS [--start K]   (pair i has order A,B when i is even, B,A when odd: alternating; the first arm of pair 0 is fixed by that rule, not drawn)
import json, os, re, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); NP = int(sys.argv[2]); START = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0
WORK = S + "/work"
CMDS = ["ls", "cat a.txt", "head -n 2 b.txt", "pwd", "wc -l a.txt", "date", "echo hi", "ls -la"]
PROMPT = "Call the Bash tool once per command, one call per turn, in this order, each command exactly as written, then stop. Write no other text. Commands: " + "; ".join("`%s`" % c for c in CMDS)
ALLOW = ",".join("Bash(%s *)" % c for c in ["ls", "cat", "head", "wc", "echo"]) + ",Bash(pwd),Bash(date),Bash(ls)"
LINE = re.compile(r"Hooks: PreToolUse:Bash \[(.*?)\] \(plugin (w07c6-[a-z]+)@inline\) finished with status (\d+) \((\d+)ms\)")
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
        t1 = time.time(); la1 = os.getloadavg()
        open("%s/runs/%s.json" % (S, tag), "w").write(r.stdout)
        durs = []
        for l in open(dbg, errors="replace"):
            m = LINE.search(l)
            if m and m.group(2) == "w07c6-" + arm.lower():
                durs.append((int(m.group(4)), int(m.group(3))))
        try: j = json.loads(r.stdout)
        except ValueError: j = {}
        row = dict(pair=i, arm=arm, rc=r.returncode, wall_s=round(t1 - t0, 2), load1_before=la0[0], load1_after=la1[0], guard_ms=[d for d, _ in durs], guard_status=[s for _, s in durs],
                   cost_usd=j.get("total_cost_usd"), turns=j.get("num_turns"), is_error=j.get("is_error"))
        open(S + "/runs/g4_rows.jsonl", "a").write(json.dumps(row) + "\n")
        print(tag, "rc", r.returncode, "%.1fs" % (t1 - t0), "guard calls", len(durs), "median ms", sorted(d for d, _ in durs)[len(durs) // 2] if durs else None, "load %.2f" % la0[0], flush=True)
        fails = fails + 1 if (r.returncode != 0 or len(durs) < 6) else 0
        if fails >= 3: sys.exit("three failed sessions in a row, stopping")
