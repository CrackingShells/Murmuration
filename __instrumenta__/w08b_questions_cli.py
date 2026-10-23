# Runs each question of a questions.tsv (id, expected_file, query, answer_regex, pattern) through the colgrep CLI (JSON, top 30) against one root and scores it: rank of the first hit in the expected file, rank of the first hit whose line span contains the answer line, hit-unit type and span against the file's length, characters a search listing (10 hits, 6-line snippets) returns against the whole file, characters of the expanded unit, wall seconds; inputs: questions.tsv, a root; output: results.tsv. Usage: python3 -I w08b_questions_cli.py QUESTIONS.tsv ROOT RESULTS.tsv [K]
import csv, json, os, re, subprocess, sys, time, importlib.util
_sp = importlib.util.spec_from_file_location("locate", os.path.expanduser("~/.claude/plugins/cache/cracking-shells/colgrep-mcp/0.5.2/server/colgrep_mcp/locate.py"))
locate = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(locate)  # the MCP server's own span correction
_FT = {}


def fix_span(h):
    """The MCP tool re-locates each unit's span in the file text; the CLI's JSON spans are not always the true ones."""
    u = h["unit"]
    if u["file"] not in _FT:
        _FT[u["file"]] = open(u["file"], errors="replace").read()
    a, b, ok = locate.locate_unit(_FT[u["file"]], u.get("code") or "", u["line"], u["end_line"])
    u["line"], u["end_line"] = a, b

qf, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 30


def listing_chars(h):
    """Size of one hit as the MCP search tool prints it: ids, names, a score and the first 6 lines of the unit."""
    u = h["unit"]
    code = u.get("code") or ""
    snip = "\n".join(code.split("\n")[:6])
    rec = {"hit_id": "%s:%d-%d" % (u["file"], u["line"], u["end_line"]), "file": u["file"], "line": u["line"], "end_line": u["end_line"],
           "name": u["name"], "qualified_name": u["qualified_name"], "unit_type": u["unit_type"], "language": u["language"],
           "signature": u.get("signature"), "score": h["score"], "snippet": snip, "code": None, "location_verified": True}
    return len(json.dumps(rec, separators=(",", ":")))


def run(q):
    cmd = ["colgrep", "search", "--json", "-y", "-k", str(K)]
    if q["pattern"]:
        cmd += ["-e", q["pattern"]]
    cmd += [q["query"], root]
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    dt = time.time() - t
    try:
        hits = json.loads(p.stdout)
    except Exception:
        hits = []
    for h in hits:
        fix_span(h)
    return hits, dt


rows = []
for q in csv.DictReader(open(qf), delimiter="\t", quoting=csv.QUOTE_NONE):
    path = os.path.join(root, q["expected_file"])
    text = open(path, errors="replace").read()
    lines = text.split("\n")
    rx = re.compile(q["answer_regex"])
    ans = next((i + 1 for i, l in enumerate(lines) if rx.search(l)), 0)
    hits, dt = run(q)
    rel = [os.path.relpath(h["unit"]["file"], root) for h in hits]
    fr = next((i + 1 for i, f in enumerate(rel) if f == q["expected_file"]), 0)
    sr = next((i + 1 for i, h in enumerate(hits) if rel[i] == q["expected_file"] and h["unit"]["line"] <= ans <= h["unit"]["end_line"]), 0)
    hu = hits[sr - 1]["unit"] if sr else (hits[fr - 1]["unit"] if fr else None)
    span = (hu["end_line"] - hu["line"] + 1) if hu else 0
    unit_chars = len("\n".join(lines[hu["line"] - 1:hu["end_line"]])) if hu else 0
    rows.append({"id": q["id"], "expected_file": q["expected_file"], "file_lines": len(lines), "file_chars": len(text), "answer_line": ans,
                 "answer_pos": round(ans / max(1, len(lines)), 2), "file_rank": fr, "section_rank": sr, "unit_type": hu["unit_type"] if hu else "",
                 "unit_span": span, "unit_chars": unit_chars, "list10_chars": sum(listing_chars(h) for h in hits[:10]), "list5_chars": sum(listing_chars(h) for h in hits[:5]),
                 "noise10": sum(1 for f in rel[:10] if re.search(r"reflective_run|/runs/|replay_lab|/scratch/|/probes/", f)), "expand200_reaches": int(bool(hu) and hu["line"] <= ans < hu["line"] + 200), "top1_file": rel[0] if rel else "",
                 "top1_type": hits[0]["unit"]["unit_type"] if hits else "", "n_hits": len(hits), "wall_s": round(dt, 2)})
with open(out, "w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
    w.writeheader()
    w.writerows(rows)
n = len(rows)
for k in (1, 3, 10):
    print("top-%d: file %d/%d, section %d/%d" % (k, sum(1 for r in rows if 0 < r["file_rank"] <= k), n, sum(1 for r in rows if 0 < r["section_rank"] <= k), n))
