#!/usr/bin/env python3
# Computes, from the tables of w06c_pi_wakeups.py (<dir>/w4_*.tsv, w5_*.tsv) and explorer-w05-b's waves123_requests.tsv, the PI share of wave spend, the PI time split, cost per wake-up against context, outcome classes of wake-ups, the 5-minute-cache counterfactual, and the fresh-session-per-wave estimate; prints tables and writes <dir>/summary_tables.txt. Usage: w06c_pi_summary.py DIR W123_REQUESTS_TSV
import csv, sys, os, datetime, collections

DIR = sys.argv[1]
W123 = sys.argv[2]
R_IN, R_OUT, R_CR, R_W5, R_W1 = 4.0, 20.0, 0.20, 5.0, 8.0  # Opus 5.5 USD/Mtok [source: scripts/lab_status.py PRICES]
BASE = 75000  # request-0 context of the PI [source: w4_req.tsv, w5_req.tsv row 0: 74632, 74966]
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


def tsv(name):
    return list(csv.DictReader(open(os.path.join(DIR, name)), delimiter="\t"))


def T(s):
    return datetime.datetime.fromisoformat(s).replace(tzinfo=datetime.timezone.utc).timestamp()


def spend_table():
    p("## spend: PI main thread vs the session's subagents (list price)")
    for label, req, wk, wave_end in (("wave 4", "w4_req.tsv", "w4_workers.tsv", None), ("wave 5", "w5_req.tsv", "w5_workers.tsv", "2026-10-21T07:19:00")):
        rq = tsv(req)
        wks = tsv(wk)
        pi_all = sum(float(r["usd_list"]) for r in rq)
        if wave_end:
            pi_w = sum(float(r["usd_list"]) for r in rq if r["t_utc"] <= wave_end)
        else:
            pi_w = pi_all
        w_usd = sum(float(r["usd_list"]) for r in wks)
        p("%s: PI in wave %.2f (whole session %.2f) | subagents %.2f over %d runs | PI share of PI+subagents %.1f%%" % (label, pi_w, pi_all, w_usd, len(wks), 100 * pi_w / (pi_w + w_usd)))
        yield label, pi_w, w_usd


def time_split(label, turns, last_idx):
    ts = turns[: last_idx + 1]
    t_first = T(ts[0]["t_start_utc"])
    t_last = T(ts[-1]["t_start_utc"]) + float(ts[-1]["turn_s"])
    wall = t_last - t_first
    busy = sum(float(t["turn_s"]) for t in ts)
    p("%s time: wall %.0f s (%.1f min), PI turns %.0f s (%.1f%%), idle between turns %.0f s (%.1f%%), turns %d" % (label, wall, wall / 60, busy, 100 * busy / wall, wall - busy, 100 * (wall - busy) / wall, len(ts)))
    # idle without the first (human-prompted) preface: idle after the first turn ends
    first_end = T(ts[0]["t_start_utc"]) + float(ts[0]["turn_s"])
    wall2 = t_last - first_end
    busy2 = sum(float(t["turn_s"]) for t in ts[1:])
    p("   from end of preface turn 0: wall %.0f s, PI turns %.0f s (%.1f%%), idle %.0f s (%.1f%%)" % (wall2, busy2, 100 * busy2 / wall2, wall2 - busy2, 100 * (wall2 - busy2) / wall2))


def classes(label, turns, last_idx):
    ts = turns[: last_idx + 1]
    tot = sum(float(t["usd_list"]) for t in ts)
    c = collections.OrderedDict()
    for t in ts:
        k = (t["trigger"].split("+")[0] if t["trigger"] else "?") + " -> " + t["cls"]
        n, u, r = c.get(k, (0, 0.0, 0))
        c[k] = (n + 1, u + float(t["usd_list"]), r + int(t["n_req"]))
    p("%s wake-ups by trigger -> outcome (turns, requests, USD, share of PI USD in this window %.2f):" % (label, tot))
    for k, (n, u, r) in sorted(c.items(), key=lambda kv: -kv[1][1]):
        p("   %-34s turns %2d  req %3d  USD %.2f  %.1f%%" % (k, n, r, u, 100 * u / tot))
    nothing = [t for t in ts[1:] if t["cls"] in ("text-only", "read-only")]
    p("   after the first turn: %d wake-ups; changed no state (text-only or read-only): %d turns, %d requests, USD %.2f = %.1f%% of the PI window; text-only alone: %d turns USD %.2f" % (
        len(ts) - 1, len(nothing), sum(int(t["n_req"]) for t in nothing), sum(float(t["usd_list"]) for t in nothing), 100 * sum(float(t["usd_list"]) for t in nothing) / tot,
        sum(1 for t in ts[1:] if t["cls"] == "text-only"), sum(float(t["usd_list"]) for t in ts[1:] if t["cls"] == "text-only")))
    reactive = [t for t in ts[1:] if t["trigger"] != "human"]
    p("   reactive (woken by a worker, not a human prompt): %d turns, USD %.2f = %.1f%%; of those that did something: %d" % (
        len(reactive), sum(float(t["usd_list"]) for t in reactive), 100 * sum(float(t["usd_list"]) for t in reactive) / tot, sum(1 for t in reactive if t["cls"] not in ("text-only", "read-only"))))


def lin(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def cost_vs_ctx(label, turns, req, last_idx):
    one = [t for t in turns[1 : last_idx + 1] if t["n_req"] == "1"]
    xs = [int(t["ctx_start"]) / 1e3 for t in one]
    ys = [float(t["usd_list"]) for t in one]
    a, b = lin(xs, ys)
    p("%s one-request wake-ups (text-only acks): n=%d, ctx %.0fk..%.0fk, USD %.3f..%.3f; fit usd = %.4f + %.6f * ctx_k  (pure cache read would be 0.0002 per k)" % (label, len(one), min(xs), max(xs), min(ys), max(ys), a, b))
    rq = [r for r in req if r["t_utc"] <= ("2026-10-21T07:19:00" if label.startswith("wave 5") else "9")]
    xs = [int(r["ctx"]) / 1e3 for r in rq[1:]]
    ys = [float(r["usd_list"]) for r in rq[1:]]
    a, b = lin(xs, ys)
    p("   all %d later requests: usd = %.4f + %.6f * ctx_k; at 100k %.3f, 200k %.3f, 300k %.3f, 390k %.3f" % (len(xs), a, b, a + b * 100, a + b * 200, a + b * 300, a + b * 390))
    # share of the PI window that is cache read of context
    cr = sum(int(r["cache_read"]) for r in rq) * R_CR / 1e6
    tot = sum(float(r["usd_list"]) for r in rq)
    p("   cache read %.2f of %.2f USD = %.1f%%; the first-request base context (75k) re-read by %d requests = %.2f USD = %.1f%%" % (cr, tot, 100 * cr / tot, len(rq) - 1, BASE * (len(rq) - 1) * R_CR / 1e6, 100 * BASE * (len(rq) - 1) * R_CR / 1e6 / tot))


def buckets(t4, t5):
    p("per wake-up cost by starting context (waves 4 and 5 pooled, turns after the first, wave-6 opening turn excluded)")
    ts = [(int(t["ctx_start"]), float(t["usd_list"]), int(t["n_req"]), t["cls"]) for t in t4[1:] + t5[1:-1]]
    for lo, hi in ((0, 250000), (250000, 300000), (300000, 350000), (350000, 10**9)):
        b = [x for x in ts if lo <= x[0] < hi]
        if b:
            p("   ctx %3dk-%4dk: %2d wake-ups, mean USD %.3f per wake-up, %.3f per request, %.1f requests per wake-up; text-only wake-ups %d" % (lo // 1000, min(hi, 999999) // 1000, len(b), sum(x[1] for x in b) / len(b), sum(x[1] for x in b) / sum(x[2] for x in b), sum(x[2] for x in b) / len(b), sum(1 for x in b if x[3] == "text-only")))


def cache5(label, req, gaps):
    # counterfactual: every cache write at the 5-minute rate, every gap over 300 s rewrites the whole previous context at that rate instead of reading it
    cw = sum(int(r["cache_write_1h"]) for r in req)
    save = cw * (R_W1 - R_W5) / 1e6
    extra = sum(int(g["prev_ctx"]) for g in gaps if float(g["gap_s"]) > 300) * (R_W5 - R_CR) / 1e6
    # a gap over 300 s rewrites; also gaps within a tool-running turn are not in gaps.tsv unless over 300 s
    p("%s: 1h writes %d tokens; 5m-rate saving %.2f USD; %d gaps over 300 s (longest %.0f s, none over 3600 s) rewrite sum prev_ctx %d tokens = +%.2f USD; net 5-minute minus 1-hour = %+.2f USD" % (
        label, cw, save, len(gaps), max(float(g["gap_s"]) for g in gaps), sum(int(g["prev_ctx"]) for g in gaps), extra, extra - save))
    if gaps:
        p("   every gap over 300 s was a cache HIT on the real run: cache_read / prev_ctx min %.4f" % min(int(g["cache_read"]) / int(g["prev_ctx"]) for g in gaps))


def fresh_wave6(req5, turns5):
    # the wave-6 opening turn (last turn of w5) at its real context vs a fresh session
    last = turns5[-1]
    t0 = last["t_start_utc"]
    rq = [r for r in req5 if r["t_utc"] >= t0]
    actual = sum(float(r["usd_list"]) for r in rq)
    ctx0 = int(last["ctx_start"])
    p("wave-6 opening turn: %d requests from %s, ctx %dk -> %dk, actual USD %.2f (preceded by 2975 s human-away gap; 1h cache hit)" % (len(rq), t0, ctx0 // 1000, int(rq[-1]["ctx"]) // 1000, actual))
    for H in (0, 10000, 30000, 85000):
        fresh_ctx0 = BASE + H
        cost = (BASE + H) * R_W1 / 1e6  # cold start: write the base and the handoff
        # preface requests to read the handoff: assume H tokens arrive over ~5 requests at the write rate, re-read cost counted
        if H:
            for i in range(5):
                cost += (BASE + H * i / 5) * R_CR / 1e6 + (H / 5) * R_W1 / 1e6
        prev = fresh_ctx0
        for r in rq:
            new = int(r["cache_write_1h"]) + int(r["cache_write_5m"])
            cost += prev * R_CR / 1e6 + new * R_W1 / 1e6 + int(r["output"]) * R_OUT / 1e6
            prev += new  # cw of a request already holds the previous request's output
        p("   fresh session, handoff H=%6d tokens: USD %.2f ; saves %+.2f vs actual %.2f" % (H, cost, actual - cost, actual))


def waves123():
    rows = list(csv.DictReader(open(W123), delimiter="\t"))
    bounds = [("wave 1", "2026-10-19T00:00:00", "2026-10-19T03:29:00"), ("wave 2", "2026-10-19T03:29:00", "2026-10-19T07:44:00"), ("wave 3", "2026-10-19T07:44:00", "2026-10-19T23:59:00")]
    p("waves 1-3 session (explorer-w05-b's table), actual vs one fresh session per wave (boundaries: wave-2 open 12:29 JST, wave-2 close 16:43 JST by commit time; wave 3 starts at the first request after that, so the wave-3 window includes the human's 17:00-20:00 gap)")
    tot_act = tot_fresh = {}
    res = {}
    for H in (10000, 30000, 85000):
        ta = tf = 0.0
        out_rows = []
        for name, lo, hi in bounds:
            rs = [r for r in rows if lo <= r["t_iso"] < hi]
            if not rs:
                continue
            act = sum(float(r["cost_usd_list"]) for r in rs)
            cost = (BASE + H) * R_W1 / 1e6
            prev = BASE + H
            if name == "wave 1":  # the real session started here: request 0 already writes the base, so only the handoff is extra
                cost, prev = H * R_W1 / 1e6, H
            for r in rs:
                new = int(r["cache_write_1h"]) + int(r["cache_write_5m"])
                ctx = int(r["ctx"])
                miss = new > 0.5 * ctx and r is not rs[0]  # whole-context rewrite after an idle gap or a compaction: in a fresh session the rewrite is the new context only
                if miss:
                    new = min(max(int(r["delta_ctx"]), 0), 20000)
                cost += prev * R_CR / 1e6 + new * R_W1 / 1e6 + int(r["output"]) * R_OUT / 1e6
                prev += new  # cw of a request already holds the previous request's output
                if int(r["reset"]):
                    prev = BASE + H + 15000  # a compaction would have happened in the real run; the fresh session carries its own growth, cap at what real compaction left
            out_rows.append((name, len(rs), max(int(r["ctx"]) for r in rs), act, cost))
            ta += act
            tf += cost
        p("  H=%d tokens: " % H + "; ".join("%s n=%d maxctx=%dk actual %.2f fresh %.2f" % (n, k, c // 1000, a, f) for n, k, c, a, f in out_rows) + " | total actual %.2f fresh %.2f saves %.2f (%.0f%%)" % (ta, tf, ta - tf, 100 * (ta - tf) / ta))


def restart_breakeven():
    p("restart-in-the-middle break-even: restart at context C saves (C - (BASE+H)) * R_CR per later request and costs (BASE+H) * R_W1 once (cold write), so it pays after N requests where N = (BASE+H)*R_W1 / ((C-(BASE+H))*R_CR)")
    for H in (10000, 30000):
        for C in (200000, 300000, 390000):
            b = BASE + H
            n = b * R_W1 / ((C - b) * R_CR)
            p("   H=%d C=%dk: N = %.1f later requests" % (H, C // 1000, n))


if __name__ == "__main__":
    for x in spend_table():
        pass
    t4, t5 = tsv("w4_turns.tsv"), tsv("w5_turns.tsv")
    r4, r5 = tsv("w4_req.tsv"), tsv("w5_req.tsv")
    p("## time split")
    time_split("wave 4 (turns 0-24)", t4, len(t4) - 1)
    time_split("wave 5 (turns 0-23)", t5, len(t5) - 2)
    p("## wake-ups")
    classes("wave 4", t4, len(t4) - 1)
    classes("wave 5 (turns 0-23)", t5, len(t5) - 2)
    p("## cost per wake-up against context")
    cost_vs_ctx("wave 4", t4, r4, len(t4) - 1)
    cost_vs_ctx("wave 5", t5, r5, len(t5) - 2)
    buckets(t4, t5)
    p("## cache life")
    cache5("wave 4", r4, tsv("w4_gaps.tsv"))
    cache5("wave 5", r5, tsv("w5_gaps.tsv"))
    p("## fresh session")
    fresh_wave6(r5, t5)
    waves123()
    restart_breakeven()
    open(os.path.join(DIR, "summary_tables.txt"), "w").write("\n".join(OUT) + "\n")
