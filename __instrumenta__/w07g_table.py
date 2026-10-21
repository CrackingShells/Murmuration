# Turns w07g_parse.py output (calls.jsonl, sessions.jsonl) and runs/loadavg.tsv into the markdown tables of explorer-w07-g: per-arm tool-phase split (hook, classifier wait, run), hook costs by script, paired differences per rep, context length early vs late, four ways to read four files; inputs: <parsed dir>, <loadavg.tsv>; output: markdown on stdout.
# usage: w07g_table.py PARSED_DIR LOADAVG_TSV
import json, sys, os, statistics as st

P, LA = sys.argv[1], sys.argv[2]
calls = [json.loads(l) for l in open(os.path.join(P, "calls.jsonl"))]
sess = [json.loads(l) for l in open(os.path.join(P, "sessions.jsonl"))]
load = {}
for l in open(LA):
    f = l.split("\t")
    load[f[0]] = (float(f[2]), float(f[4]), float(f[3]), float(f[5]))
load["trial"] = (5.99, 0, 0, 0)  # the trial was run by hand: load1 5.99 is the `uptime` read a few minutes before it; the after value was not read (0 = unknown)


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def dist(xs):
    return "%d / %d / %d (n=%d)" % (round(st.median(xs)), round(q(xs, 0.9)), round(max(xs)), len(xs)) if xs else "-"


def fl(c):
    return c["label"] if c["label"] != "trial" else "A0"


def cell_name(c):
    return {"A": "auto, colgrep hook on, no lab plugin", "B": "auto, colgrep off, no lab plugin", "C": "auto, colgrep on, lab plugin", "D": "auto, colgrep off, lab plugin",
            "F": "default + allowedTools, colgrep off, no lab plugin"}[c]


bash = [c for c in calls if c["tool"] == "Bash" and c["cell"] in "ABCDF" and c["label"][0] != "W" and c["label"][0] != "L"]
print("## 1. Bash tool phase by arm (ms; median / p90 / max), calls 2..8 of each session (call 1 carries the shell-snapshot start and is shown apart)\n")
print("| arm | sessions | n calls | tool phase (transcript: tool_use record to result record) | PreToolUse hooks (log, longest per call) | classifier wait (log permissionDecisionMs) | command run (log durationMs) | tool_use record to dispatch start (hooks and classifier, as one wait) | dispatch end to result record (PostToolUse hook) | phase, median per session |")
print("|:--|:--|--:|:--|:--|:--|:--|:--|:--|:--|")
for cell in "ABFCD":
    cs = [c for c in bash if c["cell"] == cell and c["n_in_run"] > 1]
    if not cs:
        continue
    labs = sorted({fl(c) for c in cs})
    other = [c["asst_to_disp_ms"] - c["pre_ms"] - c["perm_ms"] for c in cs]
    meds = [st.median([c["phase_ms"] for c in cs if fl(c) == l]) for l in labs]
    print("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (cell + " " + cell_name(cell), ",".join(labs), len(cs), dist([c["phase_ms"] for c in cs]), dist([c["pre_ms"] for c in cs]),
                                                       dist([c["perm_ms"] for c in cs]), dist([c["run_ms"] for c in cs]), dist([c["asst_to_disp_ms"] for c in cs]), dist([c["end_to_result_ms"] for c in cs]), " / ".join("%s %d" % (l, m) for l, m in zip(labs, meds))))
print("\nCall 1 of each session (first Bash of a session: shell snapshot), phase / run ms:\n")
print("| arm | call-1 phase ms by session | call-1 run ms by session |\n|:--|:--|:--|")
for cell in "ABFCD":
    cs = [c for c in bash if c["cell"] == cell and c["n_in_run"] == 1]
    print("| %s | %s | %s |" % (cell, ", ".join("%s %d" % (fl(c), c["phase_ms"]) for c in cs), ", ".join("%s %d" % (fl(c), c["run_ms"]) for c in cs)))

print("\n## 2. Paired differences of the median tool phase per rep (calls 2..8; one session per arm per rep; arms were run interleaved in a shuffled order, so pairs are by rep index, not adjacent in time)\n")
by = {}
for c in bash:
    if c["n_in_run"] > 1:
        by.setdefault(fl(c), []).append(c)
rep_of = lambda l: "0" if l == "A0" else l[-1]
print("| rep | A (auto, colgrep on) | B (auto, colgrep off) | C (auto, colgrep on, lab) | D (auto, colgrep off, lab) | F (default+allow, colgrep off) | A-B | C-A | D-B | B-F |")
print("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for rep in "01":
    m = {}
    for cell in "ABCDF":
        l = "A0" if (cell == "A" and rep == "0") else cell + rep
        m[cell] = st.median([c["phase_ms"] for c in by.get(l, [])]) if by.get(l) else None
    f = lambda a, b: "%d" % (m[a] - m[b]) if m[a] is not None and m[b] is not None else "-"
    print("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (rep, *[("%d" % m[c]) if m[c] is not None else "-" for c in "ABCDF"], f("A", "B"), f("C", "A"), f("D", "B"), f("B", "F")))

print("\n## 3. Hook runs the log records, by event / tool / script (ms; median / p90 / max)\n")
rows = {}
for s in sess:
    for ev, tool, script, plug, ms in s["all_hooks"]:
        rows.setdefault((ev, tool, script, plug), []).append(ms)
print("| event:tool | script | from | runs | ms |\n|:--|:--|:--|--:|:--|")
for k in sorted(rows, key=lambda k: (k[0], k[1], k[2])):
    print("| %s:%s | %s | %s | %d | %s |" % (k[0], k[1], k[2], k[3], len(rows[k]), dist(rows[k])))
print("\nLab plugin hooks fire once per Bash call: PreToolUse:Bash permission_guard.py, PostToolUse run_hook.py (budget); user plugin: colgrep-mcp PreToolUse:Bash colgrep_policy.py via `uv run --no-project --quiet python`.\n")

print("\n## 4. Does the classifier wait grow with the transcript? (sessions L0, L1: auto, no colgrep, no lab plugin; 5 Bash calls early, 3 Reads, 5 Bash calls late)\n")
print("| segment | calls | context tokens at the call | classifier wait ms | tool phase ms | run ms |\n|:--|--:|:--|:--|:--|:--|")
Ls = [c for c in calls if c["label"][0] == "L" and c["tool"] == "Bash"]
for name, sel in (("early (calls 1-5; call 1 = shell start)", lambda c: c["n_in_run"] <= 5), ("early without call 1", lambda c: 2 <= c["n_in_run"] <= 5), ("late (calls 9-13)", lambda c: c["n_in_run"] >= 9)):
    cs = [c for c in Ls if sel(c)]
    print("| %s | %d | %d-%d | %s | %s | %s |" % (name, len(cs), min(c["ctx_tokens"] for c in cs), max(c["ctx_tokens"] for c in cs), dist([c["perm_ms"] for c in cs]), dist([c["phase_ms"] for c in cs]), dist([c["run_ms"] for c in cs])))
print("\nPer session and call (L0, L1): n_in_run, ctx tokens, classifier ms, phase ms\n")
for l in ("L0", "L1"):
    print(l + ": " + "; ".join("%d: %dk %d %d" % (c["n_in_run"], c["ctx_tokens"] // 1000, c["perm_ms"], c["phase_ms"]) for c in Ls if c["label"] == l))
print("\nReads in L0, L1 (tool, ctx, phase ms): " + "; ".join("%s %dk %d" % (c["label"], c["ctx_tokens"] // 1000, c["phase_ms"]) for c in calls if c["label"][0] == "L" and c["tool"] == "Read"))

print("\n## 5. The same four files read four ways (auto, colgrep off, no lab plugin; one session each)\n")
print("| variant | sessions' wall duration_ms | prompt to last assistant record s | first tool_use to last result s | main API requests | side queries | tool calls | classifier-decided | sum of classifier waits ms | per-call tool phase ms |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|")
names = {"W1": "1 Bash, four `cat`s chained", "W2": "4 Bash calls in one message", "W3": "4 Reads in one message", "W4": "4 Reads, one per message"}
for w in ("W1", "W2", "W3", "W4"):
    s = [x for x in sess if x["label"] == w][0]
    cs = [c for c in calls if c["label"] == w]
    print("| %s %s | %d | %s | %s | %d | %d | %d | %d | %d | %s |" % (w, names[w], s["duration_ms"], s["prompt_to_last_assistant_s"], s["first_call_to_last_result_s"], s["main_requests"], s["side_queries"], s["n_calls"], s["n_classifier_results"],
                                                                sum(c["perm_ms"] for c in cs), ", ".join("%d" % c["phase_ms"] for c in cs)))

print("\n## 6. Sessions: cost, requests, load average\n")
print("| label | arm | duration_ms | api_ms | main requests | side queries | calls | USD | load1 before | load1 after |\n|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|")
for s in sess:
    la = load.get(s["label"], (0, 0, 0, 0))
    print("| %s | %s | %d | %d | %d | %d | %d | %.4f | %.2f | %.2f |" % (s["label"], "%s/%s/%s" % (s["mode"], s["colgrep"], s["plugin"]), s["duration_ms"], s["api_ms"], s["main_requests"], s["side_queries"], s["n_calls"], s["cost"], la[0], la[1]))
