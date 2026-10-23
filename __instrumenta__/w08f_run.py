# Runs one headless Sonnet 5.5 session of w08-f (agent from the test plugin, or a plain prompt) in its own copy of the task folder; from a label and options to <S>/runs/<label>.jsonl (stream-json with partial messages), <S>/runs/<label>.err and one row in <S>/runs/times.tsv.
# usage: w08f_run.py S LABEL [--agent NAME] [--effort LEVEL] [--prompt TEXT] [--task] [--env K=V ...]   (S = /private/tmp/murmuration-w08/explorer-w08-f; --task copies S/<--src, default src>/task to S/work/LABEL; permission mode auto; CLAUDE_CODE_SHELL=/bin/bash; no budget flag)
import os, sys, subprocess, time, shutil, argparse
a = argparse.ArgumentParser()
a.add_argument("S"); a.add_argument("label"); a.add_argument("--agent"); a.add_argument("--effort"); a.add_argument("--prompt", default="Verify claim c1 in claim.md."); a.add_argument("--task", action="store_true"); a.add_argument("--src", default="src"); a.add_argument("--env", nargs="*", default=[]); a.add_argument("--model", default="sonnet")
o = a.parse_args()
w = os.path.join(o.S, "work", o.label)
shutil.rmtree(w, ignore_errors=True); os.makedirs(w)
if o.task:
    for f in os.listdir(os.path.join(o.S, o.src, "task")): shutil.copy(os.path.join(o.S, o.src, "task", f), w)
os.makedirs(os.path.join(o.S, "runs"), exist_ok=True)
cmd = ["claude", "-p", o.prompt, "--model", o.model, "--permission-mode", "auto", "--output-format", "stream-json", "--verbose", "--include-partial-messages", "--strict-mcp-config", "--plugin-dir", os.path.join(o.S, "plug"), "--debug-file", os.path.join(o.S, "runs", o.label + ".debug.log")]
if o.agent: cmd += ["--agent", o.agent]
if o.effort: cmd += ["--effort", o.effort]
env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
for kv in o.env: k, v = kv.split("=", 1); env[k] = v
t0 = time.time()
r = subprocess.run(cmd, cwd=w, capture_output=True, text=True, timeout=1200, env=env, stdin=subprocess.DEVNULL)
t1 = time.time()
open(os.path.join(o.S, "runs", o.label + ".jsonl"), "w").write(r.stdout)
open(os.path.join(o.S, "runs", o.label + ".err"), "w").write(r.stderr[-2000:])
open(os.path.join(o.S, "runs", "times.tsv"), "a").write("%s\t%.0f\t%.1f\t%d\n" % (o.label, t0, t1 - t0, r.returncode))
print(o.label, "rc", r.returncode, "%.1fs" % (t1 - t0), len(r.stdout), "bytes")
