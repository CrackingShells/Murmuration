import sys, time, os, json
t0 = time.time() * 1000
sys.stdin.read()
tag = sys.argv[1] if len(sys.argv) > 1 else ""
print("noop-py " + tag)
log = os.environ.get("W06_LOG")
if log:
    with open(log, "a") as f:
        f.write(json.dumps({"lang": "py", "tag": tag, "t0_ms": t0, "t1_ms": time.time() * 1000, "pid": os.getpid()}) + "\n")
