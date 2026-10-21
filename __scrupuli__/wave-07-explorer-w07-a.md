## S-w07-explorer-w07-a-1
A binary killed by the kernel at exec (copy of `/bin/sh`, rc 137, 0.03 ms CPU) takes 13.6 ms, an unsigned image 0.1 ms, a normal exec 16 ms. Something between image activation and the signature verdict costs 13 ms of wall, not CPU, and opendirectoryd burns ~11 ms CPU per exec but not per fork. Is it Falcon (installed ES extension), AMFI or syspolicyd? I could not separate them without root. The same bench on a machine without Falcon would say whether "language does not matter" is this machine's fact or the platform's.
refs: `__reports__/wave-07/explorer-w07-a/spawn3_table.md`, `daemon_cpu.md`, `daemon_cpu_fork_vs_exec.md`

## S-w07-explorer-w07-a-2
First exec of a freshly linked binary costs 330 ms (24 of 24, C and Rust alike), against 26 ms for the next. What is in the 330 ms (syspolicyd assessment, Falcon file analysis, XProtect)? Does it recur per path, per cdhash, per boot, and does a binary extracted from a plugin git checkout pay it on every user's machine and after every update?
refs: `__reports__/wave-07/explorer-w07-a/fresh_table.md`, `fresh2_rows.jsonl`

## S-w07-explorer-w07-a-3
The platform's recorded hook durations equal the time to the hook's `main()` (0 to 1 ms after), and the platform issued the spawn within 1 to 9 ms of the debug line before it; but the hook's recorded medians under load run 1.5 to 2.2 times the minima and the unpaired variant order is not that of the exec count (`:` 52 ms vs `: #b` with `"shell":"bash"` 66; `exec c_noop` 86 vs plain `c_noop` 96). Also, the model produced up to 3 times the requested Read calls in session 2, so the design needs a paired, model-free driver. Is there a way to fire a command hook without a model turn (SessionStart repeated by `--resume`?), to get paired platform numbers?
refs: `__reports__/wave-07/explorer-w07-a/table2b.md`, `rows2b.jsonl`, `rows1.jsonl`
