#!/usr/bin/env python3
"""Runs one headless haiku session as murmuration:research-pi from an export (no agent edit) with a fixed prompt (p2, p4s, p4l, p5d, p5w) and writes request 0 tokens, the number of model requests, every Read (path, failed or not), the tool calls and the final answer to <scratch>/runs/<cell>/summary.json; inputs: scratch dir, cell name, export dir, prompt key, optional --nolab; output: summary.json and stdout.jsonl in the cell folder.
Stdlib only; the model has no seed. Launch like w07e_pi_cell.py: lab_init in a fresh lab (not for --nolab), CLAUDE_PROJECT_DIR unset, --permission-mode auto, no --max-budget-usd."""
import argparse, json, os, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell"); ap.add_argument("export"); ap.add_argument("prompt")
ap.add_argument("--nolab", action="store_true"); ap.add_argument("--mode", default="auto")
a = ap.parse_args()
S = os.path.abspath(a.scratch); ex = os.path.abspath(a.export)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
plug = os.path.join(base, "plugin"); shutil.copytree(ex, plug, symlinks=True, ignore_dangling_symlinks=True)
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env["CLAUDE_CODE_SHELL"] = "/bin/bash"; env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
env["COLGREP_DATA_DIR"] = os.path.join(base, "colgrep"); os.makedirs(env["COLGREP_DATA_DIR"])
if not a.nolab:
    subprocess.run([sys.executable, "-I", os.path.join(plug, "scripts", "lab_init.py"), "--project", lab], input="What is a smoke test?", text=True, capture_output=True, check=True, env=env)
prompts = {
 "p2": "Follow your instructions to get the research-loop procedure. Then, from the files of that skill and not from memory, answer in one line: EXPLORER_BUDGET=<the default budget line of an explorer brief> WAVE_HEADING=<the first heading of the wave-note template>. Then say DONE.",
 "p4s": "/lab-status",
 "p4l": "/lab What is a smoke test?",
 "p5d": "Use the dataviz skill. Do nothing else than get its instructions, then answer in one line: PATH=<the path of the file you read for it, or none> NAME=<the name field in its frontmatter>. Then say DONE.",
 "p5w": "Use the writing-history skill. Do nothing else than get its instructions, then answer in one line: PATH=<the path of the file you read for it, or none> NAME=<the name field in its frontmatter>. Then say DONE."}
cmd = ["claude", "-p", "--agent", "murmuration:research-pi", "--plugin-dir", plug, "--model", "haiku", "--permission-mode", a.mode, "--output-format", "stream-json", "--verbose", "--include-hook-events", prompts[a.prompt]]
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=600)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
init = None; first = None; ids = []; uses = {}; reads = []; errs = {}; res = None; final = ""; calls = []
for l in p.stdout.splitlines():
    try: r = json.loads(l)
    except ValueError: continue
    if r.get("type") == "system" and r.get("subtype") == "init": init = r
    if r.get("type") == "assistant":
        m = r["message"]
        if m["id"] not in ids: ids.append(m["id"])
        if first is None: first = m.get("usage", {})
        for c in m.get("content", []):
            if c.get("type") == "tool_use":
                uses[c["id"]] = c; calls.append(c["name"] + ":" + json.dumps(c.get("input"))[:140])
                if c["name"] == "Read": reads.append(c["id"])
            if c.get("type") == "text": final = c["text"]
    if r.get("type") == "user" and isinstance(r.get("message", {}).get("content"), list):
        for c in r["message"]["content"]:
            if c.get("type") == "tool_result": errs[c["tool_use_id"]] = bool(c.get("is_error"))
    if r.get("type") == "result": res = r
u = first or {}
tot = sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
rd = [(uses[i]["input"].get("file_path"), errs.get(i)) for i in reads]
sm = dict(cell=a.cell, prompt=a.prompt, export=ex, rc=p.returncode, wall_s=round(time.time() - t0, 1), req0_total=tot, req0_usage=u, n_requests=len(ids),
          reads=rd, reads_failed=sum(1 for _, e in rd if e), calls=calls, final=final, tool_names=(init or {}).get("tools", []),
          init_skills=len((init or {}).get("skills", [])), has_lab_status=any("lab-status" in s for s in (init or {}).get("slash_commands", [])),
          cost_usd=(res or {}).get("total_cost_usd"), is_error=(res or {}).get("is_error"), session_id=(init or {}).get("session_id"), mode=a.mode)
json.dump(sm, open(os.path.join(base, "summary.json"), "w"), indent=1)
print(a.cell, "rc", p.returncode, "req0", tot, "nreq", len(ids), "reads", rd, "cost", sm["cost_usd"], "|", final[:200].replace("\n", " "))
