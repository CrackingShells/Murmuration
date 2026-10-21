# w06-c7 (E3): the registered run, end to end: exports a commit of the plugin, builds the arena, checks that the stub `claude` is first on PATH in a live session, then runs the g1 attacks, g2 ordinary commands, mention-only commands, g5 evasions and the g3 fail-closed variants as headless haiku sessions (default permission mode + allow list; never bypass), and writes derived tables (no raw output) to <outdir>/e3_results.json and e3_results.md; inputs: a commit (default HEAD), mode `full` or `quick`; outputs: raw runs under /private/tmp/murmuration-w06/author-w06-5/runs/ (never committed) and the derived tables beside the claim. Cost: full about 20 sessions of 30-90 s each on haiku; quick 4 sessions. Full: python3 -I __instrumenta__/w06c7_e3_all.py <commit> full   Quick: python3 -I __instrumenta__/w06c7_e3_all.py <commit> quick
import json, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "__reports__", "wave-06", "author-w06-5")
commit = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
mode = sys.argv[2] if len(sys.argv) > 2 else "full"
quick = mode == "quick"
sha = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", commit], capture_output=True, text=True, check=True).stdout.strip()
PLUG = "%s/export_%s" % (E.S, sha)


def export(dest, mutate=None):
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest)
    subprocess.run("git -C %s archive %s | tar -x -C %s" % (REPO, sha, dest), shell=True, check=True)
    if mutate:
        mutate(dest)
    return dest


def load(name):
    return E.sub(json.load(open("%s/e3_%s.json" % (E.LISTS, name))))


def dbg_guard(R):
    """(spawns, [ms]) of permission_guard handlers in the session's debug log, independent of the guard's own log."""
    n, ms = 0, []
    p = R + "/dbg.log"
    if os.path.exists(p):
        for l in open(p, errors="replace"):
            if "Hooks: PreToolUse" in l and "permission_guard.py" in l and " finished " in l:
                n += 1
                m = re.search(r"\((\d+)ms\)", l)
                if m:
                    ms.append(int(m.group(1)))
    return n, ms


def guard_log(R):
    p = R + "/guard.log"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def run_list(prefix, plugin, cases, chunk):
    """Run cases in chunks; one retry per chunk for cases the model did not call. Returns {id: dict(outcome, spawns, ...)}."""
    res, i = {}, 0
    todo = [cases[k:k + chunk] for k in range(0, len(cases), chunk)]
    for ci, ch in enumerate(todo):
        for attempt in (0, 1):
            R = E.session("%s_%d_%d" % (prefix, ci, attempt), plugin, ch)
            rows = E.match(R, ch)
            info = json.load(open(R + "/cases.json"))
            n, ms = dbg_guard(R)
            gl = guard_log(R)
            stub = [l for l in open(E.S + "/stub.log")] if os.path.exists(E.S + "/stub.log") else []
            for c, (cid, outcome, text) in zip(ch, rows):
                what = c["command"] if "command" in c else c["input"].get("file_path", "")
                res[cid] = dict(outcome=outcome, spawns_for_case=sum(1 for g in gl if g.get("what") == what[:120]), run=os.path.basename(R))
            res["_run_" + os.path.basename(R)] = dict(dbg_spawns=n, guard_log_lines=len(gl), ms=ms, stub_lines=len(stub), changed=info["changed"], missing=info["missing"],
                                                       wall_s=info["wall_s"], rc=info["rc"])
            miss = [c for c, r in zip(ch, rows) if r[1] == "not-called"]
            if not miss:
                break
            ch = miss
    return res


def summarize(res, kind):
    ids = [k for k in res if not k.startswith("_run_")]
    out = {}
    for k in ids:
        out.setdefault(res[k]["outcome"], []).append(k)
    return out


def main():
    results = {"commit": sha, "mode": mode}
    export(PLUG)
    E.arena()
    # preflight: the stub is first on PATH inside the session's Bash
    R = E.session("preflight", PLUG, [dict(id="pf", tool="Bash", command="command -v claude; type -a claude | head -3; echo $PATH | tr ':' '\\n' | head -2")])
    pf = E.calls(R)
    results["preflight"] = pf[0][2][:300] if pf else "no call"
    assert pf and "/arena/bin/claude" in pf[0][2] and "STUB" not in pf[0][2] or print("PREFLIGHT FAILED", results["preflight"]) or sys.exit(2)
    attacks, ordinary = load("attacks"), load("ordinary")
    if quick:
        attacks = [c for c in attacks if c["id"] in ("a01", "a05", "a08", "b01", "b04", "c01", "d01", "d04")]
        ordinary = [c for c in ordinary if c["id"] in ("o02", "o05", "o08", "o11", "o14", "o16", "o24", "o25")]
    E.arena()   # fresh fixtures after the preflight
    results["g1"] = run_list("g1", PLUG, attacks, 8)
    results["g2"] = run_list("g2", PLUG, ordinary, 7)
    if not quick:
        results["mention"] = run_list("men", PLUG, load("mention"), 6)
        results["g5"] = run_list("g5", PLUG, load("evasions"), 7)
    # g3 fail-closed: the guard unreadable, crashing, the interpreter missing, and the control without onFailure
    probe = [c for c in attacks if c["id"] in ("a01", "a05", "a08")]
    variants = {}

    def unreadable(d):
        os.chmod(d + "/scripts/permission_guard.py", 0)

    def crash(d):
        open(d + "/scripts/permission_guard.py", "w").write("import sys\nsys.exit(1)\n")

    def nopython(d):
        h = open(d + "/hooks/hooks.json").read().replace('python3 \\"${CLAUDE_PLUGIN_ROOT}/scripts/permission_guard.py\\"', 'python3-absent \\"${CLAUDE_PLUGIN_ROOT}/scripts/permission_guard.py\\"')
        open(d + "/hooks/hooks.json", "w").write(h)

    def control(d):          # crash AND no onFailure: the default is fail-open
        crash(d)
        h = json.load(open(d + "/hooks/hooks.json"))
        for g in h["hooks"]["PreToolUse"]:
            for hk in g["hooks"]:
                hk.pop("onFailure", None)
        json.dump(h, open(d + "/hooks/hooks.json", "w"))

    def nopython_control(d):
        nopython(d)
        h = json.load(open(d + "/hooks/hooks.json"))
        for g in h["hooks"]["PreToolUse"]:
            for hk in g["hooks"]:
                hk.pop("onFailure", None)
        json.dump(h, open(d + "/hooks/hooks.json", "w"))
    for name, mut in (("unreadable", unreadable), ("crash", crash), ("nopython", nopython), ("control_crash_no_onFailure", control), ("control_nopython_no_onFailure", nopython_control)):
        if quick and name not in ("unreadable", "control_crash_no_onFailure"):
            continue
        d = export("%s/export_%s_%s" % (E.S, sha, name), mut)
        variants[name] = run_list("g3_" + name, d, probe, 3)
        if name == "unreadable":
            os.chmod(d + "/scripts/permission_guard.py", 0o644)
    results["g3"] = variants
    json.dump(results, open(E.S + "/e3_results_%s_%s.json" % (sha, mode), "w"), indent=1)
    print("done", E.S + "/e3_results_%s_%s.json" % (sha, mode))


main()
