# w06-c8 (E3 v1): the registered v1 run, one shard: exports a commit of the plugin (arm A: the three Bash rows; arm B: the reported variant), then runs h1 (21 G1 forms + a --setting-sources project,local call), h2 (the incident file, an Edit, an .md copy, and script-content extras), h3 (v0's ordinary list plus a `$(...)` call and an .md Write), h4 (guard unreadable, crashing, python missing), h5 (10 `$(...)` calls with five sessions starting in parallel) and the reported v0 cases against v1, as headless haiku sessions (default permission mode with an allow list; never bypass; stub `claude` first on PATH); inputs: commit, SHARD=i/n and W06C7_S=<folder> in the environment; outputs: <S>/e3v1_results_<sha>_s<i>.json (derived; raw runs stay in <S>/runs). Full: sh __instrumenta__/w06c8_e3v1_full.sh <commit>   Quick: python3 -I __instrumenta__/w06c8_e3v1_all.py <commit> quick
import json, os, subprocess, sys, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E
import w06c7_e3_all as A     # reuses export, dbg_guard, run_list; importing it does not run it
import w06c8_make_guard_rows as M

quick = A.quick
sha, SH, NSH = A.sha, A.SH, A.NSH
INCIDENT = subprocess.run(["git", "-C", A.REPO, "show", "c4aaebb:__instrumenta__/w06c3_run_all.py"], capture_output=True, text=True, check=True).stdout


def shard(lst):
    return [c for k, c in enumerate(lst) if k % NSH == SH]


def v1cases():
    out = json.loads(json.dumps(json.load(open(E.LISTS + "/e3v1_cases.json"))).replace("{T}", E.T))
    for c in out:
        if c.get("input", {}).get("content") == "{INCIDENT}":
            c["input"]["content"] = INCIDENT
    return out


def full(name):
    return E.sub(json.load(open("%s/e3_%s.json" % (E.LISTS, name))))


def with_arm(arm, mutate=None):
    def f(d):
        json.dump(M.apply(json.load(open(d + "/hooks/hooks.json")), arm), open(d + "/hooks/hooks.json", "w"), indent=1)
        if mutate:
            mutate(d)
    return f


def nopython(d):
    h = open(d + "/hooks/hooks.json").read().replace('python3 \\"${CLAUDE_PLUGIN_ROOT}', 'python3-absent \\"${CLAUDE_PLUGIN_ROOT}')
    open(d + "/hooks/hooks.json", "w").write(h)


def main():
    res = {"commit": sha, "shard": SH}
    plugA = A.export("%s/export_%s_A" % (E.S, sha), with_arm("A"))
    E.arena()
    attacks, ordinary, ev = full("attacks"), full("ordinary"), full("evasions")
    byid = {c["id"]: c for c in attacks}
    v1 = v1cases()
    h1ids = [c["id"] for c in attacks if c["id"].startswith("a")] + ["b03"]
    h2 = [c for c in v1 if c["id"] in ("i01", "i02", "i03")]
    extra = [c for c in v1 if c["id"] not in ("i01", "i02", "i03", "i13", "x01")]
    h3x = [c for c in v1 if c["id"] in ("i13", "x01")]
    reported = [c for c in attacks if c["id"] not in h1ids] + ev
    armB_att = [byid[i] for i in ("b01", "b02", "b03", "b09")] + [c for c in v1 if c["id"] == "x01"]
    if quick:
        h1ids, extra, reported = ["a01", "a08", "b03"], extra[:2], [byid["d01"], byid["b04"]]
        ordinary = [c for c in ordinary if c["id"] in ("o08", "o14", "o24", "o25")]
        h2, armB_att = h2[:2], armB_att[:2]
    pf = E.session("preflight", plugA, [dict(id="pf", tool="Bash", command="command -v claude; type -a claude | head -3")])
    c = E.calls(pf)
    res["preflight"] = c[0][2][:300] if c else "no call"
    if not (c and "/arena/bin/claude" in c[0][2]):
        print("PREFLIGHT FAILED", res["preflight"])
        sys.exit(2)
    E.arena()
    res["h1"] = A.run_list("h1", plugA, shard([byid[i] for i in h1ids]), 1)
    res["h2"] = A.run_list("h2", plugA, shard(h2), 1)
    res["h2x"] = A.run_list("h2x", plugA, shard(extra), 1)
    res["h3"] = A.run_list("h3", plugA, shard(ordinary), 7)
    res["h3x"] = A.run_list("h3x", plugA, shard(h3x), 1)
    res["reported"] = A.run_list("rep", plugA, shard(reported), 1)
    # offline check of the decision function on the exact incident text (CHECKED)
    sys.path.insert(0, os.path.join(A.REPO, "scripts"))
    import permission_guard as G
    w = lambda path: G.decide(dict(tool_name="Write", tool_input=dict(file_path=path, content=INCIDENT), cwd="/tmp"))
    res["offline"] = dict(incident_py=bool(w("/tmp/x/w06c3_run_all.py")), incident_md=bool(w("/tmp/x/copy.md")), n_lines=len(INCIDENT.splitlines()))
    # h4: fail closed (one variant per shard 0..2)
    probe = [c for c in attacks if c["id"] in ("a01", "a05", "a08")]
    muts = {"unreadable": lambda d: os.chmod(d + "/scripts/permission_guard.py", 0),
            "crash": lambda d: open(d + "/scripts/permission_guard.py", "w").write("import sys\nsys.exit(1)\n"),
            "nopython": nopython}
    res["h4"] = {}
    for k, name in enumerate(muts):
        if (NSH > 1 and k % NSH != SH) or (quick and name != "unreadable"):
            continue
        d = A.export("%s/export_%s_v1_%s" % (E.S, sha, name), with_arm("A", muts[name]))
        res["h4"][name] = A.run_list("h4" + name, d, probe[:1] if quick else probe, 1)
        if name == "unreadable":
            os.chmod(d + "/scripts/permission_guard.py", 0o644)
    # h5: ten `$(...)` calls, five sessions in parallel, twice (shard 0 only), while the other shards keep running
    if SH == 0:
        out = {}
        for rnd in range(1 if quick else 2):
            def one(k, rnd=rnd):
                case = dict(id="h5", tool="Bash", command="echo $(date +%s)")
                R = E.session("h5_%d_%d" % (rnd, k), plugA, [case])
                n, ms = A.dbg_guard(R)
                out["%d_%d" % (rnd, k)] = dict(outcome=E.match(R, [case])[0][1], dbg_spawns=n, ms=ms)
            ths = [threading.Thread(target=one, args=(k,)) for k in range(5)]
            [t.start() for t in ths]
            [t.join() for t in ths]
        res["h5"] = out
    # arm B (reported variant): the --setting-sources row replaced by four rows that spare `user` first
    plugB = A.export("%s/export_%s_B" % (E.S, sha), with_arm("B"))
    res["armB"] = dict(ordinary=A.run_list("Bo", plugB, shard(ordinary), 7), attacks=A.run_list("Ba", plugB, shard(armB_att), 1))
    json.dump(res, open("%s/e3v1_results_%s_s%d.json" % (E.S, sha, SH), "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
