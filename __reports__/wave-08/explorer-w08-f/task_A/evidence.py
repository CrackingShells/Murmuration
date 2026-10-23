# Computes the USD cost of one worker from data.csv (one row per streamed record; a request is a distinct msg_id) at list prices.
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
