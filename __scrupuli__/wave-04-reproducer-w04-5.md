## S-w04-reproducer-w04-5-1
The gate that makes the main-thread hook free reads its stdin one byte at a time when stdin is a pipe or socket (bash and dash `read`), and the platform gives hooks a socket. Its cost grows by about 0.27 ms per KB of payload, so a main-thread PostToolUse that carries a 300 KB tool_response is slower than the old Python (ratio 1.41). The claim measured 1 to 3 KB payloads from a file-fed timer, so neither the pipe behaviour nor the size dependence could show. `p=$(cat)` removes the growth but costs about 10 ms at small sizes on this machine (cat's own start), so it is not an obvious fix. What is the real distribution of payload sizes in a worker's PostToolBatch (a batch holds every call's tool_response)? I only had the transcripts, which store large outputs truncated.
refs: __reports__/reflective_run/w04/reproducer-w04-5/timing_sock_pad{0,30000,100000,300000}.txt; __instrumenta__/w04c5_gate_probe.py, w04c5_gate_variants.py, w04c5_payload_size_dist.py; headless probe in /private/tmp/murmuration-w04/reproducer-w04-5/hl/stdin_kind.txt (PostToolUse sock 31400)

## S-w04-reproducer-w04-5-2
The E4 long-worker figure moves with machine load and with how the long transcript is held: 0.50 when the transcript grows by one request between pairs, 0.52 to 0.54 when it is static, and the author's five runs ran from 0.47 to 0.60. The fixed part of a start (sh plus python -S -I, about 54 ms) sets the floor: new cannot go under 0.5 of an old that costs 105 ms. The criterion is a ratio, so it depends on how slow the old code was on the day; was a 50% ratio ever a sensible test of leanness rather than a statement about absolute milliseconds saved (about 50 per start, 100 per tool call)?
refs: __reports__/reflective_run/w04/reproducer-w04-5/timing_static_11.txt, timing_grow_12.txt, timing_static_13.txt, pairs_*.jsonl

## S-w04-reproducer-w04-5-3
The claim says PYTHONDONTWRITEBYTECODE=1 is set "in this Desktop environment" and that `-I` ignores it; true here, so the cache lives in the plugin folder because of -I. But the Desktop-run hooks of the platform may not inherit that variable at all; what do hooks see? My timing used my own environment (variable set), so the "noSI" ablation (1.35x on the long worker) mixes the effect of -S -I with the loss of the cache (1.23x with a pre-written cache). I do not know whether the platform's own hook environment has the variable.
refs: __reports__/reflective_run/w04/reproducer-w04-5/abl_noSI.txt, abl_noSI_cached.txt, abl_nopyc.txt; /private/tmp/murmuration-w04/reproducer-w04-5/pyc

## S-w04-reproducer-w04-5-4
Replay: I rebuilt 197 transcripts where the claim has 291 (44 + 247). The rule in the claim text ("every agent-*.jsonl with a murmuration:* .meta.json under -private-tmp-*w02*, -private-tmp-*w03*, the scratchpad dirs of wave 2 and the design session") gave me 197, 138 of which are the design session including wave-4 workers that did not exist at the claim's date. The list file is not committed. I could not tell which 94 of the author's transcripts I lack.
refs: /private/tmp/murmuration-w04/reproducer-w04-5/list.txt, replay_full.txt

## S-w04-reproducer-w04-5-5
I printed my whole process environment by mistake (`env $mode` where $mode began with a variable assignment, in a loop meant to test PYTHONDONTWRITEBYTECODE) and it came back with API keys of a local gateway in clear (RIVAULT_* variables) in my own tool output. Nothing was written to a file or to git, but the tool result sits in this transcript. The sandbox does not scrub such variables from agents' environments. Worth a note for the PI: any agent that runs `env` leaks them into its transcript, and transcripts are read by other agents.
refs: this agent's own transcript (no artifact written)

## S-w04-reproducer-w04-5-6
The header of hook_replay_equiv.py says the replay leaves out "the `python3 -S -I -B` flags of hooks.json", the commit message says "no -B", the claim text says `-S -I`, and hooks.json has `-S -I`. Stale text only, but it is the kind that makes a reader doubt which version was measured.
refs: __instrumenta__/hook_replay_equiv.py line 11; hooks/hooks.json
