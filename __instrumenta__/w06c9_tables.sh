# w06-c9: writes the derived tables of metrics e1 (process mode), e3 and e4 and the e2 tables of all pairs; inputs: env OLD, NEW (plugin roots of main and build), OUT (scratch folder, must be new), RES (folder for the tables), PAIRS (e2 pairs "main_run:new_run ..."); output: $RES/{e1_process_mode,e1_process_mode_mutant,e2_all_pairs,e3_shape,e3_selftests,e4_lines}.txt
mkdir -p $RES
python3 -I __instrumenta__/w06c9_lines.py $OLD $NEW > $RES/e4_lines.txt
python3 -I __instrumenta__/w06c9_shape.py $OLD $NEW > $RES/e3_shape.txt
sh __instrumenta__/w06c9_selftests.sh $NEW > $RES/e3_selftests.txt
python3 -I __instrumenta__/w06c9_e2e_commands.py --old $OLD --new $NEW --out $OUT/cmd_ok > $RES/e1_process_mode.txt
python3 -I __instrumenta__/w06c9_e2e_commands.py --mutate --old $OLD --new $NEW --out $OUT/cmd_mut > $RES/e1_process_mode_mutant.txt
python3 -I __instrumenta__/w06c9_measure.py $PAIRS > $RES/e2_all_pairs.txt
