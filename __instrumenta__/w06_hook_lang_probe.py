"""Runs headless `claude -p` (haiku) with a throwaway plugin of do-nothing hooks (sh, python3, compiled Rust, one stdout line each) in interleaved cells, and joins each hook's platform `durationMs` (session transcript, attachment hook_success) with its own start/end clock read from inside the script.

usage: w06_hook_lang_probe.py ROOT --reps N [--cells a,b,...] [--out rows.jsonl]   ROOT holds bin_master/ (noop.sh noop_s.sh noop.py noop-rs nowms; see header of each) and gets work/, cells/ and logs/ (outside any lab: runs below a plugin folder register it in installed_plugins.json).
Cell = (event UserPromptSubmit|PreToolUse, hook list, CLAUDE_CODE_SHELL, isolated?); isolated = `--setting-sources project,local` (no user settings, no enabled plugins, so no sibling hooks). PreToolUse cells ask for 4 `true` Bash calls (4 samples per run, one per call).
Output: one JSON line per hook record (cell, rep, event, lang, tag, dur_ms, ts, t0_start = ts - dur, body_t0, body_t1, load1 before the run) plus non-w06 sibling records (lang = "other"); then a median table per cell and language on stdout. Raw rows carry session ids: keep them outside the repository, commit only derived tables.
"""
import json, os, subprocess, sys, shutil, random, time, glob, statistics as st, datetime as dt
root = os.path.abspath(sys.argv[1]); argv = sys.argv
opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
reps = int(opt("--reps", 5)); out = opt("--out"); seed = int(opt("--seed", 20261021)); random.seed(seed)
BIN = {"sh": ("noop.sh", "%s"), "shs": ("noop_s.sh", "%s"), "py": ("noop.py", "python3 %s"), "rs": ("noop-rs", "%s")}
UPS = "UserPromptSubmit"; PTU = "PreToolUse"
def C(event, hooks, shell="/bin/bash", iso=False): return {"event": event, "hooks": hooks, "shell": shell, "iso": iso}
CELLS = {}
for ev, e in ((UPS, "ups"), (PTU, "ptu")):
    for lang in ("sh", "py", "rs"):
        CELLS["%s-%s-alone" % (e, lang)] = C(ev, [lang])
        CELLS["%s-%s-alone-iso" % (e, lang)] = C(ev, [lang], iso=True)
    CELLS["%s-all3" % e] = C(ev, ["sh", "py", "rs"])
    CELLS["%s-all3-iso" % e] = C(ev, ["sh", "py", "rs"], iso=True)
for lang in ("sh", "py", "rs"):
    CELLS["ups-%s-alone-zsh" % lang] = C(UPS, [lang], shell=None)
    CELLS["ups-%s-alone-iso-zsh" % lang] = C(UPS, [lang], shell=None, iso=True)
for n in (1, 4, 8):
    CELLS["ups-rs-x%d-iso" % n] = C(UPS, ["rs"] * n, iso=True)
    CELLS["ups-py-x%d-iso" % n] = C(UPS, ["py"] * n, iso=True)
    CELLS["ups-sh-x%d-iso" % n] = C(UPS, ["sh"] * n, iso=True)
CELLS["ups-shs-alone-iso"] = C(UPS, ["shs"], iso=True)
CELLS["ups-shs-alone"] = C(UPS, ["shs"])
CELLS["ups-stamped3-iso"] = C(UPS, ["shs", "py", "rs"], iso=True)
CELLS["ptu-stamped3-iso"] = C(PTU, ["shs", "py", "rs"], iso=True)
only = opt("--cells"); only = only.split(",") if only else list(CELLS)
os.makedirs(root + "/logs", exist_ok=True); os.makedirs(root + "/work", exist_ok=True)
def build(name, c):
    d = "%s/cells/%s" % (root, name)
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d + "/.claude-plugin"); os.makedirs(d + "/hooks"); shutil.copytree(root + "/bin_master", d + "/bin")
    json.dump({"name": "w06noop", "version": "0.0.1", "description": "throwaway"}, open(d + "/.claude-plugin/plugin.json", "w"))
    hs = []
    for i, lang in enumerate(c["hooks"]):
        f, tmpl = BIN[lang]
        hs.append({"type": "command", "command": tmpl % ('"${CLAUDE_PLUGIN_ROOT}/bin/%s"' % f) + " %s%d" % (lang, i), "timeout": 10})
    grp = {"hooks": hs}
    if c["event"] == PTU: grp["matcher"] = "Bash"
    json.dump({"hooks": {c["event"]: [grp]}}, open(d + "/hooks/hooks.json", "w"), indent=1)
    return d
dirs = {n: build(n, CELLS[n]) for n in only}
PROMPT = {UPS: "Reply with the single word ok.", PTU: "Call the Bash tool 4 times in a row, one call per turn, each with the command `true`. Write no other text."}
ts = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000
rows = []
if out: open(out, "w").close()
plan = [n for _ in range(reps) for n in random.sample(only, len(only))]
for k, n in enumerate(plan):
    c = CELLS[n]; log = "%s/logs/%d.log" % (root, k)
    if os.path.exists(log): os.remove(log)
    env = dict(os.environ, W06_LOG=log)
    env.pop("CLAUDE_CODE_SHELL", None)
    if c["shell"]: env["CLAUDE_CODE_SHELL"] = c["shell"]
    cmd = ["claude", "-p", PROMPT[c["event"]], "--model", "haiku", "--plugin-dir", dirs[n], "--output-format", "json"]
    if c["iso"]: cmd += ["--setting-sources", "project,local"]
    if c["event"] == PTU: cmd += ["--allowedTools", "Bash(true)"]
    load1 = os.getloadavg()[0]
    r = subprocess.run(cmd, cwd=root + "/work", env=env, capture_output=True, text=True, timeout=240, stdin=subprocess.DEVNULL)
    try: j = json.loads(r.stdout)
    except ValueError: print("ERR", n, (r.stdout + r.stderr)[:200], flush=True); continue
    sid = j["session_id"]; recs = []
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid)):
        for line in open(f):
            if '"hook_' not in line: continue
            rec = json.loads(line); a = rec.get("attachment") or {}
            if a.get("type") in ("hook_success", "hook_non_blocking_error", "hook_cancelled", "hook_blocking_error") and a.get("durationMs") is not None:
                recs.append((ts(rec["timestamp"]), a))
    logl = [json.loads(x) for x in open(log)] if os.path.exists(log) else []
    bytag = {}
    for x in logl: bytag.setdefault(x["tag"], []).append(x)
    for v in bytag.values(): v.sort(key=lambda x: x["t0_ms"])
    seen = {}
    for t, a in sorted(recs, key=lambda x: x[0]):
        cm = a.get("command") or ""; row = {"cell": n, "rep": k, "event": a.get("hookEvent"), "dur_ms": a["durationMs"], "ts": t, "t0_start": t - a["durationMs"], "load1": load1, "stdout": (a.get("stdout") or "")[:30], "label": cm[:70]}
        if "noop" in cm and "${CLAUDE_PLUGIN_ROOT}" in cm:
            lang_tag = cm.split()[-1]; row["tag"] = lang_tag; row["lang"] = lang_tag.rstrip("0123456789")
            i = seen.get(lang_tag, 0); seen[lang_tag] = i + 1
            lg = bytag.get(lang_tag, []); 
            if i < len(lg): row["body_t0"] = lg[i]["t0_ms"]; row["body_t1"] = lg[i]["t1_ms"]
        else: row["lang"] = "other"
        rows.append(row)
    if out: open(out, "a").write("".join(json.dumps(x) + "\n" for x in rows if x["rep"] == k))
    print(n, k, "load %.1f" % load1, [(x["lang"], x["dur_ms"]) for x in rows if x["rep"] == k and x["event"] == c["event"]], flush=True)
print("| cell | event | lang | n | median ms | p10 | p90 | min | max |\n|:--|:--|:--|--:|--:|--:|--:|--:|--:|")
agg = {}
for x in rows: agg.setdefault((x["cell"], x["event"], x["lang"]), []).append(x["dur_ms"])
for (cn, ev, lang), v in sorted(agg.items()):
    if lang == "other" and ev != CELLS[cn]["event"]: continue
    v = sorted(v); q = lambda p: v[int(p * (len(v) - 1))]
    print("| %s | %s | %s | %d | %.0f | %.0f | %.0f | %.0f | %.0f |" % (cn, ev, lang, len(v), st.median(v), q(.1), q(.9), v[0], v[-1]))
