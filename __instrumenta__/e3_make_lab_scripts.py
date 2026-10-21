# writes the 46 helper scripts of the E3 test lab (38 small synthetic ones, 8 copied from reflective_run folders and renamed); input: the repo root (script's grandparent), output: the folder given as argv[1] (default lab_scripts/ beside this file's report folder)
"""usage: python3 -I e3_make_lab_scripts.py OUTDIR

Each file's first line says what it computes, from which inputs, to which outputs (the convention of the agent files).
Two of them are the 'fit' and 'near fit' of the E3 tasks (names below, FIT and NEAR); several others are decoys on
neighbouring topics.  Stdlib only; no seeds.
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIT = "binary_max_distinct_substrings_bruteforce.py"
NEAR = "collatz_longest_stopping_time.py"

S = {}


def add(name, first, body):
    S[name] = "# " + first + "\n" + body.strip("\n") + "\n"


add(FIT, "computes, for each n from 1 to N, the maximum number of distinct non-empty substrings over all binary strings of length n and how many strings reach it, by brute force; input: N (argv[1], default 12); output: one line 'n max count' per n on stdout", '''
import sys
from itertools import product
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
ALPHABET = "01"
for n in range(1, N + 1):
    best, count = 0, 0
    for t in product(ALPHABET, repeat=n):
        s = "".join(t)
        d = len({s[i:j] for i in range(n) for j in range(i + 1, n + 1)})
        if d > best:
            best, count = d, 1
        elif d == best:
            count += 1
    print(n, best, count)
''')
add(NEAR, "finds, among start values 1 to LIMIT, the one whose Collatz trajectory takes the most steps to reach 1; input: LIMIT (argv[1], default 100000); output: 'start steps' on stdout", '''
import sys
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
cache = {1: 0}
def steps(n):
    path = []
    while n not in cache:
        path.append(n)
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    k = cache[n]
    for m in reversed(path):
        k += 1
        cache[m] = k
    return cache[path[0]] if path else cache[n]
best = max(range(1, LIMIT + 1), key=steps)
print(best, steps(best))
''')
add("collatz_trajectory_print.py", "prints the Collatz trajectory of one start value; input: n (argv[1]); output: the values, space separated, on stdout", '''
import sys
n = int(sys.argv[1])
out = [n]
while n != 1:
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    out.append(n)
print(*out)
''')
add("longest_repeated_substring.py", "finds the longest substring that occurs at least twice in a string; input: the string (argv[1]); output: the substring and its length on stdout", '''
import sys
s = sys.argv[1]
best = ""
for i in range(len(s)):
    for j in range(i + len(best) + 1, len(s) + 1):
        if s.count(s[i:j]) >= 2 and not s[i:j] == "":
            best = s[i:j]
print(best, len(best))
''')
add("distinct_subsequences_count.py", "counts the distinct subsequences of a string by dynamic programming; input: the string (argv[1]); output: the count on stdout", '''
import sys
s = sys.argv[1]
dp, last = 1, {}
for c in s:
    new = 2 * dp - last.get(c, 0)
    last[c] = dp
    dp = new
print(dp)
''')
add("de_bruijn_sequence.py", "builds a binary de Bruijn sequence of order k; input: k (argv[1]); output: the cyclic sequence as a string on stdout", '''
import sys
k = int(sys.argv[1])
a = [0] * (2 * k)
seq = []
def db(t, p):
    if t > k:
        if k % p == 0:
            seq.extend(a[1:p + 1])
    else:
        a[t] = a[t - p]
        db(t + 1, p)
        if a[t - p] == 0:
            a[t] = 1
            db(t + 1, t)
db(1, 1)
print("".join(map(str, seq)))
''')
add("string_factor_complexity_profile.py", "computes the number of distinct factors of each length 1..len for one given string; input: the string (argv[1]); output: lines 'length count' on stdout", '''
import sys
s = sys.argv[1]
for L in range(1, len(s) + 1):
    print(L, len({s[i:i + L] for i in range(len(s) - L + 1)}))
''')
add("count_binary_necklaces.py", "counts binary necklaces of length n (cyclic words up to rotation) with Burnside's lemma; input: n (argv[1]); output: the count on stdout", '''
import sys
from math import gcd
n = int(sys.argv[1])
print(sum(2 ** gcd(k, n) for k in range(n)) // n)
''')
add("catalan_numbers_table.py", "prints the first N Catalan numbers; input: N (argv[1]); output: lines 'i C_i' on stdout", '''
import sys
from math import comb
for i in range(int(sys.argv[1])):
    print(i, comb(2 * i, i) // (i + 1))
''')
add("partition_numbers.py", "computes the number of integer partitions p(n) for n up to N by dynamic programming; input: N (argv[1]); output: lines 'n p(n)' on stdout", '''
import sys
N = int(sys.argv[1])
p = [1] + [0] * N
for k in range(1, N + 1):
    for n in range(k, N + 1):
        p[n] += p[n - k]
for n in range(N + 1):
    print(n, p[n])
''')
add("prime_sieve_list.py", "lists the primes up to N with a sieve of Eratosthenes; input: N (argv[1]); output: the primes, space separated, on stdout", '''
import sys
N = int(sys.argv[1])
s = bytearray([1]) * (N + 1)
s[0:2] = b"\\x00\\x00"
for i in range(2, int(N ** 0.5) + 1):
    if s[i]:
        s[i * i::i] = bytearray(len(s[i * i::i]))
print(*[i for i in range(N + 1) if s[i]])
''')
add("gcd_lcm_of_list.py", "computes the gcd and the lcm of a list of integers; input: integers as argv; output: 'gcd lcm' on stdout", '''
import sys
from math import gcd
xs = list(map(int, sys.argv[1:]))
g, l = 0, 1
for x in xs:
    g = gcd(g, x)
    l = l * x // gcd(l, x)
print(g, l)
''')
add("fibonacci_mod_period.py", "finds the Pisano period of the Fibonacci numbers modulo m; input: m (argv[1]); output: the period on stdout", '''
import sys
m = int(sys.argv[1])
a, b, k = 0, 1, 0
while True:
    a, b = b, (a + b) % m
    k += 1
    if (a, b) == (0, 1):
        break
print(k)
''')
add("modular_inverse_table.py", "tabulates modular inverses of 1..p-1 for a prime p; input: p (argv[1]); output: lines 'a inverse' on stdout", '''
import sys
p = int(sys.argv[1])
for a in range(1, p):
    print(a, pow(a, -1, p))
''')
add("perfect_numbers_below.py", "lists the perfect numbers below N by divisor sums; input: N (argv[1]); output: the numbers on stdout", '''
import sys
N = int(sys.argv[1])
print(*[n for n in range(2, N) if sum(d for d in range(1, n // 2 + 1) if n % d == 0) == n])
''')
add("graph_connected_components.py", "counts the connected components of an undirected graph from an edge list file; input: path to a file with one 'u v' pair per line; output: the component count and sizes on stdout", '''
import sys
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
for line in open(sys.argv[1]):
    u, v = line.split()[:2]
    parent[find(u)] = find(v)
sizes = {}
for x in list(parent):
    sizes[find(x)] = sizes.get(find(x), 0) + 1
print(len(sizes), sorted(sizes.values(), reverse=True))
''')
add("graph_shortest_path_bfs.py", "finds a shortest path between two nodes of an unweighted graph by breadth-first search; input: edge list file, source, target (argv[1:4]); output: the path on stdout", '''
import sys
from collections import deque
adj = {}
for line in open(sys.argv[1]):
    u, v = line.split()[:2]
    adj.setdefault(u, []).append(v)
    adj.setdefault(v, []).append(u)
s, t = sys.argv[2], sys.argv[3]
prev, q = {s: None}, deque([s])
while q:
    x = q.popleft()
    for y in adj.get(x, []):
        if y not in prev:
            prev[y] = x
            q.append(y)
path, x = [], t
while x is not None and x in prev:
    path.append(x)
    x = prev[x]
print(*reversed(path))
''')
add("graph_degree_histogram.py", "tabulates the degree distribution of an undirected graph; input: edge list file (argv[1]); output: lines 'degree count' on stdout", '''
import sys
from collections import Counter
deg = Counter()
for line in open(sys.argv[1]):
    u, v = line.split()[:2]
    deg[u] += 1
    deg[v] += 1
for d, c in sorted(Counter(deg.values()).items()):
    print(d, c)
''')
add("csv_column_summary.py", "summarises one numeric column of a CSV file (count, mean, min, max, standard deviation); input: path, column name; output: one line of statistics on stdout", '''
import csv, statistics, sys
vals = [float(r[sys.argv[2]]) for r in csv.DictReader(open(sys.argv[1]))]
print(len(vals), statistics.mean(vals), min(vals), max(vals), statistics.pstdev(vals))
''')
add("csv_to_json_records.py", "converts a CSV file with a header row to a JSON list of records; input: CSV path (argv[1]); output: JSON on stdout", '''
import csv, json, sys
print(json.dumps(list(csv.DictReader(open(sys.argv[1]))), indent=1))
''')
add("json_keys_flatten.py", "flattens a nested JSON file into 'dotted.key value' lines; input: JSON path (argv[1]); output: lines on stdout", '''
import json, sys
def walk(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            walk(v, p + "." + k if p else k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, "%s[%d]" % (p, i))
    else:
        print(p, x)
walk(json.load(open(sys.argv[1])))
''')
add("jsonl_field_counter.py", "counts the values of one field across the lines of a JSON-lines file; input: path, field name; output: lines 'count value', most frequent first, on stdout", '''
import json, sys
from collections import Counter
c = Counter(str(json.loads(l).get(sys.argv[2])) for l in open(sys.argv[1]) if l.strip())
for v, n in c.most_common():
    print(n, v)
''')
add("word_frequency_table.py", "counts word frequencies in a text file, lower-cased; input: path (argv[1]), optional top K (argv[2], default 20); output: lines 'count word' on stdout", '''
import re, sys
from collections import Counter
c = Counter(re.findall(r"[a-z']+", open(sys.argv[1]).read().lower()))
for w, n in c.most_common(int(sys.argv[2]) if len(sys.argv) > 2 else 20):
    print(n, w)
''')
add("caesar_cipher_shift.py", "shifts the letters of a text by k places (Caesar cipher); input: text (argv[1]), k (argv[2]); output: the shifted text on stdout", '''
import sys
k = int(sys.argv[2])
print("".join(chr((ord(c) - 97 + k) % 26 + 97) if c.islower() else chr((ord(c) - 65 + k) % 26 + 65) if c.isupper() else c for c in sys.argv[1]))
''')
add("palindrome_check_batch.py", "tests each line of a text file for being a palindrome, ignoring case and non-letters; input: path (argv[1]); output: lines 'yes|no line' on stdout", '''
import sys
for line in open(sys.argv[1]):
    t = [c.lower() for c in line if c.isalpha()]
    print("yes" if t == t[::-1] else "no", line.strip())
''')
add("levenshtein_distance.py", "computes the edit distance between two strings; input: two strings (argv[1:3]); output: the distance on stdout", '''
import sys
a, b = sys.argv[1:3]
prev = list(range(len(b) + 1))
for i, ca in enumerate(a, 1):
    cur = [i]
    for j, cb in enumerate(b, 1):
        cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
    prev = cur
print(prev[-1])
''')
add("matrix_determinant_exact.py", "computes the exact determinant of an integer matrix with fractions; input: matrix rows as argv strings 'a,b,c'; output: the determinant on stdout", '''
import sys
from fractions import Fraction
m = [[Fraction(x) for x in r.split(",")] for r in sys.argv[1:]]
n, det = len(m), Fraction(1)
for i in range(n):
    p = next((r for r in range(i, n) if m[r][i] != 0), None)
    if p is None:
        det = Fraction(0)
        break
    if p != i:
        m[i], m[p] = m[p], m[i]
        det = -det
    det *= m[i][i]
    for r in range(i + 1, n):
        f = m[r][i] / m[i][i]
        m[r] = [a - f * b for a, b in zip(m[r], m[i])]
print(det)
''')
add("matrix_power_mod.py", "raises a square integer matrix to a power modulo m by repeated squaring; input: JSON matrix, exponent, modulus (argv[1:4]); output: the matrix as JSON on stdout", '''
import json, sys
A, e, m = json.loads(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
n = len(A)
mul = lambda X, Y: [[sum(X[i][k] * Y[k][j] for k in range(n)) % m for j in range(n)] for i in range(n)]
R = [[int(i == j) for j in range(n)] for i in range(n)]
while e:
    if e & 1:
        R = mul(R, A)
    A = mul(A, A)
    e >>= 1
print(json.dumps(R))
''')
add("random_walk_return_probability.py", "estimates by simulation the probability that a simple random walk on the integers returns to 0 within T steps; input: T, trials, seed (argv[1:4]); output: the estimate on stdout", '''
import random, sys
T, trials, seed = map(int, sys.argv[1:4])
random.seed(seed)
hits = 0
for _ in range(trials):
    x = 0
    for _ in range(T):
        x += random.choice((-1, 1))
        if x == 0:
            hits += 1
            break
print(hits / trials)
''')
add("monte_carlo_pi_estimate.py", "estimates pi by random points in the unit square; input: number of points, seed (argv[1:3]); output: the estimate on stdout", '''
import random, sys
n, seed = int(sys.argv[1]), int(sys.argv[2])
random.seed(seed)
print(4 * sum(random.random() ** 2 + random.random() ** 2 <= 1 for _ in range(n)) / n)
''')
add("bootstrap_mean_interval.py", "computes a bootstrap 95 percent interval for the mean of numbers in a file; input: path (one number per line), resamples, seed (argv[1:4]); output: 'lo hi' on stdout", '''
import random, sys
xs = [float(l) for l in open(sys.argv[1]) if l.strip()]
B, seed = int(sys.argv[2]), int(sys.argv[3])
random.seed(seed)
ms = sorted(sum(random.choices(xs, k=len(xs))) / len(xs) for _ in range(B))
print(ms[int(0.025 * B)], ms[int(0.975 * B) - 1])
''')
add("sort_algorithms_timing.py", "times insertion, merge and built-in sort on random lists of growing size; input: max size, seed (argv[1:3]); output: a table of seconds on stdout", '''
import random, sys, time
N, seed = int(sys.argv[1]), int(sys.argv[2])
random.seed(seed)
def ins(a):
    for i in range(1, len(a)):
        k, j = a[i], i - 1
        while j >= 0 and a[j] > k:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = k
def mer(a):
    if len(a) < 2:
        return a
    l, r = mer(a[:len(a) // 2]), mer(a[len(a) // 2:])
    o = []
    while l and r:
        o.append(l.pop(0) if l[0] <= r[0] else r.pop(0))
    return o + l + r
n = 100
while n <= N:
    a = [random.random() for _ in range(n)]
    row = []
    for f in (ins, mer, sorted):
        b = list(a)
        t = time.time()
        f(b)
        row.append(round(time.time() - t, 5))
    print(n, *row)
    n *= 2
''')
add("date_range_weekdays.py", "counts the weekdays between two dates, inclusive; input: two ISO dates (argv[1:3]); output: the count on stdout", '''
import datetime, sys
a, b = (datetime.date.fromisoformat(x) for x in sys.argv[1:3])
print(sum((a + datetime.timedelta(d)).weekday() < 5 for d in range((b - a).days + 1)))
''')
add("file_tree_size_report.py", "sums file sizes under a folder by extension; input: folder (argv[1]); output: lines 'bytes extension', largest first, on stdout", '''
import os, sys
from collections import Counter
c = Counter()
for r, _, fs in os.walk(sys.argv[1]):
    for f in fs:
        c[os.path.splitext(f)[1] or "(none)"] += os.path.getsize(os.path.join(r, f))
for e, n in c.most_common():
    print(n, e)
''')
add("duplicate_files_by_hash.py", "finds files with identical content under a folder by SHA-256; input: folder (argv[1]); output: groups of paths, one group per line, on stdout", '''
import hashlib, os, sys
g = {}
for r, _, fs in os.walk(sys.argv[1]):
    for f in fs:
        p = os.path.join(r, f)
        g.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), []).append(p)
for v in g.values():
    if len(v) > 1:
        print(*v)
''')
add("log_lines_error_rate.py", "computes the share of lines containing ERROR per hour in a timestamped log; input: log path with lines starting 'YYYY-MM-DD HH' (argv[1]); output: lines 'hour share' on stdout", '''
import sys
from collections import Counter
tot, err = Counter(), Counter()
for line in open(sys.argv[1]):
    h = line[:13]
    tot[h] += 1
    err[h] += "ERROR" in line
for h in sorted(tot):
    print(h, err[h] / tot[h])
''')
add("base_convert_numbers.py", "converts integers between bases 2 to 36; input: number string, from base, to base (argv[1:4]); output: the converted string on stdout", '''
import sys
n = int(sys.argv[1], int(sys.argv[2]))
b, d = int(sys.argv[3]), "0123456789abcdefghijklmnopqrstuvwxyz"
out = ""
while n:
    n, r = divmod(n, b)
    out = d[r] + out
print(out or "0")
''')
add("polynomial_roots_numeric.py", "finds the real roots of a polynomial by bisection on a grid; input: coefficients, highest degree first (argv), range -R..R as env R (default 10); output: the roots on stdout", '''
import os, sys
c = list(map(float, sys.argv[1:]))
R = float(os.environ.get("R", 10))
f = lambda x: sum(a * x ** (len(c) - 1 - i) for i, a in enumerate(c))
xs = [-R + i * R / 5000 for i in range(10001)]
for a, b in zip(xs, xs[1:]):
    if f(a) * f(b) < 0:
        for _ in range(60):
            m = (a + b) / 2
            a, b = (m, b) if f(a) * f(m) > 0 else (a, m)
        print(round(a, 9))
''')

COPIES = {
    "__reports__/reflective_run/w03/author-w03-2/list_tool_calls.py": ("list_tool_calls_of_session.py", "lists the tool calls of every transcript of one Claude Code session in time order with the start of each input; input: a session folder (its .jsonl beside it), optional width; output: lines on stdout"),
    "__reports__/reflective_run/w03/reproducer-w03-2/count_bash.py": ("count_bash_calls_in_transcripts.py", "counts Bash heredocs, inline Python and shell searches in Claude Code worker transcripts; input: a folder of worker .jsonl files; output: a table on stdout"),
    "__reports__/reflective_run/w03/author-w03-2/colgrep_scope_probe.py": ("colgrep_index_scope_probe.py", "lists which files of a sample lab colgrep indexes under each ignore setup; input: none (builds the lab in a temp folder); output: one table of file by setup"),
    "__reports__/reflective_run/w03/author-w03-2/ignore_effect_counts.py": ("count_files_before_after_ignore.py", "counts the files colgrep lists for a copy of a folder before and after an ignore block, by kind; input: two file lists; output: a JSON file"),
    "__reports__/reflective_run/w01/author-w01-3/bench.py": ("benchmark_session_finders.py", "times two ways of finding a lab's session transcripts and counts the lines of code each adds; input: the live ~/.claude/projects folder; output: a table on stdout"),
    "__reports__/reflective_run/w01/author-w01-3/compare.py": ("compare_lab_status_outputs.py", "compares what a human sees from two spend-reporting scripts on one lab; input: lab folders; output: text on stdout"),
    "__reports__/reflective_run/w01/author-w01-2/summarize.py": ("summarize_probe_results_jsonl.py", "summarises results.jsonl records of probe cells, last record per cell wins; input: results.jsonl in the working folder; output: group counts on stdout"),
    "__reports__/reflective_run/w01/author-w01-2/table.py": ("print_probe_cells_table.py", "prints one row per probe cell from a results.jsonl file with its cost in USD; input: results.jsonl path (argv[1]); output: a fixed-width table on stdout"),
}

if __name__ == "__main__":
    out = os.path.abspath(sys.argv[1])
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for name, text in S.items():
        with open(os.path.join(out, name), "w") as fh:
            fh.write(text)
    for src, (name, first) in COPIES.items():
        with open(os.path.join(ROOT, src)) as fh:
            body = fh.read()
        with open(os.path.join(out, name), "w") as fh:
            fh.write("# " + first + "\n" + body)
    print(len(os.listdir(out)), "scripts in", out)
    if len(sys.argv) > 2:                       # exploratory arm X: the same files under opaque names u01.py .. u46.py (first lines kept), mapping in opaque_names.json
        import json
        op = os.path.abspath(sys.argv[2])
        shutil.rmtree(op, ignore_errors=True)
        os.makedirs(op)
        names = {}
        for i, f in enumerate(sorted(os.listdir(out)), 1):
            names["u%02d.py" % i] = f
            shutil.copy(os.path.join(out, f), os.path.join(op, "u%02d.py" % i))
        json.dump(names, open(os.path.join(os.path.dirname(op), "opaque_names.json"), "w"), indent=1)
