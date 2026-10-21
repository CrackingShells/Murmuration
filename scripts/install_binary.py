#!/usr/bin/env python3
"""SessionStart hook: put the permission guard where the guard rows exec it, `${CLAUDE_PLUGIN_DATA}/bin/murmuration`, once per session; the Rust binary only when nothing doubts it.

Python standard library only; hooks.json starts it in exec form (`python3 -S -I install_binary.py`, no shell).
The binary for this platform (`bin/<target>/murmuration`, macOS arm64 or x86_64) is installed only when all of these hold:
  (a) its sha256 equals the one in `bin/manifest.json`;
  (b) the sha256 of `scripts/permission_guard.py` and of the Rust sources (computed with scripts/build_manifest.py's rule) equal the manifest's, so the binary was built from the rules that are on disk;
  (c) a copy of it, run on the fixed payloads of `scripts/guard_selftest_payloads.json`, gives the same exit code and stdout as `permission_guard.py` run by this interpreter on each of them.
On any doubt (and where no binary fits the platform) it installs a launcher that runs `scripts/permission_guard.py` instead, and tells the session why: a SessionStart
`additionalContext` line the model sees, and a line on stderr. A previous install is replaced by the launcher in that case. Copies are atomic (temporary file, then rename), so concurrent
sessions installing into one data folder never expose a partial file. A stamp file next to the binary records what was verified; while binary, sources and stamp agree, the self-test is not repeated.
Errors that stop the install itself (a data folder that cannot be written, the plugin variables missing) exit 1 with a message on stderr; the guard rows then block Bash calls (onFailure block).
"""
import hashlib
import importlib.util
import json
import os
import platform
import stat
import subprocess
import sys

TARGETS = {("Darwin", "arm64"): "aarch64-apple-darwin", ("Darwin", "x86_64"): "x86_64-apple-darwin"}


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_manifest_tool(root):
    spec = importlib.util.spec_from_file_location("build_manifest", os.path.join(root, "scripts", "build_manifest.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doubt(root, target):
    """Why the binary may not be installed, or None."""
    if target is None:
        return "no binary is built for this platform (%s %s)" % (platform.system(), platform.machine())
    try:
        with open(os.path.join(root, "bin", "manifest.json")) as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as exc:
        return "bin/manifest.json cannot be read (%s)" % type(exc).__name__
    src = os.path.join(root, "bin", target, "murmuration")
    if not os.path.isfile(src):
        return "bin/%s/murmuration is missing" % target
    if digest(src) != manifest.get("binaries", {}).get(target):
        return "the binary bin/%s/murmuration does not match its hash in bin/manifest.json" % target
    if digest(os.path.join(root, "scripts", "permission_guard.py")) != manifest.get("permission_guard_py_sha256"):
        return "scripts/permission_guard.py changed since the binaries were built"
    try:
        _, combined = load_manifest_tool(root).sources_hash(root)
    except Exception as exc:
        return "the Rust sources cannot be hashed (%s)" % type(exc).__name__
    if combined != manifest.get("rust_sources_sha256"):
        return "the Rust sources changed since the binaries were built"
    return None


def run_guard(cmd, raw):
    p = subprocess.run(cmd, input=raw.encode("utf-8", "surrogatepass"), capture_output=True, timeout=5, env=dict(os.environ, LC_ALL="en_US.UTF-8"))
    return p.returncode, p.stdout


def self_test(root, binary):
    """The name of the first payload on which the binary and permission_guard.py differ, or None."""
    with open(os.path.join(root, "scripts", "guard_selftest_payloads.json")) as fh:
        payloads = json.load(fh)
    guard = os.path.join(root, "scripts", "permission_guard.py")
    for p in payloads:
        try:
            want = run_guard([sys.executable, "-S", "-I", guard], p["raw"])
            got = run_guard([binary, "guard"], p["raw"])
        except (OSError, subprocess.SubprocessError) as exc:
            return "%s (%s)" % (p["name"], type(exc).__name__)
        if got != want:
            return p["name"]
    return None


def atomic_write(dest, data, mode):
    tmp = "%s.tmp%d" % (dest, os.getpid())
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, dest)


def launcher_body(root):
    return ("#!/bin/sh\nexec python3 -S -I '%s' \"$@\"\n" % os.path.join(root, "scripts", "permission_guard.py").replace("'", "'\\''")).encode()


def install(root, data, target):
    """Install and return (state, reason): state is 'binary' or 'launcher'; reason says why the launcher."""
    dest_dir = os.path.join(data, "bin")
    os.makedirs(dest_dir, exist_ok=True)
    dest, stamp = os.path.join(dest_dir, "murmuration"), os.path.join(dest_dir, ".verified")
    reason = doubt(root, target)
    if reason is None:
        src = os.path.join(root, "bin", target, "murmuration")
        sha = digest(src)
        guard_sha = digest(os.path.join(root, "scripts", "permission_guard.py"))
        want_stamp = json.dumps({"binary": sha, "guard": guard_sha, "python": sys.version.split()[0]}, sort_keys=True)
        try:
            current = digest(dest) == sha and open(stamp).read() == want_stamp
        except OSError:
            current = False
        if current:
            return "binary", None
        tmp = "%s.tmp%d" % (dest, os.getpid())
        with open(src, "rb") as fi, open(tmp, "wb") as fo:
            fo.write(fi.read())
        os.chmod(tmp, 0o755)
        bad = self_test(root, tmp)
        if bad is None:
            os.replace(tmp, dest)
            atomic_write(stamp, want_stamp.encode(), 0o644)
            return "binary", None
        os.remove(tmp)
        reason = "the binary's decision differs from permission_guard.py on the self-test payload %s" % bad
    body = launcher_body(root)
    try:
        os.remove(stamp)
    except OSError:
        pass
    try:
        if open(dest, "rb").read() == body:
            return "launcher", reason
    except OSError:
        pass
    atomic_write(dest, body, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    return "launcher", reason


def main():
    root, data = os.environ.get("CLAUDE_PLUGIN_ROOT"), os.environ.get("CLAUDE_PLUGIN_DATA")
    if not root or not data:
        sys.stderr.write("murmuration install: CLAUDE_PLUGIN_ROOT or CLAUDE_PLUGIN_DATA is not set; the permission guard binary is not installed and Bash calls will be blocked\n")
        return 1
    try:
        state, reason = install(root, data, TARGETS.get((platform.system(), platform.machine())))
    except Exception as exc:
        sys.stderr.write("murmuration install: cannot install the permission guard into %s (%s: %s); Bash calls will be blocked until this is fixed\n" % (data, type(exc).__name__, exc))
        return 1
    if state == "launcher":
        note = "murmuration guard: the permission guard runs as the Python script scripts/permission_guard.py, not the Rust binary, because %s. Decisions are the Python guard's." % reason
        sys.stderr.write(note + "\n")
        sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": note}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
