#!/usr/bin/env python3
"""Figures for __reports__/instrument_validation/00-findings_v0.md, drawn from validation/data and validation/runs.

Python with matplotlib: the figures are two small strip/bar charts of already computed numbers.
Usage: python3 validation/figures.py [--out __reports__/instrument_validation]
"""
import argparse
import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INK, MUTED = "#222222", "#777777"
BLUE, ORANGE, GREY = "#1f5fa8", "#d1601a", "#b5b5b5"


def fig_a(out):
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "data", "retention_scores.csv"), encoding="utf-8")) if r["sim_pi"] != ""]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=False)
    levels = ["NONE", "MENTION", "ACTED"]
    for ax, key, title in ((axes[0], "sim_pi", "MiniLM similarity to the nearest later PI-note line"),
                           (axes[1], "retention_pi", "Key-term retention in later PI notes (share)")):
        for i, lv in enumerate(levels):
            pts = [r for r in rows if r["reach"] == lv]
            # deterministic jitter from the row index
            xs = [i + ((hash_ix(r["id"]) % 11) - 5) * 0.035 for r in pts]
            ys = [float(r[key]) for r in pts]
            ax.scatter(xs, ys, s=16, color=GREY, zorder=2, label="other bullets" if i == 0 else None)
        for r in rows:
            i = levels.index(r["reach"])
            x = i + ((hash_ix(r["id"]) % 11) - 5) * 0.035
            y = float(r[key])
            if r["missed_signal"] and r["signal_match"] == "primary":
                ax.scatter([x], [y], s=70, color=ORANGE, zorder=3, edgecolor=INK, linewidth=0.6)
                ax.annotate(r["missed_signal"], (x, y), xytext=(6, 4), textcoords="offset points", fontsize=8, color=ORANGE)
            if r["followed"] == "primary":
                ax.scatter([x], [y], s=70, color=BLUE, zorder=3, edgecolor=INK, linewidth=0.6, marker="D")
                ax.annotate("F (2, 6, 20, 58)", (x, y), xytext=(6, 4), textcoords="offset points", fontsize=8, color=BLUE)
        ax.set_xticks(range(3))
        ax.set_xticklabels([f"{lv}\n(n={sum(1 for r in rows if r['reach'] == lv)})" for lv in levels])
        ax.set_xlabel("hand label: how far the bullet travelled")
        ax.set_title(title, fontsize=9, color=INK)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("cosine (higher = closer)")
    axes[1].set_ylabel("share of key terms found")
    fig.suptitle("Experiment A: hand-labelled reach vs two automatic scores (orange = missed signals M2-M5, blue diamond = the followed count)",
                 fontsize=9.5, color=INK, y=0.995)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "00-findings_v0-experiment_a.png"), dpi=170)
    plt.close(fig)


def hash_ix(s):
    return sum(ord(c) * (i + 1) for i, c in enumerate(s))


def fig_b(out):
    d = json.load(open(os.path.join(HERE, "runs", "planted_cascade_results.json"), encoding="utf-8"))["runs"]
    labels = ["null: other\nreports (mean)", "author's report\n(primed run saw it)", "reproduction report\n(neither saw it)",
              "revised report v1\n(neither saw it)", "first message\n(brief + claim [+ report])"]
    keys = ["null_reports_mean_L12", "reuse_author_L12", "reuse_reproduction_report_L12", "reuse_revised_author_v1_L12", "reuse_first_message_L12"]
    fig, ax = plt.subplots(figsize=(9, 4))
    w = 0.38
    for j, (run, col, name) in enumerate((("run1", BLUE, "run 1: independence first"), ("run2", ORANGE, "run 2: author's report first"))):
        vals = [d[run][k] * 100 for k in keys]
        xs = [i + (j - 0.5) * w for i in range(len(keys))]
        ax.bar(xs, vals, w, color=col, label=name)
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.4, f"{v:.1f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("% of the verdict's bytes\ncovered by matches >= 12 bytes")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Experiment B: byte reuse of each verdict from five sources (one run per arm)", fontsize=9.5, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "00-findings_v0-experiment_b.png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "__reports__", "instrument_validation"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fig_a(a.out)
    fig_b(a.out)
    print("wrote", a.out)
