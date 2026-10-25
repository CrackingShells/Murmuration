# Prints, for one claim id, the escalating verifier's hand-back, the PI text of the wake turns, and the verdict section of the claim file at the ESCALATE verdict, from <outdir>/wakes.json and <outdir>/claim_at_verdict/<id>.md written by w09h_extract.py.
# usage: python3 -I w09h_show.py <outdir> <claim-id> [wake-index]
import sys, json, os
out, cid = sys.argv[1], sys.argv[2]
wi = int(sys.argv[3]) if len(sys.argv) > 3 else 0
r = json.load(open(os.path.join(out, "wakes.json")))[cid]
w = r["wakes"][wi]
print("##### HANDBACK", w["label"], w["turn"], w["t"], w["agent"], w["body_chars"])
print(w["body"])
for f in w["follow"][:2]:
    print("##### PI turn", f["turn"], f["t"], f["trig"], "opens_claim", f["opens_claim"])
    print(f["pi_text"][:2500])
    print("calls:", [(c[0], c[1][:120]) for c in f["calls"]][:8])
txt = open(os.path.join(out, "claim_at_verdict", cid + ".md")).read()
i = txt.find("## verdict: " + r["verifier"])
print("##### CLAIM FILE: head+body chars", i, "; verdict section chars", len(txt) - i)
print(txt[i:])
