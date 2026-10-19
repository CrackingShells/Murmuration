import mmap,sys,re
F='/Users/hacker/.local/share/claude/versions/2.1.302'
pat=sys.argv[1].encode(); before=int(sys.argv[2]); after=int(sys.argv[3]); maxn=int(sys.argv[4])
with open(F,'rb') as f:
    m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
    pos=0;n=0
    while n<maxn:
        i=m.find(pat,pos)
        if i<0: break
        print('@%d:'%i, m[max(0,i-before):i+after].decode('utf8','replace')); print('-----')
        pos=i+1;n+=1
