import subprocess, os, glob
U="/root/.claude/uploads/1696af4d-3010-5ab5-8c32-476781fbb3bc/"
S="/tmp/claude-0/-home-user-928841/1696af4d-3010-5ab5-8c32-476781fbb3bc/scratchpad/build/"
src=lambda k: glob.glob(U+k+"*.mov")[0]
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
FPS=30; BEAT=0.7546485
# (src, start, end, gain_dB, subs[(rel_s, rel_e, text)])
talk=[
 ("8e9b",0.30,5.35,0,[(0,1.05,"Rapaziada,"),(1.05,1.95,"se você quer virar"),(1.95,3.05,"um bigode de verdade,"),(3.05,4.2,"você tem que lançar essa nave,"),(4.2,5.05,"acompanha!")]),
 ("8e9b",6.05,7.70,0,[(0,1.65,"Faróis com DRL,")]),
 ("8e9b",8.30,11.70,0,[(0,1.7,"rodas diamantadas aro 18,"),(1.7,3.4,"e o melhor tá aqui dentro.")]),
 ("8e9b",16.80,18.60,0,[(0,1.8,"Volante multifuncional,")]),
 ("8e9b",19.15,20.45,0,[(0,1.3,"câmbio knob,")]),
 ("04c6",0.15,1.85,0,[(0,1.7,"E olha a qualidade desse som.")]),
 ("04c6",3.40,9.20,5,[]),
 ("04c6",11.85,15.70,0,[(0,1.6,"E o melhor de tudo"),(1.6,2.7,"é que dá pra colocar a gata"),(2.7,3.85,"no teto solar.")]),
 ("04c6",20.25,21.30,0,[(0,1.05,"Acompanha!")]),
 ("470c",0.35,2.50,0,[(0.15,1.2,"Esqueça!")]),
 ("a81a",0.15,7.10,0,[(0,1.3,"E o melhor de tudo"),(1.3,2.6,"é que esse carro tem"),(2.6,4.1,"assistente de estacionamento"),(4.1,5.5,"e piloto automático,"),(5.6,6.95,"e acompanha essa externa!")]),
]
# montage: (src,start,beats)
mont=[("42e5",0.6,1),("b6be",0.25,1),("03b8",1.2,2),("e658",0.9,1),("a6e4",0.3,1),("d2c1",1.3,1),("d2c1",5.4,1),("2ff9",0.2,1),("2ff9",3.4,6)]
VF="vidstabtransform=input={t}:smoothing=12:optzoom=1:interpol=bicubic,scale=1080:1920:flags=lanczos,fps=30,setsar=1,format=yuv420p"
def stab(k,a,d,out,audio_gain=None):
    trf=out+".trf"
    run(["ffmpeg","-y","-ss",f"{a}","-t",f"{d}","-i",src(k),"-vf",f"vidstabdetect=shakiness=6:accuracy=15:result={trf}","-f","null","-"])
    cmd=["ffmpeg","-y","-ss",f"{a}","-t",f"{d}","-i",src(k),"-vf",VF.format(t=trf),"-frames:v",str(round(d*FPS)),"-c:v","libx264","-crf","11","-preset","medium"]
    if audio_gain is None: cmd+=["-an"]
    else:
        af=f"aresample=48000,aformat=channel_layouts=stereo,volume={audio_gain}dB,"+("alimiter=limit=0.95:level=false," if audio_gain else "")+f"afade=t=in:d=0.025,afade=t=out:st={d-0.03:.3f}:d=0.03,apad,atrim=0:{round(d*FPS)/FPS:.4f}"
        cmd+=["-af",af,"-c:a","pcm_s16le"]
    run(cmd+[out])
parts=[];subs=[];T=0.0
for i,(k,a,b,g,sb) in enumerate(talk):
    d=round((b-a)*FPS)/FPS; out=f"{S}t{i:02d}.mkv"; stab(k,a,d,out,g); parts.append(out)
    for s,e,tx in sb: subs.append((T+s,T+min(e,d),tx))
    T+=d
talkdur=T
# montage on beat grid
mparts=[];cum=0
for i,(k,a,n) in enumerate(mont):
    f0=round(cum*BEAT*FPS); cum+=n; f1=round(cum*BEAT*FPS); d=(f1-f0)/FPS
    out=f"{S}m{i:02d}.mkv"; stab(k,a,d,out,None); mparts.append(out)
mdur=round(cum*BEAT*FPS)/FPS
cta_start=talkdur+round(9*BEAT*FPS)/FPS
with open(S+"lt.txt","w") as f: f.write("".join(f"file '{p}'\n" for p in parts))
with open(S+"lm.txt","w") as f: f.write("".join(f"file '{p}'\n" for p in mparts))
run(["ffmpeg","-y","-f","concat","-safe","0","-i",S+"lt.txt","-c","copy",S+"talk.mkv"])
run(["ffmpeg","-y","-f","concat","-safe","0","-i",S+"lm.txt","-c","copy",S+"montv.mkv"])
# montage music: 04c6 [3.17, 3.17+11 beats] + loop last 4 beats, fade out
m0=3.17; e1=m0+11*BEAT; l0=e1-4*BEAT
run(["ffmpeg","-y","-i",src("04c6"),"-filter_complex",
 f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim={m0}:{e1},asetpts=N/SR/TB,afade=t=out:st={e1-m0-0.02:.3f}:d=0.02[a];"
 f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim={l0}:{e1},asetpts=N/SR/TB,afade=t=in:d=0.02,afade=t=out:st={4*BEAT-1.6:.3f}:d=1.6[b];"
 f"[a][b]concat=n=2:v=0:a=1,volume=4dB,alimiter=limit=0.95:level=false,afade=t=in:d=0.15,apad,atrim=0:{mdur:.4f}[o]","-map","[o]","-c:a","pcm_s16le",S+"monta.wav"])
run(["ffmpeg","-y","-i",S+"montv.mkv","-i",S+"monta.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","pcm_s16le",S+"mont.mkv"])
with open(S+"lf.txt","w") as f: f.write(f"file '{S}talk.mkv'\nfile '{S}mont.mkv'\n")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",S+"lf.txt","-c","copy",S+"full.mkv"])
# ASS subtitles
def ts(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h}:{m:02d}:{s:05.2f}"
ass="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Bold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3.5,1.5,2,80,80,560,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for s,e,tx in subs: ass+=f"Dialogue: 0,{ts(s)},{ts(e-0.02)},Sub,,0,0,0,,{{\\fad(60,40)}}{tx}\n"
open(S+"subs.ass","w").write(ass)
# CTA
F="/usr/share/fonts/opentype/inter/"
c=cta_start
def al(t0,dur=0.45): return f"alpha='if(lt(t,{t0}),0,min(1,(t-{t0})/{dur}))'"
def yy(base,t0): return f"y='{base}+40*(1-min(1,max(0,(t-{t0})/0.45)))^2'"
dt=[
 f"drawtext=fontfile={F}Inter-SemiBold.otf:text='FUSION TITANIUM':fontsize=58:fontcolor=white:x=(w-tw)/2:{yy(760,c+0.25)}:{al(c+0.25)}",
 f"drawbox=x=(iw-160)/2:y=860:w=160:h=4:color=white@1:t=fill:enable='gte(t,{c+0.5})'",
 f"drawtext=fontfile={F}Inter-Medium.otf:text='R$':fontsize=50:fontcolor=white@0.85:x=(w-tw)/2:{yy(905,c+0.65)}:{al(c+0.65)}",
 f"drawtext=fontfile={F}Inter-Black.otf:text='85.900,00':fontsize=150:fontcolor=white:x=(w-tw)/2:{yy(965,c+0.75)}:{al(c+0.75)}",
 f"drawtext=fontfile={F}Inter-Medium.otf:text='CHAME AGORA':fontsize=36:fontcolor=white@0.8:x=(w-tw)/2:{yy(1190,c+1.15)}:{al(c+1.15)}",
 f"drawtext=fontfile={F}Inter-Bold.otf:text='(19) 98164-5396':fontsize=74:fontcolor=white:x=(w-tw)/2:{yy(1245,c+1.25)}:{al(c+1.25)}",
]
fc=(f"[0:v]subtitles={S}subs.ass:fontsdir={F}[s];color=black@0.6:s=1080x1920:r=30,format=rgba,fade=t=in:st={c}:d=0.5:alpha=1[dk];"
    f"[s][dk]overlay=shortest=1:enable='gte(t,{c})',"+",".join(dt)+f",fade=t=out:st={talkdur+mdur-0.5:.3f}:d=0.5[v]")
run(["ffmpeg","-y","-i",S+"full.mkv","-filter_complex",fc,"-map","[v]","-map","0:a","-c:v","libx264","-crf","16","-preset","slow","-profile:v","high","-pix_fmt","yuv420p","-movflags","+faststart","-c:a","aac","-b:a","256k",S+"final.mp4"])
print("talk",talkdur,"mont",mdur,"cta",cta_start)
