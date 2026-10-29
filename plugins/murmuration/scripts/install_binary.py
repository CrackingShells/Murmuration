#!/usr/bin/env python3
"""SessionStart hook: put the plugin's hook program where the hook rows exec it, `${CLAUDE_PLUGIN_DATA}/bin/murmuration` (subcommands `budget`, `handback`), once per session; the Rust binary only when nothing doubts it.

Python standard library only; hooks.json starts it in exec form (`python3 -S -I install_binary.py`, no shell).
The binary for this platform (`bin/<target>/<binary name>`: macOS or Linux, arm64/aarch64 or x86_64; the name and the target list come from scripts/build_manifest.py; Windows installs are a later cycle) is installed only when all of these hold:
  (a) its sha256 equals the one in `bin/manifest.json`, and the manifest lists every binary that bin/ holds;
  (b) the sha256 of `scripts/budget.py`, `handback.py`, `run_hook.py` and of the Rust sources (computed with scripts/build_manifest.py's rule) equal the manifest's, which binds the binary to the scripts and to the listed Rust sources that are on disk (the hashes do not show how the binary was built: CI building the binary and the manifest from one checkout does);
  (c) a copy of it, run on six budget and hand-back events in a temporary lab (`hook_selftest`), gives the Python scripts' stdout, exit code, log kinds and hand-back file.
On any doubt (and where no binary fits the platform) it installs a launcher that runs `scripts/run_hook.py` instead, and tells the session why: a SessionStart
`additionalContext` line the model sees, and a line on stderr. A previous install is replaced by the launcher in that case. Copies are atomic (temporary file, then rename), so concurrent
sessions installing into one data folder never expose a partial file. A stamp file next to the binary records what was verified; while binary, sources and stamp agree, the self-test is not repeated.
Errors that stop the install itself (a data folder that cannot be written, the plugin variables missing) exit 1 with a message on stderr; the budget and hand-back rows then fail without blocking anything.
"""
import hashlib
import importlib.util
import json
import os
import platform
import stat
import subprocess
import sys

SCRIPTS = ["budget.py", "handback.py", "run_hook.py"]   # as in build_manifest.py
# hosts whose installs are supported; the triples are build_manifest.ALL_TARGETS (Windows stays out until its install path exists: the SessionStart rows exec `python3` and the data path is bin/murmuration)
TARGETS = {("Darwin", "arm64"): "aarch64-apple-darwin", ("Darwin", "x86_64"): "x86_64-apple-darwin",
           ("Linux", "x86_64"): "x86_64-unknown-linux-gnu", ("Linux", "aarch64"): "aarch64-unknown-linux-gnu"}


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_manifest_tool(root):
    spec = importlib.util.spec_from_file_location("build_manifest", os.path.join(root, "scripts", "build_manifest.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sources_doubt(root, tool, manifest):
    """Why the Rust sources on disk are not the ones the manifest records, or None. Names the files; says so when only their line endings differ (a CRLF checkout)."""
    per, combined = tool.sources_hash(root)
    if combined == manifest.get("rust_sources_sha256"):
        return None
    recorded = manifest.get("rust_sources")
    if not isinstance(recorded, dict):
        return "the Rust sources changed since the binaries were built"
    changed = sorted(p for p in set(per) | set(recorded) if per.get(p) != recorded.get(p))
    crlf = bool(changed)
    for p in changed:
        try:
            with open(os.path.join(root, p), "rb") as fh:
                lf = hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()
        except OSError:
            lf = None
        crlf = crlf and lf is not None and lf == recorded.get(p) and per.get(p) != lf
    names = ", ".join(changed[:3]) + (", ..." if len(changed) > 3 else "")
    if crlf:
        return "the Rust sources differ from the build only in their line endings (CRLF: %s); the binaries were built from LF files" % names
    return "the Rust sources changed since the binaries were built (%s)" % (names or "the set of files")


def doubt(root, target):
    """Why the binary may not be installed, or None.

    A stale binary (built from other sources than the ones on disk) is caught in two places. When the manifest still describes the old sources, `sources_doubt` says "changed". When someone regenerated the
    manifest over the new sources without rebuilding (build_manifest.py hashes what it finds), every hash agrees and only `hook_selftest` can see it, by running the binary against the Python
    scripts. CI is what makes that case rare: it builds, then writes the manifest in one job (`--expect-targets`)."""
    if target is None:
        return "no binary is built for this platform (%s %s)" % (platform.system(), platform.machine())
    try:
        with open(os.path.join(root, "bin", "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, ValueError) as exc:
        return "bin/manifest.json cannot be read (%s)" % type(exc).__name__
    if not isinstance(manifest, dict) or not isinstance(manifest.get("binaries"), dict):
        return "bin/manifest.json lists no binaries"
    try:
        tool = load_manifest_tool(root)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:   # SystemExit included: a broken build_manifest.py must end in the launcher, not in a failed hook that blocks every Bash call
        return "scripts/build_manifest.py cannot be loaded (%s)" % type(exc).__name__
    name = tool.binary_name(target)
    src = os.path.join(root, "bin", target, name)
    if os.path.islink(src):
        return "bin/%s/%s is a symlink, not a binary file" % (target, name)
    if not os.path.isfile(src):
        return "bin/%s/%s is missing" % (target, name)
    if target not in manifest["binaries"]:
        return "bin/manifest.json lists no binary for %s" % target
    if digest(src) != manifest["binaries"][target]:
        return "the binary bin/%s/%s does not match its hash in bin/manifest.json" % (target, name)
    try:
        extra = sorted(t for t in tool.present_binaries(root) if t not in manifest["binaries"])
    except OSError as exc:
        return "bin/ cannot be listed (%s)" % type(exc).__name__
    if extra:
        return "bin/ holds a binary for %s that bin/manifest.json does not list" % ", ".join(extra)
    scripts = manifest.get("scripts_sha256")
    if not isinstance(scripts, dict) or sorted(scripts) != sorted(SCRIPTS):
        return "bin/manifest.json does not list the hashes of %s" % ", ".join(SCRIPTS)
    for n in SCRIPTS:
        try:
            if digest(os.path.join(root, "scripts", n)) != scripts[n]:
                return "scripts/%s changed since the binaries were built" % n
        except OSError:
            return "scripts/%s cannot be read" % n
    try:
        return sources_doubt(root, tool, manifest)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:
        return "the Rust sources cannot be hashed (%s)" % type(exc).__name__


def hook_selftest(root, binary):
    """The name of the first budget or handback step on which the binary and the Python scripts (run by this interpreter) differ, or None.

    The same six events run through each in a temporary lab: stdout and exit code are compared at each step, (the lab's path replaced by `<LAB>`), then the kinds of the lines in harness.jsonl and the hand-back file with its time removed."""
    import re
    import tempfile
    brief = "Your name is reproducer-w09-1.\nBudget: USD 1.00\nTime: min 100\nGo.\n"

    def asst(rid, out):
        return json.dumps({"type": "assistant", "requestId": rid, "message": {"id": "m" + rid, "model": "claude-sonnet-5-5", "content": [{"type": "text", "text": "x"}],
                                                                              "usage": {"input_tokens": 2, "output_tokens": out, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}) + "\n"

    def run(cmd, lab, event):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root, LC_ALL="en_US.UTF-8")
        env.pop("CLAUDE_PROJECT_DIR", None)
        p = subprocess.run(cmd, input=json.dumps(dict(event, cwd=lab, transcript_path=lab + "/s.jsonl")).encode(), capture_output=True, timeout=10, env=env)
        return p.returncode, p.stdout.replace(lab.encode(), b"<LAB>"), p.stderr.replace(lab.encode(), b"<LAB>")   # the start note names the lab's absolute path, and each program runs in its own temporary lab

    results = []
    for who in ("python", "binary"):
        with tempfile.TemporaryDirectory() as lab:
            lab = os.path.realpath(lab)
            os.makedirs(lab + "/__statera__")
            os.makedirs(lab + "/s/subagents")
            tx = lab + "/s/subagents/agent-a1.jsonl"
            ev = dict(agent_id="a1", agent_type="murmuration:reproducer", permission_mode="default")
            steps = [("budget", dict(hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu1", tool_input=dict(subagent_type="murmuration:reproducer", prompt=brief, name="reproducer-w09-1")), None),
                     ("budget", dict(ev, hook_event_name="SubagentStart"), None),
                     ("budget", dict(ev, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), json.dumps({"type": "user", "message": {"role": "user", "content": brief}}) + "\n" + asst("r1", 60000)),
                     ("budget", dict(ev, hook_event_name="PostToolUse", tool_name="Bash"), json.dumps({"type": "user", "message": {"role": "user", "content": brief}}) + "\n" + asst("r1", 160000)),
                     ("handback", dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id="e1", agent_type="murmuration:explorer", tool_input={"message": "m"}), None),
                     ("handback", dict(ev, hook_event_name="SubagentStop", last_assistant_message="self-test hand-back", agent_transcript_path=tx), None)]
            out = []
            for n, (which, event, transcript) in enumerate(steps):
                if transcript is not None:
                    with open(tx, "w", encoding="utf-8") as fh:
                        fh.write(transcript)
                cmd = [sys.executable, "-S", "-I", os.path.join(root, "scripts", "run_hook.py"), which] if who == "python" else [binary, which]
                try:
                    out.append(run(cmd, lab, event))
                except (OSError, subprocess.SubprocessError) as exc:
                    return "step %d (%s: %s)" % (n + 1, which, type(exc).__name__)
            try:
                log = [json.loads(x)["event"] for x in open(lab + "/__statera__/harness.jsonl", encoding="utf-8")]
                shake = [re.sub(rb"\| \d{4}-[0-9T:+-]+ \|", b"|T|", open(os.path.join(dp, f), "rb").read()) for dp, _, fs in os.walk(lab + "/__statera__/handbacks") for f in fs]
            except (OSError, ValueError, KeyError, TypeError):
                log, shake = None, None   # a program that wrote nothing, or something that is not a record, differs from the Python scripts
            results.append((out, log, shake))
    for n, (a, b) in enumerate(zip(*[r[0] for r in results])):
        if a != b:
            return "step %d" % (n + 1)
    if results[0][1] != results[1][1] or results[0][2] != results[1][2]:
        return "the records written"
    return None


def atomic_write(dest, data, mode):
    tmp = "%s.tmp%d" % (dest, os.getpid())
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.chmod(tmp, mode)
    os.replace(tmp, dest)


def launcher_body(root):
    """What runs where the binary is not installed: run_hook.py, with the subcommand (`budget` or `handback`)."""
    return ("#!/bin/sh\nexec python3 -S -I '%s' \"$1\"\n" % os.path.join(root, "scripts", "run_hook.py").replace("'", "'\\''")).encode()


def install(root, data, target):
    """Install and return (state, reason): state is 'binary' or 'launcher'; reason says why the launcher."""
    dest_dir = os.path.join(data, "bin")
    os.makedirs(dest_dir, exist_ok=True)
    dest, stamp = os.path.join(dest_dir, "murmuration"), os.path.join(dest_dir, ".verified")
    reason = doubt(root, target)
    if reason is None:
        src = os.path.join(root, "bin", target, load_manifest_tool(root).binary_name(target))
        sha = digest(src)
        want_stamp = json.dumps({"binary": sha, "scripts": {n: digest(os.path.join(root, "scripts", n)) for n in SCRIPTS}, "python": sys.version.split()[0]}, sort_keys=True)
        try:
            current = digest(dest) == sha and open(stamp, encoding="utf-8").read() == want_stamp
        except OSError:
            current = False
        if current:
            return "binary", None
        tmp = "%s.tmp%d" % (dest, os.getpid())
        with open(src, "rb") as fi, open(tmp, "wb") as fo:
            fo.write(fi.read())
        os.chmod(tmp, 0o755)
        bad = hook_selftest(root, tmp)
        if bad is None:
            os.replace(tmp, dest)
            atomic_write(stamp, want_stamp.encode(), 0o644)
            return "binary", None
        os.remove(tmp)
        reason = "the binary's `budget/handback` differs from the Python script on the self-test (%s)" % bad
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


def selftest():
    """The mutations below are each caught by doubt() or by the self-tests, and install() then ends in the launcher.

    What this shows is limited: the hashes bind a binary to the listed sources, and behaviour is checked only on the six hook events. A binary that is wrong on other inputs, or a
    manifest regenerated over new sources around a stale binary that agrees on those events, passes; the protection against that is CI building the binary and the manifest from one checkout.

    Works on temporary copies of this plugin's scripts and Rust sources, for a fixed Linux target whatever the host is. The "binary" is a shell script that runs the Python scripts, so it behaves
    exactly like them; a mutation then makes it, or what it is checked against, wrong. A positive control (the unmutated copy installs the binary) comes first, so a mutation cannot pass by failing
    for an unrelated reason. Every mutation must give its own reason."""
    import shutil
    import tempfile
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = "x86_64-unknown-linux-gnu"
    other = "aarch64-unknown-linux-gnu"
    assert ("Windows", "AMD64") not in TARGETS and not any(k[0] == "Windows" for k in TARGETS)
    assert TARGETS[("Linux", "x86_64")] == target and TARGETS[("Linux", "aarch64")] == other
    assert sorted(TARGETS.values()) == sorted(t for t in load_manifest_tool(here).ALL_TARGETS if "windows" not in t)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = os.path.realpath(tmp)
        base = os.path.join(tmp, "base")
        shutil.copytree(os.path.join(here, "scripts"), os.path.join(base, "scripts"), ignore=shutil.ignore_patterns("__pycache__", "git-hooks", "fixtures"))
        for rel in ["rust/Cargo.toml", "rust/Cargo.lock", "rust/gen_tables.py"] + ["rust/src/" + n for n in sorted(os.listdir(os.path.join(here, "rust", "src"))) if n.endswith(".rs")]:
            os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
            shutil.copy(os.path.join(here, rel), os.path.join(base, rel))
        budget_rs = os.path.join("rust", "src", "budget.rs")
        assert b"\n" in open(os.path.join(base, budget_rs), "rb").read()

        def write(path, data, mode=0o755):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            os.chmod(path, mode)

        def manifest(root):
            tool = load_manifest_tool(root)
            code, _, err = tool.write_manifest(root)
            assert code == 0, err

        def good(root, tgt=target):
            write(os.path.join(root, "bin", tgt, "murmuration"), launcher_body(root) + b"# stands in for the binary\n")   # not the launcher's bytes: an install that replaces it by the launcher shows

        def fresh(name, setup=None):
            """A copy of base with the good binary and its manifest; `setup` mutates it before or after the manifest is written."""
            root = os.path.join(tmp, name)
            shutil.copytree(base, root)
            good(root)
            manifest(root)
            return root

        # positive control: nothing doubts it, and install() puts the binary in place
        root = fresh("control")
        assert doubt(root, target) is None, doubt(root, target)
        state, reason = install(root, os.path.join(tmp, "control-data"), target)
        assert (state, reason) == ("binary", None), (state, reason)
        assert open(os.path.join(tmp, "control-data", "bin", "murmuration"), "rb").read() == launcher_body(root) + b"# stands in for the binary\n"
        assert doubt(root, None).startswith("no binary is built for this platform")

        def flip(path):
            data = bytearray(open(path, "rb").read())
            data[len(data) // 2] ^= 0x01
            write(path, bytes(data))

        def m_sources(root):
            flip(os.path.join(root, budget_rs))

        def m_binary(root):
            flip(os.path.join(root, "bin", target, "murmuration"))

        def m_entry(root):
            path = os.path.join(root, "bin", "manifest.json")
            m = json.load(open(path, encoding="utf-8"))
            del m["binaries"][target]
            write(path, json.dumps(m).encode(), 0o644)

        def m_crlf(root):
            path = os.path.join(root, budget_rs)
            write(path, open(path, "rb").read().replace(b"\n", b"\r\n"))

        def m_extra(root):   # a binary under a target the manifest does not list
            good(root, other)

        def m_missing(root):
            os.remove(os.path.join(root, "bin", target, "murmuration"))

        def m_stale_old_manifest(root):   # a binary rebuilt from other sources, the manifest still describing the old ones
            write(os.path.join(root, "bin", target, "murmuration"), b"#!/bin/sh\nexit 0\n")

        def m_stale_new_manifest(root):   # manifest regenerated over the new sources, binary not rebuilt: every hash agrees, only the self-test can tell
            write(os.path.join(root, "bin", target, "murmuration"), b"#!/bin/sh\nexit 0\n")
            manifest(root)

        def m_symlink(root):
            path = os.path.join(root, "bin", target, "murmuration")
            os.rename(path, path + ".real")
            os.symlink(path + ".real", path)

        def m_loader_exits(root):   # the manifest tool exits instead of raising
            write(os.path.join(root, "scripts", "build_manifest.py"), b"raise SystemExit(3)\n", 0o644)

        def m_new(rel):
            def mutate(root):
                write(os.path.join(root, rel), b"// added\n", 0o644)
            return mutate

        cases = [("sources", m_sources, "Rust sources changed since the binaries were built (rust/src/budget.rs)"),
                 ("binary", m_binary, "does not match its hash"),
                 ("entry", m_entry, "lists no binary for " + target),
                 ("crlf", m_crlf, "only in their line endings (CRLF: rust/src/budget.rs)"),
                 ("extra", m_extra, "bin/ holds a binary for %s that bin/manifest.json does not list" % other),
                 ("missing", m_missing, "is missing"),
                 ("stale_old", m_stale_old_manifest, "does not match its hash"),
                 ("stale_new", m_stale_new_manifest, "the binary's `budget/handback` differs from the Python script on the self-test"),
                 ("symlink", m_symlink, "is a symlink"),
                 ("loader_exits", m_loader_exits, "scripts/build_manifest.py cannot be loaded (SystemExit)"),
                 ("build_rs", m_new("rust/build.rs"), "Rust sources changed since the binaries were built (rust/build.rs)"),
                 ("cargo_config", m_new("rust/.cargo/config.toml"), "Rust sources changed since the binaries were built (rust/.cargo/config.toml)"),
                 ("nested_module", m_new("rust/src/sub/mod.rs"), "Rust sources changed since the binaries were built (rust/src/sub/mod.rs)")]
        reasons = {}
        for name, mutate, want in cases:
            root = fresh(name)
            data = os.path.join(tmp, name + "-data")
            if name in ("sources", "stale_new"):   # a good install first: the mutation must replace it (each install runs both self-tests, so not for every case)
                assert install(root, data, target) == ("binary", None), name
            mutate(root)
            state, reason = install(root, data, target)
            assert state == "launcher" and reason is not None and want in reason, (name, state, reason)
            assert open(os.path.join(data, "bin", "murmuration"), "rb").read() == launcher_body(root) and not os.path.exists(os.path.join(data, "bin", ".verified")), name
            if name.startswith("stale"):
                d = doubt(root, target)
                assert (d is None) == (name == "stale_new"), (name, d)   # the old manifest is caught by a hash; the regenerated one only by the self-tests
            reasons[name] = reason
        assert len(set(reasons[n] for n in ("sources", "binary", "entry", "crlf", "extra", "missing", "stale_new", "symlink", "loader_exits", "build_rs"))) == 10, reasons   # each its own reason
        # strays are not sources: a .DS_Store, a local rust/target/ and a file that is not .rs leave the control tree trusted
        for rel in ("rust/.DS_Store", "rust/src/.DS_Store", "rust/target/release/x.rs", "rust/src/notes.txt"):
            write(os.path.join(os.path.join(tmp, "control"), rel), b"stray", 0o644)
        assert doubt(os.path.join(tmp, "control"), target) is None
    print("selftest install_binary: ok (%d mutations)" % len(cases))
    return 0


def _utf8_stdio():
    """Hook JSON and reports are UTF-8 on every OS, whatever the locale: `python -I` ignores PYTHONUTF8 and PYTHONIOENCODING, and a Windows pipe is otherwise read and written in the ANSI code page."""
    for stream, extra in ((sys.stdin, {}), (sys.stdout, {"newline": "\n"}), (sys.stderr, {"newline": "\n"})):
        try:
            stream.reconfigure(encoding="utf-8", **extra)
        except (AttributeError, ValueError, OSError):
            pass


def main():
    _utf8_stdio()
    if "--selftest" in sys.argv[1:]:
        return selftest()
    root, data = os.environ.get("CLAUDE_PLUGIN_ROOT"), os.environ.get("CLAUDE_PLUGIN_DATA")
    if not root or not data:
        sys.stderr.write("murmuration install: CLAUDE_PLUGIN_ROOT or CLAUDE_PLUGIN_DATA is not set; the hook binary is not installed and the budget and hand-back hooks will fail\n")
        return 1
    try:
        state, reason = install(root, data, TARGETS.get((platform.system(), platform.machine())))
    except Exception as exc:
        sys.stderr.write("murmuration install: cannot install the hook binary into %s (%s: %s); the budget and hand-back hooks will fail until this is fixed\n" % (data, type(exc).__name__, exc))
        return 1
    if state == "launcher":
        note = "murmuration: the plugin's budget and hand-back hooks run as the Python scripts, not the Rust binary, because %s. Decisions are the Python scripts'. The binary comes from CI (the `build(bin)` commit of the plugin's repository); until a release carries one that matches these files, the Python scripts decide, which is correct and slower." % reason
        sys.stderr.write(note + "\n")
        sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": note}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
