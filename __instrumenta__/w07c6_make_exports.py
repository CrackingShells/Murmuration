# Builds the minimal plugin exports that w07-c6's headless sessions load with --plugin-dir, from the committed tree of a git revision: hooks (guard rows only) + scripts + bin + plugin.json; inputs: repo, revision, scratch folder; outputs: <S>/exp_<variant>/ for A, B, Bstub, Bnobin (and prints the data-folder name the platform will use for each).
# usage: python3 -I __instrumenta__/w07c6_make_exports.py REPO REV S [--variants A,B,Bstub,Bnobin]
# A = guard rows in exec form starting `python3 -S -I scripts/permission_guard.py`; B = the committed rows (exec of ${CLAUDE_PLUGIN_DATA}/bin/murmuration guard) plus the SessionStart installer;
# Bstub = B whose bin/<host>/murmuration is the Mach-O stub w07c6_stub.c: crash on call 1, hang on call 2, the real binary from call 3 (counter file S/stub_counter);
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
        keep = os.path.join(S, "real_murmuration")      # the real binary at a fixed path outside the export (the installer copies only bin/<host>/murmuration)
        shutil.copy(real, keep)
        subprocess.run(["clang", "-O2", "-DCOUNTER=\"%s\"" % os.path.join(S, "stub_counter"), "-DREAL=\"%s\"" % keep, "-o", real, os.path.join(os.path.dirname(os.path.abspath(__file__)), "w07c6_stub.c")], check=True)
    print(v, d, "plugin name", pj["name"])
