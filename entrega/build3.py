import subprocess, glob
U="/root/.claude/uploads/1696af4d-3010-5ab5-8c32-476781fbb3bc/"
S="/tmp/claude-0/-home-user-928841/1696af4d-3010-5ab5-8c32-476781fbb3bc/scratchpad/b2/"
src=lambda k: glob.glob(U+k+"*.mov")[0]
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
FPS=30
# (src,start,end,gain_dB,subs)
talk=[
 ("8e9b",0.30,13.00,0,[(0,1.05,"Rapaziada,"),(1.05,1.95,"se você quer virar"),(1.95,3.05,"um bigode de verdade,"),(3.05,4.2,"você tem que lançar essa nave,"),(4.2,5.0,"acompanha!"),(5.85,7.3,"Faróis com DRL,"),(8.1,9.8,"rodas diamantadas aro 18,"),(9.8,11.3,"e o melhor tá aqui dentro.")]),
 ("8e9b",15.60,20.45,0,[(1.3,2.9,"Volante multifuncional,"),(3.6,4.85,"câmbio knob,")]),
 ("04c6",0.15,1.85,0,[(0,1.7,"E olha a qualidade desse som.")]),
 ("04c6",2.95,11.80,5,[]),
 ("04c6",11.80,16.40,0,[(0.05,1.65,"E o melhor de tudo"),(1.65,2.75,"é que dá pra colocar a gata"),(2.75,3.9,"no teto solar.")]),
 ("04c6",19.90,21.45,0,[(0.35,1.4,"Acompanha!")]),
 ("470c",0.00,2.87,0,[(0.5,1.55,"Esqueça!")]),
 ("a81a",0.00,7.20,0,[(0.15,1.45,"E o melhor de tudo"),(1.45,2.75,"é que esse carro tem"),(2.75,4.25,"assistente de estacionamento"),(4.25,5.65,"e piloto automático,"),(5.75,7.1,"e acompanha essa externa!")]),
]
broll=[("42e5",0.3,2.0),("b6be",0.0,1.2),("03b8",0.5,3.0),("e658",0.3,2.0),("a6e4",0.0,1.1),("d2c1",1.0,3.0),("d2c1",4.5,6.5),("2ff9",0.0,3.0),("2ff9",3.5,8.1)]
def cut(k,a,b,g,out):
    n=round((b-a)*FPS); d=n/FPS
    af=f"aresample=48000,aformat=channel_layouts=stereo,"+(f"volume={g}dB,alimiter=limit=0.95:level=false," if g else "")+f"afade=t=in:d=0.02,afade=t=out:st={d-0.025:.3f}:d=0.025,apad,atrim=0:{d:.4f}"
    run(["ffmpeg","-y","-ss",f"{a}","-i",src(k),"-frames:v",str(n),"-vf","fps=30,setsar=1","-c:v","libx264","-qp","0","-preset","fast","-af",af,"-c:a","pcm_s16le",out])
    return d
import glob as G
parts=[];subs=[];T=0
for i,(k,a,b,g,sb) in enumerate(talk):
    out=f"{S}t{i:02d}.mkv"; d=round((b-a)*FPS)/FPS; parts.append(out)
    subs+=[(T+s,T+min(e,d),tx) for s,e,tx in sb]; T+=d
M="/tmp/claude-0/-home-user-928841/1696af4d-3010-5ab5-8c32-476781fbb3bc/scratchpad/b3/"
mp=sorted(G.glob(M+"p*.mkv"))
for p in mp:
    d=float(subprocess.run(["ffprobe","-v","error","-select_streams","v","-count_frames","-show_entries","stream=nb_read_frames","-of","csv=p=0",p],capture_output=True,text=True).stdout)/30
    parts.append(p); last=d; T+=d
total=T; c=total-last
open(S+"l.txt","w").write("".join(f"file '{p}'\n" for p in parts))
run(["ffmpeg","-y","-f","concat","-safe","0","-i",S+"l.txt","-c","copy",S+"full.mkv"])
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Bold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3.5,1.5,2,80,80,560,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for s,e,tx in subs: ass+=f"Dialogue: 0,{ts(s)},{ts(e-0.02)},Sub,,0,0,0,,{{\\fad(60,40)}}{tx}\n"
open(S+"subs.ass","w").write(ass)
F="/usr/share/fonts/opentype/inter/"; k=576/1080
def al(t0): return f"alpha='if(lt(t,{t0}),0,min(1,(t-{t0})/0.45))'"
def yy(b,t0): return f"y='{b*k:.1f}+{40*k:.1f}*(1-min(1,max(0,(t-{t0})/0.45)))^2'"
def fs(x): return round(x*k)
dt=[f"drawtext=fontfile={F}Inter-SemiBold.otf:text='FUSION TITANIUM':fontsize={fs(58)}:fontcolor=white:x=(w-tw)/2:{yy(760,c+0.25)}:{al(c+0.25)}",
 f"drawbox=x=(iw-{fs(160)})/2:y={fs(860)}:w={fs(160)}:h=2:color=white@1:t=fill:enable='gte(t,{c+0.5})'",
 f"drawtext=fontfile={F}Inter-Medium.otf:text='R$':fontsize={fs(50)}:fontcolor=white@0.85:x=(w-tw)/2:{yy(905,c+0.65)}:{al(c+0.65)}",
 f"drawtext=fontfile={F}Inter-Black.otf:text='85.900,00':fontsize={fs(150)}:fontcolor=white:x=(w-tw)/2:{yy(965,c+0.75)}:{al(c+0.75)}",
 f"drawtext=fontfile={F}Inter-Medium.otf:text='CHAME AGORA':fontsize={fs(36)}:fontcolor=white@0.8:x=(w-tw)/2:{yy(1190,c+1.15)}:{al(c+1.15)}",
 f"drawtext=fontfile={F}Inter-Bold.otf:text='(19) 98164-5396':fontsize={fs(74)}:fontcolor=white:x=(w-tw)/2:{yy(1245,c+1.25)}:{al(c+1.25)}"]
fc=(f"[0:v]subtitles={S}subs.ass:fontsdir={F}[s];color=black@0.6:s=576x1024:r=30,format=rgba,fade=t=in:st={c}:d=0.5:alpha=1[dk];"
    f"[s][dk]overlay=shortest=1:enable='gte(t,{c})',"+",".join(dt)+f",fade=t=out:st={total-0.4:.3f}:d=0.4[v];[0:a]afade=t=out:st={total-0.6:.3f}:d=0.6[a]")
run(["ffmpeg","-y","-i",S+"full.mkv","-filter_complex",fc,"-map","[v]","-map","[a]","-c:v","libx264","-crf","14","-preset","slow","-pix_fmt","yuv420p",
     "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv","-movflags","+faststart","-c:a","aac","-b:a","256k",S+"final3.mp4"])
print("total",total,"cta",c)
