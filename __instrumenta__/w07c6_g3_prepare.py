# Builds the g3 bench inputs for w07-c6: N recorded Bash payloads (sampled with a fixed seed from the lab's recorded Bash calls) as stdin files, the payload list, and the arms file for the two guards; inputs: output folder, N, seed, the Rust binary path, the Python guard path, the python3 to use; outputs: <out>/payloads/pNNN.json, <out>/payloads.txt, <out>/arms.tsv, <out>/payload_sizes.tsv.
# usage: python3 -I __instrumenta__/w07c6_g3_prepare.py OUT N SEED RUST_BIN PY_GUARD PYTHON3
import glob, json, os, random, sys
out, n, seed, rust, guard, py = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
os.makedirs(out + "/payloads", exist_ok=True)
rec, seen = [], set()
for folder in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*Murmuration*"))):
    for f in sorted(glob.glob(folder + "/**/*.jsonl", recursive=True)):
        for line in open(f, errors="replace"):
            if '"tool_use"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash" and b["id"] not in seen:
                    seen.add(b["id"]); rec.append(dict(tool_name="Bash", tool_input=b["input"], cwd=m.get("cwd") or ""))
random.Random(seed).shuffle(rec)
sizes = []
with open(out + "/payloads.txt", "w") as pl:
    for i, e in enumerate(rec[:n]):
        p = "%s/payloads/p%03d.json" % (out, i)
        s = json.dumps(e)
        open(p, "w").write(s); pl.write(p + "\n"); sizes.append((i, len(s)))
open(out + "/payload_sizes.tsv", "w").write("".join("%d\t%d\n" % x for x in sizes))
open(out + "/arms.tsv", "w").write("A\t%s\t-S\t-I\t%s\nB\t%s\tguard\n" % (py, guard, rust))
print("recorded Bash calls:", len(rec), "sampled", min(n, len(rec)), "median payload bytes", sorted(s for _, s in sizes)[len(sizes) // 2])
