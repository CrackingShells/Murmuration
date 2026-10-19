## S-w03-reproducer-w03-2-1
The `.ignore` block was chosen to clean the colgrep index, and it also makes Claude Code's Grep (ripgrep) blind to the same paths. Without a path argument Grep returned 2 of 9 files holding the needle; `path` set to the ignored folder, or `glob: "*.json"`, finds them again; `type: "json"` and `glob: "**/raw/*"` do not. On this machine Grep is denied by the colgrep-mcp hook, so the working route to those files is Glob plus Read, with no content search. I do not know how often a worker needs to search inside `*.json` or `*.txt` results; a result table saved as `.json` is common in this study's reports (the author's own `colgrep_scope_probe.json` is hidden by the block).
refs: __reports__/reflective_run/w03/reproducer-w03-2/ignore_probe_1.txt, ignore_probe_2.txt, ignore_probe_3.txt

## S-w03-reproducer-w03-2-2
The block's `*.json` and `*.txt` also hide `package.json`, `requirements.txt`, `CMakeLists.txt` and the like when `/lab` runs inside an existing code project, and the `.ignore` file itself is a new untracked file at that project's root (not in `.gitignore`). I did not test a lab created in a real code repository.
refs: scripts/lab_init.py (IGNORE_BLOCK, ensure_ignore)

## S-w03-reproducer-w03-2-3
The author's `list`-type table row "of those: writing a file / appending / running inline Python = 222 / 75 / 715" sums to 1,012 against 967 heredocs: the categories overlap. My exclusive split is 190 / 59 / 718. Nothing in the claim depends on it, but a reader adding the row would find 45 calls too many.
refs: __reports__/reflective_run/w03/author-w03-2/baseline.json; __reports__/reflective_run/w03/reproducer-w03-2/baseline_40_counts.txt

## S-w03-reproducer-w03-2-4
In the same-question runs the explorer and the author each computed the same quantity (exhaustive maximum of distinct substrings) in two scripts, `substring_max.py` and `check_w01c1.py`. They started in parallel and both `ls`ed an empty `__instrumenta__/`, so no search could have found the other's script. The reuse rule has no case to act on when workers start at the same moment; reuse needs a later wave or a sequential start. The control arm shows the same duplication (`enum.py`, `check.py`).
refs: /tmp/author-w03-2/lab1/__instrumenta__/; __reports__/reflective_run/w03/reproducer-w03-2/run1_workers_counts.txt, control_workers_counts.txt

## S-w03-reproducer-w03-2-5
The proof-adversary's file says to write one's own check in code that does not import the author's, and the reproducer's file says to run or read the author's instruments. Both now sit with a folder that holds the author's scripts: an independent check placed next to the code it checks. I did not find whether that has cost independence in practice; in this run the proof-adversary did not look in the folder.
refs: agents/proof-adversary.md, agents/reproducer.md

## S-w03-reproducer-w03-2-6
Each headless `claude -p` result record in my control run repeated the same `total_cost_usd` (1.500232) for the lead and for each of the three workers (four `result` lines). I took it as one session total, not as a per-agent figure. I did not check it against `/lab-status`.
refs: /tmp/reproducer-w03-2/base_run.jsonl (raw, not kept in git)

## S-w03-reproducer-w03-2-7
`lab_init.py` prints "built the colgrep index" when `colgrep init -y` exits 0, including when the lab folded into a parent's existing index and no new index exists. The line says nothing about which index was used.
refs: scripts/lab_init.py (build_index); /tmp/reproducer-w03-2/parent (fold-in test), `colgrep status` output "Subdirectory: lab"
