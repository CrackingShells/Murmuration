#!/usr/bin/env python3
"""Prototype of a better /lab-status spend section (claim w01-c3). Read-only. Standard library only.

    lab_spend.py --root DIR [--find scan|v6|index|ids] [--also SESSION_ID_OR_FOLDER ...]
                 [--index FILE] [--since ISO-DATE] [--config-dir DIR]

What it changes against scripts/lab_status.py (v6), one line each:
  1. finds sessions by their `cwd` under the lab (and under the other git worktrees of its repository),
     not by one folder named after one path               (--find scan; --find v6 reproduces v6)
  2. counts each API message once across all files, keyed on message id and charged to the session
     named in the record's own `sessionId` (a fork's copies of its parent's messages are not its cost)
  3. prints USD: exact from Claude Code's `cost-state` record where the session has ended,
     otherwise an estimate at list price (table below, cited); subagent output is a lower bound
  4. names agents by `.meta.json` `name` (explorer-w01-a), not by agent type
"""
import collections
import glob
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- price table
# USD per million tokens: input, output, cache read, cache write 5 min, cache write 1 h.
# [source: https://platform.claude.com/docs/en/about-claude/pricing, fetched 2026-10-19, "Model pricing" table]
# The same table is checked against Claude Code's own per-model costUSD in validate.py (claim w01-c3).
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5, 4.0),
    "claude-fable-5-1": (10.0, 50.0, 0.25, 12.5, 20.0),
    # Haiku 5.5 is priced by prompt length: this row is up to 100,000 prompt tokens, LONG_HAIKU above.
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125, 0.20),
}
LONG_HAIKU = (0.50, 2.50, 0.05, 0.625, 1.0)
WEB_SEARCH_USD = 0.01  # $10 per 1,000 searches, same page
FAST_FACTOR = 2.0  # "fast mode" Opus 5.5 is $8/$40, same page; prompt-caching multipliers stack


def price_of(model):
    """Price tuple for a model id, or None (unknown model: its USD is not guessed)."""
    return PRICES.get(re.sub(r"-\d{8}$", "", model or ""))


def message_usd(model, use):
    """USD of one deduplicated API message from its usage block; None for an unknown model."""
    p = price_of(model)
    if p is None:
        return None
    cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
    cw1 = int(cc.get("ephemeral_1h_input_tokens") or 0)
    cw5 = int(cc.get("ephemeral_5m_input_tokens") or 0)
    cw = int(use.get("cache_creation_input_tokens") or 0)
    if cw > cw1 + cw5:  # no split recorded: the rest was written with the 5 minute rate
        cw5 += cw - cw1 - cw5
    i, o, cr = int(use.get("input_tokens") or 0), int(use.get("output_tokens") or 0), int(use.get("cache_read_input_tokens") or 0)
    if model.startswith("claude-haiku-5-5") and i + cr + cw > 100000:
        p = LONG_HAIKU
    usd = (i * p[0] + o * p[1] + cr * p[2] + cw5 * p[3] + cw1 * p[4]) / 1e6
    if use.get("speed") == "fast":
        usd *= FAST_FACTOR
    st = use.get("server_tool_use") if isinstance(use.get("server_tool_use"), dict) else {}
    return usd + WEB_SEARCH_USD * int(st.get("web_search_requests") or 0)


# ---------------------------------------------------------------- finding sessions

def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def encode(path):
    """The name Claude Code gives a project's transcript folder."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def git_worktrees(root):
    """Paths of every worktree of root's repository, the main checkout first (needs git; empty without it)."""
    try:
        out = subprocess.run(["git", "-C", root, "worktree", "list", "--porcelain"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [line[9:] for line in out.splitlines() if line.startswith("worktree ")]


def git_roots(root):
    """root, its real path, and every worktree of the same repository."""
    roots = [os.path.abspath(root), os.path.realpath(root)]
    for w in git_worktrees(root):
        roots += [w, os.path.realpath(w)]
    return list(dict.fromkeys(roots))


def first_cwd(path, limit=300):
    """The `cwd` of the first record of a transcript that has one."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for _, line in zip(range(limit), fh):
                if '"cwd"' in line:
                    try:
                        cwd = json.loads(line).get("cwd")
                    except ValueError:
                        continue
                    if cwd:
                        return cwd
    except OSError:
        pass
    return None


def under(cwd, roots):
    return bool(cwd) and any(cwd == r or cwd.startswith(r.rstrip("/") + "/") for r in roots)


def main_files(folder):
    return sorted(glob.glob(os.path.join(folder, "*.jsonl")))


def find_v6(root):
    """What lab_status.py does: the one folder named after the path (or its real path)."""
    base = os.path.join(config_dir(), "projects")
    found = []
    for r in (os.path.abspath(root), os.path.realpath(root)):
        d = os.path.join(base, encode(r))
        if os.path.isdir(d) and d not in found:
            found.append(d)
    return [f for d in found for f in main_files(d)]


def find_scan(root, also=()):
    """Every session transcript whose cwd is the lab or under it, in the lab's repository worktrees.

    A folder is opened only when its name starts with the encoded name of a root (a cwd below a root
    has a folder name that does). `also` adds session ids or folder names asked for by hand."""
    base = os.path.join(config_dir(), "projects")
    roots = git_roots(root)
    prefixes = tuple(encode(r)[:100] for r in roots)
    files = []
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return []
    for e in entries:
        d = os.path.join(base, e)
        if e.startswith(prefixes) and os.path.isdir(d):
            files += [f for f in main_files(d) if under(first_cwd(f), roots)]
    files += find_ids(also)
    return list(dict.fromkeys(files))


def find_ids(items):
    """Session transcripts by session id (any project folder) or by project folder name/path."""
    base = os.path.join(config_dir(), "projects")
    files = []
    for item in items:
        if os.path.isdir(item):
            files += main_files(item)
        elif os.path.isdir(os.path.join(base, item)):
            files += main_files(os.path.join(base, item))
        else:
            files += glob.glob(os.path.join(base, "*", item + ".jsonl"))
    return list(dict.fromkeys(files))


def find_index(index_path):
    """The sessions named in a run index (one JSON line per SessionStart/SubagentStart, see index_hook.py)."""
    files = []
    try:
        with open(index_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                tp = rec.get("transcript_path")
                if tp and os.path.exists(tp):  # SubagentStart carries the parent session's transcript
                    files.append(tp)
    except OSError:
        pass
    return list(dict.fromkeys(files))


# ---------------------------------------------------------------- reading transcripts

def agent_files(main):
    sess = main[:-len(".jsonl")]
    return sorted(glob.glob(os.path.join(sess, "subagents", "**", "agent-*.jsonl"), recursive=True))


def meta_of(agent_file):
    try:
        with open(agent_file[:-len(".jsonl")] + ".meta.json", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def read_file(path, warnings):
    """One transcript file: ({message id: usage etc.}, last `cost-state` record, `agent-setting` name).

    A message id is one API call; its records (one per content block) carry the same usage except that
    `output_tokens` grows over the stream, so each usage field keeps its maximum. The record's own
    `sessionId` says which session made the call: a forked session or a copied agent file holds copies
    that still name the original session."""
    msgs, cost_state, setting, wake = {}, None, None, 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"origin"' in line and '"user"' in line[:200]:
                    if '"kind":"coordinator"' in line or '"kind":"peer"' in line:
                        wake += 1  # a message from the PI or a partner reached the agent after it started
                    continue
                if '"assistant"' not in line and '"cost-state"' not in line and '"agent-setting"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                t = rec.get("type")
                if t == "cost-state":
                    cost_state = rec
                elif t == "agent-setting" and rec.get("agentSetting") and not setting:
                    setting = rec["agentSetting"]
                elif t == "assistant":
                    m = rec.get("message")
                    if not isinstance(m, dict) or not isinstance(m.get("usage"), dict) or m.get("model") == "<synthetic>":
                        continue
                    key = m.get("id") or rec.get("requestId") or rec.get("uuid")
                    use = m["usage"]
                    d = msgs.get(key)
                    if d is None:
                        d = msgs[key] = {"model": m.get("model") or "unknown", "usage": dict(use), "ts": rec.get("timestamp"),
                                         "sid": rec.get("sessionId"), "final": False}
                    merge_usage(d["usage"], use)
                    d["final"] = d["final"] or bool(m.get("stop_reason"))
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    return msgs, cost_state, setting, wake


def merge_usage(into, use):
    for f in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
        into[f] = max(int(into.get(f) or 0), int(use.get(f) or 0))
    if isinstance(use.get("cache_creation"), dict):
        into["cache_creation"] = use["cache_creation"]


def load(mains):
    """Read the sessions and count each API message once, under the session that made it.

    Returns (sessions, stats, warnings). sessions: list of {sid, path, start, cost_state, agent_files,
    rows}; rows maps (label, kind, model) to a Counter of msgs, in, out, cr, cw, usd, unpriced,
    lower_bound_msgs. A message copied into a session from another one that is not among `mains`
    is counted nowhere (stats["inherited"]): that session did not pay for it."""
    warnings, stats = [], collections.Counter()
    by_id, sess = {}, {}
    for path in sorted(mains):
        sid = os.path.basename(path)[:-6]
        msgs, cs, setting, _ = read_file(path, warnings)
        sources = [(setting + " (main thread)" if setting else "main thread", "main", msgs, 0)]
        for af in agent_files(path):
            meta = meta_of(af)
            label = meta.get("name") or meta.get("agentType") or ("subagent " + os.path.basename(af)[6:12])
            am, _, _, wake = read_file(af, warnings)
            sources.append((label, "sub", am, wake))
        sess[sid] = {"sid": sid, "path": path, "cost_state": cs, "agent_files": len(sources) - 1, "rows": {}, "start": None}
        for label, kind, m, wake in sources:
            if wake:
                sess[sid].setdefault("wake", {})[label] = wake
            for key, d in m.items():
                stats["records"] += 1
                cur = by_id.get(key)
                if cur is None:
                    by_id[key] = dict(d, label=label, kind=kind, own_file=(d["sid"] == sid))
                    continue
                stats["copies"] += 1
                merge_usage(cur["usage"], d["usage"])
                cur["final"] = cur["final"] or d["final"]
                if d["sid"] == sid and not cur["own_file"]:  # the copy lives in the owner's own file: label it there
                    cur.update(label=label, kind=kind, own_file=True)
    for key, d in by_id.items():
        s = sess.get(d["sid"])
        if s is None:
            stats["inherited"] += 1
            continue
        row = s["rows"].setdefault((d["label"], d["kind"], d["model"]), collections.Counter())
        row["msgs"] += 1
        for f, k in (("input_tokens", "in"), ("output_tokens", "out"), ("cache_read_input_tokens", "cr"),
                     ("cache_creation_input_tokens", "cw")):
            row[k] += int(d["usage"].get(f) or 0)
        usd = message_usd(d["model"], d["usage"])
        if usd is None:
            row["unpriced"] += 1
        else:
            row["usd"] += usd
        if d["kind"] == "sub" and not d["final"]:
            row["lower_bound_msgs"] += 1
        if d["ts"] and (s["start"] is None or d["ts"] < s["start"]):
            s["start"] = d["ts"]
    return sorted(sess.values(), key=lambda s: s["start"] or "9"), stats, warnings


# ---------------------------------------------------------------- the human report

# Subagent output tokens are stored at their start-of-stream value, so a transcript estimate of a subagent's
# USD is a lower bound. Measured on the two ended sessions that have Sonnet or Fable workers
# (validate.py, validate_cells.csv): cost-state USD / transcript USD of the cell.
UPLIFT = {"claude-sonnet-5-5": (1.35, 1.40), "claude-fable-5-1": (1.18, 1.20)}


def short_model(m):
    return re.sub(r"^claude-", "", m)


def report(root, find="scan", also=(), index=None, since=None):
    if find == "v6":
        mains = find_v6(root)
    elif find == "index":
        mains = find_index(index or os.path.join(root, "__expensa__", "runs.jsonl"))
    elif find == "ids":
        mains = find_ids(also)
    else:
        mains = find_scan(root, also)
    sessions, stats, warnings = load(mains)
    if since:
        sessions = [s for s in sessions if (s["start"] or "") >= since]
    out = ["## Spend (USD; Claude Code's cost-state where a session has ended, else list price of 2026-10-19)"]
    if not sessions:
        out.append("no transcripts found for %s (looked for sessions whose cwd is the lab or one of its worktrees, under %s)"
                   % (os.path.abspath(root), os.path.join(config_dir(), "projects")))
        return "\n".join(out), {}
    roots = sorted(git_roots(root), key=len, reverse=True)
    here = os.path.realpath(root)
    wts = git_worktrees(root)
    main_co = os.path.realpath(wts[0]) if wts else None
    groups = collections.OrderedDict()
    exact = est_low = est_high = 0.0
    for s in sessions:
        cwd = first_cwd(s["path"]) or ""
        rr = next((r for r in roots if under(cwd, [r])), None)
        if rr is None:
            label = "(cwd unknown)"
        elif os.path.realpath(rr) == here:
            label = "this checkout"
        elif os.path.realpath(rr) == main_co:
            label = "main checkout"
        else:
            label = "worktree " + os.path.basename(rr.rstrip("/"))
        if rr is not None and cwd != rr:
            label += ", sessions started below it"
        e = sum(r["usd"] for r in s["rows"].values())
        lo = hi = e
        cs = s["cost_state"]
        if cs and cs.get("totalCostUSD") is not None:
            basis, lo = "exact", cs["totalCostUSD"]
            hi = lo
            exact += lo
        else:
            basis = "estimate"
            hi = sum(r["usd"] * (UPLIFT.get(k[2], (1, 1))[1] if r["lower_bound_msgs"] else 1) for k, r in s["rows"].items())
            est_low += lo
            est_high += hi
        g = groups.setdefault(label, {"n": 0, "agents": 0, "lo": 0.0, "hi": 0.0, "exact": 0, "open": 0})
        g["n"] += 1
        g["agents"] += s["agent_files"]
        g["lo"] += lo
        g["hi"] += hi
        g["exact" if basis == "exact" else "open"] += 1
    total_lo, total_hi = exact + est_low, exact + est_high
    if est_low and total_hi - total_lo > 0.005:
        out.append("TOTAL  USD %.2f at least   (%.2f exact + %.2f lower bound for sessions still open); ESTIMATE about %.2f if the open "
                   "Sonnet and Fable workers scale like two ended sessions did (n=2; Opus subagents and helper calls are not scaled, so this is not an upper bound)"
                   % (total_lo, exact, est_low, total_hi))
    else:
        out.append("TOTAL  USD %.2f   (%.2f exact + %.2f estimated)" % (total_lo, exact, est_low))
    if est_low:
        out.append("An open session has no cost-state yet. Its figure is at list price and is a LOWER BOUND: a subagent's output "
                   "tokens are stored at their start-of-stream value. The scaling is x1.40 for Sonnet and x1.20 for Fable workers, the larger "
                   "of two measured values each.")
    out.append("")
    tab = [("where", "sessions", "agent files", "USD", "basis")]
    for label, g in groups.items():
        usd = "%.2f" % g["lo"] if abs(g["hi"] - g["lo"]) < 0.005 else "%.2f to %.2f" % (g["lo"], g["hi"])
        basis = "exact" if not g["open"] else ("estimate" if not g["exact"] else "%d exact, %d estimate" % (g["exact"], g["open"]))
        tab.append((label, str(g["n"]), str(g["agents"]), usd, basis))
    out += table(tab)
    out.append("")
    byagent = collections.OrderedDict()
    wakes = collections.Counter()
    for s in sessions:
        wakes.update(s.get("wake", {}))
    for s in sessions:
        for (label, kind, model), r in s["rows"].items():
            a = byagent.setdefault((label, model), collections.Counter())
            a["msgs"] += r["msgs"]
            a["usd"] += r["usd"]
            a["out"] += r["out"]
            a["lb"] += r["lower_bound_msgs"]
    rows = sorted(byagent.items(), key=lambda kv: -kv[1]["usd"])
    tab = [("agent", "model", "msgs", "est. USD", "output tokens", "wake-ups")]
    for (label, model), a in rows[:12]:
        tab.append((label, short_model(model), str(a["msgs"]), "%.2f" % a["usd"], "{:,}".format(a["out"]) + ("+" if a["lb"] else ""),
                    str(wakes[label]) if wakes[label] else ""))
    if len(rows) > 12:
        rest = rows[12:]
        tab.append(("(%d more)" % len(rest), "", str(sum(a["msgs"] for _, a in rest)), "%.2f" % sum(a["usd"] for _, a in rest), "", ""))
    out += table(tab)
    out.append("The agent rows add up to USD %.2f of the %.2f above; the rest is what only cost-state knows (subagent output beyond "
               "its start-of-stream value, helper calls)." % (sum(a["usd"] for a in byagent.values()), total_lo) if exact else "")
    out.append("wake-ups = messages from the PI or a partner that reached the agent after it started (a resume or a note queued "
               "during a run: the transcript cannot tell them apart). `+` = a lower bound. Per-agent USD is always an estimate (cost-state has no per-agent split) and does not include "
               "helper calls (web fetch summaries), which only cost-state records.")
    if stats["copies"]:
        out.append("%d of %d message records were copies of a message already counted (forked sessions, copied agent files); "
                   "%d messages belong to sessions outside this lab and are not charged to it."
                   % (stats["copies"], stats["records"], stats["inherited"]))
    out += ["! " + w for w in warnings]
    summary = {"low": total_lo, "high": total_hi, "exact": exact, "sessions": len(sessions), "copies": stats["copies"],
               "inherited": stats["inherited"], "records": stats["records"], "groups": groups}
    return "\n".join(out), summary


def table(rows):
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = []
    for n, r in enumerate(rows):
        lines.append("  ".join(c.ljust(widths[i]) if i < 2 or not c[:1].isdigit() else c.rjust(widths[i]) for i, c in enumerate(r)).rstrip())
        if n == 0:
            lines.append("  ".join("-" * w for w in widths))
    return lines


def main(argv):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    find, also, index, since = "scan", [], None, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--root":
            root = argv[i + 1]; i += 1
        elif a == "--find":
            find = argv[i + 1]; i += 1
        elif a == "--also":
            also.append(argv[i + 1]); i += 1
        elif a == "--index":
            index = argv[i + 1]; i += 1
        elif a == "--since":
            since = argv[i + 1]; i += 1
        elif a == "--config-dir":
            os.environ["CLAUDE_CONFIG_DIR"] = argv[i + 1]; i += 1
        else:
            print("lab_spend.py: unknown argument %s" % a, file=sys.stderr)
            return 2
        i += 1
    text, _ = report(root, find, also, index, since)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
