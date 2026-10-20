#!/usr/bin/env python3
"""The selftest of budget.py, kept out of it so that the hook's process does not compile it at every call. Run: `python3 scripts/budget.py --selftest`."""
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = os.path.join(HERE, "budget.py")
sys.path.insert(0, HERE)
import budget  # noqa: E402
from budget import *  # noqa: E402,F401,F403  (the names the checks use)


def selftest():
    import subprocess
    import tempfile
    import threading

    import lab_status

    # 1. the price table and the formula are the ones of lab_status
    assert PRICES == lab_status.PRICES and LONG_HAIKU == lab_status.LONG_HAIKU, "price tables drifted"
    for model, use in [
        ("claude-sonnet-5-5", dict(input_tokens=7, output_tokens=1234, cache_read_input_tokens=56789, cache_creation_input_tokens=4321)),
        ("claude-opus-5-5-20260101", dict(input_tokens=1, output_tokens=2000, cache_read_input_tokens=9000,
                                         cache_creation_input_tokens=3000, cache_creation=dict(ephemeral_5m_input_tokens=1000, ephemeral_1h_input_tokens=2000))),
        ("claude-haiku-5-5", dict(input_tokens=10, output_tokens=50, cache_read_input_tokens=120000, cache_creation_input_tokens=0)),
        ("claude-sonnet-5-5", dict(input_tokens=5, output_tokens=500, speed="fast")),
    ]:
        cc = use.get("cache_creation") or {}
        req = dict(model=model, **{"in": use.get("input_tokens", 0), "out": use.get("output_tokens", 0), "cr": use.get("cache_read_input_tokens", 0),
                                   "cw": use.get("cache_creation_input_tokens", 0), "cw5": cc.get("ephemeral_5m_input_tokens", 0),
                                   "cw1": cc.get("ephemeral_1h_input_tokens", 0), "fast": use.get("speed") == "fast"})
        assert abs(usd_of(model, req) - lab_status.message_usd(model, use)) < 1e-12, (model, use)

    # 2. a transcript: a streamed request counts once, with the largest output; the brief is the first user message
    def rec_user(text):
        return json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"

    def rec_coord(text, ts="2026-10-19T09:33:45.583Z", kind="coordinator"):
        return json.dumps({"type": "user", "isMeta": True, "origin": {"kind": kind}, "timestamp": ts,
                           "message": {"role": "user", "content": "The coordinator sent a message while you were working:\n" + text + "\n\nAddress this before completing your current task."}}) + "\n"

    def rec_queued(text, kind="coordinator", ts="2026-10-19T09:33:46.583Z"):   # a message to a worker that is running: an attachment, as measured (w03-c1)
        return json.dumps({"type": "attachment", "timestamp": ts, "attachment": {"type": "queued_command", "prompt": text, "origin": {"kind": kind}}}) + "\n"

    def rec_result(text):
        return json.dumps({"type": "user", "origin": {"kind": "coordinator"}, "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": text}]}}) + "\n"

    def rec_mixed(text):   # a tool result with a text block beside it, as the platform appends reminders to tool results
        return json.dumps({"type": "user", "origin": {"kind": "coordinator"}, "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t", "content": "ok"}, {"type": "text", "text": text}]}}) + "\n"

    def rec_asst(rid, out, cr=0, cw=0, model="claude-sonnet-5-5", inp=2, chars=0):
        return json.dumps({"type": "assistant", "requestId": rid, "message": {"id": "m" + rid, "model": model,
                                                                              "content": [{"type": "text", "text": "x" * chars}], "usage": dict(
            input_tokens=inp, output_tokens=out, cache_read_input_tokens=cr, cache_creation_input_tokens=cw)}}) + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "t.jsonl")
        open(f, "w").write(rec_user("Your name is author-w09-1.\nBudget: USD 0.50\nGo.") + rec_user("Budget: USD 9") + rec_asst("r1", 10) +
                           rec_asst("r1", 1000000) + rec_asst("r2", 0, cr=1000000) + rec_asst("r3", 0, model="<synthetic>", inp=0))
        got = scan(f)[0]
        assert got["requests"] == 2 and abs(got["usd"] - (10 + 0.10 * 1) - 8e-6) < 1e-9, got   # 1M output (10.0) + 1M cache read (0.10) + 4 input tokens
        assert patterns()[0].search(got["brief"]).group(1) == "0.50" and "Budget: USD 9" not in got["brief"], "the first user message only"
        assert got["raises"] == [], "a second user message that is not from the coordinator is not a raise"
        assert scan(os.path.join(tmp, "missing")) == (None, None)
        # output: the content length stands in for the output count when it is larger; the same message streamed twice counts once
        open(f, "w").write(rec_asst("r1", 10, chars=13000) + rec_asst("r1", 10, chars=13000) + rec_asst("r2", 5000, chars=100))
        got = scan(f)[0]
        assert abs(got["usd"] - (10000 + 5000) * 10 / 1e6 - 8e-6) < 1e-9 and abs(got["usd_recorded"] - 5010 * 10 / 1e6 - 8e-6) < 1e-9, got
        # raises: only a coordinator's plain message counts; a tool result, another origin and a line that is not exact do not; the spend before it is kept
        open(f, "w").write(rec_user("Budget: USD 1.00") + rec_asst("a", 1000) + rec_coord("Budget: USD 2.5\nTime: min 7\nGo on.") + rec_asst("b", 1000) +
                           rec_coord("Budget: USD 9", kind="peer") + rec_result("Budget: USD 8\nTime: min 8") + rec_mixed("Budget: USD 7") + rec_coord("Budget: USD 4 more\nplease") + rec_coord("Time: min 3.5") +
                           rec_queued("Budget: USD 6", kind="peer") + rec_queued("Budget: USD 1.5\nHow is it going?"))
        got = scan(f)[0]
        assert [(r["x"], r["t"]) for r in got["raises"]] == [(2.5, 7.0), (None, 3.5), (1.5, None)], got["raises"]
        assert abs(got["raises"][0]["usd_at"] - 1000 * 10 / 1e6 - 4e-6) < 1e-9 and abs(got["raises"][1]["usd_at"] - 2000 * 10 / 1e6 - 8e-6) < 1e-9 and got["raises"][0]["ts"], got["raises"]

    # 2b. reading in pieces equals reading at once: the old algorithm (the whole file, every time) is the reference; random transcripts, cut anywhere
    def scan_reference(path):
        reqs, brief, raises = {}, None, []
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if brief is None and '"user"' in line:
                    rec = json.loads(line)
                    if rec.get("type") == "user":
                        brief = plain_text((rec.get("message") or {}).get("content")) or ""
                elif '"origin"' in line:
                    rec = json.loads(line)
                    att = rec.get("attachment") or {}
                    if rec.get("type") == "user":
                        text, origin = plain_text((rec.get("message") or {}).get("content")), rec.get("origin")
                    elif att.get("type") == "queued_command":
                        text, origin = att.get("prompt") if isinstance(att.get("prompt"), str) else None, att.get("origin")
                    else:
                        text, origin = None, None
                    if text and (origin or {}).get("kind") == "coordinator":
                        usd, mins = patterns()[0].search(text), patterns()[1].search(text)
                        if (usd and float(usd.group(1)) > 0) or (mins and float(mins.group(1)) > 0):
                            raises.append(dict(x=float(usd.group(1)) if usd and float(usd.group(1)) > 0 else None,
                                               t=float(mins.group(1)) if mins and float(mins.group(1)) > 0 else None, ts=epoch(rec.get("timestamp")), n=len(reqs)))
                if '"usage"' not in line:
                    continue
                rec = json.loads(line)
                msg, use = rec.get("message") or {}, (rec.get("message") or {}).get("usage")
                if rec.get("type") != "assistant" or not isinstance(use, dict):
                    continue
                cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
                got = dict(in_=use.get("input_tokens"), out=use.get("output_tokens"), cr=use.get("cache_read_input_tokens"),
                           cw=use.get("cache_creation_input_tokens"), cw5=cc.get("ephemeral_5m_input_tokens"), cw1=cc.get("ephemeral_1h_input_tokens"))
                got = {k.rstrip("_"): int(v or 0) for k, v in got.items()}
                key = rec.get("requestId") or msg.get("id") or rec.get("uuid")
                old = reqs.setdefault(key, dict(model=msg.get("model"), fast=False, blocks=set(), **{k: 0 for k in got}))
                for k, v in got.items():
                    old[k] = max(old[k], v)
                old["blocks"].update(block_text(b) for b in msg.get("content") or [] if isinstance(b, dict))
                old["fast"] = old["fast"] or use.get("speed") == "fast"
                old["model"] = old["model"] if old["model"] and old["model"] != "<synthetic>" else msg.get("model")
        est = {k: dict(r, out=max(r["out"], int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN) if CHARS_PER_TOKEN else 0)) for k, r in reqs.items()}
        costs = [usd_of(r["model"], r) for r in est.values()]
        live = [r for r in reqs.values() if r["model"] != "<synthetic>" or r["in"] + r["out"] + r["cr"] + r["cw"]]
        for r in raises:
            r["usd_at"] = sum(costs[:r.pop("n")])
        return dict(brief=brief, usd=sum(costs), usd_recorded=sum(usd_of(r["model"], r) for r in reqs.values()), requests=len(live),
                    unpriced=sum(base_model(r["model"]) not in PRICES for r in live), raises=raises)

    import random
    rnd = random.Random(20261020)
    models = ["claude-sonnet-5-5", "claude-opus-5-5-20260101", "claude-haiku-5-5", "claude-mystery-1", "<synthetic>", None]

    def random_transcript(n):
        lines = [rec_user("Your name is x-w1-1.\nBudget: USD 2\nTime: min 9\nGo.\n")]
        rid = 0
        for i in range(n):
            what = rnd.random()
            if what < 0.55:   # a request: 1 to 3 records, sometimes repeated, sometimes a block text equal to another
                rid += 1
                model = rnd.choice(models)
                for j in range(rnd.randint(1, 3)):
                    text = rnd.choice(["same text", "", "x" * rnd.randint(1, 3000), "é\u2028ü"])
                    blocks = [{"type": "text", "text": text}, {"type": "tool_use", "id": "t", "name": "Bash", "input": {"command": rnd.choice(["ls", "cat f" * 40])}}][:rnd.randint(0, 2)]
                    use = dict(input_tokens=rnd.randint(0, 9), output_tokens=rnd.randint(0, 900), cache_read_input_tokens=rnd.randint(0, 150000),
                               cache_creation_input_tokens=rnd.randint(0, 20000))
                    if rnd.random() < 0.3:
                        use["cache_creation"] = dict(ephemeral_5m_input_tokens=rnd.randint(0, 5000), ephemeral_1h_input_tokens=rnd.randint(0, 5000))
                    if rnd.random() < 0.1:
                        use["speed"] = "fast"
                    lines.append(json.dumps({"type": "assistant", "requestId": "r%d" % rid, "message": {"id": "m%d" % rid, "model": model, "content": blocks, "usage": use}}) + "\n")
            elif what < 0.62:
                lines.append(rec_coord("Budget: USD %d\nTime: min %d\nGo." % (rnd.randint(0, 3), rnd.randint(0, 3)), ts="2026-10-19T09:%02d:00Z" % rnd.randint(0, 59)))
            elif what < 0.66:
                lines.append(rec_queued("Budget: USD 1.5\nHow is it going?", kind=rnd.choice(["coordinator", "peer"])))
            elif what < 0.72:
                lines.append(rec_result("Budget: USD 8"))
            else:
                lines.append(json.dumps({"type": "attachment", "attachment": {"type": "other", "text": "usage origin user"}}) + "\n")
        return lines

    for seed_round in range(6):
        for open_keep in (1, 3):
            budget.CARRY_OPEN = open_keep
            lines = random_transcript(rnd.randint(20, 120))
            with tempfile.TemporaryDirectory() as tmp:
                f, g = os.path.join(tmp, "t.jsonl"), os.path.join(tmp, "whole.jsonl")
                blob, carry, pos = "".join(lines).encode("utf-8"), None, 0
                while pos < len(blob):
                    pos = min(len(blob), pos + rnd.randint(1, 4000))
                    open(f, "wb").write(blob[:pos])
                    open(g, "wb").write(blob[:blob[:pos].rfind(b"\n") + 1])   # what the reference can read: complete lines
                    got, carry = scan(f, carry if rnd.random() < 0.9 else None)   # now and then a read from the start: the same answer
                    want = scan_reference(g)
                    for k in ("usd", "usd_recorded", "requests", "unpriced", "raises"):
                        assert got[k] == want[k], (seed_round, open_keep, pos, k, got[k], want[k])
                    if carry["off"] == 0 or blob[:carry["off"]].count(b"\n") == 1 or got["brief"] is not None:
                        assert got["brief"] is None or got["brief"] == want["brief"]
                # the guards: a changed past, a shorter file and a finished request named again make a read from the start, and the same answer
                head = blob[:blob.rfind(b"\n") + 1]
                open(f, "wb").write(head)
                got, carry = scan(f, None)
                altered = head.replace(b"Your name is", b"Your name iz", 1) if b"Your name is" in head[:200] else head
                open(f, "wb").write(altered + b"\n")
                open(g, "wb").write(altered + b"\n")
                got2, _ = scan(f, carry)
                assert got2["usd"] == scan_reference(g)["usd"] and got2["raises"] == scan_reference(g)["raises"]
                open(f, "wb").write(head[:len(head) // 2][:head[:len(head) // 2].rfind(b"\n") + 1])
                open(g, "wb").write(head[:len(head) // 2][:head[:len(head) // 2].rfind(b"\n") + 1])
                got3, _ = scan(f, carry)   # shorter than the carry's offset
                assert got3["usd"] == scan_reference(g)["usd"] and got3["requests"] == scan_reference(g)["requests"]
    budget.CARRY_OPEN = 3
    with tempfile.TemporaryDirectory() as tmp:   # a finished request named again: read from the start, so it merges as before
        f = os.path.join(tmp, "t.jsonl")
        budget.CARRY_OPEN = 1
        open(f, "w").write(rec_user("Budget: USD 1") + rec_asst("a", 100) + rec_asst("b", 200) + rec_asst("c", 300))
        _, carry = scan(f, None)
        open(f, "a").write(rec_asst("a", 5000))
        got, _ = scan(f, carry)
        assert got["requests"] == 3 and abs(got["usd"] - (5000 + 200 + 300) * 10 / 1e6 - 3 * 4e-6) < 1e-9, got
        budget.CARRY_OPEN = 3
        # a line that is not finished waits for its newline; a half line is not an error
        open(f, "w").write(rec_user("Budget: USD 1") + rec_asst("a", 100) + rec_asst("b", 200)[:-1])
        got, carry = scan(f, None)
        assert got["requests"] == 1
        open(f, "a").write("\n")
        got, carry = scan(f, carry)
        assert got["requests"] == 2

    for text, want in [("Budget: USD 1.5", 1.5), ("x\nBudget: USD 4\ny", 4.0), ("Budget: USD 2 more", None), ("budget: usd 2", None),
                       ("  Budget: USD 2", None), ("Budget: USD 0", None), ("", None), (None, None)]:
        assert budget_for("author", text)[0] == (want or 3.0), (text, want)
    assert [budget_for(r, "")[0] for r in ("explorer", "author", "reproducer", "proof-adversary", "depth-reviewer")] == [3.0, 3.0, 2.0, 2.0, 2.0]
    for text, want in [("Time: min 1.5", 1.5), ("x\nTime: min 4\ny", 4.0), ("Time: min 2 more", None), ("time: min 2", None), ("Time: min 0", None), ("Time: 3 min", None), (None, None)]:
        assert time_for("author", text)[0] == (want or 20.0), (text, want)
    assert [time_for(r, "")[0] for r in ("explorer", "author", "reproducer", "proof-adversary", "depth-reviewer")] == [20.0, 20.0, 15.0, 15.0, 15.0]

    # 3. the text, exactly; the schedule's thresholds; whole percent (100 only from 1.0)
    assert line(0.93, 1.0, 2.14, 4) == "Spent 0.93 of USD 1.00 (93%); 2.1 of 4 min (54%)", line(0.93, 1.0, 2.14, 4)
    assert line(1.234, 3.0, 20.0, 20.0) == "Spent 1.23 of USD 3.00 (41%); 20.0 of 20 min (100%)"
    assert line(0.9999, 1.0, 0.0, 1.5) == "Spent 1.00 of USD 1.00 (99%); 0.0 of 1.5 min (0%)", line(0.9999, 1.0, 0.0, 1.5)
    assert note_text(0.5, 1.0, 1.0, 10, 0.5) == "Spent 0.50 of USD 1.00 (50%); 1.0 of 10 min (10%)", "below 1.0 the line is the whole note"
    assert note_text(1.0, 1.0, 1.0, 10, 1.0) == ("Spent 1.00 of USD 1.00 (100%); 1.0 of 10 min (10%). If one or two more steps finish the result, finish it. "
                                                 "Otherwise hand back now: what you have, what is missing, and what more budget would buy.")
    assert [due(f) for f in (0, 0.49, 0.5, 0.74, 0.75, 0.874, 0.875, 0.9374, 0.9375, 2)] == [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
    assert all(x in start_note(3.0, 20.0, "brief") for x in ("USD 3.00 and 20 minutes (from your brief)", "50%, 75%, 87.5% and 93.75%", "at every step from 100%", "holds the money", "select:mcp__plugin_colgrep-mcp_colgrep__search,mcp__plugin_colgrep-mcp_colgrep__find_files", "`limit: 5`"))
    assert start_note(3.0, 20.0, "brief").endswith('then `search` with `paths: ["__instrumenta__"]` and `limit: 5`.')

    # 4. hooks end to end, in a temporary lab (the way the platform runs the script, and in-process where time is set)
    def fire(cwd, **kw):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run([sys.executable, BUDGET], input=json.dumps(dict(cwd=cwd, **kw)), capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and not proc.stderr, (proc.returncode, proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else None

    def logged(tmp):
        try:
            return [json.loads(x) for x in open(os.path.join(tmp, "__statera__", "harness.jsonl"))]
        except OSError:
            return []

    def ctx(answer):
        return answer["hookSpecificOutput"]["additionalContext"]

    with tempfile.TemporaryDirectory() as tmp:
        sess = os.path.join(tmp, "s")
        sub = os.path.join(sess, "subagents")
        os.makedirs(sub)
        ev = dict(agent_id="a1", agent_type="murmuration:reproducer", transcript_path=sess + ".jsonl", permission_mode="auto")
        tx = os.path.join(sub, "agent-a1.jsonl")
        assert fire(tmp, hook_event_name="SubagentStart", **ev) is None and not os.path.exists(os.path.join(tmp, "__statera__")), "no lab, no action"
        os.makedirs(os.path.join(tmp, "__statera__"))
        assert fire(tmp, hook_event_name="SubagentStart", **dict(ev, agent_type="general-purpose")) is None, "other agent types: no-op"
        assert fire(tmp, hook_event_name="SubagentStart", **{k: v for k, v in ev.items() if k != "agent_id"}) is None, "main thread: no-op"
        assert logged(tmp) == []
        # the dispatch (PreToolUse on Agent) keeps the brief's figures; the start note states them; a figure below the floor is logged and kept
        brief = "Your name is reproducer-w09-1.\nBudget: USD 1.00\nTime: min 100\nGo.\n"
        assert fire(tmp, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_1", tool_input=dict(subagent_type="murmuration:reproducer", prompt=brief, name="reproducer-w09-1")) is None
        assert fire(tmp, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_x", tool_input=dict(subagent_type="general-purpose", prompt=brief)) is None
        assert fire(tmp, hook_event_name="PreToolUse", tool_name="Agent", agent_id="zz", agent_type="murmuration:author", tool_use_id="toolu_y", tool_input=dict(subagent_type="murmuration:reproducer", prompt=brief)) is None
        assert len(os.listdir(os.path.join(tmp, "__statera__", ".harness", "pending"))) == 1, "one dispatch record: the other agent type and the call inside a subagent leave none"
        start = ctx(fire(tmp, hook_event_name="SubagentStart", **ev))
        assert "USD 1.00 and 100 minutes (from your brief)" in start and "93.75%" in start and "hand back" in start, start
        assert not os.listdir(os.path.join(tmp, "__statera__", ".harness", "pending")), "the record is used once"
        assert open(os.path.join(tmp, "__statera__", ".harness", ".gitignore")).read() == "*\n"
        assert [x["event"] for x in logged(tmp)] == ["start"] and logged(tmp)[0]["name"] == "reproducer-w09-1" and logged(tmp)[0]["B"] == 1.0 and logged(tmp)[0]["T"] == 100.0 and logged(tmp)[0]["source"] == "brief"
        # the schedule: B = 1.00. 0.49 quiet; 0.50 one note, only the line; again quiet; a jump to 0.80 sends one note, with the figures of now
        post = dict(hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash", tool_use_id="t")], **ev)
        use = dict(hook_event_name="PostToolUse", tool_name="Bash", **ev)
        cum = []

        def spend(rid, usd):   # one more request of this price
            cum.append(rec_asst(rid, int(round(usd / 10 * 1e6)) - 0) if usd else "")
            open(tx, "w").write(rec_user(brief) + "".join(cum))

        spend("r1", 0.49)
        assert fire(tmp, **post) is None and fire(tmp, **use) is None
        spend("r2", 0.0105)
        answer = fire(tmp, **post)
        assert answer["hookSpecificOutput"]["hookEventName"] == "PostToolBatch", answer
        got = ctx(answer)
        assert re.fullmatch(r"Spent 0\.50 of USD 1\.00 \(50%\); 0\.\d of 100 min \(0%\)", got), got
        spend("r3", 0.02)
        assert fire(tmp, **post) is None, "0.52: the next threshold is 0.75"
        spend("r4", 0.28)
        got = ctx(fire(tmp, **post))
        assert got.startswith("Spent 0.80 of USD 1.00 (80%)") and "finish" not in got and "hand back" not in got, got   # skipped 0.75: one note, current figures
        spend("r5", 0.07)
        assert fire(tmp, **post) is None, "0.87: below 0.875"
        spend("r6", 0.01)
        assert ctx(fire(tmp, **post)).startswith("Spent 0.88 of USD 1.00 (88%)"), "0.875"
        spend("r7", 0.056)
        assert fire(tmp, **post) is None, "0.936: below 0.9375"
        spend("r8", 0.002)
        assert ctx(fire(tmp, **post)).startswith("Spent 0.94 of USD 1.00 (94%)")
        spend("r9", 0.04)
        assert fire(tmp, **post) is None, "0.98"
        spend("r10", 0.03)
        over = ctx(fire(tmp, **post))
        assert re.fullmatch(r"Spent 1\.01 of USD 1\.00 \(101%\); 0\.\d of 100 min \(0%\)\. " + re.escape(OVER_SENTENCE), over), over
        spend("r11", 0.01)
        assert ctx(fire(tmp, **post)).endswith(OVER_SENTENCE), "from 1.0 every check sends a note"
        assert fire(tmp, **dict(post, tool_calls=[dict(tool_name="SubagentHandback")])) is None, "a batch that holds the hand-back gets no note"
        assert fire(tmp, **use) is None, "PostToolUse sends nothing below the ceiling"
        assert fire(tmp, hook_event_name="PostToolBatch", **dict(ev, agent_id="a9")) is None, "unknown agent: no transcript, no action"
        notes = [x for x in logged(tmp) if x["event"] == "note"]
        assert [x["over"] for x in notes] == [False] * 4 + [True] * 2 and [round(x["frac"], 2) for x in notes] == [0.5, 0.8, 0.88, 0.94, 1.01, 1.02], notes
        # the ceiling: PostToolUse blocks from 1.5; parallel calls (concurrent hook processes) send one block; the batch's PostToolBatch is then quiet
        spend("r12", 0.49)
        outs = []
        threads = [threading.Thread(target=lambda: outs.append(fire(tmp, **dict(use, tool_use_id="p%d" % i)))) for i in range(4)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        blocks = [o for o in outs if o]
        assert len(blocks) == 1 and blocks[0]["decision"] == "block" and "continue" not in blocks[0], outs
        assert re.match(r"Spent 1\.51 of USD 1\.00 \(151%\); 0\.\d of 100 min \(0%\)\. Hand back now with SubagentHandback", blocks[0]["reason"]) and "more budget" in blocks[0]["reason"], blocks[0]
        assert fire(tmp, **post) is None, "the block was this check's message"
        spend("r12b", 0.001)
        assert fire(tmp, **dict(use, tool_name="SubagentHandback")) is None, "the hand-back call is never blocked, on a request no block has covered yet"
        spend("r13", 0.01)
        assert ctx(fire(tmp, **post)).endswith(OVER_SENTENCE), "a later batch gets its note again"
        assert fire(tmp, **use)["decision"] == "block", "and its block"
        spend("r14", 0.01)
        assert fire(tmp, **use)["decision"] == "block"
        spend("r15", 0.01)
        halt = fire(tmp, **use)   # after HALT_AFTER (3) blocks the next one is the backstop
        assert halt["continue"] is False and halt["stopReason"].startswith("Spent 1.54 of USD 1.00") and "decision" not in halt, halt
        fire(tmp, hook_event_name="SubagentStop", **ev)
        assert [x["event"] for x in logged(tmp)].count("stop") == 3 and logged(tmp)[-2]["event"] == "halt" and logged(tmp)[-1]["event"] == "end", [x["event"] for x in logged(tmp)]
        last = logged(tmp)[-1]
        assert last["name"] == "reproducer-w09-1" and last["mode"] == "auto" and 1.53 < last["frac"] < 1.55 and "content chars" in last["basis"] and last["used_recorded"] <= last["used"], last

    # 5. the raise, and active time, in process (the clock is set by `now`): a message from the coordinator raises from that moment
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "__statera__"))
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        ev = dict(cwd=tmp, agent_id="b1", agent_type="murmuration:author", transcript_path=sess + ".jsonl", permission_mode="auto")
        tx = os.path.join(sess, "subagents", "agent-b1.jsonl")
        brief = "Your name is author-w09-2.\nBudget: USD 1.00\nTime: min 10\nGo.\n"

        def ev_(kind, **kw):
            return dict(ev, hook_event_name=kind, **kw)

        def call(now, kind, **kw):
            return handle(ev_(kind, **kw), now=now)

        T0 = 1_000_000.0
        open(tx, "w").write(rec_user(brief))
        start = call(T0, "SubagentStart")   # a new worker whose transcript is not there yet is the production case; here it is, so the brief is read
        assert "USD 1.00 and 10 minutes (from your brief)" in ctx(start), start
        body = rec_user(brief) + rec_asst("a", 120000)           # 1.20 USD: over budget
        open(tx, "w").write(body)
        got = ctx(call(T0 + 120, "PostToolBatch", tool_calls=[dict(tool_name="Bash")]))
        assert got.startswith("Spent 1.20 of USD 1.00 (120%); 2.0 of 10 min (20%). If one or two more steps"), got
        call(T0 + 150, "SubagentStop")                           # hand-back: the run lasted 150 s
        st = load_state(tmp, "b1")
        assert abs(st["acc"] - 150) < 1e-6 and st["run_open"] is False
        # the idle gap (3 hours) does not count: the resume starts a new run; a plain resume (no lines) changes no limit and the worker is still over
        R = T0 + 150 + 3 * 3600
        assert call(R, "SubagentStart") is None, "a resume has no start note: the platform does not deliver it"
        assert [x["resumed"] for x in logged(tmp) if x["event"] == "start"] == [False, True], logged(tmp)
        body += rec_asst("b", 1000)                              # 0.01 more
        open(tx, "w").write(body)
        got = ctx(call(R + 10, "PostToolBatch", tool_calls=[dict(tool_name="Bash")]))
        assert got.startswith("Spent 1.21 of USD 1.00 (121%); 2.7 of 10 min (27%). If one or two"), "no raise line: still over, active time = 150 s + 10 s: " + got
        # a raise by the PI: the message arrives after the start; limit = max(limit, spend at the message) + x, minutes likewise; not over straight away
        call(R + 20, "SubagentStop")
        R2 = R + 7200
        call(R2, "SubagentStart")
        body += rec_coord("Budget: USD 1.0\nTime: min 5\nGo on with the check.", ts=datetime.datetime.fromtimestamp(R2 + 1, datetime.timezone.utc).isoformat())
        open(tx, "w").write(body)
        assert call(R2 + 2, "PostToolBatch", tool_calls=[dict(tool_name="Bash")]) is None, "after a raise to 2.21 / 15.0 min: 55% and 18%: no note until 0.75"
        st = load_state(tmp, "b1")
        assert abs(st["B"] - 2.21) < 1e-4 and abs(st["T"] - (max(10, 171 / 60.0) + 5)) < 0.01 and st["k"] == 1, st   # spent 1.21; 171 s active at the message (150 + 20 + 1)
        raise_log = [x for x in logged(tmp) if x["event"] == "raise"]
        assert len(raise_log) == 1 and raise_log[0]["add_usd"] == 1.0 and raise_log[0]["add_min"] == 5.0 and raise_log[0]["B_before"] == 1.0, raise_log
        body += rec_asst("c", 56000)                             # 1.21 + 0.56 = 1.77: 0.80 of 2.21
        open(tx, "w").write(body)
        got = ctx(call(R2 + 30, "PostToolBatch", tool_calls=[dict(tool_name="Bash")]))
        assert got.startswith("Spent 1.77 of USD 2.21 (80%); ") and "hand back" not in got, "the schedule resumes above the new fraction: " + got
        assert call(R2 + 31, "PostToolBatch", tool_calls=[dict(tool_name="Bash")]) is None
        # the same raise is not applied twice; a tool result, another origin and the brief's own lines are no raise
        body += rec_result("Budget: USD 50\nTime: min 50") + rec_coord("Budget: USD 50", kind="peer") + rec_asst("d", 1000)
        open(tx, "w").write(body)
        call(R2 + 40, "PostToolBatch", tool_calls=[dict(tool_name="Bash")])
        assert abs(load_state(tmp, "b1")["B"] - 2.21) < 1e-4 and len([x for x in logged(tmp) if x["event"] == "raise"]) == 1
        # a mid-run raise of the minutes only: the USD limit stays; time over before, not over after
        ev2 = dict(ev, agent_id="b2")
        tx2 = os.path.join(sess, "subagents", "agent-b2.jsonl")
        handle(dict(ev2, hook_event_name="SubagentStart"), now=T0)   # a new worker: no transcript yet
        open(tx2, "w").write(rec_user("Budget: USD 5.00\nTime: min 3\n") + rec_asst("a", 1000))
        got = ctx(handle(dict(ev2, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), now=T0 + 200))
        assert got.startswith("Spent 0.01 of USD 5.00 (0%); 3.3 of 3 min (111%). If one or two"), got
        open(tx2, "a").write(rec_coord("Time: min 4", ts=datetime.datetime.fromtimestamp(T0 + 210, datetime.timezone.utc).isoformat()))
        assert handle(dict(ev2, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), now=T0 + 220) is None
        st = load_state(tmp, "b2")
        assert st["B"] == 5.0 and abs(st["T"] - (3.5 + 4)) < 0.01, st   # 210 s = 3.5 min active at the message; + 4
        # the mid-run state: a hook added during a run counts from the transcript's start and reads the brief's lines
        ev3 = dict(ev, agent_id="b3")
        open(os.path.join(sess, "subagents", "agent-b3.jsonl"), "w").write(rec_user("Budget: USD 0.20\nTime: min 2\n") + rec_asst("a", 15000))
        got = ctx(handle(dict(ev3, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), now=T0))
        assert got.startswith("Spent 0.15 of USD 0.20 (75%)"), got
        assert handle(dict(ev3, hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), now=T0 + 1) is None, "two thresholds passed at once: one note, then quiet"

    # 5b. parallel calls in process, with a slow state write between load and save: the lock makes them take turns, so one block is sent
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "__statera__"))
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        ev = dict(cwd=tmp, agent_id="d1", agent_type="murmuration:author", transcript_path=sess + ".jsonl")
        handle(dict(ev, hook_event_name="SubagentStart"), now=1.0)
        open(os.path.join(sess, "subagents", "agent-d1.jsonl"), "w").write(rec_user("Budget: USD 1.00\nTime: min 100\n") + rec_asst("a", 160000))
        real_save, outs = budget.save_state, []

        def slow_save(root, aid, st):
            time.sleep(0.15)
            real_save(root, aid, st)

        budget.save_state = slow_save
        try:
            threads = [threading.Thread(target=lambda: outs.append(handle(dict(ev, hook_event_name="PostToolUse", tool_name="Bash"), now=2.0))) for _ in range(4)]
            [t.start() for t in threads]
            [t.join() for t in threads]
        finally:
            budget.save_state = real_save
        assert len([o for o in outs if o]) == 1 and [o for o in outs if o][0]["decision"] == "block", outs
        assert load_state(tmp, "d1")["stops"] == 1

    # 6. the floor: a brief below it is logged as a warning and not raised; the start note says what the brief says
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "__statera__"))
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        ev = dict(cwd=tmp, agent_type="murmuration:explorer", transcript_path=sess + ".jsonl")
        handle(dict(ev, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="u1",
                    tool_input=dict(subagent_type="murmuration:explorer", name="explorer-w09-1", prompt="Your name is explorer-w09-1.\nBudget: USD 0.05\nTime: min 2\n")), now=5.0)
        handle(dict(ev, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="u2",
                    tool_input=dict(subagent_type="murmuration:explorer", name="explorer-w09-2", prompt="Your name is explorer-w09-2.\nBudget: USD 0.30\nTime: min 3\n")), now=6.0)
        warns = [x for x in logged(tmp) if x["event"] == "warn"]
        assert [(x["name"], x["what"], x["value"], x["floor"]) for x in warns] == [("explorer-w09-1", "budget_usd", 0.05, 0.30), ("explorer-w09-1", "time_min", 2.0, 3.0)], warns
        # two parallel dispatches of one type with different figures: the start note does not guess
        got = ctx(handle(dict(ev, agent_id="c1", hook_event_name="SubagentStart"), now=7.0))
        assert "USD 0.05 and 2 minutes" not in got and "set by the `Budget: USD <number>`" in got, got
        tx = os.path.join(sess, "subagents", "agent-c1.jsonl")
        open(tx, "w").write(rec_user("Your name is explorer-w09-1.\nBudget: USD 0.05\nTime: min 2\n") + rec_asst("a", 1000))
        assert [x for x in logged(tmp) if x["event"] == "start"][-1]["B"] == 3.0   # what the start note could know: the defaults
        handle(dict(ev, agent_id="c1", hook_event_name="PostToolBatch", tool_calls=[dict(tool_name="Bash")]), now=8.0)
        st = load_state(tmp, "c1")
        assert st["B"] == 0.05 and st["T"] == 2.0, "the brief's figure stands, below the floor, and is not raised: %r" % st
        assert len([x for x in logged(tmp) if x["event"] == "warn"]) == 2, "one warning per figure, at the dispatch"
        # the second start sees no other record, but the first start marked it: it does not guess either (starts in either order)
        got2 = ctx(handle(dict(ev, agent_id="c3", hook_event_name="SubagentStart"), now=7.5))
        assert "USD 0.30 and 3 minutes" not in got2 and "set by the `Budget: USD <number>`" in got2, got2
        # a stale record is dropped and not used
        handle(dict(ev, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="u3", tool_input=dict(subagent_type="murmuration:explorer", prompt="Budget: USD 9\n")), now=100.0)
        got = ctx(handle(dict(ev, agent_id="c2", hook_event_name="SubagentStart"), now=100.0 + PENDING_TTL + 5))
        assert "USD 3.00 and 20 minutes (the defaults for your role" in got, got

    # 7. the registration: the check on PostToolBatch, the ceiling on PostToolUse, the dispatch on Agent
    hooks = json.load(open(os.path.join(HERE, "..", "hooks", "hooks.json")))["hooks"]
    for event, matcher in (("SubagentStart", None), ("PostToolBatch", None), ("PostToolUse", None), ("SubagentStop", None), ("PreToolUse", "Agent|Task")):
        assert any(("budget.py" in h["command"]) and g.get("matcher") == matcher for g in hooks[event] for h in g["hooks"]), (event, matcher)
    assert subprocess.run([sys.executable, BUDGET], input="not json", capture_output=True, text=True).returncode == 0
    # 8. the commands of hooks.json, as the platform starts them (`sh -c`): the sh test lets a worker's event through to the script and keeps the main thread's away from Python
    root = os.path.abspath(os.path.join(HERE, ".."))
    cmds = {}
    for event in ("PostToolUse", "PostToolBatch"):
        found = [h["command"] for g in hooks[event] if g.get("matcher") is None for h in g["hooks"] if "budget.py" in h["command"]]
        assert len(found) == 1, (event, found)
        cmds[event] = found[0]
    assert all(c.count("python3 -S -I -B") == 1 for c in cmds.values()), cmds
    for event, cmd in cmds.items():
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "__statera__"))
            sess = os.path.join(tmp, "s")
            os.makedirs(os.path.join(sess, "subagents"))
            ev = dict(cwd=tmp, agent_id="g1", agent_type="murmuration:author", transcript_path=sess + ".jsonl", hook_event_name=event, tool_name="Bash",
                      tool_calls=[dict(tool_name="Bash")], tool_response="the word agent_id inside a result, and \"agent_id\" escaped")
            open(os.path.join(sess, "subagents", "agent-g1.jsonl"), "w").write(rec_user("Budget: USD 1.00\nTime: min 10\n") + rec_asst("a", 120000))

            def sh(payload, text=None):
                env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root)
                env.pop("CLAUDE_PROJECT_DIR", None)
                proc = subprocess.run(["/bin/sh", "-c", cmd], input=text if text is not None else json.dumps(payload) + "\n", capture_output=True, text=True, env=env)
                assert proc.returncode == 0 and not proc.stderr, (proc.returncode, proc.stderr)
                return proc.stdout
            main_ev = {k: v for k, v in ev.items() if k not in ("agent_id", "agent_type")}
            assert sh(main_ev) == "" and not os.listdir(os.path.join(tmp, "__statera__")), "the main thread: the sh test stops it before Python, nothing is written"
            assert sh(main_ev, json.dumps(main_ev, indent=2)) == "", "a payload on several lines is read whole"
            out = sh(ev)
            if event == "PostToolBatch":
                assert "hookSpecificOutput" in out and "Spent 1.20 of USD 1.00 (120%)" in json.loads(out)["hookSpecificOutput"]["additionalContext"], out
            assert os.path.exists(os.path.join(tmp, "__statera__", ".harness", "g1.json")), "a worker's event reaches the script"
            sh(ev, json.dumps(ev))   # no newline at the end of the payload: read all the same, no error
    print("PASS budget")
