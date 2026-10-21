# Manual labels (reproducer-w06-7) for the 114 denied lab Bash calls, by index into out/classified.json; a = mention only, no claude run; b = the act the guard exists to stop; c = other. Output: counts and a cross-check against an automatic rule
import json, collections
rows = json.load(open("/private/tmp/murmuration-w06/reproducer-w06-7/out/classified.json"))
A = {0,1,2,4,7,8,9,10,11,12,13,15,19,20,21,64,67,87, 28,55,68,73, 3,5,6,34,56}
B = {22,23,24,61,62,63,66,74,77,78,79,80,81,82,83,84,85,88,89,90,91,92,94,95,96,105,106,107,110,111,112,113,
     26,27,42,50,51,100,108,109,
     14,36,37,38,39,40,41,43,44,45,46,47,48,49,52,53,54,70,71,72,75,76,98}
C = {86,93,97,103, 16,17,18,25,65,69,99,101,102, 29,30,31,32,33,35,57,58,59,60,104}
assert not (A & B) and not (A & C) and not (B & C) and len(A | B | C) == len(rows) == 114, (len(A|B|C), len(rows))
lab = {i: "a" for i in A}; lab.update({i: "b" for i in B}); lab.update({i: "c" for i in C})
if __name__ == "__main__":
    cnt = collections.Counter((r["group"], lab[i]) for i, r in enumerate(rows)); print(sorted(cnt.items()))
    print("totals", collections.Counter(lab.values()))
    # automatic rule: b if the command text outside data heredocs still denies AND runs a claude segment (or writes settings: G3 handled by hand)
    dis = [(i, rows[i]["group"], lab[i], rows[i]["denied_without_data_heredocs"], rows[i]["runs_claude_seg"]) for i in range(len(rows)) if rows[i]["group"] != "G3" and ((rows[i]["denied_without_data_heredocs"] and rows[i]["runs_claude_seg"]) != (lab[i] == "b"))]
    print("disagreements with automatic rule (non-G3):", len(dis)); print(dis)
