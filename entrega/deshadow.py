import numpy as np
from PIL import Image, ImageFilter, ImageDraw
src="/root/.claude/uploads/1696af4d-3010-5ab5-8c32-476781fbb3bc/15f9d42a-image.jpg"
O="/tmp/claude-0/-home-user-928841/1696af4d-3010-5ab5-8c32-476781fbb3bc/scratchpad/img/"
im=Image.open(src).convert("RGB"); a=np.asarray(im).astype(np.float32)/255
L=a.max(2)
Li=Image.fromarray((L*255).astype(np.uint8))
# illumination envelope: local max then smooth
env=Li.filter(ImageFilter.GaussianBlur(2))
for _ in range(3): env=env.filter(ImageFilter.MaxFilter(15))
env=env.filter(ImageFilter.GaussianBlur(30))
E=np.asarray(env).astype(np.float32)/255
# region mask: hood (where shadow sits)
m=Image.new("L",im.size,0); d=ImageDraw.Draw(m)
d.polygon([(70,690),(230,640),(720,640),(860,700),(880,830),(740,870),(160,870),(40,820)],fill=255)
m=m.filter(ImageFilter.GaussianBlur(12)); M=np.asarray(m).astype(np.float32)/255
gain=np.clip(E/np.maximum(L,1e-3),1,3.0)
# only correct real shadow (clearly darker than envelope)
sh=np.clip((gain-1.04)/0.15,0,1)
G=1+(gain-1)*sh
Gi=Image.fromarray((np.clip((G-1)/2,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
G=1+np.asarray(Gi).astype(np.float32)/255*2
G=1+(G-1)*M
out=np.clip(a*G[...,None],0,1)
Image.fromarray((out*255+0.5).astype(np.uint8)).save(O+"foto_sem_sombra.png")
Image.fromarray(np.hstack([(a*255).astype(np.uint8),(out*255).astype(np.uint8)])).resize((900,800)).save(O+"cmp.png")
