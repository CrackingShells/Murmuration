"""Run a set of cells (parallel 4) then analyse them.
usage: python3 -I matrix.py <set> [--quick]
Sets: ablation  (flag-by-flag from a plain headless run toward the Desktop launch line, both binaries)
      modes     (foreground/background x short/long x thinking, on the Desktop-like line)
      repeat    (the full Desktop-like line, 3 repeats per binary)
"""
import subprocess, sys, os, itertools, json
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
DESK = dict(io="sdk", partial="1", thinkdisp="omitted", effort="high", auto="1")


def name(bn, c):
    if "permmode" in c:
        return "%s-pm-%s-%s-%s" % (bn[:3] if bn == "desktop" else "ins", c["permmode"], c.get("mode", "fg"), c.get("rep", "0"))
    return "%s-%s-%s-%s-%s-%s-p%s-%s-%s-%s" % (bn[:3] if bn == "desktop" else "ins", c.get("mode", "fg"), c.get("think", "on"),
        c.get("length", "long"), c.get("io", "p"), c.get("env", "inh"), c.get("partial", "0"), c.get("thinkdisp", "dflt")[:3],
        c.get("effort", "dflt")[:3], c.get("auto", "0"))


def cells(setname):
    out = []
    if setname == "ablation":
        variants = [{}, dict(partial="1"), dict(thinkdisp="omitted"), dict(io="sdk"), dict(effort="high"), dict(auto="1"), DESK]
        for bn in ("desktop", "installed"):
            for v in variants:
                out.append((bn, v))
    elif setname == "repeat":
        for bn in ("desktop", "installed"):
            for i in range(3):
                out.append((bn, dict(DESK, rep=str(i))))
    elif setname == "modes":   # permission mode auto vs bypass, crossed with fg/bg, thinking, length; plain `-p` io
        for bn in ("desktop", "installed"):
            for auto, mode, think, length in itertools.product(("0", "1"), ("fg", "bg"), ("on", "off"), ("short", "long")):
                out.append((bn, dict(auto=auto, mode=mode, think=think, length=length)))
    elif setname == "perm":    # every permission mode
        for bn in ("desktop", "installed"):
            for pm in ("default", "acceptEdits", "dontAsk", "plan", "auto", "bypassPermissions"):
                out.append((bn, dict(permmode=pm)))
    elif setname == "settle":   # polling hook: how long until the subagent file is final?  (tag pk)
        for bn in ("desktop", "installed"):
            for i in range(12): out.append((bn, dict(rep=str(i), tag="pk", poll="1")))
            for i in range(10): out.append((bn, dict(rep=str(i), tag="pk", poll="1", mode="bg", think="off", length="short")))
            for i in range(4): out.append((bn, dict(rep=str(i), tag="pk", poll="1", permmode="plan")))
            for i in range(3): out.append((bn, dict(rep=str(i), tag="pk", poll="1", permmode="auto")))
    elif setname == "bgcheck":  # separate background from short final message, bypass mode, no polling hook (tag bc)
        for bn in ("desktop", "installed"):
            for i in range(10): out.append((bn, dict(rep=str(i), tag="bc", mode="bg", think="on", length="long")))
            for i in range(10): out.append((bn, dict(rep=str(i), tag="bc", mode="fg", think="off", length="short")))
            for i in range(10): out.append((bn, dict(rep=str(i), tag="bc", mode="bg", think="off", length="long")))
    elif setname == "hookrace":  # SubagentStop timing: 10 repeats per binary, non-auto, fg, long
        for bn in ("desktop", "installed"):
            for i in range(10):
                out.append((bn, dict(rep=str(i), tag="hr")))
    return out


def run(item):
    bn, c = item
    cn = name(bn, c) + ("-r" + c["rep"] if ("rep" in c and "permmode" not in c) else "") + ("-" + c["tag"] if c.get("tag") else "")
    args = [sys.executable, "-I", os.path.join(HERE, "run_cell.py"), cn, "--bin", bn]
    for k, v in c.items():
        if k not in ("rep", "tag"):
            args += ["--" + k, v]
    r = subprocess.run(args, capture_output=True, text=True)
    return cn, r.stdout.strip() + r.stderr.strip()[-300:]


if __name__ == "__main__":
    cs = cells(sys.argv[1])
    if "--quick" in sys.argv:
        cs = cs[:2]
    with ThreadPoolExecutor(4) as ex:
        names = []
        for cn, msg in ex.map(run, cs):
            print(msg, flush=True)
            names.append(cn)
    for cn in names:
        try:
            subprocess.run([sys.executable, "-I", os.path.join(HERE, "analyze_cell.py"), cn], capture_output=True, check=True)
        except Exception as e:
            print("analyze failed", cn, e)
