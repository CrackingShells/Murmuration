// A stand-in for the guard binary that fails on purpose, for w07-c6 g2: call 1 exits 101 (a crash), call 2 sleeps 60 s (a hang past the hook's 20 s timeout), call 3 and later run the real binary with the same arguments; the call count lives in the file COUNTER. Build: clang -O2 -DCOUNTER='"/path/counter"' -DREAL='"/path/real"' -o stub w07c6_stub.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc, char **argv) {
  FILE *f = fopen(COUNTER, "r"); int n = 0;
  if (f) { if (fscanf(f, "%d", &n) != 1) n = 0; fclose(f); }
  n++;
  f = fopen(COUNTER, "w"); if (f) { fprintf(f, "%d\n", n); fclose(f); }
  if (n == 1) { fprintf(stderr, "stub: simulated crash\n"); return 101; }
  if (n == 2) { sleep(60); return 0; }
  argv[0] = REAL; execv(REAL, argv); return 127;
}
