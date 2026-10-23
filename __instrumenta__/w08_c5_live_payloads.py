# Runs one haiku headless session that dispatches N subagents of one type in one message, with a payload logger on PreToolUse(Agent), SubagentStart, SubagentStop and PostToolUse(Agent), from a git revision of the repo to RAW (a scratch folder, never committed): RAW/events.jsonl (raw payloads, one per line, with arrival time and pid), RAW/stream.jsonl, RAW/dispatch.json (names given, in order).
# usage: python3 -I w08_c5_live_payloads.py REPO REV S NAME N [--type TYPE] [--bg] [--as-murmuration [--bin PATH]]
# --as-murmuration: the plugin keeps the name `murmuration` (so the budget hooks see `murmuration:author`) and its budget and handback rows run the Python scripts (run_hook.py), or the binary at PATH (exec form), without the installer row; the lab's __statera__/harness.jsonl is then the hooks' own log.   ; cost about USD 0.1 to 0.3 on haiku for N=4; the raw files hold account identifiers (session ids, paths): keep them under S.
import json, os, shutil, subprocess, sys, tarfile, io

repo, rev, S, NAME, N = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4], int(sys.argv[5])
kind = sys.argv[sys.argv.index("--type") + 1] if "--type" in sys.argv else ("murmuration:author" if "--as-murmuration" in sys.argv else "w08c5-%s:author" % NAME)   # the plugin name is changed, so the agent type is <name>:author
BG = "--bg" in sys.argv   # dispatch with run_in_background: true
RUN = os.path.join(S, "live", NAME); PL = os.path.join(RUN, "plugin"); LAB = os.path.join(RUN, "lab")
shutil.rmtree(RUN, ignore_errors=True); os.makedirs(PL); os.makedirs(LAB)
tar = subprocess.run(["git", "-C", repo, "archive", rev, "hooks", "scripts", "bin", "agents", ".claude-plugin"], capture_output=True, check=True).stdout
tarfile.open(fileobj=io.BytesIO(tar)).extractall(PL, filter="fully_trusted")
AS = "--as-murmuration" in sys.argv; BIN = sys.argv[sys.argv.index("--bin") + 1] if "--bin" in sys.argv else None
pj = json.load(open(PL + "/.claude-plugin/plugin.json")); pj["name"] = "murmuration" if AS else "w08c5-" + NAME; pj.pop("skills", None)
json.dump(pj, open(PL + "/.claude-plugin/plugin.json", "w"), indent=2)
hp = PL + "/hooks/hooks.json"; h = json.load(open(hp))["hooks"]
h.pop("UserPromptSubmit", None)
if AS:   # rows of the hooks under test: the Python scripts, or one binary by absolute path; no installer
    for ev_, groups in list(h.items()):
        for g in groups:
            for x in g["hooks"]:
                a = x.get("args", [])
                if x.get("command", "").endswith("/bin/murmuration") and a and a[0] in ("budget", "handback"):
                    x.update(command=BIN, args=a) if BIN else x.update(command="python3", args=["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py", a[0]])
        h[ev_] = [g for g in groups if not any("install_binary" in " ".join(x.get("args", [])) for x in g["hooks"])]
EV = os.path.join(RUN, "events.jsonl"); logger = os.path.join(RUN, "log_payload.py")
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "w08_c5_payload_logger.py"), logger)
lg = {"type": "command", "command": "python3", "args": [logger, EV], "timeout": 10}
h["SubagentStart"] = [{"hooks": [lg]}] + h["SubagentStart"]
h["SubagentStop"] = [{"hooks": [lg]}] + h["SubagentStop"]
h["PreToolUse"] = [{"matcher": "Agent|Task", "hooks": [lg]}] + h["PreToolUse"]
h["PostToolUse"] = [{"matcher": "Agent|Task", "hooks": [lg]}] + h["PostToolUse"]
json.dump({"hooks": h}, open(hp, "w"), indent=1)
os.makedirs(LAB + "/__statera__"); os.makedirs(LAB + "/__pondus__"); os.makedirs(LAB + "/__instrumenta__")
subprocess.run(["git", "init", "-q", LAB], check=True)
names = ["probe-w08-%s%d" % (NAME[:1], i + 1) for i in range(N)]
json.dump(names, open(os.path.join(RUN, "dispatch.json"), "w"))
calls = "\n".join('%d. Agent call: name "%s", subagent_type "%s", model "haiku", prompt "Your name is %s. Budget: USD 0.30. Time: min 5. Reply with the single word ok."%s' % (i + 1, n, kind, n, ', run_in_background true' if BG else '') for i, n in enumerate(names))
prompt = ("Make exactly %d Agent tool calls, all in ONE message so that they run in parallel, in this order, with the arguments given:\n%s\nWhen all have returned, reply with the single word done." % (N, calls))
env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"); env.pop("CLAUDE_PROJECT_DIR", None)
p = subprocess.run(["claude", "-p", prompt, "--model", "haiku", "--plugin-dir", PL, "--permission-mode", "default", "--allowedTools", "Agent",
                    "--output-format", "stream-json", "--verbose"], cwd=LAB, env=env, capture_output=True, text=True, timeout=600)
open(os.path.join(RUN, "stream.jsonl"), "w").write(p.stdout)
open(os.path.join(RUN, "stderr.txt"), "w").write(p.stderr)
print(NAME, "rc", p.returncode, "events", sum(1 for _ in open(EV)) if os.path.exists(EV) else 0)
