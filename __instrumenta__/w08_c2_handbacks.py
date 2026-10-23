# Extracts, per subagent transcript of the given PI sessions, every SubagentHandback tool input and the final assistant text: role, wave, characters, whether it names a lab path; inputs: LABEL=MAIN_JSONL pairs (subagents read from <MAIN minus .jsonl>/subagents); output: one TSV row per hand-back (no text, only lengths and flags). Usage: w08_c2_handbacks.py OUT.tsv LABEL=MAIN_JSONL [...]
import json, sys, os, glob, re, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L
SKIP = ('{"type": "api-request-blob"', '{"type": "api-request-shape"', '{"type": "api-request"', '{"type":"api-request')
PATHRE = re.compile(r"(__reports__|__pondus__|__scrupuli__|__instrumenta__)/[\w./@-]+")
out = [["session", "agent_id", "name", "type", "role", "wave", "kind", "n_in_agent", "chars", "bytes", "lines", "has_lab_path", "has_report_path", "ts", "model", "ctx", "extra_request_read_usd"]]
for pair in sys.argv[2:]:
    label, main = pair.split("=", 1)
    for p in sorted(glob.glob(main[:-6] + "/subagents/agent-*.jsonl")):
        aid = os.path.basename(p)[6:-6]
        try:
            meta = json.load(open(p[:-6] + ".meta.json"))
        except Exception:
            meta = {}
        name = meta.get("name") or ""
        atype = meta.get("agentType") or meta.get("agent_type") or ""
        first = ""
        calls, final, usage, model = [], None, {}, {}
        for line in open(p, encoding="utf-8", errors="replace"):
            if line.startswith(SKIP):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("type") != "assistant" or not isinstance(r.get("message"), dict):
                if r.get("type") == "user" and not first:
                    c = (r.get("message") or {}).get("content")
                    first = c if isinstance(c, str) else json.dumps(c)[:20000]
                continue
            m = r["message"]
            if m.get("model") == "<synthetic>":
                continue
            c = m.get("content")
            L.merge_usage(usage.setdefault(m.get("id"), {}), m.get("usage") or {})
            model[m.get("id")] = m.get("model")
            texts = []
            if isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                        calls.append((r.get("timestamp"), (b.get("input") or {}).get("message"), m.get("id")))
                    elif b.get("type") == "text":
                        texts.append(b.get("text", ""))
            elif isinstance(c, str):
                texts.append(c)
            if texts:
                final = (r.get("timestamp"), "\n".join(texts))
        if not name:
            mm = re.search(r"Your name is ([a-z0-9-]+)", first)
            name = mm.group(1) if mm else ""
        role = re.match(r"([a-z]+)-w", name)
        role = role.group(1) if role else (atype.split(":")[-1] if atype else "?")
        wave = re.search(r"-w(\d+)-", name)
        wave = wave.group(1) if wave else ""
        rows = [("tool_input", t, m, mid) for t, m, mid in calls] if calls else ([("final_text", final[0], final[1], None)] if final else [])
        for i, (kind, t, msg, mid) in enumerate(rows):
            u = usage.get(mid) or {}
            ctx = sum(int(u.get(f) or 0) for f in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            pr = L.PRICES.get(re.sub(r"-\d{8}$", "", model.get(mid) or ""))
            msg = msg if isinstance(msg, str) else ""
            out.append([label, aid, name, atype, role, wave, kind, i + 1, len(msg), len(msg.encode("utf-8", "replace")), msg.count("\n") + 1 if msg else 0,
                        int(bool(PATHRE.search(msg))), int(bool(re.search(r"__reports__/\S+|__pondus__/\S+", msg))), t or "", model.get(mid) or "", ctx, "%.5f" % (ctx * pr[2] / 1e6) if pr and ctx else ""])
with open(sys.argv[1], "w") as fh:
    fh.write("\n".join("\t".join(str(x) for x in r) for r in out) + "\n")
print(len(out) - 1, "rows")
