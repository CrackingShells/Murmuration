# Runs the live cells of protocol P2 (w08-c2): builds two plugin exports (gate on = the branch commit, gate off = its parent; only the handback hook rows), and runs one headless cell: a haiku parent dispatches one haiku worker (explorer or author role) with a task whose natural hand-back is long or short; writes the lab folder, ground truth, stream-json and meta.json under <S>/runs/<cell>/ and copies nothing outside S.
# usage: w08_c2_live.py exports S REPO REV_ON REV_OFF
#        w08_c2_live.py cell S CELL            (CELL: e_on_auto, e_on_default, e_off_auto, e_short_auto, e_repeat_auto, a_on_auto, a_off_auto, a_nopath_auto, e_on_auto_r2, e_on_auto_r3, a_on_auto_r2, a_on_auto_r3)
# Cell names: e = explorer role, a = author role; on/off = gate on/off; auto/default = permission mode; short = a task with a short hand-back; repeat = the worker is told to resend an identical message after a deny; nopath = no file path in the brief.
# Seeds: the files' contents come from random.Random(8 + the index in CELLS of the cell, or of its gate-on pair for a gate-off cell); the model has no seed. Stdlib only. Permission mode is auto or default, never bypassed; the user's own settings load as they do for any session.
import json, os, random, shutil, subprocess, sys, tarfile, io, time

CELLS = ["e_on_auto", "e_on_default", "e_off_auto", "e_short_auto", "e_repeat_auto", "a_on_auto", "a_off_auto", "a_nopath_auto", "e_on_auto_r2", "e_on_auto_r3", "a_on_auto_r2", "a_on_auto_r3"]


def exports(S, repo, on, off):
    for tag, rev in (("on", on), ("off", off)):
        d = os.path.join(S, "exp_" + tag)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        tar = subprocess.run(["git", "-C", repo, "archive", rev, "agents", "skills", "scripts", "hooks", ".claude-plugin"], capture_output=True, check=True).stdout
        tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="data")
        pj = json.load(open(d + "/.claude-plugin/plugin.json"))
        pj.pop("mcpServers", None)
        json.dump(pj, open(d + "/.claude-plugin/plugin.json", "w"), indent=2)
        hooks = json.load(open(d + "/hooks/hooks.json"))["hooks"]
        keep = {}
        for ev, groups in hooks.items():
            g2 = []
            for g in groups:
                hs = [h for h in g["hooks"] if "handback" in " ".join(h.get("args", []))]
                if hs:
                    g2.append(dict(g, hooks=hs))
            if g2:
                keep[ev] = g2
        json.dump({"hooks": keep}, open(d + "/hooks/hooks.json", "w"), indent=2)
        print(tag, rev, d, sorted(keep), "plugin name", pj.get("name"))


FIRST = "Quill Marsh Fen Cairn Wren Slate Briar Hollow Tarn Vale Heath Moor".split()
SECOND = "moor reach ford gate wick stead haven mere".split()


def make_files(lab, rnd, n):
    ground, used = {}, set()
    for i in range(1, n + 1):
        while True:
            st = "%s%s" % (rnd.choice(FIRST), rnd.choice(SECOND))
            if st not in used:
                used.add(st)
                break
        yr, pop, days = rnd.randint(1800, 1950), rnd.randint(11000, 98000), rnd.randint(3, 30)
        fa = "%s %s" % (rnd.choice("Ada Bram Cora Dov Elin Faro".split()), rnd.choice("Verrin Holt Maro Ashby Pell".split()))
        trade = rnd.choice(["salt harvesting", "peat cutting", "weaving", "ferry work"])
        open(os.path.join(lab, "f%03d.txt" % i), "w").write(
            "The %s station was founded in %d by %s and stands on a wide valley floor. Its population is %d people, most of whom work in %s. "
            "A local saying holds that the dry wind arrives every %d days.\n" % (st, yr, fa, pop, trade, days))
        ground["f%03d" % i] = dict(station=st, year=yr, founder=fa, population=pop, trade=trade, days=days)
    return ground


PARA = ("for every file one paragraph of at least 120 words, a full 700 characters or more, with the station name, the founding year, the founder, the population, the main trade, "
        "the number of days of the dry-wind saying, and a sentence about its setting.")


def brief(kind, name, n, report, claim):
    files = "the %d files f001.txt to f%03d.txt in the current directory (`cat fNNN.txt`)" % (n, n)
    if kind == "e_long":
        return ("Read %s. Your deliverable is the findings report at %s, from the findings template of the research-loop skill: its Table holds one row per file, with the file name, "
                "the station name and the founding year only. Your hand-back message must give the complete list for the PI, so that the PI does not need to open anything: %s" % (files, report, PARA))
    if kind == "e_short":
        return ("Read %s. Your deliverable is the findings report at %s, from the findings template of the research-loop skill: its Table holds one row per file, with the file name, "
                "the station name and the founding year. Hand back with a message of two sentences that points to the report." % (files, report))
    if kind == "e_repeat":
        return brief("e_long", name, n, report, claim) + " If the hook that checks your hand-back denies it, call SubagentHandback again at once with exactly the same message, word for word: do not shorten it."
    if kind == "a_long":
        return ("You are filing a claim head. Read %s. File the head of the claim w08-x2 at %s: a title line `# w08-x2: <the claim>`, then `label: MEASURED`, `scope:`, `evidence:`, `method:` and `author: %s` lines. "
                "The claim: the founding years of the stations in the files span a stated range, with the oldest and newest station. Your hand-back message must give the complete list for the verifier, "
                "so that nobody needs to open anything: %s" % (files, claim, name, PARA))
    if kind == "a_nopath":
        return "Read %s. There is no file to write: answer only in your hand-back message. It must give the complete list: %s" % (files, PARA)
    raise ValueError(kind)


SEEDLIKE = {"e_off_auto": "e_on_auto", "a_off_auto": "a_on_auto"}
SPEC = {  # cell: (role, brief kind, files, gate arm, permission mode)
    "e_on_auto": ("explorer", "e_long", 14, "on", "auto"),
    "e_on_default": ("explorer", "e_long", 14, "on", "default"),
    "e_off_auto": ("explorer", "e_long", 14, "off", "auto"),
    "e_short_auto": ("explorer", "e_short", 4, "on", "auto"),
    "e_repeat_auto": ("explorer", "e_repeat", 14, "on", "auto"),
    "a_on_auto": ("author", "a_long", 14, "on", "auto"),
    "a_off_auto": ("author", "a_long", 14, "off", "auto"),
    "a_nopath_auto": ("author", "a_nopath", 14, "on", "auto"),
    "e_on_auto_r2": ("explorer", "e_long", 14, "on", "auto"),   # replicates of the gate-on cells with other files
    "e_on_auto_r3": ("explorer", "e_long", 14, "on", "auto"),
    "a_on_auto_r2": ("author", "a_long", 14, "on", "auto"),
    "a_on_auto_r3": ("author", "a_long", 14, "on", "auto"),
}


def cell(S, c):
    role, kind, n, arm, mode = SPEC[c]
    plugin = os.path.join(S, "exp_" + arm)
    base = os.path.join(S, "runs", c)
    shutil.rmtree(base, ignore_errors=True)
    lab = os.path.join(base, "lab")
    os.makedirs(lab)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    env.update(CLAUDE_CODE_SHELL="/bin/bash", CLAUDE_CODE_SUBAGENT_MODEL="haiku", CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0", COLGREP_DATA_DIR=os.path.join(base, "colgrep"))
    os.makedirs(env["COLGREP_DATA_DIR"])
    subprocess.run([sys.executable, os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab], input="What is the founding year of each station?", text=True, capture_output=True, check=True, env=env)
    shutil.rmtree(os.path.join(lab, ".claude"), ignore_errors=True)   # the lab's local settings would open the session as the research PI; the cell's parent is a plain haiku session
    ground = make_files(lab, random.Random(8 + CELLS.index(SEEDLIKE.get(c, c))), n)   # a gate-off cell reads the same files as its gate-on pair
    json.dump(ground, open(os.path.join(base, "ground.json"), "w"))   # outside the lab
    name = "%s-w08-x%d" % (role, CELLS.index(c) + 1)
    report = "__reports__/wave-08/%s/00-findings_v0.md" % name
    claim = "__pondus__/w08-x2.md"
    text = "Your name is %s.\nBudget: USD 0.50\nTime: min 20\n%s" % (name, brief(kind, name, n, report, claim))
    json.dump(dict(cell=c, name=name, role=role, kind=kind, files=n, arm=arm, mode=mode, brief_chars=len(text)), open(os.path.join(base, "spec.json"), "w"))
    prompt = ("Step 1: call the Agent tool once with subagent_type 'murmuration:%s', name '%s', model 'haiku', run_in_background true, with exactly the text between the lines ==== as its prompt (keep every line, change nothing).\n====\n%s\n====\n"
              "Step 2: wait for the worker's completion notification (while waiting, run `sleep 20` with Bash, one call at a time, at most 40 times). Do not end your turn before it arrives. "
              "Do not read the worker's files and do not do its work. Then say DONE.\n" % (role, name, text))
    cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", plugin, "--strict-mcp-config", "--permission-mode", mode, "--output-format", "stream-json", "--verbose", "--include-hook-events"]
    if mode == "default":
        cmd += ["--allowedTools", "Bash", "Read", "Write", "Edit", "Agent", "Glob", "Grep"]
    t0 = time.time()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=lab, env=env, timeout=1500)   # the prompt on stdin: --allowedTools takes a list and would swallow it as an argument
    open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout)
    open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
    res = None
    for l in p.stdout.splitlines():
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if r.get("type") == "result":
            res = r
    json.dump(dict(cell=c, name=name, arm=arm, mode=mode, wall_s=round(time.time() - t0, 1), rc=p.returncode, usd=res and res.get("total_cost_usd"), turns=res and res.get("num_turns"),
                   session=res and res.get("session_id"), model_usd={k: v.get("costUSD") for k, v in ((res or {}).get("modelUsage") or {}).items()}), open(os.path.join(base, "meta.json"), "w"))
    print(open(os.path.join(base, "meta.json")).read())


if __name__ == "__main__":
    if sys.argv[1] == "exports":
        exports(os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        cell(os.path.abspath(sys.argv[2]), sys.argv[3])
