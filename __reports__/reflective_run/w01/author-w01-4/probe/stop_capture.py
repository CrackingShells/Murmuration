#!/usr/bin/env python3
"""PROTOTYPE of capture at Stop (not proposed for merge; it exists to measure the trade-off).

Stop payload: transcript_path, prompt_id, cwd. The transcript record of the turn's prompt is there by then
(explorer-w01-f run4). Takes the turn's `user` record with origin.kind == "human" and, after it, the
`queued_command` attachments typed by the human (a prompt sent while the turn runs is NOT a `user` record:
MEASURED, case7). Drops text blocks that start with <system-reminder>. Appends to $STOP_OUT.
Undocumented fields relied on: promptId, origin.kind, isMeta, attachment.type == queued_command, commandMode.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "patched", "scripts"))
import user_words as uw  # noqa: E402


def blocks(content):
    if isinstance(content, str):
        return [content]
    return [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]


def turn_texts(transcript, prompt_id):
    seen, out = False, []
    for line in open(transcript):
        r = json.loads(line)
        if r.get("isSidechain"):
            continue
        if r.get("type") == "user" and r.get("promptId") == prompt_id and r.get("toolUseResult") is None:
            seen = True
            if (r.get("origin") or {}).get("kind") == "human" and not r.get("isMeta"):
                out.append((r.get("timestamp"), "user_record", blocks(r["message"]["content"])))
        elif seen and r.get("type") == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") == "queued_command" and a.get("commandMode") == "prompt" \
                    and (a.get("origin") or {}).get("kind") == "human":
                out.append((a.get("timestamp"), "queued_command", blocks(a.get("prompt"))))
    return out


def main():
    ev = json.load(sys.stdin)
    log = os.environ["STOP_OUT"]
    for ts, how, bl in turn_texts(ev["transcript_path"], ev.get("prompt_id")):
        keep = [b for b in bl if not b.lstrip().startswith("<system-reminder>")]
        text = uw.strip_injected("\n".join(keep))
        if text.strip():
            open(log, "a").write(json.dumps({"ts": ts, "how": how, "text": text}) + "\n")


if __name__ == "__main__":
    main()
