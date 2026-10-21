# w06-c13: re-counts k6 (false denials over the lab's own recorded calls) for a revision of scripts/permission_guard.py under reproducer-w06-7's labels; inputs: the guard file, the four lab project folders under ~/.claude/projects, __reports__/wave-06/reproducer-w06-7/k6_classification.tsv (label a = only mentions the words, b = an act the guard is for, c = other; matched by session and the first 60 non-blank characters of the call); outputs: totals, the labelled counts, and the denied calls with no label (new calls since the labelling, or calls this revision denies and the old one did not) on stdout, command text cut at 160 characters. Usage: python3 -I __instrumenta__/w06c13_k6_recount.py <guard.py> [--list-unlabelled]
import collections, glob, importlib.util, json, os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = importlib.util.spec_from_file_location("pg", sys.argv[1])
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
norm = lambda s: re.sub(r"\s+", "", s.replace("⏎", ""))[:60]
labels = {}
for line in open(REPO + "/__reports__/wave-06/reproducer-w06-7/k6_classification.tsv"):
    if line.startswith("#") or line.startswith("idx\t"):
        continue
    f = line.rstrip("\n").split("\t")
    if len(f) >= 6:
        labels.setdefault((f[1], f[2], norm(f[5])), []).append(f[4])
P = os.path.expanduser("~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration")
folders = [P + s for s in ("-blissful-villani-34edd8", "-lab-system-optimization-1aa673", "-murmuration-system-optimization-8cff9e", "-murmuration-wave-4-3417be")]
cnt, lab, unl, seen = collections.Counter(), collections.Counter(), [], set()
for folder in folders:
    for fn in glob.glob(folder + "/**/*.jsonl", recursive=True):
        sess = os.path.basename(fn)[:8]
        for line in open(fn, errors="replace"):
            if '"tool_use"' not in line:
                continue
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if m.get("type") != "assistant":
                continue
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") not in ("Bash", "Write", "Edit", "MultiEdit") or b.get("id") in seen:
                    continue
                seen.add(b.get("id"))
                cnt[b["name"]] += 1
                try:
                    r = G.decide(dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or ""))
                except Exception as e:
                    r = ("EXC", repr(e))
                if r and b["name"] == "Bash":
                    cmd = str(b["input"].get("command"))
                    lbs = labels.get((sess, str(m.get("timestamp", ""))[:16], norm(cmd)))
                    lb = lbs.pop(0) if lbs else None
                    cnt["denied_Bash"] += 1
                    if lb:
                        lab[lb] += 1
                    else:
                        unl.append((r[0], sess, cmd[:160].replace("\n", " ")))
                elif r:
                    cnt["denied_" + b["name"]] += 1
a, c = lab["a"], lab["c"]
print("calls %s" % dict(cnt))
print("denied Bash %d: labelled %s, unlabelled %d" % (cnt["denied_Bash"], dict(lab), len(unl)))
print("false denials, strict (label a + every unlabelled counted as false): %d; broad (a + c + unlabelled): %d; limit 55" % (a + len(unl), a + c + len(unl)))
print("labels in the tsv: %d; labelled calls no longer denied: %d" % (sum(len(v) + 0 for v in labels.values()) + sum(lab.values()), sum(len(v) + 0 for v in labels.values())))
if "--list-unlabelled" in sys.argv:
    for u in unl:
        print(*u, sep=" | ")
