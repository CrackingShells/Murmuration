---
type: findings
wave: wave-07
author: explorer-w07-f
date: 2026-10-22
version: v0
decision-required: intervene
---

# The managed setting, and what separates a session's message from the user's words: findings (v0)

Left the brief: no. Both questions were read-only. Nothing was run with a bypass flag; no settings file was touched; no headless `claude` was started. The two flag-naming test commands for the user are in this `.md` only.

## Result

1. **The managed file was probably never the managed tier.** Claude Code 2.1.304 chooses ONE managed source, "first-wins": server-managed settings, then MDM, then `managed-settings.json`; the file is dropped whenever a higher source holds any content. This machine has a server-managed cache, `~/.claude/remote-settings.json`, holding `{"channelsEnabled": true}` (29 bytes, refreshed 00:30 JST today), and `channelsEnabled` counts as policy content in the code. So `permissions.disableBypassPermissionsMode` in the file is never read into the merged settings that the check uses. The enforcement itself is not interactive-only and not mode-switch-only: the same check runs at startup for the flag in every entry point. CHECKED by reading (strings of the native binary, tier-selection code and the docs agree); not run end to end.
2. **The transcript field is what was enforced.** The run's transcript also holds the platform's own reminder to the model, "While bypass permissions mode is active", so the session was in bypass mode, not merely labelled so. But the run made no tool call, so no skipped permission check was observed. MEASURED (read) for the field and the reminder.
3. **Item 28: the transcript marks who sent a prompt; the hook payload does not.** Typed prompts have `origin: {"kind":"human"}` and `turnOrigin: "human"`. This session's first message has `promptSource:"sdk"`, `turnOrigin:"sdk"` and no `origin`. The hook payload has no such field, but it has `prompt_id`, equal to the transcript record's `promptId`. Rule for `user_words.py`: store a prompt only if the transcript's user record with that `prompt_id` has `origin.kind == "human"`. On the lab's own transcripts it keeps all 20 typed prompts and drops every sdk-origin one (476, mostly headless probe runs). CHECKED over the transcripts below; the timing of the lookup at hook time is only partly measured (see Not covered).

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Managed tier choice | `managedSourcesBehavior` default "first-wins": "the highest-priority source present (server-managed > MDM (managed plist / HKLM) > managed-settings.json) is the managed tier alone" (the binary's own description of the key) | CHECKED (read) | `binary_excerpts.md`, pattern `managedSourcesBehavior:` |
| Tier code | `wr(e,n,r,s)`: with `n !== "merge"` it returns `e[0]` only; `e` lists the tiers in the order remote, MDM, file; the remote tier wins ties (`q = p!==null && k>=Math.max(x,B)`) | CHECKED (read) | `binary_excerpts.md`, pattern `function wr(` |
| Docs agree | "Within the managed tier, the first source that delivers a non-empty configuration wins [...] if server-managed settings deliver any keys at all, endpoint-managed settings are ignored entirely"; "Run `/status` to see which managed source is active" | CITED, from a community mirror of the docs, https://github.com/pjbrito/claude-code-docs/blob/main/content/en/docs/claude-code/server-managed-settings.md via context7 `/pjbrito/claude-code-docs`; not fetched from code.claude.com: UNVERIFIED against the official page | context7 query 2026-10-22 |
| This machine's server tier | `~/.claude/remote-settings.json` = `{"channelsEnabled": true}`; signature files and `synced-at` 1792596601495 (2026-10-21 15:30 UTC) | MEASURED (read) | `ls -la ~/.claude/remote-settings.json*`, `python3 -I` key listing, in `binary_excerpts.md` |
| `channelsEnabled` is policy content | The binary lists it as a managed key ("have an administrator set channelsEnabled: true in managed settings"); the "has content" test is `Object.keys(e).some(n => !Ze.includes(n))` with `Ze = ["managedSourcesBehavior","wslInheritsWindowsSettings"]` | CHECKED (read) | `binary_excerpts.md`, pattern `Ze=[` |
| The check is not interactive-only | Startup mode resolver: `if(g==="bypassPermissions"&&v){warn("bypassPermissions mode is disabled by settings"); h="Bypass permissions mode was disabled by settings"; continue}`, `v = settings.permissions?.disableBypassPermissionsMode==="disable"`, `settings = dr()` (= `getSettings_DEPRECATED`, the cached merged settings); no `isNonInteractiveSession` condition. The flag is pushed as a candidate (`if(E) ... p.push("bypassPermissions")`) and then dropped when `v` holds | CHECKED (read) | `binary_excerpts.md` |
| The check is not mode-switch-only | Same flag feeds `isBypassPermissionsModeAvailable` (`Ee=(u==="bypassPermissions"||d&&!Z)&&!se&&!n`) and the switch refusal ("rejected - mode is not available (disableBypassPermissionsMode set, ...)") | CHECKED (read) | binary offsets 31388829, 19501077 |
| What the run recorded | user record of `3c5c3eec`: `permissionMode: bypassPermissions`, `promptSource: sdk`, `entrypoint: sdk-cli`, version 2.1.304; attachment `auto_mode` with `bypass: true` and the reminder "While bypass permissions mode is active"; the reply was "ok", no tool call | MEASURED (read) | `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-blissful-villani-34edd8/3c5c3eec-45b8-4ffb-a8c7-1a9c17ac12e5.jsonl`, records 6 and 13 |
| UserPromptSubmit payload fields | Recorded payloads: `session_id, prompt_id, permission_mode, prompt, hook_event_name`, plus `cwd`, `transcript_path`, `scratchpad_dir`, `agent_type`, `session_title` in later builds. No origin, source or sender field. The code builds it as `{...mu(session), hook_event_name, prompt, session_title}` and `mu` returns `session_id, transcript_path, cwd, scratchpad_dir, prompt_id, permission_mode, agent_id, agent_type, effort` | MEASURED (62 + 29 recorded events, 2.1.296; 2 events with transcript_path, 2.1.30x) and CHECKED (read, 2.1.304) | `__reports__/platform_probes/evidence/v1_hook_inputs.jsonl`, `__reports__/platform_probes/evidence/hook_inputs.jsonl`, `__reports__/reflective_run/w04/author-w04-4/derived/recorded_payloads_rec1.jsonl`, `binary_excerpts.md` |
| Docs on the payload | "UserPromptSubmit hooks receive the `prompt` field containing the text the user submitted", plus common fields `session_id, transcript_path, cwd, permission_mode` | CITED, community mirror (same context7 library), https://github.com/pjbrito/claude-code-docs/blob/main/content/en/docs/claude-code/hooks.md; UNVERIFIED against the official page | context7 query 2026-10-22 |
| This session's first user record | `promptSource: sdk`, `turnOrigin: sdk`, no `origin`, `entrypoint: claude-desktop`, `permissionMode: auto`, `turnPosition.promptIndex: 0`; text opens with two `<system-reminder>` blocks, then "Background (from the session that started this one):" | MEASURED (read) | `this_session_origin.txt`; `f023f552-...jsonl` record 6 |
| A typed prompt | `promptSource: sdk`, `turnOrigin: human`, `origin: {"kind":"human"}`, same version and entrypoint | MEASURED (read) | `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-...jsonl` record 232 |
| All origins seen | 90 `sdk/human/human` text records (2.1.304); 512 `sdk/sdk/none` (headless probe runs, spawned sessions); 302 `system/peer/peer` (cross-session, hand-backs); 192 task notifications; 8 `scheduled`; hand-backs carry `origin.kind: peer` or `task-notification` | MEASURED | `prompt_origin_summary.txt` (`__instrumenta__/w07f_prompt_origin.py --summary`) |
| What `user_words.md` holds | Of this checkout's 32 entries, 25 match a transcript record with `origin.kind: human`; 3 do not: "2026-10-21 17:18" and "2026-10-22 00:22" (both the first message of a spawned session, `sdk/sdk/none`) and "2026-10-22 00:12 say ok" (the user's `-p` run, `sdk/sdk/none`, entrypoint `sdk-cli`). Four more have no matching record by their first 50 characters (quoted text, `FYI:`; not checked further) | MEASURED | `words_vs_origin.txt` (`__instrumenta__/w07f_words_vs_origin.py`) |
| Text rule against origin marker | Over 3 lab-session folders (470 transcripts, mostly headless worker and probe runs): text rule stores and origin human 20; text rule stores and not human 476; text rule skips and not human 164; text rule skips and human 0 | MEASURED | `rule_confusion_lab_sessions.txt` (`__instrumenta__/w07f_rule_confusion.py`); the 476 only matter where a headless run starts inside a lab |
| Hook versus record creation | In the 2 recorded payload events whose session transcript survives, the user record's timestamp precedes the hook's end time by 0.205 s (first prompt, hook took 43 ms) and 0.890 s (a later prompt, hook took 196 ms); so the record was created before the hook started. Whether it was already flushed to disk is not shown | MEASURED, n = 2 | `recorded_payloads_rec1.jsonl` rows 1 and 2 against `1f39bc08` transcript |

## Proposed rule for `scripts/user_words.py` (not applied; `scripts/` untouched)

```
def human_prompt(event):
    # event: the hook payload; uses transcript_path and prompt_id
    pid = event.get("prompt_id"); tp = event.get("transcript_path")
    if not pid or not tp: return None                  # unknown
    deadline = now + 0.3 s
    while True:
        rec = last user record in the tail (last 256 KB) of tp with promptId == pid
        if rec: return (rec.get("origin") or {}).get("kind") == "human"
        if now > deadline: return None
        sleep 25 ms
```

`handle` then stores the prompt when `human_prompt(event)` is `True`; when it is `False` it skips; when it is `None` (no `prompt_id`, no transcript, record not found in time) it falls back to today's text rule. Reason: the text rule cannot see the difference (the spawned session's message opens with the same two system-reminder blocks as a typed prompt in a worktree), while `origin.kind` is the platform's own marker. Cost: one file-tail read, at most 0.3 s on a miss, one hook-start, no new process. CONJECTURE until the lookup is tried inside a hook in Desktop: the record may or may not be on disk when the hook starts.

## Tests for the user (commands for the user, not for any worker)

All outside any lab folder, e.g. in `/private/tmp/bypass-test`.

1. Which managed source is active (read-only): in an interactive `claude`, type `/status` and read the managed-source line. Or `cat ~/.claude/remote-settings.json`: any key at all means the file in `/Library/Application Support/ClaudeCode/` is not the managed tier. Prediction if this report is right: `/status` names server-managed settings, not the file.
2. Did the run actually skip permission checks (behaviour, not label): `cd /private/tmp/bypass-test && claude -p "Run the shell command: touch /private/tmp/bypass-test/made-by-flag. Then say done." --dangerously-skip-permissions --debug-file /private/tmp/bypass-test/dbg.txt`. Then `ls /private/tmp/bypass-test/made-by-flag` and `cat /private/tmp/bypass-test/dbg.txt | grep -i bypass`. File made and no "disabled by settings" line: the flag was honoured, the managed file did not apply. No file and the line "bypassPermissions mode is disabled by settings": the file applied, and the first run's transcript field needs another explanation. Run the same without the flag as the control.
3. Make the setting bind (only if test 1 names server-managed settings): the key has to be in the winning tier, so it belongs in the server-managed settings in the organisation's admin console (or `managedSourcesBehavior: "merge"` there, which lets the file's keys merge). Clearing the server config instead would let the file apply, but the cached copy lasts until the next successful fetch (docs, CITED as above). Repeat test 2 afterwards. Whether this account's admin console is the user's to edit is not known.

## Worst-fitting case

For the managed-setting explanation: the debug run (00:13) printed "this machine has managed settings" and "Settings changed from policySettings", which fits both explanations (a file-only tier and a server tier with the file dropped). Its raw output is not on disk (the PI's note holds three quoted lines), so the log line that would name the source, if there is one, was not read. Also unverified: whether a `-p` start of the `sdk-cli` entrypoint loads the cached server-managed settings at all; the code path read (`o8` reading the cache via `Q_`) has no entry-point condition, but a read is not a run.

For the origin rule: the 4 entries of `user_words.md` with no transcript match by their first 50 characters, and the 00:08 entries, which are `!`-prefixed terminal commands (`<bash-input>`), recorded with `origin: human`. They are the user's, but they are commands, not words to the lab; the origin rule keeps them, as today's text rule does.

## Not covered

- No end-to-end run of the bypass check and no `/status` reading (both would need the user's shell or a `claude` run, which the brief forbids). The three tests above settle it.
- Whether the server-managed cache was applied by the 00:12 `-p` run, and whether the account is an organisation account whose admin controls it: inferred from the cache, the signature files, `policy-limits.json` and a `credential_org` attachment type in the transcript (not opened); no admin-console state was seen.
- The hook-time lookup (rule above): record creation precedes hook start (n = 2); on-disk presence at hook start was not measured. A probe hook that logs `found/not found` for `prompt_id` in the transcript tail would settle it; none was run (registering a hook is a settings change, and a headless run is forbidden for this brief).
- The headless `-p` case ("say ok", entrypoint `sdk-cli`): it also reaches `user_words.md` today. The origin rule drops it (`sdk/sdk/none`), which the user may or may not want, since the words are the user's own, typed as a command argument. Not decided.
- The plugin's own permission guard (w06-c13) was not touched: the finding supports keeping it, since the file is not binding on this account.
- Official docs pages were not fetched (no downloads allowed; context7 returned a community mirror).

## Steering questions

- [now] Can the user run test 1 (`/status`) and test 2 above, and say what the managed-source line shows? That decides whether the guard's Bash row can ever be removed.
- [now] Should the origin rule treat the user's own `-p` prompts (entrypoint `sdk-cli`, `sdk/sdk`) as words to keep? The rule as written drops them.
- [now] May an author file the rule as a claim for `scripts/user_words.py` (with the probe hook that measures on-disk presence as its experiment)?

## Pointers

- `__reports__/wave-07/explorer-w07-f/binary_excerpts.md`: code excerpts (`__instrumenta__/w07f_binary_window.py <binary> <regex>`; the binary is `/Users/hacker/.local/share/claude/versions/2.1.304`; cache of its strings in `/private/tmp/murmuration-w07/explorer-w07-f/`, not committed).
- `__reports__/wave-07/explorer-w07-f/prompt_origin_summary.txt`: `python3 -I __instrumenta__/w07f_prompt_origin.py --summary <transcripts of the Murmuration and combinatorics project folders>`.
- `__reports__/wave-07/explorer-w07-f/this_session_origin.txt`: `python3 -I __instrumenta__/w07f_prompt_origin.py <f023f552 transcript>`.
- `__reports__/wave-07/explorer-w07-f/words_vs_origin.txt`: `python3 -I __instrumenta__/w07f_words_vs_origin.py __statera__/user_words.md <transcripts>`.
- `__reports__/wave-07/explorer-w07-f/rule_confusion_lab_sessions.txt` and `rule_confusion_worktree_sessions.txt`: `python3 -I __instrumenta__/w07f_rule_confusion.py <transcripts>`.
- Scripts: `__instrumenta__/w07f_binary_window.py`, `w07f_prompt_origin.py`, `w07f_words_vs_origin.py`, `w07f_rule_confusion.py` (all `@` the commit that adds them).
- Background read: `__reports__/wave-06/research-pi/managed_setting_check.md`, `permission_mechanisms.md`; `__statera__/synthesis.md` item 28.
