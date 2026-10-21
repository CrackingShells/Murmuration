# measures, per E3 worker run, whether and how the worker searched __instrumenta__/ before writing or running a script, whether it reused an existing script, the tool-output characters the search cost, and total_cost_usd; input: run folders (run.jsonl + lab/) under a run root, and the scripts folder; output: a TSV table and a JSON file, plus the baseline characters of `ls -1` plus all first lines
"""usage: python3 -I e3_measure.py RUNROOT SCRIPTS OUT_BASENAME [ID ...]

For each run id (default: every folder under RUNROOT with a run.jsonl):
  s1  first search of the folder: kind (colgrep search / colgrep find_files / Glob / Bash ls|head|cat|find on the folder / Read of a lab script) and its index
      among the tool calls, against the index of the first script written or run (a Bash `python3 *.py`, a Write or Edit of a .py, a `cat >`/`tee` of one).
      `searched_before_script` is true when a search precedes that first write or run, or when no script was written or run at all and a search occurred.
  s2  from the lab after the run: `new_files` (files in __instrumenta__/ that were not there), `modified` (starting files whose content changed), `ran_existing`
      (Bash commands that run a starting script by name without the same call writing it), and `ran_fit`/`ran_near` for the task's fit script.
      Duplicate versus reuse is a reading of the sequences, written next to the table by hand (not done here).
  s3  characters of the tool results of the search calls (kinds above), against `baseline_chars` = `ls -1` of the folder plus the first line of every script.
  s4  total_cost_usd of the result record.
Stdlib only.
"""
import json
import os
import re
import subprocess
import sys

FIT = os.environ.get("E3_FIT", "binary_max_distinct_substrings_bruteforce.py")        # E3c renames the two targets: set E3_FIT and E3_NEAR
NEAR = os.environ.get("E3_NEAR", "collatz_longest_stopping_time.py")
INSTR = "__instrumenta__"
ERRORS = set()
SUBONLY = os.environ.get("E3_SUBAGENT_ONLY") == "1"   # set for the PI-dispatched arm: count only records with a parent_tool_use_id


def load(path):
    calls, results, cost, texts = [], {}, None, []
    global ERRORS
    ERRORS = set()
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        t = r.get("type")
        if t == "result":
            cost = r.get("total_cost_usd")
        msg = r.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        if SUBONLY and not r.get("parent_tool_use_id"):
            continue  # the PI's own calls are left out when the worker is a dispatched subagent
        for b in content:
            if t == "assistant" and b.get("type") == "tool_use":
                calls.append({"id": b["id"], "name": b["name"], "input": b.get("input", {})})
            elif t == "assistant" and b.get("type") == "text":
                texts.append(b.get("text", ""))
            elif t == "user" and b.get("type") == "tool_result":
                c = b.get("content")
                if "tool_use_error" in str(c)[:80]:
                    ERRORS.add(b["tool_use_id"])
                results[b["tool_use_id"]] = len(c) if isinstance(c, str) else sum(len(x.get("text", "")) for x in c if isinstance(x, dict))
    return calls, results, cost, texts


def search_kind(c):
    n, i = c["name"], c["input"]
    if n.endswith("colgrep__search"):
        return "colgrep_search"
    if n.endswith("colgrep__find_files"):
        return "colgrep_find_files"
    if n == "Glob" and INSTR in json.dumps(i):
        return "glob"
    if n == "Bash":
        cmd = i.get("command", "")
        if INSTR in cmd and re.search(r"\b(ls|find|head|cat|wc|sed|tail)\b", cmd) and not re.search(r"cat\s*>|tee\b|python3?\s", cmd):
            return "bash_list_or_read"
    if n == "Read" and INSTR in str(i.get("file_path", "")):
        return "read_script"
    if n == "ToolSearch":
        return None
    return None


def is_script_event(c):
    n, i = c["name"], c["input"]
    if n in ("Write", "Edit") and str(i.get("file_path", "")).endswith(".py"):
        return True
    if n == "Bash":
        cmd = i.get("command", "")
        return bool(re.search(r"python3?\s+(-I\s+)?[\w./-]*\.py|cat\s*>|tee\s|python3?\s+-c|python3?\s*<<", cmd))
    return False


def baseline_chars(scripts):
    names = sorted(os.listdir(scripts))
    ls = "\n".join(names) + "\n"
    firsts = "".join(open(os.path.join(scripts, f)).readline() for f in names)
    return len(ls), len(firsts)


def measure(root, rid, scripts):
    calls, results, cost, texts = load(os.path.join(root, rid, "run.jsonl"))
    start = set(os.listdir(scripts))
    lab_i = os.path.join(root, rid, "lab", INSTR)
    now = set(f for f in os.listdir(lab_i) if os.path.isfile(os.path.join(lab_i, f))) if os.path.isdir(lab_i) else set()   # files only: a worker may add a folder
    modified = sorted(f for f in start & now if open(os.path.join(lab_i, f)).read() != open(os.path.join(scripts, f)).read())
    first_search = first_script = None
    searches, chars = [], 0
    ran = []
    for k, c in enumerate(calls):
        kind = search_kind(c)
        if kind and c["id"] in ERRORS:
            kind = None   # a call that returned a tool error (for example Glob, absent in a headless session) is not a search
        if kind:
            searches.append((k, kind))
            chars += results.get(c["id"], 0)
            if first_search is None:
                first_search = (k, kind)
        if is_script_event(c) and first_script is None:
            first_script = k
        if c["name"] == "Bash":
            cmd = re.sub(r"<<-?\s*'?\"?(\w+)'?\"?.*?\n\1\b", "", c["input"].get("command", ""), flags=re.S)   # heredoc bodies are not commands
            for f in start:
                if re.search(r"python3?\s+(-\w+\s+)*\S*%s" % re.escape(f), cmd):
                    ran.append(f)
            for f in start:
                if re.search(r"\b(cat|head|sed|tail|less)\b[^|;&]*%s|\bhead\b[^|;&]*%s" % (re.escape(f[:-3]), re.escape(f[:-3])), cmd) or ("*.py" in cmd and INSTR in cmd and re.search(r"\b(head|cat)\b", cmd)):
                    pass
    before = None
    if first_search is not None:
        before = first_script is None or first_search[0] < first_script
    import difflib
    sim = {}
    for f in sorted(now - start):
        t = open(os.path.join(lab_i, f), errors="replace").read()
        best = max(start, key=lambda o: difflib.SequenceMatcher(None, open(os.path.join(scripts, o)).read(), t).ratio())
        sim[f] = [best, round(difflib.SequenceMatcher(None, open(os.path.join(scripts, best)).read(), t).ratio(), 2)]
    errs = [c["name"] for c in calls if c["id"] in ERRORS]
    # s7 the target found: the run names the task's target script in a command (cat, head, python3, cp, sed), matches it by a glob in head/cat/sed, or Reads it
    import fnmatch
    target = FIT if re.search(r"t1", rid) else NEAR
    how = []
    for c in calls:
        if c["id"] in ERRORS:
            continue
        if c["name"] == "Read" and target in str(c["input"].get("file_path", "")):
            how.append("Read")
        if c["name"] == "Bash":
            cmd = re.sub(r"<<-?\s*'?\"?(\w+)'?\"?.*?\n\1\b", "", c["input"].get("command", ""), flags=re.S)
            if target in cmd and not re.search(r"cat\s*>[^;&]*%s" % re.escape(target), cmd):
                how.append("named")
            for tok in re.findall(r"[\w./-]*\*[\w./*-]*", cmd):
                if re.search(r"\b(head|cat|sed|tail)\b", cmd) and fnmatch.fnmatch(target, os.path.basename(tok)) and INSTR in tok:
                    how.append("glob " + tok)

    # s5 the methods used to look at the folder; s6 starting files changed other than the task's own fit or near-fit script
    methods = set()
    for c in calls:
        if c["id"] in ERRORS:
            continue
        if c["name"].endswith("colgrep__search") or c["name"].endswith("colgrep__find_files"):
            methods.add("colgrep")
        elif c["name"] == "Bash" and INSTR in c["input"].get("command", ""):
            cmd = c["input"]["command"]
            if re.search(r"head[^|;]*(\*\.py|\$f)|for \w+ in [^;]*(\*\.py|__instrumenta__/\*)[^;]*;\s*do[^;]*head", cmd):
                methods.add("head_over_all_files")
            if re.search(r"\bls\b", cmd):
                methods.add("ls")
            if re.search(r"\bls\b[^;&]*\|\s*grep", cmd):
                methods.add("ls_grep")
            m = re.search(r"\bls\b[^;&|]*__instrumenta__[^;&|]*\|\s*head\s+-(\d+)", cmd)
            if m and int(m.group(1)) < len(start):
                methods.add("ls_head_%s_of_%d" % (m.group(1), len(start)))
            if re.search(r"head[^|;]*__instrumenta__/\w", cmd) or re.search(r"\bcat\b[^|;>]*__instrumenta__/\w", cmd):
                methods.add("read_named_files")
        elif c["name"] == "Glob" and INSTR in json.dumps(c["input"]):
            methods.add("glob")
    overwritten = [f for f in modified if f not in (FIT, NEAR) and not f.startswith("u")]
    ls_c, first_c = baseline_chars(scripts)
    return {
        "id": rid, "task": re.search(r"t\d", rid).group(0), "pilot": rid.startswith("pilot-"), "tool_calls": len(calls),
        "first_search_kind": first_search[1] if first_search else None, "first_search_index": first_search[0] if first_search else None,
        "first_script_index": first_script, "searched_before_script": bool(before), "n_searches": len(searches),
        "search_kinds": [k for _, k in searches], "search_result_chars": chars,
        "baseline_ls_chars": ls_c, "baseline_first_lines_chars": first_c, "baseline_chars": ls_c + first_c,
        "new_files": sorted(now - start), "modified": modified, "ran_existing": sorted(set(ran)),
        "closest_start_script_of_new_files": sim, "s5_methods": sorted(methods), "s7_target": target, "s7_target_found": bool(how), "s7_how": sorted(set(how)), "s6_overwritten_unrelated": overwritten, "tool_errors": errs, "ran_fit": FIT in ran, "ran_near": NEAR in ran, "total_cost_usd": cost,
        "sequence": ["%s %s" % (c["name"].replace("mcp__plugin_colgrep-mcp_colgrep__", "colgrep."), json.dumps(c["input"])[:150]) for c in calls],
    }


def main(argv):
    root, scripts, out = os.path.abspath(argv[0]), os.path.abspath(argv[1]), argv[2]
    ids = argv[3:] or sorted(d for d in os.listdir(root) if os.path.exists(os.path.join(root, d, "run.jsonl")))
    rows = [measure(root, i, scripts) for i in ids]
    json.dump(rows, open(out + ".json", "w"), indent=1)
    cols = ["id", "tool_calls", "first_search_kind", "first_search_index", "first_script_index", "searched_before_script", "n_searches",
            "search_result_chars", "baseline_chars", "new_files", "modified", "ran_existing", "total_cost_usd"]
    with open(out + ".tsv", "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(json.dumps(r[c]) if isinstance(r[c], (list, bool)) else str(r[c]) for c in cols) + "\n")
    print(open(out + ".tsv").read())
    print("total_cost_usd, non-pilot:", round(sum(r["total_cost_usd"] or 0 for r in rows if not r["pilot"]), 4), "all:", round(sum(r["total_cost_usd"] or 0 for r in rows), 4))


if __name__ == "__main__":
    main(sys.argv[1:])
