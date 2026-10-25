"""Builds the table of subagent transcripts whose last tool call is not SubagentHandback, with a class, the end evidence and the deliverable verdict; reads __reports__/wave-09/explorer-w09-g/f_all.tsv (from w09g_classify.py f all); writes a markdown table to stdout."""
import csv, sys
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter="\t") if r["last_tool"] != "SubagentHandback"]
rows.sort(key=lambda r: r["end"])
ev = {
 "live": ("live at measurement (harness.jsonl has a start line, no end line; file written in the last minutes)", "not ended", "n/a", "n/a"),
 "budget_stop": ("hook_stopped_continuation attachment ('your USD 0.06 budget is used / the run ends here') after the last tool result; platform notice to the parent: 'ended without delivering a report through SubagentHandback'", "NO (hand-back message not delivered)", "report file written in 6 of 7 (s2: none)", "yes: parent said 'no report came back'; w02-c3 R5 counts it; shipped stop became decision: block"),
 "interrupted": ("last records: Bash (timeout 600000) rejected 'The user doesn't want to proceed with this tool use', then '[Request interrupted by user for tool use]'; the parent `claude -p` had ended its turn 10 min before; platform printed 'Background tasks still running 10m after the last turn ... stopping them'", "NO", "no report file written", "yes, as the arm's ending (S-w02-research-pi-2); not as a lost explorer report"),
 "final_text_after_handback": ("a SubagentHandback delivered earlier; resumed by SendMessage; answer sent by SendMessage; the last record is a text turn (end_turn); notice to the parent: 'report was delivered ... not repeated here'", "yes (earlier hand-back + SendMessage)", "no (the trailing text repeats the SendMessage content or is a remark)", "n/a (nothing missing)"),
 "final_text": ("last record is assistant text with stop_reason end_turn; agent type has no SubagentHandback tool (probe or built-in); parent's tool result starts '[Subagent hand-back] The text below is the final report' or the task notification was quoted", "yes (platform delivers the final text)", "no", "n/a"),
}
print("| # | wave / project | agent | type | name | last tool | class | end evidence | delivered | deliverable lost | PI / parent noticed |")
print("|--:|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|")
for i, r in enumerate(rows, 1):
    c = r["cls"]
    if c == "other": c = "live"
    e = ev[c]
    proj = r["proj"].replace("-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-", "wt:")
    print("| %d | %s %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (i, proj[-34:], r["end"][5:16], r["agent"], r["atype"], r["name"] or "-", r["last_tool"], c, e[0], e[1], e[2], e[3]))
