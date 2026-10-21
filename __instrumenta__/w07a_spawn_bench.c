// Times posix_spawn+wait4 of commands from a cases file, round-robin over cases, in C; inputs: cases file (one case per line: name TAB argv0 TAB argv1 ...; argv0 is the program path, used by execve), rounds N, optional warmup; output: JSONL on stdout, one row per run {case, round, wall_ns, user_us, sys_us, rc, load1}.
// build: clang -O2 -o w07a_spawn_bench w07a_spawn_bench.c   usage: w07a_spawn_bench CASES N [WARMUP] [first]  ("first" = no warmup round and rows are labelled by round, for first-run-of-a-fresh-binary studies)
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <time.h>
extern char **environ;
#define MAXC 1024
#define MAXA 16
static char *names[MAXC]; static char *argvs[MAXC][MAXA]; static int nc;
static unsigned long long now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
int main(int argc, char **argv){
  if(argc<3){fprintf(stderr,"usage\n");return 2;}
  FILE *f=fopen(argv[1],"r"); if(!f){perror("cases");return 2;}
  int N=atoi(argv[2]); int W=argc>3?atoi(argv[3]):2;
  char line[4096];
  while(fgets(line,sizeof line,f)&&nc<MAXC){
    line[strcspn(line,"\n")]=0; if(!line[0]) continue;
    char *p=line; char *tok=strsep(&p,"\t"); names[nc]=strdup(tok); int a=0;
    while((tok=strsep(&p,"\t"))&&a<MAXA-1) argvs[nc][a++]=strdup(tok);
    argvs[nc][a]=NULL; nc++;
  }
  posix_spawn_file_actions_t fa; posix_spawn_file_actions_init(&fa);
  posix_spawn_file_actions_addopen(&fa,0,"/dev/null",O_RDONLY,0);
  posix_spawn_file_actions_addopen(&fa,1,"/dev/null",O_WRONLY,0);
  posix_spawn_file_actions_addopen(&fa,2,"/dev/null",O_WRONLY,0);
  for(int r=-W;r<N;r++){
    double la[3]; getloadavg(la,3);
    for(int k=0;k<nc;k++){
      int c=(k+(r>=0?r:0))%nc; // rotate start so no case is always first in a round
      pid_t pid; int st; struct rusage ru;
      unsigned long long t0=now();
      int e=posix_spawn(&pid,argvs[c][0],&fa,NULL,argvs[c],environ);
      if(e){ if(r>=0) printf("{\"case\":\"%s\",\"round\":%d,\"wall_ns\":%llu,\"user_us\":0,\"sys_us\":0,\"rc\":-2,\"err\":%d,\"load1\":%.2f}\n",names[c],r,now()-t0,e,la[0]); continue; }
      wait4(pid,&st,0,&ru);
      unsigned long long t1=now();
      if(r>=0) printf("{\"case\":\"%s\",\"round\":%d,\"wall_ns\":%llu,\"user_us\":%ld,\"sys_us\":%ld,\"rc\":%d,\"load1\":%.2f}\n",names[c],r,t1-t0,(long)(ru.ru_utime.tv_sec*1000000+ru.ru_utime.tv_usec),(long)(ru.ru_stime.tv_sec*1000000+ru.ru_stime.tv_usec),WIFEXITED(st)?WEXITSTATUS(st):-1,la[0]);
    }
  }
  return 0;
}
