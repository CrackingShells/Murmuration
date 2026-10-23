| phase | wall minutes | requests | USD (list price) |
|:--|--:|--:|--:|
| start | 5.0 | 25 | 0.757 |
| start_python_side | 1.4 | 11 | 0.357 |
| python_done_start_rust | 1.2 | 5 | 0.216 |
| rust_first_build_ok | 6.5 | 6 | 0.291 |
| both_impls_c5_replay_equal_start_full_replay | 3.3 | 13 | 0.402 |
| live_done | 0.5 | 2 | 0.078 |
| start_rebuild_manifest | 0.3 | 1 | 0.033 |
| manifest_built | 1.8 | 6 | 0.182 |
| installer_fixed_clean_install_ok_start_full_replays | 0.8 | 4 | 0.168 |
| writing_while_replays_run | 6.2 | 5 | 0.142 |
| replays_done_mutants | 0.5 | 4 | 0.119 |
| docstring_manifest_commit | 1.9 | 4 | 0.110 |
| selftests_installs_done | 4.0 | 8 | 0.238 |
| tables_committed_writing_claim | 0.2 | 1 | 0.041 |
| total | 33.6 | 95 | 3.134 |

| group | phases | wall minutes | requests | USD |
|:--|:--|--:|--:|--:|
| python_side | start_python_side | 1.4 | 11 | 0.357 |
| rust_side | python_done_start_rust | 1.2 | 5 | 0.216 |
| equalizing | rust_first_build_ok | 6.5 | 6 | 0.291 |
| rebuild_and_manifest | start_rebuild_manifest | 0.3 | 1 | 0.033 |
| installer_fallback_diagnosis_and_fix | manifest_built | 1.8 | 6 | 0.182 |
| verification_runs_and_manifest_again | installer_fixed_clean_install_ok_start_full_replays,writing_while_replays_run,replays_done_mutants,docstring_manifest_commit,selftests_installs_done | 13.5 | 25 | 0.777 |
| shared | start,both_impls_c5_replay_equal_start_full_replay,live_done,tables_committed_writing_claim | 8.9 | 41 | 1.278 |
