# Extracts every tool call of every worker in the wave-4..7 session transcripts into one TSV (wave, agent, type, seq, time, tool, class, target path or word, result chars, error flag, colgrep query word count); inputs: the four session dirs under ~/.claude/projects (hard-coded below); output: OUT.tsv (call heads only, no raw text) plus OUT.private.jsonl (colgrep queries and Bash commands, for local analysis, never committed). Usage: python3 -I w08b_calls.py OUT_PREFIX
import json, glob, os, re, sys
H = os.path.expanduser("~/.claude/projects")
SESS = {
 "w4": "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4",
 "w5": "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-lab-system-optimization-1aa673/6b0e1f2a-b6d1-40f5-840c-f38548cd357e",
 "w6": "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-blissful-villani-34edd8/74fa512e-a149-4bbb-bd20-2d434b0f997f",
 "w7": "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-xenodochial-franklin-bc67fb/f023f552-e4a3-4823-a275-6d98b51b849c",
}
SKIP = ('{"type": "api-request-blob"', '{"type": "api-request-shape"', '{"type":"api-request-blob"', '{"type":"api-request-shape"')
PATH = re.compile(r"(?:(?<=[\s'\"=])|^)((?:/|\.{0,2}/)?[\w@.+-]+(?:/[\w@.+*-]+)*\.(?:md|py|sh|tsv|json|jsonl|txt|csv|c|rs))\b")

def tlen(c):
    if isinstance(c, str): return len(c)
    n = 0
    for b in c or []:
        if isinstance(b, dict):
            n += len(b.get("text", "")) if b.get("type") == "text" else tlen(b.get("content"))
    return n

def first_word(cmd):
    cmd = cmd.strip()
    cmd = re.sub(r"^(cd\s+\S+\s*(&&|;)\s*)+", "", cmd)
    cmd = re.sub(r"^(\w+=\S+\s+)+", "", cmd)
    m = re.match(r"[\w./-]+", cmd)
    return os.path.basename(m.group(0)) if m else "?"

def main(out):
    rows, priv = [], []
    for w, s in SESS.items():
        d = os.path.join(H, s, "subagents")
        for f in sorted(glob.glob(d + "/agent-*.jsonl")):
            meta = json.load(open(f.replace(".jsonl", ".meta.json")))
            name = os.path.basename(f)[6:14] + ":" + re.sub(r"[\t\n]", " ", meta.get("description", ""))[:34]
            typ = meta.get("agentType", "").replace("murmuration:", "")
            pend, seq, cgmap = {}, 0, {}
            for l in open(f):
                if l.startswith(SKIP): continue
                try: r = json.loads(l)
                except Exception: continue
                m = r.get("message") or {}
                c = m.get("content")
                if r.get("type") == "assistant" and isinstance(c, list):
                    for b in c:
                        if b.get("type") != "tool_use": continue
                        seq += 1
                        t, i = b["name"], b.get("input", {})
                        cls, tgt, q = t, "", 0
                        if t == "Read": tgt = i.get("file_path", ""); cls = "Read" + ("_part" if i.get("offset") or i.get("limit") else "_whole")
                        elif t == "Bash":
                            cmd = i.get("command", ""); cls = "bash_" + first_word(cmd)
                            c2 = re.sub(r"\d?>\s*&\d|\d?>\s*/dev/null|2>&1", " ", cmd)
                            if cls == "bash_cat" and ("<<" in c2 or re.search(r"(?<![<-])>", c2.split("|")[0])): cls = "bash_catwrite"
                            if cls == "bash_sed" and re.search(r"sed\s+(-\w+\s+)*-i", cmd): cls = "bash_sed_inplace"
                            ps = PATH.findall(cmd); tgt = ps[0] if ps else ""
                            priv.append({"w": w, "a": name, "seq": seq, "cmd": cmd})
                        elif "colgrep" in t:
                            cls = t.split("__")[-1]; tgt = ",".join(i.get("paths") or []); q = len((i.get("query") or "").split())
                            cg = {"w": w, "a": name, "seq": seq, "colgrep": {k: i.get(k) for k in ("query", "pattern", "paths", "limit", "hit_ids", "path") if k in i}}
                            priv.append(cg); cgmap[b["id"]] = cg
                        elif t in ("Grep", "Glob"): tgt = i.get("path", "") or i.get("pattern", "")[:60]
                        elif t in ("Write", "Edit"): tgt = i.get("file_path", "")
                        pend[b["id"]] = [w, name, typ, seq, r.get("timestamp", ""), t, cls, tgt, None, 0, q]
                elif r.get("type") == "user" and isinstance(c, list):
                    for b in c:
                        if b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                            if b["tool_use_id"] in cgmap:
                                txt = json.dumps(b.get("content"))
                                cgmap[b["tool_use_id"]]["hit_files"] = sorted(set(re.findall(r"(/[\w@.+/ -]+?\.(?:md|py|sh|json|tsv|txt|c|rs|toml|yml|yaml))", txt)))[:40]
                                cgmap[b["tool_use_id"]]["result_chars"] = tlen(b.get("content")); cgmap[b["tool_use_id"]]["head"] = txt[:300]
                            p = pend[b["tool_use_id"]]; p[8] = tlen(b.get("content")); p[9] = int(bool(b.get("is_error")))
            rows += list(pend.values())
    rows.sort(key=lambda r: (r[0], r[1], r[3]))
    with open(out + ".tsv", "w") as fo:
        fo.write("wave\tagent\ttype\tseq\ttime\ttool\tclass\ttarget\tresult_chars\terror\tquery_words\n")
        for r in rows: fo.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    with open(out + ".private.jsonl", "w") as fo:
        for p in priv: fo.write(json.dumps(p) + "\n")
    print(len(rows), "calls", len(priv), "private")

if __name__ == "__main__":
    main(sys.argv[1])
