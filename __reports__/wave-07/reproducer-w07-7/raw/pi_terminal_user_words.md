# The user's words

Prompts as the user typed them, each under its date. Written by the lab's hook and by `/lab`. Read it; never edit it.

## 2026-10-22 02:22

What is 1+1? (throwaway smoke lab)

## 2026-10-22 02:22

Smoke test of the lab's hooks, on a throwaway folder. In ONE message call the Agent tool twice so both workers run at once: (1) subagent_type `murmuration:explorer`, name `explorer-w99-1`, prompt exactly <<<Your name is explorer-w99-1.
Budget: USD 0.30
Time: min 3
Run Bash `sleep 30` four times, each as its own separate call, one after another (about two minutes in all). Then use Write to create the file __reports__/wave-99/explorer-w99-1/00-findings_v0.md containing the single line `smoke`. Then call SubagentHandback with message `done`.>>> ; (2) subagent_type `murmuration:author`, name `author-w99-2`, prompt exactly <<<Your name is author-w99-2.
Budget: USD 0.30
Time: min 3
Run Bash `echo author-ok`. Then use Write to create the file __pondus__/w99-c1.md containing the single line `# w99-c1: smoke`. Then call SubagentHandback with message `done`.>>> (markers excluded). Wait for both. Last step: reply with one line saying what each worker handed back.
