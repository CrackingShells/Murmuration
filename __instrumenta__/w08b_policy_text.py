# Counts, per wave and over all 68 workers of waves 4-7 plus the PI transcripts, how many transcripts contain given phrases (search-policy header, 'Denied in this session', the block message of the shell-corpus-search guard, COLGREP_BYPASS), and prints the length and the sentences-count of the policy block as delivered; inputs: transcripts; output: printed counts only. Usage: python3 -I w08b_policy_text.py
import glob, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08b_calls as C
PH = ["SEARCH POLICY", "Denied in this session", "Shell corpus search", "is disabled by the colgrep-mcp plugin", "COLGREP_BYPASS", "colgrep://guide", "a known file's contents"]
tab = collections.defaultdict(collections.Counter); n = collections.Counter(); plen = {}
for w, s in C.SESS.items():
    files = glob.glob(os.path.join(C.H, s, "subagents", "agent-*.jsonl")) + glob.glob(os.path.join(C.H, os.path.dirname(s), os.path.basename(s) + ".jsonl"))
    for f in files:
        kind = "PI" if "/subagents/" not in f else "worker"
        txt = open(f).read()
        n[(w, kind)] += 1
        for p in PH:
            if p in txt: tab[(w, kind)][p] += 1
        m = re.search(r"SEARCH POLICY.{0,3000}?(?=\\n\\n[A-Z]|\"\}|\Z)", txt)
        if m and (w, kind) not in plen: plen[(w, kind)] = len(m.group(0))
for k in sorted(n):
    print(k, "transcripts", n[k], dict(tab[k]), "policy-block chars (first match, escaped)", plen.get(k))
