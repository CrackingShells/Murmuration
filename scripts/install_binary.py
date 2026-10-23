#!/usr/bin/env python3
"""SessionStart hook: put the plugin's hook program where the hook rows exec it, `${CLAUDE_PLUGIN_DATA}/bin/murmuration` (subcommands `guard`, `budget`, `handback`), once per session; the Rust binary only when nothing doubts it.

Python standard library only; hooks.json starts it in exec form (`python3 -S -I install_binary.py`, no shell).
The binary for this platform (`bin/<target>/murmuration`, macOS arm64 or x86_64) is installed only when all of these hold:
  (a) its sha256 equals the one in `bin/manifest.json`;
  (b) the sha256 of `scripts/permission_guard.py`, `budget.py`, `handback.py`, `run_hook.py` and of the Rust sources (computed with scripts/build_manifest.py's rule) equal the manifest's, so the binary was built from the rules that are on disk;
  (c) a copy of it, run on the fixed payloads of `scripts/guard_selftest_payloads.json`, gives the same exit code and stdout as `permission_guard.py` run by this interpreter on each of them, and run on six budget and
      hand-back events in a temporary lab (`hook_selftest`) it gives the Python scripts' stdout, exit code, log kinds and hand-back file.
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

SCRIPTS = ["permission_guard.py", "budget.py", "handback.py", "run_hook.py"]   # as in build_manifest.py
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
    scripts = manifest.get("scripts_sha256")
    if not isinstance(scripts, dict) or sorted(scripts) != sorted(SCRIPTS):
        return "bin/manifest.json does not list the hashes of %s" % ", ".join(SCRIPTS)
    for name in SCRIPTS:
        try:
            if digest(os.path.join(root, "scripts", name)) != scripts[name]:
                return "scripts/%s changed since the binaries were built" % name
        except OSError:
            return "scripts/%s cannot be read" % name
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


def hook_selftest(root, binary):
    """The name of the first budget or handback step on which the binary and the Python scripts (run by this interpreter) differ, or None.

    The same six events run through each in a temporary lab: stdout and exit code are compared at each step, then the kinds of the lines in harness.jsonl and the hand-back file with its time removed."""
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
        return p.returncode, p.stdout, p.stderr

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
                    with open(tx, "w") as fh:
                        fh.write(transcript)
                cmd = [sys.executable, "-S", "-I", os.path.join(root, "scripts", "run_hook.py"), which] if who == "python" else [binary, which]
                try:
                    out.append(run(cmd, lab, event))
                except (OSError, subprocess.SubprocessError) as exc:
                    return "step %d (%s: %s)" % (n + 1, which, type(exc).__name__)
            try:
                log = [json.loads(x)["event"] for x in open(lab + "/__statera__/harness.jsonl")]
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
    """What runs where the binary is not installed: `budget` and `handback` start run_hook.py, anything else (`guard`) starts permission_guard.py."""
    q = lambda name: os.path.join(root, "scripts", name).replace("'", "'\\''")
    return ("#!/bin/sh\ncase \"$1\" in\nbudget|handback) exec python3 -S -I '%s' \"$1\" ;;\n*) exec python3 -S -I '%s' \"$@\" ;;\nesac\n" % (q("run_hook.py"), q("permission_guard.py"))).encode()


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
        want_stamp = json.dumps({"binary": sha, "guard": guard_sha, "scripts": {n: digest(os.path.join(root, "scripts", n)) for n in SCRIPTS}, "python": sys.version.split()[0]}, sort_keys=True)
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
            bad_hook = hook_selftest(root, tmp)
            bad = None if bad_hook is None else "budget/handback " + bad_hook
        if bad is None:
            os.replace(tmp, dest)
            atomic_write(stamp, want_stamp.encode(), 0o644)
            return "binary", None
        os.remove(tmp)
        reason = ("the binary's decision differs from the Python script on the self-test payload %s" % bad) if not bad.startswith("budget/handback") else ("the binary's `%s` differs from the Python script on the self-test (%s)" % tuple(bad.split(" ", 1)))
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
        note = "murmuration guard: the plugin's hooks (permission guard, budget, hand-back) run as the Python scripts, not the Rust binary, because %s. Decisions are the Python scripts'. To get the binary back, rebuild it with the pre-commit hook or `cargo build --release --offline` followed by `python3 scripts/build_manifest.py`, or reinstall the plugin; until then the Python scripts decide, which is correct and slower." % reason
        sys.stderr.write(note + "\n")
        sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": note}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
