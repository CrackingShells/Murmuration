#!/usr/bin/env python3
# Computes a lab digest (user's words, workers in flight, claim table with line pointers, wave-note map, files already read with exact ranges, hand-backs on disk, last plan and last words) from a hook event on stdin, the lab's files and the session transcript; prints it on stdout (PreCompact: reaches the summarizer; SessionStart compact with --post: reaches the context verbatim).
"""usage: w09e_digest.py [--post] [--max-chars N]   (reads a hook event as JSON on stdin: cwd, transcript_path)
Needs the lab's `scripts/lab_status.py` (found next to this file, else in `<cwd>/scripts`). Never fails the session: exit 0 and no output on any error outside a lab.
Sections (all computed, none remembered): 1 the user's words, verbatim; 2 workers in flight (harness.jsonl start without end) with their Dispatches row and its line; 3 this wave's claims with the line of each
head field and lab-wide counts of the states that wait for the PI; 4 the wave note's map of headings and bold entries with line numbers; 5 files read in this session (Read offset/limit, sed -n A,Bp, head, tail, cat),
whole-file or exact ranges, newest first; 6 hand-backs on disk; 7 the PI's last plan and its last words before the compaction."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
POST = "--post" in args
MAXC = int(args[args.index("--max-chars") + 1]) if "--max-chars" in args else 9000
CLAIM = re.compile(r"\bw\d\d-c\d+\b")
HEAD = re.compile(r"^## (\d{4}-\d\d-\d\d[ T]\d\d:\d\d)\s*$", re.M)
REM = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def rel(root, p):
    try:
        r = os.path.relpath(p, root)
        return p if r.startswith("..") else r
    except ValueError:
        return p


def words(root):
    try:
        t = open(os.path.join(root, "__statera__", "user_words.md"), encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = list(HEAD.finditer(t))
    if not m:
        return None
    body = re.sub(r"\n{3,}", "\n\n", REM.sub("", t[m[-1].end():]).strip())
    return m[-1].group(1), body[:1500] + (" [...cut]" if len(body) > 1500 else "")


def flying(root):
    st, names = {}, {}
    try:
        for l in open(os.path.join(root, "__statera__", "harness.jsonl"), encoding="utf-8", errors="replace"):
            try:
                e = json.loads(l)
            except ValueError:
                continue
            a = e.get("agent_id") if isinstance(e, dict) else None
            if not a:
                continue
            if e.get("name"):
                names[a] = e["name"]
            if e.get("event") == "start":
                st.pop(a, None); st[a] = dict(name=e.get("name") or "?", type=(e.get("type") or "?").split(":")[-1], t=(e.get("t") or "")[:16])
            elif e.get("event") == "end":
                st.pop(a, None)
    except OSError:
        return [], 0
    ended = len({a for a in names}) - len(st)
    return [dict(v, name=names.get(a, v["name"])) for a, v in st.items()], ended


def numbered(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        return []


def claim_fields(path):
    out, lines, first_verdict = {}, numbered(path), None
    for i, l in enumerate(lines, 1):
        if first_verdict is None and l.startswith("## verdict"):
            first_verdict = i
        for k in ("label", "scope", "evidence", "method", "author"):
            if k not in out and l.startswith(k + ":") and first_verdict is None:
                out[k] = i
    return out, first_verdict, len(lines)


def read_ranges(root, tpath):
    """[(path, 'whole' | 'A-B', approx tokens of the result)] newest first, from the session transcript."""
    if not tpath or not os.path.isfile(tpath):
        return []
    uses, sizes = {}, {}
    order = []
    try:
        for l in open(tpath, encoding="utf-8", errors="replace"):
            if '"tool_use"' not in l and '"tool_result"' not in l:
                continue
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("isSidechain") or d.get("type") not in ("assistant", "user"):
                continue
            c = d.get("message", {}).get("content")
            if not isinstance(c, list):
                continue
            for b in c:
                if b.get("type") == "tool_use":
                    uses[b["id"]] = (b["name"], b.get("input", {}))
                    order.append(b["id"])
                elif b.get("type") == "tool_result":
                    cc = b.get("content")
                    sizes[b.get("tool_use_id")] = len(cc if isinstance(cc, str) else json.dumps(cc))
    except OSError:
        return []
    seen, out = set(), []
    for tid in reversed(order):
        name, inp = uses[tid]
        items = []
        if name == "Read" and inp.get("file_path"):
            off, lim = inp.get("offset"), inp.get("limit")
            items.append((inp["file_path"], "%d-%d" % (off or 1, (off or 1) + lim - 1) if (off or lim) else "whole"))
        elif name == "Bash":
            cmd = inp.get("command", "")
            for m in re.finditer(r"sed -n '?(\d+),(\d+)p'?\s+(\S+)", cmd):
                items.append((m.group(3), "%s-%s" % (m.group(1), m.group(2))))
            for m in re.finditer(r"(?:^|[;&|]\s*)(?:cat|head(?: -n? ?\d+)?|tail(?: -n? ?\d+)?)\s+([\w./~-]+\.(?:md|py|json|jsonl|tsv|txt|rs|toml))", cmd):
                items.append((m.group(1), "whole" if cmd.lstrip().startswith("cat") or " cat " in cmd else "head/tail"))
        for path, rg in items:
            full = path if os.path.isabs(path) else os.path.join(root, path)
            key = (full, rg)
            if key in seen or not os.path.isfile(full):
                continue
            seen.add(key)
            out.append((rel(root, full), rg, sizes.get(tid, 0) // 4))
    return out


def plan_and_last(tpath):
    plan, last, plan_t = None, None, ""
    try:
        for l in open(tpath, encoding="utf-8", errors="replace"):
            if '"assistant"' not in l[:400] and '"type":"assistant"' not in l[:400].replace(" ", ""):
                continue
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            for b in d["message"].get("content", []):
                if b.get("type") == "text" and b.get("text", "").strip():
                    last = b["text"].strip()
                if b.get("type") == "tool_use" and b.get("name", "").endswith("update_plan") and isinstance(b.get("input", {}).get("items"), list):
                    plan = b["input"]["items"]; plan_t = (d.get("timestamp") or "")[11:16] + "Z"
    except OSError:
        pass
    return plan, last, plan_t


def build(ev):
    root = ev.get("cwd") or os.getcwd()
    sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(root, "scripts"))
    import lab_status as L
    if not os.path.isdir(os.path.join(root, "__statera__")):
        return ""
    o = ["LAB DIGEST (computed by the lab's hook from its files and this session's transcript at the moment of compaction; every line number is exact for the files as they stand now).",
         "Keep this block in the summary word for word under the heading `Lab digest`, then add what only you know: your plan, what you decided and why, what you were about to do.", ""]
    w = words(root)
    if w:
        o += ["1. The user's words (`__statera__/user_words.md`, %s), verbatim:" % w[0]] + ["   > " + x for x in w[1].splitlines()] + [""]
    wave = L.current_wave(root)
    wtext, wpath = (wave[2], wave[1]) if wave else ("", "")
    wl = wtext.split("\n")
    fl, ended = flying(root)
    o.append("2. Workers in flight (harness.jsonl: started, not ended; %d others have ended). Dispatches rows are at the wave-note line shown:" % ended)
    for f in fl:
        li = next((i for i, x in enumerate(wl, 1) if x.startswith("| " + f["name"] + " ")), None)
        row = wl[li - 1].strip("| ").split("|") if li else []
        o.append("   - %s (%s, started %s)%s" % (f["name"], f["type"], f["t"], (": %s [%s:%d]" % (" ".join(c.strip() for c in row[1:3])[:230], rel(root, wpath), li)) if li else ""))
    if not fl:
        o.append("   - none")
    o.append("")
    claims = L.read_claims(root)
    me = [c for c in claims if wave and c["id"].startswith("w%02d-" % wave[0])]
    o.append("3. Claims of this wave, label as the lab's rules give it (not the author's), with line numbers of the head fields:")
    for c in me:
        flds, fv, n = claim_fields(os.path.join(root, c["file"]))
        o.append("   - %s: %s | %s lines 1-%d; %s; first verdict section %s" % (c["id"], c["current"].split(";")[0], c["file"], n,
                 ", ".join("%s:%d" % kv for kv in flds.items()), ("line %d" % fv) if fv else "none yet"))
    if not me:
        o.append("   - none filed yet")
    esc = [c["id"] for c in claims if c["current"].startswith("escalated")]
    dis = [c["id"] for c in claims if c["current"].startswith("disputed")]
    unv = [c["id"] for c in claims if c["current"].startswith("unverified")]
    o.append("   Lab-wide (%d claim files): escalated, PI decides: %d (%s); disputed: %d%s; unverified: %d (%s). Full table: `python3 scripts/lab_status.py`." % (
        len(claims), len(esc), ", ".join(esc), len(dis), (" (" + ", ".join(dis) + ")") if dis else "", len(unv), ", ".join(unv)))
    o.append("")
    o.append("4. Wave note map (%s, %d lines):" % (rel(root, wpath), len(wl)))
    marks = [(i, x) for i, x in enumerate(wl, 1) if x.startswith("#") or re.match(r"\*\*[^*]{3,90}\*\*", x)]
    for k, (i, x) in enumerate(marks):
        j = (marks[k + 1][0] - 1) if k + 1 < len(marks) else len(wl)
        o.append("   - %d-%d %s" % (i, j, re.sub(r"\s+", " ", x)[:80]))
    o.append("")
    rr = read_ranges(root, ev.get("transcript_path"))
    o.append("5. Already read in this session (newest first; path, lines, approx tokens of that result). To check a detail, read the exact range, not the file:")
    for p, rg, tk in rr[:22]:
        o.append("   - %s %s (~%dk tok)" % (p, rg, tk // 1000 if tk >= 1000 else 0) if tk >= 1000 else "   - %s %s" % (p, rg))
    o.append("")
    hb = os.path.join(root, "__statera__", "handbacks")
    if os.path.isdir(hb):
        names = sorted(f for f in os.listdir(hb) if wave and f.startswith("wave-%02d-" % wave[0]))
        o.append("6. Hand-backs on disk (`__statera__/handbacks/<wave>-<name>.md`, message verbatim; the report it points to, with its line count):")
        for f in names:
            txt = open(os.path.join(hb, f), encoding="utf-8", errors="replace").read()
            m = re.search(r"`([^`]*__reports__/[^`]*\.md)`", txt)
            rp = m.group(1) if m else ""
            rp = rp if os.path.isabs(rp) else os.path.join(root, rp)
            o.append("   - %s (%dB)%s" % (f[8:-3], len(txt.encode()), (" -> %s (%d lines)" % (rel(root, rp), len(numbered(rp)))) if rp and os.path.isfile(rp) else ""))
        if not names:
            o.append("   - none")
        o.append("")
    plan, last, plan_t = plan_and_last(ev.get("transcript_path") or "")
    o.append("7. Your plan and last words before this compaction:")
    if plan:
        o.append("   plan (last update_plan call, %s; may be stale): " % plan_t + "; ".join("[%s] %s" % (i.get("status", "?"), str(i.get("content", ""))[:90]) for i in plan if isinstance(i, dict)))
    if last:
        o.append("   last words: " + re.sub(r"\s+", " ", last)[:600])
    t = "\n".join(o)
    return t if len(t) <= MAXC else t[:MAXC - 12].rstrip() + "\n[...cut]"


def main():
    try:
        raw = sys.stdin.read()
        try:
            ev = json.loads(raw) if raw.strip() else {}
        except ValueError:
            ev = {}
        out = build(ev)
        if out:
            print(out)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    main()
    sys.exit(0)
