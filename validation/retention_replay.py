#!/usr/bin/env python3
"""Experiment A: retention replay on the genesis study (offline, no agent runs).

Python fits because everything here is deterministic text arithmetic over a few hundred kilobytes
of Markdown and git history: tokenizing, set intersection, cosine similarity, rank statistics.

Functions
  extract_surprises(md, report)      bullets of "Contradictions & Surprises" and rows of "Observations"
  retention(bullet, docs, ...)       share of the bullet's key terms found in later documents
  coverage(text, terms)              share of the user's terms a text uses
  similarity(bullets, docs)          max cosine of each bullet to chunks of later PI documents
Usage
  python3 validation/retention_replay.py --selftest
  python3 validation/retention_replay.py --extract     # write labels/surprises.csv skeleton (keeps existing labels)
  python3 validation/retention_replay.py --run         # score the labelled bullets, write data/retention_scores.csv + data/summary.json

The genesis repository is read through `git show` and `git log` at a pinned revision, never written.
Measures are instruments for attention, not decision rules (see __reports__/genesis/08).
"""
import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GENESIS = "/Users/hacker/Documents/explore/combinatorics_on_binary"
REV = "17e97ae"  # pinned: the genesis HEAD when this experiment ran

REPORTS = [  # id, path, the file that is "the report as first raised" (v0)
    ("literature", "__reports__/literature/00-findings_v0.md"),
    ("foundations", "__reports__/foundations/00-findings_v0.md"),
    ("atlas", "__reports__/generative_atlas/00-findings_v0.md"),
    ("laws", "__reports__/generative_laws/00-findings_v0.md"),
    ("superstring", "__reports__/superstring_g/00-findings_v0.md"),
    ("trellis", "__reports__/strided_trellis/00-findings_v0.md"),
    ("reproduction", "__reports__/reproduction/00-findings_v0.md"),
    ("naming", "__reports__/naming/00-findings_v0.md"),
]
PI_PATHS = ["__reports__/pi_decisions/", "__design__/notebook_outline.md"]
ROADMAP_PATHS = ["__roadmap__/"]
FRAMING_PATHS = ["__design__/problem_framing.md"]
NOTEBOOK_PATHS = ["notebook/imbrication.md"]

# The user's own words as quoted in 02-knowledge_transfer_v2 (table row 1): "a combinatorics problem",
# "bounds of the numbers that can be expressed", "generative sequences", "a whole generative space",
# calling the idea "dumb or naive".
USER_TERMS = ["combinatorics", "problem", "bounds", "numbers", "expressed", "generative", "sequences", "whole",
              "space", "dumb", "naive", "idea"]

STOP = set("""a an and are as at be been but by can for from has have if in into is it its not of on or so than that the
their then there these this those to was were which while will with within without also only more most such both each
any all one two how what when where who why whose whom does do did done should would could may might must we our us you
your they them he she his her i me my versus via per vs e g i e eg ie etc about above after again against because before
below between during further here just over same some too under until very yet""".split())

# ------------------------------------------------------------------ text
TOKEN = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)


def stem(w):
    """Crude suffix stripper, applied identically to both sides of every comparison."""
    if w.endswith("ing") and len(w) > 6:
        w = w[:-3]
    elif w.endswith("ed") and len(w) > 5:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith(("ss", "us")) and len(w) > 4:
        w = w[:-1]
    if w.endswith("e") and len(w) > 4:
        w = w[:-1]
    return w


def _fold(text):
    """Strip combining marks (Piṅgala = Pingala, yamātārāja = yamataraja) but keep Greek and maths letters."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def tokens(text):
    """Lower-cased, diacritic-folded, stemmed tokens; hyphenated compounds stay whole."""
    text = re.sub(r"['’]s\b", "", _fold(text))  # possessives: Pingala's = Pingala
    return [stem(t) for t in (m.group(0).lower() for m in TOKEN.finditer(text))]


def is_content(t):
    return t not in STOP and (len(t) >= 4 or any(c.isdigit() for c in t) or any(ord(c) > 127 for c in t))


def clean(text):
    text = re.sub(r"\[source:[^\]]*\]", " ", text)
    text = re.sub(r"[*`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------ extraction
def _section(md, title_prefix):
    out, on = [], False
    for line in md.splitlines():
        if line.startswith("## "):
            on = line[3:].strip().startswith(title_prefix)
            continue
        if on:
            out.append(line)
    return out


def extract_surprises(md, report):
    """List of dicts {id, report, kind, text}. kind CS = bullet of Contradictions & Surprises,
    OBS = row of the Observations table (signal, observed, interpretation joined; baseline column omitted)."""
    items = []
    n = 0
    for line in _section(md, "Contradictions & Surprises"):
        if line.startswith("- "):
            n += 1
            items.append({"id": f"{report}:CS:{n}", "report": report, "kind": "CS", "text": clean(line[2:])})
    n = 0
    for line in _section(md, "Observations"):
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= set(":- "):
            continue
        inner = line.strip()[1:-1] if line.strip().endswith("|") else line.strip()[1:]
        cells = [c.strip() for c in re.split(r"\s\|\s", inner)]  # cell pipes have spaces; "|G|" and "|error|" do not
        if len(cells) != 4 or cells[0].lower() == "signal":
            continue
        n += 1
        items.append({"id": f"{report}:OBS:{n}", "report": report, "kind": "OBS",
                      "text": clean(" — ".join([cells[0], cells[2], cells[3]]))})
    return items


# --------------------------------------------------------------- git view
def git(*args):
    return subprocess.run(["git", "--no-optional-locks", "-C", GENESIS, *args], check=True, capture_output=True,
                          text=True).stdout


def report_time(path):
    return git("log", "--diff-filter=A", "--format=%aI", REV, "--", path).strip().splitlines()[-1]


def downstream_docs():
    """One document per (commit, file): the lines that commit added to a PI, roadmap, framing or notebook file."""
    docs = []
    classes = [("PI", PI_PATHS), ("ROADMAP", ROADMAP_PATHS), ("FRAMING", FRAMING_PATHS), ("NOTEBOOK", NOTEBOOK_PATHS)]
    allpaths = [p for _, ps in classes for p in ps]
    log = git("log", "--reverse", "--no-color", "-U0", "--format=@@@%h|%aI|%s", REV, "--", *allpaths)
    cur, path, buf = None, None, []

    def flush():
        if cur and path and buf:
            docs.append({"commit": cur[0], "ts": cur[1], "subject": cur[2], "path": path, "cls": cls_of(path),
                         "text": "\n".join(buf)})

    def cls_of(p):
        for c, ps in classes:
            if any(p.startswith(x) for x in ps):
                return c
        return "OTHER"

    for line in log.splitlines():
        if line.startswith("@@@"):
            flush()
            h, ts, subj = line[3:].split("|", 2)
            cur, path, buf = (h, ts, subj), None, []
        elif line.startswith("+++ b/"):
            flush()
            path, buf = line[6:], []
        elif line.startswith("+") and not line.startswith("+++"):
            buf.append(line[1:])
    flush()
    return docs


# ---------------------------------------------------------------- measures
def key_terms(text, df, df_max=3):
    """Distinctive content terms of a bullet: content tokens held by at most df_max bullets of the whole set."""
    seen, out = set(), []
    for t in tokens(text):
        if t in seen or not is_content(t):
            continue
        seen.add(t)
        if df.get(t, 0) <= df_max:
            out.append(t)
    return out


def found_terms(terms, docs):
    """The subset of `terms` that occurs anywhere in `docs`."""
    seen = set()
    for d in docs:
        seen.update(tokens(d["text"]))
    return [t for t in terms if t in seen]


def retention(terms, docs):
    """(share of `terms` found anywhere in `docs`, whether >= 2 terms co-occur on one line of one doc).

    docs: list of dicts with "text". Empty terms give (0.0, False); empty docs give (0.0, False).
    """
    if not terms:
        return 0.0, False
    found, co = set(), False
    for d in docs:
        for line in d["text"].splitlines():
            lt = set(tokens(line))
            hit = [t for t in terms if t in lt]
            found.update(hit)
            co = co or len(hit) >= 2
    return len(found) / len(terms), co


def coverage(text, terms):
    """Share of `terms` (stemmed) that occur in `text`."""
    tk = set(tokens(text))
    return sum(1 for t in terms if stem(t.lower()) in tk) / len(terms)


def chunks(docs):
    """Sentence-ish chunks of at least 5 words: one per non-empty line (table rows and bullets are lines)."""
    out = []
    for d in docs:
        for line in d["text"].splitlines():
            line = clean(line)
            if len(line.split()) >= 5 and not line.startswith(("---", "```")):
                out.append(line)
    return out


def _jaccard(a, b):
    a, b = {t for t in tokens(a) if is_content(t)}, {t for t in tokens(b) if is_content(t)}
    return len(a & b) / len(a | b) if a | b else 0.0


class Embedder:
    """MiniLM if loadable offline (numpy implementation, checked against transformers), else term overlap."""

    def __init__(self):
        from minilm_np import load_or_none

        self.model = load_or_none()
        self.name = "all-MiniLM-L6-v2 (numpy)" if self.model else "term overlap (Jaccard on stemmed content tokens)"
        self._cache = {}

    def _enc(self, texts):
        new = [t for t in dict.fromkeys(texts) if t not in self._cache]
        if new:
            for t, v in zip(new, self.model.encode(new)):
                self._cache[t] = v
        import numpy as np

        return np.stack([self._cache[t] for t in texts])

    def sim_matrix(self, A, B):
        if self.model is not None:
            ea, eb = self._enc(A), self._enc(B)
            return ea @ eb.T
        return [[_jaccard(a, b) for b in B] for a in A]


def similarity(bullets, doc_lists, emb):
    """For each bullet, max similarity to any chunk of its own (time-filtered) document list; None if no chunks."""
    out, cache = [], {}
    for b, docs in zip(bullets, doc_lists):
        ch = chunks(docs)
        if not ch:
            out.append((None, ""))
            continue
        m = emb.sim_matrix([b], ch)[0]
        j = max(range(len(ch)), key=lambda i: m[i])
        out.append((float(m[j]), ch[j][:90]))
    return out


# --------------------------------------------------------------------- run
LABEL_COLS = ["id", "report", "kind", "text", "reach", "reach_where", "missed_signal", "signal_match", "followed", "note"]


def read_labels(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def extract_all():
    items = []
    for rid, path in REPORTS:
        items += extract_surprises(git("show", f"{REV}:{path}"), rid)
    return items


def cmd_extract(labels_path):
    old = read_labels(labels_path)
    rows = []
    for it in extract_all():
        r = {c: "" for c in LABEL_COLS}
        r.update(old.get(it["id"], {}))
        r.update({k: it[k] for k in ("id", "report", "kind", "text")})
        rows.append(r)
    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LABEL_COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {labels_path}")


def auc(pos, neg):
    """P(a random positive scores above a random negative), ties half. None if either side is empty."""
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def perm_p(pos, neg, trials=20000, seed=0):
    """One-sided permutation p-value of auc(pos, neg) under label shuffling; exact when C(n, k) <= trials."""
    import itertools
    import random

    vals, k = list(pos) + list(neg), len(pos)
    obs = auc(pos, neg)
    from math import comb

    if comb(len(vals), k) <= trials:
        hits = tot = 0
        for idx in itertools.combinations(range(len(vals)), k):
            ps = [vals[i] for i in idx]
            ns = [vals[i] for i in range(len(vals)) if i not in set(idx)]
            hits += auc(ps, ns) >= obs - 1e-12
            tot += 1
        return hits / tot
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        rng.shuffle(vals)
        hits += auc(vals[:k], vals[k:]) >= obs - 1e-12
    return (hits + 1) / (trials + 1)


def _pct_rank(values, x):
    """Share of values strictly below x (ties count half)."""
    below = sum(1 for v in values if v < x) + 0.5 * sum(1 for v in values if v == x)
    return below / len(values)


def cmd_run(labels_path, outdir):
    labels = read_labels(labels_path)
    rows = list(labels.values())
    if not rows or any(not r["reach"] for r in rows):
        sys.exit("labels incomplete: run --extract and fill every `reach`")
    docs = downstream_docs()
    times = {rid: report_time(p) for rid, p in REPORTS}
    texts = [r["text"] for r in rows]
    df = {}
    for t in texts:
        for k in set(x for x in tokens(t) if is_content(x)):
            df[k] = df.get(k, 0) + 1
    emb = Embedder()
    later = lambda r, classes: [d for d in docs if d["cls"] in classes and d["ts"] > times[r["report"]]]
    pi_lists = [later(r, {"PI"}) for r in rows]
    ext_lists = [later(r, {"PI", "ROADMAP", "FRAMING"}) for r in rows]
    nb_lists = [later(r, {"NOTEBOOK"}) for r in rows]
    sims = similarity(texts, pi_lists, emb)
    sims_ext = similarity(texts, ext_lists, emb)
    out = []
    for r, pl, el, nl, s, se in zip(rows, pi_lists, ext_lists, nb_lists, sims, sims_ext):
        kt = key_terms(r["text"], df)
        rp, cp = retention(kt, pl)
        re_, ce = retention(kt, el)
        rn, cn = retention(kt, nl)
        out.append({**r, "n_key_terms": len(kt), "key_terms": " ".join(kt), "n_pi_docs_later": len(pl),
                    "retention_pi": round(rp, 3), "matched_pi": " ".join(found_terms(kt, pl)), "cooccur_pi": int(cp), "retention_ext": round(re_, 3),
                    "cooccur_ext": int(ce), "retention_notebook": round(rn, 3),
                    "user_terms_hit": round(coverage(r["text"], USER_TERMS) * len(USER_TERMS)),
                    "sim_pi": "" if s[0] is None else round(s[0], 3), "sim_pi_chunk": s[1],
                    "sim_ext": "" if se[0] is None else round(se[0], 3)})
    os.makedirs(outdir, exist_ok=True)
    cols = list(out[0].keys())
    with open(os.path.join(outdir, "retention_scores.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    summary = summarize(out, emb.name)
    summary["user_coverage_docs"] = doc_coverage(outdir)
    with open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))


def doc_coverage(outdir):
    """User-term coverage of whole documents (the counsel's pilot, redone): reports, PI notes, the outline, the notebook."""
    docs = [(rid, git("show", f"{REV}:{path}")) for rid, path in REPORTS]
    for n in ("00-wave2_plan_v0", "01-wave3_plan_v0", "02-q8_and_synthesis_v0"):
        docs.append(("PI:" + n, git("show", f"{REV}:__reports__/pi_decisions/{n}.md")))
    docs.append(("outline", git("show", f"{REV}:__design__/notebook_outline.md")))
    docs.append(("notebook", git("show", f"{REV}:notebook/imbrication.md")))
    framing = git("show", f"{REV}:__design__/problem_framing.md").split("## 2.")[0]
    docs.append(("framing §1", framing))
    rows = []
    for name, text in docs:
        tk = set(tokens(text))
        hit = [t for t in USER_TERMS if stem(t.lower()) in tk]
        rows.append({"document": name, "coverage": round(len(hit) / len(USER_TERMS), 2), "hit": " ".join(hit),
                     "missing": " ".join(t for t in USER_TERMS if t not in hit)})
    with open(os.path.join(outdir, "user_coverage.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


def summarize(out, embedder_name):
    has_pi = [r for r in out if r["n_pi_docs_later"] > 0]
    sims = [float(r["sim_pi"]) for r in has_pi if r["sim_pi"] != ""]
    cs = [r for r in has_pi if r["kind"] == "CS"]
    sims_cs = [float(r["sim_pi"]) for r in cs if r["sim_pi"] != ""]
    groups = {"missed_primary": [r for r in out if r["missed_signal"] and r["signal_match"] == "primary"],
              "missed_related": [r for r in out if r["missed_signal"] and r["signal_match"] == "related"],
              "followed": [r for r in out if r["followed"] == "primary"],
              "followed_other": [r for r in out if r["followed"] == "other"]}
    s = {"embedder": embedder_name, "n_bullets": len(out), "n_with_later_pi_doc": len(has_pi),
         "n_cs_with_later_pi_doc": len(cs), "groups": {}}
    for g, rs in groups.items():
        s["groups"][g] = [{"id": r["id"], "signal": r["missed_signal"] or "F", "reach": r["reach"],
                           "retention_pi": r["retention_pi"], "retention_ext": r["retention_ext"],
                           "cooccur_pi": r["cooccur_pi"], "sim_pi": r["sim_pi"],
                           "sim_pct_all": None if r["sim_pi"] == "" or not sims else round(_pct_rank(sims, float(r["sim_pi"])), 2),
                           "sim_pct_cs": None if r["sim_pi"] == "" or r["kind"] != "CS" or not sims_cs else round(_pct_rank(sims_cs, float(r["sim_pi"])), 2),
                           "user_terms_hit": r["user_terms_hit"]} for r in rs]
    # agreement between the automatic retention and the hand label
    def agree(key):
        tp = fp = fn = tn = 0
        for r in has_pi:
            hand = r["reach"] in ("MENTION", "ACTED")
            auto = float(r[key]) > 0
            tp += hand and auto
            fp += (not hand) and auto
            fn += hand and (not auto)
            tn += (not hand) and (not auto)
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}

    s["auto_vs_hand"] = {"retention_pi>0": agree("retention_pi"), "retention_ext>0": agree("retention_ext")}
    s["reach_counts"] = {k: sum(1 for r in out if r["reach"] == k) for k in ("NONE", "MENTION", "ACTED")}
    s["reach_counts_cs"] = {k: sum(1 for r in out if r["reach"] == k and r["kind"] == "CS") for k in ("NONE", "MENTION", "ACTED")}
    # discrimination of the automatic scores against the hand labels (bullets that have a later PI document)
    fl = lambda r, key: float(r[key]) if r[key] != "" else None
    carried = [r for r in has_pi if r["reach"] in ("MENTION", "ACTED")]
    dropped = [r for r in has_pi if r["reach"] == "NONE"]
    acted = [r for r in has_pi if r["reach"] == "ACTED"]
    s["auc_hand"] = {
        "sim_pi: carried(MENTION+ACTED) vs NONE": auc([fl(r, "sim_pi") for r in carried], [fl(r, "sim_pi") for r in dropped]),
        "retention_pi: carried vs NONE": auc([float(r["retention_pi"]) for r in carried], [float(r["retention_pi"]) for r in dropped]),
        "sim_pi: ACTED vs rest": auc([fl(r, "sim_pi") for r in acted], [fl(r, "sim_pi") for r in has_pi if r["reach"] != "ACTED"]),
        "retention_pi: ACTED vs rest": auc([float(r["retention_pi"]) for r in acted], [float(r["retention_pi"]) for r in has_pi if r["reach"] != "ACTED"]),
    }
    mp = [r for r in out if r["missed_signal"] and r["signal_match"] == "primary" and r["n_pi_docs_later"] > 0]
    fo = [r for r in out if r["followed"] and r["n_pi_docs_later"] > 0]
    s["missed_vs_followed"] = {"n_missed_primary": len(mp), "n_followed": len(fo)}
    for key in ("sim_pi", "retention_pi", "user_terms_hit"):
        pos, neg = [float(r[key]) for r in fo], [float(r[key]) for r in mp]
        s["missed_vs_followed"][key] = {"auc_followed_above_missed": auc(pos, neg), "perm_p_one_sided": perm_p(pos, neg),
                                        "followed": pos, "missed": neg}
    s["zero_retention_crosstab"] = {k: {"retention_pi==0": sum(1 for r in has_pi if r["reach"] == k and float(r["retention_pi"]) == 0),
                                        "retention_pi>0": sum(1 for r in has_pi if r["reach"] == k and float(r["retention_pi"]) > 0)}
                                    for k in ("NONE", "MENTION", "ACTED")}
    # share of bullets with zero retention, by hand reach
    s["mean_sim_by_reach"] = {k: (lambda v: round(sum(v) / len(v), 3) if v else None)(
        [float(r["sim_pi"]) for r in has_pi if r["reach"] == k and r["sim_pi"] != ""]) for k in ("NONE", "MENTION", "ACTED")}
    return s


# ---------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    md = ("# R\n\n## Observations\n\n| Signal | Baseline | Observed [source: x] | Interp |\n|:--|:--|:--|:--|\n"
          "| alpha | b | seen **twice** [source: f.csv] | because |\n| beta | b | seen once | so |\n\n"
          "## Contradictions & Surprises\n\n- first surprise\n- second `surprise`\n\n## Steering Questions\n- [now] ignore\n")
    its = extract_surprises(md, "r")
    check("extract: 2 CS then 2 OBS", [i["kind"] for i in its] == ["CS", "CS", "OBS", "OBS"])
    check("extract: ids", [i["id"] for i in its] == ["r:CS:1", "r:CS:2", "r:OBS:1", "r:OBS:2"])
    check("extract: source tag and markup removed, baseline column omitted", its[2]["text"] == "alpha — seen twice — because")
    check("extract: Steering Questions not read", all("ignore" not in i["text"] for i in its))
    check("tokens: diacritics folded, possessive dropped", tokens("Piṅgala") == tokens("Pingala's") == tokens("Pingala"))
    check("tokens: hyphenated compound kept whole", stem("m-sequence") in tokens("The m-sequence is free"))
    check("stem: inflections meet", stem("sequences") == stem("sequence") and stem("generated") == stem("generate") and stem("less") == "less")
    docs = [{"text": "The Champernowne completion is slow.\nOther unrelated text here."}]
    check("retention: found", retention([stem("champernowne"), stem("completion")], docs) == (1.0, True))
    check("retention: terms on different lines are found but do not co-occur", retention([stem("champernowne"), stem("unrelated")], docs) == (1.0, False))
    check("retention: half found", retention([stem("champernowne"), stem("bernoulli")], docs) == (0.5, False))
    check("retention: absent term", retention(["bernoulli"], docs) == (0.0, False))
    check("retention: empty inputs", retention([], docs) == (0.0, False) and retention(["x"], []) == (0.0, False))
    check("extract: pipes inside a cell (|G|) do not split it", len(extract_surprises("## Observations\n| S | B | O |G| and |x| y | I |\n|:-|:-|:-|:-|\n| s | b | o |G| | i |\n", "r")) == 2)
    check("coverage: 2 of 12", abs(coverage("a combinatorics problem", USER_TERMS) - 2 / 12) < 1e-12)
    check("coverage: stemmed plural", coverage("generative sequences", ["sequence"]) == 1.0)
    df = {stem("champernowne"): 1, stem("slow"): 9}
    check("key_terms: only distinctive content terms", key_terms("The Champernowne is slow slow", df) == [stem("champernowne")])
    check("jaccard: identical = 1, disjoint = 0", _jaccard("alpha beta gamma", "alpha beta gamma") == 1.0 and _jaccard("alpha beta", "gamma delta") == 0.0)
    check("auc: perfect, tie, empty", auc([3, 4], [1, 2]) == 1.0 and auc([1], [1]) == 0.5 and auc([], [1]) is None)
    check("perm_p: exact for a perfect split of 2 vs 2 (1/6)", abs(perm_p([3, 4], [1, 2]) - 1 / 6) < 1e-12)
    check("pct_rank: lowest and highest", _pct_rank([1, 2, 3], 1) == 1 / 6 and _pct_rank([1, 2, 3], 3) == 5 / 6)
    e = Embedder()
    sm = e.sim_matrix(["a trained table equals a random table", "Champernowne completes late"],
                      ["the trained table is the same as the random table", "a normal sequence finishes later than random"])
    check("embedder (%s): paraphrase beats unrelated" % e.name, sm[0][0] > sm[0][1] and sm[1][1] > sm[1][0])
    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--labels", default=os.path.join(HERE, "labels", "surprises.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "data"))
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.extract:
        cmd_extract(a.labels)
    elif a.run:
        cmd_run(a.labels, a.out)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
