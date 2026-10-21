#!/usr/bin/env python3
"""Runs one headless cell of wave-5 E6: the plugin's research-pi as main agent does a fixed smoke task (Skill, Write, Read, Edit, Bash, ToolSearch, Agent->explorer); input: <scratch> <cell> <plugin dir>; output: <scratch>/runs/<cell>/{lab/,stdout.jsonl,stderr.txt,meta.json}, meta.json holding wall time, rc and total_cost_usd.
usage: w05c3_pi_tools_cell.py <scratch> <cell> <plugin dir> [--model M] [--mcp mcp-config.json]   (no --model: the agent file's own model, opus). Stdlib only; the model has no seed.
Launch conditions as in __reports__/wave-05/00-experiment_protocol_v0.md 'Common to all runs': outside the repo, CLAUDE_PROJECT_DIR unset, COLGREP_DATA_DIR in the run folder, no --max-budget-usd."""
import argparse, json, os, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell"); ap.add_argument("plugin"); ap.add_argument("--model", default=""); ap.add_argument("--mcp", default="")   # --mcp FILE: an --mcp-config file (E6b: the dummy MCP server in both arms)
a = ap.parse_args()
S = os.path.abspath(a.scratch); plugin = os.path.abspath(a.plugin)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"; env["COLGREP_DATA_DIR"] = os.path.join(base, "colgrep"); os.makedirs(env["COLGREP_DATA_DIR"])
subprocess.run([sys.executable, "-I", os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab], input="What is a smoke test?", text=True, capture_output=True, check=True, env=env)
prompt = ("This is a smoke test of your tools. Do these seven steps in order, one tool call each, then say DONE and nothing more.\n"
          "1. Load the research-loop skill with the Skill tool.\n"
          "2. Write the file smoke/note.md with the single line: alpha\n"
          "3. Read smoke/note.md.\n"
          "4. Edit smoke/note.md, replacing alpha with beta.\n"
          "5. Run `wc -c smoke/note.md` with Bash.\n"
          "6. Use ToolSearch with the query `notebook` to find the deferred tool that edits notebooks.\n"
          "7. Dispatch one explorer with the Agent tool (subagent_type murmuration:explorer, foreground; the Agent tool has no name field, so the name goes in the prompt): its prompt is exactly: `Your name is explorer-smoke. Budget: USD 0.20. Time: min 3. Read smoke/note.md and reply with its one line. Write no file.`\n")
cmd = ["claude", "-p", "--agent", "murmuration:research-pi", "--plugin-dir", plugin, "--setting-sources", "project,local", "--strict-mcp-config", "--permission-mode", "auto",
       "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
if a.mcp:
    cmd[cmd.index("--strict-mcp-config") + 1:cmd.index("--strict-mcp-config") + 1] = ["--mcp-config", os.path.abspath(a.mcp)]
if a.model:
    cmd[2:2] = ["--model", a.model]
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=900)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for l in p.stdout.splitlines():
    try:
        r = json.loads(l)
    except ValueError:
        continue
    if r.get("type") == "result":
        res = r
json.dump(dict(cell=a.cell, plugin=os.path.basename(plugin), model=a.model or "agent-file", wall_s=round(time.time() - t0, 1), rc=p.returncode,
               total_cost_usd=(res or {}).get("total_cost_usd"), is_error=(res or {}).get("is_error"), result=((res or {}).get("result") or "")[:200]),
          open(os.path.join(base, "meta.json"), "w"), indent=1)
print(a.cell, "rc", p.returncode, "wall", round(time.time() - t0, 1), "cost", (res or {}).get("total_cost_usd"))
