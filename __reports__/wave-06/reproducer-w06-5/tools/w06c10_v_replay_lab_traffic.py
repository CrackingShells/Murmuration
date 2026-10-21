# Replay every Bash, Write and Edit tool call found in the lab's own session transcripts (given project folders) through scripts/permission_guard.py's decide(); input: guard path, transcript folders; output: counts and the denied calls (first 160 chars) on stdout. Write-over-existing is judged against the file as it is now on disk (approximation).
import glob, importlib.util, json, os, sys, collections

guard = sys.argv[1]
spec = importlib.util.spec_from_file_location("pg", guard)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
cnt = collections.Counter()
denied = []
seen = set()
for folder in sys.argv[2:]:
    for f in glob.glob(folder + "/**/*.jsonl", recursive=True):
        for line in open(f, errors="replace"):
            if '"tool_use"' not in line:
                continue
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if m.get("type") != "assistant":
                continue
            cwd = m.get("cwd") or ""
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") not in ("Bash", "Write", "Edit", "MultiEdit"):
                    continue
                key = (b.get("id"))
                if key in seen:
                    continue
                seen.add(key)
                ev = dict(tool_name=b["name"], tool_input=b["input"], cwd=cwd)
                try:
                    r = G.decide(ev)
                except Exception as e:
                    r = ("EXC", repr(e))
                cnt[b["name"]] += 1
                if r:
                    cnt["denied_" + b["name"]] += 1
                    ti = b["input"]
                    denied.append((b["name"], r[0], str(ti.get("command") or ti.get("file_path"))[:200].replace("\n", " "), os.path.basename(f)[:8]))
print(dict(cnt))
for d in denied:
    print(*d, sep=" | ")
