# Sums list-price USD of one PI session (main thread) and of its subagents by role (author, explorer, reproducer, proof-adversary, other), via scripts/lab_status.py's own parser and prices; input: one main transcript .jsonl (subagents read from its folder), output: a TSV of (agent label, role, model, msgs, usd) and role totals on stdout.
# usage: python3 -I __instrumenta__/w08h_wave_spend.py <main.jsonl>
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L
path = sys.argv[1]
ws = []
sessions, _ = L.load_sessions([path], ws)
tot = {}
print("label\trole\tmodel\tmsgs\tusd\tlower_bound")
for s in sessions:
    for (label, model), row in sorted(s["rows"].items(), key=lambda kv: -kv[1]["usd"]):
        if "main thread" in label: role = "PI"
        else:
            m = re.search(r"(author|explorer|reproducer|proof-adversary)", label)
            role = m.group(1) if m else "other"
        tot[role] = tot.get(role, 0) + row["usd"]
        print(f"{label}\t{role}\t{model}\t{row['msgs']}\t{row['usd']:.4f}\t{'+' if row['lower'] else ''}")
print("TOTALS\t" + "\t".join(f"{k}={v:.2f}" for k, v in sorted(tot.items())) + f"\tsum={sum(tot.values()):.2f}")
