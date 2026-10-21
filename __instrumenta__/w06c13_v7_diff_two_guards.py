# Replay every recorded lab Bash/Write/Edit call through two guard files' decide() and list the calls whose decision differs; input: guard A, guard B, out json, project folders; output: counts, and the differing calls in full to the json (stays under /private/tmp)
import glob, importlib.util, json, os, sys
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
A, B = load(sys.argv[1], "ga"), load(sys.argv[2], "gb"); out = sys.argv[3]
seen, flips, n = set(), [], 0
for folder in sys.argv[4:]:
    for f in sorted(glob.glob(folder + "/**/*.jsonl", recursive=True)):
        for line in open(f, errors="replace"):
            if '"tool_use"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") not in ("Bash", "Write", "Edit"): continue
                if b["id"] in seen: continue
                seen.add(b["id"]); n += 1
                ev = dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or "")
                ra, rb = A.decide(ev), B.decide(ev)
                if bool(ra) != bool(rb) or (ra and rb and ra[0] != rb[0]):
                    flips.append(dict(id=b["id"], tool=b["name"], a=ra[0] if ra else None, b=rb[0] if rb else None, session=os.path.basename(f)[:8], ts=m.get("timestamp"), command=b["input"].get("command") or b["input"].get("file_path") or ""))
json.dump(flips, open(out, "w"), indent=1); print(n, "calls;", len(flips), "differ")
for x in flips: print(x["a"], "->", x["b"], x["session"], x["ts"][5:16], x["command"][:140].replace("\n", " ⏎ "))
