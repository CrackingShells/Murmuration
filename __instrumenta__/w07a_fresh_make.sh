#!/bin/sh
# Builds K distinct freshly linked binaries (C via clang, Rust via rustc; each has a unique constant so each has a new cdhash) into a directory and writes a w07a_spawn_bench cases file in which every binary is spawned R times in a row, followed by one control spawn of a long-known binary; inputs: OUTDIR K R CONTROL_BIN; output: OUTDIR/cases.tsv and the binaries. Then run: w07a_spawn_bench OUTDIR/cases.tsv 1 0 > rows.jsonl (rows come in file order) and python3 w07a_fresh_table.py rows.jsonl R.
out=$1; K=$2; R=$3; ctl=$4; mkdir -p "$out"; : > "$out/cases.tsv"
i=0
while [ $i -lt $K ]; do
  # alternate: even i = C binary (linker ad-hoc signature), odd i = Rust std binary (release)
  if [ $((i % 2)) -eq 0 ]; then
    echo "int main(void){return $i + 1000 - $i - 1000;} /* $i $(date +%s) */" > "$out/b$i.c"; clang -O2 -o "$out/b$i" "$out/b$i.c"
  else
    echo "fn main() { std::process::exit(if std::env::args().count() > 100000 { $i } else { 0 }) } // $i $(date +%s)" > "$out/b$i.rs"; rustc -O -o "$out/b$i" "$out/b$i.rs" 2>/dev/null
  fi
  j=0; while [ $j -lt $R ]; do printf 'b%s_r%s\t%s/b%s\n' $i $j "$out" $i >> "$out/cases.tsv"; j=$((j+1)); done
  printf 'ctl_after_b%s\t%s\n' $i "$ctl" >> "$out/cases.tsv"
  i=$((i+1))
done
