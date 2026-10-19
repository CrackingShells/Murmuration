import json,sys
rows=[json.loads(l) for l in open(sys.argv[1] if len(sys.argv)>1 else 'results.jsonl')]
print("%-62s %-7s %-3s %-4s %-3s %-4s %4s %4s %4s | %-6s %6s %6s %6s %6s %s"%("cell","ver","mod","thk","len","bg","sub","nullstop/req","", "truthO","sumLast","sumFirst","subLast","subTrue?","USD"))
tot=0
for o in rows:
    sub=list(o['sub'].values())
    req=sum(s['requests'] for s in sub); ns=sum(s['null_stop_last'] for s in sub)
    subl=sum(s['sums']['last']['output_tokens'] for s in sub)
    print("%-62s %-7s %-3s %-4s %-3s %-4s sub=%d req=%d null=%d | truthOut=%d totLast=%d totFirst=%d subLast=%d think=%d diffLast=%s USD=%.4f"%(
      o['cell'],o['version'],o['mode'],o['think'],o['length'],o['started_in_background'],len(sub),req,ns,o['truth']['output_tokens'],
      o['tot_last']['output_tokens'],o['tot_first']['output_tokens'],subl,o['think_truth'],list(o['diff_last'].values()),o['cost_usd']))
    tot+=o['cost_usd']
print("total USD",tot)
