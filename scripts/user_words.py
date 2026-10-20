#!/usr/bin/env python3
"""Keep the user's own words, verbatim, in a lab project.

Runs as a UserPromptSubmit hook. It reads the hook JSON from stdin and, when the project is an
initialized lab (it has a `__statera__/` folder), appends the prompt to
`__statera__/user_words.md` under a dated heading. The lab is found from the session's first
recorded `cwd` (head of the transcript), else the payload `cwd`, else CLAUDE_PROJECT_DIR; see
`project_root`.

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
HEAD_LINES = 200  # how much of a transcript session_cwd() may read
HEAD_BYTES = 1 << 20
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


def session_cwd(transcript_path):
    """The `cwd` of the first record of the session transcript that carries one, or None.

    Reads only the head of the file (at most HEAD_LINES lines or HEAD_BYTES bytes): the first records
    are queue operations without a `cwd`, the next ones carry the directory the session started in.
    """
    if not isinstance(transcript_path, str) or not transcript_path:
        return None
    seen = 0
    try:
        with open(transcript_path, "rb") as fh:
            for number, line in enumerate(fh):
                seen += len(line)
                if b'"cwd"' in line:
                    try:
                        record = json.loads(line)
                    except ValueError:
                        record = None
                    cwd = record.get("cwd") if isinstance(record, dict) else None
                    if isinstance(cwd, str) and os.path.isabs(cwd):
                        return cwd
                if number + 1 >= HEAD_LINES or seen >= HEAD_BYTES:
                    return None
    except OSError:
        pass
    return None


def lab_above(start):
    """The nearest directory at or above `start` with a `__statera__/` folder, or None.

    The walk stops at the first directory that has a `.git` entry (a folder, or the file of a linked
    worktree), after testing that directory itself: it never leaves the repository `start` is in.
    """
    here = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(here, STORE)):
            return here
        parent = os.path.dirname(here)
        if os.path.exists(os.path.join(here, ".git")) or parent == here:
            return None
        here = parent


def project_root(event):
    """The lab a hook event belongs to, or None. In this order:

    1. the session's first recorded `cwd` (transcript head), searched upward; the live `cwd` of the
       payload follows the Bash tool's `cd`, the session's first one does not;
    2. the payload `cwd` the same way, only when the transcript has no `cwd` yet (the first prompt of
       a session may come before any record is on disk);
    3. CLAUDE_PROJECT_DIR itself, when it has a lab (the Desktop's value is the main checkout, which
       is wrong in a worktree and right when the session started elsewhere);
    else None: nothing is written.
    """
    event = event if isinstance(event, dict) else {}
    start = session_cwd(event.get("transcript_path"))
    if start is None:
        payload = event.get("cwd")
        start = payload if isinstance(payload, str) and payload else os.getcwd()
    root = lab_above(start)
    if root:
        return root
    fixed = os.environ.get("CLAUDE_PROJECT_DIR")
    if fixed and os.path.isdir(os.path.join(fixed, STORE)):
        return fixed
    return None


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
    root = project_root(event)
    if not words.strip() or root is None:
        return None
    return append_words(root, words)


def selftest_lab_root():
    """The E0 cases: which lab a prompt lands in, given the session's first cwd, the payload cwd and CLAUDE_PROJECT_DIR."""
    import subprocess
    import tempfile

    def mkdir(*parts, lab=False, git=None):
        path = os.path.join(*parts)
        os.makedirs(os.path.join(path, STORE) if lab else path, exist_ok=True)
        if git == "dir":
            os.makedirs(os.path.join(path, ".git"), exist_ok=True)
        elif git == "file":  # a linked worktree has a `.git` file
            with open(os.path.join(path, ".git"), "w") as fh:
                fh.write("gitdir: /elsewhere/.git/worktrees/x\n")
        return path

    def transcript(path, cwds, lead=2, pad=0):
        """A session file: `lead` queue records without cwd, `pad` records without cwd, then one record per cwd."""
        with open(path, "w") as fh:
            for _ in range(lead + pad):
                fh.write(json.dumps({"type": "queue-operation", "operation": "enqueue"}) + "\n")
            for cwd in cwds:
                fh.write(json.dumps({"type": "user", "cwd": cwd, "message": "m"}) + "\n")
        return path

    def fire(tmp, marker, cwd, tpath=None, project_dir=None):
        """Send one prompt; return the sorted names of the lab folders (under tmp) that now hold the marker."""
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        if project_dir is not None:
            env["CLAUDE_PROJECT_DIR"] = project_dir
        event = {"prompt": marker, "cwd": cwd, "hook_event_name": "UserPromptSubmit"}
        if tpath is not None:
            event["transcript_path"] = tpath
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(event),
                              capture_output=True, text=True, env=env, cwd=tmp)
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)
        hit = []
        for dirpath, dirs, files in os.walk(tmp):
            if FILE_NAME in files and os.path.basename(dirpath) == STORE:
                if marker in open(os.path.join(dirpath, FILE_NAME), encoding="utf-8").read():
                    hit.append(os.path.relpath(os.path.dirname(dirpath), tmp))
        return sorted(hit)

    with tempfile.TemporaryDirectory() as tmp:
        main = mkdir(tmp, "main", lab=True, git="dir")
        wt = mkdir(tmp, "wt", lab=True, git="file")
        wtsub = mkdir(wt, "sub", "deep")
        other = mkdir(tmp, "other", lab=True, git="dir")
        wtb = mkdir(tmp, "wtb", lab=True, git="file")
        bare_wt = mkdir(tmp, "bare_wt", git="file")  # a worktree that has no lab (wave 1)
        plain = mkdir(tmp, "plain", git="dir")
        n = [0]

        def land(**kw):
            n[0] += 1
            return fire(tmp, "words number %d" % n[0], **kw)

        T = lambda name, cwds, **k: transcript(os.path.join(tmp, name + ".jsonl"), cwds, **k)
        # E0-1 Desktop worktree pair: CLAUDE_PROJECT_DIR = main checkout, session started in the worktree, both with a lab.
        assert land(cwd=wt, tpath=T("a", [wt, wt]), project_dir=main) == ["wt"]
        # the same on the first prompt, before any transcript record exists: no file, and an empty file
        assert land(cwd=wt, project_dir=main) == ["wt"]
        assert land(cwd=wt, tpath=os.path.join(tmp, "missing.jsonl"), project_dir=main) == ["wt"]
        assert land(cwd=wt, tpath=T("empty", []), project_dir=main) == ["wt"]
        # E0-2 the Bash tool `cd`'d into another checkout (the payload cwd follows it): the session's lab still wins
        for moved in (main, other, wtb, plain, tmp):
            assert land(cwd=moved, tpath=T("b", [wt, moved, moved]), project_dir=main) == ["wt"], moved
        # the same when the session started in main: a later cd into the worktree does not move the words
        assert land(cwd=wt, tpath=T("c", [main, wt]), project_dir=main) == ["main"]
        # a subfolder of the worktree (start, or shell) resolves to the worktree
        assert land(cwd=wtsub, tpath=T("d", [wtsub]), project_dir=main) == ["wt"]
        assert land(cwd=wtsub, project_dir=main) == ["wt"]
        # E0-3 headless start in a lab, CLAUDE_PROJECT_DIR the same lab or not set at all
        assert land(cwd=main, tpath=T("e", [main]), project_dir=main) == ["main"]
        assert land(cwd=main, tpath=T("e", [main])) == ["main"]
        assert land(cwd=main) == ["main"]
        # the session started in a worktree that has no lab: the lookup stops at its `.git`, CLAUDE_PROJECT_DIR's lab takes it (w01-c10 case A)
        assert land(cwd=bare_wt, tpath=T("f", [bare_wt]), project_dir=main) == ["main"]
        assert land(cwd=bare_wt, project_dir=main) == ["main"]
        assert land(cwd=bare_wt, tpath=T("f", [bare_wt])) == []  # nothing set, nothing found
        # the first cwd is the first record that carries one, not the first record
        assert land(cwd=wt, tpath=T("g", [wt, other], lead=5), project_dir=main) == ["wt"]
        # a head with no cwd within the limit counts as no transcript yet: the payload cwd decides
        assert land(cwd=other, tpath=T("h", [wt], pad=HEAD_LINES), project_dir=main) == ["other"]
        # a damaged head: an unparsable record and a relative cwd are skipped, a later good record is used
        with open(os.path.join(tmp, "i.jsonl"), "w") as fh:
            fh.write('{"type":"user","cwd": truncated\n{"type":"user","cwd":"relative/dir"}\n{"cwd":7}\n')
            fh.write(json.dumps({"type": "user", "cwd": wt}) + "\n")
        assert land(cwd=main, tpath=os.path.join(tmp, "i.jsonl"), project_dir=main) == ["wt"]
        # E0-4 no lab anywhere: nothing is written, and no `__statera__` appears
        before = sorted(os.listdir(plain))
        assert land(cwd=plain, tpath=T("j", [plain]), project_dir=plain) == []
        assert land(cwd=plain, project_dir=os.path.join(tmp, "nowhere")) == []
        assert land(cwd=plain) == [] and sorted(os.listdir(plain)) == before
        assert not os.path.exists(os.path.join(plain, STORE))
        # a repository nested in a folder that has a lab: the walk stops at the inner `.git`
        outer = mkdir(tmp, "outer", lab=True)
        inner = mkdir(outer, "inner", "src", git=None)
        os.makedirs(os.path.join(outer, "inner", ".git"))
        assert land(cwd=inner, tpath=T("k", [inner])) == []
        # a plain folder inside a lab without `.git` in between: the lab above is found
        assert land(cwd=mkdir(outer, "plainsub", "x"), tpath=T("l", [os.path.join(outer, "plainsub", "x")])) == ["outer"]
        # a payload without a usable cwd falls to the process directory (the hook's own), then CLAUDE_PROJECT_DIR
        assert fire(tmp, "no cwd here", cwd=None, project_dir=wt) == ["wt"]
        assert fire(tmp, "garbage cwd", cwd=12, project_dir=wt) == ["wt"]
    # resume_brief and the writer must agree on the root: same function, tested in resume_brief --selftest


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
    selftest_lab_root()
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
