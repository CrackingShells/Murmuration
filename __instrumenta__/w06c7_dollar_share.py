# w06-c7 (g4 side estimate): the share of Bash tool calls in this lab's Claude Code transcripts whose command carries a shell expansion the `if` matcher cannot resolve (`$(`, backtick, `$NAME` other than $HOME), from ~/.claude/projects/*Murmuration* transcripts (main and subagent files); inputs: the transcripts; outputs: counts and the share on stdout (no command text is printed).
import glob, json, os, re, sys

pat = re.compile(r"\$\(|`|\$[A-Za-z_{]")
n = d = 0
files = glob.glob(os.path.expanduser("~/.claude/projects/*urmuration*/**/*.jsonl"), recursive=True)
for f in files:
    for line in open(f, errors="replace"):
        if '"name":"Bash"' not in line:
            continue
        try:
            m = json.loads(line)
        except ValueError:
            continue
        c = m.get("message", {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if b.get("type") == "tool_use" and b.get("name") == "Bash":
                cmd = (b.get("input") or {}).get("command", "")
                n += 1
                d += bool(pat.search(cmd.replace("$HOME", "")))
print("files %d  Bash calls %d  with an unresolved expansion %d  share %.3f" % (len(files), n, d, d / max(n, 1)))
