# w07-c6 g2, offline part: runs scripts/install_binary.py the way the SessionStart row does (exec form, CLAUDE_PLUGIN_ROOT and CLAUDE_PLUGIN_DATA in the environment) against scratch folders, and checks the cases: fresh copy, second run is a no-op, a changed target is replaced, an unwritable data folder fails with exit 1 and a message on stderr, missing variables fail the same way, no binary for the platform writes a launcher; then runs the launcher over the registered cases with scripts/check_guard_equal.py; inputs: the export folder S/exp_B and S/exp_Bnobin from w07c6_make_exports.py, the repo; output: one line per case on stdout.
# usage: python3 -I __instrumenta__/w07c6_g2_offline.py REPO S
import hashlib, os, shutil, stat, subprocess, sys, tempfile
repo, S = sys.argv[1], os.path.abspath(sys.argv[2])
def run(root, data, drop=()):
    env = {k: v for k, v in os.environ.items() if k not in drop}
    if root is not None: env["CLAUDE_PLUGIN_ROOT"] = root
    if data is not None: env["CLAUDE_PLUGIN_DATA"] = data
    p = subprocess.run([sys.executable, "-S", "-I", repo + "/scripts/install_binary.py"], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
T = tempfile.mkdtemp(prefix="g2off_")
root = S + "/exp_B"; host = [d for d in os.listdir(root + "/bin")][0] if False else None
import platform
host = {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"}[platform.machine()]
src = "%s/bin/%s/murmuration" % (root, host)
d = T + "/data"
print("1 fresh data folder:", run(root, d)[:1], "target sha == source sha:", sha(d + "/bin/murmuration") == sha(src), "mode %o" % stat.S_IMODE(os.stat(d + "/bin/murmuration").st_mode))
m1 = os.stat(d + "/bin/murmuration").st_mtime_ns; print("2 second run, nothing to copy:", run(root, d)[:1], "mtime unchanged:", os.stat(d + "/bin/murmuration").st_mtime_ns == m1)
open(d + "/bin/murmuration", "ab").write(b"x"); print("3 target differs (appended byte), replaced:", run(root, d)[:1], "equal again:", sha(d + "/bin/murmuration") == sha(src))
os.remove(d + "/bin/murmuration"); print("4 target absent, copied:", run(root, d)[:1], os.path.exists(d + "/bin/murmuration"))
ro = T + "/ro"; os.makedirs(ro); os.chmod(ro, 0o500); r = run(root, ro + "/data"); print("5 unwritable data folder: exit", r[0], "stdout %r" % r[1], "stderr %r" % r[2][:160]); os.chmod(ro, 0o700)
fl = T + "/file"; open(fl, "w").write("x"); r = run(root, fl + "/sub"); print("6 data path under a plain file: exit", r[0], "stderr %r" % r[2][:120])
r = run(root, None, drop=("CLAUDE_PLUGIN_DATA",)); print("7 CLAUDE_PLUGIN_DATA unset: exit", r[0], "stderr %r" % r[2][:120])
r = run(None, d, drop=("CLAUDE_PLUGIN_ROOT",)); print("8 CLAUDE_PLUGIN_ROOT unset: exit", r[0], "stderr %r" % r[2][:120])
nb = S + "/exp_Bnobin"; dl = T + "/datal"; r = run(nb, dl); p = dl + "/bin/murmuration"
print("9 no binary for the platform (bin/ absent): exit", r[0], "launcher:", repr(open(p).read()[:160]), "mode %o" % stat.S_IMODE(os.stat(p).st_mode)); print("10 launcher again:", run(nb, dl)[:1])
print("launcher path for check_guard_equal.py:", p)
open(T + "/launcher_path", "w").write(p)
