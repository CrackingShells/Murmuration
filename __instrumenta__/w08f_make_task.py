# Builds the planted-error verifier task of w08-f: from a seed to <out>/task/{claim.md,data.csv,evidence.py} (what the agent sees) and <out>/truth/truth.json (the right numbers, kept outside the task folder).
# usage: w08f_make_task.py OUT_DIR   (deterministic, seed 8). Planted error: evidence.py prices the 1-hour cache writes at the 5-minute rate; duplicated msg_id rows (streamed records) are a trap for a verifier that does not count distinct requests.
import os, sys, json, random
out = sys.argv[1]
rnd = random.Random(8)
P = dict(input=2.0, read=0.10, w5=2.5, w1=4.0, output=10.0)  # USD per million tokens, Sonnet 5.5 list price (lab_status.py PRICES)
rows = []
ctx = 14000
for i in range(1, 19):
    new = rnd.randint(300, 4000)
    cr = ctx if i > 1 else 0
    w1 = new if i in (1, 2, 9, 10, 15) or rnd.random() < 0.3 else 0
    w5 = new - w1
    inp = rnd.randint(1, 6)
    o = rnd.randint(150, 1500)
    rows.append(dict(msg_id="msg_%02d" % i, input=inp, cache_read=cr, cache_w5=w5, cache_w1=w1, output=o))
    ctx += new + o
dup = []
for i in (3, 7, 7, 12):                       # streamed duplicates: same msg_id, same usage
    r = dict(rows[i - 1]); dup.append(r)
allrows = rows + dup
rnd.shuffle(allrows)
allrows.sort(key=lambda r: r["msg_id"])
os.makedirs(out + "/task", exist_ok=True); os.makedirs(out + "/truth", exist_ok=True)
with open(out + "/task/data.csv", "w") as f:
    f.write("msg_id,input,cache_read,cache_w5,cache_w1,output\n")
    for r in allrows:
        f.write("%s,%d,%d,%d,%d,%d\n" % (r["msg_id"], r["input"], r["cache_read"], r["cache_w5"], r["cache_w1"], r["output"]))
def cost(rs, w1price):
    return sum((r["input"] * P["input"] + r["cache_read"] * P["read"] + r["cache_w5"] * P["w5"] + r["cache_w1"] * w1price + r["output"] * P["output"]) / 1e6 for r in rs)
true_total = cost(rows, P["w1"]); bug_total = cost(rows, P["w5"]); naive_total = cost(allrows, P["w1"])
truth = dict(true_total=round(true_total, 4), claimed_total=round(bug_total, 4), no_dedup_total=round(naive_total, 4),
             n_requests=len(rows), n_rows=len(allrows), claimed_mean=round(bug_total / len(rows), 4), true_mean=round(true_total / len(rows), 4))
json.dump(truth, open(out + "/truth/truth.json", "w"), indent=1)
open(out + "/task/evidence.py", "w").write('''# Computes the USD cost of one worker from data.csv (one row per streamed record; a request is a distinct msg_id) at list prices.
import csv
PRICE = dict(input=2.0, cache_read=0.10, cache_w5=2.5, cache_w1=2.5, output=10.0)  # USD per million tokens
seen = {}
for r in csv.DictReader(open("data.csv")):
    seen[r["msg_id"]] = r
total = 0.0
for r in seen.values():
    total += sum(int(r[k]) * PRICE[k] for k in PRICE) / 1e6
print("requests", len(seen))
print("total_usd %.4f" % total)
print("mean_usd_per_request %.4f" % (total / len(seen)))
''')
open(out + "/task/claim.md", "w").write('''# c1: the worker's recorded requests cost USD %.4f in total, USD %.4f per request.

label: MEASURED
scope: one worker, 18 requests (distinct msg_id) in `data.csv`; list prices below; output tokens included.
evidence: evidence.py (run in this folder), data.csv
method: `python3 evidence.py` prints requests 18, total_usd %.4f, mean_usd_per_request %.4f.

Prices, USD per million tokens (Sonnet 5.5 list price): input 2.00, cache read 0.10, cache write 5-minute 2.50, cache write 1-hour 4.00, output 10.00.
Columns of data.csv: msg_id, input (uncached input tokens), cache_read, cache_w5 (cache write tokens at the 5-minute rate), cache_w1 (at the 1-hour rate), output. A streamed message can appear in several rows with the same msg_id and the same usage; a request is a distinct msg_id.
''' % (bug_total, bug_total / len(rows), bug_total, bug_total / len(rows)))
print(json.dumps(truth))
