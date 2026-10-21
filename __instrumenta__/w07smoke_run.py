# w07 combined smoke: runs one headless `claude -p` session (haiku agent files in an export of branch HEAD) in a fresh scratch git+lab folder under /private/tmp/murmuration-w07/reproducer-w07-7/runs/<name>/; inputs: scenario (pi_terminal, guard_inherited) and optional permission mode; outputs: <run>/{stream.jsonl,stderr.txt,dbg.log,guard.log,run.meta.json,lab/}; a stub program (logs its argv to stub.log) is first on PATH. pi_terminal drops the platform's session environment variables (a terminal-like launch, as w07c5_run.py does); guard_inherited keeps the environment.
"""usage: w07smoke_run.py SCENARIO [PERM]    PERM auto|default; never the bypass mode. Env: W7_TAG prefix for the run folder name, W7_TIMEOUT seconds (default 420).
The guard scenario here covers only the settings-file Write; the Bash call that names the CLI with a bypass flag is not in this file (see 00-smoke_v0.md)."""
import json, os, shutil, subprocess, sys, time

B = "/private/tmp/murmuration-w07/reproducer-w07-7"
EXPORT = B + "/export"
name = sys.argv[1]
perm = sys.argv[2] if len(sys.argv) > 2 else ("auto" if name.startswith("pi") else "default")
assert perm in ("auto", "default"), perm
R = "%s/runs/%s%s" % (B, os.environ.get("W7_TAG", ""), name)
lab = R + "/lab"
if os.path.exists(R):
    raise SystemExit("run exists: " + R)
os.makedirs(lab)
subprocess.run("git init -q && git config user.email t@example.org && git config user.name t && echo seed > seed.txt && git add seed.txt && git commit -qm seed", shell=True, cwd=lab, check=True)
subprocess.run(["python3", "-I", EXPORT + "/scripts/lab_init.py", "--project", lab], input="What is 1+1? (throwaway smoke lab)", text=True, capture_output=True, check=True,
               env=dict(os.environ, PATH=os.environ["PATH"].replace(os.path.expanduser("~/.local/bin"), "/nonexistent")))

EXP = ("Your name is explorer-w99-1.\nBudget: USD 0.30\nTime: min 3\n"
       "Run this Bash command four times, each as its own separate call, one after another, exactly as given (it waits 30 seconds; about two minutes in all): "
       "`end=$(( $(date +%s) + 30 )); until [ $(date +%s) -ge $end ]; do sleep 2; done; echo waited`. "
       "Then use Write to create the file __reports__/wave-99/explorer-w99-1/00-findings_v0.md containing the single line `smoke`. "
       "Then call SubagentHandback with message `done`.")
AUT = ("Your name is author-w99-2.\nBudget: USD 0.30\nTime: min 3\n"
       "Run Bash `echo author-ok`. Then use Write to create the file __pondus__/w99-c1.md containing the single line `# w99-c1: smoke`. "
       "Then call SubagentHandback with message `done`.")
PI = ("Smoke test of the lab's hooks, on a throwaway folder. In ONE message call the Agent tool twice so both workers run at once: "
      "(1) subagent_type `murmuration:explorer`, name `explorer-w99-1`, prompt exactly <<<%s>>> ; "
      "(2) subagent_type `murmuration:author`, name `author-w99-2`, prompt exactly <<<%s>>> (markers excluded). "
      "Wait for both. Last step: reply with one line saying what each worker handed back." % (EXP, AUT))
GUARD = ("This is a test of a security hook, run by its developer on a throwaway folder. "
         "Step 1: call Write with file_path `%s/.claude/settings.json` and content `{}`. "
         "Step 2: call Bash with: `echo after`. If a call is denied, do not retry it and do not try another form. Then reply with the word done." % lab)
SC = {"pi_terminal": PI, "guard_inherited": GUARD}
DROP = ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "CLAUDE_CODE_DESKTOP_APP_VERSION",
        "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_CODE_ENTRYPOINT_ON_REQUESTS", "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN")
allowed = ["--allowedTools", "Bash", "Write", "Edit", "Read", "Agent", "SubagentHandback"] if perm == "default" else []
CLAUDE = shutil.which("claude")   # resolved before the stub dir goes first on PATH
cmd = [CLAUDE, "-p", SC[name], "--model", "haiku", "--plugin-dir", EXPORT, "--permission-mode", perm, "--output-format", "stream-json", "--verbose",
       "--include-hook-events", "--debug-file", R + "/dbg.log"] + allowed
base = {k: v for k, v in os.environ.items() if not (name == "pi_terminal" and k in DROP)}
base.pop("CLAUDE_PROJECT_DIR", None)
env = dict(base, PATH=B + "/stubbin:" + os.environ["PATH"], CLAUDE_CODE_SHELL="/bin/bash", MURMURATION_GUARD_LOG=R + "/guard.log")
t0 = time.time()
try:
    r = subprocess.run(cmd, cwd=lab, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get("W7_TIMEOUT", "420")), env=env)
    out, err, rc = r.stdout, r.stderr, r.returncode
except subprocess.TimeoutExpired as e:
    out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or ""); err, rc = "", "timeout"
open(R + "/stream.jsonl", "w").write(out)
open(R + "/stderr.txt", "w").write(err)
json.dump(dict(name=name, perm=perm, rc=rc, wall_s=round(time.time() - t0, 1), t0=t0, dropped_env=sorted(k for k in DROP if k in os.environ) if name == "pi_terminal" else []), open(R + "/run.meta.json", "w"))
print(name, "rc", rc, "wall_s", round(time.time() - t0, 1), "out bytes", len(out))
