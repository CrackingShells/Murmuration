# For each whole read (Read without offset/limit, or Bash cat) in waves 4-7 workers, tests whether the file's basename occurs in the worker's own brief (first user message) and whether the brief or the SubagentStart hook context mentions colgrep/search; inputs: w08b_calls.py OUT.tsv + OUT.private.jsonl + the subagent transcripts; output: OUT_brief.tsv (flags only, no raw text) and a printed summary. Usage: python3 -I w08b_brief_named.py OUT_PREFIX
import csv, json, glob, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08b_calls as C
pre = sys.argv[1]
R = list(csv.DictReader(open(pre + ".tsv"), delimiter="\t"))
P = [json.loads(l) for l in open(pre + ".private.jsonl")]
cmd = {(p["w"], p["a"], p["seq"]): p["cmd"] for p in P if "cmd" in p}
brief = {}
for w, s in C.SESS.items():
    for f in sorted(glob.glob(os.path.join(C.H, s, "subagents", "agent-*.jsonl"))):
        name = os.path.basename(f)[6:14] + ":" + re.sub(r"[\t\n]", " ", json.load(open(f.replace(".jsonl", ".meta.json"))).get("description", ""))[:34]
        txt, ctx = "", ""
        for l in open(f):
            if l.startswith(C.SKIP): continue
            r = json.loads(l)
            if r.get("type") == "user" and not txt:
                c = r["message"]["content"]; txt = c if isinstance(c, str) else json.dumps(c)
            if r.get("type") == "attachment": ctx += json.dumps(r.get("attachment"))[:20000]
            if r.get("type") == "assistant": break
        brief[(w, name)] = (txt, ctx)
rows = []
for r in R:
    if r["class"] not in ("Read_whole", "bash_cat") or not r["target"]: continue
    k = (r["wave"], r["agent"]); b, ctx = brief[k]
    base = os.path.basename(r["target"])
    rows.append([r["wave"], r["agent"], r["class"], base, r["result_chars"], int(base in b)])
with open(pre + "_brief.tsv", "w") as f:
    f.write("wave\tagent\tclass\tbasename\tresult_chars\tnamed_in_brief\n")
    for x in rows: f.write("\t".join(map(str, x)) + "\n")
n = len(rows); named = sum(x[5] for x in rows)
print("whole reads", n, "named in brief", named)
ch = sum(int(x[4] or 0) for x in rows); chn = sum(int(x[4] or 0) for x in rows if x[5])
print("chars", ch, "of which named", chn)
mb = sum("colgrep" in v[0].lower() for v in brief.values()); mc = sum("colgrep" in v[1].lower() for v in brief.values())
print("workers", len(brief), "brief mentions colgrep", mb, "start-hook context mentions colgrep", mc)
for w in ("w4", "w5", "w6", "w7"):
    ks = [k for k in brief if k[0] == w]
    print(w, len(ks), "brief colgrep", sum("colgrep" in brief[k][0].lower() for k in ks), "ctx colgrep", sum("colgrep" in brief[k][1].lower() for k in ks), "brief len median", sorted(len(brief[k][0]) for k in ks)[len(ks)//2], "ctx len median", sorted(len(brief[k][1]) for k in ks)[len(ks)//2])
