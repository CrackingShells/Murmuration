# w08-c10: times the guard (python script started as the hook starts it, and the Rust binary) on long inputs, on two checkouts (base, branch), and prints a table: input, size, decision and seconds per checkout and implementation; inputs: --base DIR, --branch DIR (checkouts with scripts/permission_guard.py and bin/<target>/murmuration, or --rust-base/--rust-branch BIN); output: stdout markdown table (+ --out JSON).
# The inputs are generated (seeded text, no files read): heredoc prose with bare `$(` mentions and apostrophes (30 KB/389 mentions, 78 KB/52, 200 KB), a 200 KB script body, `python3 -c write` + a long word (30 KB, 100 KB), nested `$(` to depth k, k unmatched `$(`. Each timing is the median of --reps runs (default 3); a run over --limit seconds is cut off and shown as `>limit`.
# usage: python3 -I w08_c10_timing.py --base DIR --branch DIR [--reps 3] [--limit 60] [--only SUBSTR] [--out FILE]
import argparse, json, os, platform, random, statistics, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--base", required=True)
ap.add_argument("--branch", required=True)
ap.add_argument("--reps", type=int, default=3)
ap.add_argument("--limit", type=float, default=60)
ap.add_argument("--only", default="")
ap.add_argument("--out")
a = ap.parse_args()
arch = "aarch64" if platform.machine() in ("arm64", "aarch64") else platform.machine()


def prose(n_bytes, mentions, seed):
    r = random.Random(seed)
    words = "the splitter closes quote after here it's odd don't we use form read guard flag segment inert cat file".split()
    lines, size, per = [], 0, max(1, n_bytes // max(mentions, 1))
    out, since = [], 0
    while size < n_bytes:
        line = " ".join(r.choice(words) for _ in range(r.randint(6, 14)))
        if since >= per and mentions > 0:
            line += " $( is cut"      # a bare mention: no closing parenthesis follows on the line
            mentions -= 1
            since = 0
        out.append(line)
        size += len(line) + 1
        since += len(line) + 1
    return "cat > note.md <<'EOF'\n" + "\n".join(out) + "\nEOF\n"


def script_body(n_bytes):
    block = "def f(x):\n    return [y for y in x if y]  # it's fine\n\nprint(f([1, 2, 3]))\nvalue = os.popen('echo $(date)').read()\n"
    return "cat > tool.py <<'EOF'\n" + block * (n_bytes // len(block)) + "EOF\n"


INPUTS = [
    ("heredoc prose 30 KB, 389 bare `$(`", prose(30000, 389, 1)),
    ("heredoc prose 78 KB, 52 bare `$(`", prose(78000, 52, 2)),
    ("heredoc prose 200 KB, 800 bare `$(`", prose(200000, 800, 3)),
    ("heredoc script body 200 KB", script_body(200000)),
    ("python3 -c write + 30 KB word", "python3 -c write " + "a" * 30000),
    ("python3 -c write + 100 KB word", "python3 -c write " + "a" * 100000),
    ("30,000 unmatched `$(`", "echo " + "$(" * 30000),
    ("nested `$(` depth 100", "echo " + "$(" * 100 + "x" + ")" * 100),
    ("nested `$(` depth 1000", "echo " + "$(" * 1000 + "x" + ")" * 1000),
    ("nested `$(` depth 2500", "echo " + "$(" * 2500 + "x" + ")" * 2500),
    ("nested `$(` depth 3500", "echo " + "$(" * 3500 + "x" + ")" * 3500),
    ("30,000 matched `$(echo a)`", "echo " + "$(echo a) " * 30000),
]


def run(cmd_argv, payload):
    t = time.perf_counter()
    try:
        p = subprocess.run(cmd_argv, input=payload, capture_output=True, timeout=a.limit)
    except subprocess.TimeoutExpired:
        return None, None
    return time.perf_counter() - t, p.stdout.decode("utf-8", "replace")


def decision(out):
    if out is None:
        return "-"
    if not out:
        return "allow"
    return "deny " + (out.split("permission_guard (")[1][:2] if "permission_guard (" in out else "?")


rows = []
for name, cmd in INPUTS:
    if a.only not in name:
        continue
    payload = json.dumps(dict(tool_name="Bash", tool_input={"command": cmd}, cwd="/h/proj")).encode()
    row = dict(input=name, chars=len(cmd))
    for tag, d in (("base", a.base), ("branch", a.branch)):
        for impl, argv in (("py", [sys.executable, "-S", "-I", os.path.join(d, "scripts", "permission_guard.py")]), ("rs", [os.path.join(d, "bin", "%s-apple-darwin" % arch, "murmuration"), "guard"])):
            ts, out = [], None
            for _ in range(a.reps if impl == "rs" or True else 1):
                t, o = run(argv, payload)
                if t is None:
                    ts = None
                    break
                ts.append(t)
                out = o
            row["%s_%s" % (tag, impl)] = (decision(out) if ts else "cut off", None if ts is None else round(statistics.median(ts), 2))
            if ts is None:
                break
    rows.append(row)
    print("| %s | %d | %s |" % (name, len(cmd), " | ".join("%s %s" % (row.get(k, ("", ""))[0], (">%g" % a.limit) if row.get(k, ("", 0))[1] is None else "%.2f s" % row[k][1]) if k in row else "" for k in ("base_py", "base_rs", "branch_py", "branch_rs"))), flush=True)
if a.out:
    json.dump(rows, open(a.out, "w"), indent=1)
