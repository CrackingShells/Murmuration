| shape | n | median s | p10 | p90 |
|:--|--:|--:|--:|--:|
| bare ls/cat/head/tail/wc/pwd/echo/date/stat/file/test | 3 | 1.02 | 0.91 | 1.02 |
| cd dir && ... | 47 | 1.34 | 0.97 | 2.85 |
| git ... | 54 | 1.47 | 1.09 | 2.54 |
| other | 93 | 1.60 | 1.00 | 5.69 |
| pipe/chain of read-only words | 42 | 1.24 | 0.98 | 2.35 |
| runs a program (python/uv/cargo/sleep/claude/heredoc) | 1623 | 1.72 | 1.11 | 51.45 |
| single grep/sed/awk/find... | 7 | 0.99 | 0.91 | 1.07 |
| all | 1869 | 1.66 | 1.08 | 43.49 |

by wave, bare commands only:
- w5: n=1 median 1.02 s p10 1.02 p90 1.02
- w6: n=2 median 0.98 s p10 0.91 p90 0.91
