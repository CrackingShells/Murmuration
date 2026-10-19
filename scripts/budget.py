#!/usr/bin/env python3
"""Give each Murmuration worker a budget in USD and in minutes and send it plain notes that get denser towards the limit and go on past it.

Runs as a hook on SubagentStart, PreToolUse(Agent), PostToolBatch, PostToolUse and SubagentStop. It reads the hook JSON from
stdin. It does nothing outside an initialized lab (a folder with `__statera__/`), for the main thread (except the dispatch
record below), and for any agent whose type is not `murmuration:<role>`.

  SubagentStart  `additionalContext`: the two budgets (USD B, minutes T) and the contract, in the same plain tone as the notes: a note
                 arrives at 50, 75, 87.5 and 93.75 percent of the larger of the two fractions and at every check from 100 percent;
                 from 100 percent the worker finishes if one or two more steps do it, else hands back with its case, and the PI,
                 who holds the money, decides whether to resume it with more. A resumed worker's run clock restarts (the idle gap
                 does not count); the platform does not deliver a SubagentStart `additionalContext` to a resumed worker (1 of 1 resumes), so none is sent.
  PreToolUse     On the `Agent` tool (the PI dispatching a worker): the brief's `Budget:` and `Time:` lines are put in a short-lived
  (Agent)        file, because the transcript of a new worker does not exist yet at SubagentStart; the start note reads the file. A
                 figure below the floor (USD 0.30, 3 minutes) is logged as a `warn` line and left as it is.
  PostToolBatch  The check. It fires once per batch of tool calls, after all have returned and before the next model request
                 (measured, w03-c1: 109 of 109 batches in 15 headless runs, foreground and background, single and parallel calls,
                 failed and denied calls included; PostToolUse does not fire for a failed or a denied call and fires once per call). It sends
                 at most one `additionalContext` note with the current figures: when the larger fraction has passed the next of
                 0.5, 0.75, 0.875, 0.9375 (one note however many thresholds were skipped), and at every check from 1.0.
                 Below 1.0 the note is the line `Spent X of USD Y (Z%); t of T min (W%)` and nothing else; from 1.0 the line is
                 followed by one sentence (finish, or hand back and ask). A batch that holds the hand-back call gets no note.
  PostToolUse    The hard ceiling only. From 1.5 of the larger fraction: `decision: block` with the line and "hand back now" (the
                 agent can still call the hand-back tool, which is never blocked), once per batch (the lock and the request count
                 make parallel calls send one). `decision: block` on PostToolBatch is not used for this: measured, it ends the
                 worker like `continue: false` (the run stops, no hand-back, no SubagentStop). After HALT_AFTER earlier blocks,
                 `continue: false`: the backstop; measured earlier (w02-c3) to lose the hand-back, so a backstop and not the stop.
  SubagentStop   one `end` line in the log, and the run's active time is closed.

The fractions. USD / B and active minutes / T. Active minutes are the minutes between SubagentStart and SubagentStop of each run, summed:
the idle gap between a hand-back and the resume does not count. B is in USD. Default by role: explorer 3.0, author 3.0, reproducer 2.0,
proof-adversary 2.0 (any other murmuration role 2.0). T is in minutes: explorer 20, author 20, reproducer 15, proof-adversary 15 (other
roles 15). A line of exactly the form `Budget: USD <number>`, and one of the form `Time: min <number>`, in the agent's first user message
(its brief) replace the defaults. The floor is no budget under USD 0.30 and no time under 3 minutes: with about USD 0.03 to 0.04 for the first
request of a worker, a smaller budget is used up before any note can come (w02-c8). A figure below it is logged, not changed.

The raise. A later message from the coordinator (the PI) with a line `Budget: USD x` or `Time: min t` grants that much more from that moment.
In the worker's transcript (measured, w03-c1) a message that resumes a stopped worker is a user record with `origin.kind == "coordinator"`, and a
message to a worker that is still running is an `attachment` of type `queued_command` with the same origin; a peer's message has `origin.kind == "peer"`.
The limit becomes the limit becomes
max(limit, spend at the message) + x and likewise for the minutes, so the worker is never over budget straight after a raise. The
figures are cumulative; the schedule restarts above the new fraction. A message from anyone else, a tool result, and the brief are not raises. A
resume without such a line changes nothing: the worker keeps its spend and its limits.

Spend is the list price of the tokens in the subagent's transcript: input, cache read, cache write for 5 minutes and for 1 hour, which are
exact, and output. In `auto` permission mode the transcript holds only 6 to 15 percent of the output as a count, so the recorded output is a
lower bound there (the log's `used_recorded`). The thresholds use the larger of the recorded count and an estimate from the message content
(`CHARS_PER_TOKEN`); the log's `used` is that figure and `basis` says so. The price table is the one `lab_status.py` uses
(https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-19); the selftest checks that the two agree.

State per agent: `__statera__/.harness/<agent_id>.json` (git-ignored by a `.gitignore` inside the folder), updated under a file lock and
replaced atomically. Log, one JSON line per `start`, `warn`, `raise`, `note`, `stop`, `halt`, `end` and `deny` (the deny is written by
`handback.py`): `__statera__/harness.jsonl`. `frac` is USD / B, `t_frac` is minutes / T, `which` names the budget that decided.

A hook runs only between tool calls: one tool call that runs for 10 minutes cannot be interrupted, and the time is checked when it returns.
The script never fails an agent: anything unexpected is dropped and it exits 0 with no output.

Usage:
    budget.py              read a hook event from stdin
    budget.py --selftest   check the script on a temporary project
"""
import datetime
import glob
import json
import os
import re
import sys
import time

try:
    import fcntl
except ImportError:   # no file lock on this platform: the request count still keeps parallel calls to one block in practice
    fcntl = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import handback  # noqa: E402  (a sibling script: one place that finds the lab, the agent's name, and writes the log)

DEFAULT = {"explorer": 3.0, "author": 3.0, "reproducer": 2.0, "proof-adversary": 2.0}
OTHER_ROLE = 2.0
# Starting values chosen from a few observed worker run times, not tuned: put `Time: min <n>` in a brief to set one.
TIME_DEFAULT = {"explorer": 20.0, "author": 20.0, "reproducer": 15.0, "proof-adversary": 15.0}   # minutes
OTHER_TIME = 15.0
FLOOR_USD, FLOOR_MIN = 0.30, 3.0
TIME_LINE = re.compile(r"^Time: min (\d+(?:\.\d+)?)[ \t]*$", re.M)
BRIEF_LINE = re.compile(r"^Budget: USD (\d+(?:\.\d+)?)[ \t]*$", re.M)
SCHEDULE = (0.5, 0.75, 0.875, 0.9375)   # the notes below 1.0
OVER_AT, HARD_AT = 1.0, 1.5
HALT_AFTER = 3   # the backstop needs this many earlier ceiling blocks: an agent that hands back and then writes its report is not halted
PENDING_TTL = 600   # seconds a dispatch record waits for its SubagentStart
OVER_SENTENCE = ("If one or two more steps finish the result, finish it. Otherwise hand back now: what you have, "
                 "what is missing, and what more budget would buy.")

# USD per million tokens: input, output, cache read, cache write 5 minutes, cache write 1 hour.
# The rows of `lab_status.PRICES`; [source: https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-19].
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5, 4.0),
    "claude-fable-5-1": (10.0, 50.0, 0.25, 12.5, 20.0),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125, 0.20),
}
LONG_HAIKU = (0.50, 2.50, 0.05, 0.625, 1.0)  # Haiku 5.5 above 100,000 prompt tokens
PRICE_FOR_UNKNOWN = "claude-opus-5-5"  # a model with no row is priced at the highest common row, and counted
# The transcript keeps an output count taken at the start of the stream, 6 to 15 percent of the real one in `auto` mode,
# but the full content of each message. Output is therefore the larger of the recorded count and the content length divided by
# CHARS_PER_TOKEN: 1.3 is the median (1.26, rounded) ratio of content characters (text plus the JSON of tool inputs) to the exact output
# tokens of 7 sonnet worker runs (range 0.96 to 1.52). It is an ESTIMATE; set it to 0 to count the recorded output only.
CHARS_PER_TOKEN = 1.3
BASIS = "input and cache exact; output = max(recorded, content chars / %s)" % CHARS_PER_TOKEN if CHARS_PER_TOKEN else "input and cache exact; output as recorded (a lower bound in auto mode)"


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


def plain_text(content):
    """The text of a user message, or None when it carries a tool result (a tool's output is never a message from the PI)."""
    if isinstance(content, str):
        return content
    blocks = [b for b in content or [] if isinstance(b, dict)]
    if any(b.get("type") == "tool_result" for b in blocks):
        return None
    return "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def epoch(stamp):
    try:
        return datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def scan(path):
    """Read a subagent transcript once: its first user message, its spend and the raises in it.

    Returns dict(brief, usd, usd_recorded, requests, unpriced, raises), or None when the file cannot be read. Records of one
    request (same requestId) are merged by the maximum of each usage field, so a streamed request counts once. A raise is a user
    record whose `origin.kind` is `coordinator` and whose plain text has a `Budget: USD x` or a `Time: min t` line: dict(x, t, ts, usd_at)
    with x and t the amounts (None when absent), ts the record's time (epoch seconds) and usd_at the spend of the requests before it."""
    reqs, brief, raises = {}, None, []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if brief is None and '"user"' in line:
                    rec = json.loads(line)
                    if rec.get("type") == "user":
                        brief = plain_text((rec.get("message") or {}).get("content")) or ""
                elif '"origin"' in line:
                    rec = json.loads(line)
                    att = rec.get("attachment") or {}
                    if rec.get("type") == "user":   # a worker resumed by a message: the message is a user record
                        text, origin = plain_text((rec.get("message") or {}).get("content")), rec.get("origin")
                    elif att.get("type") == "queued_command":   # a message to a worker that is still running: an attachment
                        text, origin = att.get("prompt") if isinstance(att.get("prompt"), str) else None, att.get("origin")
                    else:
                        text, origin = None, None
                    if text and (origin or {}).get("kind") == "coordinator":
                        usd, mins = BRIEF_LINE.search(text), TIME_LINE.search(text)
                        if (usd and float(usd.group(1)) > 0) or (mins and float(mins.group(1)) > 0):
                            raises.append(dict(x=float(usd.group(1)) if usd and float(usd.group(1)) > 0 else None,
                                               t=float(mins.group(1)) if mins and float(mins.group(1)) > 0 else None,
                                               ts=epoch(rec.get("timestamp")), n=len(reqs)))
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
    est = {k: dict(r, out=max(r["out"], int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN) if CHARS_PER_TOKEN else 0)) for k, r in reqs.items()}
    cost = {k: usd_of(r["model"], r) for k, r in est.items()}   # a request with no tokens costs 0, so a synthetic record adds nothing
    costs = list(cost.values())
    live = [r for r in reqs.values() if r["model"] != "<synthetic>" or r["in"] + r["out"] + r["cr"] + r["cw"]]
    for r in raises:
        r["usd_at"] = sum(costs[:r.pop("n")])
    return dict(brief=brief, usd=sum(costs), usd_recorded=sum(usd_of(r["model"], r) for r in reqs.values()),
                requests=len(live), unpriced=sum(re.sub(r"-\d{8}$", "", r["model"] or "") not in PRICES for r in live), raises=raises)


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


def time_for(role, brief):
    """T in minutes and whether the brief set it."""
    found = TIME_LINE.search(brief or "")
    if found and float(found.group(1)) > 0:
        return float(found.group(1)), True
    return TIME_DEFAULT.get(role, OTHER_TIME), False


def pct(frac):
    """Whole percent; 100 only from 1.0 on, so that a note below the limit never says it is at it."""
    p = int(frac * 100 + 0.5)
    return min(p, 99) if frac < 1.0 else max(p, 100)


def line(used, B, minutes, T):
    """The note, exactly: `Spent X of USD Y (Z%); t of T min (W%)`."""
    return "Spent %.2f of USD %.2f (%d%%); %.1f of %g min (%d%%)" % (used, B, pct(used / B), minutes, T, pct(minutes / T))


def note_text(used, B, minutes, T, frac):
    return line(used, B, minutes, T) + (". " + OVER_SENTENCE if frac >= OVER_AT else "")


def stop_text(used, B, minutes, T):
    return line(used, B, minutes, T) + ". Hand back now with SubagentHandback: what you have, what is missing, and what more budget would buy; do not start another item."


def halt_text(used, B, minutes, T):
    return line(used, B, minutes, T) + ". The run ends here."


def start_note(B, T, source):
    where = {"brief": "your budget for this run is USD %.2f and %g minutes (from your brief)",
             "default": "your budget for this run is USD %.2f and %g minutes (the defaults for your role; a line `Budget: USD <number>` or `Time: min <number>` in your brief replaces them)",
             "unknown": "your budget for this run is set by the `Budget: USD <number>` and `Time: min <number>` lines of your brief, else it is USD %.2f and %g minutes (the defaults for your role)"}[source] % (B, T)
    return (
        "Budget: %s. The harness counts both, as the list price of the tokens you use and the minutes you are active; "
        "you need not count anything and can work at your usual pace. When the larger of the two reaches 50%%, 75%%, 87.5%% and 93.75%%, and at every step from 100%%, "
        "a note comes from the hook that runs you (not from a file or a tool's output), in the form: Spent X of USD Y (Z%%); t of T min (W%%). "
        "From 100%% you choose: if one or two more steps finish the result, finish it; otherwise hand back what you have, what is missing, and what more budget would buy. "
        "The principal investigator holds the money and decides whether to resume you with more." % where)


def state_path(root, aid):
    return os.path.join(handback.harness_dir(root), "%s.json" % aid)


class locked:
    """An exclusive lock on one agent's state, so that parallel hook processes (one per tool call) take turns."""

    def __init__(self, root, aid):
        self.path = state_path(root, aid)[:-5] + ".lock"
        self.fh = None

    def __enter__(self):
        if fcntl:
            self.fh = open(self.path, "w")
            fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if self.fh:
            self.fh.close()   # closing releases the lock


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


def active_s(st, now):
    """Active seconds so far: the closed runs, plus the open one."""
    return st["acc"] + (max(0.0, now - st["run_start"]) if st["run_open"] else 0.0)


def figures(st, seen, now):
    used = seen["usd"] - st["base"]
    mins = active_s(st, now) / 60.0
    usd_frac, t_frac = used / st["B"], mins / st["T"]
    which = "USD" if usd_frac >= t_frac else "time"
    return used, mins, usd_frac, t_frac, max(usd_frac, t_frac), which


def due(frac):
    """How many of the schedule's thresholds the fraction has reached."""
    return sum(1 for t in SCHEDULE if frac >= t)


def active_at(st, ts, now):
    """Active seconds at the time `ts` of a message (clamped to this run; None: now)."""
    if ts is None or not st["run_open"]:
        return active_s(st, now)
    return st["acc"] + min(max(0.0, ts - st["run_start"]), max(0.0, now - st["run_start"]))


def apply_raises(root, st, seen, now, base_log):
    """Apply the raises in the transcript that this state has not seen. Returns True when the limits changed."""
    new = seen["raises"][st["raises_done"]:]
    for r in new:
        used_at = r["usd_at"] - st["base"]
        mins_at = active_at(st, r["ts"], now) / 60.0
        before = (st["B"], st["T"])
        if r["x"] is not None:
            st["B"] = max(st["B"], used_at) + r["x"]
        if r["t"] is not None:
            st["T"] = max(st["T"], mins_at) + r["t"]
        handback.log_line(root, dict(base_log, event="raise", add_usd=r["x"], add_min=r["t"], B_before=before[0], T_before=before[1], B=round(st["B"], 6), T=round(st["T"], 6),
                                     used_at=round(used_at, 6), minutes_at=round(mins_at, 4)))
    st["raises_done"] = len(seen["raises"])
    return bool(new)


def pending_dir(root):
    return os.path.join(handback.harness_dir(root), "pending")


def dispatch(event, root, now):
    """PreToolUse on the Agent tool: keep the brief's figures for the SubagentStart that follows; log a figure below the floor."""
    tin = event.get("tool_input") or {}
    kind = str(tin.get("subagent_type") or "")
    if not kind.startswith("murmuration:"):
        return None
    role, prompt = kind.split(":", 1)[1], tin.get("prompt") or ""
    B, b_set = budget_for(role, prompt)
    T, t_set = time_for(role, prompt)
    name = str(tin.get("name") or (re.search(r"Your name is ([a-z0-9-]+)", prompt) or [None, None])[1] or kind)
    os.makedirs(pending_dir(root), exist_ok=True)
    key = "%014.3f-%s" % (now, re.sub(r"[^A-Za-z0-9_-]", "", str(event.get("tool_use_id") or os.getpid())))
    with open(os.path.join(pending_dir(root), key + ".json"), "w") as fh:
        json.dump(dict(type=kind, B=B, T=T, b_set=b_set, t_set=t_set, t=now, name=name), fh)
    warn_floor(root, dict(name=name, type=kind), B if b_set else None, T if t_set else None)
    return None


def warn_floor(root, who, B, T):
    for what, value, floor in (("budget_usd", B, FLOOR_USD), ("time_min", T, FLOOR_MIN)):
        if value is not None and value < floor:
            handback.log_line(root, dict(who, event="warn", what=what, value=value, floor=floor,
                                         reason="below the floor; the figure is left as the brief gives it"))


def claim_pending(root, kind, now):
    """The oldest dispatch record of this agent type that is still fresh, removed; and whether other fresh records of the type disagree with it."""
    found = []
    for path in sorted(glob.glob(os.path.join(pending_dir(root), "*.json"))):
        try:
            rec = json.load(open(path))
        except (OSError, ValueError):
            continue
        if now - rec.get("t", 0) > PENDING_TTL:
            try:
                os.unlink(path)
            except OSError:
                pass
        elif rec.get("type") == kind:
            found.append((path, rec))
    for path, rec in found:
        try:
            os.unlink(path)   # whoever removes the file owns the record
        except OSError:
            continue
        rest = [(p, r) for p, r in found if p != path]
        mixed = bool(rec.get("ambiguous")) or any((r["B"], r["T"]) != (rec["B"], rec["T"]) for p, r in rest)
        if mixed:   # the later claimants must not trust their record either: whichever start comes first may have taken the wrong one
            for p, r in rest:
                try:
                    with open(p, "w") as fh:
                        json.dump(dict(r, ambiguous=True), fh)
                except OSError:
                    pass
        return rec, mixed
    return None, False


def handle(event, now=None):
    """The hook's answer (a dict to print) or None. Writes state and log lines as a side effect."""
    root = handback.lab_root(event)
    now, kind = now or time.time(), event.get("hook_event_name")
    if root and kind == "PreToolUse" and event.get("tool_name") in ("Agent", "Task") and not event.get("agent_id"):
        return dispatch(event, root, now)
    role = role_of(event)
    if not role or not root:
        return None
    aid = event["agent_id"]
    with locked(root, aid):
        return handle_locked(event, root, role, aid, kind, now)


def handle_locked(event, root, role, aid, kind, now):
    path = transcript_of(event)
    seen = scan(path) if path and os.path.exists(path) else None
    base_log = dict(agent_id=aid, name=handback.agent_name(event), type=event.get("agent_type"), mode=event.get("permission_mode"))
    st = load_state(root, aid)
    if kind == "SubagentStart":
        if st is None:
            rec, mixed = claim_pending(root, event.get("agent_type"), now)
            B, b_set = budget_for(role, seen and seen["brief"])
            T, t_set = time_for(role, seen and seen["brief"])
            source = "brief" if (b_set or t_set) else "default"
            if rec and not seen:   # a new worker: its transcript does not exist yet, so the dispatch record is what we know
                source = "unknown" if mixed else ("brief" if rec["b_set"] or rec["t_set"] else "default")
                if not mixed:
                    B, T = rec["B"], rec["T"]
            st = dict(role=role, B=B, T=T, base=seen["usd"] if seen else 0.0, base_recorded=seen["usd_recorded"] if seen else 0.0,
                      acc=0.0, run_start=now, run_open=True, last_seen=now, k=0, raises_done=len(seen["raises"]) if seen else 0, stops=0, ceil_req=-1,
                      brief_read=bool(seen), warned=bool(rec) or bool(seen))
            save_state(root, aid, st)
            if rec and rec.get("name"):
                base_log["name"] = rec["name"]   # the transcript and its meta file do not exist yet: the dispatch record knows the name
            handback.log_line(root, dict(base_log, event="start", B=B, T=T, source=source, resumed=bool(seen and seen["requests"]), base_usd=round(st["base"], 6)))
            return reply(kind, additionalContext=start_note(B, T, source))
        if st["run_open"]:   # the earlier run ended without a SubagentStop: count it up to the last event seen
            st["acc"] += max(0.0, st["last_seen"] - st["run_start"])
        st.update(run_start=now, run_open=True, last_seen=now)
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="start", B=st["B"], T=st["T"], resumed=True, active_s=round(st["acc"], 1)))
        return None   # measured (w03-c1): a resumed worker is not given a SubagentStart additionalContext; its notes come at the checks
    if not seen:
        return None
    if st is None:   # no SubagentStart seen (hook added mid-run): start counting from the transcript's beginning
        st = dict(role=role, B=0.0, T=0.0, base=0.0, base_recorded=0.0, acc=0.0, run_start=now, run_open=True, last_seen=now, k=0, raises_done=0, stops=0, ceil_req=-1,
                  brief_read=False, warned=False)
    if not st["warned"]:   # the brief's own figures, when no dispatch record was seen
        st["warned"] = True
        warn_floor(root, base_log, budget_for(role, seen["brief"])[0] if BRIEF_LINE.search(seen["brief"] or "") else None,
                   time_for(role, seen["brief"])[0] if TIME_LINE.search(seen["brief"] or "") else None)
    if not st["run_open"] and kind != "SubagentStop":   # events after a stop without a new start: the agent is running, count from now
        st.update(run_start=now, run_open=True)
    if not st["brief_read"]:   # the start note could say only what the dispatch record held: the brief's own lines win
        st["B"], st["T"], st["brief_read"] = budget_for(role, seen["brief"])[0], time_for(role, seen["brief"])[0], True
    changed = apply_raises(root, st, seen, now, base_log)
    used, mins, usd_frac, t_frac, frac, which = figures(st, seen, now)
    if changed:
        st["k"] = due(frac)   # the schedule restarts above the new fraction
    fields = dict(B=round(st["B"], 6), T=round(st["T"], 6), used=round(used, 6), used_recorded=round(seen["usd_recorded"] - st.get("base_recorded", 0.0), 6),
                  frac=round(usd_frac, 4), t_frac=round(t_frac, 4), which=which, basis=BASIS, requests=seen["requests"], unpriced=seen["unpriced"],
                  active_s=round(active_s(st, now), 1))
    st["last_seen"] = now
    if kind == "SubagentStop":
        if st["run_open"]:
            st["acc"] += max(0.0, now - st["run_start"])
            st["run_open"] = False
        save_state(root, aid, st)
        fields["active_s"] = round(st["acc"], 1)
        handback.log_line(root, dict(base_log, event="end", k=st["k"], stops=st["stops"], **fields))
        return None
    if kind == "PostToolBatch":
        calls = [c.get("tool_name") for c in event.get("tool_calls") or [] if isinstance(c, dict)]
        if "SubagentHandback" in calls:
            save_state(root, aid, st)
            return None
        if frac >= HARD_AT and st["ceil_req"] == seen["requests"]:   # the PostToolUse of this batch has just sent the block: one message per check
            save_state(root, aid, st)
            return None
        n = due(frac)
        if frac < OVER_AT and n <= st["k"]:
            save_state(root, aid, st)
            return None
        st["k"] = n
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="note", over=frac >= OVER_AT, **fields))
        return reply(kind, additionalContext=note_text(used, st["B"], mins, st["T"], frac))
    if kind == "PostToolUse" and event.get("tool_name") != "SubagentHandback" and frac >= HARD_AT and st["ceil_req"] != seen["requests"]:
        st["ceil_req"] = seen["requests"]   # one block per batch, whatever the number of parallel calls
        halt = st["stops"] >= HALT_AFTER
        st["stops"] += 1
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log, event="halt" if halt else "stop", n=st["stops"], **fields))
        if halt:
            return {"continue": False, "stopReason": halt_text(used, st["B"], mins, st["T"])}
        return {"decision": "block", "reason": stop_text(used, st["B"], mins, st["T"])}
    save_state(root, aid, st)
    return None


def selftest():
    import subprocess
    import tempfile
    import threading

    sys.path.insert(0, HERE)
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
        got = scan(f)
        assert got["requests"] == 2 and abs(got["usd"] - (10 + 0.10 * 1) - 8e-6) < 1e-9, got   # 1M output (10.0) + 1M cache read (0.10) + 4 input tokens
        assert BRIEF_LINE.search(got["brief"]).group(1) == "0.50" and "Budget: USD 9" not in got["brief"], "the first user message only"
        assert got["raises"] == [], "a second user message that is not from the coordinator is not a raise"
        assert scan(os.path.join(tmp, "missing")) is None
        # output: the content length stands in for the output count when it is larger; the same message streamed twice counts once
        open(f, "w").write(rec_asst("r1", 10, chars=13000) + rec_asst("r1", 10, chars=13000) + rec_asst("r2", 5000, chars=100))
        got = scan(f)
        assert abs(got["usd"] - (10000 + 5000) * 10 / 1e6 - 8e-6) < 1e-9 and abs(got["usd_recorded"] - 5010 * 10 / 1e6 - 8e-6) < 1e-9, got
        # raises: only a coordinator's plain message counts; a tool result, another origin and a line that is not exact do not; the spend before it is kept
        open(f, "w").write(rec_user("Budget: USD 1.00") + rec_asst("a", 1000) + rec_coord("Budget: USD 2.5\nTime: min 7\nGo on.") + rec_asst("b", 1000) +
                           rec_coord("Budget: USD 9", kind="peer") + rec_result("Budget: USD 8\nTime: min 8") + rec_mixed("Budget: USD 7") + rec_coord("Budget: USD 4 more\nplease") + rec_coord("Time: min 3.5") +
                           rec_queued("Budget: USD 6", kind="peer") + rec_queued("Budget: USD 1.5\nHow is it going?"))
        got = scan(f)
        assert [(r["x"], r["t"]) for r in got["raises"]] == [(2.5, 7.0), (None, 3.5), (1.5, None)], got["raises"]
        assert abs(got["raises"][0]["usd_at"] - 1000 * 10 / 1e6 - 4e-6) < 1e-9 and abs(got["raises"][1]["usd_at"] - 2000 * 10 / 1e6 - 8e-6) < 1e-9 and got["raises"][0]["ts"], got["raises"]
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
    assert all(x in start_note(3.0, 20.0, "brief") for x in ("USD 3.00 and 20 minutes (from your brief)", "50%, 75%, 87.5% and 93.75%", "at every step from 100%", "holds the money"))

    # 4. hooks end to end, in a temporary lab (the way the platform runs the script, and in-process where time is set)
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
        real_save, outs = globals()["save_state"], []

        def slow_save(root, aid, st):
            time.sleep(0.15)
            real_save(root, aid, st)

        globals()["save_state"] = slow_save
        try:
            threads = [threading.Thread(target=lambda: outs.append(handle(dict(ev, hook_event_name="PostToolUse", tool_name="Bash"), now=2.0))) for _ in range(4)]
            [t.start() for t in threads]
            [t.join() for t in threads]
        finally:
            globals()["save_state"] = real_save
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
