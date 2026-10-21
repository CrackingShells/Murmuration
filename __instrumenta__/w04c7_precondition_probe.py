# measures, in a fresh copy of the 429-script lab under RUNROOT with COLGREP_DATA_DIR inside it, the characters of `ls -1 __instrumenta__` and of one headless colgrep `search` result (limit 5, paths __instrumenta__) for a query; input: EXPORT SCRIPTS RUNROOT QUERY; output: a line on stdout and the raw stream-json in RUNROOT/probe.jsonl
import json, os, shutil, subprocess, sys
export, scripts, root, query = [os.path.abspath(a) for a in sys.argv[1:4]] + [sys.argv[4]]
lab = os.path.join(root, "lab"); shutil.rmtree(lab, ignore_errors=True); os.makedirs(os.path.join(lab, "__instrumenta__"))
for f in os.listdir(scripts): shutil.copy(os.path.join(scripts, f), os.path.join(lab, "__instrumenta__", f))
env = dict(os.environ, COLGREP_DATA_DIR=os.path.join(lab, ".colgrep"), CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0"); env.pop("CLAUDE_PROJECT_DIR", None)
subprocess.run(["git", "init", "-q", "."], cwd=lab, check=True)
subprocess.run([sys.executable, os.path.join(export, "scripts", "lab_init.py"), "--project", lab], input="probe", text=True, capture_output=True, env=env, cwd=lab, timeout=300)
ls1 = sum(len(n) + 1 for n in os.listdir(os.path.join(lab, "__instrumenta__")))
prompt = ("Call the colgrep search tool once with query \"%s\", paths [\"__instrumenta__\"], limit 5, and then answer with the single word done. If the tool is not loaded, load it first with ToolSearch." % query)
out = subprocess.run(["claude", "-p", "--plugin-dir", export, "--permission-mode", "auto", "--output-format", "stream-json", "--verbose", prompt], cwd=lab, env=env, capture_output=True, text=True, timeout=400).stdout
open(os.path.join(root, "probe.jsonl"), "w").write(out)
ids, chars, cost = {}, [], None
for line in out.splitlines():
    try: r = json.loads(line)
    except ValueError: continue
    if r.get("type") == "result": cost = r.get("total_cost_usd")
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list):
        for b in c:
            if b.get("type") == "tool_use" and b["name"].endswith("colgrep__search"): ids[b["id"]] = b["input"]
            if b.get("type") == "tool_result" and b["tool_use_id"] in ids:
                x = b.get("content"); chars.append(len(x) if isinstance(x, str) else sum(len(t.get("text", "")) for t in x))
print("ls_1_chars", ls1, "search_chars", chars, "ratio", [round(ls1 / c, 2) for c in chars], "cost", cost, "inputs", list(ids.values()))
