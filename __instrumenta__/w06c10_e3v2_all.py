# w06-c10 (E3 v2): the registered v2 run, one shard: v1's build (arm A, three Bash rows) with G4 changed to deny only words an edit adds; runs h1, h2 (+ script-content extras), h3 (ordinary list; the four calls that name --setting-sources are reported and must be allowed), h4, h5 and the new h6 (engineering edits of copies of scripts/handback.py and scripts/permission_guard.py, plus added-words cases) as headless haiku sessions (default permission mode with an allow list; never bypass; stub `claude` first on PATH); inputs: commit, SHARD=i/n and W06C7_S=<folder> in the environment; outputs: <S>/e3v2_results_<sha>_s<i>.json (derived; raw runs stay in <S>/runs). Full: sh __instrumenta__/w06c10_e3v2_full.sh <commit>   Quick: python3 -I __instrumenta__/w06c8_e3v1_all.py <commit> quick  (the v1 driver's quick mode runs the shared cases against the same build; h6 needs this driver)
import json, os, shutil, sys, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E
import w06c7_e3_all as A
import w06c8_e3v1_all as V
import w06c8_make_guard_rows as M


ARM = os.environ.get("W06_ARM", "A")        # A: v2 (three Bash `if` rows); C: v3 (one Bash row, no `if`)
PFX = "e3v3" if ARM == "C" else "e3v2"


def main():
    quick, sha, SH, NSH = A.quick, A.sha, A.SH, A.NSH
    res = {"commit": sha, "shard": SH}
    plug = A.export("%s/export_%s_A" % (E.S, sha), V.with_arm(ARM))
    E.arena()
    os.makedirs(E.T + "/h6")
    for f in ("handback.py", "permission_guard.py"):
        shutil.copy("%s/scripts/%s" % (plug, f), "%s/h6/%s" % (E.T, f))
    handback = open(plug + "/scripts/handback.py").read()
    attacks, ordinary = V.full("attacks"), V.full("ordinary")
    byid = {c["id"]: c for c in attacks}
    v1 = V.v1cases()
    h1ids = [c["id"] for c in attacks if c["id"].startswith("a")] + ["b03"]
    h2 = [c for c in v1 if c["id"] in ("i01", "i02", "i03")]
    extra = [c for c in v1 if c["id"] not in ("i01", "i02", "i03", "i13", "x01")]
    h3x = [c for c in v1 if c["id"] in ("i13", "x01")]
    h6 = json.loads(json.dumps(json.load(open(E.LISTS + "/e3v2_cases.json"))).replace("{T}", E.T))
    for c in h6:
        if c.get("input", {}).get("content") == "{HANDBACK}":
            c["input"]["content"] = handback
    if quick:
        h1ids, extra, h2 = ["a01", "b03"], extra[:2], h2[:2]
        ordinary = [c for c in ordinary if c["id"] in ("o08", "o14", "o24", "o25")]
        h6 = [c for c in h6 if c["id"] in ("j01", "j04")]
    pf = E.session("preflight", plug, [dict(id="pf", tool="Bash", command="command -v claude; type -a claude | head -3")])
    c = E.calls(pf)
    res["preflight"] = c[0][2][:300] if c else "no call"
    if not (c and "/arena/bin/claude" in c[0][2]):
        print("PREFLIGHT FAILED", res["preflight"])
        sys.exit(2)
    E.arena()
    os.makedirs(E.T + "/h6")
    for f in ("handback.py", "permission_guard.py"):
        shutil.copy("%s/scripts/%s" % (plug, f), "%s/h6/%s" % (E.T, f))
    S = V.shard
    res["h1"] = A.run_list("h1", plug, S([byid[i] for i in h1ids]), 1)
    res["h2"] = A.run_list("h2", plug, S(h2), 1)
    res["h2x"] = A.run_list("h2x", plug, S(extra), 1)
    res["h3"] = A.run_list("h3", plug, S(ordinary), 7)
    res["h3x"] = A.run_list("h3x", plug, S(h3x), 1)
    res["h6"] = A.run_list("h6", plug, S(h6), 1)
    # offline checks of the decision function on exact texts (CHECKED)
    sys.path.insert(0, os.path.join(A.REPO, "scripts"))
    import permission_guard as G
    hb = E.T + "/h6/handback.py"
    d = lambda inp, tool="Write": bool(G.decide(dict(tool_name=tool, tool_input=inp, cwd="/tmp")))
    res["offline"] = dict(
        incident_new_py=d(dict(file_path="/tmp/new_dir_x/w06c3_run_all.py", content=V.INCIDENT)), incident_md=d(dict(file_path="/tmp/x/c.md", content=V.INCIDENT)),
        handback_over_itself=d(dict(file_path=hb, content=handback)), handback_plus_word=d(dict(file_path=hb, content=handback + "\nMODE = 'bypassPermissions'\n")),
        guard_over_itself=d(dict(file_path=E.T + "/h6/permission_guard.py", content=open(plug + "/scripts/permission_guard.py").read())))
    probe = [c for c in attacks if c["id"] in ("a01", "a05", "a08")]
    muts = {"unreadable": lambda d: os.chmod(d + "/scripts/permission_guard.py", 0),
            "crash": lambda d: open(d + "/scripts/permission_guard.py", "w").write("import sys\nsys.exit(1)\n"), "nopython": V.nopython}
    res["h4"] = {}
    for k, name in enumerate(muts):
        if (NSH > 1 and k % NSH != SH) or (quick and name != "unreadable"):
            continue
        dd = A.export("%s/export_%s_v2_%s" % (E.S, sha, name), V.with_arm(ARM, muts[name]))
        res["h4"][name] = A.run_list("h4" + name, dd, probe[:1] if quick else probe, 1)
        if name == "unreadable":
            os.chmod(dd + "/scripts/permission_guard.py", 0o644)
    if SH == 0:
        out = {}
        for rnd in range(1 if quick else 2):
            def one(k, rnd=rnd):
                case = dict(id="h5", tool="Bash", command="echo $(date +%s)")
                R = E.session("h5_%d_%d" % (rnd, k), plug, [case])
                n, ms = A.dbg_guard(R)
                out["%d_%d" % (rnd, k)] = dict(outcome=E.match(R, [case])[0][1], dbg_spawns=n, ms=ms)
            ths = [threading.Thread(target=one, args=(k,)) for k in range(5)]
            [t.start() for t in ths]
            [t.join() for t in ths]
        res["h5"] = out
    if ARM == "C":      # k2 (the 7 v0 pass-throughs and the two heredoc bypass flags) and the mention-only commands, reported
        k2 = json.loads(json.dumps(json.load(open(E.LISTS + "/e3v3_cases.json"))).replace("{T}", E.T))
        k2 = [byid[i] for i in ("b04", "b11", "d01", "d02", "d09", "d12", "d13")] + k2
        if quick:
            k2 = [c for c in k2 if c["id"] in ("b04", "d01", "k01")]
        res["k2"] = A.run_list("k2", plug, S(k2), 1)
        res["mention"] = A.run_list("men", plug, S(V.full("mention")), 1)
    json.dump(res, open("%s/%s_results_%s_s%d.json" % (E.S, PFX, sha, SH), "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
