#!/usr/bin/env python3
"""The target and binary-name contract, and the writer of bin/manifest.json: what the committed guard binaries were built from.

Python standard library only. CI builds one binary per target in ALL_TARGETS, copies it to bin/<target>/<binary_name(target)> and writes the manifest; nothing else writes bin/.

    python3 -I scripts/build_manifest.py [--root DIR] [--expect-targets t1,t2,...]   write bin/manifest.json
    python3 -I scripts/build_manifest.py binary-name <target>                         print murmuration.exe for a Windows triple, murmuration otherwise
    python3 -I scripts/build_manifest.py [--root DIR] sources-hash                    print rust_sources_sha256 (the combined hash of the Rust sources)
    python3 -I scripts/build_manifest.py --selftest

With --expect-targets the manifest is written only when the set of targets that have a binary under bin/<target>/<binary_name(target)> equals the list exactly (a missing or an extra target
exits 1 with a message on stderr and leaves the manifest as it was). Without it the manifest is written for whatever bin/ holds. Either way it refuses (exit 1, manifest untouched) a bin/ that holds anything CI
does not put there: a folder that is not in ALL_TARGETS, a file in bin/<t>/ that is not binary_name(t) (`murmuration` in the Windows folder, `.exe` in a Unix one), a binary that is a symlink.

The manifest holds the sha256 of each bin/<target>/<binary_name(target)>, the sha256 of scripts/permission_guard.py, budget.py, handback.py and run_hook.py (`scripts_sha256`), the sha256 of each Rust
source file (the allowlist in RUST_FILES, rust/.cargo/** and rust/src/**/*.rs) and one hash over those (`rust_sources_sha256`). scripts/install_binary.py installs a binary only when all of them still match the
tree it runs in. `sources_hash()`, `binary_name()` and `host_target()` are what the installer and scripts/check_guard_equal.py import, so every side uses one definition.
"""
import argparse
import hashlib
import json
import os
import platform
import sys

# every input that shapes the binary, as an allowlist (never "everything under rust/": a .DS_Store or a local rust/target/ must not change the hash): these files when present, rust/.cargo/**, rust/src/**/*.rs.
# The crate has no include_str!/include_bytes!; add the file here if it gains one. Keys are paths relative to the plugin root with "/" on every OS, so the hash is the same on the Windows runner.
RUST_FILES = ["rust/Cargo.toml", "rust/Cargo.lock", "rust/gen_tables.py", "rust/build.rs", "rust/rust-toolchain", "rust/rust-toolchain.toml"]
# the Python scripts the binary stands in for, and the fall-back that runs when it does not: an edit to any of them after the build makes the installer put the launcher in place
SCRIPTS = ["permission_guard.py", "budget.py", "handback.py", "run_hook.py"]
# the triples CI builds. Not all of them are installable: install_binary.TARGETS lists the hosts whose installs are supported (Windows is a later cycle).
ALL_TARGETS = ["aarch64-apple-darwin", "x86_64-apple-darwin", "x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu", "x86_64-pc-windows-msvc"]
HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.abspath(os.path.join(HERE, ".."))


def binary_name(target):
    """The file name of the binary built for `target`."""
    return "murmuration.exe" if "windows" in target else "murmuration"


def host_target():
    """The triple of the machine this runs on, or None where no binary is built."""
    system, machine = platform.system(), platform.machine().lower()
    arch = {"x86_64": "x86_64", "amd64": "x86_64", "arm64": "aarch64", "aarch64": "aarch64"}.get(machine)
    triple = {"Darwin": "%s-apple-darwin", "Linux": "%s-unknown-linux-gnu", "Windows": "%s-pc-windows-msvc"}.get(system)
    t = triple % arch if triple and arch else None
    return t if t in ALL_TARGETS else None


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rust_source_paths(root):
    """Sorted, "/"-separated paths (relative to root) of the files whose bytes the binary depends on; an optional file that is absent is simply not listed."""
    found = [p for p in RUST_FILES if os.path.isfile(os.path.join(root, p))]
    for sub, keep in (("rust/.cargo", lambda n: n != ".DS_Store"), ("rust/src", lambda n: n.endswith(".rs"))):
        for dirpath, _, names in os.walk(os.path.join(root, *sub.split("/"))):
            rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
            found += ["%s/%s" % (rel, n) for n in names if keep(n)]
    return sorted(found)


def sources_hash(root):
    """(per-file hashes, one combined hash) of the Rust sources under root."""
    per = {p: sha256_file(os.path.join(root, p)) for p in rust_source_paths(root)}
    combined = hashlib.sha256("".join("%s\0%s\n" % (p, h) for p, h in sorted(per.items())).encode()).hexdigest()
    return per, combined


def present_binaries(root):
    """{target: sha256} of every bin/<folder>/<binary_name(folder)> that is a file. Files directly under bin/ (the manifest) are not binaries; see bin_problems for what must not be there."""
    bindir = os.path.join(root, "bin")
    found = {}
    for target in sorted(os.listdir(bindir)) if os.path.isdir(bindir) else []:
        p = os.path.join(bindir, target, binary_name(target))
        if os.path.isfile(p):
            found[target] = sha256_file(p)
    return found


def bin_problems(root):
    """What bin/ holds that CI never puts there: a folder that is not in ALL_TARGETS, a file or folder in bin/<t>/ other than binary_name(t) (.DS_Store aside), a binary that is a symlink."""
    bindir = os.path.join(root, "bin")
    problems = []
    for entry in sorted(os.listdir(bindir)) if os.path.isdir(bindir) else []:
        folder = os.path.join(bindir, entry)
        if not os.path.isdir(folder) or os.path.islink(folder):
            continue   # bin/manifest.json
        if entry not in ALL_TARGETS:
            problems.append("bin/%s is not a target CI builds (%s)" % (entry, ", ".join(ALL_TARGETS)))
            continue
        for name in sorted(os.listdir(folder)):
            if name == ".DS_Store":
                continue
            if name != binary_name(entry):
                problems.append("bin/%s/%s is not the binary of that target (expected %s)" % (entry, name, binary_name(entry)))
            elif os.path.islink(os.path.join(folder, name)) or not os.path.isfile(os.path.join(folder, name)):
                problems.append("bin/%s/%s is not a regular file" % (entry, name))
    return problems


def build(root):
    binaries = present_binaries(root)
    per, combined = sources_hash(root)
    return {"format": 2, "binaries": binaries, "permission_guard_py_sha256": sha256_file(os.path.join(root, "scripts", "permission_guard.py")),
            "scripts_sha256": {n: sha256_file(os.path.join(root, "scripts", n)) for n in SCRIPTS},
            "rust_sources": per, "rust_sources_sha256": combined}


def write_manifest(root, expect=None):
    """Write bin/manifest.json and return (exit code, stdout line, stderr line). With `expect` (a collection of triples) nothing is written unless the targets present equal it."""
    problems = bin_problems(root)
    if problems:
        return 1, "", "build_manifest: manifest not written: unexpected content in bin/: " + "; ".join(problems)
    m = build(root)
    if expect is not None:
        want, have = set(expect), set(m["binaries"])
        if want != have:
            parts = []
            if want - have:
                parts.append("no binary for %s (expected bin/<target>/<binary name>)" % ", ".join("%s (bin/%s/%s)" % (t, t, binary_name(t)) for t in sorted(want - have)))
            if have - want:
                parts.append("binaries for %s were not expected" % ", ".join(sorted(have - want)))
            return 1, "", "build_manifest: manifest not written: " + "; ".join(parts)
    dest = os.path.join(root, "bin", "manifest.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = "%s.tmp%d" % (dest, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, dest)
    return 0, "bin/manifest.json: %d binaries, %d rust sources" % (len(m["binaries"]), len(m["rust_sources"])), ""


def _utf8_stdio():
    """Hook JSON and reports are UTF-8 on every OS, whatever the locale: `python -I` ignores PYTHONUTF8 and PYTHONIOENCODING, and a Windows pipe is otherwise read and written in the ANSI code page."""
    for stream, extra in ((sys.stdin, {}), (sys.stdout, {"newline": "\n"}), (sys.stderr, {"newline": "\n"})):
        try:
            stream.reconfigure(encoding="utf-8", **extra)
        except (AttributeError, ValueError, OSError):
            pass


def main(argv=None):
    _utf8_stdio()
    ap = argparse.ArgumentParser(prog="build_manifest.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", nargs="*", metavar="binary-name TARGET | sources-hash", help="a subcommand; none writes the manifest")
    ap.add_argument("--root", default=PLUGIN_ROOT, help="the plugin tree (default: the one this script is in)")
    ap.add_argument("--expect-targets", default=None, metavar="t1,t2,...", help="write only when exactly these targets have a binary under bin/")
    ap.add_argument("--selftest", action="store_true", help="check this script on a temporary tree")
    a = ap.parse_intermixed_args(argv)
    if a.selftest:
        return selftest()
    cmd = a.command
    if cmd[:1] == ["binary-name"]:
        if len(cmd) != 2 or not cmd[1]:
            ap.error("binary-name takes one target")
        print(binary_name(cmd[1]))
        return 0
    if cmd[:1] == ["sources-hash"]:
        if len(cmd) != 1:
            ap.error("sources-hash takes no argument")
        print(sources_hash(a.root)[1])
        return 0
    if cmd:
        ap.error("unknown command %r" % " ".join(cmd))
    expect = None if a.expect_targets is None else [t.strip() for t in a.expect_targets.split(",") if t.strip()]
    code, out, err = write_manifest(a.root, expect)
    if err:
        sys.stderr.write(err + "\n")
    if out:
        print(out)
    return code


def selftest():
    import contextlib
    import io
    import shutil
    import tempfile
    from unittest import mock

    def cli(*argv):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            try:
                code = main(list(argv))
            except SystemExit as exc:   # argparse's usage errors
                code = exc.code
        return code, o.getvalue(), e.getvalue()

    # the names
    assert binary_name("x86_64-pc-windows-msvc") == "murmuration.exe"
    assert all(binary_name(t) == "murmuration" for t in ALL_TARGETS if "windows" not in t) and len(ALL_TARGETS) == 5
    assert cli("binary-name", "x86_64-pc-windows-msvc") == (0, "murmuration.exe\n", "")
    assert cli("binary-name", "aarch64-unknown-linux-gnu") == (0, "murmuration\n", "")
    assert cli("binary-name")[0] == 2 and cli("nonsense")[0] == 2
    # the host
    for (system, machine), want in {("Darwin", "arm64"): "aarch64-apple-darwin", ("Darwin", "x86_64"): "x86_64-apple-darwin", ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
                                    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu", ("Windows", "AMD64"): "x86_64-pc-windows-msvc", ("Windows", "ARM64"): None,
                                    ("Linux", "riscv64"): None, ("FreeBSD", "amd64"): None}.items():
        with mock.patch("platform.system", return_value=system), mock.patch("platform.machine", return_value=machine):
            assert host_target() == want, (system, machine, host_target())
    # a temporary tree
    with tempfile.TemporaryDirectory() as root:
        def put(rel, data):
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(data)
        for n in SCRIPTS:
            put("scripts/" + n, n.encode())
        for p in RUST_FILES[:3] + ["rust/src/main.rs", "rust/src/guard.rs"]:
            put(p, p.encode())
        put("rust/src/notes.txt", b"not hashed")
        put("bin/aarch64-apple-darwin/murmuration", b"mac")
        put("bin/x86_64-pc-windows-msvc/murmuration.exe", b"win")
        manifest = os.path.join(root, "bin", "manifest.json")
        assert sorted(present_binaries(root)) == ["aarch64-apple-darwin", "x86_64-pc-windows-msvc"] and bin_problems(root) == []
        # anything CI does not put in bin/ is refused, bare or with --expect-targets, and the manifest stays absent
        for rel, why in (("bin/x86_64-unknown-linux-gnu/murmuration.exe", ".exe in a Unix folder"), ("bin/x86_64-pc-windows-msvc/murmuration", "no .exe in the Windows folder"),
                         ("bin/stray/readme.txt", "a folder that is no target"), ("bin/aarch64-apple-darwin/notes.txt", "a stray file")):
            put(rel, b"x")
            for argv in (["--root", root], ["--root", root, "--expect-targets", "aarch64-apple-darwin,x86_64-pc-windows-msvc"]):
                code, out, err = cli(*argv)
                assert code == 1 and "unexpected content in bin/" in err and rel.split("/")[1] in err and not os.path.exists(manifest), (why, code, err)
            os.remove(os.path.join(root, rel))
        shutil.rmtree(os.path.join(root, "bin", "stray"))
        put("bin/aarch64-apple-darwin/.DS_Store", b"x")   # tolerated
        link = os.path.join(root, "bin", "x86_64-unknown-linux-gnu")
        os.makedirs(link, exist_ok=True)
        os.symlink(os.path.join(root, "bin", "aarch64-apple-darwin", "murmuration"), os.path.join(link, "murmuration"))
        code, out, err = cli("--root", root)
        assert code == 1 and "bin/x86_64-unknown-linux-gnu/murmuration is not a regular file" in err and not os.path.exists(manifest), (code, err)
        shutil.rmtree(link)
        assert bin_problems(root) == []
        # the exact-target check: refused cases leave the manifest as it was (absent, then the earlier one)
        for expect in ("aarch64-apple-darwin", "aarch64-apple-darwin,x86_64-pc-windows-msvc,x86_64-unknown-linux-gnu", "aarch64-apple-darwin,x86_64-apple-darwin", ""):
            code, out, err = cli("--root", root, "--expect-targets", expect)
            assert code == 1 and out == "" and err.startswith("build_manifest: manifest not written") and not os.path.exists(manifest), (expect, code, err)
        code, out, err = cli("--expect-targets", "x86_64-pc-windows-msvc,aarch64-apple-darwin", "--root", root)   # order of the arguments and of the list is free
        assert code == 0 and err == "" and os.path.isfile(manifest), (code, err)
        m = json.load(open(manifest, encoding="utf-8"))
        assert sorted(m["binaries"]) == ["aarch64-apple-darwin", "x86_64-pc-windows-msvc"] and m["binaries"]["x86_64-pc-windows-msvc"] == hashlib.sha256(b"win").hexdigest()
        assert sorted(m["rust_sources"]) == sorted(RUST_FILES[:3] + ["rust/src/main.rs", "rust/src/guard.rs"]) and sorted(m["scripts_sha256"]) == sorted(SCRIPTS)
        before = open(manifest, "rb").read()
        put("bin/x86_64-apple-darwin/murmuration", b"intel")
        code, out, err = cli("--root", root, "--expect-targets", "aarch64-apple-darwin,x86_64-pc-windows-msvc")
        assert code == 1 and "x86_64-apple-darwin" in err and open(manifest, "rb").read() == before, (code, err)
        # the bare call writes whatever bin/ holds; sources-hash agrees with what it wrote
        assert cli("--root", root)[0] == 0
        m = json.load(open(manifest, encoding="utf-8"))
        assert sorted(m["binaries"]) == ["aarch64-apple-darwin", "x86_64-apple-darwin", "x86_64-pc-windows-msvc"]
        assert cli("--root", root, "sources-hash") == (0, m["rust_sources_sha256"] + "\n", "") and cli("sources-hash", "--root", root)[1] == m["rust_sources_sha256"] + "\n"
        put("rust/src/main.rs", b"changed")
        assert cli("--root", root, "sources-hash")[1] != m["rust_sources_sha256"] + "\n"
        # the source set: the allowlist, recursively, with "/" keys; strays do not count
        keys = rust_source_paths(root)
        assert keys == sorted(keys) and "\\" not in "".join(keys)
        base_hash = sources_hash(root)[1]
        for rel in ("rust/.DS_Store", "rust/src/.DS_Store", "rust/target/release/x.rs", "rust/src/notes.txt", "rust/.cargo/.DS_Store", "rust/tests/t.rs"):
            put(rel, b"stray")
            assert sources_hash(root)[1] == base_hash, rel
        for rel in ("rust/build.rs", "rust/rust-toolchain", "rust/rust-toolchain.toml", "rust/.cargo/config.toml", "rust/.cargo/sub/x.toml", "rust/src/sub/mod.rs", "rust/src/bin/x.rs"):
            put(rel, b"new")
            h = sources_hash(root)[1]
            assert h != base_hash and rel in rust_source_paths(root), rel
            os.remove(os.path.join(root, rel))
            assert sources_hash(root)[1] == base_hash, (rel, rust_source_paths(root), keys)   # an optional file that comes and goes leaves no trace
        os.remove(os.path.join(root, "bin", "manifest.json"))
        os.rename(os.path.join(root, "bin"), os.path.join(root, "bin-away"))   # no bin/ at all: an empty list matches
        assert cli("--root", root, "--expect-targets", "x86_64-apple-darwin")[0] == 1 and cli("--root", root, "--expect-targets", "")[0] == 0
    print("selftest build_manifest: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
