"""Wraps one plugin hook command: copies the hook's stdin payload and the wall time of the real script to a JSONL file, then runs the real script unchanged.

Inputs: argv[1] = label (event|matcher|script), argv[2] = absolute path of the real script, stdin = the hook payload, env REC_DIR = folder for `payloads.jsonl`.
Output: one JSON line per call in $REC_DIR/payloads.jsonl (label, t, wall_ms of the inner run, payload text, stdout text); the real script's stdout is passed through, its exit code kept.
Used only in recording runs outside the repository (w04-c5); never registered in the shipped plugin.
"""
import json, os, subprocess, sys, time

raw = sys.stdin.buffer.read()
t0 = time.perf_counter()
p = subprocess.run([sys.executable, sys.argv[2]], input=raw, capture_output=True, env={k: v for k, v in os.environ.items() if k != "REC_DIR"})
wall = (time.perf_counter() - t0) * 1000
rec = dict(label=sys.argv[1], t=time.time(), wall_ms=round(wall, 2), payload=raw.decode("utf-8", "replace"), stdout=p.stdout.decode("utf-8", "replace"), rc=p.returncode, nl_end=raw.endswith(b"\n"))
fd = os.open(os.path.join(os.environ["REC_DIR"], "payloads.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
os.write(fd, (json.dumps(rec) + "\n").encode())
os.close(fd)
sys.stdout.buffer.write(p.stdout)
sys.exit(p.returncode)
