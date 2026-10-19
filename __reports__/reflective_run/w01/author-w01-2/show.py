import json,sys
for l in sys.stdin:
    o=json.loads(l)
    print("==",o['cell'],o['version'],o['bin'],o['mode'],o['think'],o['length'],o['env'],o['io'],'partial',o['partial'],'tdisp',o['thinkdisp'],'eff',o['effort'],'USD',o['cost_usd'],'bg',o['started_in_background'],'spawned',o['spawned'],'results',o['n_results'])
    print(' truth',o['truth'],'think',o['think_truth'])
    for m in ('first','last','max'): print(' diff',m,list(o['diff_'+m].values()))
    for a,s in o['sub'].items():
        print(' sub',a[:8],'req',s['requests'],'rec',s['records'],'nullstop',s['null_stop_last'],'stops',s['stops'],'out first',s['outs_first'],'last',s['outs_last'],'think',s['think'])
    print(' main per req',o['main_per_request'])
    for h in o['hook_view']: print(' hook',h)
