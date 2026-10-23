# w08-j: collects every Bash/Write/Edit/MultiEdit/NotebookEdit tool call from the Murmuration session transcripts (~/.claude/projects/*urmuration*, subagents included) with its live guard answer (a tool result starting "PreToolUse:<Tool> hook error: permission_guard (G"); input: the transcript folders; output: one JSON line per unique tool_use id (stratum lab or arena) to the path in argv[1], and counts on stdout (a scratch file, never committed: it holds command text and cwd). Usage: python3 -I w08j_collect_calls.py OUT.jsonl
import glob, json, os, re, sys, collections

B = os.path.expanduser("~/.claude/projects/")
LAB = ("-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-blissful-villani-34edd8",
       "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-lab-system-optimization-1aa673",
       "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e",
       "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be",
       "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-8-928ebd",
       "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-xenodochial-franklin-bc67fb")
TOOLS = ("Bash", "Write", "Edit", "MultiEdit", "NotebookEdit")
DENY = re.compile(r"^PreToolUse:(\w+) hook error: permission_guard \((G.)\): (.*)", re.S)


def text_of(c):
    if isinstance(c, list):
        c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


def main(out):
    calls, order = {}, []
    folders = [d for d in sorted(os.listdir(B)) if "urmuration" in d]
    nfiles = 0
    for d in folders:
        stratum = "lab" if d in LAB else "arena"
        for f in sorted(glob.glob(B + d + "/**/*.jsonl", recursive=True)):
            nfiles += 1
            for line in open(f, errors="replace"):
                if '"tool_use"' not in line and '"tool_result"' not in line:
                    continue
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                cont = (m.get("message") or {}).get("content")
                if not isinstance(cont, list):
                    continue
                for b in cont:
                    if not isinstance(b, dict):
                        continue
                    if m.get("type") == "assistant" and b.get("type") == "tool_use" and b.get("name") in TOOLS:
                        if b["id"] not in calls:
                            calls[b["id"]] = dict(id=b["id"], stratum=stratum, folder=d[-30:], session=os.path.basename(f)[:8], ts=m.get("timestamp"),
                                                  tool=b["name"], input=b["input"], cwd=m.get("cwd") or "", live=None, live_msg=None)
                            order.append(b["id"])
                    elif m.get("type") == "user" and b.get("type") == "tool_result":
                        t = text_of(b.get("content"))
                        mm = DENY.match(t)
                        c = calls.get(b.get("tool_use_id"))
                        if mm and c is not None and c["live"] is None:
                            c["live"], c["live_msg"] = mm.group(2), mm.group(3)[:200]
                        elif mm:
                            calls.setdefault("orphan:" + b.get("tool_use_id", ""), dict(id=b.get("tool_use_id"), orphan=True, live=mm.group(2)))
    cnt = collections.Counter()
    with open(out, "w") as fh:
        for i in order:
            c = calls[i]
            cnt[(c["stratum"], c["tool"], c["live"])] += 1
            fh.write(json.dumps(c) + "\n")
    print("files", nfiles, "unique calls", len(order), "orphan denials", sum(1 for k in calls if k.startswith("orphan:")))
    for k, v in sorted(cnt.items(), key=str):
        print(v, k)


main(sys.argv[1])
