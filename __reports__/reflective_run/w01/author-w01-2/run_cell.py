"""Run one experiment cell: a headless `claude -p` run with one subagent, then analyse.

usage: python3 -I run_cell.py <cell-name> --bin {installed|desktop} --mode {fg|bg} --think {on|off}
                              --length {short|long} --env {inherit|clean} --io {p|sdk}
Everything lands under runs/<cell-name>/ (work/ is the cwd, hooks/ the hook logs, stdout.jsonl).
Model: haiku.  Budget cap: --max-budget-usd 0.40.
"""
import argparse, json, os, subprocess, sys, time, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BINS = {"installed": "claude",
        "desktop": "/Users/hacker/Library/Application Support/Claude/claude-code/2.1.299/4fa9694b7975/claude.app/Contents/MacOS/claude"}

TOPIC = "why the number of subsets of an n-element set doubles each time n grows by one"


def build(args, cell):
    work = os.path.join(HERE, "runs", cell, "work")
    hooks = os.path.join(HERE, "runs", cell, "hooks")
    os.makedirs(work, exist_ok=True)
    os.makedirs(hooks, exist_ok=True)
    open(os.path.join(work, "note.txt"), "w").write("Topic: " + TOPIC + "\n")
    hk = {"type": "command", "command": "python3 -I %s %s" % (os.path.join(HERE, "probe_hook.py"), hooks), "timeout": 20}
    settings = {"hooks": {e: [{"hooks": [hk]}] for e in
                          ("SessionStart", "SubagentStart", "SubagentStop", "Stop", "SessionEnd")}}
    sp = os.path.join(HERE, "runs", cell, "settings.json")
    json.dump(settings, open(sp, "w"), indent=1)
    if args.length == "long":
        task = ("Read note.txt with the Bash tool (cat note.txt). Think it through carefully first. Then write a "
                "clear, self-contained explanation of the topic of about 600 words, as your final answer, in prose.")
    else:
        task = "Read note.txt with the Bash tool (cat note.txt). Then answer in one short sentence."
    agent = {"essayist": {"description": "reads note.txt, then writes about its topic",
                          "prompt": "You are an essayist. " + task, "model": "haiku"}}
    where = "in the background (run_in_background: true)" if args.mode == "bg" else \
        "in the foreground (run_in_background: false); wait for its result"
    prompt = ("Call the Agent tool exactly once with subagent_type 'essayist', %s. "
              "When it has finished, reply with the single word DONE." % where)
    cmd = [BINS[args.bin], "-p", "--model", "haiku", "--setting-sources", "project", "--settings", sp,
           "--agents", json.dumps(agent), "--output-format", "stream-json", "--verbose",
           "--permission-mode", (args.permmode or ("auto" if args.auto == "1" else "bypassPermissions")), "--max-budget-usd", "0.40"]
    if args.permmode in ("default", "acceptEdits", "dontAsk", "plan"):
        cmd += ["--allowedTools=Bash,Read,Agent,Task"]
    if args.partial == "1":
        cmd += ["--include-partial-messages"]
    if args.thinkdisp == "omitted":
        cmd += ["--thinking-display", "omitted"]
    if args.effort == "high":
        cmd += ["--effort=high"]
    stdin = None
    if args.io == "sdk":
        cmd += ["--input-format", "stream-json"]
        stdin = json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": prompt}]}}) + "\n"
    else:
        cmd += [prompt]
    env = dict(os.environ)
    if args.env == "clean":
        for k in list(env):
            if k.startswith("CLAUDE_") or k.startswith("CLAUDECODE") or k in ("__CFBundleIdentifier",):
                del env[k]
    if os.environ.get("PROBE_POLL") == "1" or args.poll == "1":
        env["PROBE_POLL"] = "1"
    if args.think == "off":
        env["MAX_THINKING_TOKENS"] = "0"
    return cmd, stdin, env, work


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell")
    ap.add_argument("--bin", choices=BINS, default="installed")
    ap.add_argument("--mode", choices=("fg", "bg"), default="fg")
    ap.add_argument("--think", choices=("on", "off"), default="on")
    ap.add_argument("--length", choices=("short", "long"), default="long")
    ap.add_argument("--env", choices=("inherit", "clean"), default="inherit")
    ap.add_argument("--io", choices=("p", "sdk"), default="p")
    ap.add_argument("--partial", choices=("0", "1"), default="0")      # --include-partial-messages
    ap.add_argument("--thinkdisp", choices=("default", "omitted"), default="default")  # --thinking-display omitted
    ap.add_argument("--effort", choices=("default", "high"), default="default")
    ap.add_argument("--auto", choices=("0", "1"), default="0")          # --permission-mode auto instead of bypass
    ap.add_argument("--poll", choices=("0", "1"), default="0")   # hook polls the subagent file until final (remedy test)
    ap.add_argument("--permmode", default=None)  # explicit --permission-mode value (overrides --auto)
    args = ap.parse_args()
    cell = args.cell
    shutil.rmtree(os.path.join(HERE, "runs", cell), ignore_errors=True)
    cmd, stdin, env, work = build(args, cell)
    base = os.path.join(HERE, "runs", cell)
    json.dump(dict(vars(args), cmd=cmd, started=time.time()), open(os.path.join(base, "cell.json"), "w"), indent=1)
    t0 = time.time()
    p = subprocess.run(cmd, input=(stdin if stdin is not None else ""), capture_output=True, text=True, cwd=work, env=env, timeout=420)
    open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout)
    open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
    print(cell, "exit", p.returncode, "wall %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
