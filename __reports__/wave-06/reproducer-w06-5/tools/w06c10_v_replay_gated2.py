# (v2: heredoc bodies hidden from the gate) Replay the lab's own Bash calls through the guard the way the hook rows would: the guard starts only when the command carries bypassPermissions, dangerously-skip-permissions or setting-sources (or an expansion `$`/backtick, which matches every row); input: guard path, transcript folders; output: counts (spawn-eligible, started by words, denied, denied-with-claude-segment) and the denied commands in a file given by env OUT.
import glob, importlib.util, json, os, sys, collections, re
spec = importlib.util.spec_from_file_location("pg", sys.argv[1]); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
cnt = collections.Counter(); out = []; seen = set()
for folder in sys.argv[2:]:
    for f in glob.glob(folder + "/**/*.jsonl", recursive=True):
        for line in open(f, errors="replace"):
            if '"name":"Bash"' not in line.replace('": "', '":"'): continue
            try: m = json.loads(line)
            except ValueError: continue
            if m.get("type") != "assistant": continue
            for b in (m.get("message", {}).get("content") or []):
                if not isinstance(b, dict) or b.get("type") != "tool_use" or b.get("name") != "Bash" or b["id"] in seen: continue
                seen.add(b["id"]); cmd = b["input"].get("command") or ""
                cnt["bash"] += 1
                vis = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\b", "", cmd, flags=re.S)   # heredoc bodies are not seen by an `if` rule (live: w06c10 f01, k01)
                words = bool(re.search(r"bypassPermissions|dangerously-skip-permissions|setting-sources", vis))
                exp = bool(re.search(r"\$\(|`|\$[A-Za-z_{]", vis.replace("$HOME", "")))
                if words: cnt["start_by_words"] += 1
                if exp and not words: cnt["start_by_expansion_only"] += 1
                if not (words or exp): continue
                r = G.decide(dict(tool_name="Bash", tool_input=b["input"], cwd=m.get("cwd") or ""))
                if r:
                    cnt["denied"] += 1
                    # does a simple command start `claude` ?
                    segs = G.expand(cmd)
                    runs_claude = any(os.path.basename(t[G.program(t)[0]]) == "claude" for s, t in segs if G.program(t)[0] < len(t))
                    cnt["denied_runs_claude"] += runs_claude
                    cnt["denied_no_claude_segment"] += (not runs_claude)
                    out.append(dict(group=r[0], runs_claude=runs_claude, file=os.path.basename(f)[:12], cmd=cmd[:400]))
print(dict(cnt))
json.dump(out, open(os.environ.get("OUT", "gated_denied.json"), "w"), indent=1)
