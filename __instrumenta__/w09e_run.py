# Runs one PI-resume cell: `claude -p --resume <cut session> --fork-session` on the scratch lab with the research-pi agent, an arm's hooks (B1 brief only; H PreCompact digest; HP digest after compaction), one stream-json question turn; writes S/runs/NAME/{stream.jsonl,debug.log,stderr.txt,meta.json,plugin/} and prints the run's cost and compaction facts.
"""usage: w09e_run.py S NAME --arm B1|H|HP --session-id ID --lab LAB --export DIR --questions FILE [--model opus|haiku] [--window 230000] [--max-usd 5] [--perm auto|default]
S scratch folder (outside the repo); LAB the scratch lab (cwd of the run, the cut transcript was installed for it by w09e_cut_session.py); DIR a copy of the plugin (scripts/, agents/, skills/, hooks/).
Hooks written into the run's plugin copy (all other rows of hooks/hooks.json dropped: the Rust guard binary and the budget hooks are not needed for a compaction):
 B1  SessionStart matcher compact -> scripts/resume_brief.py (the lab's existing state)
 H   B1 + PreCompact -> scripts/w09e_digest.py (stdout reaches the summarizer)
 HP  B1 + a second SessionStart compact row -> scripts/w09e_digest.py --post (stdout reaches the context verbatim after the summary)
Env: CLAUDE_CODE_SHELL=/bin/bash, CLAUDE_CODE_AUTO_COMPACT_WINDOW=<window> (compaction when the context passes window - 33,000). Permission mode auto (the PI's own) or default, never bypass. One process, input stream-json, one user turn."""
import json, os, shutil, subprocess, sys, time

a = sys.argv[1:]
S, NAME = os.path.abspath(a[0]), a[1]
o = dict(zip(a[2::2], a[3::2]))
ARM, SID, LAB, EXPORT, QF = o["--arm"], o["--session-id"], os.path.abspath(o["--lab"]), os.path.abspath(o["--export"]), o["--questions"]
MODEL, WINDOW, MAXUSD, PERM = o.get("--model", "opus"), int(o.get("--window", 230000)), o.get("--max-usd", "5"), o.get("--perm", "auto")
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(S, "runs", NAME); PL = os.path.join(RUN, "plugin")
shutil.rmtree(RUN, ignore_errors=True); os.makedirs(RUN)
shutil.copytree(EXPORT, PL, ignore=shutil.ignore_patterns("__*", "rust", "probes", "validation", ".git", "bin"))
shutil.copy(os.path.join(HERE, "w09e_digest.py"), os.path.join(PL, "scripts", "w09e_digest.py"))
row = lambda *x: {"type": "command", "command": "python3", "args": ["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/" + x[0]] + list(x[1:]), "timeout": 20}
brief = {"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/resume_brief.py"], "timeout": 20}
hooks = {"SessionStart": [{"matcher": "compact", "hooks": [brief] + ([row("w09e_digest.py", "--post")] if ARM == "HP" else [])}]}
if ARM == "H": hooks["PreCompact"] = [{"hooks": [row("w09e_digest.py")]}]
json.dump({"hooks": hooks}, open(os.path.join(PL, "hooks", "hooks.json"), "w"), indent=1)
env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
for k in list(env):
    if k.startswith("CLAUDE_AUTOCOMPACT") or k.startswith("CLAUDE_CODE_AUTO_COMPACT") or k in ("DISABLE_AUTO_COMPACT", "DISABLE_COMPACT", "CLAUDE_PROJECT_DIR"): env.pop(k)
env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = str(WINDOW)
tools = ["Read", "Glob", "Grep", "mcp__plugin_colgrep-mcp_colgrep__search", "mcp__plugin_colgrep-mcp_colgrep__expand", "mcp__plugin_colgrep-mcp_colgrep__find_files"] + \
        ["Bash(%s:*)" % c for c in ("cat", "head", "sed", "jq", "ls", "wc", "grep", "tail", "awk", "cut", "nl", "python3 scripts/lab_status.py", "git log", "git show")]
cmd = ["claude", "-p", "--resume", SID, "--fork-session", "--agent", "murmuration:research-pi", "--model", MODEL, "--plugin-dir", PL, "--permission-mode", PERM,
       "--max-budget-usd", MAXUSD, "--allowedTools"] + tools + ["--disallowedTools", "Agent", "Task", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch",
       "--input-format", "stream-json", "--output-format", "stream-json", "--verbose", "--include-hook-events", "--debug-file", os.path.join(RUN, "debug.log")]
q = open(QF).read().strip()
t0 = time.time()
p = subprocess.run(cmd, cwd=LAB, env=env, input=json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": q}]}}) + "\n",
                   stdout=open(os.path.join(RUN, "stream.jsonl"), "w"), stderr=open(os.path.join(RUN, "stderr.txt"), "w"), text=True, timeout=1500)
res, bounds = None, 0
for l in open(os.path.join(RUN, "stream.jsonl")):
    try: d = json.loads(l)
    except ValueError: continue
    if d.get("type") == "system" and d.get("subtype") == "compact_boundary": bounds += 1
    if d.get("type") == "result": res = d
json.dump(dict(name=NAME, arm=ARM, model=MODEL, window=WINDOW, session_id=SID, rc=p.returncode, wall_s=round(time.time() - t0, 1), boundaries=bounds,
               cost_reported=res and res.get("total_cost_usd"), turns=res and res.get("num_turns")), open(os.path.join(RUN, "meta.json"), "w"), indent=1)
print(NAME, "arm", ARM, "rc", p.returncode, "boundaries", bounds, "cost", res and res.get("total_cost_usd"), "wall", round(time.time() - t0, 1))
