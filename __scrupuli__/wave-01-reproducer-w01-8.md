## S-w01-reproducer-w01-8-1
A claim's Result 3 table (design 22 worker notices, 3ccc 6 with one wait of 584.5 s) is not what the author's own script and CSV produce (design 12, 3ccc 2, none over 300 s). Tables in a claim head drift from the code when the code is edited after the text; nothing in the lab ties a quoted table to the run that made it (no hash of the CSV in the claim). Does a claim need a `run_log` line or checksum per quoted table?
refs: __pondus__/w01-c8.md (Result 3); __reports__/reflective_run/w01/author-w01-5/pi_reaction_latency.csv, run_log.txt; __reports__/reflective_run/w01/reproducer-w01-8/latency.py

## S-w01-reproducer-w01-8-2
Forked sessions (design and `3ccc590f` copy the genesis history, same task ids and same millisecond stamps) make a notice appear in several files, and in the fork the copied notice is followed by records that were not written in reaction to it (a 584.5 s "wait" that is 2.8 s in the parent). Any latency or count taken from a session file in this project must say how forks are de-duplicated. The framing lists the sessions as if independent.
refs: __reports__/reflective_run/w01/reproducer-w01-8/latency.py (GLOBAL set); __design__/framing.md (Data)

## S-w01-reproducer-w01-8-3
Cache TTL from the gap data: warm at 282.0 s, cold at 284.9 s (this run, after the author's snapshot), while the 12 resumes inside the snapshot only bracket the TTL between 238.9 and 425.4 s. The cache clock should start at the last request, not at the last record, so the true TTL gap is a little longer than the measured gap and a 300 s TTL fits. Is there a transcript field with the request start time that would make this a measurement instead of a bracket?
refs: __reports__/reflective_run/w01/reproducer-w01-8/resume.py output (a701db132 282.0 warm; aa70e320b 284.9 cold; a9745700a 319.7 cold)

## S-w01-reproducer-w01-8-4
A "worker notice" is told apart from a background-shell notice only by the task id having been returned by an Agent launch; a resumed agent's second notice carries no tool-use-id at all, so a filter on tool-use-id silently halves the count (my first pass gave 6 instead of 9 in this run). Easy to get wrong in the next script; the notice format has no explicit kind field.
refs: __reports__/reflective_run/w01/reproducer-w01-8/latency.py
