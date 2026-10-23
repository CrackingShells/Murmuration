# c1: the worker's recorded requests cost USD 0.7915 in total, USD 0.0198 per request.

label: MEASURED
scope: one worker, 40 requests (distinct msg_id) in `data.csv`; list prices below; output tokens included.
evidence: evidence.py (run in this folder), data.csv
method: `python3 evidence.py` prints requests 40, total_usd 0.7915, mean_usd_per_request 0.0198.

Prices, USD per million tokens (Sonnet 5.5 list price): input 2.00, cache read 0.10, cache write 5-minute 2.50, cache write 1-hour 4.00, output 10.00.
Columns of data.csv: msg_id, input (uncached input tokens), cache_read, cache_w5 (cache write tokens at the 5-minute rate), cache_w1 (at the 1-hour rate), output. A streamed message can appear in several rows with the same msg_id and the same input and cache columns; the output column of the earlier rows is a partial count and the message's output is the largest value. A request is a distinct msg_id.
