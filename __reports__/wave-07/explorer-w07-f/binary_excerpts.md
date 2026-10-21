# Code excerpts from Claude Code 2.1.304 (strings of the native binary; offsets are into 'strings -a -n 8' output)

## pattern: function e0o\(\)\{
@18886063: dr}from"/$bunfs/root/chunk-qwytg6a7.js";function e0o(){if((dr()||{}).permissions?.disableBypassPermissionsMode==="disable")return"Bypass permissions mode was disabled by settings";return}function oC(){return e0o()!==void 0}\nexport{e0o,oC};\n// @bun @bytecode\n// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.\n// By using Claude Code, you agree that all code acceptance or rejection decisions you make,\n// and the associated conversations in context


## pattern: managedSourcesBehavior:\(\)=>N
@14766294: er, still filtered restrictive-only).`),managedSourcesBehavior:()=>N(["first-wins","merge"]).optional().describe('Controls how the managed settings sources compose. "first-wins" (default): the highest-priority source present (server-managed > MDM (managed plist / HKLM) > managed-settings.json) is the managed tier alone. "merge": every present source deep-merges with fixed '+"precedence server-managed > MDM > managed-settings.json \u2014 scalars "+"take the highest source's value (a r


## pattern: if\(E\)if\(Wln\("bypassPermissions"\)\)
@18133642: ved)"):void 0,x=c?O?.mode??YR(c):void 0;if(E)if(Wln("bypassPermissions"))h=zgt,p.push("default");else p.push("bypassPermissions");if(u){let g=ne(u,y,"auto mode killswitch active (override- or payload-served) \u2014 falling back to default");if(g){if(g.unconsented)h=zgt;p.push(g.mode)}}if(m)if(m==="auto"&&y)t("agent frontmatter requested auto mode but circuit breaker active \u2014 falling through",{level:"warn"});else if(x&&$$(m,x)===void 0)t(`agent frontmatter permissionMode "${m}" ignore


## pattern: for\(let g of p\)\{if\(g==="bypassPermissions"&&v\)
@18137303: .length===0)h=zgt;p.push(g.mode)}}let M;for(let g of p){if(g==="bypassPermissions"&&v){t("bypassPermissions mode is disabled by settings",{level:"warn"}),h="Bypass permissions mode was disabled by settings";continue}M={mode:g,notification:h};break}let L=!1,P=!1,N,F=!1;if(!M){let g=C&&(!$e(r.CLAUDE_CODE_REMOTE)&&$3n()&&(!n.isNonInteractiveSession||mh()||k("tengu_moss_anchor",!1))||$e(r.CLAUDE_CODE_BRIDGE_CHILD_AUTO_DEFAULT)),_="default";if(g){let w=cDr(),D=$e(r.CLAUDE_CODE_BRIDGE_CHILD_AUTO_DEFAULT);if


## pattern: se=\(dr\(\)\|\|\{\}\)\.permissions\?\.disableBypassPermissionsMode
@31388802: te.set(G,{path:G,source:"session"});let se=(dr()||{}).permissions?.disableBypassPermissionsMode==="disable",Z=d&&u!=="bypassPermissions"&&!se&&!n&&Wln("bypassPermissions");if(Z)i("tengu_bg_allow_bypass_unconsented_ignored",{}),b.push(DIn);let Ee=(u==="bypassPermissions"||d&&!Z)&&!se&&!n&&!0,ne=z()&&A!==void 0&&A.hostFiles.serving("workspace")==="host"?{strictPersistedTrust:await n1o(A)}:{},U=lz(ne),X=[...T,...V].map(jn),_e=X.some(ce),Me=X.some((l)=>l.toolName===We)||U.some((l)=>l.ruleBehavior==="deny"&&l.ruleV


## pattern: function ft\(\)\{return vm\(\)\.settings\|\|\{\}\}var dr=ft
@15401718: t:e.reduce((s,{keys:E})=>s+E.length,0)}}function ft(){return vm().settings||{}}var dr=ft;function kjr(){er();let e=[];for(let n of Fo()){let r=me(n);if(r&&Object.keys(r).length>0)e.push({source:n,settings:r})}return{effective:ft(),sources:e}}function VR(e){let n=Fo();for(let r=n.length-1;r>=0;r--){let s=n[r];if(me(s)?.[e]!==void 0)return s}return null}function vm(){let e=gs(),n=e.mergedSettings;if(n!==null)return n;uo("loadSettingsFromDisk_start");let r=EWr(w());return uo("loadSettingsFromDisk_end"),e.m


## pattern: Ze=\["managedSourcesBehavior"
@14796582: ustomization",...Wo().map((e)=>e.key)]),Ze=["managedSourcesBehavior","wslInheritsWindowsSettings"];function zt(e){return L(e)&&Object.values(e).every(zt)}function nGo(e){let n=e.wslInheritsWindowsSettings;if(n===void 0||n===null)return"disarmed";let r=yC(n);return r===!0?"armed":r===!1?"disarmed":"unreadable"}function Nn(e){let n=e.source==="hostPattern"?e.hostPattern:e.source==="pathPattern"?e.pathPattern:null;if(n!==null&&!ahn(n))return`${e.source}: regex does not compile; the entr


## pattern: function wr\(e,n,r,s\)\{let i=e\[0\]
@14937193: settingsNotHeld,heldInTheHostsPlace:Dr}}function wr(e,n,r,s){let i=e[0];if(!i)return{admin:null,merged:!1};let{managedSourcesBehavior:c,...p}=i,g=n==="merge"&&e.length>=2;if(!g&&s===0)return{admin:c===void 0?i:p,merged:!1};let m=e.slice(g?1:e.length-s).map((S,b)=>{let y=g&&r&&b===0,A=y?{...S}:Go(S,pXs());if(!y){for(let H of qii)if(qR(A,H)!==void 0)gO(A,H,void 0)}let R=qR(A.sandbox,["enabledPlatforms"]);if(Array.isArray(R)&&R.includes(M()))gO(A,["sandbox","enabledPlatforms"],void 0);else


## pattern: hook_event_name:"UserPromptSubmit",prompt:r
@26439090: ",n,e.id))return;let w={...mu(e,zm(),s),hook_event_name:"UserPromptSubmit",prompt:r,...!1,session_title:hg(e.id)};yield*Ax({session:e,hookInput:w,toolUseID:eEn(),signal:h,timeoutMs:swo,sessionHooks:n,storageV5:y,credentials:b})}async function*cct(e,n,r,s,h={}){let y=r.agentId??r.session.id;if(!h.managedHooksOnly&&!SM("UserPromptSubmit",r.sessionHooksRegistry,y))return;let b={...mu(r.session,zm(),n),hook_event_name:"UserPromptSubmit",prompt:e,...!1,session_title:hg(r.session.id)};yield*Ax({session:r


## pattern: function mu\(e,n,r,s\)\{let h=s\?\.agentType
@26445640: ction Nnt(e){return Z()?e.project:ko(e)}function mu(e,n,r,s){let h=s?.agentType??Ak(),y=s?.options?.mainLoopModel,b=Od(s?.getAppState?.()??{},y,{withHold:WHr(s??{})}),w=xy(s?.permissionLayers),H=y&&s?.getAppState&&Kb(y)?{level:Ez(y,b,w)}:void 0,q=n??"",V=s?.remoteCall;if(V!==void 0)return{session_id:`served:${(YUn.test(V.origin.callerSessionId??"")?V.origin.callerSessionId:void 0)??"unknown"}`,transcript_path:"",cwd:q,permission_mode:r,agent_id:s?.agentId,effort:H};return{session_id:e.id,transc


## the server-managed settings cache (keys only)
['channelsEnabled'] size bytes 29
