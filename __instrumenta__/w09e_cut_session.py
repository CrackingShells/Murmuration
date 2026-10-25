# Cuts a PI session transcript (.jsonl) after record IDX, rewrites the PI's worktree path to a scratch lab path, drops api-request-* debug records, and installs the copy under a fresh session id in ~/.claude/projects/<encoded scratch cwd>/ so `claude --resume <id> --fork-session` can continue it; reads the original, never writes it.
"""usage: w09e_cut_session.py SRC.jsonl IDX LAB_DIR OUT_DIR [--old-root PATH]
Writes OUT_DIR/cut.jsonl (the master copy, scratch) and ~/.claude/projects/<enc(LAB_DIR)>/<new-id>.jsonl (same bytes, `sessionId` fields rewritten); prints the new id and the context tokens of the last
assistant record at or before IDX (input + cache read + cache write). The encoded project folder name is LAB_DIR with every non-alphanumeric character turned into '-'."""
import json, os, re, sys, uuid

src, idx, lab, out = sys.argv[1], int(sys.argv[2]), os.path.realpath(sys.argv[3]), sys.argv[4]
old = "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd"
if "--old-root" in sys.argv: old = sys.argv[sys.argv.index("--old-root") + 1]
new_id = str(uuid.uuid4()); os.makedirs(out, exist_ok=True)
lines = open(src, encoding="utf-8").read().split("\n")
keep, last_ctx, dropped = [], None, 0
for i, l in enumerate(lines[:idx + 1]):
    if not l.strip(): continue
    d = json.loads(l)
    if d.get("type") in ("api-request", "api-request-blob", "api-request-shape"): dropped += 1; continue
    if d.get("type") == "assistant" and not d.get("isSidechain"):
        u = d["message"].get("usage", {}); last_ctx = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
    s = l.replace(old, lab)
    d = json.loads(s)
    if "sessionId" in d: d["sessionId"] = new_id
    keep.append(json.dumps(d, ensure_ascii=False))
text = "\n".join(keep) + "\n"
open(os.path.join(out, "cut.jsonl"), "w", encoding="utf-8").write(text)
enc = re.sub(r"[^A-Za-z0-9]", "-", lab)
pd = os.path.expanduser("~/.claude/projects/" + enc); os.makedirs(pd, exist_ok=True)
open(os.path.join(pd, new_id + ".jsonl"), "w", encoding="utf-8").write(text)
print(json.dumps(dict(session_id=new_id, records=len(keep), dropped=dropped, last_ctx_tokens=last_ctx, bytes=len(text.encode()), project_dir=pd)))
