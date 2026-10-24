# w09-a: extracts every tool call with the permission decision recorded on its result from all ~/.claude/projects/*/ transcripts (main threads and subagents), redacts secrets, writes one JSON line per unique tool_use id to OUT_DIR/calls.jsonl (never committed: command text, cwd, prompts) and prints counts. Usage: python3 -I w09a_collect.py OUT_DIR
import glob, json, os, re, sys, collections

B = os.path.expanduser("~/.claude/projects/")

# ---- redaction: obvious secrets only; every hit is counted, none printed
RED = [
    ("key_sk", re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_\-]{16,}")),
    ("key_gh", re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{16,}")),
    ("key_aws", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{12,}")),
    ("key_slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("key_google", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]*")),
    ("bearer", re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=\-]{16,}")),
    ("assign", re.compile(r"(?i)\b([A-Za-z0-9_\-]*(?:password|passwd|secret|token|api[_\-]?key|apikey|credential)[A-Za-z0-9_\-]*)(\s*[=:]\s*|\s+)(['\"]?)[^\s'\"&;|]{6,}")),
    ("hdr", re.compile(r"(?i)(authorization|x-api-key|x-auth-token)(\s*[:=]\s*)(['\"]?)[^\s'\"]{8,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("privkey", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)")),
    ("longhex", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
    ("b64long", re.compile(r"\b[A-Za-z0-9+/]{48,}={0,2}")),
]
RC = collections.Counter()


def redact(s):
    if not isinstance(s, str):
        return s
    for name, rx in RED:
        if name in ("assign", "hdr"):
            s, n = rx.subn(lambda m: m.group(1) + m.group(2) + "<REDACTED>", s)
        elif name == "bearer":
            s, n = rx.subn(lambda m: m.group(1) + " <REDACTED>", s)
        else:
            s, n = rx.subn("<REDACTED-%s>" % name, s)
        if n:
            RC[name] += n
    return s


def redact_obj(o, lim):
    if isinstance(o, str):
        r = redact(o)
        return r if len(r) <= lim else r[:lim] + "...[+%d chars]" % (len(r) - lim)
    if isinstance(o, dict):
        return {k: redact_obj(v, lim) for k, v in o.items()}
    if isinstance(o, list):
        return [redact_obj(v, lim) for v in o[:20]]
    return o


def text_of(c):
    if isinstance(c, list):
        c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


def condense_ctx(x):
    # what the transcript shows of the classifier's context: git state summary, cwd, platform (no prompt text is recorded)
    if not isinstance(x, dict):
        return None
    c = x.get("context") or {}
    g = c.get("git_state") or {}
    st = g.get("status") or {}
    vis = ((g.get("visibility") or {}).get("origin") or {}).get("visibility")
    return {"request": x.get("request"), "live_cwd": c.get("live_cwd"), "platform": c.get("platform"),
            "branch": g.get("branch"), "clean": st.get("clean"), "counts": st.get("counts"), "origin_visibility": vis,
            "keys": sorted(c.keys())}


REASON = re.compile(r"Reason: (.*?)\. If you have other tasks")


def main(out):
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(B + "*/**/*.jsonl", recursive=True))
    calls, res = {}, {}
    dup_use = 0
    stats = collections.Counter()
    for fi, f in enumerate(files):
        rel = f[len(B):]
        project = rel.split("/")[0]
        sub = "/subagents/" in f
        mode = None
        auto_att = False
        prompts = {}
        last_prompt = None
        for line in open(f, errors="replace"):
            interesting = ('"tool_use"' in line or '"tool_result"' in line or "permissionMode" in line
                           or '"permission-mode"' in line or '"auto_mode"' in line or '"auto_mode_exit"' in line)
            if not interesting:
                continue
            try:
                m = json.loads(line)
            except ValueError:
                continue
            t = m.get("type")
            if t == "permission-mode":
                mode = m.get("permissionMode") or m.get("mode")
                continue
            if t == "attachment":
                at = (m.get("attachment") or {}).get("type")
                if at == "auto_mode":
                    auto_att = True
                elif at == "auto_mode_exit":
                    auto_att = False
                continue
            msg = m.get("message") or {}
            cont = msg.get("content")
            if t == "user":
                if m.get("permissionMode"):
                    mode = m["permissionMode"]
                if isinstance(cont, str) and not m.get("isMeta"):
                    prompts[m.get("promptId") or "_"] = cont
                    last_prompt = cont
                elif isinstance(cont, list):
                    txt = [b for b in cont if isinstance(b, dict) and b.get("type") == "text"]
                    trs = [b for b in cont if isinstance(b, dict) and b.get("type") == "tool_result"]
                    if txt and not trs and not m.get("isMeta"):
                        s = "".join(b.get("text", "") for b in txt)
                        prompts[m.get("promptId") or "_"] = s
                        last_prompt = s
                    for b in trs:
                        tid = b.get("tool_use_id")
                        if not tid or tid in res:
                            continue
                        pd = m.get("permissionDecision")
                        res[tid] = {
                            "is_error": bool(b.get("is_error")),
                            "text": text_of(b.get("content"))[:900],
                            "kind": m.get("toolDenialKind"),
                            "pd": pd,
                            "cat": (pd or {}).get("classifierCategory"),
                            "has_ctx": "serverClassifierContext" in m,
                            "ctx": condense_ctx(m.get("serverClassifierContext")),
                            "rts": m.get("timestamp"),
                            "unanswered": m.get("toolDenialUnanswered"),
                        }
            elif t == "assistant" and isinstance(cont, list):
                for b in cont:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tid = b.get("id")
                        if tid in calls:
                            dup_use += 1
                            continue
                        pid = m.get("promptId")
                        calls[tid] = {
                            "id": tid, "tool": b.get("name"), "input": b.get("input"),
                            "ts": m.get("timestamp"), "session": m.get("sessionId"),
                            "project": project, "sub": sub, "file": rel,
                            "mode": mode, "auto_att": auto_att,
                            "prompt": prompts.get(pid) or last_prompt, "model": msg.get("model"),
                            "version": m.get("version"),
                        }
        stats["files"] += 1
    print("files", len(files), "unique tool_use", len(calls), "duplicate tool_use blocks", dup_use, "results", len(res))
    n_out = 0
    with open(os.path.join(out, "calls.jsonl"), "w") as fo:
        for tid, c in calls.items():
            r = res.get(tid)
            c["res"] = r
            c["input"] = redact_obj(c["input"], 4000)
            c["prompt"] = redact((c["prompt"] or "")[:2000])
            if r:
                r["text"] = redact(r["text"])
                r["ctx"] = redact_obj(r["ctx"], 200)
                if r["pd"]:
                    r["pd"] = redact_obj(r["pd"], 200)
            fo.write(json.dumps(c) + "\n")
            n_out += 1
    print("written", n_out)
    print("redactions by kind (count only):", dict(RC))


if __name__ == "__main__":
    main(sys.argv[1])
