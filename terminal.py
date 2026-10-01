# SPDX-License-Identifier: MIT
"""Terminal typography, native/fallback fonts, shared lyric token display."""
import math, os
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1920,1080,30
BG=(6,9,15);PANEL=(9,14,23);AMBER=(239,186,107);BLUE=(133,166,255)
WHITE=(222,232,247);DIM=(65,85,108);GREEN=(127,213,161)
PINK=(240,131,181);RED=(255,109,127);TAU=2*math.pi
ROOT=Path(__file__).resolve().parent
MONO=os.environ.get('PV_FONT','/System/Library/Fonts/Menlo.ttc')
if not Path(MONO).exists():MONO=str(ROOT/'assets'/'fonts'/'SpaceMono-Bold.ttf')
@lru_cache(None)
def font(size,bold=False):
    return ImageFont.truetype(MONO,size,index=int(bold) if MONO.endswith('Menlo.ttc') else 0)
def shade(c,x):
    return tuple(max(0,min(255,int(BG[k]+(c[k]-BG[k])*x))) for k in range(3))
def smooth(x):
    x=max(0,min(1,float(x)));return x*x*(3-2*x)
def center(d,x,y,s,size=24,c=WHITE,bold=False):
    f=font(size,bold);d.text((x-d.textlength(s,font=f)/2,y),s,font=f,fill=c)
def panel(d,box,label,c=AMBER):
    x0,y0,x1,y1=box;d.rectangle(box,fill=PANEL,outline=shade(c,.28))
    for x,y,sx,sy in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
        d.line((x,y,x+sx*17,y),fill=shade(c,.9),width=2);d.line((x,y,x,y+sy*17),fill=shade(c,.9),width=2)
    tw=d.textlength(' '+label+' ',font=font(18));d.rectangle((x0+22,y0-9,x0+22+tw,y0+14),fill=BG)
    d.text((x0+23,y0-8),' '+label+' ',font=font(18),fill=shade(c,.78))
def project(points,angle,tilt=.35):
    p=np.asarray(points);c,s=math.cos(angle),math.sin(angle)
    x=p[...,0]*c-p[...,2]*s;z=p[...,0]*s+p[...,2]*c
    y=p[...,1]*math.cos(tilt)-z*math.sin(tilt);z=p[...,1]*math.sin(tilt)+z*math.cos(tilt)
    perspective=4/(4+z);return x*perspective,y*perspective,z
class TerminalFilm:
    def __init__(self,track,words,offset=0):
        self.track=track;self.words=words['lines'];self.offset=offset
        self.scan=Image.new('RGB',(W,H),(255,255,255));sd=ImageDraw.Draw(self.scan)
        for y in range(0,H,4):sd.line((0,y,W,y),fill=(237,237,237))
    def phase_at(self,t):
        return next((v for v in reversed(self.phases) if t>=v[0]),self.phases[0])
    def lyric_line(self,t):
        clock=t-self.offset
        return next((ln for ln in self.words if ln['start']<=clock<ln['hold_until']),None)
    def lyrics(self,d,t,phase):
        c=RED if phase.startswith('execution') else PINK if phase in ('love','heart','cage','freedom') else AMBER
        panel(d,(60,880,1860,1016),' stdout / lyric tokens ',c)
        d.text((86,916),'>',font=font(38,True),fill=c)
        ln=self.lyric_line(t)
        if ln is None:
            if int(t*2)%2==0:d.rectangle((126,922,143,951),fill=shade(c,.86))
            d.text((1610,970),'[ listening ]',font=font(16),fill=shade(DIM,.75));return
        clock=t-self.offset;fade=1-smooth((clock-ln['end']-.25)/.4)
        keywords={'power','protection','pieces','object','creation','data','parameters','initialization','world','simulation','dimension','circumference','tangents','limitations','ac','dc','stimulations','satisfaction','execution','nutrients','antioxidants','enjoyment','existence','vibrations','completion','isolation','fragments','disheartened','illegal','arguments','lo-o-ove','love'}
        size=36
        while size>24 and sum(d.textlength(w['text'],font=font(size,True))+32 for w in ln['words'])>1690:size-=1
        x=131
        for j,w in enumerate(ln['words']):
            if clock<w['start']:break
            word=w['text'];key=word.lower().strip(',.?!');is_key=key in keywords
            if is_key:word=word.upper()
            width=d.textlength(word,font=font(size,True))+22
            age=clock-w['start'];full=min(.16,max(.05,(w['end']-w['start'])*.55))
            count=min(len(word),max(1,int(len(word)*age/full)+1));shown=word[:count];alive=clock<w['end']
            base=BLUE if key in ('object','creation','world','dimension','circumference','completion') else c
            if is_key and count==len(word):
                d.rectangle((x,912,x+width,960),fill=shade(base,.80*fade));d.text((x+10,915),shown,font=font(size,True),fill=BG)
            else:
                d.rectangle((x,912,x+width,960),outline=shade(base,(.5 if alive else .22)*fade));d.text((x+10,915),shown,font=font(size,True),fill=shade(WHITE if alive else base,.92*fade))
            d.text((x+2,974),f'{j:02}',font=font(12),fill=shade(base,.45*fade))
            if alive:d.line((x,905,x+width,905),fill=shade(base,.85*fade),width=2)
            x+=width+10
        if int(t*4)%2==0 and x<1780:d.rectangle((x+3,922,x+15,951),fill=shade(c,.82*fade))
