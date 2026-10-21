# Computes request-0 usage and the loaded tool names of a Desktop session, from its transcript JSONL (argv[1]), to stdout (no account identifiers printed).
import json, sys
first = None; shape = None
for l in open(sys.argv[1]):
    r = json.loads(l)
    if r.get('type') == 'api-request-shape' and shape is None:
        shape = r
    if r.get('type') == 'assistant' and first is None:
        first = r
u = first['message']['usage']
tot = u['input_tokens'] + u['cache_creation_input_tokens'] + u['cache_read_input_tokens']
print('version', shape.get('version'), 'request0_ts', first['timestamp'])
print('input', u['input_tokens'], 'cache_write', u['cache_creation_input_tokens'], 'cache_read', u['cache_read_input_tokens'], 'total', tot)
tools = shape['shape'].get('tools', [])
print('loaded_tools', len(tools), 'tools_json_chars', len(json.dumps(tools)), 'system_json_chars', len(json.dumps(shape['shape'].get('system'))))
print('names', ','.join(t.get('name', '?') for t in tools))
