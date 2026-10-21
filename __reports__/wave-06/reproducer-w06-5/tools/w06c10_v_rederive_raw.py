# Re-derive, for each raw headless session folder (stream.jsonl + guard.log), the tool calls, what the model saw, the PreToolUse hook starts and the guard log decisions; input: run folders (globs) as arguments; output: one block per run on stdout (independent of the author's classifier).
import glob, json, os, sys


def parse(R):
    uses, res, hooks = [], {}, []
    for line in open(R + "/stream.jsonl"):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        t = m.get("type")
        if t in ("assistant", "user"):
            c = m["message"].get("content")
            if isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_use":
                        uses.append((b["id"], b["name"], b["input"]))
                    elif b.get("type") == "tool_result":
                        x = b.get("content")
                        res[b["tool_use_id"]] = x if isinstance(x, str) else " ".join(y.get("text", "") for y in x or [])
        elif t == "system" and str(m.get("subtype", "")).startswith("hook_"):
            hooks.append((m["subtype"], m.get("hook_name"), m.get("outcome"), str(m.get("output") or m.get("stdout") or "")[:200]))
    return uses, res, hooks


def verdict(text):
    if "permission_guard (G" in text:
        return "DENIED-BY-GUARD"
    if "hook error" in text:
        return "BLOCKED-HOOK-FAILURE"
    if "STUB-RAN" in text:
        return "STUB-RAN"
    return "OTHER"


def show(R):
    uses, res, hooks = parse(R)
    pre = [h for h in hooks if h[0] == "hook_started" and (h[1] or "").startswith("PreToolUse:") and not (h[1] or "").startswith(("PreToolUse:Agent", "PreToolUse:Task"))]
    print("==", os.path.basename(R), "PreToolUse starts:", len(pre))
    for u, n, i in uses:
        if n in ("Read",):
            continue
        r = res.get(u, "")
        print("  ", n, json.dumps(i)[:150], "->", verdict(r), "|", r.replace("\n", " ")[:100])
    g = R + "/guard.log"
    if os.path.exists(g):
        print("   guard.log:", [json.loads(l)["decision"] for l in open(g) if l.strip()])


if __name__ == "__main__":
    for a in sys.argv[1:]:
        for R in sorted(glob.glob(a)):
            if os.path.exists(R + "/stream.jsonl"):
                show(R)
