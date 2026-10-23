# Lists the whole reads (Read without offset/limit, or cat) of lab documents and scripts in waves 4-7 worker transcripts that were not named in the worker's brief, with the next three tool calls (class and file basename) and the first 200 chars of the worker's next text block, so a test question can be written by hand; inputs: w08b_calls.py OUT.tsv + OUT_brief.tsv + transcripts; output: OUT_candidates.private.tsv (contains transcript text: scratchpad only, never committed). Usage: python3 -I w08b_candidates.py OUT_PREFIX
import csv, json, glob, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08b_calls as C
pre = sys.argv[1]
R = list(csv.DictReader(open(pre + ".tsv"), delimiter="\t"))
rows = [r for r in R if r["class"] in ("Read_whole", "bash_cat") and r["target"]]
B = list(csv.DictReader(open(pre + "_brief.tsv"), delimiter="\t"))
byk = collections.defaultdict(list)
for r in R:
    byk[(r["wave"], r["agent"])].append(r)
for v in byk.values():
    v.sort(key=lambda r: int(r["seq"]))
# text after each tool result: map (wave, agent, seq) -> next assistant text
nexttext = {}
for w, s in C.SESS.items():
    for f in sorted(glob.glob(os.path.join(C.H, s, "subagents", "agent-*.jsonl"))):
        name = os.path.basename(f)[6:14] + ":" + re.sub(r"[\t\n]", " ", json.load(open(f.replace(".jsonl", ".meta.json"))).get("description", ""))[:34]
        seq = 0
        last = None
        for l in open(f):
            if l.startswith(C.SKIP):
                continue
            r = json.loads(l)
            c = (r.get("message") or {}).get("content")
            if r.get("type") == "assistant" and isinstance(c, list):
                txt = " ".join(b.get("text", "") for b in c if b.get("type") == "text").strip()
                if last is not None and txt and last not in nexttext:
                    nexttext[last] = txt[:200].replace("\n", " ").replace("\t", " ")
                for b in c:
                    if b.get("type") == "tool_use":
                        seq += 1
                        last = (w, name, seq)
with open(pre + "_candidates.private.tsv", "w") as f:
    f.write("wave\tagent\tseq\tfile\tchars\tnamed\tnext3\ttext_after\n")
    for r, b in zip(rows, B):
        k = (r["wave"], r["agent"])
        s0 = int(r["seq"])
        nx = [c for c in byk[k] if int(c["seq"]) > s0][:3]
        nx3 = " ; ".join(c["class"] + ":" + os.path.basename(c["target"]) for c in nx)
        f.write("\t".join([r["wave"], r["agent"], r["seq"], r["target"].split("Murmuration/")[-1][-70:], r["result_chars"], b["named_in_brief"], nx3, nexttext.get((r["wave"], r["agent"], s0), "")]) + "\n")
