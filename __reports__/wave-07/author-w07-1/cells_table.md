| cell | prompt | req0 tokens | deferred names | deferred chars | listing skills | listing chars | model requests | Reads (failed) | final answer (first 90 chars) |
|:--|:--|--:|--:|--:|--:|--:|--:|:--|:--|
| A1 | p2 | 31307 | 110 | 4156 | 86 | 29957 | 3 | skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE. |
| A2 | p2 | 31305 | 110 | 4156 | 86 | 29957 | 3 | skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE |
| A3 | p2 | 30975 | 110 | 4156 | 86 | 29957 | 3 | skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=`Budget: USD 3` WAVE_HEADING=`# Wave NN`  DONE |
| A4 | p2 | 33692 | 229 | 7867 | 86 | 29957 | 3 | skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=`Budget: USD 3` (and `Time: min 20`) WAVE_HEADING=`# Wave NN`  Both values |
| A_p5d | p5d | 34229 | 262 | 8866 | 86 | 29957 | 2 |  (0) | PATH=/private/tmp/claude-501/bundled-skills/2.1.304/da704b915ba50ecf1c38af6faffe5843/datav |
| B1 | p2 | 20645 | 129 | 4678 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE |
| B2 | p2 | 20355 | 110 | 4156 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE |
| B3 | p2 | 22739 | 229 | 7867 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE |
| B_p4l | p4l | 21763 | 110 | 4156 | 0 | 0 | 3 | skills/research-loop/SKILL.md (0) | The lab is set up in `/private/tmp/murmuration-w07/author-w07-1/runs/B_p4l/lab`, and your  |
| B_p4s | p4s | 21553 | 110 | 4156 | 0 | 0 | 2 | skills/research-loop/SKILL.md (0) | ``` # Lab status  Current wave note: __statera__/wave-01.md  ## Open puzzles (0) none rais |
| B_p5d | p5d | 20340 | 110 | 4156 | 0 | 0 | 3 | skills/research-loop/SKILL.md (0) | PATH=none NAME=none DONE |
| B_p5w | p5w | 20341 | 110 | 4156 | 0 | 0 | 3 | /Users/hacker/.claude/plugins/cache/cracking-shells/writing-history/1.1.0/skills/writing-history/SKILL.md (0) | PATH=/Users/hacker/.claude/plugins/cache/cracking-shells/writing-history/1.1.0/skills/writ |
| V1_1 | p2 | 21864 | 194 | 6769 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE. |
| V1_2 | p2 | 22803 | 229 | 7867 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=Budget: USD 3 WAVE_HEADING=# Wave NN  DONE |
| V1_3 | p2 | 22314 | 203 | 7160 | 0 | 0 | 3 | skills/research-loop/SKILL.md; skills/research-loop/references/briefs.md; skills/research-loop/templates/wave.md (0) | EXPLORER_BUDGET=`Budget: USD 3` (with `Time: min 20` on the next line; source: research-lo |
| V1_p4l | p4l | 23692 | 203 | 7160 | 0 | 0 | 2 | skills/research-loop/SKILL.md (0) | The lab is initialized in `/private/tmp/murmuration-w07/author-w07-1/runs/V1_p4l/lab`, wit |
| V1_p4s | p4s | 22945 | 182 | 6578 | 0 | 0 | 2 | skills/research-loop/SKILL.md (0) | ``` # Lab status  Current wave note: __statera__/wave-01.md  ## Open puzzles (0) none rais |
| V1_p5d | p5d | 22502 | 210 | 7345 | 0 | 0 | 2 |  (0) | PATH=none NAME=none (dataviz is a built-in skill with no SKILL.md on disk, so I could not  |
| V1_p5w | p5w | 20870 | 145 | 5432 | 0 | 0 | 3 | skills/research-loop/SKILL.md; /Users/hacker/.claude/plugins/cache/cracking-shells/writing-history/1.1.0/skills/writing-history/SKILL.md (0) | PATH=/Users/hacker/.claude/plugins/cache/cracking-shells/writing-history/1.1.0/skills/writ |

Pairs (p1): A request 0 - B request 0 (rule: >= 9000 in each pair)
- pair 1: A1 31307 (deferred 110), B1 20645 (deferred 129), drop 10662
- pair 2: A2 31305 (deferred 110), B2 20355 (deferred 110), drop 10950
- pair 3: A3 30975 (deferred 110), B3 22739 (deferred 229), drop 8236

Extra cells, outside the v0 rule:
- A4 33692 (deferred 229) vs V1_1 21864 (deferred 194): drop 11828
- A4 33692 (deferred 229) vs V1_2 22803 (deferred 229): drop 10889
- A4 33692 (deferred 229) vs V1_3 22314 (deferred 203): drop 11378

p2 correct (budget and heading): {'A1': True, 'A2': True, 'A3': True, 'A4': True, 'B1': True, 'B2': True, 'B3': True, 'V1_1': True, 'V1_2': True, 'V1_3': True}
