# w06-c9: writes plugin variants (hooks.json command forms for budget.py and handback.py) from a plugin tree (a git export or the working tree) into new folders; inputs: SRC tree, OUT folder (must not exist), form name; output: OUT with hooks/ and scripts/ copied and the hook commands of budget.py and handback.py rewritten
"""usage: w06c9_variants.py SRC OUT FORM
FORM, the command that replaces `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"` (hooks.json rows keep their events, matchers and count):
  main      unchanged
  si        python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"
  s         python3 -S "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"
  sic       python3 -S -I -c "import sys; sys.path.insert(0, sys.argv[1]); import <name>; <name>.main()" "${CLAUDE_PLUGIN_ROOT}/scripts"   (the module is imported, so Python keeps its bytecode)
  sc        the same with -S only
  rh        python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" <name>   (run_hook.py imports the script, so Python keeps its bytecode)
"""
import json, os, shutil, sys

src, out, form = sys.argv[1:4]
if os.path.exists(out):
    raise SystemExit("OUT exists: " + out)
os.makedirs(out)
for d in ("hooks", "scripts", "agents", "skills", ".claude-plugin"):
    if os.path.isdir(os.path.join(src, d)):
        shutil.copytree(os.path.join(src, d), os.path.join(out, d), ignore=shutil.ignore_patterns("__pycache__"))
os.makedirs(os.path.join(out, "__reports__"), exist_ok=True)
FORMS = {
    "main": None,
    "si": 'python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/%s.py"',
    "s": 'python3 -S "${CLAUDE_PLUGIN_ROOT}/scripts/%s.py"',
    "sic": 'python3 -S -I -c "import sys; sys.path.insert(0, sys.argv[1]); import %s; %s.main()" "${CLAUDE_PLUGIN_ROOT}/scripts"',
    "rh": 'python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" %s',
    "sc": 'python3 -S -c "import sys; sys.path.insert(0, sys.argv[1]); import %s; %s.main()" "${CLAUDE_PLUGIN_ROOT}/scripts"',
}
path = os.path.join(out, "hooks", "hooks.json")
data = json.load(open(path))
if FORMS[form]:
    for groups in data["hooks"].values():
        for g in groups:
            for h in g["hooks"]:
                for name in ("budget", "handback"):
                    old = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/%s.py"' % name
                    if h["command"] == old:
                        h["command"] = FORMS[form].replace("%s", name)
    json.dump(data, open(path, "w"), indent=2)
print(out, form)
