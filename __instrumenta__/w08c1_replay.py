# Replays hook events through scripts/budget.py|handback.py (via w08c1_pyshim.py, fixed clock) and through `murmuration budget|handback`, each scenario in its own folder run once per implementation at the same path, and compares stdout, exit code, stderr and the whole lab folder after every step.
# inputs: the repo (scripts, Rust binary built with --features testclock for the exact pass, or the shipped binary for the real-clock pass), a corpus of real subagent transcripts (read only, copied), seeds; outputs: a JSON summary and a diff file in --out.
# usage: python3 -I w08c1_replay.py --repo WT --rust BIN --scratch DIR --out DIR [--exact|--realclock] [--quick] [--jobs N] [--transcripts N] [--fuzz N] [--seed S]
import argparse, concurrent.futures as cf, glob, hashlib, json, os, random, re, shutil, subprocess, sys, time

NOW0 = 1792700000.125
PROJECT = "murmuration:author"


def lines_of(recs):
    return "".join(json.dumps(r) + "\n" for r in recs)


def rec_user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def rec_coord(text, ts="2026-10-19T09:33:45.583Z", kind="coordinator"):
    return {"type": "user", "isMeta": True, "origin": {"kind": kind}, "timestamp": ts,
            "message": {"role": "user", "content": "The coordinator sent a message while you were working:\n" + text + "\n\nAddress this before completing your current task."}}


def rec_queued(text, kind="coordinator", ts="2026-10-19T09:33:46.583Z"):
    return {"type": "attachment", "timestamp": ts, "attachment": {"type": "queued_command", "prompt": text, "origin": {"kind": kind}}}


def rec_result(text):
    return {"type": "user", "origin": {"kind": "coordinator"}, "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": text}]}}


def rec_mixed(text):
    return {"type": "user", "origin": {"kind": "coordinator"}, "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": "ok"}, {"type": "text", "text": text}]}}


def rec_asst(rid, out, cr=0, cw=0, model="claude-sonnet-5-5", inp=2, chars=0, extra=None, content=None, cc=None, speed=None):
    use = dict(input_tokens=inp, output_tokens=out, cache_read_input_tokens=cr, cache_creation_input_tokens=cw)
    if cc:
        use["cache_creation"] = cc
    if speed:
        use["speed"] = speed
    msg = {"id": "m" + rid, "model": model, "content": content if content is not None else [{"type": "text", "text": "x" * chars}], "usage": use}
    r = {"type": "assistant", "requestId": rid, "message": msg}
    if extra:
        r.update(extra)
    return r


class Scn:
    def __init__(self, name, steps, nolab=False, group="synthetic"):
        self.name, self.steps, self.nolab, self.group = name, steps, nolab, group


def ev(which, kind, now, aid="a1", atype=PROJECT, mode="default", **kw):
    d = dict(cwd="{LAB}", hook_event_name=kind, transcript_path="{SESS}.jsonl", agent_id=aid, agent_type=atype, permission_mode=mode)
    d.update({k: v for k, v in kw.items() if v is not ...})
    for k in [k for k, v in kw.items() if v is ...]:
        d.pop(k, None)
    return ("ev", which, d, now)


def canon_state(B=1.0, T=100000.0, base=0.0, acc=0.0, run_start=NOW0, run_open=True, last_seen=NOW0, k=0, raises_done=0, stops=0, ceil_req=-1, brief_read=True, warned=True, role="author", base_recorded=0.0):
    d = dict(role=role, B=B, T=T, base=base)
    if base_recorded is not None:
        d["base_recorded"] = base_recorded
    d.update(acc=acc, run_start=run_start, run_open=run_open, last_seen=last_seen, k=k, raises_done=raises_done, stops=stops, ceil_req=ceil_req, brief_read=brief_read, warned=warned)
    return d


def threshold_scn(name, atype=PROJECT, mode="auto", brief="Your name is reproducer-w09-1.\nBudget: USD 1.00\nTime: min 100\nGo.\n"):
    steps = [("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_1", tool_input=dict(subagent_type="murmuration:reproducer", prompt=brief, name="reproducer-w09-1")), NOW0),
             ("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_x", tool_input=dict(subagent_type="general-purpose", prompt=brief)), NOW0 + 0.001),
             ("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", agent_id="zz", agent_type="murmuration:author", tool_use_id="toolu_y", tool_input=dict(subagent_type="murmuration:reproducer", prompt=brief)), NOW0 + 0.002),
             ev("budget", "SubagentStart", NOW0 + 1, aid="a1", atype="murmuration:reproducer", mode=mode)]
    cum = []
    t = [NOW0 + 2]

    def spend(rid, usd):
        cum.append(rec_asst(rid, int(round(usd / 10 * 1e6))) if usd else rec_asst(rid, 0, model="<synthetic>", inp=0))
        steps.append(("tx", "a1", lines_of([rec_user(brief)] + cum)))

    def at(kind, **kw):
        t[0] += 1.5
        steps.append(ev("budget", kind, t[0], aid="a1", atype="murmuration:reproducer", mode=mode, **kw))

    post = dict(tool_calls=[dict(tool_name="Bash", tool_use_id="t")])
    for rid, usd in [("r1", 0.49), ("r2", 0.0105), ("r3", 0.02), ("r4", 0.28), ("r5", 0.07), ("r6", 0.01), ("r7", 0.056), ("r8", 0.002), ("r9", 0.04), ("r10", 0.03), ("r11", 0.01)]:
        spend(rid, usd)
        at("PostToolBatch", **post)
        at("PostToolUse", tool_name="Bash")
    at("PostToolBatch", tool_calls=[dict(tool_name="SubagentHandback")])
    at("PostToolUse", tool_name="Bash")
    spend("r12", 0.49)
    for i in range(4):
        at("PostToolUse", tool_name="Bash", tool_use_id="p%d" % i)
    at("PostToolBatch", **post)
    spend("r12b", 0.001)
    at("PostToolUse", tool_name="SubagentHandback")
    for rid in ("r13", "r14", "r15", "r16"):
        spend(rid, 0.01)
        at("PostToolBatch", **post)
        at("PostToolUse", tool_name="Bash")
    at("SubagentStop")
    return Scn(name, steps)


def raise_scn(name):
    brief = "Your name is author-w09-2.\nBudget: USD 1.00\nTime: min 10\nGo.\n"
    steps = [("tx", "b1", lines_of([rec_user(brief)])), ev("budget", "SubagentStart", NOW0, aid="b1", atype="murmuration:author", mode="auto")]
    body = [rec_user(brief), rec_asst("a", 120000)]
    steps.append(("tx", "b1", lines_of(body)))
    steps.append(ev("budget", "PostToolBatch", NOW0 + 30, aid="b1", atype="murmuration:author", mode="auto", tool_calls=[dict(tool_name="Bash")]))
    body += [rec_coord("Budget: USD 2.5\nTime: min 7\nGo on."), rec_asst("b", 1000), rec_coord("Budget: USD 9", kind="peer"), rec_result("Budget: USD 8\nTime: min 8"),
             rec_mixed("Budget: USD 7"), rec_coord("Budget: USD 4 more\nplease"), rec_coord("Time: min 3.5", ts="2026-10-19T09:35:45.5Z"), rec_queued("Budget: USD 6", kind="peer"), rec_queued("Budget: USD 1.5\nHow is it going?", ts="2026-10-19T09:36:00+09:00")]
    steps.append(("tx", "b1", lines_of(body)))
    for i, kind in enumerate(["PostToolBatch", "PostToolUse", "PostToolBatch", "SubagentStop", "PostToolBatch", "SubagentStart", "PostToolBatch", "PostToolUse", "SubagentStop"]):
        steps.append(ev("budget", kind, NOW0 + 60 + 40 * i, aid="b1", atype="murmuration:author", mode="auto", tool_name="Bash", tool_calls=[dict(tool_name="Bash")]))
    return Scn(name, steps)


def time_scn(name, T=10.0, B=1000.0):
    brief = "Your name is explorer-w09-3.\nBudget: USD %s\nTime: min %s\n" % (B, T)
    steps = [("tx", "c1", lines_of([rec_user(brief), rec_asst("a", 100)])), ev("budget", "SubagentStart", NOW0, aid="c1", atype="murmuration:explorer")]
    for frac in (0.1, 0.49, 0.5, 0.74, 0.76, 0.9, 0.94, 1.0, 1.2, 1.49, 1.51, 1.6, 2.0, 2.2):
        for kind in ("PostToolBatch", "PostToolUse"):
            steps.append(ev("budget", kind, NOW0 + frac * T * 60, aid="c1", atype="murmuration:explorer", tool_name="Bash", tool_calls=[dict(tool_name="Bash")]))
    steps.append(ev("budget", "SubagentStop", NOW0 + 3 * T * 60, aid="c1", atype="murmuration:explorer"))
    return Scn(name, steps)


def dispatch_scn(name, mixed=False, expire=False, floor=False):
    b1 = "Your name is author-w09-5.\nBudget: USD %s\nTime: min %s\n" % ("0.1" if floor else "2.5", "1" if floor else "30")
    b2 = "Your name is author-w09-6.\nBudget: USD 4\nTime: min 40\n"
    steps = [("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu1", tool_input=dict(subagent_type="murmuration:author", prompt=b1)), NOW0)]
    if mixed:
        steps.append(("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Task", tool_use_id="tu2", tool_input=dict(subagent_type="murmuration:author", prompt=b2, name="author-w09-6")), NOW0 + 0.5))
    steps.append(("ev", "budget", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu3", tool_input=dict(subagent_type="murmuration:reproducer", prompt="no lines here")), NOW0 + 0.6))
    steps.append(ev("budget", "SubagentStart", NOW0 + (700 if expire else 1), aid="d1", atype="murmuration:author", mode=None))
    steps.append(ev("budget", "SubagentStart", NOW0 + (701 if expire else 2), aid="d2", atype="murmuration:author", mode=None))
    steps.append(("tx", "d1", lines_of([rec_user(b1), rec_asst("a", 1000)])))
    steps.append(ev("budget", "PostToolBatch", NOW0 + 800, aid="d1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")]))
    steps.append(ev("budget", "SubagentStop", NOW0 + 900, aid="d1", atype="murmuration:author"))
    return Scn(name, steps)


def weird_budget_scns():
    out = []
    briefs = ["Budget: USD 0\nTime: min 0\n", "Budget: USD 0.2\n", "Budget: USD 3 \nTime: min 5\t\n", "  Budget: USD 3\n", "Budget: USD 1e3\n", "Budget: USD 12.50\nBudget: USD 99\n", "Budget: USD\n", "no budget here, é中\n", "Time: min 2.5\nBudget: USD 0.3\n", "Budget: USD ٣\n", "Budget: USD 5\r\nTime: min 6\r\n"]
    for i, b in enumerate(briefs):
        brief = "Your name is explorer-w09-%d.\n%s" % (i, b)
        out.append(Scn("brief%d" % i, [("tx", "e1", lines_of([rec_user(brief), rec_asst("a", 5000, cr=20000)])), ev("budget", "PostToolBatch", NOW0 + 100, aid="e1", atype="murmuration:explorer", tool_calls=[dict(tool_name="Bash")]),
                                       ev("budget", "SubagentStart", NOW0 + 101, aid="e1", atype="murmuration:explorer"), ev("budget", "PostToolBatch", NOW0 + 200, aid="e1", atype="murmuration:explorer", tool_calls=[]), ev("budget", "SubagentStop", NOW0 + 300, aid="e1", atype="murmuration:explorer")]))
    # usage shapes: models, dates, haiku long, fast, cache split, unpriced, content blocks with inputs
    recs = [rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n"),
            rec_asst("r1", 1000, cr=1000, cw=500, model="claude-opus-5-5-20260101"), rec_asst("r2", 10, cr=120000, model="claude-haiku-5-5"), rec_asst("r3", 5, speed="fast"),
            rec_asst("r4", 100, cw=3000, cc=dict(ephemeral_5m_input_tokens=1000, ephemeral_1h_input_tokens=1500)), rec_asst("r5", 50, model="gpt-x"), rec_asst("r6", 0, model=None),
            rec_asst("r7", 1, content=[{"type": "tool_use", "name": "Bash", "input": {"b": [1, 2.5, {"z": None, "a": "é\U0001f600\"\\\n"}], "a": 1e22, "c": -0.0, "d": 12345678901234567890}}, {"type": "thinking", "thinking": "hmm"}, {"type": "text", "text": ""}]),
            rec_asst("r7", 1, content=[{"type": "text", "text": "later chunk"}]), rec_asst("r8", 3, extra={"requestId": None}), rec_asst("r8", 3, extra={"requestId": ""}), {"type": "assistant", "message": {"usage": {"input_tokens": 5}}},
            {"type": "summary"}, rec_asst("r9", 77, model="<synthetic>", inp=0), rec_asst("r10", 1, content="just a string"), rec_asst("r11", 1, content=[{"type": "text", "text": "x" * 4000}, {"type": "tool_use", "input": {}}])]
    steps = [("tx", "g1", lines_of(recs))]
    for kind in ("SubagentStart", "PostToolBatch", "PostToolUse", "PostToolBatch", "SubagentStop"):
        steps.append(ev("budget", kind, NOW0 + 50 + len(steps), aid="g1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")], tool_name="Bash"))
    out.append(Scn("usage_shapes", steps))
    # broken transcript lines
    for i, bad in enumerate(["{not json\n", "[1,2]\n", '{"type":"assistant","message":{"usage":{"input_tokens":"5"}}}\n', '{"type":"assistant","message":"x","usage":1}\n', '{"type": "user", "origin": "str", "message": {"content": "Budget: USD 4"}}\n', "﻿" + json.dumps(rec_user("x")) + "\n", '{"type":"assistant","message":{"model":"claude-sonnet-5-5","usage":{"input_tokens":3.5,"output_tokens":9}}}\n']):
        txt = lines_of([rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n"), rec_asst("r1", 100)]) + bad + lines_of([rec_asst("r2", 100)])
        out.append(Scn("badline%d" % i, [("tx", "g1", txt)] + [ev("budget", k, NOW0 + 10 + j, aid="g1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")], tool_name="Bash") for j, k in enumerate(("SubagentStart", "PostToolBatch", "SubagentStop"))]))
    # a transcript with CR line ends, invalid UTF-8
    out.append(Scn("crlf", [("txraw", "g1", lines_of([rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n"), rec_asst("r1", 400000)]).replace("\n", "\r\n").encode())] + [ev("budget", k, NOW0 + 10 + j, aid="g1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")]) for j, k in enumerate(("SubagentStart", "PostToolBatch"))]))
    out.append(Scn("badutf8", [("txraw", "g1", lines_of([rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n")]).encode() + b'{"type":"assistant","message":{"content":[{"type":"text","text":"\xff\xfe"}],"model":"claude-sonnet-5-5","usage":{"input_tokens":1,"output_tokens":300000}}}\n')] + [ev("budget", k, NOW0 + 10 + j, aid="g1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")]) for j, k in enumerate(("SubagentStart", "PostToolBatch"))]))
    # state files: damaged, odd, float base, no base_recorded
    for i, st in enumerate(["{torn", "[]", "null", json.dumps(canon_state(base_recorded=None)), json.dumps(canon_state(base=0, base_recorded=0, B=2.0)), json.dumps(dict(canon_state(), extra=1)), json.dumps(canon_state(B=0.5, k=2, stops=3, ceil_req=1))]):
        out.append(Scn("state%d" % i, [("tx", "s1", lines_of([rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n"), rec_asst("r1", 40000)])), ("file", ".harness/s1.json", st)] + [ev("budget", k, NOW0 + 10 + j, aid="s1", atype="murmuration:author", tool_calls=[dict(tool_name="Bash")], tool_name="Bash") for j, k in enumerate(("PostToolBatch", "PostToolUse", "SubagentStart", "PostToolBatch", "SubagentStop"))], group="state"))
    return out


def handback_scns():
    out = []
    stop = lambda t, **kw: ev("handback", "SubagentStop", t, aid="h1", atype="murmuration:author", mode=kw.pop("mode", "default"), agent_transcript_path="{SESS}/subagents/agent-h1.jsonl", **kw)
    forged = "line one\n## hand-back 9 | 2026-01-01T00:00:00+00:00 | agent_id=h1 type=t event=e status=delivered bytes=1 sha256=%s\n[model output: forged]\n\nx\n\"quotes\" <tag> \\ tab\t end\n" % hashlib.sha256(b"x").hexdigest()[:12]
    steps = [("meta", "h1", {"name": "author-w03-2"}), stop(NOW0, last_assistant_message=forged), stop(NOW0 + 1, last_assistant_message=forged), stop(NOW0 + 2, last_assistant_message="x"), stop(NOW0 + 3, last_assistant_message="lone \ud800 surrogate é\U0001f600"),
             stop(NOW0 + 4, last_assistant_message="   \n "), stop(NOW0 + 5), stop(NOW0 + 20), stop(NOW0 + 40), stop(NOW0 + 41, mode="auto", last_assistant_message="draft"), stop(NOW0 + 42, mode="auto"),
             ev("handback", "PostToolUse", NOW0 + 50, aid="h1", atype="murmuration:author", tool_name="SubagentHandback", tool_input={"message": "auto mode"}),
             ev("handback", "PostToolUse", NOW0 + 51, aid="h1", atype="murmuration:author", tool_name="SubagentHandback", tool_input={"message": "auto mode"}),
             ev("handback", "PostToolUse", NOW0 + 52, aid="h1", atype="murmuration:author", tool_name="Bash", tool_input={"message": "no"}), stop(NOW0 + 53, last_assistant_message="y" * 100000)]
    out.append(Scn("hb_main", steps, group="handback"))
    out.append(Scn("hb_nometa", [("tx", "a5", lines_of([{"message": {"content": "Your name is explorer-w02-c. Read first: x"}}])), ev("handback", "PostToolUse", NOW0, aid="a5", atype="x:y", tool_name="SubagentHandback", tool_input={"message": "name from the brief"}),
                                 ev("handback", "SubagentStop", NOW0 + 1, aid="a3", atype="x:y"), ev("handback", "SubagentStop", NOW0 + 2, aid="a6", atype="x:y", mode="auto", last_assistant_message="draft"), ev("handback", "SubagentStop", NOW0 + 3, aid="a6", atype="x:y", mode="auto"),
                                 ev("handback", "PostToolUse", NOW0 + 4, aid="a4", atype=None, tool_name="Bash", tool_input={"command": "ls"}), ev("handback", "PostToolUse", NOW0 + 5, aid="a7", atype=None, tool_name="SubagentHandback", tool_input={"message": "no type"}, transcript_path=...),
                                 ev("handback", "SubagentStop", NOW0 + 6, aid="WEIRD ID/..", atype="X Y:Z", last_assistant_message="odd id")], group="handback"))
    pre = lambda t, aid, **kw: ev("handback", "PreToolUse", t, aid=aid, atype=kw.pop("atype", "murmuration:explorer"), tool_name=kw.pop("tool_name", "SubagentHandback"), tool_input={"message": "m"}, **kw)
    brief = lambda n: ("tx", n, lines_of([{"message": {"content": "Your name is explorer-w02-c. Read first: x"}}]))
    steps = [brief("e1"), brief("e2"), brief("e3"), pre(NOW0, "e1"), pre(NOW0 + 1, "e1"), ("file", "__reports__/wave-02/explorer-w02-cc/x.md", "x"), ("file", "__reports__/wave-02/explorer-w02-c0/x.md", "x"), pre(NOW0 + 2, "e2"),
             ("file", "__reports__/somewhere/explorer-w02-c/notes.md", "x"), pre(NOW0 + 3, "e3"), pre(NOW0 + 4, "e4", atype="murmuration:author"), ("ev", "handback", dict(cwd="{LAB}", hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_type="murmuration:explorer", tool_input={"message": "m"}), NOW0 + 5),
             pre(NOW0 + 6, "e5", tool_name="Bash"), pre(NOW0 + 7, "e6", transcript_path=None), pre(NOW0 + 8, "e6", transcript_path=None)]
    out.append(Scn("hb_gate", steps, group="handback"))
    out.append(Scn("hb_nolab", [ev("handback", "SubagentStop", NOW0, aid="h1", atype="murmuration:author", last_assistant_message="no lab"), pre(NOW0 + 1, "e1")], nolab=True, group="handback"))
    out.append(Scn("hb_wave", [("meta", "w1", {"name": "author-w12-3"}), ("meta", "w2", {"name": "explorer-wx-3\n"}), ("meta", "w3", {"name": "-bad"}), ("meta", "w4", {"name": ["x"]}),
                               ev("handback", "SubagentStop", NOW0, aid="w1", atype="murmuration:author", last_assistant_message="a"), ev("handback", "SubagentStop", NOW0 + 1, aid="w2", atype="murmuration:author", last_assistant_message="b"),
                               ev("handback", "SubagentStop", NOW0 + 2, aid="w3", atype="murmuration:author", last_assistant_message="c"), ev("handback", "SubagentStop", NOW0 + 3, aid="w4", atype="murmuration:author", last_assistant_message="d"),
                               ev("handback", "SubagentStop", NOW0 + 4, aid="w1", atype="murmuration:author", last_assistant_message="e")], group="handback"))
    out.append(Scn("hb_corrupt", [("file", "__statera__/handbacks/wave-03-author-w03-2.md", "garbage ## hand-back 1 | not-a-time | agent_id=h1 type=a event=b status=delivered bytes=3 sha256=abc\n[model output]\n\nxyz\n"), ("meta", "h1", {"name": "author-w03-2"}),
                                 stop(NOW0, last_assistant_message="again"), stop(NOW0 + 1)], group="handback"))
    return out


MALFORMED = [b"", b"  ", b"not json", b"[]", b"null", b"{}", b"\xef\xbb\xbf{}", b"\xff\xfe{}", b"[" * 20000, b"{\"cwd\": 1e999, \"x\": NaN, \"agent_id\": 1" + b"9" * 5000 + b"}", b'{"a": 1} x', b'{"cwd": "{LAB}", "agent_id": "x", "agent_type": 7}', b'{"cwd": "{LAB}", "agent_id": "x", "agent_type": "murmuration:author", "hook_event_name": "PostToolBatch", "tool_calls": 5}',
             b'{"cwd": 5, "hook_event_name": "SubagentStop", "agent_id": "x"}', b'{"cwd": ["a"], "hook_event_name": "SubagentStart", "agent_id": "x", "agent_type": "murmuration:author"}', b'{"cwd": "{LAB}", "hook_event_name": "SubagentStop", "agent_id": "x", "last_assistant_message": 5}',
             b'{"cwd": "{LAB}", "hook_event_name": "PostToolUse", "tool_name": "SubagentHandback", "agent_id": "x", "tool_input": "str"}', b'{"cwd": "{LAB}", "hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_input": []}', b'{"cwd": "{LAB}", "hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_input": {"subagent_type": 5}}']


def malformed_scns():
    out = []
    for i, raw in enumerate(MALFORMED):
        out.append(Scn("mal%d" % i, [("raw", "budget", raw, NOW0), ("raw", "handback", raw, NOW0 + 1)], group="malformed"))
    return out


def fuzz_scns(n, seed):
    rnd = random.Random(seed)
    kinds = ["SubagentStart", "PostToolBatch", "PostToolUse", "SubagentStop", "PreToolUse", "Other", None, 5]
    vals = lambda: rnd.choice([None, True, False, 0, 1, 2.5, "", "x", "murmuration:author", "Agent", "SubagentHandback", [], [1], {}, {"a": 1}, "aé", "\ud800", "a\x00b", {"subagent_type": "murmuration:author", "prompt": "Budget: USD 1\n", "name": "n"}, [{"tool_name": "SubagentHandback"}, 3], 10 ** 25, "{LAB}", "/"])
    out = []
    for i in range(n):
        base = dict(cwd="{LAB}", hook_event_name=rnd.choice(kinds), transcript_path="{SESS}.jsonl", agent_id=rnd.choice(["f1", "f2"]), agent_type=rnd.choice(["murmuration:author", "murmuration:explorer", "x:y"]), permission_mode=rnd.choice(["default", "auto", None]),
                    tool_name=rnd.choice(["Bash", "Agent", "Task", "SubagentHandback"]), tool_calls=[dict(tool_name="Bash")], tool_use_id="tu%d" % i, tool_input={"message": "m", "subagent_type": "murmuration:author", "prompt": "Budget: USD 2\n"}, last_assistant_message=rnd.choice(["text", None, "  "]))
        for _ in range(rnd.randint(0, 3)):
            base[rnd.choice(list(base) + ["extra"])] = vals()
        if rnd.random() < 0.15:
            base.pop(rnd.choice(list(base)), None)
        which = rnd.choice(["budget", "handback"])
        recs = [rec_user("Your name is author-w09-9.\nBudget: USD 0.5\n"), rec_asst("r1", rnd.choice([100, 40000, 90000]))]
        out.append(Scn("fuzz%d" % i, [("tx", "f1", lines_of(recs)), ("tx", "f2", lines_of(recs)), ("ev", which, base, NOW0), ("ev", which, base, NOW0 + 1)], group="fuzz"))
    return out


def real_scns(paths, seed, budget_mod):
    out = []
    rnd = random.Random(seed)
    for i, p in enumerate(paths):
        aid = os.path.basename(p)[len("agent-"):-len(".jsonl")]
        try:
            seen = budget_mod.scan(p)
        except Exception:
            seen = None
        total = seen["usd"] if seen else 0.0
        target = rnd.choice([0.3, 0.6, 0.8, 0.92, 0.97, 1.3, 1.7, 2.1])
        B = round(total / target, 6) if total > 0 else 1.0
        steps = [("txcopy", aid, p, 0.25)]
        steps.append(("file", ".harness/%s.json" % aid, json.dumps(canon_state(B=B, role="author"))))
        steps.append(ev("budget", "SubagentStart", NOW0 + 1, aid=aid, mode=rnd.choice(["default", "auto"])))
        for j, f in enumerate((0.3, 0.6, 0.85, 1.0)):
            steps.append(("txcopy", aid, p, f))
            steps.append(ev("budget", "PostToolBatch", NOW0 + 10 * (j + 1), aid=aid, tool_calls=[dict(tool_name="Bash")]))
            steps.append(ev("budget", "PostToolUse", NOW0 + 10 * (j + 1) + 1, aid=aid, tool_name="Bash"))
        steps.append(ev("budget", "SubagentStop", NOW0 + 100, aid=aid))
        out.append(Scn("real%d_seeded" % i, steps, group="real"))
        steps = [("txcopy", aid, p, 0.3), ev("budget", "SubagentStart", NOW0 + 1, aid=aid, mode="default")]
        for j, f in enumerate((0.6, 1.0)):
            steps.append(("txcopy", aid, p, f))
            steps.append(ev("budget", "PostToolBatch", NOW0 + 30 * (j + 1), aid=aid, tool_calls=[dict(tool_name="Bash")]))
        steps.append(ev("budget", "SubagentStop", NOW0 + 100, aid=aid))
        steps.append(ev("handback", "SubagentStop", NOW0 + 101, aid=aid, last_assistant_message="hand-back text of %d" % i, agent_transcript_path="{SESS}/subagents/agent-%s.jsonl" % aid))
        out.append(Scn("real%d_fresh" % i, steps, group="real"))
    return out


# ---- execution ----

def subst(o, lab, sess):
    if isinstance(o, str):
        return o.replace("{LAB}", lab).replace("{SESS}", sess)
    if isinstance(o, list):
        return [subst(x, lab, sess) for x in o]
    if isinstance(o, dict):
        return {subst(k, lab, sess): subst(v, lab, sess) for k, v in o.items()}
    return o


def snap(lab):
    out = {}
    for root, dirs, files in os.walk(lab):
        for d in dirs:
            out[os.path.relpath(os.path.join(root, d), lab) + "/"] = b""
        for f in files:
            p = os.path.join(root, f)
            try:
                out[os.path.relpath(p, lab)] = open(p, "rb").read()
            except OSError:
                out[os.path.relpath(p, lab)] = b"<unreadable>"
    return out


def run_proc(cmd, raw, now, env_extra, repo, timeout=60):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "MURMURATION_NOW")}
    env.update(LC_ALL="en_US.UTF-8", CLAUDE_PLUGIN_ROOT=repo, MURMURATION_NOW=repr(now))
    env.update(env_extra)
    try:
        p = subprocess.run(cmd, input=raw, capture_output=True, timeout=timeout, env=env, cwd="/private/tmp")
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return "timeout", b"", b""


class Ctx:
    """One implementation's lab and session folders for one scenario."""

    def __init__(self, scn, impl, base, a):
        self.scn, self.impl, self.a = scn, impl, a
        shutil.rmtree(base, ignore_errors=True)
        self.base = base
        self.lab, self.sess = os.path.join(base, "lab"), os.path.join(base, "sess")
        os.makedirs(os.path.join(self.sess, "subagents"))
        os.makedirs(self.lab)
        if not scn.nolab:
            os.makedirs(os.path.join(self.lab, "__statera__"))
        self.dlog = os.path.join(base, "delegate.log")

    def do(self, st):
        lab, sess, a = self.lab, self.sess, self.a
        kind = st[0]
        out = None
        if kind == "tx":
            open(os.path.join(sess, "subagents", "agent-%s.jsonl" % st[1]), "w").write(st[2])
        elif kind == "txraw":
            open(os.path.join(sess, "subagents", "agent-%s.jsonl" % st[1]), "wb").write(st[2])
        elif kind == "txcopy":
            lines = open(st[2], "rb").read().splitlines(keepends=True)
            open(os.path.join(sess, "subagents", "agent-%s.jsonl" % st[1]), "wb").write(b"".join(lines[:max(1, int(len(lines) * st[3]))]))
            m = st[2][:-6] + ".meta.json"
            if os.path.exists(m):
                shutil.copy(m, os.path.join(sess, "subagents", "agent-%s.meta.json" % st[1]))
        elif kind == "meta":
            json.dump(st[2], open(os.path.join(sess, "subagents", "agent-%s.meta.json" % st[1]), "w"))
        elif kind == "file":
            p = os.path.join(lab, st[1])
            if st[1].startswith(".harness"):
                p = os.path.join(lab, "__statera__", st[1])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            body = subst(st[2], lab, sess)
            if a.realclock:
                body = body.replace(repr(NOW0), repr(time.time()))
            open(p, "w", encoding="utf-8", errors="surrogatepass").write(body)
        else:
            which = st[1]
            if kind == "ev":
                raw = json.dumps(subst(st[2], lab, sess)).encode("utf-8", "surrogatepass")
            else:
                raw = st[2].replace(b"{LAB}", lab.encode())
            now = st[3]
            if self.impl == "py" and a.realclock:
                cmd = [sys.executable, "-S", "-I", os.path.join(a.repo, "scripts", "run_hook.py"), which]
            elif self.impl == "py":
                cmd = [sys.executable, "-S", "-I", os.path.join(a.repo, "__instrumenta__", "w08c1_pyshim.py"), os.path.join(a.repo, "scripts"), which]
            else:
                cmd = [a.rust, which]
            extra = {"MURMURATION_DELEGATE_LOG": self.dlog, "MURMURATION_DELEGATE_SHIM": os.path.join(a.repo, "__instrumenta__", "w08c1_pyshim.py")}
            out = run_proc(cmd, raw, now, extra, a.repo)
        return out, snap(lab)

    def delegated(self):
        return len(open(self.dlog).read().split()) if os.path.exists(self.dlog) else 0


def run_scn(scn, impl, root, a):
    ctx = Ctx(scn, impl, os.path.join(root, scn.name), a)
    res = []
    for i, st in enumerate(scn.steps):
        out, sn = ctx.do(st)
        res.append((i, st[0], out, sn))
    return res, ctx.delegated()


# the fields that follow the clock, compared within a tolerance in the real-clock pass
TIMEY = {"active_s": 1.0, "acc": 1.0, "run_start": 1.0, "last_seen": 1.0, "minutes_at": 0.05, "t_frac": 0.001, "t": 1.0}


def tol_equal(a, b, name):
    if a == b:
        return True
    if name.endswith("harness.jsonl") or (name.startswith("__statera__/.harness") and name.endswith(".json")) or "pending" in name:
        try:
            la = [json.loads(x) for x in a.decode().splitlines() if x] if name.endswith(".jsonl") else [json.loads(a.decode())]
            lb = [json.loads(x) for x in b.decode().splitlines() if x] if name.endswith(".jsonl") else [json.loads(b.decode())]
        except Exception:
            return False
        if len(la) != len(lb):
            return False
        for x, y in zip(la, lb):
            if set(x) != set(y):
                return False
            for k in x:
                if k == "t" and isinstance(x[k], str):
                    continue
                if k == "which" and x[k] != y[k] and "t_frac" in x and "frac" in x and abs(x["t_frac"] - x["frac"]) <= 0.001:
                    continue   # the two fractions are within the clock's noise of each other: which one decided is not fixed
                if k in TIMEY:
                    if isinstance(x[k], (int, float)) and isinstance(y[k], (int, float)):
                        if abs(x[k] - y[k]) > TIMEY[k]:   # the two implementations run back to back on the real clock
                            return False
                    elif x[k] != y[k]:
                        return False
                    continue
                if x[k] != y[k]:
                    return False
        return True
    if "handbacks" in name:
        sub = lambda s: re.sub(rb"\| \d{4}-\d\d-\d\dT[\d:+-]+ \|", b"| T |", s)
        return sub(a) == sub(b)
    return False


def compare(scn, ra, rb, realclock):
    diffs = []
    for (i, k, oa, sa), (_, _, ob, sb) in zip(ra, rb):
        if oa is not None:
            if oa[0] != ob[0]:
                diffs.append((scn.name, i, "rc", oa[0], ob[0]))
            if oa[1] != ob[1] and not (realclock and tol_stdout(oa[1], ob[1])):
                diffs.append((scn.name, i, "stdout", oa[1][:300], ob[1][:300]))
            if oa[2] != ob[2]:
                diffs.append((scn.name, i, "stderr", oa[2][:200], ob[2][:200]))
        names = set(sa) | set(sb)
        norm = (lambda n: re.sub(r"^(.*pending/)\d+\.\d+-", r"\1", n)) if realclock else (lambda n: n)
        sa2, sb2 = {norm(n): v for n, v in sa.items()}, {norm(n): v for n, v in sb.items()}
        for n in sorted(set(sa2) | set(sb2)):
            if n not in sa2 or n not in sb2:
                diffs.append((scn.name, i, "file-presence", n, n in sa2))
            elif sa2[n] != sb2[n] and not (realclock and tol_equal(sa2[n], sb2[n], n)):
                diffs.append((scn.name, i, "file", n, (sa2[n][-400:], sb2[n][-400:])))
    return diffs


def tol_stdout(a, b):
    sub = lambda s: re.sub(rb"\d+\.\d of ", b"M of ", s)
    return sub(a) == sub(b)


def one(scn, a, root):
    if a.realclock:
        return one_lockstep(scn, a, root)
    ra, _ = run_scn(scn, "py", root, a)
    rb, deleg = run_scn(scn, "rs", root, a)
    steps_ev = sum(1 for s in scn.steps if s[0] in ("ev", "raw"))
    return scn, compare(scn, ra, rb, a.realclock), steps_ev, deleg


def one_lockstep(scn, a, root):
    """Real clock: both implementations run each step back to back (order alternating), in two folders; the folder names are normalized in what is compared."""
    base = os.path.join(root, scn.name)
    shutil.rmtree(base, ignore_errors=True)
    cp, cr = Ctx(scn, "py", os.path.join(base, "py"), a), Ctx(scn, "rs", os.path.join(base, "rs"), a)
    ra, rb = [], []
    for i, st in enumerate(scn.steps):
        first, second = (cp, cr) if i % 2 == 0 else (cr, cp)
        o1 = first.do(st)
        o2 = second.do(st)
        oa, ob = (o1, o2) if first is cp else (o2, o1)
        ra.append((i, st[0], oa[0], oa[1]))
        rb.append((i, st[0], ob[0], ob[1]))
    unpath = lambda r, ctx: [(i, k, None if o is None else (o[0], o[1].replace(ctx.base.encode(), b"BASE"), o[2].replace(ctx.base.encode(), b"BASE")), {n: v.replace(ctx.base.encode(), b"BASE") for n, v in sn.items()}) for i, k, o, sn in r]
    steps_ev = sum(1 for x in scn.steps if x[0] in ("ev", "raw"))
    return scn, compare(scn, unpath(ra, cp), unpath(rb, cr), True), steps_ev, cr.delegated()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rust", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--realclock", action="store_true")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--transcripts", type=int, default=150)
    ap.add_argument("--fuzz", type=int, default=600)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.repo, "scripts"))
    import budget
    rnd = random.Random(a.seed)
    allt = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/agent-*.jsonl")), key=lambda p: (os.path.getsize(p), p))
    allt = [p for p in allt if os.path.getsize(p) > 1000]
    n = 12 if a.quick else a.transcripts
    idx = sorted(set([int(i * (len(allt) - 1) / max(1, n - 1)) for i in range(n)]))
    chosen = [allt[i] for i in idx]
    scns = [threshold_scn("thr_auto"), threshold_scn("thr_default", mode="default"), raise_scn("raises"), time_scn("time10"), time_scn("time0_5", T=0.5, B=5), dispatch_scn("disp_plain"), dispatch_scn("disp_mixed", mixed=True), dispatch_scn("disp_expire", mixed=True, expire=True), dispatch_scn("disp_floor", floor=True)]
    scns += weird_budget_scns() + handback_scns() + malformed_scns() + fuzz_scns(60 if a.quick else a.fuzz, a.seed) + real_scns(chosen, a.seed, budget)
    if a.realclock:
        scns = [x for x in scns if not x.name.startswith("time")]
    scns.append(Scn("nolab_budget", [ev("budget", "SubagentStart", NOW0, aid="n1", atype="murmuration:author"), ev("budget", "PostToolBatch", NOW0 + 1, aid="n1", atype="murmuration:author")], nolab=True, group="nolab"))
    os.makedirs(a.out, exist_ok=True)
    root = os.path.join(a.scratch, "replay-real" if a.realclock else "replay-exact")
    os.makedirs(root, exist_ok=True)
    t0 = time.time()
    summary, alld = {}, []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for scn, diffs, nev, deleg in ex.map(lambda s: one(s, a, root), scns):
            g = summary.setdefault(scn.group, dict(scenarios=0, events=0, delegated=0, differing_events=0, differing_scenarios=0))
            g["scenarios"] += 1
            g["events"] += nev
            g["delegated"] += deleg
            if diffs:
                g["differing_scenarios"] += 1
                g["differing_events"] += len({(d[0], d[1]) for d in diffs})
                alld += diffs
    tot = {k: sum(g[k] for g in summary.values()) for k in ("scenarios", "events", "delegated", "differing_events", "differing_scenarios")}
    res = dict(mode="realclock" if a.realclock else "exact", transcripts=len(chosen), seconds=round(time.time() - t0, 1), groups=summary, total=tot)
    json.dump(res, open(os.path.join(a.out, "replay_%s.json" % res["mode"]), "w"), indent=1)
    with open(os.path.join(a.out, "replay_%s_diffs.txt" % res["mode"]), "w") as fh:
        for d in alld[:300]:
            fh.write(repr(d)[:1500] + "\n")
    with open(os.path.join(a.out, "replay_%s_transcripts.txt" % res["mode"]), "w") as fh:
        fh.write("\n".join("%d %s" % (os.path.getsize(p), os.path.basename(p)) for p in chosen) + "\n")
    print(json.dumps(res, indent=1))
    return 1 if alld else 0


if __name__ == "__main__":
    sys.exit(main())
