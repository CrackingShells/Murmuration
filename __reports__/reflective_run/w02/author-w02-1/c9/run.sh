#!/bin/sh
# Full and quick are the same (about 3 s, no model calls, no seeds): selftests, mutants, the lab's claim states before and after,
# and every verdict section of every claim file that holds more than one `verdict:` line.
D=$(cd "$(dirname "$0")" && pwd); WT=$(cd "$D/../../../../.." && pwd); PY=$(command -v python3); cd "$D"
for f in lab_status lab_init resume_brief user_words; do "$PY" -I "$WT/scripts/$f.py" --selftest; done
"$PY" -I mutants9.py
"$PY" -I sections.py "$WT" | tee sections.txt
for v in before after; do
  if [ $v = before ]; then S=lab_status_before.py; else S="$WT/scripts/lab_status.py"; fi
  "$PY" -I -c "import importlib.util as u,sys;sp=u.spec_from_file_location('l',sys.argv[1]);m=u.module_from_spec(sp);sp.loader.exec_module(m);print('\n'.join(m.report_claims(sys.argv[2])))" "$S" "$WT" > ${v}_claims_now.txt
done
diff before_claims_now.txt after_claims_now.txt; echo "claim lines that differ: $(diff before_claims_now.txt after_claims_now.txt | grep -c '^>')"
