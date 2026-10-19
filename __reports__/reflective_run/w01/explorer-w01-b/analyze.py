#!/usr/bin/env python3
"""explorer-w01-b: summary tables from the extracted CSVs and the transcripts.
Run: python3 -I analyze.py OUTDIR      (needs extract_comm.py in the same directory, run first)
Writes: brief_anatomy.csv, handbacks.csv, summary.txt
"""
import csv, json, re, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_comm as E

out = sys.argv[1]
S = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); S.append(s)

CLASSES = [
    ("role", re.compile(r"^(You are|You build|You're|Your name is)", re.I)),
    ("readfirst", re.compile(r"^(READ FIRST|Read first|READ:|CONTEXT:|READING RULE|RULE OF THE REVIEW)", re.I)),
    ("final", re.compile(r"^(FINAL MESSAGE|End with your puzzles|Return:)", re.I)),
    ("commit", re.compile(r"^(Commit|Commit only)", re.I)),
    ("deliverable", re.compile(r"^(DELIVERABLE|Deliverable)", re.I)),
    ("rules", re.compile(r"^(RULES|Rules|CONSTRAINTS|THE WRITING RULE|Constraints)", re.I)),
]
def classify(par):
    for n, rx in CLASSES:
        if rx.match(par.strip()):
            return n
    return "task"

# ---- T1 brief anatomy over all Agent briefs (unique)
briefs = []
seen = set()
for label, jf, subdir, root in E.SESSIONS:
    for i, d in E.load(jf):
        for b in E.blocks(d):
            if b.get("type") == "tool_use" and b["name"] == "Agent" and b["id"] not in seen:
                seen.add(b["id"])
                briefs.append((label, i, b["input"].get("description", ""), b["input"].get("prompt", ""), b["input"].get("name", "")))
rows = []
for label, i, desc, p, nm in briefs:
    cl = {}
    for par in re.split(r"\n\s*\n", p):
        c = classify(par)
        cl[c] = cl.get(c, 0) + len(par)
    r = dict(session=label, line=i, description=desc, name=nm, chars=len(p))
    for n in ["role", "readfirst", "task", "rules", "deliverable", "commit", "final"]:
        r[n] = cl.get(n, 0)
    rows.append(r)
with open(out + "/brief_anatomy.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
say("T1 brief anatomy: N briefs =", len(rows))
for lab in ["genesis", "design", "thisrun"]:
    rr = [r for r in rows if r["session"] == lab]
    if not rr: continue
    tot = sum(r["chars"] for r in rr)
    say(" ", lab, "n=%d" % len(rr), "median chars %d" % st.median(r["chars"] for r in rr),
        "range %d-%d" % (min(r["chars"] for r in rr), max(r["chars"] for r in rr)),
        "share by class:", {n: round(sum(r[n] for r in rr) / tot, 3) for n in ["role", "readfirst", "task", "rules", "deliverable", "commit", "final"]})

# ---- T1b brief vs always-present context
sc = list(csv.DictReader(open(out + "/startctx.csv")))
say("T1b start context per subagent (chars; mean over runs)")
for lab in ["genesis", "design", "thisrun"]:
    rr = [r for r in sc if r["session"] == lab and int(r["instructions"]) > 0]
    if not rr: continue
    m = lambda k: round(st.mean(int(r[k]) for r in rr))
    b, ins, sk, hk, spr, dfr, ctx = m("brief_chars"), m("instructions"), m("skill_listing"), m("hook_additional_context"), m("system_prompt"), m("deferred"), m("session_context")
    tot = b + ins + sk + hk + spr + dfr + ctx
    say(" ", lab, "n=%d" % len(rr), "brief", b, "CLAUDE.md(instructions)", ins, "skill_listing", sk, "SubagentStart hook ctx", hk,
        "system_prompt", spr, "deferred_tools", dfr, "session_ctx", ctx, "| brief share of start context %.1f%%" % (100 * b / tot))

# ---- T2/T3 hand-backs
alld = list(csv.DictReader(open(out + "/dispatches.csv")))
def last_dispatch(session, agent, enq):
    c = [r for r in alld if r["agent_id"] == agent and r["session"] == session and int(r["line"]) < int(enq)]
    if not c:
        c = [r for r in alld if r["agent_id"] == agent and r["tool"] == "Agent"]
    c = sorted(c, key=lambda r: int(r["line"]))
    if not c:
        return {}
    last = dict(c[-1])
    if not last.get("return_word_limit"):  # a follow-up without its own limit: the earlier limit still stands
        for r in reversed(c):
            if r.get("return_word_limit"):
                last["return_word_limit"] = r["return_word_limit"]
                break
    return last
rets = [r for r in csv.DictReader(open(out + "/returns.csv")) if r["kind"] == "agent-message"]
# re-read raw reports for first-line analysis
raw = {}
for label, jf, subdir, root in E.SESSIONS:
    for i, d in E.load(jf):
        if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
            c = d.get("content") or ""
            if c.startswith("<agent-message"):
                p = E.parse_handback(c)
                if p:
                    raw[(label, str(i))] = p["report"]
hb = []
for r in rets:
    rep = raw.get((r["session"], r["enq_line"]), "")
    lines = [l for l in rep.split("\n") if l.strip()]
    harness = bool(lines) and lines[0].startswith("[harness:")
    body = [l for l in lines if not l.startswith("[harness:")]
    first = body[0] if body else ""
    absp = len(re.findall(r"`?/Users/hacker/[\w./\-]+", rep))
    relp = len([p for p in E.paths_in(rep) if not p.startswith("/")])
    commit = len(re.findall(r"\b[0-9a-f]{7}\b", rep))
    neutral = rep.count("<\\")
    d = last_dispatch(r["session"], r["agent_id"], r["enq_line"])
    lim = d.get("return_word_limit", "")
    words = int(r["report_words"]) - (len(lines[0].split()) if harness else 0)
    status = "other"
    f = first.lower()
    if re.search(r"blocker|cannot|could not|blocked|failed", f): status = "blocker"
    elif re.search(r"gates:|pass|settled|done|delivered|committed|written|resolved|complete|are in|is done|is in", f): status = "done/pass"
    elif re.search(r"verdict|recommended|result|one root|\*\*", f): status = "result/verdict"
    hb.append(dict(session=r["session"], delivery_line=r["delivery_line"], agent=r["agent_id"], description=r["description"],
                   words=words, brief_limit=lim, over_limit=(int(lim) < words) if lim else "", ratio=(round(words / int(lim), 2) if lim else ""),
                   harness_flag=int(harness), harness_patterns=r["harness_flag"], neutralised_tags=neutral,
                   n_abs_paths=absp, n_rel_paths=relp, n_commit_hashes=commit,
                   headers=r["n_headers"], bullets=r["n_bullets"], table_rows=r["n_table_rows"], bold_heads=r["bold_headings"],
                   first_line_class=status, first_line=first[:140],
                   labels=r["labels"]))
with open(out + "/handbacks.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(hb[0].keys())); w.writeheader(); w.writerows(hb)
say("T2 hand-backs (agent-message form), N =", len(hb), "(genesis+design, unique by enqueue line)")
lim = [h for h in hb if h["brief_limit"]]
say("  with a stated word limit in the brief:", len(lim), "; over limit:", sum(1 for h in lim if h["over_limit"]), "; ratio median %.2f" % st.median(float(h["ratio"]) for h in lim))
say("  words (excl. harness line): median %d, min %d, max %d" % (st.median(h["words"] for h in hb), min(h["words"] for h in hb), max(h["words"] for h in hb)))
nolim = [h for h in hb if not h["brief_limit"]]
say("  without limit in brief: n=%d median words %d" % (len(nolim), st.median(h["words"] for h in nolim) if nolim else 0))
say("  harness flag on first line:", sum(h["harness_flag"] for h in hb), "of", len(hb), "; reports with neutralised '<\\' tags:", sum(1 for h in hb if h["neutralised_tags"]))
say("  first-line class:", {k: sum(1 for h in hb if h["first_line_class"] == k) for k in set(h["first_line_class"] for h in hb)})
say("  reports naming >=1 absolute path:", sum(1 for h in hb if h["n_abs_paths"]), "; >=1 relative path:", sum(1 for h in hb if h["n_rel_paths"]), "; >=1 commit hash:", sum(1 for h in hb if h["n_commit_hashes"]))
say("  reports with table rows:", sum(1 for h in hb if int(h["table_rows"])), "; with bullets:", sum(1 for h in hb if int(h["bullets"])), "; with # headers:", sum(1 for h in hb if int(h["headers"])))
say("  reports containing a label word (THEOREM/CHECKED/...):", sum(1 for h in hb if h["labels"] not in ("{}", "")))
open(out + "/summary.txt", "w").write("\n".join(S) + "\n")
