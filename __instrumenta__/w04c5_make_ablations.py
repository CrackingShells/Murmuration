"""Builds ablation copies of the lean plugin (66a0902) under DEST: nogate (python -S -I at every PostToolUse/PostToolBatch, no sh gate), noSI (plain python3), nopyc (-B and no __pycache__), nojson (handback_core loads/dumps replaced by json's).

Inputs: argv[1] = the lean plugin root (git archive of 66a0902), argv[2] = DEST (created fresh). Output: DEST/<variant>/ plugin roots, each differing from the lean one in one thing only.
"""
import json, os, shutil, sys
src, dest = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
shutil.rmtree(dest, ignore_errors=True); os.makedirs(dest)
def mk(name):
    d = os.path.join(dest, name); shutil.copytree(src, d, ignore=shutil.ignore_patterns("__pycache__")); return d
d = mk("nogate"); p = d + "/hooks/hooks.json"; h = json.load(open(p))
for ev in ("PostToolUse", "PostToolBatch"):
    for g in h["hooks"][ev]:
        for x in g["hooks"]:
            if x["command"].startswith("p="): x["command"] = 'python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/budget.py"'
json.dump(h, open(p, "w"), indent=1)
d = mk("noSI"); p = d + "/hooks/hooks.json"; t = open(p).read(); open(p, "w").write(t.replace("python3 -S -I ", "python3 "))
d = mk("nopyc"); p = d + "/hooks/hooks.json"; t = open(p).read(); open(p, "w").write(t.replace("python3 -S -I ", "python3 -S -I -B "))
d = mk("nojson")
open(d + "/scripts/handback_core.py", "a").write("\nimport json as _jm   # ablation: json instead of the hand-written reader/writer\ndef loads(data): return _jm.loads(data)\ndef dumps(obj, sort_keys=False): return _jm.dumps(obj, sort_keys=sort_keys)\n")
for n in ("nogate", "noSI", "nopyc", "nojson"):
    print(n, [c["command"][:60] for g in json.load(open(os.path.join(dest, n, "hooks/hooks.json")))["hooks"]["PostToolUse"][:1] for c in g["hooks"]])
