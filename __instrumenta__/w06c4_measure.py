# w06-c4: derives s2 (platform-recorded hook time per worker run), s3 (outage: text received, boundary waits, effects) and the request-0 token counts from the headless runs of w06c4_run.py; inputs: run names under /private/tmp/murmuration-w06/author-w06-4/runs (args), mode (s2|s3|m3); outputs: a markdown table on stdout
import glob, json, os, re, statistics as st, sys

S = "/private/tmp/murmuration-w06/author-w06-4"
mode, names = sys.argv[1], sys.argv[2:]
HOME = os.path.expanduser("~")


def jl(path):
    for line in open(path, errors="replace"):
        try:
            yield json.loads(line)
        except ValueError:
            pass


def transcripts(name):
    run = json.load(open("%s/runs/%s/run.json" % (S, name)))
    folder = glob.glob("%s/.claude/projects/*author-w06-4-runs-%s-lab" % (HOME, name.replace("_", "-")))[0]
    main = "%s/%s.jsonl" % (folder, run["session_id"])
    return main, sorted(glob.glob(main[:-6] + "/subagents/agent-*.jsonl")), run


def dbg(name):
    return open("%s/runs/%s/dbg.log" % (S, name), errors="replace").read().splitlines()


def hook_ms(name):
    """(command ms by script, mcp_tool ms list) the platform recorded in one run."""
    cmd, mcp = {}, []
    for line in dbg(name):
        m = re.search(r"Hooks: (\S+) \[python3 \"[^\"]*/scripts/(budget|handback|outage|user_words|resume_brief)\.py\"[^\]]*\].* finished with status \d+ \((\d+)ms\)", line)
        if m:
            cmd.setdefault(m.group(2), []).append(int(m.group(3)))
    main, subs, _ = transcripts(name)
    for f in [main] + subs:
        for r in jl(f):
            a = r.get("attachment") or {}
            if a.get("type") == "hook_success" and a.get("command") == "plugin:murmuration:hooks/hook":
                mcp.append(a.get("durationMs", 0))
    return cmd, mcp


def s2():
    print("| run | workers | command hook ms (budget / handback / outage: n, sum) | mcp_tool ms (n, sum) | platform total ms | per worker ms |\n|:--|--:|:--|:--|--:|--:|")
    for n in names:
        cmd, mcp = hook_ms(n)
        _, subs, _ = transcripts(n)
        c = " / ".join("%s: %d, %d" % (k, len(cmd.get(k, [])), sum(cmd.get(k, []))) for k in ("budget", "handback", "outage"))
        tot = sum(sum(v) for k, v in cmd.items() if k in ("budget", "handback", "outage")) + sum(mcp)
        print("| %s | %d | %s | %d, %d | %d | %.0f |" % (n, len(subs), c, len(mcp), sum(mcp), tot, tot / max(1, len(subs))))


def s3():
    print("| run | server starts | failure records (main / workers) | boundaries over 1 s: PostToolUse+PostToolBatch settle ms | longest boundary ms | text with HOOKS DOWN / Hooks down in: PI transcript / worker transcripts | DENYME-style effects |\n|:--|--:|:--|:--|--:|:--|:--|")
    for n in names:
        main, subs, run = transcripts(n)
        starts = len([l for l in open(S + "/runs/%s/server.starts" % n)]) if os.path.exists(S + "/runs/%s/server.starts" % n) else -1
        def count(f):
            c = {"hook_non_blocking_error": 0, "hook_cancelled": 0}
            txt = 0
            for r in jl(f):
                a = r.get("attachment") or {}
                if a.get("type") in c:
                    c[a["type"]] += 1
                s = json.dumps(r)
                if ("HOOKS DOWN" in s or "Hooks down" in s) and r.get("type") in ("attachment", "user") and "Hooks down:" in s or ("permissionDecisionReason" in s and "HOOKS DOWN" in s) or ("tool_result" in s and "HOOKS DOWN" in s):
                    txt += 1
            return c, txt
        cm, tm = count(main)
        ws = [count(f) for f in subs]
        fw = sum(x[0]["hook_non_blocking_error"] for x in ws)
        settles = []
        for line in dbg(n):
            m = re.search(r"classic\.(PostToolUse|PostToolBatch) settled in (\d+)ms", line)
            if m:
                settles.append((m.group(1), int(m.group(2))))
        bounds = [(settles[i][1] + settles[i + 1][1]) for i in range(len(settles) - 1) if settles[i][0] == "PostToolUse" and settles[i + 1][0] == "PostToolBatch"]
        slow = [b for b in bounds if b >= 1000]
        print("| %s | %d | %d err, %d cancelled / %d err | %s | %s | %d / %s | final: %s |" % (n, starts, cm["hook_non_blocking_error"], cm["hook_cancelled"], fw, slow, max(bounds or [0]), tm, [x[1] for x in ws],
                                                                                          (run.get("result") or "")[:0]))


def m3():
    print("| run | request 0 input tokens, main thread | worker request 0 input tokens (each) |\n|:--|--:|:--|")
    for n in names:
        main, subs, _ = transcripts(n)
        def req0(f):
            for r in jl(f):
                u = (r.get("message") or {}).get("usage")
                if r.get("type") == "assistant" and u:
                    return u["input_tokens"] + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
        print("| %s | %s | %s |" % (n, req0(main), [req0(f) for f in subs]))


{"s2": s2, "s3": s3, "m3": m3}[mode]()
