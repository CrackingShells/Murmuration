// Hook-side clock stamp, in C: appends one line "<tag> pid ppid main_start_realtime_ns main_end_realtime_ns" to the file given as argv[1] (tag = argv[2]), reading nothing from stdin; inputs: output path, tag; output: the appended line. Used to place a hook process's main() on the debug log's millisecond clock (CLOCK_REALTIME ns since epoch).
// build: clang -O2 -o stamp_hook w07a_stamp_hook.c
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
int main(int argc, char **argv){
  unsigned long long a = clock_gettime_nsec_np(CLOCK_REALTIME);
  if(argc<3) return 2;
  unsigned long long b = clock_gettime_nsec_np(CLOCK_REALTIME);
  char buf[256]; int n=snprintf(buf,sizeof buf,"%s %d %d %llu %llu\n",argv[2],(int)getpid(),(int)getppid(),a,b);
  int fd=open(argv[1],O_WRONLY|O_APPEND|O_CREAT,0644); write(fd,buf,n); close(fd);
  return 0;
}
