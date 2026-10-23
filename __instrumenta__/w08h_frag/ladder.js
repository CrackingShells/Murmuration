/* ---------- A. lever ladder ---------- */
const STAT={land:["landed","sw-land"],not:["not landed","sw-not"],user:["yours to set","sw-user"],out:["stays out","sw-out"],untried:["not tried","sw-untried"]};
/* USD figures: lo, pt (central, optional), hi; b = USD of the spend the lever's side carries; nb = USD of the narrow pool it touches */
const LEV=[
 {n:"1-hour cache for the PI",on:"PI spend, USD 144.47 (six sessions)",b:144.47,nb:144.47,lo:43.6,hi:104.0,st:"land",stx:"landed: every PI cache write is 1-hour",lab:"ESTIMATE",
  t:"Low end: net +13.1, +30.7, −0.16 USD for the PI sessions of waves 5–7 (mean +14.55; explorer-w08-c), summed to 43.6. High end: a 5-minute cache would have re-written USD 119.07 that the 1-hour tier read, for a 15.08 premium, over all six sessions (explorer-w08-d), net 104.0. The two do not count the same hits (see the report). It is how the Desktop PI runs, not a setting the lab changed. P(net > 0) 0.99 by one model, n = 3 sessions."},
 {n:"PI compaction near 250k tokens",on:"PI spend, USD 144.47",b:144.47,nb:144.47,lo:31.27,hi:44.78,st:"user",stx:"yours to set: a window key in a guarded settings file",lab:"ESTIMATE",
  t:"Net of what compaction costs (0.54 USD each, MEASURED at 200k on haiku, re-priced), by what the PI re-reads afterwards: USD 44.78 at 0 tokens, 42.15 at 10k, 31.27 at 45k, 11.37 at 90k (explorer-w08-e; explorer-w08-c3's Opus-priced run gives 43–45 at 2.5–10k and 32.3 at 45k). One real compaction exists in the data; the information lost is not priced. w08-c3 (MEASURED, verified): 15 of 17 PI-like runs on a 150k-window scratch lab answered all five questions after a compaction with the existing resume brief; it does not carry the jump to a real PI at 250k (a 91k floor, larger files), and the settings route through the project file was not run. The setting lives in the main checkout's settings file, which the permission guard refuses to write: the file is yours. The PreCompact hook added nothing and does not land."},
 {n:"Drop the skills listing from the PI",on:"skill listings re-sent, USD 14.78 (six PI sessions)",b:144.47,nb:14.78,lo:2.90,hi:14.78,st:"not",stx:"not landed: built-in skills would be lost",lab:"ESTIMATE",
  t:"The skill listing cost USD 14.78 across six PI sessions, of which 11.88 is session 1's 22 re-injections (explorer-w08-d). The low end, 2.90, is the other five sessions (14.78 − 11.88). Wave 7 measured request 0 about 10.6–11.0k tokens lower without it (w07-c1, below MEASURED: restate). Not landed: built-in skills such as dataviz would be lost."},
 {n:"Send the PI's orientation reads to a worker",on:"orientation reads to the first dispatch, USD 10.44",b:144.47,nb:10.44,pt:8.87,lo:8.87,hi:8.87,st:"untried",stx:"not tried",lab:"ESTIMATE",
  t:"Six sessions: saving 2.05 / 1.19 / 1.95 / 1.43 / 1.98 / 0.27 = USD 8.87 after a 1,500-token summary and a Sonnet worker's cost (explorer-w08-d, formula there). The narrow pool, 10.44, is the six session figures 2.36 + 1.46 + 2.23 + 1.67 + 2.25 + 0.47 added. explorer-w08-c's frame says delegating a read pays only above about 50,000 tokens (P 0.57)."},
 {n:"Cap the PI's incoming hand-backs, gross",on:"187 hand-backs carried, USD 12.55",b:144.47,nb:12.55,lo:5.99,hi:10.30,st:"land",stx:"landed as a line in the brief (w08-c6); the gate is not",lab:"ESTIMATE",
  t:"Capping at 3,000 to 1,000 characters saves USD 5.99–10.30 over their lives in context (explorer-w08-d). Gross: it leaves out the worker's extra request and the PI opening the file instead. The cap went into the briefs as a line (w08-c6, MEASURED: first hand-backs of 1,809–2,449 characters against 3,328–5,873 without it, n = 6 each); the gate below is the net, and is not landed."},
 {n:"rtk on the shell commands it lists",on:"worker context USD 83.69; rtk-listed 9.81",b:83.69,nb:9.81,lo:1.5,hi:8.8,st:"out",stx:"stays out",lab:"ESTIMATE",
  t:"CITED claim of 60–90% compression (a fetch summary of the README page, not the README) times the MEASURED share of listed commands. Low end 1.5: git, grep, find, ls only (2.44 × 60%). High end 8.8: all listed output at 90%, which includes `cat` of the files a verifier must read. Nothing was installed or run. The PI's reading: no."},
 {n:"Lab documents by section, or capped",on:"lab documents read by workers, USD 11.98",b:83.69,nb:11.98,lo:2.73,pt:5.74,hi:8.98,st:"land",stx:"landed as brief practice (w08-c6); saving not measured",lab:"ESTIMATE",
  t:"A cap or a section of 5,000 / 2,500 / 1,000 tokens saves at most USD 2.73 / 5.74 / 8.98 of the 11.98 (3.3% / 6.9% / 10.7% of worker context USD). A ceiling: nothing needed was cut and no re-read followed. No document Read of 117 used offset or limit. explorer-w08-b: colgrep returns the whole file for markdown."},
 {n:"Cap every tool result, 5,000 down to 2,500 tokens",on:"all tool results, USD 38.53 (overlaps rows around it)",b:83.69,nb:38.53,lo:5.89,hi:13.06,st:"untried",stx:"not tried; not realistic (cuts the worker's own code output too)",lab:"ESTIMATE",
  t:"Ceiling from explorer-w08-a: capping every tool result at 5,000 tokens saves at most USD 5.89 (7.0%), at 2,500 USD 13.06 (15.6%). It contains the script and document rows, so it must not be added to them. It replaces wave 7's 29.7% of cache-read spend for results over 5,000 characters, a different base."},
 {n:"Compact just before a pause over an hour",on:"the seven re-writes, USD 14.17",b:144.47,nb:14.17,pt:5.27,lo:5.27,hi:5.27,st:"untried",stx:"not tried",lab:"ESTIMATE",
  t:"Seven cache misses re-wrote USD 14.17; compacting first would net USD 5.27 in total (−0.30 to +2.45 each; the three smallest contexts lose). explorer-w08-d."},
 {n:"The PI reads documents by section",on:"documents over 1,500 tokens, USD 7.14",b:144.47,nb:7.14,lo:3.10,hi:4.64,st:"untried",stx:"not tried for the PI's own reads (briefs name sections since w08-c6)",lab:"ESTIMATE",
  t:"Keeping 50% or 25% of each large document read saves USD 3.10 / 4.64 (explorer-w08-d), f assumed. The PI mostly reads by cat/sed/head in Bash (80 items, USD 5.26), and Read of documents is 15 items."},
 {n:"Hand-back gate at 5,000 characters (w08-c2)",on:"180 priced past hand-backs; PI spend 144.47",b:144.47,nb:12.55,lo:0.9,hi:2.8,st:"not",stx:"not landed (PI decision); unverified",lab:"ESTIMATE",
  t:"Net of the worker's extra request: USD 0.9–2.8 over 180 past hand-backs, 1–2% of PI spend as the claim states it. Negative if the PI newly opens the worker's file in more than 20–62% of the fired cases; in the past it opened the named file after 19 of 26 explorer hand-backs. The mechanism worked live (5 of 5 cells shortened). w08-c2 has no verdict: the PI decided against landing and against a verifier."},
 {n:"Merge independent tool calls (a line in the agent file)",on:"worker recorded cost, USD 109.92 (waves 4–8)",b:109.92,nb:109.92,lo:0.26,hi:2.25,st:"out",stx:"stays out: unchanged agents already batch",lab:"ESTIMATE",
  t:"Low end 0.26: audit-adjusted strict reads. High end 2.25: loose upper bound with the thinking each merged request would not carry (explorer-w08-g; 0.2–2.1% of recorded USD). The lever test: fresh Sonnet subagents sent all independent Reads in one message without the line (8 of 8, 16 of 16 in 3 of 4); the line changed nothing. 65% of the lab's single-call requests are run-then-run Bash, which the line does not address."},
 {n:"Cap lab-script output at 5,000 → 1,000 tokens",on:"lab-script output, USD 3.07",b:83.69,nb:3.07,lo:0.12,pt:0.45,hi:1.14,st:"out",stx:"stays out",lab:"ESTIMATE",
  t:"USD 0.12 / 0.45 / 1.14 at 5,000 / 2,500 / 1,000 tokens (0.1% / 0.5% / 1.4% of worker context USD). Scripts' output has a median of 540 tokens; the largest is 10,257 (explorer-w08-a). Wave 7's first look had said about 2%, from 60 results."},
 {n:"Fewer PI requests per dispatch batch",on:"consecutive dispatching requests, USD 144.47",b:144.47,nb:144.47,pt:0.75,lo:0.75,hi:0.75,st:"untried",stx:"not tried (loose upper bound USD 12)",lab:"ESTIMATE",
  t:"Strict count: 10 requests would merge, USD 0.75 of cache reads. A looser count (dispatches within 120 s) gives USD 12.01 as an upper bound, not drawn (explorer-w08-d)."},
 {n:"1-hour cache for authors",on:"authors' cache cost, 14 lives, USD 32.06",b:109.92,nb:32.06,lo:-2.15,pt:-0.28,hi:3.31,st:"land",stx:"landed (wave 7, by decision); the sign is a coin flip",lab:"ESTIMATE",
  t:"Per life, waves 5–7: mean −0.02 USD, sd 0.39, 10th / median / 90th −0.26 / −0.10 / +0.25; 5 of 14 lives gain (explorer-w08-c). The central point is 14 × −0.02 = −0.28. The range −2.15 to +3.31 is wave 7's, over waves 4–6 under two counting rules, and rests on wave 4's unrecorded pauses (w07-c7 escalated, unresolved). 5 of 7 decision rules say 5 minutes, 2 say 1 hour. Narrow pool: the authors' cache cost, 2.29 × 14 = 32.06."},
 {n:"Lower effort for workers (low)",on:"thinking carried, USD 15.8 (workers, waves 4–7)",b:83.69,nb:15.8,lo:0,pt:0,hi:0,ceil:15.8,st:"out",stx:"stays out: nothing to save below the default",lab:"MEASURED",
  t:"Measured on two planted-error verifier tasks, 30 subagent runs (n = 3 per arm): USD 0.0185 low against 0.0194 default on task A and 0.0157 against 0.0190 on B, inside the run-to-run range; every arm gave the right verdict; max cost 7–8 times default. The dotted outline is the ceiling no effort level reaches: all thinking carried, USD 15.8 or 18.9% of worker context USD (ESTIMATE from a signature fit; explorer-w08-a inferred 22.5%). The lab's agent files were not run."},
];
const ladState={u:"side",z:0};
function ladKey(r){const v=r.pt!==undefined?r.pt:(r.lo+r.hi)/2;return v/(ladState.u==="narrow"?r.nb:r.b)}
function drawLadder(){
  const svg=$("#ladder");svg.innerHTML="";
  const u=ladState.u,L=430,R=1010,rowH=48,top=34;
  const val=(r,x)=>u==="usd"?x:100*x/(u==="narrow"?r.nb:r.b);
  const rows=LEV.slice().sort((a,b)=>val(b,b.pt!==undefined?b.pt:(b.lo+b.hi)/2)-val(a,a.pt!==undefined?a.pt:(a.lo+a.hi)/2));
  let mx=0,mn=0;rows.forEach(r=>{mx=Math.max(mx,val(r,r.hi),val(r,r.ceil||0));mn=Math.min(mn,val(r,r.lo))});
  const nice=v=>{const s=[1,2,3,5,8,10,12,15,20,25,30,40,50,60,75,100,120];return s.find(x=>x>=v)||v};
  let hiAx=ladState.z?(u==="usd"?10:12):nice(mx), loAx=mn<0?-Math.ceil(-mn/ (hiAx/10))*(hiAx/10):0;
  if(loAx<0&&!ladState.z)loAx=Math.min(loAx,-hiAx/12);
  const sx=v=>L+(R-L)*(Math.max(loAx,Math.min(hiAx,v))-loAx)/(hiAx-loAx);
  const step=hiAx>=60?10:hiAx>=20?5:hiAx>=10?2:hiAx>=5?1:0.5;
  const unit=u==="usd"?"$":"";const suf=u==="usd"?"":"%";
  for(let v=Math.ceil(loAx/step)*step;v<=hiAx+1e-9;v+=step){const x=sx(v);el("line",{x1:x,y1:top-8,x2:x,y2:top+rows.length*rowH-6,stroke:"var(--grid)"},svg);
    txt(svg,{x,y:top-14,"text-anchor":"middle","font-size":"11",class:"muted"},unit+(Math.round(v*10)/10)+suf)}
  el("line",{x1:sx(0),y1:top-8,x2:sx(0),y2:top+rows.length*rowH-6,stroke:"var(--text-muted)"},svg);
  rows.forEach((r,i)=>{
    const y=top+i*rowH,[stn,cls]=STAT[r.st];
    const g=el("g",{"data-tip":r.n+". "+r.t+"  Acts on: "+r.on+". Label: "+r.lab+". Status: "+r.stx+"."},svg);
    el("rect",{x:0,y:y-6,width:1080,height:rowH-4,class:"hit"},g);
    txt(g,{x:0,y:y+10,"font-size":"13","font-weight":"600"},r.n);
    txt(g,{x:0,y:y+25,"font-size":"11",class:"sec"},"acts on: "+r.on);
    const sub=txt(g,{x:0,y:y+39,"font-size":"11","font-weight":"600",class:cls},r.stx+" · "+r.lab);
    const lo=val(r,r.lo),hi=val(r,r.hi),pt=val(r,r.pt!==undefined?r.pt:r.lo);
    const est=r.lab==="ESTIMATE";
    const H=18,by=y+4;
    if(r.ceil!==undefined){el("rect",{x:sx(0),y:by,width:Math.max(sx(val(r,r.ceil))-sx(0),2),height:H,rx:3,fill:"none",stroke:"var(--text-muted)","stroke-dasharray":"2 3"},g)}
    const x0=sx(Math.min(0,lo)),xh=sx(hi);
    const bar=(xa,xb,op)=>{const e=el("rect",{x:Math.min(xa,xb),y:by,width:Math.max(Math.abs(xb-xa),2),height:H,rx:3,class:cls,"fill-opacity":op},g);if(est){e.setAttribute("stroke","var(--text-primary)");e.setAttribute("stroke-dasharray","3 2");e.setAttribute("stroke-width","1")}};
    if(r.pt!==undefined&&r.pt!==r.lo&&r.pt!==r.hi){bar(sx(0),sx(Math.max(pt,0)),1);bar(sx(0),xh,0.4);if(lo<0)bar(sx(0),sx(lo),0.4)}
    else if(lo===hi){bar(sx(0),xh,1)}
    else {bar(sx(0),sx(Math.max(lo,0)),1);bar(sx(Math.max(lo,0)),xh,0.4);if(lo<0)bar(sx(lo),sx(0),0.4)}
    if(r.pt!==undefined&&r.pt!==r.lo&&r.pt!==r.hi){const px=sx(pt);el("line",{x1:px,y1:by-3,x2:px,y2:by+H+3,stroke:"var(--text-primary)","stroke-width":2},g)}
    const clipped=hi>hiAx;
    const f=v=>{const a=Math.abs(v);return (v<0?"−":"")+(u==="usd"?"$":"")+(a>=10?a.toFixed(0):a>=1?a.toFixed(1):a.toFixed(2))+suf};
    let tx=r.pt!==undefined&&r.pt===r.lo&&r.pt===r.hi?f(pt):(f(lo)+" to "+f(hi));
    if(r.pt!==undefined&&r.pt!==r.lo&&r.pt!==r.hi)tx=f(lo)+" · "+f(pt)+" · "+f(hi);
    if(r.ceil!==undefined)tx="≈ 0 (ceiling "+f(val(r,r.ceil))+")";
    if(r.lab==="ESTIMATE"&&false)tx+="";
    if(clipped||xh>R-90){txt(g,{x:R-6,y:by+14,"text-anchor":"end","font-size":"11.5","font-weight":"600",style:"paint-order:stroke;stroke:var(--surface-1);stroke-width:4px;stroke-linejoin:round"},tx+(clipped?" ▸":""))}
    else txt(g,{x:Math.max(xh,sx(0))+8,y:by+14,"font-size":"11.5","font-weight":"600"},tx);
  });
  svg.setAttribute("viewBox",`0 0 1080 ${top+rows.length*rowH+10}`);
  const nt={side:"Bars are a share of the spend of the side the lever sits on: worker context USD 83.69 (waves 4–7) or recorded worker cost 109.92 (waves 4–8) for worker levers; the PI's USD 144.47 for PI levers. The 1-hour author row is a share of the workers' 109.92.",narrow:"Bars are a share of the narrow pool each lever touches (the second line of each row): small pools make big shares, so this view ranks levers by how much of their own pool they remove, not by money.",usd:"Bars are USD over the data each report used (waves 4–7 or 4–8 for workers, six PI sessions for the PI), not per wave. Rows overlap: do not add them. The pale part is the rest of the range; the vertical tick, where there is one, is the central value."}[u];
  $("#ladNote").textContent=nt;
  bindTips(svg);
}
document.querySelectorAll("#ladUnit button").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll("#ladUnit button").forEach(x=>x.setAttribute("aria-pressed",x===b));ladState.u=b.dataset.u;drawLadder()}));
document.querySelectorAll("#ladZoom button").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll("#ladZoom button").forEach(x=>x.setAttribute("aria-pressed",x===b));ladState.z=+b.dataset.z;drawLadder()}));
drawLadder();
(function(){
  const svg=$("#ladTime"),L=330,R=1010,max=90,sx=v=>L+(R-L)*v/max,rowH=34,top=28;
  const T=[
   ["Exec form: permission guard start",81,81,"123 → 42 ms, pooled medians, 10 of 10 pairs (w07-c3, MEASURED)","land"],
   ["Exec form: budget (PostToolUse)",63.5,63.5,"104.5 → 41 ms, 10 of 10 pairs (w07-c3, MEASURED)","land"],
   ["Lean hook starts (wave 6)",20,28,"−20 to −28 ms a worker start (w06-c9, MEASURED)","land"],
   ["Rust permission guard",15.8,15.8,"start to exit 32.3 → 16.5 ms, 598 of 600 pairs (w07-c6, MEASURED). The recorded hook is 23.5 ms lower (w07-c8, below MEASURED: restate)","land"],
   ["Rust budget (w08-c4)",7,12,"7.4–12.3 ms outside the platform; in the platform PostToolUse 9.0 ms (10 of 12 pairs), PostToolBatch 7.0 ms (9 of 12, below the registered 10); reproducer-w08-1 measured 12.1–12.9 (w08-c4, MEASURED, SUPPORTED; on main)","land"],
   ["Rust hand-back (w08-c4)",8,15,"8.1–15.5 ms per start outside the platform (w08-c4, MEASURED, SUPPORTED; on main)","land"],
  ];
  for(let v=0;v<=max;v+=10){const x=sx(v);el("line",{x1:x,y1:top-8,x2:x,y2:top+T.length*rowH-4,stroke:"var(--grid)"},svg);txt(svg,{x,y:top-12,"text-anchor":"middle","font-size":"11",class:"muted"},v+" ms")}
  T.forEach(([n,lo,hi,t,st],i)=>{const y=top+i*rowH,g=el("g",{"data-tip":n+": "+t},svg);
    el("rect",{x:0,y:y-6,width:1080,height:rowH-2,class:"hit"},g);txt(g,{x:0,y:y+12,"font-size":"12.5","font-weight":"600"},n);
    el("rect",{x:sx(0),y:y,width:sx(lo)-sx(0),height:16,rx:3,class:STAT[st][1]},g);
    if(hi>lo)el("rect",{x:sx(lo),y:y,width:sx(hi)-sx(lo),height:16,rx:3,class:STAT[st][1],"fill-opacity":.4},g);
    txt(g,{x:sx(hi)+8,y:y+13,"font-size":"11.5","font-weight":"600"},lo===hi?lo+" ms":lo+"–"+hi+" ms")});
  svg.setAttribute("viewBox",`0 0 1080 ${top+T.length*rowH+6}`);
  bindTips(svg);
})();
