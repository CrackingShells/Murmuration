"""Counts, from session transcripts, how many times each hook registration of hooks/hooks.json starts a process, per tool call and per session.

Inputs: argv[1] = a session transcript (`<id>.jsonl`, the main thread); its subagents are read from `<id>/subagents/agent-*.jsonl`; optional `--window T0 T1`
(ISO times) restricts the main thread to records inside it; `--only SUBSTRING` keeps only subagents whose `.meta.json` name contains it; `--no-main` skips the main thread.
Output: JSON on stdout: per thread class (main, workers) the counts of tool calls, batches, hand-back calls, dispatches and prompts, and the process starts per registration.
Rules (an ESTIMATE from transcripts, not a count of hook logs: the transcript does not record hook runs): PostToolUse = tool_use blocks whose tool_result is not an error;
PostToolBatch = distinct requestIds with at least one tool_use; PreToolUse(Agent|Task) = `Agent`/`Task` tool_use in the main thread; handback.py = 2 per `SubagentHandback`
call (PreToolUse for every attempt, denied ones included, + PostToolUse for completed ones) + 1 per SubagentStop; SubagentStart / SubagentStop = 1 per worker transcript (+1 per coordinator message that resumes it);
UserPromptSubmit = main-thread user records that are plain text with no `origin`, no `isMeta` and no tool result (undercounts: queued task notifications also fire it).
"""
import collections, glob, json, os, sys

argv = sys.argv[1:]
window = None
only = ""
main_on = True
if "--window" in argv:
    i = argv.index("--window")
    window = (argv[i + 1], argv[i + 2])
    argv = argv[:i] + argv[i + 3:]
if "--only" in argv:
    i = argv.index("--only")
    only = argv[i + 1]
    argv = argv[:i] + argv[i + 2:]
if "--no-main" in argv:
    main_on = False
    argv.remove("--no-main")
main = argv[0]


def count(path, is_main):
    uses, errors, reqs_with_tool, hb, dispatch, prompts, resumes = {}, 0, set(), 0, 0, 0, 0
    all_uses = {}
    last_ts = first_ts = None
    for line in open(path, encoding="utf-8", errors="replace"):
        r = json.loads(line)
        ts = r.get("timestamp")
        if window and is_main and ts and not (window[0] <= ts <= window[1]):
            continue
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        t = r.get("type")
        msg = r.get("message") or {}
        content = msg.get("content")
        if t == "assistant" and isinstance(content, list):
            key = r.get("requestId") or msg.get("id") or r.get("uuid")
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    uses[b["id"]] = all_uses[b["id"]] = b.get("name")
                    reqs_with_tool.add(key)
        elif t == "user":
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                        errors += 1
                        uses.pop(b.get("tool_use_id"), None)
            elif is_main and not r.get("origin") and not r.get("isMeta") and not r.get("isSidechain"):
                text = content if isinstance(content, str) else "".join(b.get("text", "") for b in content or [] if isinstance(b, dict))
                if text.strip():
                    prompts += 1
            elif not is_main and (r.get("origin") or {}).get("kind") == "coordinator":
                resumes += 1
    names, all_names = collections.Counter(uses.values()), collections.Counter(all_uses.values())
    return dict(tool_calls=len(uses), error_calls=errors, batches=len(reqs_with_tool), handback_calls=names.get("SubagentHandback", 0), handback_attempts=all_names.get("SubagentHandback", 0),
                dispatches=names.get("Agent", 0) + names.get("Task", 0), prompts=prompts, resumes=resumes, by_tool=dict(names.most_common(8)), first=first_ts, last=last_ts)


out = {"main": None, "workers": []}
if main_on:
    out["main"] = count(main, True)
for f in sorted(glob.glob(main[:-6] + "/subagents/agent-*.jsonl")):
    meta = f[:-6] + ".meta.json"
    name = json.load(open(meta)).get("name", "") if os.path.exists(meta) else ""
    if only and only not in name:
        continue
    c = count(f, False)
    c.update(name=name, bytes=os.path.getsize(f))
    out["workers"].append(c)


def starts(main_c, workers):
    """Process starts per registration, as (event, matcher, script) -> n."""
    s = collections.Counter()
    for c, is_main in [(main_c, True)] + [(w, False) for w in workers]:
        if not c:
            continue
        s[("PostToolUse", "", "budget.py")] += c["tool_calls"]
        s[("PostToolBatch", "", "budget.py")] += c["batches"]
        s[("PreToolUse", "SubagentHandback", "handback.py")] += c["handback_attempts"]
        s[("PostToolUse", "SubagentHandback", "handback.py")] += c["handback_calls"]
        if is_main:
            s[("PreToolUse", "Agent|Task", "budget.py")] += c["dispatches"]
            s[("UserPromptSubmit", "", "user_words.py")] += c["prompts"]
        else:
            s[("SubagentStart", "", "budget.py")] += 1 + c["resumes"]
            s[("SubagentStop", "", "budget.py")] += 1 + c["resumes"]
            s[("SubagentStop", "", "handback.py")] += 1 + c["resumes"]
    return {"|".join(k): v for k, v in sorted(s.items())}


out["starts"] = {"main": starts(out["main"], []), "workers": starts(None, out["workers"])}
out["totals"] = {"main_tool_calls": out["main"]["tool_calls"] if out["main"] else 0, "worker_tool_calls": sum(w["tool_calls"] for w in out["workers"]), "workers": len(out["workers"]),
                 "main_starts": sum(out["starts"]["main"].values()), "worker_starts": sum(out["starts"]["workers"].values())}
json.dump(out, sys.stdout, indent=1)
print()
