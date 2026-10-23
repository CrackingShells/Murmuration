/* ---------- 3. spend (B) ---------- */
const spend=[
  {w:"Waves 1–3",pi:63.23,other:98.91},
  {w:"Wave 4",pi:10.51,after:0,wk:17.88,hl:26.52},
  {w:"Wave 5",pi:11.90,after:6.18,wk:15.85,hl:18.18},
  {w:"Wave 6",pi:16.06,after:7.02,wk:32.03,hl:7.54},
  {w:"Wave 7",pi:15.86,after:11.28,wk:22.64,hl:2.48,roles:[["authors",10.07],["explorers",7.32],["verifiers",4.17],["page helper",1.08]]},
  {w:"Wave 8 so far",pi:6.10,after:0,wk:27.92,hl:19.91,lb:1,roles:[["authors",13.02],["explorers",13.57],["verifiers",1.33]]},
];
(function(){
  const svg=$("#spend"), L=130,R=1000,max=70,sx=v=>L+(R-L)*Math.min(v,max)/max,rowH=48,top=12,n=spend.length;
  hatchDef(svg,"hatchpi2");
  const dfs=el("defs",{},svg);const pp=el("pattern",{id:"hpi",width:5,height:5,patternUnits:"userSpaceOnUse",patternTransform:"rotate(45)"},dfs);
  el("rect",{width:5,height:5,fill:"var(--surface-0)"},pp);el("line",{x1:0,y1:0,x2:0,y2:5,stroke:"var(--s1)","stroke-width":2},pp);
  const nrows=n+2;
  for(let v=0;v<=max;v+=10){const x=sx(v);el("line",{x1:x,y1:top-4,x2:x,y2:top+nrows*rowH+4,stroke:"var(--grid)"},svg);
    txt(svg,{x,y:top+nrows*rowH+20,"text-anchor":"middle","font-size":"11",class:"muted"},"$"+v)}
  spend.forEach((s,i)=>{
    const y=top+i*rowH;
    if(s.other!==undefined){
      const tot=s.pi+s.other;
      const g=el("g",{"data-tip":`Waves 1–3 (one session, one worktree, exact): USD ${tot.toFixed(2)}, of which the PI's main thread ${s.pi.toFixed(2)} (explorer-w08-d, session ab96c5ed) and the rest of the worktree ${s.other.toFixed(2)} (workers and sessions started below it; scripts/lab_status.py --spend, 162.14 minus 63.23). Not split by role. The bar is cut at $70.`},svg);
      el("rect",{x:0,y:y-4,width:1080,height:rowH-8,class:"hit"},g);
      txt(g,{x:0,y:y+20,"font-size":"13","font-weight":"600"},s.w);
      let x=L;const w1=sx(s.pi)-L-2;el("rect",{x,y,width:w1,height:28,rx:4,class:"s1"},g);txt(g,{x:x+8,y:y+18,"font-size":"11.5",style:"fill:#fff"},"PI "+s.pi.toFixed(1));x+=w1+2;
      el("rect",{x,y,width:R-x,height:28,rx:4,fill:"var(--theirs)"},g);txt(g,{x:x+8,y:y+18,"font-size":"11.5",style:"fill:var(--text-primary)"},"rest "+s.other.toFixed(0)+" ▸");
      txt(g,{x:R+6,y:y+19,"font-size":"12","font-weight":"600"},"$"+tot.toFixed(0)+", workers + headless not split");
      return}
    const tot=s.pi+s.after+s.wk+s.hl;
    const g=el("g",{"data-tip":`${s.w}: PI ${s.pi.toFixed(2)}${s.after?" (+"+s.after.toFixed(2)+" after the close, same session)":""} · workers ${s.wk.toFixed(2)} · headless ${s.hl.toFixed(2)}${s.lb?" (at least)":""} = ${tot.toFixed(2)} USD. PI share of the wave ${(100*(s.pi+s.after)/tot).toFixed(0)}%.${s.lb?" The wave is open; every figure grows.":""}`},svg);
    el("rect",{x:0,y:y-4,width:1080,height:rowH-8,class:"hit"},g);
    txt(g,{x:0,y:y+20,"font-size":"13","font-weight":"600"},s.w);
    let x=L;[[s.pi,"s1","PI",0],[s.after,"hpi","after",1],[s.wk,"s2","workers",0],[s.hl,"s3","headless",0]].forEach(([v,c,nm,h])=>{
      if(!v)return;const w=sx(v)-L-2;const r=el("rect",{x,y,width:w,height:28,rx:4},g);
      if(h){r.setAttribute("fill","url(#hpi)");r.setAttribute("stroke","var(--s1)")}else r.setAttribute("class",c);
      if(w>60&&!h){txt(g,{x:x+8,y:y+18,"font-size":"11.5",style:"fill:#fff"},`${nm} ${v.toFixed(1)}`)}
      x+=w+2});
    txt(g,{x:x+8,y:y+19,"font-size":"12.5","font-weight":"600"},(s.lb?"≥ $":"$")+tot.toFixed(1));
  });
  [["Wave 7 workers",spend[4]],["Wave 8 workers",spend[5]]].forEach(([lab,s],k)=>{
    const y=top+(n+k)*rowH;
    txt(svg,{x:0,y:y+20,"font-size":"13","font-weight":"600"},lab);
    const g=el("g",{"data-tip":lab+", USD at list price, by role: "+s.roles.map(r=>r[0]+" "+r[1].toFixed(2)).join(" · ")+(k?". The present session to 01:25 JST, the explorer writing this page included.":". The largest single worker was author-w07-5 (the Rust guard), 4.30.")},svg);
    el("rect",{x:0,y:y-4,width:1080,height:rowH-8,class:"hit"},g);
    let x=L;const op=[1,0.75,0.55,0.35];
    s.roles.forEach(([nm,v],i)=>{const w=sx(v)-L-2;el("rect",{x,y,width:w,height:28,rx:4,class:"s2","fill-opacity":op[i]},g);
      if(w>70)txt(g,{x:x+8,y:y+18,"font-size":"11.5",style:i<2?"fill:#fff":""},nm+" "+v.toFixed(1));else txt(g,{x:x+w/2,y:y-6-(i%2)*11,"text-anchor":"middle","font-size":"10.5",class:"sec"},nm+" "+v.toFixed(1));x+=w+2});
    txt(g,{x:x+8,y:y+19,"font-size":"12.5","font-weight":"600"},"$"+s.wk.toFixed(1));
  });
  bindTips(svg);
})();
/* PI by source */
(function(){
  const svg=$("#piSrc"),L=330,R=900,tot=144.47;
  // price part
  const parts=[["cache reads",81.15,"s1","#fff"],["fresh cache writes",26.02,"s2","#fff"],["re-writes of context already there",14.19,"s3","#fff"],["billed output",23.11,"fam4","#fff"]];
  txt(svg,{x:0,y:16,"font-size":"12.5","font-weight":"600"},"By price part (MEASURED)");
  let x=L;const sxp=v=>(R-L)*v/tot;
  parts.forEach(([nm,v,c,fc])=>{const g=el("g",{"data-tip":`${nm}: USD ${v.toFixed(2)} (${(100*v/tot).toFixed(0)}% of 144.47). Every cache write of the PI is 1-hour (5.0 M tokens). Uncached input USD 0.01. [__reports__/wave-08/explorer-w08-d/tables.md section 1]`},svg);
    const w=sxp(v);el("rect",{x,y:4,width:w-1,height:26,rx:4,class:c},g);txt(g,{x:x+6,y:21,"font-size":"11",style:"fill:"+fc},`${nm.split(" ")[0]} ${v.toFixed(1)}`);x+=w});
  txt(svg,{x:R+8,y:21,"font-size":"12","font-weight":"600"},"= $144.47");
  txt(svg,{x:L,y:46,"font-size":"11",class:"sec"},"reads 56% · fresh writes 18% · re-writes 10% · billed output 16%");
  const fam={1:"own words (44.2%, USD 63.84)",2:"injected text and the prefix (22.0%, 31.79)",3:"tool results (17.5%, 25.29)",4:"workers' messages and notices (12.2%, 17.68)",5:"the one compaction's context (3.9%, 5.64)",6:"the user's messages (0.2%, 0.24)"};
  const rows=[
   ["billed output",23.11,1,"16.0%"],["own thinking carried in context (inferred)",18.76,1,"13.0%"],["skill listing, re-sent",14.78,2,"10.2%"],["worker hand-back messages (187)",12.55,4,"8.7%"],
   ["own tool calls",9.00,1,"6.2%"],["system prompt + tool definitions",8.45,2,"5.8%"],["dispatch briefs and messages",6.32,1,"4.4%"],["post-compaction context",5.64,5,"3.9%"],
   ["Bash cat/sed/head/tail of files",5.26,3,"3.6%"],["git output",5.26,3,"3.6%"],["deferred-tool, agent, MCP listings",5.04,2,"3.5%"],["task notifications (215)",4.97,4,"3.4%"],
   ["Bash python, scripts, other",4.97,3,"3.4%"],["Write/Edit content",3.47,1,"2.4%"],["other injected (hooks, reminders, skills)",3.53,2,"2.4%"],["lab_status.py output",2.86,3,"2.0%"],["own text",2.80,1,"1.9%"],
   ["search results",2.45,3,"1.7%"],["Agent/SendMessage acks",2.08,3,"1.4%"],["Read of a document or code",1.88,3,"1.3%"],["everything else (user 0.24, notes 0.15, other results 0.53, recorded thinking 0.39)",1.31,6,"0.9%"]];
  const y0=62,rh=24,sx=v=>L+(R-L)*v/24;
  txt(svg,{x:0,y:y0-4,"font-size":"12.5","font-weight":"600"},"By source (ESTIMATE)");
  for(let v=0;v<=24;v+=4){el("line",{x1:sx(v),y1:y0,x2:sx(v),y2:y0+rows.length*rh,stroke:"var(--grid)"},svg);txt(svg,{x:sx(v),y:y0+rows.length*rh+14,"text-anchor":"middle","font-size":"11",class:"muted"},"$"+v)}
  rows.forEach(([nm,v,f,sh],i)=>{const y=y0+6+i*rh;const g=el("g",{"data-tip":`${nm}: USD ${v.toFixed(2)} (${sh} of the PI's 144.47). Family: ${fam[f]}. ESTIMATE: tokens = characters × a ratio fitted per session; USD by position in the cache (explorer-w08-d, source_usd.tsv).`},svg);
    el("rect",{x:0,y:y-4,width:1080,height:rh-2,class:"hit"},g);
    txt(g,{x:0,y:y+11,"font-size":"11.5"},nm.length>56?nm.slice(0,54)+"…":nm);
    el("rect",{x:L,y:y,width:Math.max(sx(v)-L,2),height:14,rx:3,class:"fam"+f},g);
    txt(g,{x:sx(v)+6,y:y+12,"font-size":"11","font-weight":"600"},"$"+v.toFixed(2)+" · "+sh)});
  const ly=y0+rows.length*rh+34;
  Object.entries(fam).forEach(([k,t],q)=>{const lx=(q%3)*360,lyy=ly+Math.floor(q/3)*18;el("rect",{x:lx,y:lyy-9,width:10,height:10,rx:2,class:"fam"+k},svg);txt(svg,{x:lx+14,y:lyy,"font-size":"10.5",class:"sec"},t)});
  svg.setAttribute("viewBox",`0 0 1080 ${ly+34}`);
  bindTips(svg);
})();
/* workers by source */
(function(){
  const svg=$("#wkSrc"),L=400,R=960,mx=20;
  const fam={1:"the worker's own earlier turns (41.5%)",2:"documents (14.3%)",3:"code and scripts it runs or reads (19.7%)",4:"lab-script output (3.7%)",5:"other tool results (8.3%)",6:"harness, system prompt, messages (12.4%)"};
  const rows=[
   ["own turns: thinking blocks",18.82,1,"22.5%"],["own turns: tool-call text",15.92,1,"19.0%"],["cat/sed/head/tail of a document in Bash",7.22,2,"8.6%"],["the worker's own code run (inline python, scratch scripts)",7.28,3,"8.7%"],
   ["cat/sed/head/tail of source code in Bash",6.70,3,"8.0%"],["Read of a lab document",4.31,2,"5.1%"],["messages, resume prompts, task notices",3.34,6,"4.0%"],["other tool results (edits, mkdir, ls …)",3.09,5,"3.7%"],
   ["lab script output (scripts/, __instrumenta__/)",3.07,4,"3.7%"],["harness text at start",2.77,6,"3.3%"],["Read of source code",2.53,3,"3.0%"],["system prompt and tool schemas",1.81,6,"2.2%"],
   ["hook-injected text",1.76,6,"2.1%"],["search results (colgrep, grep, find)",1.73,5,"2.1%"],["ToolSearch results",0.92,5,"1.1%"],["git output",0.85,5,"1.0%"],["the brief",0.71,6,"0.8%"],["Read of a non-lab document",0.45,2,"0.5%"],["web or MCP results",0.38,5,"0.4%"]];
  const y0=8,rh=24,sx=v=>L+(R-L)*v/mx;
  for(let v=0;v<=mx;v+=4){el("line",{x1:sx(v),y1:y0,x2:sx(v),y2:y0+rows.length*rh,stroke:"var(--grid)"},svg);txt(svg,{x:sx(v),y:y0+rows.length*rh+14,"text-anchor":"middle","font-size":"11",class:"muted"},"$"+v)}
  rows.forEach(([nm,v,f,sh],i)=>{const y=y0+6+i*rh;const g=el("g",{"data-tip":`${nm}: USD ${v.toFixed(2)} (${sh} of 83.69). Family: ${fam[f]}. ESTIMATE (explorer-w08-a, by_class.tsv, tables.md).`},svg);
    el("rect",{x:0,y:y-4,width:1080,height:rh-2,class:"hit"},g);
    txt(g,{x:0,y:y+11,"font-size":"11.5"},nm);
    el("rect",{x:L,y:y,width:Math.max(sx(v)-L,2),height:14,rx:3,class:"fam"+f},g);
    txt(g,{x:sx(v)+6,y:y+12,"font-size":"11","font-weight":"600"},"$"+v.toFixed(2)+" · "+sh)});
  const ly=y0+rows.length*rh+34;
  Object.entries(fam).forEach(([k,t],q)=>{const lx=(q%3)*360,lyy=ly+Math.floor(q/3)*18;el("rect",{x:lx,y:lyy-9,width:10,height:10,rx:2,class:"fam"+k},svg);txt(svg,{x:lx+14,y:lyy,"font-size":"10.5",class:"sec"},t)});
  svg.setAttribute("viewBox",`0 0 1080 ${ly+34}`);
  bindTips(svg);
})();
/* C. cache lifetime: net per life, and which rule picks what */
(function(){
  const svg=$("#cnet"),L=170,R=980;
  const T=[["authors","14 lives",-0.26,-0.10,0.25,-0.02,0.39,"5/14","2.29 / 2.30"],["verifiers","14 lives",-0.16,-0.13,0.08,-0.09,0.10,"3/14","0.65 / 0.74"],["explorers","9 lives",-0.27,-0.21,0.11,-0.13,0.19,"2/9","0.87 / 1.01"]];
  const mn=-0.4,mxv=0.4,sx=v=>L+(R-L)*(v-mn)/(mxv-mn);
  const top=26;
  for(let v=-0.4;v<=0.401;v+=0.1){el("line",{x1:sx(v),y1:top-8,x2:sx(v),y2:top+T.length*52-6,stroke:"var(--grid)"},svg);txt(svg,{x:sx(v),y:top-12,"text-anchor":"middle","font-size":"11",class:"muted"},(v>0.001?"+":"")+(Math.abs(v)<0.01?"0":v.toFixed(1)))}
  el("line",{x1:sx(0),y1:top-8,x2:sx(0),y2:top+T.length*52-6,stroke:"var(--text-primary)","stroke-width":1.5},svg);
  txt(svg,{x:sx(0)-6,y:top+T.length*52+8,"text-anchor":"end","font-size":"11.5",style:"fill:var(--s1)","font-weight":"600"},"◂ 5 minutes pays");
  txt(svg,{x:sx(0)+6,y:top+T.length*52+8,"font-size":"11.5",style:"fill:var(--s2)","font-weight":"600"},"1 hour pays ▸");
  T.forEach(([n,lv,p10,med,p90,mean,sd,pg,cc],i)=>{const y=top+i*52+14;
    const g=el("g",{"data-tip":`${n} (${lv}): net of 1 hour over 5 minutes per life, USD. 10th ${p10}, median ${med}, 90th ${p90}; mean ${mean}, sd ${sd}. Lives that gain: ${pg}. Mean cache cost per life, 5-minute / 1-hour: ${cc} USD. ESTIMATE (explorer-w08-c, tables 3).`},svg);
    el("rect",{x:0,y:y-18,width:1080,height:48,class:"hit"},g);
    txt(g,{x:0,y:y,"font-size":"13","font-weight":"600"},n);txt(g,{x:0,y:y+16,"font-size":"11",class:"sec"},lv+" · cache "+cc+" USD/life");
    el("line",{x1:sx(p10),y1:y-2,x2:sx(p90),y2:y-2,stroke:i?"var(--text-muted)":"var(--s2)","stroke-width":6,"stroke-linecap":"round","stroke-opacity":.6},g);
    el("line",{x1:sx(med),y1:y-11,x2:sx(med),y2:y+7,stroke:"var(--text-primary)","stroke-width":2},g);
    el("circle",{cx:sx(mean),cy:y-2,r:5,fill:"var(--text-primary)"},g);
    txt(g,{x:sx(p90)+10,y:y+2,"font-size":"11.5","font-weight":"600"},`mean ${mean>0?"+":"−"}${Math.abs(mean).toFixed(2)} · ${pg} gain`)});
  // PI panel
  const y=top+T.length*52+46,Rp=980,mnp=-2,mxp=30,sp=v=>L+(Rp-L)*(v-mnp)/(mxp-mnp);
  txt(svg,{x:0,y:y-14,"font-size":"12","font-weight":"600",class:"sec"},"PI, its own axis (USD per session)");
  for(let v=0;v<=30;v+=5){el("line",{x1:sp(v),y1:y-6,x2:sp(v),y2:y+26,stroke:"var(--grid)"},svg);txt(svg,{x:sp(v),y:y+40,"text-anchor":"middle","font-size":"11",class:"muted"},"+"+v)}
  const g=el("g",{"data-tip":"PI (Opus, 3 sessions): net of 1 hour over 5 minutes per session, USD. 10th +2.50, median +13.13, 90th +27.17; mean +14.55, sd 15.47. The sessions were +13.1, +30.7 and −0.16, so n = 3 says little about the next one. Cache cost per session 27.4 (5-minute) against 12.9 (1-hour). ESTIMATE (explorer-w08-c)."},svg);
  txt(g,{x:0,y:y+8,"font-size":"13","font-weight":"600"},"PI");
  el("line",{x1:sp(2.5),y1:y+4,x2:sp(27.17),y2:y+4,stroke:"var(--s1)","stroke-width":6,"stroke-linecap":"round","stroke-opacity":.6},g);
  el("line",{x1:sp(13.13),y1:y-5,x2:sp(13.13),y2:y+13,stroke:"var(--text-primary)","stroke-width":2},g);
  el("circle",{cx:sp(14.55),cy:y+4,r:5,fill:"var(--text-primary)"},g);
  txt(g,{x:sp(27.17)+10,y:y+8,"font-size":"11.5","font-weight":"600"},"mean +14.55 · 2 of 3");
  svg.setAttribute("viewBox",`0 0 1080 ${y+54}`);
  bindTips(svg);
})();
(function(){
  const svg=$("#crules"),L=300,cw=170,rh=36,top=34;
  const types=["authors","verifiers","explorers","PI"];
  const R=[
   ["Expected value (mean net)",["5m","5m","5m","1h"],"mean net −0.02 / −0.09 / −0.13 / +14.55"],
   ["Token share re-written (1h if > 0.385)",["5m","5m","5m","1h"],"0.372 / 0.21 / 0.20 / 0.85"],
   ["Probability of a gain above half",["5m","5m","5m","1h"],"0.36 / 0.21 / 0.22 / 0.67 (n = 3)"],
   ["Worst-case cost ratio (competitive)",["5m","5m","1h","1h"],"1.13 vs 1.56 · 1.09 vs 1.37 · 1.31 vs 1.43 (1h) · 1.04 vs 2.60"],
   ["Expected cost ratio",["5m","5m","5m","1h"],"1.03 vs 1.21 (authors) · 1.01 vs 1.83 (PI)"],
   ["CVaR of regret, 0.8 and 0.9",["1h","5m","5m","1h"],"authors 0.49 vs 0.65 at 0.9"],
   ["Minimax regret in USD",["1h","5m","5m","1h"],"authors max 0.72 vs 1.04 · PI 0.16 vs 30.7"]];
  types.forEach((t,j)=>txt(svg,{x:L+j*cw+cw/2,y:top-12,"text-anchor":"middle","font-size":"12.5","font-weight":"600"},t));
  R.forEach(([nm,cells,tt],i)=>{const y=top+i*rh;
    const g=el("g",{"data-tip":nm+". "+tt+" (explorer-w08-c, table 4, ESTIMATE; waves 5–7)."},svg);
    el("rect",{x:0,y:y-2,width:1080,height:rh-2,class:"hit"},g);
    txt(g,{x:0,y:y+20,"font-size":"12.5"},nm);
    cells.forEach((c,j)=>{el("rect",{x:L+j*cw+4,y:y,width:cw-8,height:rh-8,rx:6,class:c==="1h"?"s2":"s1"},g);
      txt(g,{x:L+j*cw+cw/2,y:y+18,"text-anchor":"middle","font-size":"12.5","font-weight":"700",style:"fill:#fff"},c==="1h"?"1 hour":"5 minutes")})});
  svg.setAttribute("viewBox",`0 0 1080 ${top+R.length*rh+4}`);
  bindTips(svg);
})();

