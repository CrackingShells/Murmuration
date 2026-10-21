// Splits one process start into phases, in C: parent stamps t0 (before posix_spawn), t1 (posix_spawn returned = exec done in kernel), child stamps tm (first line of main) and te (last line of main) on a pipe (same CLOCK_UPTIME_RAW clock), parent stamps t2 (wait4 returned); also times fork()+_exit(0) with no exec; inputs: rounds N, optional extra child argv (an extra program to spawn instead of self, which then must write nothing: only t0,t1,t2 reported); output: JSONL {mode, round, spawn_ret_us, to_main_us, main_us, exit_reap_us, total_us, load1}.
// build: clang -O2 -o w07a_spawn_stamp w07a_spawn_stamp.c    usage: w07a_spawn_stamp N [WARMUP] [ONLY: 0 spawn, 1 fork]
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <time.h>
extern char **environ;
static unsigned long long now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
int main(int argc, char **argv){
  if(argc>1 && !strcmp(argv[1],"--child")){ unsigned long long a=now(); unsigned long long b=now(); write(3,&a,8); write(3,&b,8); return 0; }
  int N=argc>1?atoi(argv[1]):100, W=argc>2?atoi(argv[2]):3; int only=argc>3?atoi(argv[3]):-1; /* 0 = spawn only, 1 = fork only */
  char self[4096]; strncpy(self,argv[0],sizeof self-1);
  for(int r=-W;r<N;r++){
    double la[3]; getloadavg(la,3);
    for(int mode=0;mode<2;mode++){ if(only>=0 && mode!=only) continue;
      int p[2]; pipe(p); fcntl(p[0],F_SETFD,FD_CLOEXEC); fcntl(p[1],F_SETFD,FD_CLOEXEC);
      pid_t pid; int st; unsigned long long t0,t1,t2,tm=0,te=0;
      if(mode==0){
        posix_spawn_file_actions_t fa; posix_spawn_file_actions_init(&fa);
        posix_spawn_file_actions_adddup2(&fa,p[1],3);
        char *av[]={self,"--child",NULL};
        t0=now(); posix_spawn(&pid,self,&fa,NULL,av,environ); t1=now();
        wait4(pid,&st,0,NULL); t2=now();
        unsigned long long buf[2]={0,0}; read(p[0],buf,16); tm=buf[0]; te=buf[1];
        posix_spawn_file_actions_destroy(&fa);
      } else {
        t0=now(); pid=fork(); if(pid==0) _exit(0); t1=now();
        wait4(pid,&st,0,NULL); t2=now();
      }
      close(p[0]); close(p[1]);
      if(r>=0){
        if(mode==0) printf("{\"mode\":\"spawn\",\"round\":%d,\"spawn_ret_us\":%.1f,\"to_main_us\":%.1f,\"main_us\":%.1f,\"exit_reap_us\":%.1f,\"total_us\":%.1f,\"load1\":%.2f}\n",r,(t1-t0)/1e3,(double)((long long)tm-(long long)t1)/1e3,(te-tm)/1e3,(double)((long long)t2-(long long)te)/1e3,(t2-t0)/1e3,la[0]);
        else printf("{\"mode\":\"fork_exit\",\"round\":%d,\"spawn_ret_us\":%.1f,\"total_us\":%.1f,\"load1\":%.2f}\n",r,(t1-t0)/1e3,(t2-t0)/1e3,la[0]);
      }
    }
  }
  return 0;
}
