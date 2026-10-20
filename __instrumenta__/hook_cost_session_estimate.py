"""Estimates the hook time of a whole session: the process starts per registration (from hook_count_invocations.py) times the median cost per start (from hook_cost_time.py), old and new.

Inputs: argv[1] = counts JSON (hook_count_invocations.py output), argv[2] = results.jsonl (hook_cost_time.py output). Output: a markdown table on stdout, wall and CPU seconds,
for the main thread and for the workers, with the worker starts priced once at the short-transcript figure (a lower bound) and once at the long-transcript figure (an upper bound).
ESTIMATE: sum over registrations of (starts x median per start); it adds up time that the platform may overlap (hooks of one event run side by side) and it takes no account of
the load of the machine beyond what the medians carry.
"""
import collections, json, statistics, sys

counts = json.load(open(sys.argv[1]))
rows = [json.loads(l) for l in open(sys.argv[2])]
cell = collections.defaultdict(list)
for r in rows:
    cell[(r["case"], r["script"], r["variant"])].append(r)


def med(case, script, variant, field):
    return statistics.median(x[field] for x in cell[(case, script, variant)])


# registration key of hook_count_invocations -> (case in the timing for the main thread, for a worker, script)
MAIN = {"PostToolUse||budget.py": ("post_tool_use:main", "budget"), "PostToolBatch||budget.py": ("post_tool_batch:main", "budget"),
        "PreToolUse|Agent|Task|budget.py": ("pre_tool_use:dispatch", "budget"), "UserPromptSubmit||user_words.py": ("user_prompt_submit:main", "user_words")}
WORK = {"PostToolUse||budget.py": ("post_tool_use:worker-%s", "budget"), "PostToolBatch||budget.py": ("post_tool_batch:worker-%s", "budget"),
        "SubagentStop||budget.py": ("subagent_stop:worker-%s", "budget"), "SubagentStop||handback.py": ("subagent_stop:worker-%s", "handback"),
        "SubagentStart||budget.py": ("subagent_start:worker", "budget"), "PreToolUse|SubagentHandback|handback.py": ("pre_tool_use:handback-explorer-no-report", "handback"),
        "PostToolUse|SubagentHandback|handback.py": ("post_tool_use:handback", "handback")}


def total(starts, table, variant, field, size):
    s = 0.0
    for key, n in starts.items():
        if key in table:
            case, script = table[key]
            s += n * med(case % size if "%s" in case else case, script, variant, field) / 1000.0
    return s


print("| part | starts | old wall s | new wall s | old CPU s | new CPU s |")
print("|:--|--:|--:|--:|--:|--:|")
main_starts = {k: v for k, v in counts["starts"]["main"].items()}
print("| main thread | %d | %.1f | %.1f | %.1f | %.1f |" % (sum(main_starts.values()), total(main_starts, MAIN, "old", "wall_ms", None), total(main_starts, MAIN, "new", "wall_ms", None),
                                                         total(main_starts, MAIN, "old", "cpu_ms", None), total(main_starts, MAIN, "new", "cpu_ms", None)))
wk = counts["starts"]["workers"]
for size, label in (("short", "workers, priced at the short transcript"), ("long", "workers, priced at the long transcript")):
    print("| %s | %d | %.1f | %.1f | %.1f | %.1f |" % (label, sum(wk.values()), total(wk, WORK, "old", "wall_ms", size), total(wk, WORK, "new", "wall_ms", size),
                                                      total(wk, WORK, "old", "cpu_ms", size), total(wk, WORK, "new", "cpu_ms", size)))
