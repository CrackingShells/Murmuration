# w07-c6 g5, what it costs to ship: binary size per target, the crate's dependency list, clean build time per target, and the first exec of (a) a fresh COPY of the committed binary (what the SessionStart installer makes), (b) a fresh BUILD with a new cdhash, each against the same file's later execs; inputs: repo, payload file, a scratch folder; output: lines on stdout.
# usage: python3 -I __instrumenta__/w07c6_g5.py REPO PAYLOAD SCRATCH [N]
import os, platform, resource, shutil, statistics as st, subprocess, sys, time
repo, payload, scratch = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]); N = int(sys.argv[4]) if len(sys.argv) > 4 else 12
os.makedirs(scratch, exist_ok=True)
host = {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"}[platform.machine()]
for t in ("aarch64-apple-darwin", "x86_64-apple-darwin"):
    print("size %s: %d bytes" % (t, os.path.getsize("%s/bin/%s/murmuration" % (repo, t))))
print("dependencies:", subprocess.run(["cargo", "tree", "--offline", "--manifest-path", repo + "/rust/Cargo.toml"], capture_output=True, text=True).stdout.strip().replace("\n", " | "))
print("lines of Rust:", subprocess.run("cat %s/rust/src/*.rs | wc -l; cat %s/rust/src/guard.rs %s/rust/src/json.rs %s/rust/src/main.rs %s/rust/src/shlex.rs %s/rust/src/text.rs | wc -l; wc -l < %s/scripts/permission_guard.py" % ((repo,) * 7), shell=True, capture_output=True, text=True).stdout.split())
def timed(path, payload):
    t0 = time.perf_counter()
    with open(payload, "rb") as fh:
        p = subprocess.run([path, "guard"], stdin=fh, capture_output=True)
    return (time.perf_counter() - t0) * 1e3, p.returncode
src = "%s/bin/%s/murmuration" % (repo, host)
firsts, laters = [], []
for i in range(N):
    d = "%s/copy%d" % (scratch, i); shutil.copy(src, d)
    f, _ = timed(d, payload); l = [timed(d, payload)[0] for _ in range(4)]
    firsts.append(f); laters.append(st.median(l))
print("(a) fresh copy of the committed binary, first exec ms: median %.1f (min %.1f, max %.1f), later execs of the same file median %.1f; first minus later median %.1f, first slower in %d of %d" % (st.median(firsts), min(firsts), max(firsts), st.median(laters), st.median(a - b for a, b in zip(firsts, laters)), sum(a > b for a, b in zip(firsts, laters)), N))
bf, bl, bt = [], [], []
for i in range(3):
    td = "%s/build%d" % (scratch, i); shutil.rmtree(td, ignore_errors=True)
    env = dict(os.environ, RUSTFLAGS="-C metadata=w07c6fresh%d" % i)
    t0 = time.perf_counter()
    subprocess.run(["cargo", "build", "--release", "--offline", "--manifest-path", repo + "/rust/Cargo.toml", "--target-dir", td], capture_output=True, env=env, check=True)
    bt.append(time.perf_counter() - t0)
    b = td + "/release/murmuration"
    f, _ = timed(b, payload); l = st.median(timed(b, payload)[0] for _ in range(4)); bf.append(f); bl.append(l)
print("(b) fresh build (clean, new hash each), build seconds %s; first exec ms %s; later execs median ms %s" % ([round(x, 2) for x in bt], [round(x, 1) for x in bf], [round(x, 1) for x in bl]))
print("load average", os.getloadavg())
