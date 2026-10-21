## S-w06-reproducer-w06-4-1
The 20% line of s2 sits inside the machine noise: main's per-pair hook time ranges 4.2 s to 13.2 s, and the same SessionStart hooks take 0.5 s in one run and 2.3 s in another. Pair ratios run from 17.7% to 27.3% on builds that differ by a few commands. Pooled "fail" by 1 to 2 points on six or nine pairs is not a margin that more pairs would obviously settle; the pooled figure is also pulled down by one slow main run (`g_s2_main_0`). A quiet-machine rerun with n >= 8 pairs is what s2 needs.
refs: /private/tmp/murmuration-w06/author-w06-4/runs/{s2,f_s2,g_s2}_{main,new}_{0,1,2}/dbg.log; __instrumenta__/w06c4_repro_s2.py

## S-w06-reproducer-w06-4-2
The registered s4 says "production code" and "300 for the server", and the claim counted whole files, production lines of four files and the lab_status additions as three different numbers (+432, +320, +299, and +303 by my ast count). Which lines count was never fixed before the runs. The claim now gives both readings, but the title still states the fail.
refs: __instrumenta__/w06c4_repro_s4.py output on the two exports; __reports__/wave-06/00-experiment_protocol_v0.md line 74

## S-w06-reproducer-w06-4-3
v1's s3b has two clauses that say nearly the same thing ("no tool boundary waits more than 10 s in total, and no boundary waits more than 10 s in total over the whole outage"). The per-boundary reading passes at 6.0 s, the cumulative one fails at 12 to 18 s. The author read the weaker one first and said so only after my question. The PI should settle which was meant before reading E1 as a result.
refs: __reports__/wave-06/00-experiment_protocol_v1.md s3b; /private/tmp/murmuration-w06/author-w06-4/runs/{g_c0,out2_c0,out2_c1,f_c0,f_c1}/dbg.log

## S-w06-reproducer-w06-4-4
In the (b) runs the PI itself kills the server in step 2 of the prompt, so the "Hooks down" notice tells it what it already did. The PI's own answers (g_b0 line 77, g_b1 line 84) quote the notice, but a PI that does not know why hooks fail (the real case) is only tested by g_mid1, one run. The mid-run PI notice also arrives at the Agent call's return, which is after the worker's hand-back for a foreground worker.
refs: /private/tmp/murmuration-w06/author-w06-4/runs/{g_b0,g_b1,g_mid1}; __instrumenta__/w06c4_repro_s3.py

## S-w06-reproducer-w06-4-5
The revert at b79e81c restores hooks, scripts and `.mcp.json` to 134e3ac exactly, but `agents/*.md` and two skill references on the branch still differ from 134e3ac (guardrail commit b200173, not from this build). Anyone reading "the plugin is back at 134e3ac" should know the diff is not empty outside hooks/scripts.
refs: `git diff --stat 134e3ac HEAD -- agents skills`
