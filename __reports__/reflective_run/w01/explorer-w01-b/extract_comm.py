#!/usr/bin/env python3
"""explorer-w01-b: extract dispatches, hand-backs, PI reactions and start-context sizes
from Claude Code transcripts. Read-only on transcripts.

Run:  python3 -I extract_comm.py OUTDIR
Outputs (CSV): dispatches.csv returns.csv reactions.csv startctx.csv
"""
import csv
import glob
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
PROJ = HOME + "/.claude/projects/"
GEN = PROJ + "-Users-hacker-Documents-explore-combinatorics-on-binary/"
RUN = PROJ + "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/"
SESSIONS = [
    # label, jsonl, subagent dir, repo root (to resolve paths named in briefs)
    ("genesis", GEN + "566fa912-7009-421a-9d79-11145e2b8db9.jsonl",
     GEN + "566fa912-7009-421a-9d79-11145e2b8db9/subagents",
     "/Users/hacker/Documents/explore/combinatorics_on_binary"),
    ("design", GEN + "82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl",
     GEN + "82e8a947-1a0c-441c-bc39-df8e2e5fa743/subagents",
     "/Users/hacker/Documents/explore/combinatorics_on_binary"),
    ("thisrun", RUN + "ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl",
     RUN + "ab96c5ed-ead3-4b36-9671-6076e3914087/subagents",
     "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e"),
]
ALT_ROOT = "/Users/hacker/Documents/src/CrackingShells/Murmuration"
PATH_RE = re.compile(r"[`'\"(\s]((?:[\w.\-]+/)+[\w.\-]+\.[A-Za-z0-9]{1,6}|__[a-z_]+__/[\w./\-]*|[\w\-]+\.(?:md|py|csv|json|wl|png|txt))")
NUM_RE = re.compile(r"\d[\d,]*\.?\d*")
LABELS = ["THEOREM", "CHECKED", "CONJECTURE", "MEASURED", "ESTIMATE", "CITED", "UNVERIFIED",
          "SUPPORTED", "OVERSTATED", "UNSUPPORTED", "SOUND", "WRONG", "ESCALATE", "VERIFIED"]


def load(path):
    out = []
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            try:
                out.append((i, json.loads(line)))
            except Exception:
                pass
    return out


def blocks(d):
    m = d.get("message")
    if isinstance(m, dict):
        c = m.get("content")
        if isinstance(c, list):
            return c
        if isinstance(c, str):
            return [{"type": "text", "text": c}]
    return []


def paths_in(text):
    return sorted(set(p.rstrip(".,;:)") for p in PATH_RE.findall(text or "")))


def shingles(text, n=6):
    w = re.findall(r"\w+", (text or "").lower())
    return set(tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1)))


def result_text(b):
    c = b.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def parse_handback(content):
    """return dict(agent, kind, report, usage) or None"""
    m = re.search(r'<agent-message from="([^"]+)">\n(.*?)</agent-message>', content, re.S)
    if m:
        body = m.group(2)
        k = body.find("The report follows:")
        if k >= 0:
            body = body[k + len("The report follows:"):].lstrip("\n")
        rep = "\n".join(l[2:] if l.startswith("  ") else l for l in body.split("\n")).strip()
        return dict(agent=m.group(1), kind="agent-message", report=rep, usage=None)
    m = re.search(r"<task-notification>.*?<task-id>([^<]+)</task-id>.*?<status>([^<]*)</status>", content, re.S)
    if m:
        r = re.search(r"<result>(.*?)</result>", content, re.S)
        u = re.search(r"<usage>(.*?)</usage>", content, re.S)
        usage = None
        if u:
            usage = dict(re.findall(r"<(\w+)>(\d+)</\1>", u.group(1)))
        return dict(agent=m.group(1), kind="task-notification:" + m.group(2),
                    report=(r.group(1).strip() if r else ""), usage=usage)
    return None


def start_context(subfile):
    """chars of what the subagent held before its first assistant turn, by attachment type"""
    sizes = {}
    brief = ""
    first_ts = last_ts = None
    n_asst = n_tool = 0
    try:
        ev = load(subfile)
    except Exception:
        return None
    seen_asst = False
    for i, d in ev:
        t = d.get("type")
        if d.get("timestamp"):
            first_ts = first_ts or d["timestamp"]
            last_ts = d["timestamp"]
        if t == "assistant":
            seen_asst = True
            n_asst += 1
            for b in blocks(d):
                if b.get("type") == "tool_use":
                    n_tool += 1
        if t == "user" and not brief:
            for b in blocks(d):
                if b.get("type") == "text":
                    brief = b["text"]
        if t == "attachment" and not seen_asst:
            a = d["attachment"]
            ty = a.get("type")
            txt = ""
            if ty == "hook_additional_context":
                txt = "\n".join(a.get("content", []))
            elif ty == "skill_listing":
                txt = a.get("content", "")
            elif ty == "instructions":
                txt = "".join(f.get("content", "") for f in a.get("files", []))
            elif ty == "session_context":
                txt = json.dumps(a.get("context", ""))
            elif ty == "agent_listing_delta":
                txt = "\n".join(a.get("addedLines", []))
            elif ty == "mcp_instructions_delta":
                txt = "\n".join(a.get("addedBlocks", []))
            elif ty == "prompt_snapshot":
                txt = json.dumps(a.get("systemPrompt", ""))
            elif ty == "deferred_tools_delta":
                txt = "\n".join(a.get("addedLines", []))
            if txt:
                sizes[ty] = sizes.get(ty, 0) + len(txt)
    return dict(sizes=sizes, brief=brief, first_ts=first_ts, last_ts=last_ts, n_asst=n_asst, n_tool=n_tool)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    genesis_uuids = set()
    genesis_q = set()
    for _, x in load(SESSIONS[0][1]):
        if x.get("uuid"):
            genesis_uuids.add(x["uuid"])
        if x.get("type") == "queue-operation":
            genesis_q.add((x.get("timestamp"), x.get("operation"), x.get("content")))
    all_brief_shingles = []  # (label, line, shingleset) in time order
    disp, rets, reacts, ctxs = [], [], [], []
    for label, jf, subdir, root in SESSIONS:
        ev = load(jf)
        if label == "design":  # lines shared with genesis are the same events
            ev = [(i, d) for i, d in ev if d.get("uuid") not in genesis_uuids
                  and (d.get("timestamp"), d.get("operation"), d.get("content")) not in genesis_q]
        if label == "thisrun":
            all_brief_shingles = []
        by_line = {i: d for i, d in ev}
        order = [i for i, _ in ev]
        pos = {i: k for k, i in enumerate(order)}
        # 1. tool_uses and their results
        uses = {}
        agent_of_use = {}
        for i, d in ev:
            for b in blocks(d):
                if b.get("type") == "tool_use" and b["name"] in ("Agent", "SendMessage"):
                    uses[b["id"]] = (i, d, b)
                if b.get("type") == "tool_result" and b.get("tool_use_id"):
                    txt = result_text(b)
                    m = re.search(r"agentId: (\w+)", txt)
                    if m:
                        agent_of_use[b["tool_use_id"]] = m.group(1)
        sub_by_agent = {}
        for f in glob.glob(subdir + "/agent-*.jsonl"):
            sub_by_agent[os.path.basename(f)[6:-6]] = f
        # fall back to genesis folder for forked ids
        for f in glob.glob(SESSIONS[0][2] + "/agent-*.jsonl"):
            sub_by_agent.setdefault(os.path.basename(f)[6:-6], f)
        meta_by_agent = {}
        for a, f in sub_by_agent.items():
            mf = f[:-6] + ".meta.json"
            if os.path.exists(mf):
                try:
                    meta_by_agent[a] = json.load(open(mf))
                except Exception:
                    pass
        # 2. hand-backs: delivery lines
        deliveries = []  # (line, parsed)
        enq = {}
        for i, d in ev:
            if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
                c = d.get("content") or ""
                if c.startswith("<agent-message") or c.startswith("<task-notification"):
                    p = parse_handback(c)
                    if p:
                        enq[i] = (d.get("timestamp"), p)
        # delivery = first user/attachment line after enqueue that carries the same agent id
        for i, (ts, p) in sorted(enq.items()):
            dl = None
            for j in order[pos[i] + 1: pos[i] + 60]:
                x = by_line[j]
                if x.get("type") == "user" and isinstance(x.get("message", {}).get("content"), str) \
                        and p["agent"] in x["message"]["content"]:
                    dl = j
                    break
                if x.get("type") == "attachment" and x["attachment"].get("type") == "queued_command" \
                        and p["agent"] in str(x["attachment"].get("prompt", "")):
                    dl = j
                    break
            deliveries.append((i, dl, ts, p))
        # 3. dispatch rows
        brief_rows = {}
        for uid, (i, d, b) in sorted(uses.items(), key=lambda kv: kv[1][0]):
            inp = b["input"]
            text = inp.get("prompt") if b["name"] == "Agent" else inp.get("message")
            text = text or ""
            aid = agent_of_use.get(uid)
            sub = sub_by_agent.get(aid) if aid else None
            sc = start_context(sub) if sub else None
            ps = paths_in(text)
            existing = []
            for p in ps:
                for cand in (os.path.join(root, p), os.path.join(ALT_ROOT, p), p):
                    if os.path.isfile(cand):
                        existing.append(cand)
                        break
            sh = shingles(text)
            file_sh = set()
            for fp in existing:
                try:
                    file_sh |= shingles(open(fp, errors="ignore").read())
                except Exception:
                    pass
            prev_sh = set()
            for _, _, s2 in all_brief_shingles:
                prev_sh |= s2
            instr_sh = set()
            if sc:
                pass
            fm = re.search(r"FINAL MESSAGE[^\n]*?\((?:under|<|max)?\s*~?(\d+)\s*words", text, re.I) or \
                re.search(r"under (\d+) words", text, re.I) or re.search(r"(\d+) words", text)
            ret_spec = ""
            m2 = re.search(r"(FINAL MESSAGE.*|What to return.*|Return:.*|Report back.*)", text, re.S | re.I)
            if m2:
                ret_spec = m2.group(1)[:300].replace("\n", " ")
            row = dict(
                session=label, line=i, uuid=d.get("uuid"), ts=d.get("timestamp"), tool=b["name"],
                subagent_type=inp.get("subagent_type", ""), name=inp.get("name", "") or inp.get("to", ""),
                model=inp.get("model", ""), background=inp.get("run_in_background", ""),
                description=inp.get("description") or inp.get("summary") or "",
                agent_id=aid or inp.get("to", ""), chars=len(text), words=len(re.findall(r"\S+", text)),
                n_paths=len(ps), n_paths_exist=len(existing),
                shingle_in_named_files=round(len(sh & file_sh) / len(sh), 3) if sh else 0,
                shingle_in_earlier_briefs=round(len(sh & prev_sh) / len(sh), 3) if sh else 0,
                has_return_spec=int(bool(ret_spec)), return_word_limit=(fm.group(1) if fm else ""),
                has_commit_boiler=int("Co-Authored-By" in text or "Commit only" in text),
                has_read_first=int(bool(re.search(r"read first|READ FIRST|Read first", text))),
                has_labels_asked=int(bool(re.search(r"THEOREM|CHECKED|MEASURED|CONJECTURE", text))),
                ret_spec=ret_spec,
            )
            disp.append(row)
            all_brief_shingles.append((label, i, sh))
            if sc:
                s = sc["sizes"]
                ctxs.append(dict(session=label, agent_id=aid, name=inp.get("name", ""),
                                 description=row["description"], brief_chars=len(sc["brief"]),
                                 instructions=s.get("instructions", 0),
                                 skill_listing=s.get("skill_listing", 0),
                                 hook_additional_context=s.get("hook_additional_context", 0),
                                 mcp_instructions=s.get("mcp_instructions_delta", 0),
                                 agent_listing=s.get("agent_listing_delta", 0),
                                 system_prompt=s.get("prompt_snapshot", 0),
                                 session_context=s.get("session_context", 0),
                                 deferred=s.get("deferred_tools_delta", 0),
                                 n_asst=sc["n_asst"], n_tool=sc["n_tool"],
                                 first_ts=sc["first_ts"], last_ts=sc["last_ts"]))
            brief_rows[aid] = row
        # 4. returns + reactions
        for k, (enq_line, dl, ts, p) in enumerate(deliveries):
            rep = p["report"]
            words = len(re.findall(r"\S+", rep))
            nums = NUM_RE.findall(rep)
            lab = {l: len(re.findall(r"\b" + l + r"\b", rep)) for l in LABELS}
            lab = {a: b for a, b in lab.items() if b}
            rp = paths_in(rep)
            drow = brief_rows.get(p["agent"], {})
            lines = rep.split("\n")
            rows = dict(
                session=label, enq_line=enq_line, delivery_line=dl or "", ts=ts, agent_id=p["agent"],
                description=drow.get("description", ""), kind=p["kind"],
                report_chars=len(rep), report_words=words, n_lines=len(lines),
                n_headers=sum(1 for l in lines if l.lstrip().startswith("#")),
                n_bullets=sum(1 for l in lines if re.match(r"\s*([-*]|\d+\.)\s", l)),
                n_table_rows=sum(1 for l in lines if l.strip().startswith("|")),
                n_codefence=rep.count("```") // 2, n_paths=len(rp), n_numbers=len(nums),
                labels=json.dumps(lab, sort_keys=True),
                bold_headings=len(re.findall(r"^\s*\*\*[^*]+\*\*", rep, re.M)),
                tail_is_json=int(bool(re.search(r"[\}\]]\s*$", rep)) and "{" in rep[-400:]),
                first_line=lines[0][:160] if lines else "",
                brief_word_limit=drow.get("return_word_limit", ""),
                brief_words=drow.get("words", ""),
                usage=json.dumps(p["usage"]) if p["usage"] else "",
                is_pointer=int("delivered to you as a message" in rep),
                harness_flag=(re.search(r"\[harness: subagent output matched instruction-shaped pattern\(s\): ([^.]*)\.", rep).group(1) if re.search(r"\[harness: subagent output matched", rep) else ""),
            )
            rets.append(rows)
            # reaction window
            if dl and not rows["is_pointer"]:
                seq = []
                followed_at = None
                sent_to = []
                spawned = 0
                texts = []
                n_asst = 0
                start = pos[dl]
                for j in order[start + 1:]:
                    x = by_line[j]
                    t = x.get("type")
                    if t == "queue-operation" and x.get("operation") == "enqueue":
                        continue
                    if t == "user" and isinstance(x.get("message", {}).get("content"), str):
                        break  # next prompt or hand-back delivered
                    if t != "assistant":
                        continue
                    n_asst += 1
                    if n_asst > 60:
                        break
                    for b in blocks(x):
                        if b.get("type") == "text" and b["text"].strip():
                            texts.append(b["text"].strip())
                        if b.get("type") == "tool_use":
                            nm = b["name"]
                            inp = b["input"]
                            tgt = ""
                            if nm == "Read":
                                tgt = inp.get("file_path", "")
                            elif nm == "Bash":
                                tgt = inp.get("command", "")[:200]
                            elif nm == "SendMessage":
                                tgt = inp.get("to", "")
                                sent_to.append(tgt)
                            elif nm == "Agent":
                                tgt = inp.get("description", "")
                                spawned += 1
                            elif nm in ("Write", "Edit"):
                                tgt = inp.get("file_path", "")
                            seq.append((nm, tgt))
                            full = inp.get("command", "") if nm == "Bash" else tgt
                            if followed_at is None and nm in ("Read", "Bash", "Edit", "Write"):
                                for q in rp:
                                    key = "/".join(q.rstrip("/").split("/")[-2:])
                                    if key and (key in full):
                                        followed_at = len(seq)
                                        break
                reacts.append(dict(
                    session=label, delivery_line=dl, agent_id=p["agent"], description=drow.get("description", ""),
                    report_words=words, n_report_paths=len(rp),
                    n_steps=len(seq), first_tools=" > ".join(n for n, _ in seq[:8]),
                    followed_pointer_at_step=followed_at or "", reasked=int(p["agent"] in sent_to),
                    spawned_after=spawned, sent_to=",".join(sent_to),
                    first_text=(texts[0][:400].replace("\n", " ") if texts else ""),
                    first_targets=" || ".join(t[:80].replace("\n", " ") for _, t in seq[:4]),
                ))
    for name, rows in (("dispatches", disp), ("returns", rets), ("reactions", reacts), ("startctx", ctxs)):
        if not rows:
            continue
        keys = []
        for r in rows:
            for k in r:
                if k not in keys:
                    keys.append(k)
        with open(os.path.join(outdir, name + ".csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(name, len(rows))


if __name__ == "__main__":
    main(sys.argv[1])
