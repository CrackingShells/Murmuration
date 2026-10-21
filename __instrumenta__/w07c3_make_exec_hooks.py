# w07-c3: rewrites hooks/hooks.json from shell form (`command` string) to exec form (`command` + `args`, no shell), same rows otherwise; input: path of a hooks.json (in place, or --out FILE); output: the rewritten file; the split is shlex.split of the string, so every argument is what the shell would have passed
"""usage: w07c3_make_exec_hooks.py HOOKS_JSON [--out FILE]
A handler with no `args` and a `command` that shlex-splits into a bare executable plus arguments without any shell feature (no pipes, `&&`, `;`, redirects, `$`, backticks outside
the plugin-root placeholder `${CLAUDE_PLUGIN_ROOT}`) becomes {"command": argv[0], "args": argv[1:]}; anything else stops the script (nothing is guessed). Key order inside a handler is kept.
"""
import json, re, shlex, sys

src = sys.argv[1]
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else src
SHELL = re.compile(r"[|&;<>`()]|\$(?!\{CLAUDE_PLUGIN_ROOT\})")
doc = json.load(open(src))
n = 0
for groups in doc["hooks"].values():
    for g in groups:
        for h in g["hooks"]:
            if h.get("type") != "command" or "args" in h:
                continue
            c = h["command"]
            if SHELL.search(c):
                raise SystemExit("shell feature in: " + c)
            argv = shlex.split(c)
            new = {}
            for k, v in h.items():
                if k == "command":
                    new["command"] = argv[0]; new["args"] = argv[1:]
                else:
                    new[k] = v
            h.clear(); h.update(new); n += 1
text = json.dumps(doc, indent=2)
text = re.sub(r'"args": \[([^\]]*)\]', lambda m: '"args": [' + ", ".join(x.strip() for x in m.group(1).split(",\n")) + "]", text)   # one line per args array: a small diff
open(out, "w").write(text)
print("rewrote %d handlers into exec form: %s" % (n, out))
