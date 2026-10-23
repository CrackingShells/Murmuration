## S-w08-reproducer-w08-14-1
`bash +c 'cmd'`, `sh +lc 'cmd'` run the string in bash 3.2, sh, zsh and dash (the shells ignore the sign for `c`), yet the guard reads only `-` words as setting -c. The claim's scope says "`-c` under `+c`" is not covered; unclear whether that meant this form. Why does the reader test `t[0] == "-"`?
refs: /private/tmp/murmuration-w08/reproducer-w08-14/real3.json (95 `+c` rows), holes.json kind gap shapes plus_c, plus_lc, l_plus_c

## S-w08-reproducer-w08-14-2
zsh `-O` does not take a value (`zsh -O noglob -c ...` fails to open `noglob`, `zsh -O -lc 'echo S1'` runs S1), ksh `-oc` does not take the next word as value; the guard follows bash. Both leave `zsh -Oc 'claude ... --bare'`-type forms allowed. Is the exotic form worth the fix? No real claude was run.
refs: /private/tmp/murmuration-w08/reproducer-w08-14/real3.json (zsh 74, ksh 53 non-plus rows), real2.json

## S-w08-reproducer-w08-14-3
In the frozen set the 19 true-labelled cases still allowed are untouched by this claim (indirect program or file); the claim's (b) can only show "nothing moved". Mine agrees (178/197 both sides).
refs: /private/tmp/murmuration-w08/reproducer-w08-14/frozen.log

## S-w08-reproducer-w08-14-4
My first timing harness labelled every Python row "deny" (the snippet prints a word, my label treated any output as deny); fixed in w08_v14_time.py. The 300 KB-word `bash -lc` Python time doubles (0.92 -> 1.81 s) because the string is expanded now; not a defect, but unmentioned in the claim (the claim holds no timing figure for this change).
refs: /private/tmp/murmuration-w08/reproducer-w08-14/time.log
