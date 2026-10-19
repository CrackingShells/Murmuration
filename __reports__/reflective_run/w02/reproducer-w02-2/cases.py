import importlib.util, os, re, sys, tempfile
ROOT = "/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e"
spec = importlib.util.spec_from_file_location("uw", ROOT + "/scripts/user_words.py")
uw = importlib.util.module_from_spec(spec); spec.loader.exec_module(uw)
os.environ.pop("CLAUDE_PROJECT_DIR", None)
R = "<system-reminder>\nLinked sessions: a = local_1.\n</system-reminder>"
def P(i, b): return '<pasted_content id="%s">\n%s\n</pasted_content id="%s">' % (i, b, i)
# (name, prompt, expected stored text or None) -- expectations written by hand from the claim's rule
C = [
 ("plain", "hello world", "hello world"),
 ("typed /lab", "/lab why?", None),
 ("typed /lab-status", "/lab-status", None),
 ("typed bare /clear", "/clear", None),
 ("typed /foo bar (not lab, has args)", "/foo bar", "/foo bar"),
 ("pasted /lab", P("1", "/lab why is this"), "/lab why is this"),
 ("pasted /clear", P("1", "/clear"), "/clear"),
 ("ws-only wrapper", P("1", "   \n  "), None),
 ("empty wrapper", '<pasted_content id="1">\n\n</pasted_content id="1">', None),
 ("nested wrapper", P("1", "a " + P("2", "b") + " c"), "a " + P("2", "b") + " c"),
 ("reminder + /clear", R + "\n\n/clear", None),
 ("reminder + /lab x", R + "\n\n/lab x", None),
 ("reminder only", R + "\n", None),
 ("literal leading reminder + text", "<system-reminder>\nbe nice\n</system-reminder>\n\nmy q", "my q"),
 ("mid-text reminder", "see\n" + R + "\nafter", "see\n" + R + "\nafter"),
 ("one-line reminder", "<system-reminder>x</system-reminder> and more", "<system-reminder>x</system-reminder> and more"),
 ("CRLF reminder", "<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi", "<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi"),
 ("unclosed reminder", "<system-reminder>\nx\nhi", "<system-reminder>\nx\nhi"),
 ("reminder + cross-session", R + "\n\n<cross-session-message from=\"a\">m</cross-session-message>", None),
 ("reminder + task-notif", R + "\n<task-notification>x</task-notification>", None),
 ("reminder + agent-message", R + "\n<agent-message from=\"a\">m</agent-message>", None),
 ("cross-session plain", "<cross-session-message from=\"a\">m</cross-session-message>", None),
 ("two reminders", R + "\n" + R + "\nreal", "real"),
 ("reminder, typed, reminder", R + "\ntyped\n" + R, "typed\n" + R),
 ("reminder + paste", R + "\n\n" + P("7", "pp"), "pp"),
 ("text + paste + text", "a\n" + P("7", "pp") + "\nb", "a\npp\nb"),
 ("two pastes", P("1","x") + "\n" + P("2","y"), "x\ny"),
 ("mismatched id", '<pasted_content id="a">\nx\n</pasted_content id="b">', '<pasted_content id="a">\nx\n</pasted_content id="b">'),
 ("artifact-view + text", '<artifact-view-context artifact="x">\n{}\n</artifact-view-context>\n\nreply', "reply"),
 ("side-sessions only", "<side-sessions-event>\nx\n</side-sessions-event>\n\n", None),
 ("side-sessions + text", "<side-sessions-event>\nx\n</side-sessions-event>\n\nwords", "words"),
 ("leading ws then reminder", "  \n" + R + "\n\nhi", "hi"),
 ("non-str prompt", 5, None),
 ("missing prompt", None, None),
 ("reminder containing </system-reminder> in typed text", R + "\nsay </system-reminder> please", "say </system-reminder> please"),
 ("quote reply", "> q\n\nok", "> q\n\nok"),
 ("trailing newlines", "hello\n\n\n", "hello"),
 ("multiline reminder body w/ blank lines", "<system-reminder>\na\n\nb\n</system-reminder>\nhi", "hi"),
]
bad = 0
for name, prompt, want in C:
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(t + "/__statera__")
        ev = {"cwd": t}
        if prompt is not None: ev["prompt"] = prompt
        ret = uw.handle(ev)
        pth = t + "/__statera__/user_words.md"
        got = None
        if os.path.exists(pth):
            body = open(pth, encoding="utf-8", newline="").read()
            got = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", body, flags=re.M)[-1]
            assert got.endswith("\n"); got = got[:-1]
        ok = got == want and ((ret is None) == (want is None))
        bad += not ok
        print("OK  " if ok else "FAIL", name, "" if ok else (repr(got), repr(want)))
# project-root: not a lab -> nothing; env wins over cwd
with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
    os.makedirs(a + "/__statera__")
    assert uw.handle({"prompt": "x", "cwd": b}) is None          # b is no lab
    os.environ["CLAUDE_PROJECT_DIR"] = a
    assert uw.handle({"prompt": "x", "cwd": b}) is not None       # env wins
    assert os.path.exists(a + "/__statera__/user_words.md") and not os.path.exists(b + "/__statera__")
    del os.environ["CLAUDE_PROJECT_DIR"]
print("cases", len(C), "failures", bad)
sys.exit(bad)
