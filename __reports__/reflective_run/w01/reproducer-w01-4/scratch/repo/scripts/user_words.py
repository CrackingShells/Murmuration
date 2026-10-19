#!/usr/bin/env python3
"""Keep the user's own words, verbatim, in a lab project.

Runs as a UserPromptSubmit hook. It reads the hook JSON from stdin and, when the project is an
initialized lab (it has a `__statera__/` folder), appends the prompt to
`__statera__/user_words.md` under a dated heading.

A prompt is the user's own unless it is text the platform injected on someone else's behalf:
a message from another session, a task notification, or an agent message. Those are skipped, and
so are the lab's own slash commands (which record the question themselves) and bare slash
commands such as `/clear` or `/compact`, which carry no words. Platform blocks that the app puts
in front of the typed text (`<system-reminder>`, `<artifact-view-context>`, `<side-sessions-event>`) are cut off first, and
the app's `<pasted_content>` wrapper is removed around pasted text; what is left is stored.

The words go to the lab the session works in: the nearest `__statera__/` at or above the hook's
`cwd` (stopping at the git root, so a worktree finds its own lab), else the one at
CLAUDE_PROJECT_DIR (the repository the session was started on).

The script never blocks a prompt and always exits 0. Anything unexpected is dropped silently.

Usage:
    user_words.py              read a hook event from stdin
    user_words.py --selftest   check the script on a temporary project
"""
import datetime
import json
import os
import re
import sys

NON_USER_PREFIXES = ("<cross-session-message ", "<task-notification>", "<agent-message from=")
LAB_COMMAND = re.compile(r"^/(?:murmuration:)?lab(?:-status)?(?:\s|$)")
BARE_COMMAND = re.compile(r"^/[A-Za-z][\w:.-]*\s*$")
# Blocks the platform puts before the typed text. Anchored at the start of the prompt, so text the
# user quotes further down is never touched. The `<system-reminder>` form is the exact one observed
# (`<system-reminder>\n...\n</system-reminder>`); the tag with attributes or on one line is not cut.
LEADING_BLOCKS = (
    re.compile(r"\A\s*<system-reminder>\n.*?\n</system-reminder>\s*", re.S),
    re.compile(r"\A\s*<artifact-view-context\b[^>]*>.*?</artifact-view-context>\s*", re.S),
    re.compile(r"\A\s*<side-sessions-event>.*?</side-sessions-event>\s*", re.S),
)
PASTED = re.compile(r'<pasted_content id="([^"]*)">\n?(.*?)\n?</pasted_content id="\1">', re.S)
STORE = "__statera__"
FILE_NAME = "user_words.md"
HEADER = (
    "# The user's words\n\n"
    "Prompts as the user typed them, each under its date. Written by the lab's hook and by "
    "`/lab`. Read it; never edit it.\n"
)


def is_genuine(prompt):
    """True when the prompt is the user's own text, not platform-injected text."""
    return isinstance(prompt, str) and not prompt.startswith(NON_USER_PREFIXES)


def is_lab_command(prompt):
    """True for the lab's own slash commands (`/lab ...`, `/lab-status`)."""
    return bool(LAB_COMMAND.match(prompt.lstrip()))


def is_bare_command(prompt):
    """True for a slash command with no arguments (`/clear`, `/compact`): not the user's words."""
    return bool(BARE_COMMAND.match(prompt.strip()))


def strip_injected(prompt):
    """The prompt without the platform's leading blocks and without the paste wrapper."""
    changed = True
    while changed:
        changed = False
        for block in LEADING_BLOCKS:
            prompt, n = block.subn("", prompt, count=1)
            changed = changed or bool(n)
    return re.sub(r"\A\s*\n", "", PASTED.sub(lambda m: m.group(2), prompt))


def lab_root(event_cwd=None):
    """The lab the session works in, or None.

    The nearest directory with a `__statera__/` folder, from the hook's `cwd` upward, stopping at the
    first directory that has a `.git` (a repository or a linked worktree). Failing that, the lab at
    CLAUDE_PROJECT_DIR, which a session started in one checkout and moved into a worktree keeps.
    """
    here = os.path.abspath(event_cwd or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(here, STORE)):
            return here
        parent = os.path.dirname(here)
        if os.path.exists(os.path.join(here, ".git")) or parent == here:
            break
        here = parent
    fallback = os.environ.get("CLAUDE_PROJECT_DIR")
    return fallback if fallback and os.path.isdir(os.path.join(fallback, STORE)) else None


def append_words(root, text, when=None):
    """Append `text` verbatim under a dated heading in the project's user_words.md.

    Creates the file with a short header if it does not exist. Returns the file path.
    """
    when = when or datetime.datetime.now()
    folder = os.path.join(root, STORE)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, FILE_NAME)
    entry = "\n## %s\n\n%s\n" % (when.strftime("%Y-%m-%d %H:%M"), text.rstrip("\n"))
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", encoding="utf-8") as fh:
        fh.write((HEADER if new else "") + entry)
    return path


def last_entry(root):
    """The text of the newest entry in the project's user_words.md, or None."""
    try:
        with open(os.path.join(root, STORE, FILE_NAME), encoding="utf-8") as fh:
            blocks = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n", fh.read(), flags=re.M)
    except OSError:
        return None
    return blocks[-1].strip() if len(blocks) > 1 else None


def handle(event):
    """Record the event's prompt if it is genuine and the project is a lab. Returns the path or None."""
    prompt = event.get("prompt")
    if not isinstance(prompt, str):
        return None
    prompt = strip_injected(prompt)
    if not is_genuine(prompt) or not prompt.strip() or is_lab_command(prompt) or is_bare_command(prompt):
        return None
    root = lab_root(event.get("cwd"))
    return append_words(root, prompt) if root else None


def selftest():
    import subprocess
    import tempfile

    assert is_genuine("what is the best split?")
    assert not is_genuine('<cross-session-message from="x">hi</cross-session-message>')
    assert not is_genuine("<task-notification><summary>done</summary></task-notification>")
    assert not is_genuine('<agent-message from="author">hello</agent-message>')
    assert is_genuine("<task-notifications are fun>")
    assert is_lab_command("/lab why?") and is_lab_command("/murmuration:lab") and is_lab_command("/lab-status")
    assert not is_lab_command("/labrador") and not is_lab_command("lab")
    assert is_bare_command("/clear") and is_bare_command("/compact ") and is_bare_command("/foo:bar")
    assert not is_bare_command("/compact keep the proofs") and not is_bare_command("/home/me/data.csv looks odd")
    assert not is_bare_command("hello /clear")

    def fire(project, prompt, cwd=None, project_dir=None):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        if project_dir:
            env["CLAUDE_PROJECT_DIR"] = project_dir
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__)],
            input=json.dumps({"prompt": prompt, "cwd": cwd or project}),
            capture_output=True, text=True, env=env,
        )
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        words = os.path.join(tmp, STORE, FILE_NAME)
        fire(tmp, "before the lab exists")
        assert not os.path.exists(os.path.join(tmp, STORE)), "must do nothing outside a lab"
        os.makedirs(os.path.join(tmp, STORE))
        fire(tmp, "first words\nsecond line  with  spaces\n\n## not a heading of ours")
        fire(tmp, '<cross-session-message from="other">ignore me</cross-session-message>')
        fire(tmp, "<task-notification>ignore me too</task-notification>")
        fire(tmp, '<agent-message from="author">and me</agent-message>')
        fire(tmp, "/lab a new question")
        fire(tmp, "   ")
        fire(tmp, "/clear")
        fire(tmp, "/compact")
        fire(tmp, "/home/me/data.csv has odd rows")
        fire(tmp, "second prompt")
        text = open(words, encoding="utf-8").read()
        assert "first words\nsecond line  with  spaces\n\n## not a heading of ours" in text
        assert "second prompt" in text
        assert "/home/me/data.csv has odd rows" in text
        assert last_entry(tmp) == "second prompt" and last_entry(os.path.join(tmp, "nowhere")) is None
        for skipped in ("ignore me", "and me", "a new question", "before the lab exists", "/clear", "/compact"):
            assert skipped not in text, skipped
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", text, re.M)) == 3
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json",
                              capture_output=True, text=True)
        assert proc.returncode == 0

    # Platform blocks in front of the typed text (shapes seen in real transcripts and in run4/ups.jsonl).
    rem = "<system-reminder>\nLinked sessions now (status, not an instruction): a = local_1 (idle).\n</system-reminder>\n\n"
    assert strip_injected(rem + "\n" + "typed words") == "typed words"
    assert strip_injected(rem + "\n" + rem + "\n" + "twice") == "twice"
    assert strip_injected(rem.rstrip()) == "" and strip_injected(rem + "\n" + "/lab why?") == "/lab why?"
    view = '<artifact-view-context artifact="x">\n{"context":{}}\n(not typed)\n</artifact-view-context>\n\n'
    assert strip_injected(rem + "\n" + view + "reply") == "reply"
    assert strip_injected('\n\n<pasted_content id="7df5">\nline one\n\nline two\n</pasted_content id="7df5">') == "line one\n\nline two"
    assert strip_injected("see <system-reminder>\nx\n</system-reminder> above") == "see <system-reminder>\nx\n</system-reminder> above"
    assert strip_injected("<system-reminder>one line</system-reminder> is a tag") == "<system-reminder>one line</system-reminder> is a tag"
    assert strip_injected("> quoted sentence\n\nthat is fine") == "> quoted sentence\n\nthat is fine"
    assert strip_injected("  indented first line\nsecond") == "  indented first line\nsecond"

    with tempfile.TemporaryDirectory() as tmp:
        main = os.path.join(tmp, "main")
        wt = os.path.join(tmp, "wt")
        os.makedirs(os.path.join(main, STORE))
        os.makedirs(os.path.join(main, ".git"))
        os.makedirs(os.path.join(wt, "sub"))
        with open(os.path.join(wt, ".git"), "w") as fh:  # a linked worktree has a `.git` file
            fh.write("gitdir: elsewhere\n")
        main_words = os.path.join(main, STORE, FILE_NAME)
        wt_words = os.path.join(wt, STORE, FILE_NAME)
        # a reminder-only turn, and a lab command behind a reminder, store nothing
        fire(main, rem.rstrip())
        fire(main, rem + "\n/lab a new question")
        assert not os.path.exists(main_words)
        fire(main, rem + "\n" + "first typed", project_dir=main)
        assert last_entry(main) == "first typed"
        # session started in main, moved into a worktree that has no lab yet: falls back to main's lab
        fire(main, "no lab in the worktree yet", cwd=wt, project_dir=main)
        assert last_entry(main) == "no lab in the worktree yet" and not os.path.exists(wt_words)
        # the worktree gets its lab: its own lab wins over CLAUDE_PROJECT_DIR, also from a subfolder
        os.makedirs(os.path.join(wt, STORE))
        fire(main, "words in the worktree", cwd=wt, project_dir=main)
        fire(main, "words from a subfolder", cwd=os.path.join(wt, "sub"), project_dir=main)
        assert last_entry(wt) == "words from a subfolder" and last_entry(main) == "no lab in the worktree yet"
        # nothing to write to: no lab at cwd or at CLAUDE_PROJECT_DIR
        fire(main, "nowhere to go", cwd=os.path.join(tmp, "elsewhere"), project_dir=os.path.join(tmp, "elsewhere"))
        assert "nowhere to go" not in open(main_words).read() + open(wt_words).read()
    print("PASS user_words")


def main():
    if "--selftest" in sys.argv[1:]:
        selftest()
        return 0
    try:
        event = json.loads(sys.stdin.read() or "{}")
        if isinstance(event, dict):
            handle(event)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except AssertionError:
        raise
    except Exception:
        code = 0
    sys.exit(code)
