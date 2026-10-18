#!/usr/bin/env python3
"""Keep the user's own words, verbatim, in a lab project.

Runs as a UserPromptSubmit hook. It reads the hook JSON from stdin and, when the project is an
initialized lab (it has a `__statera__/` folder), appends the prompt to
`__statera__/user_words.md` under a dated heading.

A prompt is the user's own unless it is text the platform injected on someone else's behalf:
a message from another session, a task notification, or an agent message. Those are skipped, and
so are the lab's own slash commands, which record the question themselves.

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


def project_root(event_cwd=None):
    """The project directory: CLAUDE_PROJECT_DIR, else the hook's `cwd`, else the current one."""
    return os.environ.get("CLAUDE_PROJECT_DIR") or event_cwd or os.getcwd()


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


def handle(event):
    """Record the event's prompt if it is genuine and the project is a lab. Returns the path or None."""
    prompt = event.get("prompt")
    if not is_genuine(prompt) or not prompt.strip() or is_lab_command(prompt):
        return None
    root = project_root(event.get("cwd"))
    if not os.path.isdir(os.path.join(root, STORE)):
        return None
    return append_words(root, prompt)


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

    def fire(project, prompt, cwd=None):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
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
        fire(tmp, "second prompt")
        text = open(words, encoding="utf-8").read()
        assert "first words\nsecond line  with  spaces\n\n## not a heading of ours" in text
        assert "second prompt" in text
        for skipped in ("ignore me", "and me", "a new question", "before the lab exists"):
            assert skipped not in text, skipped
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", text, re.M)) == 2
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json",
                              capture_output=True, text=True)
        assert proc.returncode == 0
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
