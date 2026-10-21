# Replay lab Bash calls through a guard's decide(); input: guard path, out json, project folders; output: JSON list of the denied Bash calls in full (id, group, why, cwd, session, command) -- data stays under /private/tmp, never committed
import glob, importlib.util, json, os, sys
guard, out = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("pg", guard); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
seen, res, nb = set(), [], 0
for folder in sys.argv[3:]:
    for f in sorted(glob.glob(folder + "/**/*.jsonl", recursive=True)):
        for ln, line in enumerate(open(f, errors="replace")):
            if '"tool_use"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") != "Bash": continue
                if b["id"] in seen: continue
                seen.add(b["id"]); nb += 1
                r = G.decide(dict(tool_name="Bash", tool_input=b["input"], cwd=m.get("cwd") or ""))
                if r: res.append(dict(id=b["id"], group=r[0], why=r[1], cwd=m.get("cwd"), session=os.path.basename(f)[:8], file=f, line=ln, ts=m.get("timestamp"), command=b["input"].get("command") or ""))
json.dump(res, open(out, "w"), indent=1)
print(nb, len(res))
