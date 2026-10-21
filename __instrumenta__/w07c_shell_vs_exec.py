"""Times one hook command started four ways, outside Claude Code: `/bin/sh -c`, `/bin/bash -c`, `/bin/zsh -c` (shell form), and direct exec (exec form, no shell), each running `python3 -S -I hook.py label` with a payload on stdin; inputs: path of the probe hook script (w07c_hook.py), reps; output: markdown table of wall time per start (ms): median, p10, p90, interleaved arms, W7C_LOG=/dev/null.
"""
import os, subprocess, sys, time, random, statistics as st, shutil, json
hook = os.path.abspath(sys.argv[1]); reps = int(sys.argv[2]) if len(sys.argv) > 2 else 40
py = shutil.which("python3"); payload = json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": "echo x"}, "tool_use_id": "toolu_x"}).encode()
env = dict(os.environ, W7C_LOG="/dev/null")
arms = {"sh -c": ["/bin/sh", "-c", 'python3 -S -I "%s" lbl' % hook], "bash -c": ["/bin/bash", "-c", 'python3 -S -I "%s" lbl' % hook],
        "zsh -c": ["/bin/zsh", "-c", 'python3 -S -I "%s" lbl' % hook], "exec (no shell)": [py, "-S", "-I", hook, "lbl"],
        "sh -c ':' (shell alone)": ["/bin/sh", "-c", ":"], "bash -c ':' (shell alone)": ["/bin/bash", "-c", ":"]}
res = {k: [] for k in arms}
for r in range(reps + 3):
    for k in random.sample(list(arms), len(arms)):
        t = time.perf_counter(); subprocess.run(arms[k], input=payload, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); d = (time.perf_counter() - t) * 1000
        if r >= 3: res[k].append(d)
print("python3 =", py, "| reps", reps, "\n| start form | median ms | p10 | p90 |\n|:--|--:|--:|--:|")
for k, v in res.items():
    v.sort(); print("| %s | %.1f | %.1f | %.1f |" % (k, st.median(v), v[int(.1 * (len(v) - 1))], v[int(.9 * (len(v) - 1))]))
