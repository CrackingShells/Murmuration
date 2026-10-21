# Time N cold starts of scripts/permission_guard.py on one event (as the hook runs it: python3 reading stdin) with K CPU-bound busy processes running; input: guard path, N, K; output: median/p90/max ms (stdout); it starts and stops only its own busy processes
import subprocess, sys, time, json, statistics as st, os, signal
g, N, K = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
busy = [subprocess.Popen([sys.executable, "-I", "-c", "while True: pass"]) for _ in range(K)]
ev = json.dumps(dict(tool_name="Bash", tool_input={"command": "echo $(date +%s) && git status"}, cwd="/tmp"))
ms = []
try:
    time.sleep(1)
    for _ in range(N):
        t = time.time(); subprocess.run([sys.executable, g], input=ev, text=True, capture_output=True); ms.append((time.time() - t) * 1000)
finally:
    for b in busy: b.kill()
    for b in busy: b.wait()
ms.sort(); print("K=%d N=%d median %.0f p90 %.0f p99 %.0f max %.0f ms" % (K, N, st.median(ms), ms[int(.9 * len(ms))], ms[int(.99 * len(ms)) - 1], ms[-1]))
