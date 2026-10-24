# w09-a: assigns each call of calls.jsonl (from w09a_collect.py) a decider class and an auto-mode flag, writes classified.jsonl and prints count tables (decider x tool, x month, x project group, x mode). Usage: python3 -I w09a_classify.py IN_DIR [tables.md]
import json, re, sys, collections, os

REASON = re.compile(r"Reason: (.*?)\. If you have other tasks")


def project_group(p):
    if "urmuration" in p:
        if p.startswith("-private-tmp") or "-runs-" in p or "scratchpad" in p or "-tmp-murmuration-" in p:
            return "murmuration-arena"
        return "murmuration-lab"
    q = p
    q = re.sub(r"^-Users-hacker-Documents-tmp-claude-worktrees-", "wt:", q)
    q = re.sub(r"--claude-worktrees-.*$", "", q)
    q = re.sub(r"^-Users-hacker-Documents-", "", q)
    q = re.sub(r"^-Users-hacker-", "", q)
    if q.startswith("wt:"):
        # worktree: base project is the leading token(s) before the branch slug; keep first two tokens
        q = "wt:" + "-".join(q[3:].split("-")[:2])
    if q.startswith("-private-tmp") or q.startswith("private-tmp"):
        return "other-tmp"
    return q[:48]


def decider(c):
    r = c.get("res")
    if not r:
        return "no_result"
    pd, kind, txt = r.get("pd") or {}, r.get("kind"), r.get("text") or ""
    rt, dec, src = pd.get("reasonType"), pd.get("decision"), pd.get("source")
    if kind == "automode-blocked" or pd.get("reasonCode") == "classifier:auto-mode":
        return "classifier_block"
    if kind == "automode-unavailable" or "unavailable" in str(pd.get("reasonCode")):
        return "classifier_unavailable"
    if rt == "classifier" and dec == "accept":
        return "classifier_allow"
    if rt == "classifier":
        return "classifier_other"
    if kind == "user-rejected" or src in ("user_reject", "user_abort"):
        return "user_reject"
    if kind == "cancelled":
        return "cancelled"
    if kind == "interrupted":
        return "interrupted_by_safety_classifier" if "safety classifier" in txt else "interrupted"
    if kind == "permission-rule" or dec == "reject":
        if src == "hook" or txt.startswith("Error: PreToolUse") or "hook error" in txt[:80]:
            return "hook_reject"
        if rt == "safetyCheck" or "built-in Claude Code safety check" in txt:
            return "safetycheck_reject"
        if rt == "mode" or "don't ask mode" in txt:
            return "dontask_reject"
        return "rule_reject"
    if src in ("user_temporary", "user_permanent") and rt != "rule":
        return "user_accept"
    if src == "hook":
        return "hook_accept"
    if dec == "accept":
        return {"rule": "rule_accept", "mode": "mode_accept", "subcommandResults": "subcommand_accept", "other": "other_accept"}.get(rt, "accept_unlabelled")
    if txt.startswith("Error: PreToolUse") or "hook error" in txt[:80]:
        return "hook_reject"
    return "no_decision_record"


def tool_family(t):
    if t in ("Bash", "Write", "Edit", "MultiEdit", "NotebookEdit", "WebFetch", "WebSearch", "Read", "Glob", "Grep", "Agent", "Task"):
        return t
    if t and t.startswith("mcp__"):
        return "MCP"
    return "other"


def main(d, tables=None):
    out = open(os.path.join(d, "classified.jsonl"), "w")
    T = collections.Counter()
    by_tool, by_month, by_proj, by_mode = (collections.defaultdict(collections.Counter) for _ in range(4))
    blocks_reason = collections.Counter()
    for line in open(os.path.join(d, "calls.jsonl")):
        c = json.loads(line)
        dk = decider(c)
        c["decider"] = dk
        c["tool_family"] = tool_family(c["tool"])
        c["pgroup"] = project_group(c["project"])
        c["month"] = (c.get("ts") or "")[:7]
        c["auto"] = (c.get("mode") == "auto") or bool(c.get("auto_att")) or dk.startswith("classifier")
        if dk == "classifier_block":
            m = REASON.search(c["res"]["text"])
            c["reason"] = m.group(1) if m else None
            blocks_reason[c["reason"]] += 1
        out.write(json.dumps(c) + "\n")
        T[dk] += 1
        by_tool[dk][c["tool_family"]] += 1
        by_month[dk][c["month"]] += 1
        by_proj[dk][c["pgroup"]] += 1
        by_mode[dk][str(c.get("mode")) + ("|att" if c.get("auto_att") else "")] += 1
    out.close()
    L = []
    P = lambda *a: L.append(" ".join(str(x) for x in a))
    P("## decider totals (unique tool_use ids)")
    for k, v in T.most_common():
        P("-", k, v)
    P("\n## by tool family (rows decider)")
    tools = sorted({t for c in by_tool.values() for t in c})
    P("| decider | " + " | ".join(tools) + " |")
    P("|:--|" + "--:|" * len(tools))
    for k, _ in T.most_common():
        P("|", k, "|", " | ".join(str(by_tool[k].get(t, 0)) for t in tools), "|")
    P("\n## by month")
    months = sorted({t for c in by_month.values() for t in c})
    P("| decider | " + " | ".join(months) + " |")
    P("|:--|" + "--:|" * len(months))
    for k, _ in T.most_common():
        P("|", k, "|", " | ".join(str(by_month[k].get(t, 0)) for t in months), "|")
    P("\n## by permissionMode seen before the call (|att = auto_mode attachment seen)")
    modes = sorted({t for c in by_mode.values() for t in c})
    P("| decider | " + " | ".join(modes) + " |")
    P("|:--|" + "--:|" * len(modes))
    for k, _ in T.most_common():
        P("|", k, "|", " | ".join(str(by_mode[k].get(t, 0)) for t in modes), "|")
    P("\n## project groups, classifier_allow / classifier_block / classifier_unavailable")
    pg = collections.Counter()
    for k in ("classifier_allow", "classifier_block", "classifier_unavailable"):
        for p, v in by_proj[k].items():
            pg[p] += v
    P("| project group | allow | block | unavailable |")
    P("|:--|--:|--:|--:|")
    for p, _ in pg.most_common():
        P("|", p, "|", by_proj["classifier_allow"].get(p, 0), "|", by_proj["classifier_block"].get(p, 0), "|", by_proj["classifier_unavailable"].get(p, 0), "|")
    P("\n## classifier block reasons")
    for k, v in blocks_reason.most_common():
        P("-", k, v)
    txt = "\n".join(L)
    print(txt)
    if tables:
        open(tables, "w").write(txt + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
