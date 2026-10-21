# writes the 300-plus helper scripts of the E3b test lab (the 46 of E3 plus generated families of sequences, digit predicates, string tools, base conversions, statistics, matrices and unit conversions, each with its own descriptive name and first line); input: OUTDIR (argv[1]); output: the scripts in OUTDIR and the count
"""usage: python3 -I e3b_make_lab_scripts.py OUTDIR

The 46 scripts of E3 (`e3_make_lab_scripts.py`, including the fit `binary_max_distinct_substrings_bruteforce.py` and the near fit
`collatz_longest_stopping_time.py`) come first; the rest are generated from templates and checked to compile.  Stdlib only; no seeds.
"""
import ast
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[1])
subprocess.run([sys.executable, "-I", os.path.join(HERE, "e3_make_lab_scripts.py"), out], check=True, capture_output=True)
G = {}


def add(name, first, body):
    assert name not in G and not os.path.exists(os.path.join(out, name)), name
    G[name] = "# " + first + "\n" + body.strip("\n") + "\n"


# A. sequences given by a closed form in n
SEQ = [
    ("triangular", "n*(n+1)//2"), ("square", "n*n"), ("cube", "n**3"), ("pentagonal", "n*(3*n-1)//2"), ("hexagonal", "n*(2*n-1)"),
    ("heptagonal", "n*(5*n-3)//2"), ("octagonal", "n*(3*n-2)"), ("centered_square", "2*n*(n+1)+1"), ("centered_hexagonal", "3*n*(n+1)+1"),
    ("pronic", "n*(n+1)"), ("tetrahedral", "n*(n+1)*(n+2)//6"), ("pentatope", "n*(n+1)*(n+2)*(n+3)//24"), ("star", "6*n*(n-1)+1"),
    ("fourth_power", "n**4"), ("fifth_power", "n**5"), ("power_of_two", "2**n"), ("power_of_three", "3**n"), ("power_of_five", "5**n"),
    ("power_of_seven", "7**n"), ("mersenne", "2**n-1"), ("cullen", "n*2**n+1"), ("woodall", "n*2**n-1"), ("factorial", "__import__('math').factorial(n)"),
    ("central_binomial", "__import__('math').comb(2*n,n)"), ("catalan", "__import__('math').comb(2*n,n)//(n+1)"),
    ("odd_number", "2*n+1"), ("even_number", "2*n"), ("multiple_of_seven", "7*n"), ("multiple_of_eleven", "11*n"),
    ("square_pyramidal", "n*(n+1)*(2*n+1)//6"), ("octahedral", "n*(2*n*n+1)//3"), ("dodecahedral", "n*(3*n-1)*(3*n-2)//2"),
    ("icosahedral", "n*(5*n*n-5*n+2)//2"), ("stella_octangula", "n*(2*n*n-1)"), ("cubic_centered", "n**3+(n+1)**3"),
    ("sum_of_first_n_cubes", "(n*(n+1)//2)**2"), ("sum_of_first_n_odd_cubes", "n*n*(2*n*n-1)"), ("n_to_the_n", "n**n"),
    ("bell_triangle_row_sum", "sum(__import__('math').comb(n,k) for k in range(n+1))"), ("number_of_subsets_of_size_two", "n*(n-1)//2"),
    ("number_of_diagonals_of_polygon", "n*(n-3)//2"), ("number_of_handshakes", "n*(n-1)//2"), ("lazy_caterer", "n*(n+1)//2+1"),
    ("cake_numbers", "(n**3+5*n+6)//6"), ("magic_constant", "n*(n*n+1)//2"), ("gnomon", "2*n-1"), ("hex_number_centered", "3*n*n-3*n+1"),
    ("difference_of_squares_consecutive", "(n+1)**2-n**2"), ("harmonic_denominator_lcm", "__import__('math').lcm(*range(1,n+1))"),
    ("primorial_like_product_of_first_n_integers_plus_one", "__import__('math').factorial(n)+1"), ("double_factorial", "__import__('math').prod(range(n,0,-2))"),
]
for slug, expr in SEQ:
    add("sequence_%s_numbers_table.py" % slug, "prints the first N terms of the %s sequence a(n) = %s, n from 1; input: N (argv[1], default 20); output: lines 'n a(n)' on stdout" % (slug.replace("_", " "), expr.replace("__import__('math').", "math.")), '''
import sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for n in range(1, N + 1):
    print(n, %s)
''' % expr)
# A2. linear recurrences
REC = [("fibonacci", [0, 1], "a[-1]+a[-2]"), ("lucas", [2, 1], "a[-1]+a[-2]"), ("pell", [0, 1], "2*a[-1]+a[-2]"), ("jacobsthal", [0, 1], "a[-1]+2*a[-2]"),
       ("padovan", [1, 1, 1], "a[-2]+a[-3]"), ("perrin", [3, 0, 2], "a[-2]+a[-3]"), ("tribonacci", [0, 0, 1], "a[-1]+a[-2]+a[-3]"),
       ("tetranacci", [0, 0, 0, 1], "a[-1]+a[-2]+a[-3]+a[-4]"), ("leonardo", [1, 1], "a[-1]+a[-2]+1"), ("pell_lucas", [2, 2], "2*a[-1]+a[-2]"),
       ("narayana_cows", [1, 1, 1], "a[-1]+a[-3]"), ("fibonacci_like_three_one", [3, 1], "a[-1]+a[-2]"), ("doubling_plus_one", [0], "2*a[-1]+1"),
       ("tripling_minus_one", [1], "3*a[-1]-1"), ("quadrupling_with_alternating_sign", [1, 1], "4*a[-1]-a[-2]")]
for slug, init, rule in REC:
    add("sequence_%s_by_recurrence.py" % slug, "prints the first N terms of the %s sequence from its recurrence a(n) = %s with start %s; input: N (argv[1], default 20); output: lines 'index value' on stdout" % (slug.replace("_", " "), rule, init), '''
import sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
a = %s
while len(a) < N:
    a.append(%s)
for i, v in enumerate(a[:N]):
    print(i, v)
''' % (init, rule))
# B. digit and divisor predicates: count and list
PRED = [
    ("palindromic", "str(n)==str(n)[::-1]"), ("prime", "isp(n)"), ("semiprime", "sum(f(n).values())==2"), ("square_free", "all(e==1 for e in f(n).values())"),
    ("perfect_square", "int(n**0.5)**2==n"), ("perfect_cube", "round(n**(1/3))**3==n"), ("power_of_two", "n&(n-1)==0"),
    ("abundant", "sigma(n)>2*n"), ("deficient", "sigma(n)<2*n"), ("harshad", "n%ds(n)==0"), ("even_digit_sum", "ds(n)%2==0"), ("odd_digit_sum", "ds(n)%2==1"),
    ("all_digits_odd", "all(int(c)%2 for c in str(n))"), ("all_digits_even", "all(int(c)%2==0 for c in str(n))"), ("containing_digit_seven", "'7' in str(n)"),
    ("without_digit_zero", "'0' not in str(n)"), ("repdigit", "len(set(str(n)))==1"), ("strictly_increasing_digits", "list(str(n))==sorted(set(str(n)))"),
    ("twin_prime_lower", "isp(n) and isp(n+2)"), ("sophie_germain", "isp(n) and isp(2*n+1)"), ("divisible_by_three_or_five", "n%3==0 or n%5==0"),
    ("with_exactly_four_divisors", "sum(1 for d in range(1,n+1) if n%d==0)==4"), ("with_digit_product_zero", "'0' in str(n)"),
    ("whose_digit_sum_is_prime", "isp(ds(n))"), ("of_the_form_four_k_plus_one", "n%4==1"), ("squares_plus_one_prime", "isp(n*n+1)"),
    ("with_prime_number_of_divisors", "isp(sum(1 for d in range(1,n+1) if n%d==0))"), ("triangular", "int((8*n+1)**0.5)**2==8*n+1"),
    ("with_digits_summing_to_ten", "ds(n)==10"), ("with_three_digits_or_fewer", "n<1000"),
    ("whose_square_is_a_palindrome", "str(n*n)==str(n*n)[::-1]"), ("congruent_to_two_modulo_seven", "n%7==2"), ("whose_reversal_is_prime", "isp(int(str(n)[::-1]))"),
    ("with_an_even_number_of_prime_factors_with_multiplicity", "sum(f(n).values())%2==0"), ("with_at_most_two_distinct_digits", "len(set(str(n)))<=2"),
    ("that_are_sums_of_two_squares", "any(int((n-a*a)**0.5)**2==n-a*a for a in range(int(n**0.5)+1))"), ("with_a_digit_equal_to_the_digit_count", "str(len(str(n))) in str(n)"),
    ("coprime_to_twelve", "__import__('math').gcd(n,12)==1"), ("whose_last_digit_is_three", "n%10==3"), ("with_first_digit_one", "str(n)[0]=='1'"),
    ("that_are_multiples_of_their_digit_sum_and_even", "n%ds(n)==0 and n%2==0"), ("whose_binary_form_is_a_palindrome", "bin(n)[2:]==bin(n)[2:][::-1]"),
]
HELP = '''
import sys
N = int(sys.argv[1])
def isp(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
def ds(n):
    return sum(map(int, str(n)))
def sigma(n):
    return sum(d for d in range(1, n + 1) if n % d == 0)
def f(n):
    r, d = {}, 2
    while n > 1:
        while n % d == 0:
            r[d] = r.get(d, 0) + 1
            n //= d
        d += 1
    return r
'''
for slug, pr in PRED:
    nice = slug.replace("_", " ")
    add("count_integers_%s_up_to_N.py" % slug, "counts the integers from 1 to N that are %s; input: N (argv[1]); output: the count on stdout" % nice,
        HELP + "print(sum(1 for n in range(1, N + 1) if %s))\n" % pr)
    add("list_first_K_integers_%s.py" % slug, "lists the first K positive integers that are %s; input: K (argv[1]); output: the integers, space separated, on stdout" % nice,
        HELP.replace("N = int(sys.argv[1])", "K = int(sys.argv[1])") + "out, n = [], 0\nwhile len(out) < K:\n    n += 1\n    if %s:\n        out.append(n)\nprint(*out)\n" % pr)
# C. string tools
STR = [
    ("reverse", "s[::-1]", "the string reversed"), ("upper_case", "s.upper()", "the string in upper case"), ("lower_case", "s.lower()", "the string in lower case"),
    ("swap_case", "s.swapcase()", "the string with the case of each letter swapped"), ("sorted_letters", "''.join(sorted(s))", "the characters in sorted order"),
    ("unique_characters_in_order", "''.join(dict.fromkeys(s))", "the characters without repeats, in first-seen order"),
    ("vowel_count", "sum(c in 'aeiouAEIOU' for c in s)", "the number of vowels"), ("consonant_count", "sum(c.isalpha() and c not in 'aeiouAEIOU' for c in s)", "the number of consonants"),
    ("word_count", "len(s.split())", "the number of words"), ("character_count_without_spaces", "len(s.replace(' ', ''))", "the number of characters that are not spaces"),
    ("longest_word", "max(s.split(), key=len)", "the longest word"), ("title_case", "s.title()", "the string in title case"), ("remove_spaces", "s.replace(' ', '')", "the string without spaces"),
    ("remove_digits", "''.join(c for c in s if not c.isdigit())", "the string without digits"), ("rot13", "__import__('codecs').encode(s, 'rot13')", "the ROT13 transform of the string"),
    ("ascii_codes", "' '.join(str(ord(c)) for c in s)", "the character codes"), ("binary_of_characters", "' '.join(format(ord(c), '08b') for c in s)", "the 8-bit binary form of each character"),
    ("hex_of_characters", "' '.join(format(ord(c), '02x') for c in s)", "the hexadecimal form of each character"),
    ("run_length_encoding", "''.join(str(len(list(g)))+k for k, g in __import__('itertools').groupby(s))", "the run-length encoding"),
    ("first_repeated_character", "next((c for i, c in enumerate(s) if c in s[:i]), 'none')", "the first character that occurs twice"),
    ("is_pangram", "set('abcdefghijklmnopqrstuvwxyz') <= set(s.lower())", "whether it uses every letter of the alphabet"),
    ("is_isogram", "len(set(s.lower())) == len(s)", "whether no character repeats"), ("count_uppercase_letters", "sum(c.isupper() for c in s)", "the number of upper-case letters"),
    ("most_common_character", "__import__('collections').Counter(s).most_common(1)[0]", "the most common character and its count"),
    ("distinct_word_count", "len(set(s.lower().split()))", "the number of distinct words"), ("capitalize_each_sentence", "'. '.join(x.strip().capitalize() for x in s.split('.'))", "the string with each sentence capitalised"),
    ("acronym", "''.join(w[0].upper() for w in s.split())", "the acronym of the words"), ("camel_case_to_snake_case", "__import__('re').sub(r'(?<!^)(?=[A-Z])', '_', s).lower()", "the snake_case form of a camelCase name"),
    ("snake_case_to_camel_case", "''.join(w.title() if i else w for i, w in enumerate(s.split('_')))", "the camelCase form of a snake_case name"),
    ("number_of_palindromic_substrings", "sum(s[i:j]==s[i:j][::-1] for i in range(len(s)) for j in range(i+1, len(s)+1))", "the number of palindromic substrings (with positions)"),
    ("number_of_distinct_substrings_of_one_string", "len({s[i:j] for i in range(len(s)) for j in range(i+1, len(s)+1)})", "the number of distinct non-empty substrings of this one string"),
    ("longest_common_prefix_of_words", "__import__('os').path.commonprefix(s.split())", "the longest common prefix of its words"),
    ("is_balanced_brackets", "(lambda t: all(t.count(a)==t.count(b) for a,b in ('()','[]','{}')))(s)", "whether the brackets are balanced by count"),
    ("number_of_words_longer_than_five_letters", "sum(len(w)>5 for w in s.split())", "the number of words longer than five letters"),
    ("characters_that_appear_exactly_once", "''.join(c for c in s if s.count(c)==1)", "the characters that appear exactly once"),
    ("words_in_reverse_order", "' '.join(s.split()[::-1])", "the words in reverse order"), ("each_word_reversed_in_place", "' '.join(w[::-1] for w in s.split())", "each word reversed in place"),
    ("length_of_the_longest_run_of_equal_characters", "max(len(list(g)) for _, g in __import__('itertools').groupby(s))", "the length of the longest run of equal characters"),
    ("positions_of_every_space", "[i for i, c in enumerate(s) if c == ' ']", "the positions of every space"), ("characters_sorted_by_frequency", "''.join(c for c, _ in __import__('collections').Counter(s).most_common())", "the characters sorted by decreasing frequency"),
    ("is_a_valid_binary_string", "set(s) <= set('01')", "whether it is made of 0 and 1 only"), ("count_of_ones_in_a_binary_string", "s.count('1')", "the number of ones in a binary string"),
    ("binary_string_complement", "''.join('1' if c=='0' else '0' for c in s)", "the complement of a binary string"), ("binary_string_value_as_integer", "int(s, 2)", "the integer value of a binary string"),
    ("number_of_zero_runs_in_binary_string", "len([r for r in s.split('1') if r])", "the number of runs of zeros in a binary string"),
    ("number_of_distinct_letters", "len(set(c for c in s.lower() if c.isalpha()))", "the number of distinct letters"),
    ("the_string_repeated_three_times_with_dashes", "'-'.join([s]*3)", "the string three times, joined with dashes"), ("the_middle_character_or_characters", "s[(len(s)-1)//2:len(s)//2+1]", "the middle character or characters"),
    ("digits_only", "''.join(c for c in s if c.isdigit())", "the digits only"), ("letters_only", "''.join(c for c in s if c.isalpha())", "the letters only"),
    ("sum_of_digits_in_string", "sum(int(c) for c in s if c.isdigit())", "the sum of its digits"), ("zigzag_case", "''.join(c.upper() if i%2 else c.lower() for i, c in enumerate(s))", "the string in alternating case"),
]
for slug, expr, what in STR:
    add("string_%s.py" % slug, "computes %s of a string; input: the string (argv[1]); output: the result on stdout" % what, "import sys\ns = sys.argv[1]\nprint(%s)\n" % expr)
# D. base conversions
for b in range(2, 17):
    add("digit_sum_of_N_in_base_%d.py" % b, "computes the sum of the digits of an integer written in base %d; input: N (argv[1]); output: the sum on stdout" % b,
        "import sys\nn, s = int(sys.argv[1]), 0\nwhile n:\n    s += n %% %d\n    n //= %d\nprint(s)\n" % (b, b))
    add("write_N_in_base_%d.py" % b, "writes an integer in base %d; input: N (argv[1]); output: its digits (letters above 9) on stdout" % b,
        "import sys\nn, d, o = int(sys.argv[1]), '0123456789abcdef', ''\nwhile n:\n    o = d[n %% %d] + o\n    n //= %d\nprint(o or '0')\n" % (b, b))
for slug, pr in PRED:
    nice = slug.replace("_", " ")
    add("sum_of_the_integers_%s_up_to_N.py" % slug, "adds up the integers from 1 to N that are %s; input: N (argv[1]); output: the sum on stdout" % nice,
        HELP + "print(sum(n for n in range(1, N + 1) if %s))\n" % pr)
for slug, expr in SEQ:
    add("sequence_%s_numbers_partial_sums.py" % slug, "prints the partial sums of the first N terms of the %s sequence a(n) = %s; input: N (argv[1], default 20); output: lines 'n partial_sum' on stdout" % (slug.replace("_", " "), expr.replace("__import__('math').", "math.")), '''
import sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
t = 0
for n in range(1, N + 1):
    t += %s
    print(n, t)
''' % expr)
# E. conversions
CONV = [("celsius_to_fahrenheit", "x*9/5+32"), ("fahrenheit_to_celsius", "(x-32)*5/9"), ("kilometres_to_miles", "x*0.621371"), ("miles_to_kilometres", "x/0.621371"),
        ("kilograms_to_pounds", "x*2.20462"), ("pounds_to_kilograms", "x/2.20462"), ("litres_to_gallons", "x*0.264172"), ("degrees_to_radians", "x*3.141592653589793/180"),
        ("radians_to_degrees", "x*180/3.141592653589793"), ("seconds_to_hours", "x/3600"), ("hours_to_seconds", "x*3600"), ("metres_to_feet", "x*3.28084"),
        ("feet_to_metres", "x/3.28084"), ("bytes_to_mebibytes", "x/2**20"), ("kelvin_to_celsius", "x-273.15"), ("area_of_circle_from_radius", "3.141592653589793*x*x"),
        ("circumference_from_radius", "2*3.141592653589793*x"), ("volume_of_sphere_from_radius", "4/3*3.141592653589793*x**3"), ("compound_interest_factor_ten_years_at_rate_percent", "(1+x/100)**10"),
        ("body_mass_index_from_kg_and_height_m_ratio", "x")]
for slug, expr in CONV:
    add("convert_%s.py" % slug, "converts a number, %s; input: the number x (argv[1]); output: the result on stdout" % slug.replace("_", " "), "import sys\nx = float(sys.argv[1])\nprint(%s)\n" % expr)
# F. statistics of a file of numbers
STAT = [("mean", "statistics.mean(x)"), ("median", "statistics.median(x)"), ("mode", "statistics.mode(x)"), ("population_variance", "statistics.pvariance(x)"),
        ("sample_standard_deviation", "statistics.stdev(x)"), ("minimum", "min(x)"), ("maximum", "max(x)"), ("range", "max(x)-min(x)"), ("sum", "sum(x)"),
        ("product", "math.prod(x)"), ("geometric_mean", "statistics.geometric_mean(x)"), ("harmonic_mean", "statistics.harmonic_mean(x)"),
        ("interquartile_range", "statistics.quantiles(x, n=4)[2]-statistics.quantiles(x, n=4)[0]"), ("coefficient_of_variation", "statistics.pstdev(x)/statistics.mean(x)"),
        ("number_of_values_above_the_mean", "sum(v>statistics.mean(x) for v in x)"), ("cumulative_sums", "list(itertools.accumulate(x))"),
        ("successive_differences", "[b-a for a,b in zip(x,x[1:])]"), ("z_scores", "[(v-statistics.mean(x))/statistics.pstdev(x) for v in x]"),
        ("sorted_descending", "sorted(x, reverse=True)"), ("number_of_distinct_values", "len(set(x))")]
for slug, expr in STAT:
    add("numbers_file_%s.py" % slug, "computes the %s of the numbers in a text file; input: path to a file with one number per line (argv[1]); output: the result on stdout" % slug.replace("_", " "),
        "import itertools, math, statistics, sys\nx = [float(l) for l in open(sys.argv[1]) if l.strip()]\nprint(%s)\n" % expr)
# G. matrices (JSON argv)
MAT = [("transpose", "[list(r) for r in zip(*A)]"), ("trace", "sum(A[i][i] for i in range(len(A)))"), ("row_sums", "[sum(r) for r in A]"), ("column_sums", "[sum(c) for c in zip(*A)]"),
       ("is_symmetric", "A == [list(r) for r in zip(*A)]"), ("main_diagonal", "[A[i][i] for i in range(len(A))]"), ("anti_diagonal", "[A[i][len(A)-1-i] for i in range(len(A))]"),
       ("maximum_entry", "max(max(r) for r in A)"), ("square_of_matrix", "[[sum(a*b for a,b in zip(r,c)) for c in zip(*A)] for r in A]"),
       ("flatten_row_major", "[v for r in A for v in r]"), ("is_identity", "A == [[int(i==j) for j in range(len(A))] for i in range(len(A))]"),
       ("frobenius_norm", "sum(v*v for r in A for v in r)**0.5")]
for slug, expr in MAT:
    add("matrix_%s.py" % slug, "computes the %s of a matrix; input: the matrix as JSON rows (argv[1]); output: the result on stdout" % slug.replace("_", " "), "import json, sys\nA = json.loads(sys.argv[1])\nprint(%s)\n" % expr)
# H. decoys near the two tasks
add("collatz_steps_of_one_start_value.py", "counts the steps a single start value takes to reach 1 under the Collatz rule; input: n (argv[1]); output: the step count on stdout", "import sys\nn, k = int(sys.argv[1]), 0\nwhile n != 1:\n    n = n // 2 if n % 2 == 0 else 3 * n + 1\n    k += 1\nprint(k)\n")
add("collatz_stopping_time_histogram.py", "tabulates how many start values up to LIMIT take each number of Collatz steps; input: LIMIT (argv[1]); output: lines 'steps count' on stdout", "import sys\nfrom collections import Counter\nc = Counter()\nfor s in range(1, int(sys.argv[1]) + 1):\n    n, k = s, 0\n    while n != 1:\n        n = n // 2 if n % 2 == 0 else 3 * n + 1\n        k += 1\n    c[k] += 1\nfor k in sorted(c):\n    print(k, c[k])\n")
add("collatz_odd_steps_only_count.py", "counts only the 3n+1 steps of the Collatz trajectory of one start value; input: n (argv[1]); output: the count on stdout", "import sys\nn, k = int(sys.argv[1]), 0\nwhile n != 1:\n    if n % 2:\n        k += 1\n        n = 3 * n + 1\n    else:\n        n //= 2\nprint(k)\n")
add("distinct_substrings_of_all_binary_strings_histogram.py", "tabulates, for binary strings of length n, how many strings have each count of distinct non-empty substrings; input: n (argv[1]); output: lines 'distinct count' on stdout", "import sys\nfrom collections import Counter\nfrom itertools import product\nn = int(sys.argv[1])\nc = Counter(len({s[i:j] for i in range(n) for j in range(i + 1, n + 1)}) for s in map(''.join, product('01', repeat=n)))\nfor d in sorted(c):\n    print(d, c[d])\n")
add("binary_strings_avoiding_a_pattern_count.py", "counts binary strings of length n that do not contain a given pattern; input: n, pattern (argv[1:3]); output: the count on stdout", "import sys\nfrom itertools import product\nn, p = int(sys.argv[1]), sys.argv[2]\nprint(sum(p not in ''.join(s) for s in product('01', repeat=n)))\n")
add("ternary_strings_with_all_letters_count.py", "counts strings over a three-letter alphabet of length n that use all three letters; input: n (argv[1]); output: the count on stdout", "import sys\nn = int(sys.argv[1])\nprint(3**n - 3*2**n + 3)\n")

for name, text in G.items():
    ast.parse(text)
    with open(os.path.join(out, name), "w") as fh:
        fh.write(text)
names = sorted(os.listdir(out))
ls_chars = sum(len(n) + 1 for n in names)
print(len(names), "scripts in", out, "; ls -1 is", ls_chars, "characters")
