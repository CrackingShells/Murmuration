"""Counts Bash-call practice in Claude Code transcripts: reads <dir>/*.jsonl (worker transcripts), prints a table; own code, independent of the author's.
usage: python3 -I count_bash.py <subagents dir> [--exclude w03] [--main <main.jsonl>]  -> table on stdout, per-worker rows with --rows"""
import glob, json, os, re, sys

def calls(path):
    seen = {}
    with open(path) as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            m = r.get("message") or {}
            c = m.get("content")
            if r.get("type") != "assistant" or not isinstance(c, list):
                continue
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    seen[b["id"]] = b
    return list(seen.values())

def name_of(path):
    with open(path) as fh:
        r = json.loads(fh.readline())
    c = r["message"]["content"]
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    m = re.search(r"[Yy]our name is ([a-z0-9-]+)", c)
    return m.group(1) if m else os.path.basename(path)

def strip_heredoc_bodies(cmd):
    # remove bodies of << 'EOF' ... EOF so that words inside text do not count as commands
    return re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", "<<\\1", cmd, flags=re.S)

SEARCH = re.compile(r"(^|[|;&(\s])(grep|rg|egrep|fgrep|find|fd|ag|ack)(\s|$)")
WALK = re.compile(r"glob|os\.walk|listdir|rglob|scandir|iterdir|\.walk\(")
def classify(cmd):
    out = {"bash": 1}
    heredoc = "<<" in cmd
    out["heredoc"] = int(heredoc)
    body = strip_heredoc_bodies(cmd)
    if heredoc:
        py = re.search(r"\bpython3?\b(\s+-\w+)*\s*(-\s*)?<<", cmd) is not None or re.search(r"\bpython3?\b[^\n|;]*<<", cmd) is not None
        wr = re.search(r"(cat|tee)\b[^\n<]*>>?\s*\S+\s*<<|<<[^\n]*>>?\s*\S+", cmd) is not None
        app = re.search(r">>", cmd.split("\n")[0]) is not None
        out["h_py"] = int(py)
        out["h_append"] = int(app and not py)
        out["h_write"] = int(wr and not app and not py)
        out["h_other"] = int(not (py or app or wr))
        out["py_walk"] = int(py and WALK.search(cmd) is not None)
    out["shell_search"] = int(SEARCH.search(body) is not None)
    out["chars"] = len(cmd)
    out["heredoc_chars"] = len(cmd) if heredoc else 0
    return out

def tally(paths):
    t = {}
    def add(k, v=1):
        t[k] = t.get(k, 0) + v
    for p in paths:
        for b in calls(p):
            n = b["name"]
            inp = b.get("input") or {}
            add("tool_calls")
            if n == "Bash":
                for k, v in classify(inp.get("command", "")).items():
                    add(k, v)
            elif n == "Write":
                add("write")
                fp = inp.get("file_path", "")
                if fp.endswith(".py"):
                    add("write_py")
                if "__instrumenta__/" in fp:
                    add("write_instr")
                add("write_chars", len(inp.get("content", "")))
            elif n in ("Glob", "Grep"):
                add(n.lower())
            elif "colgrep" in n and n.split("__")[-1] in ("search", "find_files"):
                add("colgrep_" + n.split("__")[-1])
    return t

if __name__ == "__main__":
    d = sys.argv[1]
    ex = sys.argv[sys.argv.index("--exclude") + 1] if "--exclude" in sys.argv else None
    files = sorted(glob.glob(os.path.join(d, "*.jsonl")))
    sel = [f for f in files if not (ex and ex in name_of(f))]
    if "--main" in sys.argv:
        sel.append(sys.argv[sys.argv.index("--main") + 1])
    t = tally(sel)
    print("workers", len(sel))
    for k in sorted(t):
        print("%-16s %d" % (k, t[k]))
    if t.get("bash"):
        print("heredoc share of Bash calls %.3f" % (t.get("heredoc", 0) / t["bash"]))
    if "--rows" in sys.argv:
        for f in sel:
            print(name_of(f), tally([f]).get("bash", 0))
