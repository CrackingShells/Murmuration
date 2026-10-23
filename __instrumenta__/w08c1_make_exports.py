# Builds the two plugin exports of w08-c1's live sessions from the committed tree of a git revision: exp_A (the budget and handback rows in Python exec form: `python3 -S -I run_hook.py <name>`) and exp_B (the committed rows: exec of ${CLAUDE_PLUGIN_DATA}/bin/murmuration <name>); both keep the SessionStart installer, the Bash guard row and every budget/handback row, and have their own plugin name (w08c1-a, w08c1-b), hence their own data folder.
# usage: python3 -I w08c1_make_exports.py REPO REV S
import json, os, shutil, subprocess, sys, tarfile, io

repo, rev, S = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
tar = subprocess.run(["git", "-C", repo, "archive", rev, "hooks", "scripts", "bin", "rust", ".claude-plugin"], capture_output=True, check=True).stdout
for v in ("A", "B"):
    d = os.path.join(S, "exp_" + v)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="fully_trusted")
    pj = json.load(open(d + "/.claude-plugin/plugin.json"))
    pj["name"] = "w08c1-" + v.lower()
    pj.pop("skills", None)
    json.dump(pj, open(d + "/.claude-plugin/plugin.json", "w"), indent=2)
    hooks = json.load(open(d + "/hooks/hooks.json"))["hooks"]
    new = {}
    for ev, groups in hooks.items():
        keep = []
        for g in groups:
            hs = []
            for h in g["hooks"]:
                a = h.get("args", [])
                is_hook = h.get("command", "").endswith("/bin/murmuration") and a and a[0] in ("budget", "handback")
                if is_hook and v == "A":
                    h = dict(h, command="python3", args=["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py", a[0]])
                if is_hook or "install_binary" in " ".join(a) or (ev == "PreToolUse" and g.get("matcher") == "Bash"):
                    hs.append(h)
            if hs:
                keep.append(dict(g, hooks=hs))
        if keep:
            new[ev] = keep
    json.dump({"hooks": new}, open(d + "/hooks/hooks.json", "w"), indent=2)
    print(v, d, "plugin name", pj["name"], {k: len(x) for k, x in new.items()})
