"""Compares the tool lists of the first api-request-shape record of two session transcripts in ~/.claude/projects (argv: two paths) with the `disallowedTools:` line of agents/research-pi.md: prints counts, bytes, tools removed/added and whether every removed tool matches the denylist, to stdout."""
import json, sys, re, fnmatch, os
lab = os.path.abspath(os.path.dirname(__file__) + "/..")
deny = [x.strip() for x in re.search(r"^disallowedTools: (.*)$", open(lab + "/agents/research-pi.md").read(), re.M).group(1).split(",")]
def tools(p):
    for l in open(os.path.expanduser(p), errors="replace"):
        if '"api-request-shape"' in l:
            t = json.loads(l)["shape"]["tools"]; return {x["name"]: len(json.dumps(x)) for x in t}
b, a = tools(sys.argv[1]), tools(sys.argv[2])
rem = sorted(set(b) - set(a)); add = sorted(set(a) - set(b))
print("before", len(b), "tools", sum(b.values()), "bytes; after", len(a), "tools", sum(a.values()), "bytes")
print("removed", len(rem), "bytes", sum(b[n] for n in rem), "added", len(add))
print("removed tools not matched by the denylist:", [n for n in rem if not any(fnmatch.fnmatch(n, d) for d in deny)])
print("after-session tools that the denylist matches:", [n for n in a if any(fnmatch.fnmatch(n, d) for d in deny)])
