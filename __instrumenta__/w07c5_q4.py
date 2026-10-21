# r5 of w07-c5 (v0's q4 cases again, for the v1 script that runs async and polls up to 3 s): runs the script as a process on 8 failure cases (unreadable file, directory, missing file, no prompt_id, malformed records, 50 MB transcript without the record, 50 MB single line, a control that must drop) and checks rc 0, empty output, the prompt stored or dropped as expected, wall under 3.6 s (the poll is 3 s); inputs: argv[1] = user_words.py, argv[2] = scratch folder under /private/tmp, `--quick` = 5 MB transcripts; output: stdout table.
import json, sys, os, time, subprocess, tempfile, shutil
sys.argv = [sys.argv[0], sys.argv[1], "unused", sys.argv[2]] + sys.argv[3:]
sys.argv[1] = os.path.abspath(sys.argv[1]); scratch = os.path.abspath(sys.argv[3]); assert scratch.startswith("/private/tmp/"); os.makedirs(scratch, exist_ok=True)
quick = "--quick" in sys.argv; BIG = (5 if quick else 50) * 1000 * 1000
def mk_transcript(path, size, pid, mark, record_last=True):
    rec = json.dumps({"type": "user", "promptId": pid, "message": {"content": "words"}, **mark}) + "\n"
    with open(path, "w") as fh:
        chunk = json.dumps({"type": "attachment", "pad": "y" * 900}) + "\n"
        n = max(0, size // len(chunk))
        for _ in range(n): fh.write(chunk)
        if record_last: fh.write(rec)
# ---- q4: the branch script as a hook process, each failure case
print("\nq4: the script as a process on a lab with a plain prompt; rc, stderr empty, stored, wall (s)")
def hook(event, tp_setup=None):
    lab = tempfile.mkdtemp(dir=scratch); os.makedirs(os.path.join(lab, "__statera__"))
    env = dict(os.environ); env.pop("CLAUDE_PROJECT_DIR", None)
    ev = dict(event, prompt="plain words here", cwd=lab, hook_event_name="UserPromptSubmit")
    t = time.perf_counter()
    p = subprocess.run([sys.executable, sys.argv[1]], input=json.dumps(ev), capture_output=True, text=True, env=env, cwd=lab, timeout=60)
    wall = time.perf_counter() - t
    f = os.path.join(lab, "__statera__", "user_words.md")
    stored = os.path.exists(f) and "plain words here" in open(f).read()
    shutil.rmtree(lab); return p.returncode, p.stderr == "" and p.stdout == "", stored, wall
peer = {"origin": {"kind": "peer"}, "promptSource": "system", "turnOrigin": "peer"}
unread = os.path.join(scratch, "unreadable.jsonl"); mk_transcript(unread, 1000, "pid-u", peer); os.chmod(unread, 0)
malformed = os.path.join(scratch, "malformed.jsonl"); open(malformed, "w").write('{"type":"user","promptId":"pid-m","origin":{"kind":"pe\n{"type":"user","promptId":"pid-m"\n')
big_miss = os.path.join(scratch, "big_miss.jsonl"); mk_transcript(big_miss, BIG, "pid-bm", peer, record_last=False)
big_peer = os.path.join(scratch, "big_peer.jsonl"); mk_transcript(big_peer, BIG, "pid-bp", peer)
oneline = os.path.join(scratch, "oneline.jsonl")
with open(oneline, "w") as fh: fh.write('{"type":"user","promptId":"pid-ol","pad":"' + "z" * BIG + '"}')
cases = [("unreadable transcript (mode 000)", {"transcript_path": unread, "prompt_id": "pid-u"}, True), ("transcript path is a directory", {"transcript_path": scratch, "prompt_id": "pid-u"}, True),
         ("transcript missing", {"transcript_path": os.path.join(scratch, "nope.jsonl"), "prompt_id": "pid-u"}, True),
         ("missing prompt_id (peer record present)", {"transcript_path": big_peer}, True), ("malformed records", {"transcript_path": malformed, "prompt_id": "pid-m"}, True),
         ("%d MB transcript, record absent" % (BIG // 1000000), {"transcript_path": big_miss, "prompt_id": "pid-bm"}, True),
         ("%d MB transcript, single line, id at its start" % (BIG // 1000000), {"transcript_path": oneline, "prompt_id": "pid-ol"}, True),
         ("%d MB transcript, peer record last (control: must drop)" % (BIG // 1000000), {"transcript_path": big_peer, "prompt_id": "pid-bp"}, False)]
fails = 0
for name, ev, want in cases:
    rc, clean, stored, wall = hook(ev)
    ok = rc == 0 and clean and stored == want and wall < 3.6
    fails += not ok
    print("  %-62s rc=%d clean=%s stored=%s (want %s) wall=%.2f %s" % (name, rc, clean, stored, want, wall, "ok" if ok else "FAIL"))
os.chmod(unread, 0o600)
print("q4 failures:", fails)
