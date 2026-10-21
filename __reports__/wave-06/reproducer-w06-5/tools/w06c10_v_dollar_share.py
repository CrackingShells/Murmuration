# Share of the lab's Bash calls (given transcript folders) whose command carries an expansion the `if` matcher cannot resolve per w06-c7 (`$(`, backtick, `$NAME` other than HOME, `${`), and the share carrying a bypass trigger word; input: folders; output: counts on stdout.
import glob, json, re, sys, collections
c = collections.Counter(); seen = set()
for folder in sys.argv[1:]:
    for f in glob.glob(folder + "/**/*.jsonl", recursive=True):
        for line in open(f, errors="replace"):
            if '"Bash"' not in line: continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash" and b["id"] not in seen:
                    seen.add(b["id"]); cmd = b["input"].get("command") or ""
                    c["bash"] += 1
                    if re.search(r"\$\(|`|\$\{|\$(?!HOME\b)[A-Za-z_]", cmd): c["expansion"] += 1
                    if re.search(r"\$\(|`", cmd): c["cmdsub"] += 1
                    if re.search(r"bypassPermissions|dangerously-skip-permissions|setting-sources", cmd): c["words"] += 1
print(dict(c), "expansion share %.1f%%, cmd-substitution share %.1f%%, words share %.1f%%" % (100*c["expansion"]/c["bash"], 100*c["cmdsub"]/c["bash"], 100*c["words"]/c["bash"]))
