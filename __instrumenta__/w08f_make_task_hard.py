# Builds the harder planted-error verifier task of w08-f (task B): from a fixed seed to <out>/task/{claim.md,data.csv,evidence.py} (what the agent sees) and <out>/truth/truth.json (right numbers, outside the task folder).
# usage: w08f_make_task_hard.py OUT_DIR   Two planted errors: evidence.py keeps the LAST row of each msg_id (streamed rows carry a growing output count, the final one is the largest and not always last in file order) and prices 1-hour cache writes at the 5-minute rate. 40 requests, 9 streamed duplicates with partial output counts.
import os, sys, json, random
out = sys.argv[1]; rnd = random.Random(88)
P = dict(input=2.0, read=0.10, w5=2.5, w1=4.0, output=10.0)
rows = []; ctx = 14000
for i in range(1, 41):
    new = rnd.randint(300, 4000); cr = ctx if i > 1 else 0
    w1 = new if (i % 7 in (1, 2) or rnd.random() < 0.2) else 0
    rows.append(dict(msg_id="msg_%02d" % i, input=rnd.randint(1, 6), cache_read=cr, cache_w5=new - w1, cache_w1=w1, output=rnd.randint(150, 1500)))
    ctx += new + rows[-1]["output"]
allrows = list(rows)
for i in (4, 9, 13, 20, 20, 27, 31, 35, 38):
    r = dict(rows[i - 1]); r["output"] = rnd.randint(3, 8); allrows.append(r)   # early streamed record, partial output count
# file order: by msg_id, but the early (partial) record of some messages comes after the final one
allrows.sort(key=lambda r: (r["msg_id"], -r["output"] if rnd.random() < 0.5 else r["output"]))
def usd(r, w1p): return (r["input"] * P["input"] + r["cache_read"] * P["read"] + r["cache_w5"] * P["w5"] + r["cache_w1"] * w1p + r["output"] * P["output"]) / 1e6
true_total = sum(usd(r, P["w1"]) for r in rows)
last = {}
for r in allrows: last[r["msg_id"]] = r
bug_total = sum(usd(r, P["w5"]) for r in last.values())
os.makedirs(out + "/task", exist_ok=True); os.makedirs(out + "/truth", exist_ok=True)
with open(out + "/task/data.csv", "w") as f:
    f.write("msg_id,input,cache_read,cache_w5,cache_w1,output\n")
    for r in allrows: f.write("%s,%d,%d,%d,%d,%d\n" % (r["msg_id"], r["input"], r["cache_read"], r["cache_w5"], r["cache_w1"], r["output"]))
n = len(rows)
json.dump(dict(true_total=round(true_total, 4), claimed_total=round(bug_total, 4), n_requests=n, n_rows=len(allrows), only_price_bug_total=round(sum(usd(r, P["w5"]) for r in rows), 4), only_last_row_total=round(sum(usd(r, P["w1"]) for r in last.values()), 4)), open(out + "/truth/truth.json", "w"), indent=1)
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
scope: one worker, 40 requests (distinct msg_id) in `data.csv`; list prices below; output tokens included.
evidence: evidence.py (run in this folder), data.csv
method: `python3 evidence.py` prints requests 40, total_usd %.4f, mean_usd_per_request %.4f.

Prices, USD per million tokens (Sonnet 5.5 list price): input 2.00, cache read 0.10, cache write 5-minute 2.50, cache write 1-hour 4.00, output 10.00.
Columns of data.csv: msg_id, input (uncached input tokens), cache_read, cache_w5 (cache write tokens at the 5-minute rate), cache_w1 (at the 1-hour rate), output. A streamed message can appear in several rows with the same msg_id and the same input and cache columns; the output column of the earlier rows is a partial count and the message's output is the largest value. A request is a distinct msg_id.
''' % (bug_total, bug_total / n, bug_total, bug_total / n))
print(open(out + "/truth/truth.json").read())
