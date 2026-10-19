#!/usr/bin/env python3
"""Replay this run's real subagent transcripts through the prototype hook, and compare its output with the
files the PI saved from the hand-backs with save_handback.py.
Usage: replay_run.py <subagents dir> <repo root> <out dir>   (writes a temporary lab in <out dir>; reads, never writes the run)
For each agent transcript: every SubagentHandback tool_use (deduplicated by tool_use id) becomes a synthetic
PostToolUse event for plugin/scripts/handback.py. Then: verbatim text vs the saved report.md of that agent."""
import glob, json, os, re, subprocess, sys

sub, repo, out = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(out, "__statera__"), exist_ok=True)
rows = []
for f in sorted(glob.glob(os.path.join(sub, "agent-*.jsonl"))):
    aid = os.path.basename(f)[6:-6]; seen = {}; 
    for line in open(f, encoding="utf-8"):
        r = json.loads(line); m = r.get("message")
        if isinstance(m, dict) and isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback": seen[b["id"]] = b["input"]["message"]
    meta = json.load(open(f[:-6] + ".meta.json"))
    for tid, text in seen.items():
        ev = dict(hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id=aid, agent_type=meta.get("agentType"),
                  tool_input={"message": text}, cwd=out, transcript_path=os.path.join(sub, "..", "x.jsonl")[:-6] + ".jsonl")
        # transcript_path of the real event is the main transcript; the hook derives <it minus .jsonl>/subagents/agent-<id>.meta.json
        ev["transcript_path"] = os.path.normpath(os.path.join(sub, "..")) + ".jsonl"
        subprocess.run([sys.executable, "-I", os.path.join(here, "plugin/scripts/handback.py")], input=json.dumps(ev), text=True, check=True)
        rows.append((meta.get("name"), aid, text))

def norm_saved(path):
    s = open(path, encoding="utf-8").read()
    s = s[s.index("The report follows:") + len("The report follows:"):]
    lines = [l[2:] if l.startswith("  ") else l for l in s.split("\n")[1:]]
    lines = [l for l in lines if not l.startswith("[harness: subagent output matched")]
    t = "\n".join(lines)
    cut = t.find("\n</agent-message>")
    return t[:cut] if cut >= 0 else t

print("agent\tagent_id\tverbatim_chars\tfile_in_lab\tsaved_report\tsaved_equals_verbatim\tfirst_difference")
for name, aid, text in rows:
    lab = glob.glob(os.path.join(out, "__statera__", "handbacks", "*" + name + ".md"))
    inlab = bool(lab) and text in open(lab[0], encoding="utf-8").read()
    saved = glob.glob(os.path.join(repo, "__reports__/reflective_run/w01", name, "report.md"))
    eq, diff = "", ""
    if saved and "Subagent hand-back" in open(saved[0], encoding="utf-8").read():
        full = norm_saved(saved[0]); a, b = full.strip(), text.strip()
        a2, b2 = re.sub(r"\s+", " ", a), re.sub(r"\s+", " ", b)
        n_saved, n_verb = a.count("<\\"), b.count("<\\")
        eq = "identical" if a == b else ("equal_modulo_whitespace" if a2 == b2 else ("equal_modulo_neutralization(saved has %d '<\\\\' more)" % (n_saved - n_verb) if a.replace("<\\", "<") == b.replace("<\\", "<") else "DIFFERENT"))
        if eq != "identical":
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            diff = "pos %d: saved=%r verbatim=%r" % (i, a[max(0, i-15):i+25], b[max(0, i-15):i+25])
    print("\t".join([name or "", aid, str(len(text)), str(inlab), os.path.relpath(saved[0], repo) if saved else "none", eq, diff]))
