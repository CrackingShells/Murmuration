#!/usr/bin/env python3
"""Measure one explorer run: report file shape, subagent first-turn context, skill listing, preload.
usage: measure.py <tag> ...   (tags like new_a ctl_b); run from the scratchpad folder; reads only."""
import glob, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
HEADINGS = ["Result", "Table", "Worst-fitting case", "Not covered", "Steering questions", "Pointers"]
KEYS = ["type", "wave", "author", "date", "version", "decision-required"]

def recs(path):
    return [json.loads(l) for l in open(path) if l.strip()]

def shape(report):
    t = open(report).read()
    lines = t.splitlines()
    out = {"words": len(t.split())}
    out["starts_with_frontmatter"] = lines[0] == "---"
    fm = t.split("---")[1] if t.startswith("---") else ""
    out["frontmatter_keys"] = all(re.search(r"^%s:" % k, fm, re.M) for k in KEYS)
    heads = re.findall(r"^## (.+)$", t, re.M)
    out["headings_in_order"] = heads == HEADINGS
    out["heads"] = heads
    out["comment_line_dropped"] = "<!--" not in t
    out["placeholders_left"] = bool(re.search(r"<[^>\n]*(your name|Topic|one line)[^>\n]*>|YYYY|wave-NN", t))
    return out

for tag in sys.argv[1:]:
    e = json.load(open(os.path.join(S, "e_%s.json" % tag)))
    name = tag.split("_")[1]
    lab = os.path.join(S, "lab_" + tag)
    want = "__reports__/wave-01/explorer-w01-%s/00-findings_v0.md" % name
    rep = os.path.join(lab, want)
    r = {"tag": tag, "cost_usd": round(e["total_cost_usd"], 4), "report_at_convention_path": os.path.exists(rep)}
    r["other_files_in_report_folder"] = sorted(os.listdir(os.path.dirname(rep))) if os.path.isdir(os.path.dirname(rep)) else []
    r["puzzle_file"] = os.path.exists(os.path.join(lab, "__scrupuli__/wave-01-explorer-w01-%s.md" % name))
    if r["report_at_convention_path"]:
        r.update(shape(rep))
    sd = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents" % e["session_id"]))
    r["subagent_dir_found"] = bool(sd)
    if sd:
        fs = glob.glob(sd[0] + "/agent-*.jsonl")
        R = recs(fs[0])
        asst = [x for x in R if x.get("type") == "assistant"]
        u = asst[0]["message"]["usage"]
        r["first_turn_ctx_tokens"] = u["input_tokens"] + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
        r["subagent_assistant_turns"] = len(asst)
        r["skill_listing_chars"] = [len(x["attachment"]["content"]) for x in R if x.get("type") == "attachment" and x["attachment"].get("type") == "skill_listing"]
        txt = [json.dumps(x["message"]["content"]) for x in R if x.get("type") == "user"]
        pre = [t for t in txt if "command-name>research-loop" in t or "Base directory for this skill" in t]
        r["research_loop_preloaded"] = bool(pre)
        r["preload_has_report_section"] = any("Report file" in t for t in pre)
        r["preload_template_path_substituted"] = any(re.search(r"/skills/research-loop/templates/report_findings.md", t) and "${CLAUDE_PLUGIN_ROOT}" not in t for t in pre)
        calls = [c for x in asst for c in x["message"]["content"] if c.get("type") == "tool_use"]
        r["tools_used"] = sorted({c["name"] for c in calls})
        r["skill_tool_calls"] = sum(1 for c in calls if c["name"] == "Skill")
        r["read_template"] = any("report_findings.md" in json.dumps(c["input"]) for c in calls if c["name"] in ("Read", "Bash"))
        r["write_tool_paths"] = [os.path.relpath(c["input"].get("file_path", ""), lab) for c in calls if c["name"] == "Write"]
        r["tool_names_in_handback"] = None
        r["write_refused"] = sum(1 for x in R if x.get("type") == "user" and "is_error" in json.dumps(x["message"]["content"]) and "Write" in json.dumps(x.get("toolUseResult", "")))
    print(json.dumps(r))
