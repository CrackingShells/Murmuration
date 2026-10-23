# w08-j: replays events through scripts/permission_guard.py (decide() in process) and the Rust `murmuration guard` (one process per event, stdin JSON, as the hook starts it); input: a JSONL of events (fields id, tool, input, cwd) or the frozen set JSON (entries with id, tool, input, cwd); output: JSONL with id, py and rs decisions (rule group G1..G4, G? or null) to argv[2]. Usage: python3 -I w08j_replay.py IN OUT [--jobs N] [--rust BIN]
import concurrent.futures, importlib.util, json, os, re, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RUST = os.path.join(REPO, "bin", "aarch64-apple-darwin", "murmuration")
spec = importlib.util.spec_from_file_location("pg", os.path.join(REPO, "scripts", "permission_guard.py"))
PG = importlib.util.module_from_spec(spec); spec.loader.exec_module(PG)
GRP = re.compile(r"permission_guard \((G.)\)")


def load(path):
    txt = open(path).read()
    if txt.lstrip().startswith("["):
        return json.loads(txt)
    if txt.lstrip().startswith("{") and '"cases"' in txt[:3000]:
        return json.loads(txt)["cases"]
    return [json.loads(l) for l in txt.splitlines() if l.strip()]


def event(c):
    return dict(tool_name=c["tool"], tool_input=c["input"], cwd=c.get("cwd") or "")


def py(c):
    try:
        r = PG.decide(event(c))
    except Exception as e:
        return "G?"
    return r[0] if r else None


def rs(c, rust):
    p = subprocess.run([rust, "guard"], input=json.dumps(event(c)), capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return "rc%d" % p.returncode
    if not p.stdout.strip():
        return None
    m = GRP.search(p.stdout)
    return m.group(1) if m else "deny?"


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    rust = sys.argv[sys.argv.index("--rust") + 1] if "--rust" in sys.argv else RUST
    if rust in a: a.remove(rust)
    if str(jobs) in a: a.remove(str(jobs))
    cases = load(a[0])
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        rsd = list(ex.map(lambda c: rs(c, rust), cases))
    with open(a[1], "w") as fh:
        for c, r in zip(cases, rsd):
            fh.write(json.dumps(dict(id=c["id"], py=py(c), rs=r)) + "\n")
    print("replayed", len(cases), "py denies", sum(1 for c in cases if py(c)), "rs denies", sum(1 for r in rsd if r))


main()
