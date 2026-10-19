"""Extra counts over worker transcripts: py heredocs with 'glob' anywhere, output-character share of heredocs, inline python. Own code.
usage: python3 -I extra_counts.py <dir of worker jsonl> [--exclude w03] [--main file]"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import count_bash as cb
d = sys.argv[1]
ex = sys.argv[sys.argv.index("--exclude") + 1] if "--exclude" in sys.argv else None
files = [f for f in sorted(glob.glob(d + "/*.jsonl")) if not (ex and ex in cb.name_of(f))]
if "--main" in sys.argv:
    files.append(sys.argv[sys.argv.index("--main") + 1])
tot_out = heredoc_chars = 0
pyg = pywalk_any = pyc = 0
for f in files:
    seen_text = {}
    for line in open(f):
        try: r = json.loads(line)
        except ValueError: continue
        c = (r.get("message") or {}).get("content")
        if r.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "text":
                    seen_text[(r.get("message", {}).get("id"), hash(b["text"]))] = len(b["text"])
    tot_out += sum(seen_text.values())
    for b in cb.calls(f):
        inp = json.dumps(b.get("input", {}))
        tot_out += len(inp)
        if b["name"] == "Bash":
            cmd = b["input"].get("command", "")
            if "<<" in cmd:
                heredoc_chars += len(json.dumps(b["input"]))
                if re.search(r"\bpython3?\b", cmd.split("<<")[0]):
                    pyc += 1
                    if "glob" in cmd: pyg += 1
                    if cb.WALK.search(cmd): pywalk_any += 1
print("files", len(files), "output chars", tot_out, "heredoc chars", heredoc_chars, "share %.3f" % (heredoc_chars / tot_out))
print("python heredocs (python before <<)", pyc, "with 'glob'", pyg, "with any walk token", pywalk_any)
