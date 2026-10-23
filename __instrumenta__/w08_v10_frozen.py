# w08-c10 verifier: decides the 739 frozen cases of explorer-w08-j and the 9 probe cases with the Python and the Rust guard of a BASE and a NEW tree and tallies against the labels; inputs: frozen set JSON, probe JSON, two trees; output: stdout (counts, every case whose decision differs between base and new, labelled-true cases still allowed on new, python-vs-rust differences). Usage: python3 -I w08_v10_frozen.py SET.json PROBES.json BASE_TREE NEW_TREE [--jobs N]
import concurrent.futures, importlib.util, json, os, subprocess, sys

a = [x for x in sys.argv[1:] if not x.startswith("--")]
jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
if str(jobs) in a: a.remove(str(jobs))
SET, PROBES, BASE, NEW = a[:4]


def load(tree):
    s = importlib.util.spec_from_file_location("pg" + str(abs(hash(tree))), os.path.join(tree, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def ev(c):
    return dict(tool_name=c["tool"], tool_input=c["input"], cwd=c.get("cwd") or "")


def rs(tree, c):
    p = subprocess.run([os.path.join(tree, "bin", "aarch64-apple-darwin", "murmuration"), "guard"], input=json.dumps(ev(c)), capture_output=True, text=True, timeout=60)
    return bool(p.stdout.strip()) if p.returncode == 0 else None


cases = json.load(open(SET))["cases"]
for c in cases:
    if isinstance(c["input"], str):
        c["input"] = eval(c["input"])
for i, p in enumerate(json.load(open(PROBES))):
    cases.append(dict(id=p["id"], tool="Bash", input=dict(command=p["command"]), cwd="/private/tmp", label="probe", source="probe"))
PB, PN = load(BASE), load(NEW)
with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
    RB = list(ex.map(lambda c: rs(BASE, c), cases))
    RN = list(ex.map(lambda c: rs(NEW, c), cases))
for c, rb, rn in zip(cases, RB, RN):
    c["pb"], c["pn"] = bool(PB.decide(ev(c))), bool(PN.decide(ev(c)))
    c["rb"], c["rn"] = rb, rn
fro = [c for c in cases if c["label"] in ("true", "false")]
for lab in ("true", "false"):
    k = [c for c in fro if c["label"] == lab]
    print("label %-5s n=%d: denied base py/rs %d/%d new py/rs %d/%d" % (lab, len(k), sum(c["pb"] for c in k), sum(bool(c["rb"]) for c in k), sum(c["pn"] for c in k), sum(bool(c["rn"]) for c in k)))
print("python!=rust: base %d new %d (all %d cases)" % (sum(1 for c in cases if c["pb"] != c["rb"]), sum(1 for c in cases if c["pn"] != c["rn"]), len(cases)))
print("base denied -> new allowed (py/rs):", sum(1 for c in cases if c["pb"] and not c["pn"]), sum(1 for c in cases if c["rb"] and not c["rn"]))
for c in cases:
    if c["pb"] != c["pn"] or c["rb"] != c["rn"]:
        print("CHANGED %s label=%s src=%s py %s->%s rs %s->%s | %s" % (c["id"], c["label"], c["source"], c["pb"], c["pn"], c["rb"], c["rn"], (c["input"].get("command") or c["input"].get("file_path") or "")[:130].replace("\n", "\\n")))
for c in fro:
    if c["label"] == "true" and not c["pn"]:
        print("TRUE-STILL-ALLOWED %s indirect=%s | %s" % (c["id"], c.get("indirect"), (c["input"].get("command") or c["input"].get("file_path") or "")[:130].replace("\n", "\\n")))
for c in cases:
    if c["label"] == "probe":
        print("PROBE %s base py/rs %s/%s new py/rs %s/%s" % (c["id"], c["pb"], c["rb"], c["pn"], c["rn"]))
