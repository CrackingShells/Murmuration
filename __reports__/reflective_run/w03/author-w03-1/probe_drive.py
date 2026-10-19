#!/usr/bin/env python3
"""One PostToolBatch probe cell: a scratch folder, a haiku parent that dispatches one murmuration worker (sonnet by its agent file),
a logging-only hook plugin (PROBE_MODE log|ctx|block|ctxuse) that writes every event to <cell>/events.jsonl.

usage: probe_drive.py <scratch> <cell> --mode log|ctx|block|ctxuse [--bg] [--type author|explorer]
Everything is written under <scratch>/runs/<cell>/ (outside the worktree). Stdlib only. One `claude -p` call per cell, --max-budget-usd 0.6."""
import argparse, json, os, shutil, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("scratch"); ap.add_argument("cell")
ap.add_argument("--mode", default="log"); ap.add_argument("--bg", action="store_true"); ap.add_argument("--type", default="author")
ap.add_argument("--deny", action="store_true"); ap.add_argument("--long", action="store_true"); ap.add_argument("--plugin", default="plugin_probe"); ap.add_argument("--cap", default="0.6")
a = ap.parse_args()
S = os.path.abspath(a.scratch)
plugin = os.path.join(S, a.plugin)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
for n in ["d1", "d2", "s1", "s2", "s3", "p1", "p2", "p3", "q1", "q2", "q3", "t1", "u1", "u2"]:
    open(os.path.join(lab, n + ".txt"), "w").write("file %s: ok\n" % n)
name = "%s-w03-%s" % (a.type, a.cell.replace("_", "").replace("-", ""))
brief = (("Your name is %s.\n"
         "This is a harness test; do not write any file. Follow these steps exactly, in this order. A 'round' is one assistant message.\n"
         "Round 1: one Bash call: cat s1.txt.\n"
         "Round 2: one Bash call: cat missing_file.txt (it will fail; that is expected).\n"
         "Round 3: three tool calls in ONE message so that they run in parallel: Bash `cat p1.txt`, Read of p2.txt (absolute path in the current directory), Bash `cat p3.txt`.\n"
         "Round 4: three Bash calls in ONE message: `cat q1.txt`, `cat q2.txt`, `cat q3.txt`.\n"
         "Round 5: one Bash call: cat s2.txt.\n"
         "Round 6: two Bash calls in ONE message: `cat t1.txt`, `cat u1.txt`.\n"
         "Round 7: one Bash call: cat s3.txt.\n"
         + ("Round 8: two Bash calls in ONE message: `sleep 6; cat t1.txt` and `cat u1.txt`.\nRound 9: one Bash call with run_in_background true: `sleep 3; cat u2.txt`.\nRound 10: one Bash call: `sleep 5; cat s1.txt`.\n" if a.long else "")
         + ("Round 8: two Bash calls in ONE message: `cat d1.txt`, `cat d2.txt` (the harness may refuse one of them; that is expected).\n" if a.deny else "") +
         "Then hand back. In the hand-back, list verbatim every text beginning with PROBE- that you saw anywhere other than in a file's content "
         "(in a tool result, a system message or a hook message), say in which round you saw it, and give the exact wording of anything the harness told you.") % name)
where = ("in the background (run_in_background: true), and then wait for its completion notification: do not end your turn before it arrives "
         "(while waiting, run `sleep 10` with Bash, one call at a time, at most 15 times)") if a.bg else "in the foreground"
prompt = ("Call the Agent tool exactly once with subagent_type 'murmuration:%s', name '%s', %s, with exactly the text between "
          "the lines ==== as its prompt (keep every line, change nothing).\n====\n%s\n====\nWhen the Agent call is finished, say DONE." % (a.type, name, where, brief))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", plugin, "--setting-sources", "project", "--strict-mcp-config",
       "--permission-mode", "auto", "--max-budget-usd", a.cap, "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env.update(PROBE_LOG=os.path.join(base, "events.jsonl"), PROBE_MODE=a.mode, PROBE_FULL="1")
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=900)
wall = time.time() - t0
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for line in p.stdout.splitlines():
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if r.get("type") == "result":
        res = r
json.dump(dict(cell=a.cell, name=name, mode=a.mode, bg=a.bg, type=a.type, wall_s=round(wall, 1), rc=p.returncode, usd=res and res.get("total_cost_usd"),
               turns=res and res.get("num_turns"), session=res and res.get("session_id")), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
