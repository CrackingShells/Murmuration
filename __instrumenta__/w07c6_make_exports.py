# Builds the minimal plugin exports that w07-c6's headless sessions load with --plugin-dir, from the committed tree of a git revision: hooks (guard rows only) + scripts + bin + plugin.json; inputs: repo, revision, scratch folder; outputs: <S>/exp_<variant>/ for A, B, Bstub, Bnobin (and prints the data-folder name the platform will use for each).
# usage: python3 -I __instrumenta__/w07c6_make_exports.py REPO REV S [--variants A,B,Bstub,Bnobin]
# A = guard rows in exec form starting `python3 -S -I scripts/permission_guard.py`; B = the committed rows (exec of ${CLAUDE_PLUGIN_DATA}/bin/murmuration guard) plus the SessionStart installer;
# Bstub = B whose bin/<host>/murmuration is a stub that crashes on call 1, hangs on call 2, and runs the real binary from call 3 (counter file next to the stub's data folder);
# Bnobin = B without bin/, so the installer writes the Python launcher. Every export has its own plugin name (w07c6-<variant>), hence its own data folder.
import json, os, platform, shutil, subprocess, sys, tarfile, io

repo, rev, S = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
variants = sys.argv[sys.argv.index("--variants") + 1].split(",") if "--variants" in sys.argv else ["A", "B", "Bstub", "Bnobin"]
host = {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"}[platform.machine()]
tar = subprocess.run(["git", "-C", repo, "archive", rev, "hooks", "scripts", "bin", ".claude-plugin"], capture_output=True, check=True).stdout
for v in variants:
    d = os.path.join(S, "exp_" + v)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="data")
    pj = json.load(open(d + "/.claude-plugin/plugin.json"))
    pj["name"] = "w07c6-" + v.lower()
    pj.pop("skills", None)
    json.dump(pj, open(d + "/.claude-plugin/plugin.json", "w"), indent=2)
    hooks = json.load(open(d + "/hooks/hooks.json"))["hooks"]
    pre = [g for g in hooks["PreToolUse"] if any("murmuration" in h.get("command", "") for h in g["hooks"])]
    new = {"PreToolUse": pre}
    if v != "A":
        new["SessionStart"] = [g for g in hooks["SessionStart"] if any("install_binary" in " ".join(h.get("args", [])) for h in g["hooks"])]
    else:
        for g in pre:
            for h in g["hooks"]:
                h["command"] = "python3"
                h["args"] = ["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/permission_guard.py"]
    json.dump({"hooks": new}, open(d + "/hooks/hooks.json", "w"), indent=2)
    if v == "Bnobin":
        shutil.rmtree(d + "/bin")
    if v == "Bstub":
        real = os.path.join(d, "bin", host, "murmuration")
        shutil.move(real, real + ".real")
        counter = os.path.join(S, "stub_counter")
        open(os.path.join(d, "bin", host, "murmuration"), "w").write(
            "#!/bin/sh\nn=$(cat '%s' 2>/dev/null || echo 0); n=$((n+1)); echo $n > '%s'\n"
            "if [ $n -eq 1 ]; then echo 'stub: simulated crash' >&2; exit 101; fi\n"
            "if [ $n -eq 2 ]; then sleep 60; exit 0; fi\n"
            "exec '%s' \"$@\"\n" % (counter, counter, "REALPATH"))
        os.chmod(os.path.join(d, "bin", host, "murmuration"), 0o755)
        # the stub needs the real binary at a fixed path outside the export (the installer copies only bin/<host>/murmuration)
        keep = os.path.join(S, "real_murmuration")
        shutil.copy(real + ".real", keep)
        os.remove(real + ".real")
        p = os.path.join(d, "bin", host, "murmuration")
        open(p, "w").write(open(p).read().replace("REALPATH", keep))
    print(v, d, "plugin name", pj["name"])
