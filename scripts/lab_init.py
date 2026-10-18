#!/usr/bin/env python3
"""Start a lab in a project, or add a question to the lab that is already there.

The question is read from stdin (so any text is safe to pass).

    lab_init.py [--project DIR]   initialize the lab if `__statera__/` is missing, otherwise
                                  append the question to `__statera__/user_words.md`
    lab_init.py --selftest        check the script on a temporary project

The project directory is --project, else CLAUDE_PROJECT_DIR, else the current directory.

Initializing creates, without overwriting anything that exists:
    __statera__/                 the state of the work
        user_words.md            the question, verbatim and dated
        wave-01.md               the first wave note, from the research-loop template
    __pondus__/                  one file per claim
    __scrupuli__/                the puzzles each agent raises
    __design__/framing.md        the framing, from the research-loop template
and merges into `.claude/settings.local.json` (personal settings; not for version control):
    "agent": "murmuration:research-pi"      new sessions in the folder open as the research PI
    permissions.deny: Bash(pkill:*), Bash(killall:*)
An `agent` setting that names something else, in that file or in `.claude/settings.json`, is left
alone and reported. Shared settings are never written.

Exit status: 0 done, 2 no question given, 3 `.claude/settings.local.json` exists but is not a JSON object.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import user_words  # noqa: E402  (a sibling script: one writer for the user's words)

PLUGIN_ROOT = os.path.dirname(HERE)
TEMPLATES = os.path.join(PLUGIN_ROOT, "skills", "research-loop", "templates")
AGENT = "murmuration:research-pi"
DENY = ["Bash(pkill:*)", "Bash(killall:*)"]
LOCAL_SETTINGS = os.path.join(".claude", "settings.local.json")
SHARED_SETTINGS = os.path.join(".claude", "settings.json")
NEXT_STEPS = [
    "Next: start a new Claude Code session in this folder (run `claude` here). It opens as the research PI.",
    "Then ask it to begin, for example: Let's begin.",
]
STORES = ["__statera__", "__pondus__", "__scrupuli__", "__design__"]


def project_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def template(name):
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as fh:
        return fh.read()


def first_wave_note(question, today):
    """The first wave note: the template with the number, date and the user's sentence filled in."""
    text = template("wave.md")
    text = text.replace("# Wave NN", "# Wave 01").replace("wNN", "w01")
    text = text.replace("opened: YYYY-MM-DD", "opened: %s" % today)
    quote = "\n".join("> " + line if line.strip() else ">" for line in question.splitlines())
    text = re.sub(r"^> <quoted from [^>]*>$", lambda _m: quote, text, count=1, flags=re.M)
    text = re.sub(r"\n*closed: YYYY-MM-DD\s*$", "\n", text)  # added by the PI when the wave closes
    return text


def read_settings(path):
    """The settings object at `path` ({} if absent). Raises ValueError if it is not a JSON object."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    return data


def merge_settings(data, shared=None):
    """Merge the lab's settings into `data` in place. Returns a list of notes about what happened.

    `shared` is the project's shared settings (read only): an `agent` named there that is not the
    PI is reported and left to win, since writing ours would silently override the team's choice.
    """
    notes = []
    current = data.get("agent")
    other = (shared or {}).get("agent")
    if current in (None, "") and other not in (None, "", AGENT):
        notes.append('kept the shared "agent": "%s" from .claude/settings.json (the lab expects "%s"; set it in '
                     '.claude/settings.local.json to open as the PI)' % (other, AGENT))
    elif current in (None, ""):
        data["agent"] = AGENT
        notes.append('set "agent": "%s"' % AGENT)
    elif current != AGENT:
        notes.append('kept the existing "agent": "%s" (the lab expects "%s"; change it to open as the PI)'
                     % (current, AGENT))
    perms = data.get("permissions")
    if not isinstance(perms, dict):
        perms = data["permissions"] = {}
    deny = perms.get("deny")
    if not isinstance(deny, list):
        deny = perms["deny"] = []
    added = [d for d in DENY if d not in deny]
    deny.extend(added)
    if added:
        notes.append("added permissions.deny: " + ", ".join(added))
    return notes


def initialize(root, question, now=None):
    """Create the lab in `root`. Returns the list of what was done."""
    now = now or datetime.datetime.now()
    settings_path = os.path.join(root, LOCAL_SETTINGS)
    settings = read_settings(settings_path)  # fail before touching anything else
    try:
        shared = read_settings(os.path.join(root, SHARED_SETTINGS))
    except ValueError:
        shared = {}  # not ours to repair
    done = []
    for store in STORES:
        path = os.path.join(root, store)
        if not os.path.isdir(path):
            os.makedirs(path)
            done.append("created %s/" % store)
    framing = os.path.join(root, "__design__", "framing.md")
    if os.path.exists(framing):
        done.append("kept the existing __design__/framing.md (the team's briefs expect the research-loop "
                    "framing format: question, notation, scope, rules)")
    else:
        with open(framing, "w", encoding="utf-8") as fh:
            fh.write(template("framing.md"))
        done.append("wrote __design__/framing.md (a stub for the PI to fill in)")
    user_words.append_words(root, question, now)
    done.append("recorded the question in __statera__/user_words.md")
    wave = os.path.join(root, "__statera__", "wave-01.md")
    if not os.path.exists(wave):
        with open(wave, "w", encoding="utf-8") as fh:
            fh.write(first_wave_note(question, now.strftime("%Y-%m-%d")))
        done.append("wrote __statera__/wave-01.md")
    notes = merge_settings(settings, shared)
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.write("\n")
    local = ".claude/settings.local.json"
    done += ["%s: %s" % (local, n) for n in notes] or ["%s: already as the lab needs it" % local]
    done.append("%s holds personal settings: keep it out of version control" % local)
    return done


def run(root, question):
    """Initialize or append. Returns (mode, what was done)."""
    if os.path.isdir(os.path.join(root, "__statera__")):
        if user_words.last_entry(root) == question.strip():
            return "append", ["the question is already the newest entry in __statera__/user_words.md; not repeated"]
        user_words.append_words(root, question)
        return "append", ["appended the question to __statera__/user_words.md"]
    return "init", initialize(root, question)


def selftest():
    import tempfile

    def load(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    with tempfile.TemporaryDirectory() as tmp:
        question = "Why does the \"3-bit\" case $HOME break?\nSecond line with 'quotes' and `ticks`."
        # Shared settings are never written; pre-existing personal settings are merged, not replaced.
        os.makedirs(os.path.join(tmp, ".claude"))
        shared_text = json.dumps({"model": "opus", "permissions": {"allow": ["Read"]}})
        with open(os.path.join(tmp, SHARED_SETTINGS), "w") as fh:
            fh.write(shared_text)
        with open(os.path.join(tmp, LOCAL_SETTINGS), "w") as fh:
            json.dump({"env": {"A": "1"}, "permissions": {"allow": ["Edit"], "deny": ["Bash(pkill:*)"]}}, fh)
        mode, done = run(tmp, question)
        assert mode == "init", mode
        for store in STORES:
            assert os.path.isdir(os.path.join(tmp, store)), store
        assert load(os.path.join(tmp, "__design__", "framing.md")) == template("framing.md")
        words = load(os.path.join(tmp, "__statera__", "user_words.md"))
        assert question in words and re.search(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", words, re.M)
        wave = load(os.path.join(tmp, "__statera__", "wave-01.md"))
        assert wave.startswith("# Wave 01") and "Why does the \"3-bit\" case $HOME break?" in wave
        assert "\n> Second line with 'quotes'" in wave
        assert "YYYY" not in wave and "NN" not in wave and "closed:" not in wave
        assert re.search(r"^opened: \d{4}-\d{2}-\d{2}$", wave, re.M)
        assert load(os.path.join(tmp, SHARED_SETTINGS)) == shared_text, "shared settings must not change"
        local = json.loads(load(os.path.join(tmp, LOCAL_SETTINGS)))
        assert local["agent"] == AGENT and local["env"] == {"A": "1"}
        assert local["permissions"]["allow"] == ["Edit"]
        assert local["permissions"]["deny"] == ["Bash(pkill:*)", "Bash(killall:*)"], local
        assert any("settings.local.json holds personal settings" in d for d in done), done
        # The first wave note is open to the status scripts, and the lab is readable by them.
        import lab_status
        assert lab_status.current_wave(tmp)[0] == 1 and lab_status.open_puzzles(tmp) == []
        # A second call appends and leaves everything else alone.
        before = load(os.path.join(tmp, "__statera__", "wave-01.md"))
        mode, _ = run(tmp, "a later question")
        assert mode == "append"
        assert load(os.path.join(tmp, "__statera__", "wave-01.md")) == before
        words = load(os.path.join(tmp, "__statera__", "user_words.md"))
        assert words.count("\n## ") == 2 and words.rstrip().endswith("a later question")
        # The same text twice in a row (the hook already recorded the user's answer) is kept once.
        _, done = run(tmp, "a later question")
        assert load(os.path.join(tmp, "__statera__", "user_words.md")) == words and "not repeated" in done[0], done
        # Merging again is idempotent.
        assert merge_settings(json.loads(load(os.path.join(tmp, LOCAL_SETTINGS)))) == []
        # A different `agent`, in either settings file, is kept and reported.
        other = os.path.join(tmp, "other")
        os.makedirs(os.path.join(other, ".claude"))
        with open(os.path.join(other, LOCAL_SETTINGS), "w") as fh:
            json.dump({"agent": "mine"}, fh)
        _, done = run(other, "q")
        assert json.loads(load(os.path.join(other, LOCAL_SETTINGS)))["agent"] == "mine"
        assert any("kept the existing" in d for d in done), done
        team = os.path.join(tmp, "team")
        os.makedirs(os.path.join(team, ".claude"))
        with open(os.path.join(team, SHARED_SETTINGS), "w") as fh:
            json.dump({"agent": "team-lead"}, fh)
        _, done = run(team, "q")
        assert "agent" not in json.loads(load(os.path.join(team, LOCAL_SETTINGS)))
        assert any("kept the shared" in d for d in done), done
        # Invalid personal settings stop the init before anything is written.
        bad = os.path.join(tmp, "bad")
        os.makedirs(os.path.join(bad, ".claude"))
        with open(os.path.join(bad, LOCAL_SETTINGS), "w") as fh:
            fh.write("{not json")
        try:
            run(bad, "q")
            raise AssertionError("invalid settings must stop the init")
        except ValueError:
            pass
        assert not os.path.exists(os.path.join(bad, "__statera__"))
        # From scratch: no .claude folder at all, and a framing file the project already has is kept.
        fresh = os.path.join(tmp, "fresh")
        os.makedirs(os.path.join(fresh, "__design__"))
        with open(os.path.join(fresh, "__design__", "framing.md"), "w") as fh:
            fh.write("my own framing\n")
        _, done = run(fresh, "q")
        assert json.loads(load(os.path.join(fresh, LOCAL_SETTINGS)))["agent"] == AGENT
        assert not os.path.exists(os.path.join(fresh, SHARED_SETTINGS))
        assert load(os.path.join(fresh, "__design__", "framing.md")) == "my own framing\n"
        assert any("kept the existing __design__/framing.md" in d for d in done), done
        # The command line: question on stdin, next steps printed after an init, exit 2 without a question.
        import subprocess
        cli = os.path.join(tmp, "cli")
        os.makedirs(cli)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        run_cli = lambda text: subprocess.run([sys.executable, os.path.abspath(__file__), "--project", cli],
                                              input=text, capture_output=True, text=True, env=env)
        out = run_cli("")
        assert out.returncode == 2 and not os.path.exists(os.path.join(cli, "__statera__"))
        out = run_cli("the question")
        assert out.returncode == 0 and "Lab initialized" in out.stdout, out
        assert "start a new Claude Code session in this folder" in out.stdout and "Let's begin" in out.stdout, out.stdout
        out = run_cli("another")
        assert out.returncode == 0 and "Question added" in out.stdout and "start a new" not in out.stdout, out
    print("PASS lab_init")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    root = project_root()
    if "--project" in argv:
        i = argv.index("--project")
        if i + 1 >= len(argv):
            print("lab_init.py: --project needs a directory", file=sys.stderr)
            return 2
        root = argv[i + 1]
    question = sys.stdin.read().strip()
    if not question:
        print("lab_init.py: no question given on stdin", file=sys.stderr)
        return 2
    try:
        mode, done = run(root, question)
    except ValueError:
        print("lab_init.py: %s exists but is not a JSON object; fix it and run again"
              % os.path.join(root, LOCAL_SETTINGS), file=sys.stderr)
        return 3
    print("%s in %s" % ("Lab initialized" if mode == "init" else "Question added", os.path.abspath(root)))
    for line in done:
        print("- " + line)
    if mode == "init":
        print()
        for line in NEXT_STEPS:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
