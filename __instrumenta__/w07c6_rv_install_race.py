#!/usr/bin/env python3
"""Races many scripts/install_binary.py runs against one data folder while a loop executes the installed guard; counts guard runs that failed to start or gave a wrong answer; also tries a stale/corrupt installed file. Usage: w07c6_rv_install_race.py <plugin root with bin/ and scripts/> <scratch data folder> [rounds]. Reproducer-w07-5."""
import json, os, shutil, subprocess, sys, threading, time, hashlib
root, data = sys.argv[1], sys.argv[2]
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 6
shutil.rmtree(data, ignore_errors=True)
os.makedirs(data)
env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root, CLAUDE_PLUGIN_DATA=data)
inst = [sys.executable, "-S", "-I", os.path.join(root, "scripts", "install_binary.py")]
dest = os.path.join(data, "bin", "murmuration")
ALLOW = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/h"}).encode()
DENY = json.dumps({"tool_name": "Bash", "tool_input": {"command": "cat > .claude/settings.json"}, "cwd": "/h"}).encode()
stop = False
bad = []
runs = [0]


def prober():
    while not stop:
        if not os.path.exists(dest):
            time.sleep(0.001)
            continue
        for payload, want in ((ALLOW, b""), (DENY, b"deny")):
            try:
                r = subprocess.run([dest, "guard"], input=payload, capture_output=True, timeout=20)
            except Exception as e:
                bad.append(("exc", repr(e)))
                continue
            runs[0] += 1
            ok = r.returncode == 0 and ((want == b"" and r.stdout == b"") or (want and want in r.stdout))
            if not ok:
                bad.append((r.returncode, r.stdout[:80], r.stderr[:80]))


ths = [threading.Thread(target=prober) for _ in range(3)]
for t in ths:
    t.start()
rc_all = []
for rd in range(rounds):
    if rd % 2 == 0:
        shutil.rmtree(os.path.join(data, "bin"), ignore_errors=True)
    elif os.environ.get("CORRUPT", "1") == "1" and os.path.exists(dest):  # corrupt installed copy: the installer must replace it
        with open(dest, "ab") as f:
            f.write(b"\0junk")
    ps = [subprocess.Popen(inst, env=env, stderr=subprocess.PIPE) for _ in range(12)]
    rc_all += [p.wait() for p in ps]
    time.sleep(0.2)
stop = True
for t in ths:
    t.join()
src = hashlib.sha256(open(os.path.join(root, "bin", "aarch64-apple-darwin", "murmuration"), "rb").read()).hexdigest()
now = hashlib.sha256(open(dest, "rb").read()).hexdigest()
print("installer exit codes", sorted(set(rc_all)), "| installed == committed:", src == now, "| leftover tmp files:", [f for f in os.listdir(os.path.dirname(dest)) if f != "murmuration"])
print("guard runs during the race:", runs[0], "| bad:", len(bad), bad[:5])
