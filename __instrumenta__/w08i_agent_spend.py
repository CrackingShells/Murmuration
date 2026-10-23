# Lists list-price USD, requests and output tokens per named agent (author, explorer, reproducer, proof-adversary, PI) over every session scripts/lab_status.py finds for this lab; input: the Claude Code transcripts under ~/.claude/projects (via lab_status's own finder, parser and prices); output: a TSV on stdout (label, role, wave, msgs, usd, lower_bound).
# usage: python3 -I __instrumenta__/w08i_agent_spend.py > __reports__/wave-08/explorer-w08-i/agent_spend.tsv
import sys, os, re, collections
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L
trees = L.git_worktrees(root)
roots = L.lab_roots(root, trees)
ws = []
sessions, _ = L.load_sessions(L.find_sessions(roots), ws)
agg = collections.OrderedDict()
for s in sessions:
    for (label, model), r in s["rows"].items():
        a = agg.setdefault(label, collections.Counter())
        a.update({"msgs": r["msgs"], "usd": r["usd"], "lower": r["lower"], "output": r["output"]})
print("label\trole\twave\tmsgs\tusd\tlower_bound\toutput_tokens")
for label, a in agg.items():
    m = re.search(r"(author|explorer|reproducer|proof-adversary)(?:-w(\d\d))?", label)
    role = "PI" if "main thread" in label else (m.group(1) if m else "other")
    wave = ("w" + m.group(2)) if m and m.group(2) else ""
    print(f"{label}\t{role}\t{wave}\t{a['msgs']}\t{a['usd']:.4f}\t{'+' if a['lower'] else ''}\t{a['output']}")
