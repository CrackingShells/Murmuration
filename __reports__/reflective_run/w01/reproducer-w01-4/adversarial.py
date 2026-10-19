import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myreplay as m
REM = "<system-reminder>\nLinked sessions now (status): a (idle).\n</system-reminder>\n\n"
cases = {
 'typed literal reminder (user quotes one, starts prompt)': "<system-reminder>\nremember to use tabs\n</system-reminder>\nplease explain this tag",
 'user typed ONLY a literal reminder': "<system-reminder>\nremember to use tabs\n</system-reminder>",
 'reminder not at start': "Why does this show up?\n<system-reminder>\nx\n</system-reminder>\nthanks",
 'one-line reminder at start': "<system-reminder>x</system-reminder> what is this?",
 'one-line reminder CRLF form': "<system-reminder>\r\nx\r\n</system-reminder>\r\nreal words",
 'paste wrapper nested tags': '<pasted_content id="ab12">\n<pasted_content id="cd34">\ninner\n</pasted_content id="cd34">\nouter\n</pasted_content id="ab12">',
 'paste wrapper w/ literal system-reminder inside': 'see:\n<pasted_content id="a1">\n<system-reminder>\nfoo\n</system-reminder>\nbody\n</pasted_content id="a1">',
 'paste wrapper, content = lab cmd': '<pasted_content id="a1">\n/lab why?\n</pasted_content id="a1">',
 'reminder + /lab hidden': REM + "/lab why does it fail?",
 'reminder + /lab-status': REM + "\n/lab-status",
 'reminder + bare /clear': REM + "/clear",
 'reminder + /compact keep proofs': REM + "/compact keep the proofs",
 'reminder only': REM,
 'reminder + whitespace only': REM + "   \n\n",
 'two reminders then words': REM + REM + "words",
 'reminder, then quote reply': REM + "> quoted\n\nreply",
 'unterminated reminder': "<system-reminder>\nnever closed\nreal words that must not vanish",
 'reminder, words, then 2nd reminder (non-greedy check)': REM + "words " + REM.strip(),
 'two reminder blocks separated by text; first block only cut': "<system-reminder>\na\n</system-reminder>\ntext\n<system-reminder>\nb\n</system-reminder>\nmore",
 'artifact-view-context unterminated': '<artifact-view-context artifact="x">\nno close\nwords',
 'leading text then paste wrapper (suffix only)': 'before <pasted_content id="1">\nX\n</pasted_content id="1"> after',
 'mismatched paste ids': '<pasted_content id="1">\nX\n</pasted_content id="2">',
 'side-sessions-event then words': "<side-sessions-event>foo</side-sessions-event>\nactual",
 'empty string': "",
 'cross-session after reminder': REM + '<cross-session-message from="x">hi</cross-session-message>',
 'task-notification after reminder': REM + '<task-notification>done</task-notification>',
}
print('%-62s | %-30s | %s' % ('case', 'shipped stores', 'patched stores'))
for name, p in cases.items():
    a = m.run(m.old, 'o', p); b = m.run(m.new, 'n', p)
    f = lambda x: 'NOTHING' if x is None else repr(x.rstrip('\n')[:50])
    print('%-62s | %-30s | %s' % (name, f(a), f(b)))
