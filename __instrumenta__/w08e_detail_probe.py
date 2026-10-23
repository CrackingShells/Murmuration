# Resumes a finished w08e compaction run's session once more and asks for one ordinary-prose detail per file (the 5th word of line 100 of f0..f9, read before the compactions), then scores the answer against the file: from RUNDIR to a one-line count on stdout.
"""usage: w08e_detail_probe.py RUNDIR (a run with stream.jsonl, plugin/, lab/). No tools are used by the model (it is told not to). Costs about USD 0.03 on haiku."""
import json, os, re, subprocess, sys
D = os.path.abspath(sys.argv[1]); LAB = os.path.join(D, "lab"); PL = os.path.join(D, "plugin")
sid = next(d["session_id"] for d in (json.loads(l) for l in open(os.path.join(D, "stream.jsonl")) if l.strip()) if d.get("type") == "system" and d.get("subtype") == "init")
truth = {n: open(os.path.join(LAB, "fill", "f%d.txt" % n)).read().splitlines()[99].split()[5] for n in range(10)}   # line 100: '<nnn.nnn> w1 w2 ...' -> index 5 is the 5th word
q = ("Without using any tool and without reading any file: for each file f0..f9, give the 5th word of line 100 of that file (the first token on a line is its line label like 003.099; count words after the label) "
     "if you know it exactly from what you read, else UNKNOWN. Format fK=WORD, one per line, nothing else.")
env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
p = subprocess.run(["claude", "-p", q, "--resume", sid, "--model", "haiku", "--plugin-dir", PL, "--permission-mode", "default", "--allowedTools", "Read", "--output-format", "stream-json", "--verbose"], cwd=LAB, env=env, capture_output=True, text=True)
open(os.path.join(D, "stream_detail.jsonl"), "w").write(p.stdout)
txt = "\n".join(c.get("text", "") for d in (json.loads(l) for l in p.stdout.splitlines() if l.strip()) if d.get("type") == "assistant" for c in d["message"]["content"] if c.get("type") == "text")
got = {int(a): b.strip().strip(".,") for a, b in re.findall(r"\bf(\d+)\s*=\s*(\S+)", txt)}
ok = sum(1 for n in truth if got.get(n) == truth[n]); unk = sum(1 for n in truth if got.get(n, "UNKNOWN") == "UNKNOWN")
print("%s: files f0..f9, exact %d, UNKNOWN %d, wrong %d" % (os.path.basename(D), ok, unk, 10 - ok - unk))
