"""Runs the real hook commands (sh -c, payload on a socket stdin) of two plugin roots on a long worker whose budget is already exceeded, so that PostToolUse blocks and PostToolBatch sends a note, and compares stdout of old and new.

Inputs: argv: OLD_ROOT NEW_ROOT PAYLOADS LONG_TRANSCRIPT FX. Output: per event, old and new stdout (first 200 chars, with the date-dependent fields left in) and EQUAL / DIFFERENT after masking the digits that depend on the clock (none expected: the run clock is fixed by the transcript).
Also runs the same payload with the `agent_id` key renamed (gate must stay silent in new, and old must also say nothing).
"""
import json, os, re, shutil, socket, subprocess, sys, threading
old, new, pay, long_, fx = [os.path.abspath(x) for x in sys.argv[1:6]]
rows = [json.loads(l) for l in open(pay)]
def pick(label, agent, tool=None):
    for r in rows:
        p = json.loads(r["payload"])
        if r["label"] == label and bool(p.get("agent_id")) == agent and (tool is None or p.get("tool_name") == tool): return p
START, POST, BATCH = pick("SubagentStart||budget.py", True), pick("PostToolUse||budget.py", True, "Bash"), pick("PostToolBatch||budget.py", True)
shutil.rmtree(fx, ignore_errors=True)
def cmds(root, ev):
    return [x["command"] for g in json.load(open(root + "/hooks/hooks.json"))["hooks"][ev] if g.get("matcher") is None for x in g["hooks"] if "budget" in x["command"]][0]
def run(root, lab, command, payload):
    sa, sb = socket.socketpair(); data = (json.dumps(payload) + "\n").encode()
    th = threading.Thread(target=lambda: (sa.sendall(data), sa.close())); th.start()
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root); env.pop("CLAUDE_PROJECT_DIR", None)
    r = subprocess.run(["/bin/sh", "-c", 'cd "%s" && %s' % (lab, command)], stdin=sb, capture_output=True, env=env); th.join(); sb.close()
    return r.stdout.decode()
out = {}
for name, root in (("old", old), ("new", new)):
    lab, sess = fx + "/%s/lab" % name, fx + "/%s/sess" % name
    os.makedirs(lab + "/__statera__"); os.makedirs(sess + "/subagents")
    shutil.copy(long_, sess + "/subagents/agent-azz.jsonl"); json.dump({"name": "explorer-w05-x", "agentType": "murmuration:explorer"}, open(sess + "/subagents/agent-azz.meta.json", "w")); open(sess + ".jsonl", "w").close()
    def P(base, **o):
        p = dict(base, cwd=lab, transcript_path=sess + ".jsonl", agent_id="azz", agent_type="murmuration:explorer"); p.update(o); return p
    run(root, lab, cmds(root, "SubagentStart"), P(START))
    sp = lab + "/__statera__/.harness/azz.json"; s = json.load(open(sp)); s.update(B=0.5, T=1e6, brief_read=True, warned=True); json.dump(s, open(sp, "w"))
    with open(sess + "/subagents/agent-azz.jsonl", "a") as f:   # a fresh expensive request after the start: spend now exceeds 1.5 x B
        f.write(json.dumps({"type": "assistant", "requestId": "req_w05_big", "timestamp": "2026-10-19T19:59:00.000Z", "message": {"id": "msg_w05_big", "role": "assistant", "model": "claude-sonnet-4-5", "content": [{"type": "text", "text": "z"}], "usage": {"input_tokens": 1000000, "output_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}) + "\n")
    out[name] = dict(batch=run(root, lab, cmds(root, "PostToolBatch"), P(BATCH)), post=run(root, lab, cmds(root, "PostToolUse"), P(POST)),
                     renamed=run(root, lab, cmds(root, "PostToolUse"), {("agentId" if k == "agent_id" else k): v for k, v in P(POST).items()}))
for k in ("batch", "post", "renamed"):
    o, n = out["old"][k], out["new"][k]
    print("%-8s %s | old: %r | new: %r" % (k, "EQUAL" if o == n else "DIFFERENT", o[:160], n[:160]))
