# w06-c9 verifier: wall-clock of the registered `sh -c` command for a worker PostToolUse (budget), main's tree against the build's, alternating, in a primed lab each; inputs: --old ROOT --new ROOT --work DIR --transcript PATH --n N; output: medians, p10/p90 of both arms, of the pairwise difference, and of `sh :` and `python3 -S -I -c pass` in the same loop
import argparse, json, os, re, shutil, statistics as st, subprocess, sys, time
ap = argparse.ArgumentParser()
ap.add_argument("--old"); ap.add_argument("--new"); ap.add_argument("--work"); ap.add_argument("--transcript"); ap.add_argument("--n", type=int, default=40)
a = ap.parse_args()
W = os.path.abspath(a.work); shutil.rmtree(W, ignore_errors=True)

def cmd_of(root, event):
    for g in json.load(open(root + "/hooks/hooks.json"))["hooks"][event]:
        for h in g["hooks"]:
            if "budget" in h["command"]:
                return h["command"].replace("${CLAUDE_PLUGIN_ROOT}", root)

def prime(tag, root):
    lab, sess = "%s/%s/lab" % (W, tag), "%s/%s/sess" % (W, tag)
    os.makedirs(lab + "/__statera__"); os.makedirs(sess + "/subagents")
    aid = "benchw1"
    shutil.copy(a.transcript, "%s/subagents/agent-%s.jsonl" % (sess, aid))
    json.dump({"name": "explorer-w98-1"}, open("%s/subagents/agent-%s.meta.json" % (sess, aid), "w"))
    base = dict(session_id="s", transcript_path=sess + ".jsonl", permission_mode="auto", cwd=lab, agent_id=aid, agent_type="murmuration:explorer")
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root); env.pop("CLAUDE_PROJECT_DIR", None)
    subprocess.run(["sh", "-c", cmd_of(root, "SubagentStart")], input=json.dumps(dict(base, hook_event_name="SubagentStart")), text=True, capture_output=True, cwd=lab, env=env)
    return lab, env, json.dumps(dict(base, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}, tool_response="ok", tool_use_id="t1"))

arms = {}
for tag, root in (("old", os.path.abspath(a.old)), ("new", os.path.abspath(a.new))):
    lab, env, payload = prime(tag, root)
    arms[tag] = (["sh", "-c", cmd_of(root, "PostToolUse")], lab, env, payload)
arms["sh"] = (["sh", "-c", ":"], arms["old"][1], arms["old"][2], arms["old"][3])
arms["py"] = (["sh", "-c", "python3 -S -I -c pass"], arms["old"][1], arms["old"][2], arms["old"][3])
res = {k: [] for k in arms}
def once(k):
    cmd, lab, env, payload = arms[k]
    t = time.perf_counter()
    p = subprocess.run(cmd, input=payload, text=True, capture_output=True, cwd=lab, env=env)
    return (time.perf_counter() - t) * 1000, p
for k in ("old", "new"): once(k); once(k)
outs = {}
for i in range(a.n):
    order = ["old", "new", "sh", "py"] if i % 2 == 0 else ["py", "sh", "new", "old"]
    for k in order:
        ms, p = once(k); res[k].append(ms); outs[k] = (p.returncode, p.stdout, p.stderr)
q = lambda xs, f: sorted(xs)[min(len(xs) - 1, int(f * len(xs)))]
for k in res:
    print("%-4s median %.1f ms  p10 %.1f  p90 %.1f" % (k, st.median(res[k]), q(res[k], .1), q(res[k], .9)))
d = [o - n for o, n in zip(res["old"], res["new"])]
print("old - new: median %.1f ms  mean %.1f  p10 %.1f  p90 %.1f  positive in %d of %d pairs" % (st.median(d), st.mean(d), q(d, .1), q(d, .9), sum(x > 0 for x in d), len(d)))
print("outputs of the last start: old %r, new %r, equal=%s" % (outs["old"][1][:60], outs["new"][1][:60], outs["old"] == outs["new"]))
