#!/usr/bin/env python3
"""Counts, for the worker transcripts of one session, heredoc Bash calls, inline Python, file searches, scripts saved under __instrumenta__/ and their reuse; input: session folders and filters on the command line, output: a text table and one JSON file.

Extends the baseline of the principal investigator (scratchpad/heredoc_measure.py, same counting rules for
tools, Bash, heredoc and inline Python) with: colgrep calls and their `limit`, Glob/Grep calls, shell search
commands, Python heredocs that walk files, scripts written to __instrumenta__/ and used by a second agent.

    python3 -I bash_practice_measure.py --label NAME --out out.json [--exclude-name REGEX] [--main] SESSION_DIR...
    python3 -I bash_practice_measure.py --selftest

SESSION_DIR holds `subagents/*.jsonl`; with --main the main transcript `SESSION_DIR.jsonl` is counted as an
extra agent called `research-pi` (reported on its own line, kept out of the "workers" totals).
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

INSTR = "__instrumenta__"
HEREDOC_BODY = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?:\n|$)", re.S)
INLINE_PY_BASE = re.compile(r"python3?\s+(-I\s+)?(-\s*<<|-c)")             # the baseline's rule, kept for comparison
INLINE_PY = re.compile(r"python[0-9.]*\s+(?:-[A-Za-z]+\s+)*(?:-c\b|-\s*<<|<<)")  # also `python3 <<EOF`
WALK = re.compile(r"\bglob\b|\.rglob\(|os\.walk|os\.listdir|iterdir\(|scandir\(|fnmatch")
SEARCH_PI = re.compile(r"\b(grep|rg|find)\b")   # the PI's wider rule: the word anywhere in the command, heredoc bodies too
SHELL_SEARCH = re.compile(r"(?:^|[\s;&|(`])(grep|egrep|fgrep|rg|ag|ack|fd|find|locate|mdfind)(?=\s|$)")
HD_APPEND = re.compile(r"(?:cat|tee\s+-a|printf\s+\S+)\s*>>[^\n<]*<<")
HD_WRITE = re.compile(r"(?:cat|tee)\s*>(?!>)[^\n<]*<<|<<[^\n]*\|\s*tee\s")
PIPE_FILTER = re.compile(r"\|\s*(grep|egrep|fgrep|rg)\b")
INSTR_FILE = re.compile(re.escape(INSTR) + r"/([A-Za-z0-9_][A-Za-z0-9_.\-]*)")
WRITES_INSTR = re.compile(r"(?:>>?|\btee(?:\s+-a)?|\bcp\s+\S+|\bmv\s+\S+)\s*['\"]?\S*" + re.escape(INSTR) + r"/[A-Za-z0-9_.\-]+")
COLGREP = "mcp__plugin_colgrep-mcp_colgrep__"


def strip_heredocs(cmd):
    """The command line without the bodies of its heredocs."""
    return HEREDOC_BODY.sub("<<HEREDOC\n", cmd)


def classify_bash(cmd):
    """Flags of one Bash command, by the rules above."""
    head = strip_heredocs(cmd)
    inline = bool(INLINE_PY.search(cmd))
    flags = {
        "heredoc": "<<" in cmd,                      # the baseline's rule
        "heredoc_append": "<<" in cmd and bool(HD_APPEND.search(cmd)),
        "heredoc_write": "<<" in cmd and bool(HD_WRITE.search(cmd)) and not HD_APPEND.search(cmd),
        "inline_py_base": bool(INLINE_PY_BASE.search(cmd)),
        "inline_py": inline,
        "py_walk": inline and bool(WALK.search(cmd)),
        "shell_search_pi": bool(SEARCH_PI.search(cmd)),
        "py_walk_pi": "python" in cmd and "glob" in cmd,
        "shell_search": bool(SHELL_SEARCH.search(head)),
        "shell_search_pipe_only": bool(SHELL_SEARCH.search(head)) and not SHELL_SEARCH.search(PIPE_FILTER.sub("", head)),
    }
    return flags


def instrument_events(tool, inp):
    """(kind, file) pairs for one tool call: kind is write, edit or use (run or read)."""
    out = []
    if tool == "Bash":
        cmd = strip_heredocs(inp.get("command", ""))   # a path named inside a heredoc body is text, not a use
        names = INSTR_FILE.findall(cmd)
        written = {m.group(0).rsplit("/", 1)[1] for m in WRITES_INSTR.finditer(cmd)}
        for n in names:
            out.append(("write" if n in written else "use", n))
    elif tool in ("Write", "Edit"):
        m = INSTR_FILE.search(str(inp.get("file_path", "")))
        if m:
            out.append(("write" if tool == "Write" else "edit", m.group(1)))
    elif tool == "Read":
        m = INSTR_FILE.search(str(inp.get("file_path", "")))
        if m:
            out.append(("use", m.group(1)))
    elif tool == COLGREP + "expand":
        for h in inp.get("hit_ids") or []:
            m = INSTR_FILE.search(str(h))
            if m:
                out.append(("use", m.group(1)))
    return out


def read_agent(path, main=False):
    """One transcript -> counters, the colgrep calls, the instrument events."""
    name = "research-pi" if main else None
    c = collections.Counter()
    colgrep, events = [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        m = r.get("message") or {}
        cont = m.get("content")
        if r.get("type") == "user" and name is None:
            txt = cont if isinstance(cont, str) else " ".join(json.dumps(b) for b in (cont or []))
            mm = re.search(r"Your name is ([a-z0-9-]+)", txt)
            if mm:
                name = mm.group(1)
        if r.get("type") != "assistant" or not isinstance(cont, list):
            continue
        ts = r.get("timestamp", "")
        for b in cont:
            t = b.get("type")
            if t == "text":
                c["text_chars"] += len(b.get("text", ""))
            if t != "tool_use":
                continue
            tool, inp = b.get("name", ""), b.get("input", {}) or {}
            c["tool_calls"] += 1
            c["tool_chars"] += len(json.dumps(inp))
            for kind, fname in instrument_events(tool, inp):
                events.append((ts, kind, fname))
            if tool == "Bash":
                cmd = inp.get("command", "")
                c["bash"] += 1
                c["bash_chars"] += len(cmd)
                f = classify_bash(cmd)
                for k, v in f.items():
                    c[k] += int(v)
                if f["heredoc"]:
                    c["heredoc_chars"] += len(cmd)
                if f["inline_py"]:
                    c["inline_py_chars"] += len(cmd)
            elif tool in ("Write", "Edit"):
                c[tool] += 1
                if tool == "Write" and str(inp.get("file_path", "")).endswith(".py"):
                    c["write_py"] += 1
            elif tool == "Glob":
                c["glob"] += 1
            elif tool == "Grep":
                c["grep_tool"] += 1
            elif tool.startswith(COLGREP):
                kind = tool[len(COLGREP):]
                c["colgrep_" + kind] += 1
                if kind in ("search", "find_files"):
                    paths = inp.get("paths") or []
                    scoped = any(INSTR in str(p) for p in paths)
                    colgrep.append({"tool": kind, "limit": inp.get("limit", "absent"), "paths": paths, "scoped_instr": scoped})
                    c["colgrep_scoped_instr"] += int(scoped)
            elif tool == "ToolSearch":
                c["toolsearch"] += 1
                if "colgrep" in json.dumps(inp):
                    c["toolsearch_colgrep"] += 1
    return {"name": name or os.path.basename(path)[:14], "c": c, "colgrep": colgrep, "events": events, "path": path}


def reuse(agents):
    """Per instrument file: who wrote it first, who else wrote or used it. Returns (files, reused_by_second_agent)."""
    seen = collections.defaultdict(list)
    for a in agents:
        for ts, kind, fname in a["events"]:
            seen[fname].append((ts, a["name"], kind))
    files = {}
    for fname, evs in seen.items():
        evs.sort()
        writers = [e for e in evs if e[2] in ("write", "edit")]
        first = writers[0][1] if writers else None
        others_use = sorted({e[1] for e in evs if e[2] == "use" and e[1] != first})
        others_ext = sorted({e[1] for e in evs if e[2] in ("write", "edit") and e[1] != first})
        files[fname] = {"first_writer": first, "used_by_other": others_use, "extended_by_other": others_ext,
                        "events": len(evs)}
    return files, [f for f, v in files.items() if v["used_by_other"] or v["extended_by_other"]]


def summarize(agents, label):
    tot = collections.Counter()
    for a in agents:
        tot.update(a["c"])
    out_chars = tot["tool_chars"] + tot["text_chars"]
    files, reused = reuse(agents)
    cg = [x for a in agents for x in a["colgrep"]]
    return {
        "label": label, "agents": len(agents), "totals": dict(tot),
        "heredoc_share_of_bash": tot["heredoc"] / max(1, tot["bash"]),
        "inline_py_base_share_of_heredoc": tot["inline_py_base"] / max(1, tot["heredoc"]),
        "inline_py_share_of_bash": tot["inline_py"] / max(1, tot["bash"]),
        "heredoc_share_of_output_chars": tot["heredoc_chars"] / max(1, out_chars),
        "bash_share_of_output_chars": tot["bash_chars"] / max(1, out_chars),
        "instrument_files": sorted(files), "instrument_files_n": len(files),
        "instrument_files_reused_by_second_agent": sorted(reused),
        "instrument_detail": files,
        "colgrep_searches": [x for x in cg],
        "colgrep_search_limits": dict(collections.Counter(str(x["limit"]) for x in cg)),
    }


def load(session_dirs, exclude_name, main):
    workers, pis = [], []
    ex = re.compile(exclude_name) if exclude_name else None
    for d in session_dirs:
        d = d.rstrip("/")
        for f in sorted(glob.glob(d + "/subagents/*.jsonl")):
            a = read_agent(f)
            if a["c"]["tool_calls"] == 0 or (ex and ex.search(a["name"])):
                continue
            workers.append(a)
        if main and os.path.exists(d + ".jsonl"):
            pis.append(read_agent(d + ".jsonl", main=True))
    return workers, pis


def table(agents):
    rows = ["%-22s %5s %5s %5s %5s %5s %6s %6s %5s %5s %5s" % (
        "agent", "tools", "bash", "hdoc", "inlpy", "walk", "shsrch", "colgr", "glob", "wrpy", "instr")]
    for a in sorted(agents, key=lambda a: -a["c"]["bash_chars"]):
        c = a["c"]
        rows.append("%-22s %5d %5d %5d %5d %5d %6d %6d %5d %5d %5d" % (
            a["name"], c["tool_calls"], c["bash"], c["heredoc"], c["inline_py"], c["py_walk"], c["shell_search"],
            c["colgrep_search"] + c["colgrep_find_files"], c["glob"], c["write_py"], len(a["events"])))
    return "\n".join(rows)


def report(s):
    t = s["totals"]
    L = ["== %s: %d agents ==" % (s["label"], s["agents"]),
         "tool calls %d, Bash %d (%.0f%% of calls)" % (t.get("tool_calls", 0), t.get("bash", 0), 100 * t.get("bash", 0) / max(1, t.get("tool_calls", 0))),
         "heredoc Bash %d = %.0f%% of Bash; inline Python (baseline rule) %d = %.0f%% of heredocs; inline Python (wider rule) %d" % (
             t.get("heredoc", 0), 100 * s["heredoc_share_of_bash"], t.get("inline_py_base", 0), 100 * s["inline_py_base_share_of_heredoc"], t.get("inline_py", 0)),
         "heredocs that write a file %d, append %d, run inline Python (baseline rule) %d" % (t.get("heredoc_write", 0), t.get("heredoc_append", 0), t.get("inline_py_base", 0)),
         "heredoc share of output chars %.0f%%; Bash share %.0f%%" % (100 * s["heredoc_share_of_output_chars"], 100 * s["bash_share_of_output_chars"]),
         "Write .py %d, Write %d, Edit %d" % (t.get("write_py", 0), t.get("Write", 0), t.get("Edit", 0)),
         "file searches: colgrep search %d, find_files %d (scoped to %s: %d), expand %d; Glob %d; Grep tool %d; shell search commands %d (pipe filters only: %d; the PI's wider rule: %d); Python commands that walk files %d (the PI's rule, `glob` in a python command: %d); ToolSearch %d (naming colgrep: %d)" % (
             t.get("colgrep_search", 0), t.get("colgrep_find_files", 0), INSTR, t.get("colgrep_scoped_instr", 0), t.get("colgrep_expand", 0),
             t.get("glob", 0), t.get("grep_tool", 0), t.get("shell_search", 0), t.get("shell_search_pipe_only", 0), t.get("shell_search_pi", 0), t.get("py_walk", 0), t.get("py_walk_pi", 0),
             t.get("toolsearch", 0), t.get("toolsearch_colgrep", 0)),
         "colgrep limits: %s" % s["colgrep_search_limits"],
         "scripts under %s: %d; reused or extended by a second agent: %d %s" % (
             INSTR, s["instrument_files_n"], len(s["instrument_files_reused_by_second_agent"]), s["instrument_files_reused_by_second_agent"])]
    return "\n".join(L)


def selftest():
    import tempfile
    assert classify_bash("python3 -I - <<'E'\nimport glob\nglob.glob('*')\nE")["py_walk"]
    f = classify_bash("grep -rn foo . | head\nls")
    assert f["shell_search"] and not f["shell_search_pipe_only"]
    assert classify_bash("cat x | grep foo")["shell_search_pipe_only"]
    assert not classify_bash("python3 - <<'E'\nprint('grep -r foo')\nE")["shell_search"], "heredoc bodies are not shell commands"
    assert not classify_bash("python3 -c 'x.find(1)'")["shell_search"]
    assert classify_bash("cat > f.py <<'E'\nx\nE")["heredoc_write"] and classify_bash("cat >> f.md <<'E'\nx\nE")["heredoc_append"]
    assert not classify_bash("cat >> f.md <<'E'\nx\nE")["heredoc_write"] and not classify_bash("python3 - <<'E'\nx\nE")["heredoc_write"]
    assert classify_bash("echo a <<< b")["heredoc"] and not classify_bash("ls")["heredoc"]
    assert classify_bash("python3 <<'E'\nprint(1)\nE")["inline_py"] and not classify_bash("python3 <<'E'\nprint(1)\nE")["inline_py_base"]
    assert instrument_events("Bash", {"command": "cat > __instrumenta__/a.py <<'E'\nx\nE"}) == [("write", "a.py")]
    assert instrument_events("Bash", {"command": "python3 __instrumenta__/a.py out"}) == [("use", "a.py")]
    assert instrument_events("Bash", {"command": "cat > s.md <<'E'\nsee __instrumenta__/a.py@abc\nE"}) == [], "naming a script in text is not a use"
    assert instrument_events("Bash", {"command": "ls __instrumenta__/"}) == []
    assert instrument_events("Write", {"file_path": "/x/__instrumenta__/b.py"}) == [("write", "b.py")]
    assert instrument_events("Read", {"file_path": "/x/__instrumenta__/b.py"}) == [("use", "b.py")]
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(tmp + "/s/subagents")

        def rec(role, blocks, ts):
            return json.dumps({"type": role, "timestamp": ts, "message": {"content": blocks}}) + "\n"
        with open(tmp + "/s/subagents/a.jsonl", "w") as fh:
            fh.write(rec("user", "Your name is author-x-1.", "1"))
            fh.write(rec("assistant", [{"type": "tool_use", "name": "Write", "input": {"file_path": "/p/__instrumenta__/count.py", "content": "x"}},
                                       {"type": "tool_use", "name": COLGREP + "search", "input": {"query": "q", "paths": ["__instrumenta__"], "limit": 5}}], "2"))
        with open(tmp + "/s/subagents/b.jsonl", "w") as fh:
            fh.write(rec("user", "Your name is reproducer-x-1.", "3"))
            fh.write(rec("assistant", [{"type": "tool_use", "name": "Bash", "input": {"command": "python3 __instrumenta__/count.py 5"}},
                                       {"type": "tool_use", "name": "Bash", "input": {"command": "python3 - <<'E'\nimport glob\nglob.glob('*')\nE"}}], "4"))
        w, _ = load([tmp + "/s"], None, False)
        s = summarize(w, "t")
        assert s["agents"] == 2 and s["instrument_files"] == ["count.py"] and s["instrument_files_reused_by_second_agent"] == ["count.py"], s
        assert s["colgrep_search_limits"] == {"5": 1} and s["totals"]["colgrep_scoped_instr"] == 1 and s["totals"]["py_walk"] == 1
        assert s["heredoc_share_of_bash"] == 0.5
        w, _ = load([tmp + "/s"], "^author", False)
        assert [a["name"] for a in w] == ["reproducer-x-1"]
    print("PASS bash_practice_measure")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--label", default="run")
    ap.add_argument("--out")
    ap.add_argument("--exclude-name", help="regex on the agent name; matching transcripts are left out")
    ap.add_argument("--main", action="store_true", help="also count the main transcript, on its own line")
    ap.add_argument("sessions", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    workers, pis = load(a.sessions, a.exclude_name, a.main)
    print(table(workers + pis))
    s = summarize(workers, a.label + " (workers)")
    print(report(s))
    result = {"workers": s}
    if pis:
        sp = summarize(pis, a.label + " (main transcript)")
        sall = summarize(workers + pis, a.label + " (workers and main)")
        print(report(sp))
        print(report(sall))
        result.update(main=sp, all=sall)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(result, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
