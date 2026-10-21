# w07-c8 h1, h2, h3: runs scripts/install_binary.py the way the SessionStart row does (python3 -S -I, CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA in the environment) against scratch trees cut from a git revision with one fault each, and a clean tree, and checks what is installed, what the notice says, and that the installed program decides the registered cases as the tree's permission_guard.py does; then times the installer and runs 12 concurrent installers against one data folder; inputs: repo, revision, scratch folder; outputs: markdown tables on stdout and trees under <scratch>/trees.
# usage: python3 -I __instrumenta__/w07c8_h_tests.py REPO REV SCRATCH [h1|h2|h3 ...]
import hashlib, io, json, os, platform, shutil, statistics as st, subprocess, sys, tarfile, threading, time
repo, rev, W = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
which = sys.argv[4:] or ["h1", "h2", "h3"]
host = {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"}[platform.machine()]
tar = subprocess.run(["git", "-C", repo, "archive", rev, "hooks", "scripts", "bin", "rust", ".claude-plugin"], capture_output=True, check=True).stdout
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def tree(name):
    d = os.path.join(W, "trees", name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="data")
    return d


def install(root, data, python=sys.executable, prefix=()):
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root, CLAUDE_PLUGIN_DATA=data)
    t0 = time.perf_counter()
    p = subprocess.run(list(prefix) + [python, "-S", "-I", root + "/scripts/install_binary.py"], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr, (time.perf_counter() - t0) * 1e3


def kind(data):
    f = data + "/bin/murmuration"
    if not os.path.exists(f):
        return "absent"
    b = open(f, "rb").read(2)
    return "launcher" if b == b"#!" else "binary"


def equal_run(root, data, tag):
    """The registered and malformed sets through the installed program against the tree's own permission_guard.py; prints the checker's rows."""
    out = os.path.join(W, "eq_" + tag)
    p = subprocess.run([sys.executable, "-I", repo + "/scripts/check_guard_equal.py", "--rust", data + "/bin/murmuration", "--python-guard", root + "/scripts/permission_guard.py", "--no-recorded", "--fuzz", "300", "--fuzz-write", "60",
                        "--sets", "registered,malformed,fuzz_bash,fuzz_write", "--jobs", "6", "--out", out], capture_output=True, text=True)
    rows = [l for l in p.stdout.splitlines() if l.split()[:1] and l.split()[0] in ("registered", "malformed", "fuzz_bash", "fuzz_write")]
    return p.returncode == 0, "; ".join(" ".join(r.split()[:4]) for r in rows)


def edit(path, fn):
    s = open(path).read()
    open(path, "w").write(fn(s))


if "h1" in which:
    print("## h1: each doubt falls back, visibly\n")
    print("| fault | installed | notice on stdout (additionalContext) | stderr line | exit | named cause | decisions equal the tree's permission_guard.py (registered, malformed, 300+60 fuzz: events differing) |")
    print("|:--|:--|:--|:--|--:|:--|:--|")
    faults = {}
    t = tree("f1_guard_edited")
    edit(t + "/scripts/permission_guard.py", lambda s: s.replace('"permission_guard (%s): %s.', '"permission_guard-EDITED (%s): %s.', 1))
    faults["permission_guard.py edited after the build"] = (t, "scripts/permission_guard.py changed")
    t = tree("f2_rust_edited")
    edit(t + "/rust/src/guard.rs", lambda s: s + "\n// edited after the build\n")
    faults["rust source edited after the build"] = (t, "Rust sources changed")
    t = tree("f3_byte_flipped")
    b = bytearray(open(t + "/bin/%s/murmuration" % host, "rb").read()); b[len(b) // 2] ^= 0xFF
    open(t + "/bin/%s/murmuration" % host, "wb").write(bytes(b))
    faults["one byte flipped in the binary"] = (t, "does not match its hash")
    t = tree("f4_selftest")
    open(t + "/bin/%s/murmuration" % host, "w").write("#!/bin/sh\ncat > /dev/null\nexit 0\n")
    os.chmod(t + "/bin/%s/murmuration" % host, 0o755)
    subprocess.run([sys.executable, "-I", t + "/scripts/build_manifest.py", "--root", t], check=True, capture_output=True)
    faults["a binary that answers wrongly (stub allows everything; manifest rebuilt so only the self-test can catch it)"] = (t, "self-test payload")
    t = tree("f5_no_manifest")
    os.remove(t + "/bin/manifest.json")
    faults["bin/manifest.json missing (extra case)"] = (t, "manifest.json cannot be read")
    ok = 0
    for i, (name, (t, cause)) in enumerate(faults.items()):
        data = os.path.join(W, "data_h1_%d" % i); shutil.rmtree(data, ignore_errors=True)
        rc, out, err, _ = install(t, data)
        note = ""
        try: note = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        except Exception: pass
        named = cause in note and cause in err
        same, rows = equal_run(t, data, "h1_%d" % i)
        good = kind(data) == "launcher" and rc == 0 and named and same
        ok += good and i < 4
        print("| %s | %s | %s | %s | %d | %s | %s |" % (name, kind(data), "yes" if note else "NO", "yes" if err.strip() else "NO", rc, "yes" if named else "NO", ("equal: " if same else "DIFFER: ") + rows))
        if i == 0: print("\nfirst notice text: `%s`\n" % note)
    print("\nh1 (first 4 faults): %d of 4 install the launcher, name the cause and decide like permission_guard.py\n" % ok)

if "h2" in which:
    print("## h2: the clean tree installs the binary\n")
    t = tree("clean")
    data = os.path.join(W, "data_h2"); shutil.rmtree(data, ignore_errors=True)
    rc, out, err, ms = install(t, data)
    print("- native (%s): exit %d, installed %s, stdout %r, stderr %r, binary sha equals manifest: %s, stamp present: %s, %.0f ms cold" % (host, rc, kind(data), out, err, sha(data + "/bin/murmuration") == json.load(open(t + "/bin/manifest.json"))["binaries"][host], os.path.exists(data + "/bin/.verified"), ms))
    same, rows = equal_run(t, data, "h2_native")
    print("- native decisions: %s %s" % ("equal" if same else "DIFFER", rows))
    if os.path.exists("/usr/bin/python3"):
        datax = os.path.join(W, "data_h2x"); shutil.rmtree(datax, ignore_errors=True)
        rc, out, err, ms = install(t, datax, python="/usr/bin/python3", prefix=["arch", "-x86_64"])
        mx = json.load(open(t + "/bin/manifest.json"))["binaries"]["x86_64-apple-darwin"]
        print("- x86_64 under Rosetta (`arch -x86_64 /usr/bin/python3`, Python %s): exit %d, installed %s, stdout %r, stderr %r, binary sha equals the x86_64 manifest entry: %s, %.0f ms cold" % (subprocess.run(["arch", "-x86_64", "/usr/bin/python3", "-c", "import platform;print(platform.python_version(), platform.machine())"], capture_output=True, text=True).stdout.strip(), rc, kind(datax), out, err, sha(datax + "/bin/murmuration") == mx, ms))
    print()

if "h3" in which:
    print("## h3: cost and races\n")
    t = tree("clean_h3")
    def timing(label, setup, n=10):
        ms = []
        for i in range(n):
            data = os.path.join(W, "data_h3_%s" % label)
            setup(data)
            rc, out, err, m = install(t, data)
            assert rc == 0, (label, rc, err)
            ms.append(m)
        return ms
    cold = timing("cold", lambda d: shutil.rmtree(d, ignore_errors=True))
    install(t, os.path.join(W, "data_h3_warm"))
    warm = timing("warm", lambda d: None)
    tf = tree("fault_h3"); edit(tf + "/rust/src/guard.rs", lambda s: s + "\n// x\n")
    def fb(label):
        ms = []
        for i in range(10):
            data = os.path.join(W, "data_h3_fb"); shutil.rmtree(data, ignore_errors=True)
            ms.append(install(tf, data)[3])
        return ms
    fall = fb("fb")
    base = [ (lambda t0: (subprocess.run([sys.executable, "-S", "-I", "-c", "pass"]), (time.perf_counter() - t0) * 1e3)[1])(time.perf_counter()) for _ in range(10)]
    q = lambda x: "median %.0f ms (min %.0f, max %.0f)" % (st.median(x), min(x), max(x))
    print("- installer wall time per session start, 10 runs each, whole process incl. the interpreter's start (idle machine, load %.2f): fresh data folder (copy + self-test of 12 payloads) %s; warm (binary and stamp current) %s; fallback to the launcher %s; reference `python3 -S -I -c pass` %s" % (os.getloadavg()[0], q(cold), q(warm), q(fall), q(base)))
    payload = json.loads(open(t + "/scripts/guard_selftest_payloads.json").read())
    exp = {p["name"]: subprocess.run([sys.executable, "-S", "-I", t + "/scripts/permission_guard.py"], input=p["raw"].encode(), capture_output=True).stdout for p in payload}
    total_inst = total_runs = bad_runs = bad_inst = 0
    for rep in range(3):
        data = os.path.join(W, "data_h3_conc%d" % rep); shutil.rmtree(data, ignore_errors=True)
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=t, CLAUDE_PLUGIN_DATA=data)
        procs = [subprocess.Popen([sys.executable, "-S", "-I", t + "/scripts/install_binary.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(12)]
        dest = data + "/bin/murmuration"; runs = bad = 0; deadline = time.time() + 60
        while time.time() < deadline and ( any(p.poll() is None for p in procs) or runs < 20):
            if os.path.exists(dest):
                for p in payload[:4]:
                    try:
                        r = subprocess.run([dest, "guard"], input=p["raw"].encode(), capture_output=True, timeout=10)
                        runs += 1; bad += (r.returncode != 0 or r.stdout != exp[p["name"]])
                    except OSError:
                        runs += 1; bad += 1
            if all(p.poll() is not None for p in procs) and runs >= 20: break
        res = [(p.wait(), p.stdout.read(), p.stderr.read()) for p in procs]
        failed = sum(1 for rc, o, e in res if rc != 0 or o or e)
        mf = json.load(open(t + "/bin/manifest.json"))["binaries"][host]
        leftovers = [f for f in os.listdir(data + "/bin") if ".tmp" in f]
        print("- concurrent round %d: 12 installers, %d failed or noisy; %d guard runs on the installed file while they ran, %d wrong or failed; final binary sha equals manifest: %s; leftover temporary files: %d" % (rep + 1, failed, runs, bad, sha(dest) == mf, len(leftovers)))
        total_inst += 12; bad_inst += failed; total_runs += runs; bad_runs += bad + (0 if sha(dest) == mf else 1) + len(leftovers)
    print("\nh3 concurrency total: %d installers, %d failed; %d guard runs, %d wrong or failed (including final-hash and leftover checks)" % (total_inst, bad_inst, total_runs, bad_runs))
