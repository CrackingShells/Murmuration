#!/usr/bin/env python3
"""The code of budget.py (see its docstring for what the hook does). Kept in a module, apart from the entry script, so that Python caches its bytecode: the entry is
compiled at every call, the module only when it changes (w04-c5)."""
import os
import sys
import time
import zlib

try:
    import fcntl
except ImportError:   # no file lock on this platform: the request count still keeps parallel calls to one block in practice
    fcntl = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # under `python3 -I` the script's folder is not on the path
import handback_core as handback  # noqa: E402  (a sibling module: one place that finds the lab, the agent's name, and writes the log)

DEFAULT = {"explorer": 3.0, "author": 3.0, "reproducer": 2.0, "proof-adversary": 2.0}
OTHER_ROLE = 2.0
# Starting values chosen from a few observed worker run times, not tuned: put `Time: min <n>` in a brief to set one.
TIME_DEFAULT = {"explorer": 20.0, "author": 20.0, "reproducer": 15.0, "proof-adversary": 15.0}   # minutes
OTHER_TIME = 15.0
FLOOR_USD, FLOOR_MIN = 0.30, 3.0
SCHEDULE = (0.5, 0.75, 0.875, 0.9375)   # the notes below 1.0
OVER_AT, HARD_AT = 1.0, 1.5
HALT_AFTER = 3   # the backstop needs this many earlier ceiling blocks: an agent that hands back and then writes its report is not halted
PENDING_TTL = 600   # seconds a dispatch record waits for its SubagentStart
CARRY_OPEN = 3   # requests kept in full in the state, because their records may still arrive; an older one named again forces a read from the start
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

_PATTERNS = []


def patterns():
    """The `Budget:` and `Time:` line patterns, compiled on first use (importing `re` costs a few milliseconds that a quiet check never needs)."""
    if not _PATTERNS:
        import re
        _PATTERNS.extend([re.compile(r"^Budget: USD (\d+(?:\.\d+)?)[ \t]*$", re.M), re.compile(r"^Time: min (\d+(?:\.\d+)?)[ \t]*$", re.M)])
    return _PATTERNS


def base_model(model):
    """The model name without a trailing `-YYYYMMDD` (what `re.sub(r"-\\d{8}$", "", model)` gives, for any name without a trailing newline)."""
    m = model or ""
    return m[:-9] if len(m) > 9 and m[-9] == "-" and m[-8:].isdecimal() else m


def usd_of(model, req):
    """USD of one API request at list price; `req` holds the max of each usage field over its records."""
    p = PRICES.get(base_model(model))
    if p is None:
        p = PRICES[PRICE_FOR_UNKNOWN]
    elif model.startswith("claude-haiku-5-5") and req["in"] + req["cr"] + req["cw"] > 100000:
        p = LONG_HAIKU
    cw5 = req["cw5"] + max(0, req["cw"] - req["cw5"] - req["cw1"])  # a write with no recorded split is charged at the 5 minute rate
    usd = (req["in"] * p[0] + req["out"] * p[1] + req["cr"] * p[2] + cw5 * p[3] + req["cw1"] * p[4]) / 1e6
    return usd * (2.0 if req["fast"] else 1.0)


def block_text(block):
    """What a content block adds to the output: its text or thinking, or the JSON of a tool call's input."""
    return handback.dumps(block["input"], sort_keys=True) if "input" in block else str(block.get("text") or block.get("thinking") or "")


def block_id(text):
    """A block's identity inside one request, for counting equal blocks once: its length and two checksums (the text itself would fill the state file)."""
    raw = text.encode("utf-8", "surrogatepass")
    return [len(text), zlib.crc32(raw), zlib.adler32(raw)]


def plain_text(content):
    """The text of a user message, or None when it carries a tool result (a tool's output is never a message from the PI)."""
    if isinstance(content, str):
        return content
    blocks = [b for b in content or [] if isinstance(b, dict)]
    if any(b.get("type") == "tool_result" for b in blocks):
        return None
    return "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def epoch(stamp):
    import datetime
    try:
        return datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


class Rescan(Exception):
    """A record names a request that was finished and left out of the state: the carried figures cannot be trusted, read from the start."""


def cost_of(agg):
    """(estimated cost, recorded cost, live, unpriced) of one request from its full aggregate."""
    blocks = len({tuple(b) for b in agg["blocks"]}) and sum({tuple(b): b[0] for b in agg["blocks"]}.values())
    est = dict(agg, out=max(agg["out"], int(blocks / CHARS_PER_TOKEN) if CHARS_PER_TOKEN else 0))
    live = agg["model"] != "<synthetic>" or agg["in"] + agg["out"] + agg["cr"] + agg["cw"] > 0
    return usd_of(agg["model"], est), usd_of(agg["model"], agg), live, live and base_model(agg["model"]) not in PRICES


def scan(path, carry=None):
    """Read a subagent transcript: its first user message, its spend and the raises in it. Reads only what was added since `carry`, when given.

    Returns (result, carry): result is dict(brief, usd, usd_recorded, requests, unpriced, raises), carry the dict to keep for the next call; (None, None) when the
    file cannot be read. The brief is only given by a read from the start (carry None). Records of one request (same requestId) are merged by the maximum of
    each usage field, so a streamed request counts once. A raise is a user record whose `origin.kind` is `coordinator` and whose plain text has a `Budget: USD x`
    or a `Time: min t` line: dict(x, t, ts, usd_at) with x and t the amounts (None when absent), ts the record's time (epoch seconds) and usd_at the spend of
    the requests before it. The result of reading in pieces equals the result of reading at once (budget_selftest, check 2b)."""
    try:
        return _scan(path, carry)
    except Rescan:
        return _scan(path, None)
    except (OSError, ValueError):
        return None, None


def _scan(path, carry):
    brief_re, time_re = patterns() if carry is None else (None, None)
    brief = None
    off, tail = 0, ""
    if carry is not None:
        off, tail = carry["off"], carry["tail"]
        if os.path.getsize(path) < off:
            raise Rescan
    with open(path, "rb") as fh:
        if tail:
            fh.seek(off - len(tail))
            if fh.read(len(tail)).decode("latin-1") != tail:   # the file is not the one the carry was made from
                raise Rescan
        data = fh.read()
    end = data.rfind(b"\n") + 1   # an unfinished last line waits for the next check
    c = carry or dict(off=0, tail="", bf=False, keys=[], c=[], r=[], f="", ob={}, raises=[])
    done = set(c["keys"])
    bf, ob, raises = c["bf"], c["ob"], c["raises"]
    for raw in data[:end].split(b"\n"):
        if not bf and b'"user"' in raw:
            rec = handback.loads(raw.decode("utf-8", "replace"))
            if rec.get("type") == "user":
                bf = True
                if carry is None:
                    brief = plain_text((rec.get("message") or {}).get("content")) or ""
        elif b'"origin"' in raw:
            rec = handback.loads(raw.decode("utf-8", "replace"))
            att = rec.get("attachment") or {}
            if rec.get("type") == "user":   # a worker resumed by a message: the message is a user record
                text, origin = plain_text((rec.get("message") or {}).get("content")), rec.get("origin")
            elif att.get("type") == "queued_command":   # a message to a worker that is still running: an attachment
                text, origin = att.get("prompt") if isinstance(att.get("prompt"), str) else None, att.get("origin")
            else:
                text, origin = None, None
            if text and (origin or {}).get("kind") == "coordinator":
                if brief_re is None:
                    brief_re, time_re = patterns()
                usd, mins = brief_re.search(text), time_re.search(text)
                if (usd and float(usd.group(1)) > 0) or (mins and float(mins.group(1)) > 0):
                    raises.append(dict(x=float(usd.group(1)) if usd and float(usd.group(1)) > 0 else None,
                                       t=float(mins.group(1)) if mins and float(mins.group(1)) > 0 else None,
                                       ts=epoch(rec.get("timestamp")), n=len(c["keys"]) + len(ob)))
        if b'"usage"' not in raw:
            continue
        rec = handback.loads(raw.decode("utf-8", "replace"))
        msg, use = rec.get("message") or {}, (rec.get("message") or {}).get("usage")
        if rec.get("type") != "assistant" or not isinstance(use, dict):
            continue
        cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
        got = dict(in_=use.get("input_tokens"), out=use.get("output_tokens"), cr=use.get("cache_read_input_tokens"),
                   cw=use.get("cache_creation_input_tokens"), cw5=cc.get("ephemeral_5m_input_tokens"),
                   cw1=cc.get("ephemeral_1h_input_tokens"))
        got = {k.rstrip("_"): int(v or 0) for k, v in got.items()}
        key = rec.get("requestId") or msg.get("id") or rec.get("uuid")
        if key in done:
            raise Rescan
        old = ob.get(key)
        if old is None:
            old = ob[key] = dict(model=msg.get("model"), fast=False, blocks=[], **{k: 0 for k in got})
        for k, v in got.items():
            old[k] = max(old[k], v)
        seen_ids = {tuple(b) for b in old["blocks"]}
        for b in msg.get("content") or []:
            if isinstance(b, dict):
                ident = block_id(block_text(b))
                if tuple(ident) not in seen_ids:
                    seen_ids.add(tuple(ident))
                    old["blocks"].append(ident)
        old["fast"] = old["fast"] or use.get("speed") == "fast"
        old["model"] = old["model"] if old["model"] and old["model"] != "<synthetic>" else msg.get("model")
    if not data[:end] and carry is not None:
        pass
    while len(ob) > CARRY_OPEN:   # the oldest open request is finished (no record of this read names it again): keep its cost only
        k0 = next(iter(ob))
        est, rec_cost, live, unpriced = cost_of(ob.pop(k0))
        c["keys"].append(k0)
        c["c"].append(est)
        c["r"].append(rec_cost)
        c["f"] += "U" if unpriced else ("L" if live else "-")
    c["off"] = off + end
    keep = (data[:end][-48:] if end else b"")
    c["tail"] = keep.decode("latin-1") if keep else tail
    c["bf"] = bf
    opened = [cost_of(a) for a in ob.values()]
    costs = c["c"] + [o[0] for o in opened]
    flags = c["f"] + "".join("U" if o[3] else ("L" if o[2] else "-") for o in opened)
    for r in raises:
        r["usd_at"] = sum(costs[:r["n"]])
    result = dict(brief=brief, usd=sum(costs), usd_recorded=sum(c["r"] + [o[1] for o in opened]),
                  requests=flags.count("L") + flags.count("U"), unpriced=flags.count("U"),
                  raises=[dict(x=r["x"], t=r["t"], ts=r["ts"], usd_at=r["usd_at"]) for r in raises])
    return result, c


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
    found = patterns()[0].search(brief or "")
    if found and float(found.group(1)) > 0:
        return float(found.group(1)), True
    return DEFAULT.get(role, OTHER_ROLE), False


def time_for(role, brief):
    """T in minutes and whether the brief set it."""
    found = patterns()[1].search(brief or "")
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
        "The principal investigator holds the money and decides whether to resume you with more. "
        "Before you write a helper script: ToolSearch `select:mcp__plugin_colgrep-mcp_colgrep__search,mcp__plugin_colgrep-mcp_colgrep__find_files`, "
        "then `search` with `paths: [\"__instrumenta__\"]` and `limit: 5`." % where)


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
            return handback.loads(fh.read())
    except (OSError, ValueError):
        return None


def save_state(root, aid, st):
    tmp = state_path(root, aid) + ".%d.tmp" % os.getpid()
    with open(tmp, "w") as fh:
        fh.write(handback.dumps(st))
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


def apply_raises(root, st, seen, now, base_log):   # base_log: a function giving the header of a log line
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
        handback.log_line(root, dict(base_log(), event="raise", add_usd=r["x"], add_min=r["t"], B_before=before[0], T_before=before[1], B=round(st["B"], 6), T=round(st["T"], 6),
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
    import re
    role, prompt = kind.split(":", 1)[1], tin.get("prompt") or ""
    B, b_set = budget_for(role, prompt)
    T, t_set = time_for(role, prompt)
    name = str(tin.get("name") or (re.search(r"Your name is ([a-z0-9-]+)", prompt) or [None, None])[1] or kind)
    os.makedirs(pending_dir(root), exist_ok=True)
    key = "%014.3f-%s" % (now, re.sub(r"[^A-Za-z0-9_-]", "", str(event.get("tool_use_id") or os.getpid())))
    with open(os.path.join(pending_dir(root), key + ".json"), "w") as fh:
        fh.write(handback.dumps(dict(type=kind, B=B, T=T, b_set=b_set, t_set=t_set, t=now, name=name)))
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
    try:
        names = sorted(n for n in os.listdir(pending_dir(root)) if n.endswith(".json") and not n.startswith("."))
    except OSError:
        names = []
    for path in (os.path.join(pending_dir(root), n) for n in names):
        try:
            rec = handback.loads(open(path, "rb").read())
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
                        fh.write(handback.dumps(dict(r, ambiguous=True)))
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
    st = load_state(root, aid)
    named = []

    def base_log_():   # the agent's name costs a file read: found only when a line is to be written
        if not named:
            named.append(dict(agent_id=aid, name=handback.agent_name(event), type=event.get("agent_type"), mode=event.get("permission_mode")))
        return named[0]
    seen, carry = None, None
    if (kind != "SubagentStart" or st is None) and path and os.path.exists(path):   # a resume reads no transcript: it only reopens the run
        # from the byte where the last check stopped, unless the brief's own figures are still to be read
        seen, carry = scan(path, st.get("sc") if st and st.get("brief_read") and st.get("warned") else None)
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
                      brief_read=bool(seen), warned=bool(rec) or bool(seen), sc=carry)
            save_state(root, aid, st)
            if rec and rec.get("name"):
                base_log_()["name"] = rec["name"]   # the transcript and its meta file do not exist yet: the dispatch record knows the name
            handback.log_line(root, dict(base_log_(), event="start", B=B, T=T, source=source, resumed=bool(seen and seen["requests"]), base_usd=round(st["base"], 6)))
            return reply(kind, additionalContext=start_note(B, T, source))
        if st["run_open"]:   # the earlier run ended without a SubagentStop: count it up to the last event seen
            st["acc"] += max(0.0, st["last_seen"] - st["run_start"])
        st.update(run_start=now, run_open=True, last_seen=now)
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log_(), event="start", B=st["B"], T=st["T"], resumed=True, active_s=round(st["acc"], 1)))
        return None   # measured (w03-c1): a resumed worker is not given a SubagentStart additionalContext; its notes come at the checks
    if not seen:
        return None
    if st is None:   # no SubagentStart seen (hook added mid-run): start counting from the transcript's beginning
        st = dict(role=role, B=0.0, T=0.0, base=0.0, base_recorded=0.0, acc=0.0, run_start=now, run_open=True, last_seen=now, k=0, raises_done=0, stops=0, ceil_req=-1,
                  brief_read=False, warned=False)
    st["sc"] = carry
    if not st["warned"]:   # the brief's own figures, when no dispatch record was seen
        st["warned"] = True
        brief_re, time_re = patterns()
        warn_floor(root, base_log_(), budget_for(role, seen["brief"])[0] if brief_re.search(seen["brief"] or "") else None,
                   time_for(role, seen["brief"])[0] if time_re.search(seen["brief"] or "") else None)
    if not st["run_open"] and kind != "SubagentStop":   # events after a stop without a new start: the agent is running, count from now
        st.update(run_start=now, run_open=True)
    if not st["brief_read"]:   # the start note could say only what the dispatch record held: the brief's own lines win
        st["B"], st["T"], st["brief_read"] = budget_for(role, seen["brief"])[0], time_for(role, seen["brief"])[0], True
    changed = apply_raises(root, st, seen, now, base_log_)
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
        handback.log_line(root, dict(base_log_(), event="end", k=st["k"], stops=st["stops"], **fields))
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
        handback.log_line(root, dict(base_log_(), event="note", over=frac >= OVER_AT, **fields))
        return reply(kind, additionalContext=note_text(used, st["B"], mins, st["T"], frac))
    if kind == "PostToolUse" and event.get("tool_name") != "SubagentHandback" and frac >= HARD_AT and st["ceil_req"] != seen["requests"]:
        st["ceil_req"] = seen["requests"]   # one block per batch, whatever the number of parallel calls
        halt = st["stops"] >= HALT_AFTER
        st["stops"] += 1
        save_state(root, aid, st)
        handback.log_line(root, dict(base_log_(), event="halt" if halt else "stop", n=st["stops"], **fields))
        if halt:
            return {"continue": False, "stopReason": halt_text(used, st["B"], mins, st["T"])}
        return {"decision": "block", "reason": stop_text(used, st["B"], mins, st["T"])}
    save_state(root, aid, st)
    return None




def main():
    try:
        event = handback.loads(sys.stdin.buffer.read() or b"{}")   # bytes: the locale decides nothing
        answer = handle(event) if isinstance(event, dict) else None
        if answer:
            print(handback.dumps(answer))
    except Exception:
        pass
    return 0


def run(argv):
    """The entry script's body: the selftest, or one hook event from stdin. Returns the exit code."""
    if "--selftest" in argv:
        import budget_selftest
        budget_selftest.selftest()   # any error here is a failure and must show
        return 0
    try:
        return main()
    except Exception:
        return 0
