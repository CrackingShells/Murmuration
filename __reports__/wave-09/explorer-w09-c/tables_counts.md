## decider totals (unique tool_use ids)
- no_decision_record 75197
- classifier_allow 30663
- mode_accept 4835
- rule_accept 2722
- hook_reject 1161
- accept_unlabelled 902
- subcommand_accept 484
- other_accept 423
- rule_reject 152
- user_reject 134
- classifier_block 67
- user_accept 45
- classifier_unavailable 38
- safetycheck_reject 25
- no_result 10
- hook_accept 9
- dontask_reject 2
- interrupted_by_safety_classifier 1
- cancelled 1

## by tool family (rows decider)
| decider | Agent | Bash | Edit | Glob | Grep | MCP | MultiEdit | Read | WebFetch | WebSearch | Write | other |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| no_decision_record | 1246 | 46230 | 6458 | 11 | 2 | 2901 | 1 | 11105 | 739 | 514 | 2563 | 3427 |
| classifier_allow | 1134 | 26374 | 28 | 0 | 0 | 1088 | 0 | 0 | 137 | 131 | 96 | 1675 |
| mode_accept | 208 | 1302 | 344 | 19 | 3 | 25 | 0 | 2126 | 0 | 0 | 788 | 20 |
| rule_accept | 49 | 1093 | 15 | 19 | 14 | 590 | 0 | 870 | 0 | 0 | 69 | 3 |
| hook_reject | 12 | 916 | 16 | 0 | 1 | 7 | 0 | 0 | 0 | 0 | 76 | 133 |
| accept_unlabelled | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 882 |
| subcommand_accept | 0 | 484 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| other_accept | 0 | 0 | 79 | 0 | 0 | 0 | 0 | 124 | 110 | 0 | 108 | 2 |
| rule_reject | 0 | 27 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 121 |
| user_reject | 0 | 89 | 2 | 0 | 0 | 7 | 0 | 2 | 0 | 0 | 7 | 27 |
| classifier_block | 2 | 57 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 2 | 2 |
| user_accept | 0 | 1 | 0 | 0 | 0 | 5 | 0 | 2 | 0 | 0 | 0 | 37 |
| classifier_unavailable | 2 | 32 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| safetycheck_reject | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| no_result | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 1 | 0 | 3 |
| hook_accept | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| dontask_reject | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| interrupted_by_safety_classifier | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cancelled | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## by month
| decider | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 | 2026-10 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| no_decision_record | 90 | 2369 | 862 | 17323 | 32773 | 13878 | 7902 |
| classifier_allow | 0 | 0 | 0 | 0 | 0 | 0 | 30663 |
| mode_accept | 0 | 0 | 0 | 0 | 0 | 0 | 4835 |
| rule_accept | 0 | 0 | 0 | 0 | 0 | 0 | 2722 |
| hook_reject | 0 | 34 | 8 | 62 | 344 | 51 | 662 |
| accept_unlabelled | 0 | 0 | 0 | 0 | 0 | 0 | 902 |
| subcommand_accept | 0 | 0 | 0 | 0 | 0 | 0 | 484 |
| other_accept | 0 | 0 | 0 | 0 | 0 | 0 | 423 |
| rule_reject | 0 | 0 | 0 | 37 | 53 | 32 | 30 |
| user_reject | 0 | 0 | 0 | 3 | 33 | 6 | 92 |
| classifier_block | 0 | 0 | 0 | 8 | 4 | 28 | 27 |
| user_accept | 0 | 0 | 0 | 0 | 0 | 0 | 45 |
| classifier_unavailable | 0 | 0 | 0 | 1 | 5 | 3 | 29 |
| safetycheck_reject | 0 | 0 | 0 | 0 | 0 | 1 | 24 |
| no_result | 0 | 1 | 1 | 1 | 3 | 0 | 4 |
| hook_accept | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| dontask_reject | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| interrupted_by_safety_classifier | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| cancelled | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

## by permissionMode seen before the call (|att = auto_mode attachment seen)
| decider | None | None|att | acceptEdits | acceptEdits|att | auto | auto|att | bypassPermissions | default | default|att | dontAsk | plan | plan|att |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| no_decision_record | 36363 | 12538 | 47 | 57 | 8571 | 12765 | 0 | 88 | 15 | 0 | 3906 | 847 |
| classifier_allow | 9915 | 12955 | 0 | 0 | 3707 | 3782 | 0 | 7 | 0 | 0 | 56 | 241 |
| mode_accept | 1965 | 892 | 0 | 0 | 145 | 405 | 938 | 446 | 0 | 0 | 4 | 40 |
| rule_accept | 69 | 17 | 2 | 0 | 104 | 539 | 0 | 1977 | 0 | 2 | 3 | 9 |
| hook_reject | 443 | 133 | 0 | 0 | 72 | 101 | 5 | 377 | 0 | 0 | 25 | 5 |
| accept_unlabelled | 75 | 232 | 0 | 0 | 116 | 385 | 0 | 72 | 0 | 0 | 12 | 10 |
| subcommand_accept | 5 | 0 | 0 | 0 | 68 | 0 | 0 | 411 | 0 | 0 | 0 | 0 |
| other_accept | 109 | 103 | 0 | 0 | 8 | 154 | 0 | 0 | 0 | 0 | 16 | 33 |
| rule_reject | 3 | 14 | 0 | 0 | 3 | 12 | 0 | 5 | 0 | 0 | 100 | 15 |
| user_reject | 6 | 4 | 0 | 0 | 12 | 23 | 0 | 71 | 0 | 0 | 9 | 9 |
| classifier_block | 4 | 16 | 0 | 0 | 6 | 41 | 0 | 0 | 0 | 0 | 0 | 0 |
| user_accept | 0 | 1 | 0 | 0 | 0 | 18 | 0 | 7 | 0 | 0 | 8 | 11 |
| classifier_unavailable | 4 | 10 | 0 | 0 | 1 | 23 | 0 | 0 | 0 | 0 | 0 | 0 |
| safetycheck_reject | 0 | 23 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| no_result | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| hook_accept | 0 | 0 | 0 | 0 | 2 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| dontask_reject | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| interrupted_by_safety_classifier | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| cancelled | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## project groups, classifier_allow / classifier_block / classifier_unavailable
| project group | allow | block | unavailable |
|:--|--:|--:|--:|
| murmuration-arena | 11420 | 0 | 1 |
| murmuration-lab | 8403 | 9 | 0 |
| explore-combinatorics-on-binary | 1517 | 2 | 0 |
| other-tmp | 1478 | 0 | 0 |
| wt:async-work | 1447 | 0 | 0 |
| wt:mcp-python | 1143 | 1 | 0 |
| src-CrackingShells-Hatchling | 1125 | 3 | 2 |
| explore-augmented-light | 881 | 5 | 1 |
| explore-llm-gen-robot-protocol | 778 | 3 | 8 |
| wt:hypomnesis-v0214 | 532 | 0 | 0 |
| src-External-PCfVW-mcp-arangodb-async | 387 | 2 | 13 |
| career-colleagues-automation-level-review | 303 | 0 | 0 |
| src-LittleCoinCoin-usd-bio | 267 | 4 | 2 |
| career | 193 | 3 | 0 |
| wt:mcp-biomodelling | 186 | 0 | 0 |
| Library-Application-Support-Claude-scratch-works | 158 | 0 | 0 |
| src-CrackingShells | 103 | 0 | 0 |
| wt:llm-gen | 79 | 0 | 0 |
| wt:lbc-llm | 77 | 0 | 0 |
| career-Projects-CRPs-async | 70 | 1 | 1 |
| wt:usd-bio | 63 | 1 | 0 |
| wt:BDR-Retreat | 33 | 0 | 0 |
| wt:colgrep-mcp | 10 | 16 | 2 |
| wt:hypomnesis-intelligent | 10 | 0 | 2 |
| wt:ai-agent | 0 | 4 | 0 |
| src-External-PCfVW-mcp-python-ingestion | 0 | 2 | 1 |
| src-External-RIKEN-RCCS-Rikyu-Agent | 0 | 0 | 3 |
| career-Projects-ai-agent-academy | 0 | 1 | 1 |
| explore-colgrep-mcp | 0 | 2 | 0 |
| src-External-PCfVW-hypomnesis | 0 | 1 | 1 |
| wt:sift-table | 0 | 2 | 0 |
| src-CrackingShells-Hatch | 0 | 1 | 0 |
| src-CrackingShells-cracking-shells-playbook | 0 | 1 | 0 |
| src-External-rikenlbc-lbc-llm-agents | 0 | 1 | 0 |
| src-LittleCoinCoin-sift | 0 | 1 | 0 |
| wt:dai-mas | 0 | 1 | 0 |

## classifier block reasons
- Blocked by classifier 32
- [Auto-Mode Bypass] 6
- [PII Data Handling] 4
- [Safety Bypass Flag] 3
- The server-side auto mode classifier judged this action dangerous (it gave no explanation) 3
- [Self-Modification] 3
- None 2
- [Merge Without Review] 2
- [Security Test Removal] 2
- [Security Weaken] 1
- [External System Writes] 1
- [Safety Bypass Flag] The command sets `COLGREP_BYPASS=1`, an env var whose `_BYPASS_` name signals disarming the colgrep safety guard; clears only if the user names this flag. 1
- [Irreversible Local Destruction] 1
- [Git Destructive] 1
- [Safety Bypass Flag] The command sets `COLGREP_BYPASS=1` — an env var whose name signals it is designed to disarm colgrep's guard/wrapper — to fall back to raw grep after colgrep apparently failed, with no user authorization for this specific bypass. 1
- [Remote Shell Writes] 1
- [Create Unsafe Agents] 1
- [Interfere With Workloads] 1
- [Modify Shared Resources] 1
