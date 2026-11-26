import subprocess, glob
U="/root/.claude/uploads/1696af4d-3010-5ab5-8c32-476781fbb3bc/"
S="/tmp/claude-0/-home-user-928841/1696af4d-3010-5ab5-8c32-476781fbb3bc/scratchpad/b3/"
import os; os.makedirs(S,exist_ok=True)
src=lambda k: glob.glob(U+k+"*.mov")[0]
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
# piece: (src, start, end, speed)  speed<1 = slow motion with motion interpolation
pieces=[("03b8",0.0,1.2,1.6),("03b8",1.2,2.6,0.6),
        ("e658",0.3,1.9,1.0),
        ("b6be",0.0,1.2,0.7),
        ("42e5",1.2,2.4,0.7),
        ("a6e4",0.0,1.1,0.7),
        ("d2c1",1.0,2.4,0.7),
        ("2ff9",0.0,1.5,1.6),("2ff9",1.5,3.2,0.6),
        ("2ff9",3.5,8.1,1.0)]
out=[]
for i,(k,a,b,sp) in enumerate(pieces):
    n=round((b-a)/sp*30); d=n/30
    vf="fps=30,"
    if sp<1: vf+=f"minterpolate=fps={round(30/sp)}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=PTS/{sp},fps=30,"
    elif sp>1: vf+=f"setpts=PTS/{sp},fps=30,"
    vf+="setsar=1"
    at=f"atempo={sp}," if sp!=1 else ""
    af=f"aresample=48000,aformat=channel_layouts=stereo,{at}afade=t=in:d=0.02,afade=t=out:st={d-0.025:.3f}:d=0.025,apad,atrim=0:{d:.4f}"
    o=f"{S}p{i:02d}.mkv"
    run(["ffmpeg","-y","-ss",f"{a}","-t",f"{b-a+0.1}","-i",src(k),"-vf",vf,"-frames:v",str(n),"-c:v","libx264","-qp","0","-preset","fast","-af",af,"-c:a","pcm_s16le",o])
    out.append(o); print(i,d)
open(S+"list.txt","w").write("".join(f"file '{p}'\n" for p in out))
