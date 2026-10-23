# Finds, in each wave-4..7 worker transcript, the assistant text and thinking blocks and the final hand-back text that mention colgrep, semantic search or the search policy, with the index of the request in which each occurs and whether that worker called colgrep; inputs: the session transcripts; output: OUT.private.tsv (contains transcript text: scratchpad only, never committed) and a printed count per wave. Usage: python3 -I w08b_colgrep_mentions.py OUT.private.tsv
import glob, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08b_calls as C
RX = re.compile(r"colgrep|semantic search|semantic mapping|search policy|SEARCH POLICY|COLGREP_BYPASS", re.I)
out = open(sys.argv[1], "w")
out.write("wave\tagent\treq\tkind\tcalled_colgrep\ttext\n")
cnt = collections.Counter()
for w, s in C.SESS.items():
    for f in sorted(glob.glob(os.path.join(C.H, s, "subagents", "agent-*.jsonl"))):
        a = os.path.basename(f)[6:14]
        lines = [l for l in open(f) if not l.startswith(C.SKIP)]
        called = any('"name": "mcp__plugin_colgrep-mcp_colgrep__' in l or '"name":"mcp__plugin_colgrep-mcp_colgrep__' in l for l in lines if '"type": "assistant"' in l or '"type":"assistant"' in l)
        req = 0
        for l in lines:
            r = json.loads(l)
            if r.get("type") != "assistant":
                continue
            req += 1
            for b in (r.get("message") or {}).get("content") or []:
                t = b.get("text") if b.get("type") == "text" else b.get("thinking") if b.get("type") == "thinking" else None
                if t and RX.search(t):
                    i = RX.search(t).start()
                    out.write("\t".join([w, a, str(req), b["type"], str(int(called)), t[max(0, i - 150):i + 250].replace("\n", " ").replace("\t", " ")]) + "\n")
                    cnt[(w, b["type"], called)] += 1
for k in sorted(cnt):
    print(k, cnt[k])
