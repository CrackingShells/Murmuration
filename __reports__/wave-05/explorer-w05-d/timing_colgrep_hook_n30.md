| case | n | wall median ms | wall p90 ms | cpu median ms | rc != 0 |
|:--|--:|--:|--:|--:|--:|
| floor: sh : | 30 | 31.9 | 48.5 | 3.0 | 0 |
| floor: python3 -S -I -c pass | 30 | 54.1 | 76.6 | 10.8 | 0 |
| colgrep_policy PreToolUse Bash, as shipped (uv run --no-project --quiet python) | 30 | 118.8 | 139.5 | 58.4 | 0 |
| colgrep_policy, python3 directly | 30 | 78.4 | 97.8 | 34.4 | 0 |
| colgrep_policy, python3 -S -I | 30 | 72.4 | 95.3 | 28.7 | 0 |
| uv run --no-project --quiet python -c pass | 30 | 107.2 | 129.1 | 46.4 | 0 |
