import re, collections
exec(open("derive.py").read().split("print(\"typed distinct keys")[0])
c = collections.Counter(); bad = []
for k, t in typed.items():
    a, b = stored(SHIPPED, t), stored(PATCHED, t)
    if a == b: continue
    # reconstruct: remove from a the blocks we claim to remove; what remains must equal b
    rest = a
    n = 0
    while True:
        m = re.match(r"\s*(<system-reminder>\n.*?\n</system-reminder>|<artifact-view-context\b[^>]*>.*?</artifact-view-context>|<side-sessions-event>.*?</side-sessions-event>)\s*", rest, re.S)
        if not m: break
        c[m.group(1).split(">")[0].split(" ")[0]] += 1; rest = rest[m.end():]
    paste = re.sub(r'<pasted_content id="([^"]*)">\n?(.*?)\n?</pasted_content id="\1">', lambda m: (c.update(["pasted_wrapper"]) or m.group(2)), rest, flags=re.S).lstrip("\n")
    if paste.strip("\n") != b.strip("\n"): bad.append(k)
print("tag types removed (count of removals):", dict(c)); print("changed entries not explained by removal alone:", len(bad))
