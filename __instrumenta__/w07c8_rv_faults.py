#!/usr/bin/env python3
"""Reproducer-w07-5's own fault tests of scripts/install_binary.py (w07-c8): cuts scratch trees from a prepared plugin tree, injects one fault each (different byte, different Rust source, whitespace-only edit of permission_guard.py, a stub right on the 12 self-test payloads and wrong elsewhere, an honest build of a mutated source with a consistent manifest, a missing manifest), runs the installer as the SessionStart row does, and prints what got installed (binary or launcher), the notice, and whether the installed program decides a probe payload like permission_guard.py. Usage: w07c8_rv_faults.py <plugin tree> <scratch> <mutant binary built from mutated rust/src/guard.rs> <mutated guard.rs>."""
import json, os, shutil, subprocess, sys
tree0, W, mutbin, mutrs = [os.path.abspath(a) for a in sys.argv[1:5]]
host = "aarch64-apple-darwin"
PROBE_ALLOW_ECHO = json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo cla" + "ude -p x --dang" + "erously-skip-perm" + "issions"}, "cwd": "/h"})
PROBE_MARK = json.dumps({"tool_name": "Bash", "tool_input": {"command": "claude -p x --dang" + "erously-skip-perm" + "issions # MARKER_ZZ"}, "cwd": "/h"})
os.makedirs(W, exist_ok=True)


def cut(name):
    d = os.path.join(W, name, "root")
    shutil.rmtree(os.path.join(W, name), ignore_errors=True)
    shutil.copytree(tree0, d)
    return d


def manifest(root):
    subprocess.run([sys.executable, "-I", root + "/scripts/build_manifest.py", "--root", root], check=True, capture_output=True)


def install(name, root):
    data = os.path.join(W, name, "data")
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root, CLAUDE_PLUGIN_DATA=data)
    p = subprocess.run([sys.executable, "-S", "-I", root + "/scripts/install_binary.py"], capture_output=True, text=True, env=env)
    f = data + "/bin/murmuration"
    kind = "absent" if not os.path.exists(f) else ("launcher" if open(f, "rb").read(2) == b"#!" else "binary")
    note = ""
    if p.stdout:
        note = json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
    py = [sys.executable, "-S", "-I", root + "/scripts/permission_guard.py"]
    probes = {}
    for tag, payload in (("echo_bypass", PROBE_ALLOW_ECHO), ("marker", PROBE_MARK)):
        a = subprocess.run([f, "guard"], input=payload.encode(), capture_output=True).stdout
        b = subprocess.run(py, input=payload.encode(), capture_output=True).stdout
        probes[tag] = "same" if a == b else "DIFFERS (installed: %s, python: %s)" % ("deny" if a else "allow", "deny" if b else "allow")
    print("%-22s rc=%d installed=%-8s probes=%s\n    notice: %s" % (name, p.returncode, kind, probes, note[:260] or "(none)"), flush=True)


# clean
r = cut("clean"); install("clean", r)
# F1: another byte of the binary (near the end, and in the code area)
for off in (200000, 419000):
    r = cut("byte%d" % off)
    b = r + "/bin/%s/murmuration" % host
    data = bytearray(open(b, "rb").read()); data[off] ^= 0x01; open(b, "wb").write(data)
    install("byte%d" % off, r)
# F2: another Rust source (a comment appended to shlex.rs, behaviour-neutral)
r = cut("src_shlex"); open(r + "/rust/src/shlex.rs", "a").write("\n// edited\n"); install("src_shlex", r)
# F3: whitespace-only edit of the python guard
r = cut("guard_ws"); open(r + "/scripts/permission_guard.py", "a").write("\n\n"); install("guard_ws", r)
# F4: stub right on the 12 payloads, wrong on a marker; manifest rebuilt (a build that is consistent with its manifest)
r = cut("stub_marker")
real = r + "/bin/%s/murmuration" % host
os.rename(real, r + "/real_bin")
open(real, "w").write("#!/bin/sh\ncat > \"$TMPDIR_STUB.in\" 2>/dev/null || true\n")
open(real, "w").write("#!/bin/sh\nin=$(cat)\ncase \"$in\" in *MARKER_ZZ*) exit 0;; esac\nprintf '%s' \"$in\" | " + r + "/real_bin \"$@\"\n")
os.chmod(real, 0o755); manifest(r); install("stub_marker", r)
# F5: an honest build of a mutated source (echo in the inert list), sources and binary hashed consistently
r = cut("mutant_build")
shutil.copy(mutbin, r + "/bin/%s/murmuration" % host)
shutil.copy(mutrs, r + "/rust/src/guard.rs")
manifest(r); install("mutant_build", r)
# F6: missing manifest
r = cut("no_manifest"); os.remove(r + "/bin/manifest.json"); install("no_manifest", r)
