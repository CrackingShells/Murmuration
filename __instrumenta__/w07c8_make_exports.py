# Builds the two plugin exports for w07-c8's live sessions (h4) from the committed tree of a git revision: hooks (guard rows and the installer row) + scripts + bin + rust + plugin.json; Hclean is the tree as committed, Hfault is the same with scripts/permission_guard.py edited after the build (its denial text reads permission_guard-EDITED, so a decision by the launcher is visible in the model's tool result); inputs: repo, revision, scratch folder; outputs: <S>/exp_Hclean, <S>/exp_Hfault, plugin names w07c8-hclean and w07c8-hfault (data folders ~/.claude/plugins/data/<name>-inline).
# usage: python3 -I __instrumenta__/w07c8_make_exports.py REPO REV S
import json, os, shutil, subprocess, sys, tarfile, io

repo, rev, S = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
tar = subprocess.run(["git", "-C", repo, "archive", rev, "hooks", "scripts", "bin", "rust", ".claude-plugin"], capture_output=True, check=True).stdout
for v in ("Hclean", "Hfault"):
    d = os.path.join(S, "exp_" + v)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="data")
    pj = json.load(open(d + "/.claude-plugin/plugin.json"))
    pj["name"] = "w07c8-" + v[1:].lower()
    pj.pop("skills", None)
    json.dump(pj, open(d + "/.claude-plugin/plugin.json", "w"), indent=2)
    hooks = json.load(open(d + "/hooks/hooks.json"))["hooks"]
    new = {"PreToolUse": [g for g in hooks["PreToolUse"] if any("murmuration" in h.get("command", "") for h in g["hooks"])],
           "SessionStart": [g for g in hooks["SessionStart"] if any("install_binary" in " ".join(h.get("args", [])) for h in g["hooks"])]}
    json.dump({"hooks": new}, open(d + "/hooks/hooks.json", "w"), indent=2)
    if v == "Hfault":
        p = d + "/scripts/permission_guard.py"
        s = open(p).read()
        assert '"permission_guard (%s): %s.' in s
        open(p, "w").write(s.replace('"permission_guard (%s): %s.', '"permission_guard-EDITED (%s): %s.', 1))
    print(v, d, "plugin name", pj["name"])
