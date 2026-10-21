#!/usr/bin/env python3
# Computes, from w06c_pi_wakeups.py's <label>_turns.tsv and <label>_workers.tsv, every PI idle window (end of one turn to start of the next) with its length, the subagents whose transcript span overlaps it, and the next turn's trigger and outcome; prints totals of idle seconds with at least one subagent running; writes <dir>/<label>_idle_windows.tsv. Usage: w06c_idle_windows.py DIR LABEL LAST_TURN_INDEX
import csv, sys, os, datetime
d, label, last = sys.argv[1], sys.argv[2], int(sys.argv[3])
def T(s): return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()
turns = list(csv.DictReader(open(os.path.join(d, label + "_turns.tsv")), delimiter="\t"))[: last + 1]
ws = [(r["name"], T(r["t0_utc"]), T(r["t1_utc"])) for r in csv.DictReader(open(os.path.join(d, label + "_workers.tsv")), delimiter="\t")]
tot = busy = 0.0
with open(os.path.join(d, label + "_idle_windows.tsv"), "w") as f:
    f.write("after_turn\tidle_start_utc\tidle_s\tn_workers_overlapping\tidle_s_with_any_worker\tnext_trigger\tnext_cls\tnext_turn_s\n")
    for k in range(len(turns) - 1):
        a = T(turns[k]["t_start_utc"]) + float(turns[k]["turn_s"]); b = T(turns[k + 1]["t_start_utc"])
        if b <= a: continue
        ov = [(max(a, s), min(b, e)) for n, s, e in ws if s < b and e > a]
        ov = sorted(x for x in ov if x[1] > x[0])
        u, cur = 0.0, a
        for s, e in ov:
            s = max(s, cur)
            if e > s: u += e - s; cur = e
        tot += b - a; busy += u
        f.write("\t".join(map(str, [k, datetime.datetime.fromtimestamp(a, datetime.timezone.utc).strftime("%H:%M:%S"), "%.0f" % (b - a), len(ov), "%.0f" % u, turns[k + 1]["senders"] or turns[k + 1]["trigger"], turns[k + 1]["cls"], turns[k + 1]["turn_s"]])) + "\n")
print(label, "idle windows %.0f s, with at least one subagent transcript span overlapping %.0f s (%.1f%%)" % (tot, busy, 100 * busy / tot))
