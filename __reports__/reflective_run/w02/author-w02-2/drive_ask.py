"""Headless host that answers AskUserQuestion permission requests (the SDK/Desktop protocol). usage: drive_ask.py <cwd> <settings> <out.jsonl> <prompt> <answers.json>"""
import os, json, subprocess, sys, time, threading
cwd, settings, out, prompt, answers_json = sys.argv[1:6]
answers = json.loads(answers_json)   # {question text: answer (str or list)}
p = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
    "--model", "haiku", "--setting-sources", "project", "--settings", settings, "--tools", "AskUserQuestion",
    "--permission-prompts", "host", "--permission-prompt-tool", "stdio", "--max-budget-usd", "0.30"],
    cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": prompt}]}}) + "\n"); p.stdin.flush()
t0 = time.time()
with open(out, "w") as fh:
    for line in p.stdout:
        fh.write(line); fh.flush()
        try: r = json.loads(line)
        except ValueError: continue
        if r.get("type") == "control_request" and r["request"].get("subtype") == "can_use_tool":
            req = r["request"]
            upd = dict(req["input"]); upd["answers"] = answers
            body = {"behavior": "deny", "message": "User declined to answer questions"} if os.environ.get("DENY") else {"behavior": "allow", "updatedInput": upd}
            resp = {"type": "control_response", "response": {"subtype": "success", "request_id": r["request_id"], "response": body}}
            p.stdin.write(json.dumps(resp) + "\n"); p.stdin.flush()
        if r.get("type") == "result" or time.time() - t0 > 100:
            break
p.stdin.close()
try: p.wait(timeout=20)
except Exception: p.kill()
