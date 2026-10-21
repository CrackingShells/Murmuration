# Failure and edge cases of a user_words.py hook run as a process (argv[1] = script, argv[2] = scratch folder under /private/tmp): for each case builds a lab and a transcript, feeds a UserPromptSubmit payload on stdin, and prints return code, stdout/stderr size, wall time and whether the prompt was stored; the expectation column is what must hold for a record of a person (a typed prompt is never lost; a peer or harness prompt is not stored when its record is found).
import json, os, subprocess, sys, time, stat, shutil
script = os.path.abspath(sys.argv[1]); base = sys.argv[2]; assert base.startswith("/private/tmp/")
shutil.rmtree(base, ignore_errors=True); os.makedirs(base)
PID = "aaaaaaaa-1111-2222-3333-444444444444"
def rec(pid=PID, **kw):
    d = {"type": "user", "promptId": pid, "message": {"role": "user", "content": "x"}}; d.update(kw); return json.dumps(d) + "\n"
HUMAN = dict(origin={"kind": "human"}, promptSource="sdk", turnOrigin="human", entrypoint="claude-desktop")
PEER = dict(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer", entrypoint="claude-desktop")
cases = []
def case(name, content=None, want_stored=True, event=None, setup=None, timeout=15, late=None):
    cases.append((name, content, want_stored, event or {}, setup, timeout, late))
case("record human", rec(**HUMAN), True)
case("record peer (dropped)", rec(**PEER), False)
case("record absent, 1 KB file", rec(pid="other", **PEER), True)
case("no prompt_id", rec(**PEER), True, event={"prompt_id": None})
case("empty transcript", "", True)
case("missing file", None, True, event={"transcript_path": "/private/tmp/nonexistent-dir-x/t.jsonl"})
case("directory", None, True, setup=lambda p: (os.remove(p) if os.path.exists(p) else None, os.mkdir(p)))
case("mode 000", rec(**PEER), True, setup=lambda p: os.chmod(p, 0))
case("symlink loop", None, True, setup=lambda p: (os.path.exists(p) and os.remove(p), os.symlink(p, p)))
case("garbage + torn last line", "not json %s\n" % PID + '{"type":"user","promptId":"%s","origin":{"kind":"pe' % PID, True)
case("binary garbage", None, True, setup=lambda p: open(p, "wb").write(os.urandom(300000) + PID.encode()))
case("record human then torn peer line (same id)", rec(**HUMAN) + '{"type":"user","promptId":"%s","origin":{"kind":"peer"' % PID, True)
case("human record 5 MB from the end (past both windows)", rec(**PEER) + rec(pid="o", pad="x" * 5000000), True)
case("human typed, record lands 1 s late", "", True, late=(1.0, rec(**HUMAN)))
case("peer, record lands 1 s late (dropped)", "", False, late=(1.0, rec(**PEER)))
case("typed, record lands 4 s late (after the wait)", "", True, late=(4.0, rec(**HUMAN)), timeout=20)
case("50 MB multi-line, record absent", None, True, setup=lambda p: open(p, "w").write((rec(pid="o", pad="x" * 9000) * 5500)))
case("50 MB single line", None, True, setup=lambda p: open(p, "w").write('{"a":"' + "x" * 50000000 + '"}\n'))
case("FIFO as transcript (open blocks)", None, True, setup=lambda p: (os.path.exists(p) and os.remove(p), os.mkfifo(p)), timeout=14)
case("human record whose tool-result sibling says peer", rec(**HUMAN) + rec(toolUseResult={"a": 1}, **PEER), True)
case("empty prompt text", rec(**PEER), False, event={"prompt": ""})
print("%-52s %-3s %-6s %-6s %-7s %-7s %s" % ("case", "rc", "stdout", "stderr", "wall s", "stored", "ok?"))
bad = 0
for i, (name, content, want, event, setup, timeout, late) in enumerate(cases):
    d = os.path.join(base, "c%02d" % i); lab = os.path.join(d, "lab"); os.makedirs(lab + "/__statera__"); tp = os.path.join(d, "t.jsonl")
    if content is not None: open(tp, "w").write(content)
    if setup: setup(tp)
    ev = {"prompt": "unique words %02d" % i, "cwd": lab, "prompt_id": PID, "transcript_path": tp, "hook_event_name": "UserPromptSubmit"}; ev.update(event)
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    t0 = time.time(); p = subprocess.Popen([sys.executable, script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=d, env=env)
    if late:
        import threading
        def app(d=late, tp=tp):
            time.sleep(d[0]); open(tp, "a").write(d[1])
        threading.Thread(target=app).start()
    try: out, err = p.communicate(json.dumps(ev), timeout=timeout); rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill(); out, err = p.communicate(); rc = "HANG"
    wall = time.time() - t0
    f = os.path.join(lab, "__statera__", "user_words.md"); stored = os.path.exists(f) and ev["prompt"] in open(f).read() if ev["prompt"] else os.path.exists(f)
    if name == "mode 000": os.chmod(tp, 0o600)
    ok = (rc == 0 and out == "" and err == "" and (stored == want))
    if not ok: bad += 1
    print("%-52s %-3s %-6d %-6d %-7.2f %-7s %s" % (name, rc, len(out), len(err), wall, stored, "ok" if ok else "CHECK want_stored=%s" % want))
print("cases not matching expectation:", bad)
