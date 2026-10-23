# w08-j: runs the Bash commands of a JSON case list through scripts/permission_guard.py decide() and prints the decision per case; input: a JSON list of {id, note, command} (argv[1]); output: stdout (id, decision group or ALLOW, note). Usage: python3 -I w08j_probe_run.py CASES.json
import importlib.util, json, os, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = importlib.util.spec_from_file_location("pg", REPO + "/scripts/permission_guard.py")
PG = importlib.util.module_from_spec(spec); spec.loader.exec_module(PG)
for c in json.load(open(sys.argv[1])):
    r = PG.decide(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd="/h/proj"))
    print(c["id"], r[0] if r else "ALLOW", "|", c["note"])
