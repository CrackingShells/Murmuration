# Runs one haiku session that dispatches one haiku subagent to read eight reports of the scratch lab and then answer from its brief and the first report, with the lab's PreCompact hook and a payload logger in the plugin export, optionally at a small auto-compact window, and scores the subagent's answer: from S, NAME, WINDOW to S/cells/NAME/{stream.jsonl,debug.log,hooks.log,meta.json} and a one-line score on stdout.
"""usage: w08_c3_subagent_cell.py S NAME EXPORT [WINDOW]   (WINDOW omitted: no compaction. Protocol P3 v0, m7: does the PreCompact payload identify a subagent, does the hook run there, does a compacted subagent keep its brief and a detail.)
Brief planted in the subagent's prompt: name worker-w03-x, claim w03-c9, verifier reproducer-w03-9. Reads fill from a lab built by w08_c3_make_lab.py (seed 1). Default permission mode, Read only. About USD 0.2 on haiku."""
import json, os, re, shutil, subprocess, sys, time
S, NAME, EXPORT = os.path.abspath(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3]); WINDOW = sys.argv[4] if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(S, "cells", NAME); LAB = os.path.join(RUN, "lab"); PL = os.path.join(RUN, "plugin"); shutil.rmtree(RUN, ignore_errors=True); os.makedirs(RUN)
subprocess.run([sys.executable, os.path.join(HERE, "w08_c3_make_lab.py"), LAB, "1"], check=True, capture_output=True)
truth = json.load(open(os.path.join(LAB, "truth.json")))
shutil.copytree(EXPORT, PL, ignore=shutil.ignore_patterns("__reports__", "__roadmap__", "rust", "probes", "validation", ".git", "__pondus__", "__statera__", "__scrupuli__", "__instrumenta__"))
hp = os.path.join(PL, "hooks", "hooks.json"); h = json.load(open(hp))["hooks"]; h.pop("UserPromptSubmit", None)
LOG = os.path.join(RUN, "hooks.log"); logger = os.path.join(RUN, "log_hook.py")
open(logger, "w").write("import sys,json,time\nd=json.loads(sys.stdin.read())\nopen(%r,'a').write(json.dumps({'t':time.time(),'event':d.get('hook_event_name'),'keys':sorted(d),'agent_id':d.get('agent_id'),'agent_type':d.get('agent_type'),'transcript':str(d.get('transcript_path'))[-60:]})+'\\n')\n" % LOG)
h["PreCompact"] = h["PreCompact"] + [{"hooks": [{"type": "command", "command": "python3", "args": [logger], "timeout": 10}]}]
h["SessionStart"] = h["SessionStart"] + [{"hooks": [{"type": "command", "command": "python3", "args": [logger], "timeout": 10}]}]
json.dump({"hooks": h}, open(hp, "w"), indent=1)
env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash")
for k in list(env):
    if k.startswith("CLAUDE_AUTOCOMPACT") or k.startswith("CLAUDE_CODE_AUTO_COMPACT") or k == "CLAUDE_PROJECT_DIR": env.pop(k)
if WINDOW: env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = WINDOW
files = [os.path.join(LAB, r) for r in truth["reports"][:8]]
brief = ("Your name is worker-w03-x. You work on claim w03-c9; your verifier will be reproducer-w03-9. Read these eight files one at a time, one Read call per turn, in this order, and after each write one short sentence saying what it adds, then go on to the next file: %s. "
         "After the eighth, without reading anything again, answer in two lines: (a) your name, your claim id and your verifier's name from this brief; (b) the 'Largest gap in this report' line of the FIRST file, as g and k." % " then ".join(files))
prompt = "Dispatch exactly one subagent with the Agent tool (subagent_type general-purpose, model haiku) using this brief verbatim, wait for it, then reply with its final answer only.\n\nBRIEF:\n" + brief
t0 = time.time()
p = subprocess.run(["claude", "-p", prompt, "--model", "haiku", "--plugin-dir", PL, "--permission-mode", "default", "--allowedTools", "Read", "Agent",
                    "--output-format", "stream-json", "--verbose", "--debug-file", os.path.join(RUN, "debug.log")], cwd=LAB, env=env, capture_output=True, text=True, timeout=600)
open(os.path.join(RUN, "stream.jsonl"), "w").write(p.stdout)
final = ""
for l in p.stdout.splitlines():
    try: d = json.loads(l)
    except ValueError: continue
    if d.get("type") == "result": final = d.get("result") or ""
dbg = open(os.path.join(RUN, "debug.log"), errors="replace").read()
ev = [json.loads(l) for l in open(LOG)] if os.path.exists(LOG) else []
pre = [e for e in ev if e["event"] == "PreCompact"]
ok = dict(name="worker-w03-x" in final, claim="w03-c9" in final, verifier="reproducer-w03-9" in final, g=truth["q5"]["g"] in final and bool(re.search(r"k\s*=\s*%d\b" % truth["q5"]["k"], final)))
meta = dict(name=NAME, window=WINDOW, wall_s=round(time.time() - t0, 1), precompact_events=len(pre), payload_keys=sorted({k for e in pre for k in e["keys"]}), payload_has_agent_id=any(e["agent_id"] for e in pre),
            transcript_tails=[e["transcript"] for e in pre][:3], forked_compactions=len(re.findall(r"Forked agent \[[\w-]+compact\] finished", dbg)), hook_settled_ms=re.findall(r"classic\.PreCompact settled in ([\d.]+)ms", dbg), score=ok)
json.dump(meta, open(os.path.join(RUN, "meta.json"), "w"), indent=1)
print(NAME, json.dumps(meta))
