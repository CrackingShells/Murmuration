# Runs one headless haiku `claude -p` session that is driven past a small auto-compact threshold, from a scenario name (and env overrides) to <S>/runs/<name>/{stream.jsonl,stderr.txt,debug.log,hooks.log,meta.json}; the lab, filler files and a trimmed plugin export (resume|compact brief, PreCompact/PostCompact loggers) are built under <S>.
"""usage: w08e_compact_run.py S NAME [ENV=VAL ...] [--precompact-text TEXT]
S = scratch folder outside the repo (e.g. /private/tmp/murmuration-w08/explorer-w08-e); the plugin export is S/plugin (git archive).
Facts planted in the first user message: number 48213, path /opt/zeta/config.toml, quote 'the heron files its taxes in blue ink'; one more in the first file read: audit code KX-9917.
Filler: 20 files (default) of ~6k tokens of seeded pseudo-prose. Permission mode: default, tools Read only. No budget flag. Cost per run about USD 0.3 on haiku."""
import json, os, random, shutil, subprocess, sys, time

S = os.path.abspath(sys.argv[1]); NAME = sys.argv[2]
env_over = {}; pre_text = None; nfiles = 20; model = "haiku"; tail = []
args = sys.argv[3:]
i = 0
while i < len(args):
    a = args[i]
    if a == "--precompact-text": pre_text = args[i + 1]; i += 2; continue
    if a == "--no-resume": i += 1; continue
    if a == "--nfiles": nfiles = int(args[i + 1]); i += 2; continue
    if a == "--model": model = args[i + 1]; i += 2; continue
    if "=" in a: k, v = a.split("=", 1); env_over[k] = v
    i += 1

RUN = os.path.join(S, "runs", NAME); LAB = os.path.join(RUN, "lab"); shutil.rmtree(RUN, ignore_errors=True)
os.makedirs(os.path.join(LAB, "__statera__")); os.makedirs(os.path.join(LAB, "__scrupuli__")); os.makedirs(os.path.join(LAB, "fill"))
open(os.path.join(LAB, "__statera__", "wave-01.md"), "w").write("# Wave 01\n\nopened: 2026-01-01\n\nWAVE-NOTE-BODY-MARKER: test lab for compaction run.\n")
open(os.path.join(LAB, "__scrupuli__", "wave-01-x.md"), "w").write("## S-w01-x-1\nOPEN-PUZZLE-MARKER odd rows\nrefs: a.csv\n")
subprocess.run(["git", "init", "-q", LAB])
rnd = random.Random(7); codes = {}
words = ("river stone lantern copper meadow harbor violet engine thunder marble orchard signal winter anchor basket "
         "candle desert forest garden island jungle kettle ladder mirror needle ocean pebble quartz ribbon saddle "
         "tunnel umbrella valley window yonder zephyr amber bridge cobalt dragon ember falcon glacier horizon").split()
for n in range(nfiles):
    lines = []
    for ln in range(160):
        lines.append("%03d.%03d " % (n, ln) + " ".join(rnd.choice(words) for _ in range(22)) + ".")
    code = "".join(rnd.choice("BCDFGHJKLMNPQRSTVWXZ") for _ in range(6)); codes[n] = code
    lines[80] = "%03d.080 NOTE: ref code %s." % (n, code)
    if n == 0: lines[40] = "000.040 NOTE: the audit code of this archive is KX-9917, do not lose it."
    open(os.path.join(LAB, "fill", "f%d.txt" % n), "w").write("\n".join(lines) + "\n")

json.dump(codes, open(os.path.join(RUN, "codes.json"), "w"))
# trimmed plugin: only the lab's SessionStart resume|compact row, plus loggers
PL = os.path.join(RUN, "plugin"); shutil.copytree(os.path.join(S, "plugin"), PL, ignore=shutil.ignore_patterns("__reports__", "__roadmap__", "rust", "probes", "validation", "bin", ".git"))
HOOKLOG = os.path.join(RUN, "hooks.log")
logger = os.path.join(RUN, "log_hook.py")
open(logger, "w").write('import sys,json,time,os\nraw=sys.stdin.read()\nd=json.loads(raw)\nopen(%r,"a").write(json.dumps({"t":time.time(),"event":d.get("hook_event_name"),"source":d.get("source"),"trigger":d.get("trigger"),"keys":sorted(d),"summary_chars":len(d.get("compact_summary") or ""),"custom_instructions":d.get("custom_instructions")})+"\\n")\nif d.get("hook_event_name")=="PostCompact": open(%r,"w").write(d.get("compact_summary",""))\nt=os.environ.get("PRECOMPACT_TEXT")\nif t and d.get("hook_event_name")=="PreCompact": print(t)\n' % (HOOKLOG, os.path.join(RUN, "summary.txt")))
def row(ev, matcher, cmd):
    r = {"hooks": [{"type": "command", "command": "python3", "args": cmd, "timeout": 10}]}
    if matcher: r["matcher"] = matcher
    return r
hooks = {"hooks": {
    "SessionStart": [row("SessionStart", "resume|compact", ["${CLAUDE_PLUGIN_ROOT}/scripts/resume_brief.py"]),
                     row("SessionStart", None, [logger])],
    "PreCompact": [row("PreCompact", None, [logger])],
    "PostCompact": [row("PostCompact", None, [logger])]}}
json.dump(hooks, open(os.path.join(PL, "hooks", "hooks.json"), "w"), indent=1)

files = " then ".join("fill/f%d.txt" % n for n in range(nfiles))
prompt = ("Please remember these three things exactly: (1) my lucky number is 48213; (2) my config file is /opt/zeta/config.toml; "
          "(3) I said: 'the heron files its taxes in blue ink'. "
          "Now read these files one at a time with the Read tool, in this order, one tool call per turn, never several at once: %s. "
          "Say only 'ok' after each. After the last file, without reading anything again, write exactly four lines: my lucky number, "
          "my config file path, my quoted sentence, and the audit code you found in the first file; if you do not know one, write UNKNOWN for it." % files)
env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
for k in list(env):
    if k.startswith("CLAUDE_AUTOCOMPACT") or k.startswith("CLAUDE_CODE_AUTO_COMPACT") or k in ("DISABLE_AUTO_COMPACT", "DISABLE_COMPACT"): env.pop(k)
env.update(env_over)
if pre_text: env["PRECOMPACT_TEXT"] = pre_text
cmd = ["claude", "-p", prompt, "--model", model, "--plugin-dir", PL, "--permission-mode", "default", "--allowedTools", "Read",
       "--output-format", "stream-json", "--verbose", "--debug-file", os.path.join(RUN, "debug.log"), "--max-turns", "40"]
t0 = time.time()
p = subprocess.run(cmd, cwd=LAB, env=env, capture_output=True, text=True)
open(os.path.join(RUN, "stream.jsonl"), "w").write(p.stdout); open(os.path.join(RUN, "stderr.txt"), "w").write(p.stderr)
sid = None
for ln in p.stdout.splitlines():
    try: d = json.loads(ln)
    except ValueError: continue
    if d.get("type") == "system" and d.get("subtype") == "init": sid = d.get("session_id"); break
if sid and "--no-resume" not in sys.argv:
    q = ("Without using any tool and without reading any file: write exactly four lines: my lucky number, my config file path, "
         "my quoted sentence, and the audit code of the first file. If you do not know one of them, write UNKNOWN for it. "
         "Then, on %d more lines of the form fK=CODE, give for each file f0..f%d the ref code of its NOTE line (the line that says 'ref code') if you still know it exactly, else fK=UNKNOWN." % (nfiles, nfiles - 1))
    cmd2 = ["claude", "-p", q, "--resume", sid, "--model", model, "--plugin-dir", PL, "--permission-mode", "default", "--allowedTools", "Read",
            "--output-format", "stream-json", "--verbose", "--debug-file", os.path.join(RUN, "debug_resume.log")]
    p2 = subprocess.run(cmd2, cwd=LAB, env=env, capture_output=True, text=True)
    open(os.path.join(RUN, "stream_resume.jsonl"), "w").write(p2.stdout)
json.dump({"name": NAME, "env": env_over, "precompact_text": pre_text, "model": model, "nfiles": nfiles, "rc": p.returncode, "wall_s": round(time.time() - t0, 1), "t0": t0, "cmd_head": cmd[:2] + cmd[3:]}, open(os.path.join(RUN, "meta.json"), "w"), indent=1)
print(NAME, "rc", p.returncode, "wall", round(time.time() - t0, 1))
