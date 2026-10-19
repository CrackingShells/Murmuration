#!/usr/bin/env python3
"""Give each Murmuration worker a budget in USD, tell it once at 80 percent, stop it at 100 percent.

Runs as a hook on SubagentStart, PostToolUse and SubagentStop. It reads the hook JSON from stdin.
It does nothing outside an initialized lab (a folder with `__statera__/`), for the main thread, and
for any agent whose type is not `murmuration:<role>`.

  SubagentStart  `additionalContext`: the budget B and a short contract. The worker is told that one
                 note comes at about 80 percent of B, that it is genuine, to finish the item in hand
                 then and hand back the deliverable with what it did not cover, and that at about
                 100 percent the harness stops the run.
  PostToolUse    spend so far, from the subagent's own transcript. At 0.8 B one `additionalContext`
                 note, once per agent. At 1.0 B `decision: block` with a reason that says to hand back
                 now, on every call from there (the agent can still call the hand-back tool and the
                 hand-back is never blocked). At 1.5 B, only after 3 such notices went unheeded,
                 `continue: false`: the run ends and, measured, the hand-back is lost (see below), so this is
                 a backstop, not the stop.
  SubagentStop   one `end` line in the log, with the spend at the end (the overshoot is read from it).

Why `block` and not `continue: false` at 1.0 B: `continue: false` ended the subagent at once, without
the hand-back, in 6 of 8 headless runs (w02-c3); `decision: block` gives the reason to the agent, which then hands back.

B is in USD. Default by role: explorer 3.0, author 3.0, reproducer 2.0, proof-adversary 2.0 (any other
murmuration role 2.0). A line of exactly the form `Budget: USD <number>` in the agent's first user
message (its brief) replaces the default; the transcript does not exist yet at SubagentStart, so the
start note says so and the hook reads the line from the first PostToolUse on. A resumed agent starts a
new run: the spend already in its transcript is the baseline, B applies to what it spends from there.

Spend is the list price of the tokens in the subagent's transcript: input, cache read, cache write for
5 minutes and for 1 hour, which are exact, and output. In `auto` permission mode the transcript holds only
8 to 15 percent of the output as a count (explorer-w02-a, w01-c2), so the recorded output is a lower
bound there (the log's `used_recorded`). The thresholds use the larger of the recorded count and an
estimate from the message content (`CHARS_PER_TOKEN`); the log's `used` is that figure. The price
table is the one `lab_status.py` uses (w02-c1, https://platform.claude.com/docs/en/about-claude/pricing,
fetched 2026-10-19); the selftest checks that the two agree.

State per agent: `__statera__/.harness/<agent_id>.json` (git-ignored by a `.gitignore` inside the folder).
Log, one JSON line per `start`, `note`, `stop`, `halt`, `end` and `deny` (the deny is written by `handback.py`):
`__statera__/harness.jsonl`.

The script never fails an agent: anything unexpected is dropped and it exits 0 with no output.

Usage:
    budget.py              read a hook event from stdin
    budget.py --selftest   check the script on a temporary project
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import handback  # noqa: E402  (a sibling script: one place that finds the lab, the agent's name, and writes the log)

DEFAULT = {"explorer": 3.0, "author": 3.0, "reproducer": 2.0, "proof-adversary": 2.0}
OTHER_ROLE = 2.0
NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.5
HALT_AFTER = 3   # the backstop needs this many earlier stop notices: an agent that hands back and then writes its report is not halted
BRIEF_LINE = re.compile(r"^Budget: USD (\d+(?:\.\d+)?)[ \t]*$", re.M)

# USD per million tokens: input, output, cache read, cache write 5 minutes, cache write 1 hour.
# The rows of `lab_status.PRICES` (w02-c1); [source: https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-19].
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5, 4.0),
    "claude-fable-5-1": (10.0, 50.0, 0.25, 12.5, 20.0),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125, 0.20),
}
LONG_HAIKU = (0.50, 2.50, 0.05, 0.625, 1.0)  # Haiku 5.5 above 100,000 prompt tokens
PRICE_FOR_UNKNOWN = "claude-opus-5-5"  # a model with no row is priced at the highest common row, and counted
# The transcript keeps an output count taken at the start of the stream, 8 to 15 percent of the real one (w01-c2, explorer-w02-a),
# but the full content of each message. Output is therefore the larger of the recorded count and the content length divided by
# CHARS_PER_TOKEN: 1.3 is the median (1.26, rounded) ratio of content characters (text plus the JSON of tool inputs) to the exact output
# tokens of 7 sonnet worker runs (range 0.96 to 1.52; `calibrate.py` in the w02-c3 folder). It is an ESTIMATE; set it to 0 to count
# the recorded output only.
CHARS_PER_TOKEN = 1.3


def usd_of(model, req):
    """USD of one API request at list price; `req` holds the max of each usage field over its records."""
    p = PRICES.get(re.sub(r"-\d{8}$", "", model or ""))
    if p is None:
        p = PRICES[PRICE_FOR_UNKNOWN]
    elif model.startswith("claude-haiku-5-5") and req["in"] + req["cr"] + req["cw"] > 100000:
        p = LONG_HAIKU
    cw5 = req["cw5"] + max(0, req["cw"] - req["cw5"] - req["cw1"])  # a write with no recorded split is charged at the 5 minute rate
    usd = (req["in"] * p[0] + req["out"] * p[1] + req["cr"] * p[2] + cw5 * p[3] + req["cw1"] * p[4]) / 1e6
    return usd * (2.0 if req["fast"] else 1.0)


def block_text(block):
    """What a content block adds to the output: its text or thinking, or the JSON of a tool call's input."""
    return json.dumps(block["input"], sort_keys=True) if "input" in block else str(block.get("text") or block.get("thinking") or "")


def scan(path):
    """Read a subagent transcript once: its first user message and its spend.

    Returns dict(brief, usd, requests, unpriced), or None when the file cannot be read. Records of one
    request (same requestId) are merged by the maximum of each usage field, so a streamed request counts once."""
    reqs, brief = {}, None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if brief is None and '"user"' in line:
                    rec = json.loads(line)
                    if rec.get("type") == "user":
                        content = (rec.get("message") or {}).get("content")
                        brief = content if isinstance(content, str) else "\n".join(
                            b.get("text", "") for b in content or [] if isinstance(b, dict))
                if '"usage"' not in line:
                    continue
                rec = json.loads(line)
                msg, use = rec.get("message") or {}, (rec.get("message") or {}).get("usage")
                if rec.get("type") != "assistant" or not isinstance(use, dict):
                    continue
                cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
                got = dict(in_=use.get("input_tokens"), out=use.get("output_tokens"), cr=use.get("cache_read_input_tokens"),
                           cw=use.get("cache_creation_input_tokens"), cw5=cc.get("ephemeral_5m_input_tokens"),
                           cw1=cc.get("ephemeral_1h_input_tokens"))
                got = {k.rstrip("_"): int(v or 0) for k, v in got.items()}
                key = rec.get("requestId") or msg.get("id") or rec.get("uuid")
                old = reqs.setdefault(key, dict(model=msg.get("model"), fast=False, blocks=set(), **{k: 0 for k in got}))
                for k, v in got.items():
                    old[k] = max(old[k], v)
                old["blocks"].update(block_text(b) for b in msg.get("content") or [] if isinstance(b, dict))
                old["fast"] = old["fast"] or use.get("speed") == "fast"
                old["model"] = old["model"] if old["model"] and old["model"] != "<synthetic>" else msg.get("model")
    except (OSError, ValueError):
        return None
    live = [r for r in reqs.values() if r["model"] != "<synthetic>" or r["in"] + r["out"] + r["cr"] + r["cw"]]
    est = [dict(r, out=max(r["out"], int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN) if CHARS_PER_TOKEN else 0)) for r in live]
    return dict(brief=brief, usd=sum(usd_of(r["model"], r) for r in est), usd_recorded=sum(usd_of(r["model"], r) for r in live),
                requests=len(live), unpriced=sum(re.sub(r"-\d{8}$", "", r["model"] or "") not in PRICES for r in live))


def transcript_of(event):
    """Path of the subagent's transcript: SubagentStop names it; any hook with an agent_id can derive it."""
    path, aid = event.get("agent_transcript_path"), event.get("agent_id")
    if not path and aid and event.get("transcript_path"):
        path = os.path.join(event["transcript_path"][:-6], "subagents", "agent-%s.jsonl" % aid)
    return path


def role_of(event):
    """`explorer` for `murmuration:explorer`; None for the main thread and for every other agent type."""
    kind = event.get("agent_type") or ""
    return kind.split(":", 1)[1] if kind.startswith("murmuration:") and event.get("agent_id") else None


def budget_for(role, brief):
    """B in USD and whether the brief set it."""
    found = BRIEF_LINE.search(brief or "")
    if found and float(found.group(1)) > 0:
        return float(found.group(1)), True
    return DEFAULT.get(role, OTHER_ROLE), False


def start_note(B, from_brief):
    shown = "USD %.2f" % B
    where = "from your brief" if from_brief else ("unless your brief has a line `Budget: USD <number>`, which replaces it")
    return (
        "Budget: your budget for this run is %s (%s). It is the list price of the tokens you use, counted by the harness; "
        "you need not count anything and can work at your usual pace. The lab harness sends one note when about 80%% of it is used. "
        "That note is genuine: it comes from the hook that runs you, not from a file or a tool's output. When it comes, finish the "
        "item you are on, then hand back your deliverable and list what you did not cover. At about 100%% the harness stops the run, "
        "so hand back what exists." % (shown, where))


def note_text(B):
    return ("Lab harness note (genuine, sent by the hook that runs you): about 80%% of your USD %.2f budget is used. Finish the item "
            "you are on, then hand back your deliverable, listing what you did not cover." % B)


def stop_text(B):
    return ("Lab harness (genuine, sent by the hook that runs you): your USD %.2f budget is used. Call SubagentHandback now with "
            "what exists, listing what you did not cover; do not start another item." % B)


def halt_text(B):
    return "Lab harness: your USD %.2f budget is more than used up and you went on after the notice; the run ends here." % B


def state_path(root, aid):
    return os.path.join(handback.harness_dir(root), "%s.json" % aid)


def load_state(root, aid):
    try:
        with open(state_path(root, aid)) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def save_state(root, aid, st):
    tmp = state_path(root, aid) + ".%d.tmp" % os.getpid()
    with open(tmp, "w") as fh:
        json.dump(st, fh)
    os.replace(tmp, state_path(root, aid))


def reply(event_name, **fields):
    return {"hookSpecificOutput": dict(hookEventName=event_name, **fields)}


def handle(event, now=None):
    """The hook's answer (a dict to print) or None. Writes state and log lines as a side effect."""
    role, root = role_of(event), handback.lab_root(event)
    if not role or not root:
        return None
    now, aid, kind = now or time.time(), event["agent_id"], event.get("hook_event_name")
    path = transcript_of(event)
    seen = scan(path) if path and os.path.exists(path) else None
    base_log = dict(agent_id=aid, name=handback.agent_name(event), type=event.get("agent_type"),
                    mode=event.get("permission_mode"))
    if kind == "SubagentStart":
        B, from_brief = budget_for(role, seen and seen["brief"])
        old = load_state(root, aid)   # a state file or an existing transcript: this agent is resumed, a new run begins
        base = seen["usd"] if seen else 0.0
        save_state(root, aid, dict(role=role, B=B, base=base, base_recorded=seen["usd_recorded"] if seen else 0.0, start=now, noted=False, stops=0))
        handback.log_line(root, dict(base_log, event="start", B=B, from_brief=from_brief, resumed=bool(old or seen), base_usd=round(base, 6)))
        return reply(kind, additionalContext=start_note(B, from_brief))
    if not seen:
        return None
    st = load_state(root, aid)
    if st is None:   # no SubagentStart seen (hook added mid-run): start counting from nothing
        st = dict(role=role, B=budget_for(role, seen["brief"])[0], base=0.0, start=now, noted=False, stops=0)
    B, from_brief = budget_for(role, seen["brief"])   # the brief's line wins over what the start note could say
    used = seen["usd"] - st["base"]
    fields = dict(B=B, used=round(used, 6), used_recorded=round(seen["usd_recorded"] - st.get("base_recorded", 0.0), 6), frac=round(used / B, 4),
                  requests=seen["requests"], unpriced=seen["unpriced"],
                  elapsed_s=round(now - st["start"], 1))
    if kind == "SubagentStop":
        handback.log_line(root, dict(base_log, event="end", noted=st["noted"], stops=st["stops"], **fields))
        return None
    if kind != "PostToolUse" or event.get("tool_name") == "SubagentHandback":
        return None
    if used >= HARD_AT * B and st["stops"] >= HALT_AFTER:
        st.update(B=B, noted=True, stops=st["stops"] + 1)
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="halt", n=st["stops"], **fields))
        return {"continue": False, "stopReason": halt_text(B)}
    if used >= STOP_AT * B:
        st.update(B=B, noted=True, stops=st["stops"] + 1)
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="stop", n=st["stops"], **fields))
        return {"decision": "block", "reason": stop_text(B)}
    if used >= NOTE_AT * B and not st["noted"]:
        st.update(B=B, noted=True)
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="note", **fields))
        return reply(kind, additionalContext=note_text(B))
    if st["B"] != B:
        st["B"] = B
        save_state(root, aid, st)
    return None


def selftest():
    import subprocess
    import tempfile

    sys.path.insert(0, HERE)
    import lab_status

    # 1. the price table and the formula are the ones of lab_status (w02-c1)
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

    def rec_asst(rid, out, cr=0, cw=0, model="claude-sonnet-5-5", inp=2, chars=0):
        return json.dumps({"type": "assistant", "requestId": rid, "message": {"id": "m" + rid, "model": model,
                                                                              "content": [{"type": "text", "text": "x" * chars}], "usage": dict(
            input_tokens=inp, output_tokens=out, cache_read_input_tokens=cr, cache_creation_input_tokens=cw)}}) + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "t.jsonl")
        open(f, "w").write(rec_user("Your name is author-w09-1.\nBudget: USD 0.50\nGo.") + rec_user("Budget: USD 9") + rec_asst("r1", 10) +
                           rec_asst("r1", 1000000) + rec_asst("r2", 0, cr=1000000) + rec_asst("r3", 0, model="<synthetic>", inp=0))
        got = scan(f)
        assert got["requests"] == 2 and abs(got["usd"] - (10 + 0.10 * 1) - 8e-6) < 1e-9, got   # 1M output (10.0) + 1M cache read (0.10) + 4 input tokens
        assert BRIEF_LINE.search(got["brief"]).group(1) == "0.50" and "Budget: USD 9" not in got["brief"], "the first user message only"
        assert scan(os.path.join(tmp, "missing")) is None
        # output: the content length stands in for the output count when it is larger; the same message streamed twice counts once
        open(f, "w").write(rec_asst("r1", 10, chars=13000) + rec_asst("r1", 10, chars=13000) + rec_asst("r2", 5000, chars=100))
        got = scan(f)
        assert abs(got["usd"] - (10000 + 5000) * 10 / 1e6 - 8e-6) < 1e-9 and abs(got["usd_recorded"] - 5010 * 10 / 1e6 - 8e-6) < 1e-9, got
    for text, want in [("Budget: USD 1.5", 1.5), ("x\nBudget: USD 4\ny", 4.0), ("Budget: USD 2 more", None), ("budget: usd 2", None),
                       ("  Budget: USD 2", None), ("Budget: USD 0", None), ("", None), (None, None)]:
        assert budget_for("author", text)[0] == (want or 3.0), (text, want)
    assert [budget_for(r, "")[0] for r in ("explorer", "author", "reproducer", "proof-adversary", "depth-reviewer")] == [3.0, 3.0, 2.0, 2.0, 2.0]

    # 3. hooks, end to end through the script (the way the platform runs it)
    def fire(cwd, **kw):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(dict(cwd=cwd, **kw)), capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and not proc.stderr, (proc.returncode, proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else None

    def logged(tmp):
        try:
            return [json.loads(x) for x in open(os.path.join(tmp, "__statera__", "harness.jsonl"))]
        except OSError:
            return []

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
        start = fire(tmp, hook_event_name="SubagentStart", **ev)["hookSpecificOutput"]
        assert start["hookEventName"] == "SubagentStart" and "USD 2.00" in start["additionalContext"] and "80%" in start["additionalContext"] \
            and "genuine" in start["additionalContext"] and "hand back" in start["additionalContext"], start
        assert open(os.path.join(tmp, "__statera__", ".harness", ".gitignore")).read() == "*\n"
        # the brief sets B to 1.00: 0.79 used is quiet, 0.80 gives one note, then quiet, 1.00 stops (every time), the hand-back call is never stopped
        post = dict(hook_event_name="PostToolUse", tool_name="Bash", **ev)
        open(tx, "w").write(rec_user("Your name is reproducer-w09-1.\nBudget: USD 1.00\n") + rec_asst("r1", 79000))        # 0.79 USD
        assert fire(tmp, **post) is None
        open(tx, "a").write(rec_asst("r2", 1000))                                                                          # 0.80 USD
        note = fire(tmp, **post)["hookSpecificOutput"]
        assert note["hookEventName"] == "PostToolUse" and "USD 1.00" in note["additionalContext"] and "80%" in note["additionalContext"], note
        open(tx, "a").write(rec_asst("r3", 5000))                                                                          # 0.85 USD
        assert fire(tmp, **post) is None, "one note per agent"
        open(tx, "a").write(rec_asst("r4", 15000))                                                                         # 1.00 USD
        stop = fire(tmp, **post)
        assert stop["decision"] == "block" and "continue" not in stop and "handback" in stop["reason"].lower() and "USD 1.00" in stop["reason"], stop
        assert fire(tmp, **dict(post, tool_name="SubagentHandback")) is None, "the hand-back call is not stopped"
        assert fire(tmp, hook_event_name="PreToolUse", tool_name="Bash", **ev) is None
        assert fire(tmp, **post)["decision"] == "block", "the notice repeats while the agent goes on"
        open(tx, "a").write(rec_asst("r4b", 50000))                                                                        # 1.50 USD
        assert fire(tmp, **post)["decision"] == "block", "an agent that has had only two notices is not halted: it may be writing its report"
        halt = fire(tmp, **post)
        assert halt["continue"] is False and "USD 1.00" in halt["stopReason"] and "decision" not in halt, halt
        fire(tmp, hook_event_name="SubagentStop", **ev)
        lines = logged(tmp)
        assert [x["event"] for x in lines] == ["start", "note", "stop", "stop", "stop", "halt", "end"], lines
        assert lines[1]["name"] == "reproducer-w09-1" and lines[1]["B"] == 1.0 and 0.80 <= lines[1]["frac"] < 0.81 and lines[1]["requests"] == 2, lines[1]
        assert lines[-1]["frac"] == 1.5 and lines[-1]["stops"] == 4 and lines[-1]["noted"] and lines[-1]["mode"] == "auto", lines[-1]
        # a resumed agent: the spend so far is the baseline, the start note shows the brief's B, the flags are reset
        again = fire(tmp, hook_event_name="SubagentStart", **ev)["hookSpecificOutput"]["additionalContext"]
        assert "USD 1.00 (from your brief)" in again, again
        assert fire(tmp, **post) is None, "a new run starts from zero"
        open(tx, "a").write(rec_asst("r5", 80000))
        assert "80%" in fire(tmp, **post)["hookSpecificOutput"]["additionalContext"], "the note comes again in the new run"
        assert logged(tmp)[-2]["event"] == "start" and logged(tmp)[-2]["resumed"] is True and abs(logged(tmp)[-2]["base_usd"] - 1.5) < 1e-3, logged(tmp)[-2:]
        assert fire(tmp, **post) is None and fire(tmp, **dict(post, agent_id="a9")) is None, "unknown agent: no transcript, no action"
        # a second agent has its own state and log name; a hook added mid-run (no SubagentStart) counts from nothing
        tx2 = os.path.join(sub, "agent-a2.jsonl")
        open(tx2, "w").write(rec_user("Budget: USD 0.10\n") + rec_asst("q1", 8000))
        got = fire(tmp, **dict(post, agent_id="a2", agent_type="murmuration:explorer"))
        assert got and "USD 0.10" in got["hookSpecificOutput"]["additionalContext"], got
        assert os.path.exists(os.path.join(tmp, "__statera__", ".harness", "a2.json"))
        assert subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json", capture_output=True, text=True).returncode == 0
    print("PASS budget")


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
        answer = handle(event) if isinstance(event, dict) else None
        if answer:
            print(json.dumps(answer))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        selftest()   # any error here is a failure and must show
        sys.exit(0)
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)
