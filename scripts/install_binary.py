#!/usr/bin/env python3
"""SessionStart hook: put the permission guard where the guard rows exec it, `${CLAUDE_PLUGIN_DATA}/bin/murmuration`, once per session.

Python standard library only; hooks.json starts it in exec form (`python3 -S -I install_binary.py`, no shell).
  - A binary for this platform exists in `${CLAUDE_PLUGIN_ROOT}/bin/<target>/murmuration`: copy it to the data folder when the target is absent or differs (sha256), atomically, mode 755.
  - No binary fits this platform (not macOS arm64 or x86_64): write a launcher there that runs `scripts/permission_guard.py` with the same arguments the rows pass, so the rows still decide.
  - The data folder cannot be written, or the plugin variables are missing: say so on stderr and exit 1, so the session shows it. The guard rows then block Bash calls (onFailure block), which is the fail-closed answer.
Prints nothing on success.
"""
import hashlib
import os
import platform
import stat
import sys

TARGETS = {("Darwin", "arm64"): "aarch64-apple-darwin", ("Darwin", "x86_64"): "x86_64-apple-darwin"}


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def install(root, data, target):
    dest_dir = os.path.join(data, "bin")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "murmuration")
    src = os.path.join(root, "bin", target, "murmuration") if target else None
    if src and os.path.isfile(src):
        if os.path.isfile(dest) and digest(dest) == digest(src):
            return "current"
        tmp = "%s.tmp%d" % (dest, os.getpid())
        with open(src, "rb") as fi, open(tmp, "wb") as fo:
            fo.write(fi.read())
        os.chmod(tmp, 0o755)
        os.replace(tmp, dest)
        return "copied"
    body = "#!/bin/sh\nexec python3 -S -I '%s' \"$@\"\n" % os.path.join(root, "scripts", "permission_guard.py").replace("'", "'\\''")
    if os.path.isfile(dest) and open(dest, "rb").read() == body.encode():
        return "launcher current"
    tmp = "%s.tmp%d" % (dest, os.getpid())
    with open(tmp, "w") as fh:
        fh.write(body)
    os.chmod(tmp, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    os.replace(tmp, dest)
    return "launcher written"


def main():
    root, data = os.environ.get("CLAUDE_PLUGIN_ROOT"), os.environ.get("CLAUDE_PLUGIN_DATA")
    if not root or not data:
        sys.stderr.write("murmuration install: CLAUDE_PLUGIN_ROOT or CLAUDE_PLUGIN_DATA is not set; the permission guard binary is not installed and Bash calls will be blocked\n")
        return 1
    try:
        install(root, data, TARGETS.get((platform.system(), platform.machine())))
    except Exception as exc:
        sys.stderr.write("murmuration install: cannot install the permission guard into %s (%s: %s); Bash calls will be blocked until this is fixed\n" % (data, type(exc).__name__, exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
