"""Render prompts.csv as a markdown table (appendix of report.md). usage: python3 -I table_md.py prompts.csv > table.md"""
import csv,sys
print('| # | sess | UTC | ch | click | class | who | gap min | asked | uuid8 | what the human did (my words) |')
print('|:--|:--|:--|:--|:--|:--|:--|--:|:--|:--|:--|')
for i,r in enumerate(csv.DictReader(open(sys.argv[1])),1):
    g=r['gap_since_prev_human_min']
    g='' if g=='' else str(round(float(g)))
    print(f"| {i} | {r['session']} | {r['ts_utc'][5:10]} {r['ts_utc'][11:16]} | {r['channel']} | {r['verbatim_click'].replace('yes:','')} | {r['cls']} | {r['who']} | {g} | {r['agent_asked']} | {r['uuid'][:8]} | {r['note'].replace('|','/')[:150]} |")
