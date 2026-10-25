## M5 (per record vs per worker; records before 2026-10-25T00:00Z)
records: start 159, end 171, raise 36, note 102; unique workers with a start 91, with an end 91, starts with no end 0
end records: n 171, median frac 0.38, max 0.92, over 1.0: 0, with stops>0: 0
per worker (last end record): n 91, median frac 0.36, max 0.92, over 1.0 B_at_end: 0, share of workers with at least one raise: 28 of 91
workers with a raise: n 28; spend at last end / budget before their first raise: median 0.57, max 1.10; over 1.0 of the pre-raise budget: 1
    ('xenodochial-', 'author-w07-5', 6.614073, 6.0, 1.1023455, 2)
    ('xenodochial-', 'author-w07-2', 2.877422, 3.0, 0.9591406666666668, 1)
    ('murmuration-', 'author-w08-5', 5.629761, 6.0, 0.9382935, 1)
    ('blissful-vil', 'reproducer-w06-7', 2.742161, 3.0, 0.9140536666666667, 1)
    ('murmuration-', 'explorer-w08-h', 4.412929, 5.0, 0.8825858, 1)
    ('murmuration-', 'reproducer-w08-5', 2.468418, 3.0, 0.8228059999999999, 1)
time: per worker median t_frac 0.47, over 1.0 T_at_end: 2 of 91

## M7 (per dispatch: the first, non-resumed start of each agent_id; merge 3d5147a = 2026-10-24T03:18:27+09:00)
| side | dispatches | with meta name | in a same-type batch (starts within 5 s) | wrong name | wrong name, in a batch | name_unconfirmed |
|:--|--:|--:|--:|--:|--:|--:|
| before | 86 | 66 | 29 | 14 | 14 | 0 |
| after | 5 | 5 | 2 | 0 | 0 | 0 |

start records (the explorer's unit, resumes included): 126 with a meta name, 14 wrong name, of which resume starts 0
wrong-name dispatches by source: {'unknown': 10, 'brief': 4}
after-merge batches (size, names):
    2026-10-24T14:22:53 murmuration-wa explorer explorer-w09-b meta: explorer-w09-b 
    2026-10-24T14:22:53 murmuration-wa explorer explorer-w09-a meta: explorer-w09-a 

live wave-9 start records (not frozen; as of the run):
    2026-10-25T23:29:49 start murmuration-explorer-a970a160 meta: explorer-w09-e B=3.0 unconfirmed True 
    2026-10-25T23:29:49 start explorer-w09-c meta: explorer-w09-c B=8.0  
    2026-10-25T23:29:49 start explorer-w09-d meta: explorer-w09-d B=5.0  
    2026-10-25T23:29:50 start explorer-w09-f meta: explorer-w09-f B=4.0  
    2026-10-25T23:29:50 named explorer-w09-e meta: explorer-w09-e B=None  
    2026-10-25T23:39:32 start author-w09-1 meta: author-w09-1 B=3.0  
