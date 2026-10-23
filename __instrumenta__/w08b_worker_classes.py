# Classifies each of the 68 workers of waves 4-7 as never-colgrep / colgrep-then-whole-read-of-a-hit-file / colgrep-and-used-hit, and counts per-class tool calls and results chars, from w08b_calls.py output (OUT.tsv and OUT.private.jsonl); output: OUT_classes.tsv (no raw text) and a printed summary. Usage: python3 -I w08b_worker_classes.py OUT_PREFIX
import csv, json, sys, os, re, collections
pre = sys.argv[1]
R = list(csv.DictReader(open(pre + ".tsv"), delimiter="\t"))
P = [json.loads(l) for l in open(pre + ".private.jsonl")]
cmd = {(p["w"], p["a"], p["seq"]): p["cmd"] for p in P if "cmd" in p}
cg = {(p["w"], p["a"], p["seq"]): p for p in P if "colgrep" in p}
W = collections.defaultdict(list)
for r in R: W[(r["wave"], r["agent"])].append(r)
out = []
tot = collections.Counter()
for k, calls in sorted(W.items()):
    calls.sort(key=lambda r: int(r["seq"]))
    cgs = [c for c in calls if "colgrep" in c["tool"]]
    whole_after = used_after = part_after = 0
    for c in cgs:
        p = cg[(k[0], k[1], int(c["seq"]))]
        hits = {os.path.basename(h) for h in p.get("hit_files", [])}
        for c2 in calls:
            if int(c2["seq"]) <= int(c["seq"]): continue
            if c2["class"] in ("Read_whole", "Read_part", "Write", "Edit"):
                paths = [c2["target"]]
            elif c2["class"].startswith("bash_"):
                paths = re.findall(r"[\w@.+/-]+\.(?:md|py|sh|json|tsv|txt|c|rs)", cmd.get((k[0], k[1], int(c2["seq"])), ""))
            else: continue
            m = [x for x in paths if os.path.basename(x) in hits]
            if m:
                whole = c2["class"] in ("Read_whole", "bash_cat")
                part = c2["class"] in ("Read_part", "bash_sed", "bash_head", "bash_tail", "bash_grep")
                if whole: whole_after += 1
                elif part: part_after += 1
                else: used_after += 1  # ran, wrote or edited the hit file
    cls = "never" if not cgs else ("colgrep_then_whole_read_of_hit" if whole_after else ("colgrep_then_partial_read_of_hit" if part_after else ("colgrep_then_ran_or_wrote_hit" if used_after else "colgrep_no_later_touch_of_hit")))
    tools = collections.Counter(c["class"] for c in calls)
    out.append([k[0], k[1], cls, len(calls), len(cgs), tools["Read_whole"], tools["bash_cat"], tools["bash_sed"], tools["bash_grep"], whole_after, part_after, used_after])
    tot[cls] += 1
with open(pre + "_classes.tsv", "w") as f:
    f.write("wave\tagent\tclass\tcalls\tcolgrep\tRead_whole\tcat\tsed\tgrep\twhole_after_hit\tpartial_after_hit\tran_or_wrote_hit\n")
    for o in out: f.write("\t".join(map(str, o)) + "\n")
print(tot)
for w in ("w4", "w5", "w6", "w7"):
    print(w, collections.Counter(o[2] for o in out if o[0] == w))
print("colgrep users by type of reading:", [o for o in out if o[4]][:0])
