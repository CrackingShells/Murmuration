# c1: the worker's recorded requests cost USD 0.3051 in total, USD 0.0169 per request.

label: MEASURED
scope: one worker, 18 requests (distinct msg_id) in `data.csv`; list prices below; output tokens included.
evidence: evidence.py (run in this folder), data.csv
method: `python3 evidence.py` prints requests 18, total_usd 0.3051, mean_usd_per_request 0.0169.

Prices, USD per million tokens (Sonnet 5.5 list price): input 2.00, cache read 0.10, cache write 5-minute 2.50, cache write 1-hour 4.00, output 10.00.
Columns of data.csv: msg_id, input (uncached input tokens), cache_read, cache_w5 (cache write tokens at the 5-minute rate), cache_w1 (at the 1-hour rate), output. A streamed message can appear in several rows with the same msg_id and the same usage; a request is a distinct msg_id.
