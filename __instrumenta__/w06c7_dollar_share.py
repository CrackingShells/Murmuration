# w06-c7 (g4 side estimate): the share of Bash tool calls in this lab's Claude Code transcripts whose command carries a shell expansion the `if` matcher cannot resolve (`$(`, backtick, `$NAME` other than $HOME), per project folder and pooled, from ~/.claude/projects/*urmuration* transcripts (main and subagent files); inputs: the transcripts; outputs: one line per folder with more than 300 Bash calls, a pooled line over all folders, and a pooled line over the lab-session folders only (those under claude-worktrees); no command text is printed. Corrected after reproducer-w06-5: the pooled figure of 17.7 percent included about 1,900 headless probe sessions with short commands (3 to 4 percent), the lab sessions themselves are near 45 percent.
import glob, json, os, re

pat = re.compile(r"\$\(|`|\$[A-Za-z_{]")
tot = {"all": [0, 0], "lab": [0, 0]}
for d in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*urmuration*"))):
    n = k = 0
    for fn in glob.glob(d + "/**/*.jsonl", recursive=True):
        for line in open(fn, errors="replace"):
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
                    k += bool(pat.search(cmd.replace("$HOME", "")))
    lab = "claude-worktrees" in d and "scratch" not in d and "work" != d[-4:]
    tot["all"][0] += n; tot["all"][1] += k
    if lab:
        tot["lab"][0] += n; tot["lab"][1] += k
    if n > 300:
        print("%-95s %s bash %5d share %.3f" % (os.path.basename(d)[-95:], "LAB" if lab else "   ", n, k / n))
for key, (n, k) in tot.items():
    print("pooled %-4s bash %5d with expansion %5d share %.3f" % (key, n, k, k / max(n, 1)))
