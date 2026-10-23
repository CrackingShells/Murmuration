# Builds __reports__/wave-08/explorer-w08-h/lab_cost_map.html from the wave-7 cost map (__reports__/wave-07/research-pi/lab_cost_map.html) by string patches and inserted wave-8 sections; inputs: the wave-7 HTML and the fragment files in __instrumenta__/w08h_frag/; output: the wave-8 HTML (self-contained, no network).
# usage: python3 -I __instrumenta__/w08h_build_cost_map.py
import os, re, sys
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
src = open(os.path.join(root, "__reports__/wave-07/research-pi/lab_cost_map.html"), encoding="utf-8").read()
F = lambda n: open(os.path.join(root, "__instrumenta__/w08h_frag", n), encoding="utf-8").read()
def rep(s, old, new, count=1):
    if s.count(old) < 1:
        sys.exit("patch target missing: " + old[:80])
    return s.replace(old, new, count)
def cut(s, a, b, new):
    i = s.index(a); j = s.index(b, i)
    return s[:i] + new + s[j:]
s = src
# head, title, tiles
s = rep(s, "<title>Murmuration after wave 7 (local main)</title>", "<title>Murmuration after wave 8 so far (local main)</title>")
s = rep(s, "<h1>Murmuration after wave 7 (local main)</h1>", "<h1>Murmuration after wave 8 (so far)</h1>")
s = cut(s, '<p class="sub">', '<!-- 1. STRUCTURE -->', F("top.html"))
# css additions
s = rep(s, "@media (prefers-reduced-motion: reduce)", F("css.css") + "\n@media (prefers-reduced-motion: reduce)")
# section 1 node texts
for a, b in [x.split("\n=====\n") for x in F("patches_s1.txt").split("\n#####\n")]:
    s = rep(s, a, b)
# section 2: extra design row
s = rep(s, '<svg id="bars" viewBox="0 0 1080 280"', '<svg id="bars" viewBox="0 0 1080 340"')
s = rep(s, '''  {k:"After wave 7  ✓",''', '''  {k:"After wave 7",''')
s = rep(s, "];\nconst CLS=628;", F("design_row.js") + "];\nconst CLS=628;")
# section 3 -> B, 3b -> C
i3 = s.index('<h3 style="margin-top:22px">3b'); j3 = s.index("</div>\n\n<!-- 4. GRAVEYARD -->")
old3b = s[i3:j3]
s = cut(s, "<!-- 3. SPEND -->", "<!-- 4. GRAVEYARD -->", F("sec3.html").replace("@@OLD3B@@", old3b))
# section 4 cards
s = rep(s, '<p class="note">Each card is a claim with an independent verdict. A red badge is a move that did not land; a green one, a move on <code>main</code>; an orange one, an idea looked at and not pursued. Wave 7 first.</p>',
        '<p class="note">Each card is a claim with an independent verdict, or an idea looked at without one. A red badge is a move that did not land; a green one, a move on <code>main</code>; an orange one, an idea looked at and not pursued; a purple one waits for you. Wave 8 first, then wave 7 and earlier.</p>')
s = rep(s, "const moves=[\n", "const moves=[\n" + F("moves8.js"))
# section 5 updates
for a, b in [x.split("\n=====\n") for x in F("patches_s5.txt").split("\n#####\n")]:
    s = rep(s, a, b)
# JS: replace spend and ttl blocks by wave-8 code
s = cut(s, "/* ---------- 3. spend ---------- */", "/* ---------- 3b. 1-hour cache break-even ---------- */", F("sec3.js"))
# sources
s = rep(s, "const src=[\n", "const src=[\n" + F("sources8.js"))
s = rep(s, "<h2>Sources (table view)</h2>", "<h2>Sources (table view)</h2>\n  <p class=\"note\">Labels are the report's, and never above a claim's current label from <code>scripts/lab_status.py</code> (w08-c3, w08-c4, w08-c6 MEASURED, verified; w08-c2 unverified; w08-c8 CONJECTURE; w07-c1 and w07-c8 below MEASURED: restate; w07-c7 escalated). Rows marked <b>not in the reports</b> are numbers the page needed and could not source.</p>")
# ladder JS goes before section-1 JS
s = rep(s, "/* ---------- 1. hook chain ---------- */", F("ladder.js") + "\n/* ---------- 1. hook chain ---------- */")
# card A before section 1
s = rep(s, "<!-- 1. STRUCTURE -->", F("cardA.html") + "\n<!-- 1. STRUCTURE -->")
out = os.path.join(root, "__reports__/wave-08/explorer-w08-h/lab_cost_map.html")
open(out, "w", encoding="utf-8").write(s)
print("wrote", out, len(s))
