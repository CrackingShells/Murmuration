// Times posix_spawn+wait4 of two guard commands on the same stdin payload, interleaved pairs, order flipped each round; inputs: arms file (2 lines: name TAB argv0 TAB argv1 ...), payload list (one path per line), rounds N, optional warmup; output: JSONL on stdout, one row per run {arm, payload, round, wall_ns, user_us, sys_us, rc, load1}. Derived from __instrumenta__/w07a_spawn_bench.c with stdin read from the payload file.
// build: clang -O2 -o w07c6_pair_bench w07c6_pair_bench.c   usage: w07c6_pair_bench ARMS PAYLOADS ROUNDS [WARMUP]   (round r uses payload r mod count; payload order in the list is the sample's order)
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <time.h>
extern char **environ;
#define MAXA 16
#define MAXP 4096
static char *names[2]; static char *argvs[2][MAXA]; static char *payloads[MAXP]; static int np;
static unsigned long long now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
int main(int argc, char **argv){
  if(argc<4){fprintf(stderr,"usage: ARMS PAYLOADS ROUNDS [WARMUP]\n");return 2;}
  FILE *f=fopen(argv[1],"r"); if(!f){perror("arms");return 2;}
  char line[4096]; int na=0;
  while(fgets(line,sizeof line,f)&&na<2){
    line[strcspn(line,"\n")]=0; if(!line[0]) continue;
    char *p=line; char *tok=strsep(&p,"\t"); names[na]=strdup(tok); int a=0;
    while((tok=strsep(&p,"\t"))&&a<MAXA-1) argvs[na][a++]=strdup(tok);
    argvs[na][a]=NULL; na++;
  }
  FILE *g=fopen(argv[2],"r"); if(!g){perror("payloads");return 2;}
  while(fgets(line,sizeof line,g)&&np<MAXP){ line[strcspn(line,"\n")]=0; if(line[0]) payloads[np++]=strdup(line); }
  int N=atoi(argv[3]); int W=argc>4?atoi(argv[4]):2;
  for(int r=-W;r<N;r++){
    double la[3]; getloadavg(la,3);
    const char *pl=payloads[(r>=0?r:0)%np];
    for(int k=0;k<2;k++){
      int c=(k+(r>=0?r:-r))%2; // order flips each round
      posix_spawn_file_actions_t fa; posix_spawn_file_actions_init(&fa);
      posix_spawn_file_actions_addopen(&fa,0,pl,O_RDONLY,0);
      posix_spawn_file_actions_addopen(&fa,1,"/dev/null",O_WRONLY,0);
      posix_spawn_file_actions_addopen(&fa,2,"/dev/null",O_WRONLY,0);
      pid_t pid; int st; struct rusage ru;
      unsigned long long t0=now();
      int e=posix_spawn(&pid,argvs[c][0],&fa,NULL,argvs[c],environ);
      if(e){ if(r>=0) printf("{\"arm\":\"%s\",\"payload\":\"%s\",\"round\":%d,\"wall_ns\":%llu,\"user_us\":0,\"sys_us\":0,\"rc\":-2,\"err\":%d,\"load1\":%.2f}\n",names[c],pl,r,now()-t0,e,la[0]); posix_spawn_file_actions_destroy(&fa); continue; }
      wait4(pid,&st,0,&ru);
      unsigned long long t1=now();
      if(r>=0) printf("{\"arm\":\"%s\",\"payload\":\"%s\",\"round\":%d,\"wall_ns\":%llu,\"user_us\":%ld,\"sys_us\":%ld,\"rc\":%d,\"load1\":%.2f}\n",names[c],pl,r,t1-t0,(long)(ru.ru_utime.tv_sec*1000000+ru.ru_utime.tv_usec),(long)(ru.ru_stime.tv_sec*1000000+ru.ru_stime.tv_usec),WIFEXITED(st)?WEXITSTATUS(st):-1,la[0]);
      posix_spawn_file_actions_destroy(&fa);
    }
  }
  return 0;
}
