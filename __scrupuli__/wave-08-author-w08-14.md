## S-w08-author-w08-14-1
The frozen set of explorer-w08-j holds no `bash -lc`-type case, so its 739 cases cannot show the new forms are denied; (b) only shows that nothing else moved (0 newly denied, 0 newly allowed on 739 and on 10,634 recorded calls). The recorded calls do not hold one either: the hole was never used in the lab's own traffic, so its reach is only what the generated cases show.
refs: __reports__/wave-08/author-w08-14/frozen_compare.md, recorded_diff.txt

## S-w08-author-w08-14-2
My first run of the cases counted 5 nested cases (`bash -c 'bash -Cc ...'`) whose "plain" form was allowed on the base, because the plain reference itself held a combined cluster; the metamorphic law needs the reference to be the fully plain form (`bash -c 'bash -c ...'`). Fixed in w08_c14_cases.py (`plain` per case). A check built on "plain form denied" can silently shrink when the reference carries the same hole.
refs: __instrumenta__/w08_c14_cases.py (nested shape), __reports__/wave-08/author-w08-14/cases_base.txt

## S-w08-author-w08-14-3
The full case run (36,280 cases, one Rust process per case) took about 25 min wall when run beside check_guard_equal, against 20 s for the quick subset (907 cases, which scales to about 13 min): the Rust per-process start dominates. A batch mode of `murmuration guard` (many events per process) would make every hole-case run of waves 6-8 cheaper; not built, not in scope.
refs: __reports__/wave-08/author-w08-14/cases_new.txt

## S-w08-author-w08-14-4
Option semantics were taken from the bash manual, not run (a real `bash -eoc pipefail 'x'` was not tried here, and the live guard blocks running such forms with a flag anyway). If bash read `-oc` differently, the guard still reads both the old and the new string, so a wrong guess can only add denials, but an ordinary `bash -oc ...` string could then be read as a command that is not run; no case of this kind appeared in the controls.
refs: __instrumenta__/w08_c14_cases.py OUTERS (eoc, oec, eo_c)
