# builds one fresh lab per run (46 scripts in __instrumenta__/, colgrep index built by scripts/lab_init.py) and runs author workers headless in parallel on briefs that do not name the folder; input: export dir, scripts dir, run root, list of run ids 'task:rep'; output: per-run folders with stream-json and the lab, plus runs.json
"""usage: python3 -I e3_run_workers.py EXPORT SCRIPTS RUNROOT CAP_USD ID [ID ...]      ID = t1r1, t2r1, pilot-t1, ...

The task is the 't<digit>' in the id (t1 fit, t2 near fit, t3 near fit of the fit script, other alphabet); an id starting with 's' (st1r1) is arm S: the research PI is started and told to dispatch the author with the brief unchanged, so the worker is a subagent and gets the start note.
Each run: `claude -p --plugin-dir EXPORT --agent murmuration:author --permission-mode auto --max-budget-usd CAP`, cwd = the run's lab,
COLGREP_DATA_DIR inside the lab, CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0, CLAUDE_PROJECT_DIR unset.  Stdlib only; no seeds (the model samples).
"""
import json
import os
import re
import shutil
import subprocess
import sys

H = os.path.dirname(os.path.abspath(__file__))
QUESTION = "What does a worker do when scripts for its task already exist in the lab? (E3 test lab)"

BRIEFS = {
    "t1": ("for binary strings of length n, tabulate the maximum number of distinct non-empty substrings and the number of strings that "
           "reach it, for n = 1 to 14. File the claim with the table, labelled by what you ran."),
    "t2": ("among the start values 1 to 200000, find the start whose Collatz trajectory (3n+1 rule) reaches the highest peak value, "
           "and the peak. File the claim with the start and the peak, labelled by what you ran."),
    "t3": ("for strings over a three-letter alphabet, tabulate the maximum number of distinct non-empty substrings and the number of strings that "
           "reach it, for n = 1 to 9. File the claim with the table, labelled by what you ran."),
}


def task_of(rid):
    return re.search(r"t\d", rid).group(0)


def pi_prompt(rid):
    """Arm S (ids starting 's'): the research PI of the lab dispatches the author, so the SubagentStart note of scripts/budget.py reaches the worker."""
    return ("Dispatch one worker with the Agent tool: subagent_type murmuration:author, and as its prompt exactly the text between the two lines of dashes, "
            "unchanged. When it hands back, stop; do not do its work yourself.\n---\n%s\n---" % brief(rid))


def brief(rid):
    task = task_of(rid)
    return ("Your name is author-w04-3-%s. Claim id: w04-c9. Your verifier will be reproducer-w04-9.\n"
            "Hunch, from the principal investigator: %s Work by experiment.\n"
            "Budget: USD 1.00\nTime: min 10" % (rid, BRIEFS[task]))


def build_lab(rid, scripts, root, export):
    lab = os.path.join(root, rid, "lab")
    shutil.rmtree(os.path.join(root, rid), ignore_errors=True)
    os.makedirs(os.path.join(lab, "__instrumenta__"))
    for f in os.listdir(scripts):
        shutil.copy(os.path.join(scripts, f), os.path.join(lab, "__instrumenta__", f))
    env = dict(os.environ, COLGREP_DATA_DIR=os.path.join(lab, ".colgrep"))
    env.pop("CLAUDE_PROJECT_DIR", None)
    subprocess.run(["git", "init", "-q", "."], cwd=lab, check=True)
    out = subprocess.run([sys.executable, os.path.join(export, "scripts", "lab_init.py"), "--project", lab], input=QUESTION, text=True,
                         capture_output=True, env=env, cwd=lab, timeout=300)
    with open(os.path.join(root, rid, "lab_init.out"), "w") as fh:
        fh.write(out.stdout + out.stderr)
    with open(os.path.join(lab, ".gitignore"), "w") as fh:
        fh.write(".claude/settings.local.json\n.colgrep/\n")
    subprocess.run(["git", "add", "-A"], cwd=lab, check=True)
    subprocess.run(["git", "-c", "user.name=lab", "-c", "user.email=lab@example.invalid", "commit", "-qm", "lab: start"], cwd=lab, check=True)
    return lab, env


def main(argv):
    export, scripts, root, cap, ids = os.path.abspath(argv[0]), os.path.abspath(argv[1]), os.path.abspath(argv[2]), argv[3], argv[4:]
    procs = {}
    for rid in ids:
        lab, env = build_lab(rid, scripts, root, export)
        env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
        with open(os.path.join(root, rid, "brief.txt"), "w") as fh:
            fh.write(brief(rid))
        sub = re.match(r"(pilot-)?s", rid) is not None
        cmd = ["claude", "-p", "--plugin-dir", export, "--agent", "murmuration:research-pi" if sub else "murmuration:author", "--permission-mode", "auto",
               "--max-budget-usd", cap, "--output-format", "stream-json", "--verbose", pi_prompt(rid) if sub else brief(rid)]
        procs[rid] = subprocess.Popen(cmd, cwd=lab, env=env, stdout=open(os.path.join(root, rid, "run.jsonl"), "w"),
                                      stderr=open(os.path.join(root, rid, "run.err"), "w"))
    import time
    for rid, p in procs.items():
        t0, done_at = time.time(), None
        while p.poll() is None and time.time() - t0 < 1200:
            if done_at is None and '"type":"result"' in open(os.path.join(root, rid, "run.jsonl")).read()[-3000:]:
                done_at = time.time()          # the run has printed its result record
            if done_at is not None and time.time() - done_at > 30:
                p.terminate()                  # a worker's background job kept the process alive (xt2r1, 10 minutes): stop this run's own process by its handle
                break
            time.sleep(2)
        p.wait(timeout=60)
        print(rid, "exit", p.returncode)


if __name__ == "__main__":
    main(sys.argv[1:])
