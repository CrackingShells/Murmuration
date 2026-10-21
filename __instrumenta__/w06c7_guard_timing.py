# w06-c7 (g4 side measure): wall time of one guard process (python3 with different interpreter flags) on an allowed Bash event, and of a bare interpreter start, 30 runs each; inputs: none (uses scripts/permission_guard.py); outputs: median and p90 milliseconds per variant on stdout.
import json, os, statistics, subprocess, sys, time

G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "permission_guard.py")
ev = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/tmp"})
N = 30


def t(args, stdin):
    out = []
    for _ in range(N):
        t0 = time.perf_counter()
        subprocess.run(args, input=stdin, capture_output=True, text=True)
        out.append((time.perf_counter() - t0) * 1000)
    out.sort()
    return round(statistics.median(out), 1), round(out[int(N * 0.9) - 1], 1)


for name, args, stdin in [
    ("python3 -c pass", ["python3", "-c", "pass"], ""),
    ("python3 -I -S -c pass", ["python3", "-I", "-S", "-c", "pass"], ""),
    ("guard: python3", ["python3", G], ev),
    ("guard: python3 -I", ["python3", "-I", G], ev),
    ("guard: python3 -I -S", ["python3", "-I", "-S", G], ev),
    ("sh -c true", ["sh", "-c", "true"], ""),
]:
    print("%-24s median %6.1f ms  p90 %6.1f ms" % ((name,) + t(args, stdin)))
