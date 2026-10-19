#!/usr/bin/env python3
"""Keep the user's own words, verbatim, in a lab project.

Runs as a UserPromptSubmit hook. It reads the hook JSON from stdin and, when the project is an
initialized lab (it has a `__statera__/` folder), appends the prompt to
`__statera__/user_words.md` under a dated heading.

A prompt is the user's own unless it is text the platform injected on someone else's behalf:
a message from another session, a task notification, or an agent message. Those are skipped, and
so are the lab's own slash commands (which record the question themselves) and bare slash
commands such as `/clear` or `/compact`, which carry no words. Platform blocks the app puts in
front of the typed text (`<system-reminder>`, `<artifact-view-context>`, `<side-sessions-event>`)
are cut first, and the app's `<pasted_content>` wrapper is removed around pasted text; what is
left is stored.

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
# Blocks the platform puts before the typed text, cut only at the start of the prompt. The
# `<system-reminder>` form is the exact one seen: `<system-reminder>\n...\n</system-reminder>`.
LEADING_BLOCKS = (
    re.compile(r"\A\s*<system-reminder>\n.*?\n</system-reminder>(?:[ \t]*\n)*", re.S),
    re.compile(r"\A\s*<artifact-view-context\b[^>]*>.*?</artifact-view-context>(?:[ \t]*\n)*", re.S),
    re.compile(r"\A\s*<side-sessions-event>.*?</side-sessions-event>(?:[ \t]*\n)*", re.S),
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


def strip_leading(prompt):
    """The prompt without the platform blocks in front of the typed text. The paste wrapper stays."""
    changed = True
    while changed:
        changed = False
        for block in LEADING_BLOCKS:
            prompt, n = block.subn("", prompt, count=1)
            changed = changed or bool(n)
    return prompt


def unwrap_pasted(text):
    """The text with the paste wrapper removed, one level, and leading blank lines dropped."""
    return re.sub(r"\A\s*\n", "", PASTED.sub(lambda m: m.group(2), text))


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
    prompt = strip_leading(prompt)  # the command tests below see the paste wrapper, so pasted `/lab ...` is kept
    if not is_genuine(prompt) or not prompt.strip() or is_lab_command(prompt) or is_bare_command(prompt):
        return None
    words = unwrap_pasted(prompt)
    root = project_root(event.get("cwd"))
    if not words.strip() or not os.path.isdir(os.path.join(root, STORE)):
        return None
    return append_words(root, words)


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
    # Platform blocks and the paste wrapper: what a prompt stores (None = nothing).
    rem = "<system-reminder>\nLinked sessions now (status): a = local_1 (idle).\n</system-reminder>\n\n"
    view = '<artifact-view-context artifact="x">\n{"context":{}}\n(not typed)\n</artifact-view-context>\n\n'
    side = "<side-sessions-event>\nsession a finished a turn\n</side-sessions-event>\n\n"

    def paste(i, body):
        return '<pasted_content id="%s">\n%s\n</pasted_content id="%s">' % (i, body, i)

    cases = [
        (rem + "typed words", "typed words"),
        (rem + "\n" + rem + "twice", "twice"),
        (rem + view + "reply", "reply"),
        (side + "words", "words"),
        (rem + side, None),
        (rem.rstrip(), None),
        (rem + "/lab what next", None),
        (rem + "/clear", None),
        (rem + '<cross-session-message from="x">hi</cross-session-message>', None),
        (rem + "<task-notification>done</task-notification>", None),
        (paste("a", "line one\n\nline two"), "line one\n\nline two"),
        (rem + paste("a", "pasted words"), "pasted words"),
        ("see this:\n" + paste("a", "line"), "see this:\nline"),
        (paste("a", "/lab inside a paste"), "/lab inside a paste"),
        (paste("a", "/clear"), "/clear"),
        (rem + paste("a", "/lab inside"), "/lab inside"),
        ("/lab typed outside " + paste("a", "x"), None),
        (paste("a", "  \n "), None),
        ('<pasted_content id="a">\n\n</pasted_content id="a">', None),
        (paste("a", "outer " + paste("b", "inner") + " end"), 'outer ' + paste("b", "inner") + ' end'),
        # left untouched: not at the start, one-line, other line endings, unclosed, other id, quote, indentation
        ("see <system-reminder>\nx\n</system-reminder> above", "see <system-reminder>\nx\n</system-reminder> above"),
        ("<system-reminder>one line</system-reminder> is a tag", "<system-reminder>one line</system-reminder> is a tag"),
        ("<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi", "<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi"),
        ("<system-reminder>\nx\nhi", "<system-reminder>\nx\nhi"),
        ('<pasted_content id="a">\nx\n</pasted_content id="b">', '<pasted_content id="a">\nx\n</pasted_content id="b">'),
        (rem + "typed\n" + rem.rstrip(), "typed\n" + rem.rstrip()),
        ("> quoted sentence\n\nthat is fine", "> quoted sentence\n\nthat is fine"),
        ("  indented first line\nsecond", "  indented first line\nsecond"),
        (rem + "\n    code line\nnext", "    code line\nnext"),
        (rem + "  indented after a block", "  indented after a block"),
        ("\n\nhi", "hi"),
        # a typed block in the exact reminder form is cut like the platform's
        ("<system-reminder>\nremember\n</system-reminder>\n\nmy question", "my question"),
        ("<system-reminder>\nremember\n</system-reminder>", None),
    ]
    for prompt, want in cases:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, STORE))
            fire(tmp, prompt)
            path = os.path.join(tmp, STORE, FILE_NAME)
            got = None
            if os.path.exists(path):  # newline="" keeps a CRLF as stored
                body = open(path, encoding="utf-8", newline="").read()
                got = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", body, flags=re.M)[-1][:-1]
            assert got == want, (prompt, got, want)
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
