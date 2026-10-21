#!/usr/bin/env python3
"""Tabulates the w07e headless PI cells: reads <scratch>/runs/*/summary.json and each cell's session transcript (~/.claude/projects/*/<session>.jsonl), and prints a markdown table (request 0 tokens, skill_listing attachment chars and count, deferred-name count, loaded tools in the request shape, where the SKILL.md body occurs, slash commands, tool calls); input: scratch dir; output: stdout.
Read-only on transcripts; prints no credentials."""
import glob, json, os, sys
S = sys.argv[1]; rows = []
for d in sorted(glob.glob(os.path.join(S, "runs", "*"))):
    try: sm = json.load(open(os.path.join(d, "summary.json")))
    except Exception: continue
    fs = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sm["session_id"]))
    sl = (0, 0); dn = 0; loaded = []; body_in = set(); mcpi = 0
    if fs:
        for l in open(fs[0]):
            r = json.loads(l)
            if r.get("type") == "attachment":
                a = r["attachment"]
                if a.get("type") == "skill_listing": sl = (a.get("skillCount"), len(a.get("content", "")))
                if a.get("type") == "deferred_tools_delta": dn += len(a.get("addedNames", []))
                if a.get("type") == "mcp_instructions_delta": mcpi += len(json.dumps(a.get("addedBlocks")))
            if r.get("type") == "api-request-shape" and not loaded: loaded = [t["name"] for t in r["shape"].get("tools", [])]
            if "A Murmuration team works in waves" in l: body_in.add(r.get("type") + ("/" + r["attachment"].get("type", "") if r.get("type") == "attachment" else ""))
    rows.append((os.path.basename(d), sm["req0_total"], sl[0], sl[1], dn, mcpi, len(loaded), sm["init_slash"], sm["has_lab_status"], ",".join(sorted(body_in)) or "-", sm["final"][:70].replace("\n", " ")))
    json.dump(dict(cell=os.path.basename(d), loaded=loaded), open(os.path.join(d, "loaded_tools.json"), "w"))
print("| cell | req0 tokens | listing skills | listing chars | deferred names | mcp instr chars | loaded tools | slash cmds | lab-status | SKILL.md body seen in | answer |")
print("|:--|--:|--:|--:|--:|--:|--:|--:|:--|:--|:--|")
for r in rows: print("| " + " | ".join(str(x) for x in r) + " |")
