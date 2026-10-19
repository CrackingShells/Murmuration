#!/usr/bin/env python3
"""Timeline of one end-to-end cell: for the worker's transcript, each hook message it received (SubagentStart, PostToolBatch, blocking errors),
the number of tool calls before it, what the worker did next (its next text and its next tool call), the coordinator's messages, the hand-backs; and the hook log.
usage: e2e_analyze.py <scratch> <cell>      Stdlib only."""
import glob, json, os, sys
S, cell = os.path.abspath(sys.argv[1]), sys.argv[2]
base = os.path.join(S, "runs", cell); meta = json.load(open(os.path.join(base, "meta.json")))
tx = glob.glob(os.path.expanduser("~/.claude/projects/*-runs-%s-lab/%s/subagents/agent-*.jsonl" % (cell, meta["session"])))
tx = [t for t in tx if not t.endswith("meta.json")]
assert tx, "no subagent transcript"
calls, n_req, pending = 0, set(), []
out = []
for l in open(tx[0]):
    r = json.loads(l); t = r.get("type"); m = r.get("message") or {}
    if t == "attachment":
        a = r["attachment"]
        if a.get("type") in ("hook_additional_context", "hook_blocking_error", "hook_stopped_continuation"):
            txt = a.get("content") if a["type"] == "hook_additional_context" else json.dumps(a.get("blockingError") or a.get("message"))
            txt = " ".join(txt) if isinstance(txt, list) else str(txt)
            ev = {"type": a["type"], "event": a.get("hookEvent"), "calls_before": calls, "text": txt}
            out.append(ev); pending.append(ev)
    elif t == "assistant":
        for b in m.get("content") or []:
            if b.get("type") == "tool_use":
                calls += 1
                for ev in pending:
                    if "next" not in ev:
                        ev["next"] = "%s %s" % (b["name"], json.dumps(b["input"])[:140])
            elif b.get("type") == "text" and b.get("text", "").strip():
                for ev in pending:
                    ev.setdefault("then_said", b["text"][:300].replace("\n", " "))
                if len(b["text"]) > 400: out.append({"type": "assistant_text", "calls_before": calls, "text": b["text"][:200]})
    elif t == "user" and (r.get("origin") or {}).get("kind") == "coordinator":
        out.append({"type": "coordinator_message", "calls_before": calls, "text": str(m.get("content"))[:200].replace("\n", " | ")})
    if t == "assistant":
        for b in m.get("content") or []:
            if b.get("type") == "tool_use" and b["name"] == "SubagentHandback":
                out.append({"type": "hand-back", "calls_before": calls, "text": b["input"].get("message", "")[:700].replace("\n", " | ")})
for ev in out:
    print(json.dumps(ev, ensure_ascii=False))
print("total tool calls:", calls)
