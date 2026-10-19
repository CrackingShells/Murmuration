#!/usr/bin/env python3
"""Puzzle helper: share of cache-write tokens that arrives in spikes (>8k in one turn) in this run's explorers,
and how many skill_listing attachments the file holds. Run: python3 -I cw_spikes.py  (read-only, stdlib)."""
import importlib.util, os, json, collections
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p", os.path.join(here, "..", "explorer-w01-a", "profile_runs.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
d = os.path.join(P.PROJ, P.WT, "ab96c5ed-ead3-4b36-9671-6076e3914087", "subagents")
for rid, n in [("a1f4458ce75dacdec", "c"), ("ac6c27171353e66ed", "b"), ("a996dba2994d53126", "d"), ("af01bccf4de2a3706", "a"),
               ("a53e063b007b7a428", "e"), ("a6a6066b76cfb02ea", "f")]:
    p = os.path.join(d, "agent-%s.jsonl" % rid)
    s = P.scan(p)
    mids = sorted(s["msgs"], key=lambda m: s["msgs"][m]["ts"][0])
    cws = [P.usage_vec(s["msgs"][m]["copies"][-1])["cw"] for m in mids]
    spikes = [c for i, c in enumerate(cws) if i > 0 and c > 8000]
    listings = sum(1 for l in open(p) if '"type":"skill_listing"' in l.replace(' ', ''))
    print("explorer-w01-%s turns %d cw_total %d first_turn_cw %d spikes(>8k, not first) n=%d sum=%d share_of_cw=%.2f skill_listing_attachments=%d" %
          (n, len(mids), sum(cws), cws[0], len(spikes), sum(spikes), sum(spikes) / sum(cws), listings))
