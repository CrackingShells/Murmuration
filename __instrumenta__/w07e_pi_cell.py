#!/usr/bin/env python3
"""Runs one headless haiku session started as murmuration:research-pi from an export, with an optional agent-frontmatter edit and an optional --settings JSON, and writes request 0's usage, the init event's skills/slash_commands/tools and the tool calls to <scratch>/runs/<cell>/{stdout.jsonl,summary.json}; inputs: scratch dir, cell name, export dir, --deny EXTRA (appended to disallowedTools:), --noskillsfm (drop the skills: frontmatter), --settings FILE.
Stdlib only; the model has no seed. Launch as wave-5 cells: lab_init in a fresh lab, CLAUDE_PROJECT_DIR unset, --permission-mode auto, no --max-budget-usd."""
import argparse, json, os, re, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell"); ap.add_argument("export")
ap.add_argument("--deny", default=""); ap.add_argument("--noskillsfm", action="store_true"); ap.add_argument("--settings", default="")
ap.add_argument("--appendbody", default=""); ap.add_argument("--prompt", default="P1"); ap.add_argument("--agent", default="research-pi")
a = ap.parse_args()
S = os.path.abspath(a.scratch); ex = os.path.abspath(a.export)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
plug = os.path.join(base, "plugin"); shutil.copytree(ex, plug, symlinks=True)   # per-cell copy so the agent edit never leaks
f = os.path.join(plug, "agents", a.agent + ".md"); t = open(f).read()
if a.deny:
    t = re.sub(r"^(disallowedTools:.*)$", lambda m: m.group(1) + ", " + a.deny if m.group(1).strip() != "disallowedTools:" else "disallowedTools: " + a.deny, t, count=1, flags=re.M)
if a.noskillsfm:
    t = re.sub(r"^skills:\n  - research-loop\n", "", t, flags=re.M)
if a.appendbody: t = t.rstrip("\n") + "\n\n" + a.appendbody + "\n"
open(f, "w").write(t)
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env["CLAUDE_CODE_SHELL"] = "/bin/bash"; env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"; env["COLGREP_DATA_DIR"] = os.path.join(base, "colgrep"); os.makedirs(env["COLGREP_DATA_DIR"])
subprocess.run([sys.executable, "-I", os.path.join(plug, "scripts", "lab_init.py"), "--project", lab], input="What is a smoke test?", text=True, capture_output=True, check=True, env=env)
skillpath = os.path.join(plug, "skills", "research-loop", "SKILL.md")
prompts = {"P1": "Load the research-loop skill with the Skill tool if you have a Skill tool. If you have none, check whether the text of the research-loop skill is already in your context. If neither, Read " + skillpath + ". Then answer with one line: HOW=<SKILL_TOOL|PRELOADED|READ|NONE> TITLE=<the first heading of the skill>. Then say DONE.",
           "P3": "Follow your instructions to get the research-loop procedure. Then answer with one line: HOW=<SKILL_TOOL|PRELOADED|READ|NONE> PATH=<the exact path you read, or none> TITLE=<the first heading of the skill>. Then say DONE.",
           "P4": "/lab-status",
           "P0": "Say OK and nothing more."}
cmd = ["claude", "-p", "--agent", "murmuration:" + a.agent, "--plugin-dir", plug, "--model", "haiku", "--permission-mode", "auto", "--output-format", "stream-json", "--verbose", "--include-hook-events"]
if a.settings: cmd += ["--settings", os.path.abspath(a.settings)]
cmd.append(prompts[a.prompt])
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=600)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
init = None; first = None; calls = []; res = None; final = ""
for l in p.stdout.splitlines():
    try: r = json.loads(l)
    except ValueError: continue
    if r.get("type") == "system" and r.get("subtype") == "init": init = r
    if r.get("type") == "assistant":
        u = r["message"].get("usage", {})
        if first is None: first = u
        for c in r["message"].get("content", []):
            if c.get("type") == "tool_use": calls.append(c["name"] + ":" + json.dumps(c.get("input"))[:100])
            if c.get("type") == "text": final = c["text"]
    if r.get("type") == "result": res = r
u = first or {}
tot = sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
sm = dict(cell=a.cell, deny=a.deny, noskillsfm=a.noskillsfm, settings=a.settings, rc=p.returncode, wall_s=round(time.time() - t0, 1), req0_total=tot, req0_usage=u,
          init_skills=len((init or {}).get("skills", [])), init_slash=len((init or {}).get("slash_commands", [])), init_tools=len((init or {}).get("tools", [])),
          has_research_loop=any("research-loop" in s for s in (init or {}).get("skills", [])), has_lab_status=any("lab-status" in s for s in (init or {}).get("slash_commands", [])),
          mcp=[(m.get("name"), m.get("status")) for m in (init or {}).get("mcp_servers", [])], tool_names=(init or {}).get("tools", []), calls=calls, final=final[:300],
          cost_usd=(res or {}).get("total_cost_usd"), session_id=(init or {}).get("session_id"))
json.dump(sm, open(os.path.join(base, "summary.json"), "w"), indent=1)
json.dump({k: (init or {}).get(k) for k in ("skills", "slash_commands", "tools", "mcp_servers", "agents", "plugins")}, open(os.path.join(base, "init_lists.json"), "w"), indent=1)
print(a.cell, "rc", p.returncode, "req0", tot, "skills", sm["init_skills"], "slash", sm["init_slash"], "tools", sm["init_tools"], "cost", sm["cost_usd"], "|", final[:120].replace("\n", " "))
