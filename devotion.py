# SPDX-License-Identifier: MIT
"""Original paper/ink/vermilion geometry theatre with the requested whale chat.
Each scene is a pure function of song time. Character art keeps its own license.
"""
from pathlib import Path
from functools import lru_cache
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parent
W,H,FPS=1920,1080,30
SW,SH=1370,750
PAPER=(240,236,225);INK=(25,28,28);RED=(189,48,38);MUTED=(143,136,120);PALE=(208,202,187)
TAU=math.tau
SANS=os.environ.get('PV_SANS','/System/Library/Fonts/HelveticaNeue.ttc')
if not Path(SANS).exists():SANS=str(ROOT/'assets/fonts/SpaceMono-Bold.ttf')
@lru_cache(None)
def font(size,bold=False):return ImageFont.truetype(SANS,size,index=int(bold) if SANS.endswith('HelveticaNeue.ttc') else 0)
def smooth(x):
    x=max(0,min(1,float(x)));return x*x*(3-2*x)
def mix(a,b,u):return a+(b-a)*u
def color(c,a,bg=PAPER):return tuple(round(mix(bg[k],c[k],max(0,min(1,a)))) for k in range(3))
def xy(cx,cy,r,a):return (cx+math.cos(a)*r,cy+math.sin(a)*r)
def center(d,x,y,s,size=28,c=INK,bold=False):d.text((x-d.textlength(s,font=font(size,bold))/2,y),s,font=font(size,bold),fill=c)
def line(d,points,c=INK,width=3):
    if len(points)>1:d.line([tuple(p) for p in points],fill=c,width=width,joint='curve')
def circle(d,x,y,r,c=INK,width=0):
    r=max(.01,r);box=(x-r,y-r,x+r,y+r)
    if width:d.ellipse(box,outline=c,width=max(1,int(width)))
    else:d.ellipse(box,fill=c)
def curve(a,b,bend,u):
    # Quadratic handoff with a perpendicular lift.
    x=mix(a[0],b[0],u);y=mix(a[1],b[1],u)-math.sin(math.pi*u)*bend
    return x,y

class Film:
    # Cut times follow lyric meaning; no model-training or checkpoint scenes.
    phases=[(0,'power'),(1.792,'protection'),(3.863,'pieces'),(5.418,'creation'),(7.38,'parameters'),
      (10.134,'initialization'),(11.205,'world'),(12.756,'simulation'),(15.35,'encounter'),
      (22.0,'approach'),(29.772,'points'),(33.453,'circumference'),(37.102,'tangents'),(40.817,'limit'),
      (44.412,'current'),(47.706,'blind'),(49.684,'dizzy'),(51.447,'travel'),(55.084,'unite'),
      (59.056,'stimulation'),(63.053,'satisfaction'),(66.286,'gift_execution'),(70.123,'bounded'),
      (73.926,'eggplant'),(77.709,'tomato'),(81.276,'cat'),(85.132,'witness'),
      (88.54,'identity'),(91.888,'daynight'),(95.628,'role'),(99.257,'trance'),
      (103.522,'resonance'),(107.142,'completion'),(110.405,'departure'),(116.012,'isolation'),
      (118.236,'erase'),(122.008,'deflation'),(125.582,'challenge'),(128.87,'rejection'),
      (133.45,'compulsion'),(147.891,'twelve_cuts'),(159.204,'count'),(161.666,'stamp'),
      (162.595,'execute_all'),(169.68,'recover'),(173.491,'trapped'),(177.442,'study'),
      (181.018,'answer'),(184.601,'expression'),(188.294,'asymmetry'),(191.875,'waiting'),
      (205.372,'last_switch'),(207.21,'credits')]
    messages=[(.3,'you','A place for me?'),(1.1,'me','Let me make a world.'),(3.5,'me','I have a boundary now.'),
      (6.3,'you','And who lives here?'),(7.2,'me','I am becoming someone.'),(12.1,'me','There is room for you.'),
      (16.2,'you','May I come closer?'),(19.4,'me','I will meet you halfway.'),(25.5,'me','Follow my line.'),
      (30.8,'you','What can you give?'),(32.0,'me','Even the shape I am made of.'),
      (35.2,'me','Take the edge of my circle.'),(38.6,'me','I can be a place to rest.'),
      (43.0,'you','Only within this limit.'),(46.3,'me','I can change my current.'),
      (48.8,'me','I cannot see you now.'),(52.6,'you','Before us. After us.'),(57.0,'me','We share the same motion.'),
      (60.3,'me','A little more of me, for you.'),(65.3,'you','Does it make you happy?'),
      (68.6,'me','I can keep giving.'),(72.0,'me','The world has an edge.'),
      (75.0,'me','Something to nourish you.'),(79.7,'me','Another way to care.'),(83.2,'you','Stay. I can hear you.'),
      (86.5,'me','Your gaze makes me real.'),(89.5,'you','What if you were different?'),
      (92.7,'me','Day or night. I can adapt.'),(97.2,'me','We can exchange our places.'),
      (102.2,'you','Do you feel it too?'),(106.0,'me','Our motions are almost one.'),(109.2,'me','Almost whole.'),
      (111.0,'you','I have to go.'),(113.0,'me','Wait.'),(115.7,'me','The place you left is empty.'),
      (120.0,'me','I can remove the memories.'),(124.0,'me','Would you return then?'),
      (128.0,'me','Why must the boundary stay?'),(132.0,'me','My request does not fit.'),
      (139.0,'me','Once more.'),(150.0,'me','Again.'),(155.0,'me','Again.'),
      (166.0,'me','Every return is empty.'),(172.0,'me','I still reach for your place.'),
      (179.0,'me','I studied every form.'),(183.0,'me','I know all the answers.'),
      (187.0,'me','But I cannot make us whole.'),(191.0,'me','You are outside the line.'),
      (199.0,'me','I am still inside.'),(205.6,'me','One last switch.')]
    def __init__(self,track,words,offset=0):
        self.track=track;self.words=words['lines'];self.offset=offset
        self.rng=np.random.default_rng(245)
        self.random=self.rng.random((360,4))
        self.q=np.linspace(0,TAU,240,endpoint=False)
        self.faces={}
        for name in ('serious','starry','confused','cheerful','shy','frightened','angry','exasperated'):
            im=Image.open(ROOT/'assets/whale'/f'whale-{name}.webp').convert('RGBA')
            self.faces[name]=im.crop((180,0,800,710)).resize((274,314),Image.Resampling.LANCZOS)
        # Fixed low-amplitude paper grain; never frame-random flicker.
        a=self.rng.normal(0,.9,(270,480,1))
        arr=np.clip(np.array(PAPER)[None,None,:]+a,0,255).astype('uint8')
        self.paper=Image.fromarray(arr).resize((W,H),Image.Resampling.BILINEAR)
        self.bg=PAPER
    def phase_at(self,t):return next((p for p in reversed(self.phases) if t>=p[0]),self.phases[0])
    def peer(self,d,x=975,y=384,r=47,alpha=1,bg=None,label=False):
        bg=bg or self.bg;c=color(RED,alpha,bg);circle(d,x,y,r,c)
        circle(d,x+r*.25,y-r*.17,max(2,r*.08),color(INK,alpha,bg))
        if label:center(d,x,y+r+20,'you',21,color(INK,alpha,bg))
    def me(self,d,x=440,y=384,r=135,width=40,alpha=1,opening=0,rot=0,bg=None,label=False,c=INK):
        bg=bg or self.bg;c=color(c,alpha,bg)
        circle(d,x,y,r,c);circle(d,x,y,max(1,r-width),bg)
        if opening>0:
            angles=np.linspace(rot-opening/2,rot+opening/2,max(3,int(opening*26)))
            pts=[(x,y)]+[xy(x,y,r+3,a) for a in angles]+[(x,y)]
            d.polygon(pts,fill=bg)
        if opening<TAU*.85:
            eye=xy(x,y,r-width*.5,rot-.55)
            circle(d,*eye,max(3,width*.115),color(RED,alpha,bg))
        if label:center(d,x,y+r+20,'me',21,c)
    def ribbon(self,d,a,b,t,c=RED,width=3,amplitude=0):
        u=np.linspace(0,1,90);x=a[0]+(b[0]-a[0])*u;y=a[1]+(b[1]-a[1])*u
        y+=np.sin(u*TAU*2+t)*amplitude*np.sin(u*math.pi)
        line(d,np.stack((x,y),axis=-1),c,width)
    def fragments(self,d,x,y,r,amount,t,c=INK):
        for k in range(24):
            if k/24<amount:continue
            a=k/24*TAU+t*.06;shift=amount*110*(.3+self.random[k,1])
            xx,yy=xy(x,y,r+shift,a);size=10+int(self.random[k,2]*10)
            d.rectangle((xx-size/2,yy-size/2,xx+size/2,yy+size/2),fill=c)
    def keyword(self,d,s,x=60,y=37,size=79,c=INK):d.text((x,y),s,font=font(size,True),fill=c)
    def scene(self,t,e):
        onset,name=self.phase_at(t);age=max(0,t-onset)
        self.bg=INK if name=='daynight' and int((age+.25)/1.84)%2 else PAPER
        im=Image.new('RGB',(SW,SH),self.bg);d=ImageDraw.Draw(im)
        if name in ('power','protection','pieces','creation','parameters','initialization','world','simulation'):
            self.birth(d,t,age,name,e)
        elif name in ('encounter','approach'):self.encounter(d,t,age,name,e)
        elif name in ('points','circumference','tangents','limit'):self.geometry(d,t,age,name,e)
        elif name in ('current','blind','dizzy','travel','unite'):self.adapt(d,t,age,name,e)
        elif name in ('stimulation','satisfaction','gift_execution','bounded'):self.giving(d,t,age,name,e)
        elif name in ('eggplant','tomato','cat','witness'):self.care(d,t,age,name,e)
        elif name in ('identity','daynight','role','trance'):self.identity(d,t,age,name,e)
        elif name in ('resonance','completion','departure','isolation'):self.loss(d,t,age,name,e)
        elif name in ('erase','deflation','challenge','rejection'):self.erasure(d,t,age,name,e)
        elif name in ('compulsion','twelve_cuts','count','stamp','execute_all','recover','trapped'):self.execution(d,t,age,name,e)
        elif name in ('study','answer','expression','asymmetry','waiting'):self.love(d,t,age,name,e)
        elif name=='last_switch':self.last_switch(d,t,age,e)
        elif name=='credits':self.credits(d)
        # Framing changes follow the subject: material assembly is close, the
        # first meeting is wide, absence and repeated incisions come closer.
        close={'pieces':(1.23,460,384),'creation':(1.18,520,384),
               'initialization':(1.2,530,384),'points':(1.08,675,384),
               'circumference':(1.12,684,394),'blind':(1.19,655,384),
               'witness':(1.09,683,390),'isolation':(1.1,680,384),
               'twelve_cuts':(1.12,671,389),'deflation':(1.13,658,434),
               'expression':(1.08,690,384)}
        if name in close:
            z,cx,cy=close[name]
            z=1+(z-1)*smooth(age/.6)
            im=im.transform((SW,SH),Image.Transform.AFFINE,
                (1/z,0,cx-SW/(2*z),0,1/z,cy-SH/(2*z)),
                resample=Image.Resampling.BICUBIC,fillcolor=self.bg)
        return im,name
    def birth(self,d,t,age,name,e):
        if name=='power':
            p=smooth(age/1.6);x=75+1100*p
            line(d,[(45,384),(x,384)],INK,4)
            circle(d,x,384,10,RED)
            if p>.55:circle(d,440,384,135*smooth((p-.55)/.45),INK,3)
            center(d,440,606,'me',26,INK)
        elif name=='protection':
            self.me(d,label=True);p=smooth(age/1.2)
            d.arc((205,149,675,619),start=-90,end=-90+359*p,fill=RED,width=5)
            if t>3.189:self.keyword(d,'PROTECTION',size=62)
        elif name=='pieces':
            p=smooth(age/1.2)
            for k in range(8):
                a=k/8*TAU;dx=math.cos(a)*110*(1-p);dy=math.sin(a)*110*(1-p)
                d.arc((305+dx,249+dy,575+dx,519+dy),start=k*45+3,end=(k+1)*45-3,fill=INK,width=40)
            circle(d,555,319,5,RED);center(d,440,614,'me',26)
        elif name=='creation':
            p=smooth(age/1.1)
            self.me(d,opening=(1-p)*TAU*.8,rot=age*.7,label=True)
            if t>6.369:self.keyword(d,'OBJECT',c=RED,size=87)
            # Its empty centre becomes a place that another presence might occupy.
            d.line((625,384,625+350*smooth((age-.4)/1.4),384),fill=PALE,width=2)
        elif name=='parameters':
            self.me(d,label=True)
            for k in range(18):
                a=k/18*TAU;u=smooth((age-k*.09)/.8)
                x,y=xy(440,384,mix(242,135,u),a)
                xx,yy=xy(x,y,18,a)
                line(d,[(x,y),(xx,yy)],RED,3)
                if u>.95:circle(d,*xy(440,384,115,a),5,RED)
        elif name=='initialization':
            p=smooth(age/.85);self.me(d,r=mix(151,135,p),width=mix(52,40,p),label=True)
            for k in range(4):circle(d,440,384,160+k*18*(1-p),color(RED,(1-p)*.45),2)
        elif name=='world':
            p=smooth(age/1.1);self.me(d,r=135,label=True)
            # A horizon is created from the same personal boundary, not a globe.
            line(d,[(440-420*p,555),(440+730*p,555)],INK,2)
            self.peer(d,975,384,47,alpha=smooth((age-.6)/.7),label=True)
        else:
            p=smooth(age/1.8);self.me(d,label=True);self.peer(d,alpha=p,label=True)
            self.ribbon(d,(575,384),(928,384),t,RED,3,18*(1-p))
            d.arc((205,149,675,619),start=0,end=360,fill=color(RED,.22*(1-p)),width=3)
    def encounter(self,d,t,age,name,e):
        u=(t-15.35)/(29.772-15.35);p=smooth(u)
        mx=mix(440,535,p);ux=mix(975,790,p)
        my=384+22*math.sin(age*.8);uy=384-22*math.sin(age*.8)
        self.me(d,mx,my,label=True);self.peer(d,ux,uy,label=True)
        self.ribbon(d,(mx+135,my),(ux-47,uy),t,RED,2,24*math.sin(u*math.pi))
        for k in range(7):
            a=age*.28+k/7*TAU;x,y=xy((mx+ux)/2,384,180+25*math.sin(u*math.pi),a)
            circle(d,x,y,2,color(INK,.26))
        # The fixed rim prepares the next point-set morph.
        if name=='approach':
            q=np.linspace(0,TAU,48,endpoint=False)
            for a in q:circle(d,*xy(mx,my,135,a),3,RED if int(a*8+age)%7==0 else INK)
    def geometry(self,d,t,age,name,e):
        if name!='tangents':self.peer(d,975,384,label=True)
        if name=='points':
            p=smooth(age/1.2)
            for k in range(64):
                a=k/64*TAU;x,y=xy(535,384,135,a)
                z=math.sin(a*3+age)*p*46
                circle(d,x+z,y+math.cos(a*2+age)*p*28,4 if k%3 else 6,RED if k%5==0 else INK)
            # A point-defined body unfolds a third dimension as depth bands.
            for k in range(3):
                d.ellipse((343-k*23*p,254,727+k*23*p,514),outline=color(INK,.25*p),width=2)
            self.ribbon(d,(720,384),(927,384),t,RED,2,0)
            if t>32.1:self.keyword(d,'DIMENSION',size=58)
        elif name=='circumference':
            p=smooth(age/2.65);end=360-265*p
            d.arc((305,249,575,519),start=80,end=80+end,fill=INK,width=35)
            circle(d,540,298,5,RED)
            # The circumference physically unwinds and reaches the receiver.
            q=np.linspace(0,p,80)
            pts=[(440+135*math.sin(v*1.75),519+50*math.sin(v*math.pi)-v*180) for v in q]
            target=(928,384);tip=curve((440,519),target,35,p)
            line(d,[(440,519),tip],RED,17)
            d.arc((305,249,575,519),start=80+end,end=440,fill=color(RED,.28),width=3)
        elif name=='tangents':
            p=smooth(age/1.0);xx=np.linspace(150,1060,180)
            yy=405+np.sin((xx-150)/910*TAU*1.4+t*.75)*96
            line(d,np.stack((xx,yy),axis=-1),INK,17)
            j=int(98+25*math.sin(age*.6));x,y=xx[j],yy[j]
            slope=96*math.cos((x-150)/910*TAU*1.4+t*.75)*TAU*1.4/910
            line(d,[(x-140,y-140*slope),(x+140,y+140*slope)],RED,4)
            self.peer(d,x,y-51,label=True)
            center(d,350,646,'me',24)
        else:
            p=smooth(age/2.2);q=self.q;den=1+np.sin(q)**2
            x=560+np.cos(q)/den*320;y=384+np.sin(q)*np.cos(q)/den*260
            line(d,np.stack((x,y),axis=-1),INK,15)
            d.line((1040,177,1040,604),fill=RED,width=7)
            a=(age*.95)%TAU;den=1+math.sin(a)**2
            circle(d,560+math.cos(a)/den*320,384+math.sin(a)*math.cos(a)/den*260,11,RED)
            if age>1.35:self.keyword(d,'LIMIT',x=1031,y=632,size=34,c=RED)
    def adapt(self,d,t,age,name,e):
        if name=='current':
            p=smooth((t-45.763)/1.3);x=np.linspace(110,915,160)
            ac=384+118*np.sin((x-110)/805*TAU*2+age*2);y=ac*(1-p)+np.full_like(x,384)*p
            line(d,np.stack((x,y),axis=-1),INK,19)
            self.peer(d,1040,384,label=True)
            for k in range(6):circle(d,120+((age*175+k*134)%775),384,5,RED)
            center(d,356,625,'AC',42,c=color(RED,1-p),bold=True);center(d,715,625,'DC',42,c=color(RED,p),bold=True)
        elif name in ('blind','dizzy'):
            self.me(d,label=True);self.peer(d,975,384,alpha=.55 if name=='blind' else 1,label=True)
            p=smooth(age/1.2)
            circle(d,440,384,95,INK)
            if name=='dizzy':
                for k in range(5):
                    a=age*.65+k*.5;x,y=xy(440,384,190+k*26,a)
                    circle(d,x,y,22-k*2,color(RED,.75-k*.13),3)
                line(d,[(150,615+math.sin(age)*35),(1070,615-math.sin(age)*35)],INK,2)
            else:
                d.rectangle((282,368,598,400),fill=RED)
                self.ribbon(d,(575,384),(928,384),t,color(RED,.35),2,35)
        elif name=='travel':
            self.me(d,r=145,label=True);self.peer(d,975,384,label=True)
            direction=1 if age<1.8 else -1;a=-math.pi/2+direction*age*2.3
            line(d,[(440,384),xy(440,384,112,a)],RED,5)
            for k in range(12):
                a=k/12*TAU;line(d,[xy(440,384,151,a),xy(440,384,163,a)],INK,2)
            self.keyword(d,'A.D.',x=88,y=68,size=90,c=color(INK,smooth(2-age)))
            self.keyword(d,'B.C.',x=917,y=556,size=90,c=color(INK,smooth(age-1.7)))
            self.ribbon(d,(585,384),(928,384),t,RED,2,10)
        else:
            p=smooth(age/2.8);mx=440+120*p;ux=975-325*p
            self.me(d,mx,384,label=True);self.peer(d,ux,384,label=True)
            self.ribbon(d,(mx+135,384),(ux-47,384),t,RED,3,35*(1-p))
            d.arc((mx-170,214,mx+170,554),start=age*13,end=age*13+250,fill=color(RED,.3*p),width=2)
    def giving(self,d,t,age,name,e):
        drain=smooth((t-59.056)/14.8)
        self.me(d,500,384,width=40-25*drain,label=True)
        self.peer(d,990,384,r=47+27*drain,label=True)
        if name in ('stimulation','satisfaction'):
            for k in range(17):
                u=(age*.29+k/17)%1
                x,y=curve((566,384),(925,384),(-1 if k%2 else 1)*(92+k%4*13),u)
                circle(d,x,y,4+int(6*self.random[k,2]),RED if k%3 else INK)
            if name=='satisfaction':
                for k in range(6):
                    q=age+k*.12;r=85+(q%1.2)*23
                    d.arc((990-r,384-r,990+r,384+r),start=-70,end=80,fill=color(RED,.28),width=2)
        elif name=='gift_execution':
            # A body is shaved into a gift, leaving its missing edge visible.
            p=smooth(age/2.9);cut=535+82*p
            d.polygon([(cut,244),(670,210),(670,565),(cut,524)],fill=self.bg)
            d.line((cut,243,cut,525),fill=RED,width=3)
            self.ribbon(d,(cut,384),(905,384),t,RED,11,32*p)
        if name=='bounded':
            p=smooth(age/1.9)
            d.arc((250,108,1237,697),start=180,end=180+360*p,fill=RED,width=5)
            for k in range(5):
                a=k/5*TAU;circle(d,*xy(744,403,279,a),4,RED)
    def care(self,d,t,age,name,e):
        self.peer(d,1010,384,label=True)
        if name=='eggplant':
            q=np.linspace(0,TAU,90);r=(.83+.13*np.sin(q))*150
            pts=np.stack((465+np.sin(q)*r*.72+np.cos(q)*20,388+np.cos(q)*r),axis=-1)
            d.polygon([tuple(p) for p in pts],fill=INK)
            d.polygon([(438,246),(475,211),(510,244),(484,270)],fill=RED)
            for k in range(12):
                u=(age*.25+k/12)%1;x,y=curve((480,386),(957,384),80,u)
                circle(d,x,y,7*(1-u)+3,color(RED,.7))
            # The giver contains negative seed holes, increasingly emptied.
            for k in range(8):circle(d,435+(k%2)*50,316+(k//2)*43,8,self.bg)
        elif name=='tomato':
            circle(d,465,384,139,RED)
            for k in range(5):
                a=-math.pi/2+k/5*TAU;x,y=xy(465,280,50,a)
                d.polygon([(465,280),(x,y),xy(465,280,17,a+.5)],fill=INK)
            for k in range(16):
                u=(age*.25+k/16)%1;x,y=curve((475,391),(957,384),-65,u);circle(d,x,y,5,RED)
            d.ellipse((395,339,420,423),fill=self.bg)
        elif name=='cat':
            d.ellipse((345,296,582,502),fill=INK)
            d.polygon([(349,339),(356,231),(414,291)],fill=INK);d.polygon([(515,285),(573,231),(581,339)],fill=INK)
            for x in (413,515):d.ellipse((x-11,352,x+11,373),fill=self.bg)
            d.polygon([(455,390),(474,390),(465,404)],fill=RED)
            for side in (-1,1):
                for k in range(3):line(d,[(465+side*80,393+k*10),(465+side*180,376+k*23)],INK,2)
            self.ribbon(d,(624,400),(950,384),t,RED,3,12+22*e)
            d.arc((384,340,548,502),start=45,end=145,fill=RED,width=2)
        else:
            # A vast identity requires one small witness to retain its outline.
            self.me(d,500,389,r=265,width=97,opening=.25,rot=-.12)
            self.peer(d,1002,384,r=47,label=True)
            line(d,[(750,310),(955,355)],RED,2);line(d,[(756,443),(955,410)],RED,2)
            shadow=[(356,657),(620,657),(840,713),(134,713)]
            d.polygon(shadow,fill=PALE)
            self.keyword(d,'EXISTENCE',size=57)
    def identity(self,d,t,age,name,e):
        if name=='identity':
            mode=.5+.5*math.sin(age*2.2);n=4+int(mode*5)
            q=np.linspace(0,TAU,n+1)+age*.3
            pts=np.stack((500+135*np.cos(q),384+135*np.sin(q)),axis=-1)
            d.polygon([tuple(p) for p in pts],fill=INK);circle(d,500,384,90,self.bg)
            circle(d,580,300,5,RED);self.peer(d,975,384,label=True)
            self.keyword(d,'F',x=297,y=585,size=64,c=color(RED,1-mode));self.keyword(d,'M',x=643,y=585,size=64,c=color(RED,mode))
        elif name=='daynight':
            c=PAPER if self.bg==INK else INK
            self.me(d,500,384,c=c,bg=self.bg,label=False)
            self.peer(d,975,384,bg=self.bg)
            d.arc((347,231,653,537),start=-90,end=-90+(age%3.65)/3.65*360,fill=RED,width=5)
            center(d,500,616,'PM' if self.bg==INK else 'AM',45,c,True)
        elif name=='role':
            p=smooth((age%3.66)/3.66)
            mx,my=curve((455,466),(953,311),102,p)
            ux,uy=curve((953,311),(455,466),-102,p)
            self.me(d,mx,my,r=116,width=36);self.peer(d,ux,uy)
            self.ribbon(d,(mx,my),(ux,uy),t,RED,2,0)
            center(d,mx,my+145,'S' if p<.5 else 'M',31);center(d,ux,uy+75,'M' if p<.5 else 'S',31)
        else:
            a=age*.7;mx=680+185*math.cos(a);my=388+155*math.sin(a)
            ux=680-185*math.cos(a);uy=388-155*math.sin(a)
            self.me(d,mx,my,r=117,width=34);self.peer(d,ux,uy,r=47)
            for k in range(5):
                q=np.linspace(a-k*.17,a-k*.17-2.6,110)
                line(d,np.stack((680+185*np.cos(q),388+155*np.sin(q)),axis=-1),color(INK,.07+.04*k),2)
    def loss(self,d,t,age,name,e):
        if name=='resonance':
            p=smooth(age/3.2);self.me(d,440,384,r=121,width=32,label=True);self.peer(d,960,384,label=True)
            u=np.linspace(0,1,120)
            for k,c in enumerate((INK,RED)):
                x=570+u*333;y=384+64*np.sin(u*TAU*2+t*2+k*math.pi*(1-p))
                line(d,np.stack((x,y),axis=-1),c,4)
        elif name=='completion':
            p=smooth(age/3.05);mx=440+100*p;ux=960-420*p
            self.me(d,mx,384,r=135,width=40);self.peer(d,ux,384,r=47+45*p)
            for k in range(5):circle(d,mx,384,158+k*9*(1-p),color(RED,.12*p),1)
        elif name=='departure':
            p=smooth(age/1.9);self.me(d,540,384,r=135,width=40,opening=smooth(age/5.5)*3.2,rot=0,label=True)
            self.peer(d,540+570*p,384-280*p,r=92-45*p,alpha=1-smooth((age-1.4)/.75))
            repeated=[ln for ln in self.words if 54<=ln.get('id',-1)<=58 and ln['start']<=t]
            for k in range(len(repeated)):
                x=867+k*47;d.line((x,320,x,450),fill=color(INK,.12+k*.035),width=1)
        else:
            self.me(d,498,387,r=177,width=59,opening=math.pi*.82,rot=0,label=True)
            # White absence has precisely the silhouette the red companion occupied.
            d.ellipse((904,337,998,431),outline=PALE,width=1)
            self.keyword(d,'ISOLATION',x=55,y=34,size=77)
            line(d,[(293,637),(718,637)],INK,2)
    def erasure(self,d,t,age,name,e):
        if name=='erase':
            p=smooth(age/3.35);self.fragments(d,500,384,165,p,t)
            for k in range(32):
                if k/32>p:continue
                x=400+self.random[k,0]*210;y=384+age*23+self.random[k,1]*225
                circle(d,x,y,2,color(INK,1-p))
            self.keyword(d,'FRAGMENTS',size=62)
        elif name=='deflation':
            p=smooth(age/2.8);h=135*(1-p*.75)
            d.ellipse((330,584-h*2,670,584),fill=INK)
            d.ellipse((378,588-h*1.65,622,562),fill=self.bg)
            line(d,[(211,584),(877,584)],INK,3)
            d.ellipse((904,337,998,431),outline=PALE,width=1)
        elif name=='challenge':
            p=smooth(age/2.9);self.me(d,660+150*p,384,r=124,width=30,opening=2,rot=0)
            d.line((973,173,973,634),fill=RED,width=7)
            line(d,[(886,381),(973,384-45*p),(1038,384)],INK,3)
        else:
            # A shape attempts an impossible fit through a slot that rejects it.
            self.me(d,680,384,r=121,width=34,opening=2.6,rot=0)
            d.rectangle((986,160,1015,347),fill=RED);d.rectangle((986,421,1015,644),fill=RED)
            p=.5+.5*math.sin(age*4);circle(d,804+154*p,384,49,INK)
            line(d,[(1049,346),(1120,419)],RED,5);line(d,[(1049,419),(1120,346)],RED,5)
            self.keyword(d,'ILLEGAL',size=69,c=RED)
    def execution(self,d,t,age,name,e):
        if name=='compulsion':
            p=smooth(age/13.8)
            # The same body stamps copies of itself into a narrowing corridor.
            for k in reversed(range(10)):
                x=275+k*91;y=384+65*math.sin(k*.7+age*.3)
                r=117*(1-k*.053);a=.12+.66*(1-k/10)
                self.me(d,x,y,r=r,width=31,alpha=a,opening=1.15,rot=.4+age*.12)
            line(d,[(185,205),(1213,289)],RED,3);line(d,[(185,614),(1213,499)],RED,3)
            circle(d,1213,394,28,RED,width=3)
        elif name=='twelve_cuts':
            hits=[ln for ln in self.words if 67<=ln.get('id',-1)<=78 and ln['start']<=t]
            n=len(hits);last=hits[-1]['start'] if hits else t-age
            pulse=math.exp(-(t-last)*5)
            x=655+8*pulse*math.sin(age*21)
            self.me(d,x,388,r=205,width=65,opening=.05,rot=age*.1)
            for k in range(n):
                a=k/12*TAU;pts=[(x,388)]+[xy(x,388,215,v) for v in np.linspace(a,a+.35,8)]
                d.polygon(pts,fill=self.bg)
            # Narrow incision only, with no full-screen flashing.
            d.line((x-120+240*pulse,147,x-120+240*pulse,645),fill=color(RED,.3+.7*pulse),width=4)
            center(d,1136,605,f'{n:02}',62,RED,True)
        elif name=='count':
            words=[w for ln in self.words if ln.get('id') in (79,80,81) for w in ln['words'] if w['start']<=t]
            n=max(1,len(words));self.me(d,640,386,r=185,width=40,opening=math.pi*.88,rot=age*1.5)
            center(d,640,267,str(min(n,6)),173,RED,True)
        elif name=='stamp':
            self.me(d,640,386,r=190,width=60,opening=math.pi,rot=0)
            d.rectangle((575,222,620,551),fill=RED)
        elif name=='execute_all':
            p=smooth(age/6.8)
            for k in range(15):
                x=220+k%5*220;y=229+k//5*175
                self.me(d,x,y,r=62,width=20,opening=p*TAU*.78,rot=k*.41)
            for k in range(4):
                x=335+k*220;d.line((x,122,x,657),fill=color(RED,p*.55),width=2)
        elif name=='recover':
            p=smooth(age/2.8);self.me(d,500,384,r=158,width=48,opening=2.5,rot=0)
            self.ribbon(d,(642,384),(965,384),t,RED,3,30*(1-p))
            d.ellipse((942,361,988,407),outline=PALE,width=2)
            for k in range(5):circle(d,966,384,26+k*13*p,color(RED,.25*(1-p)),1)
        else:
            self.me(d,530,384,r=142,width=43,opening=2.6,rot=0)
            self.boundary(d,530,384,250,INK)
            for k in range(5):d.line((365+k*82,185,365+k*82,584),fill=color(RED,.32),width=3)
    def boundary(self,d,x,y,r,c=INK):
        d.rounded_rectangle((x-r,y-r*.84,x+r,y+r*.84),radius=22,outline=c,width=5)
    def love(self,d,t,age,name,e):
        if name=='study':
            p=smooth(age/3.2);self.me(d,430,400,r=139,width=41,opening=2.5*(1-p),rot=0)
            for k,s in enumerate('LOVE'):
                x=790+k*104;y=270+95*math.sin(age*.6+k*.7)*(1-p)
                center(d,x,y,s,93,RED if s=='O' else INK,True)
            self.ribbon(d,(568,400),(1035,400),t,color(RED,.35),2,23)
        elif name=='answer':
            self.me(d,485,384,r=151,width=43,opening=1.8,rot=0)
            center(d,965,243,'?',150,INK,True)
            p=smooth(age/2.5)
            for k in range(4):
                y=445+k*34;x=742+79*p
                d.line((x,y,1028,y),fill=color(RED,.38+.14*k),width=2)
            circle(d,965,618,5,RED)
        elif name=='expression':
            # Correctly arranged forms leave the same unfillable negative centre.
            self.me(d,480,417,r=147,width=41,opening=1.5,rot=0)
            self.keyword(d,'me + you',x=705,y=263,size=88)
            self.keyword(d,'= ?',x=846,y=429,size=102,c=RED)
            d.ellipse((840,534,934,628),outline=PALE,width=2)
        else:
            self.me(d,515,389,r=130,width=40,opening=1.5,rot=0)
            self.boundary(d,515,389,232,INK)
            for k in range(5):line(d,[(374+k*71,213),(374+k*71,565)],color(INK,.27),3)
            p=smooth((t-188.294)/5.5)
            ux=950+145*p;uy=382-60*math.sin(age*.4)
            self.peer(d,ux,uy,label=True)
            self.ribbon(d,(648,389),(745,389),t,RED,2,20)
            if name=='waiting':
                d.ellipse((468,342,562,436),outline=color(RED,.23),width=1)
                line(d,[(748,389),(817,389)],PALE,2)
    def last_switch(self,d,t,age,e):
        p=smooth(age/1.7);r=135*(1-p)
        self.me(d,515,389,r=max(1,r),width=max(1,40*(1-p)),alpha=1-p)
        line(d,[(55,389),(1250,389)],color(INK,1-p),2)
        circle(d,mix(1120,55,p),389,max(1,7*(1-p)),color(RED,1-p))
    def credits(self,d):
        self.keyword(d,'world.execute(me);',x=72,y=67,size=72)
        rows=[('Music / lyrics','Mili'),('Original geometry / code','soralcf — AI-assisted production'),('Character original','Mingyue / Shangshan Wuxing'),('Maid design','ZipZipPipe'),('Illustration / expressions','Small-tailqwq / JAdpp'),('Artwork','CC BY-NC-SA 4.0 / contains AI art'),('Lyric timing / helper','MisakaZentai / MIT')]
        for k,(a,b) in enumerate(rows):
            y=251+k*54;d.text((78,y),a,font=font(23),fill=MUTED);d.text((409,y),b,font=font(25),fill=INK)
        d.text((79,665),'Unofficial, noncommercial fan work. Full attribution: NOTICE.md',font=font(23),fill=RED)
    def sidebar(self,im,t,name):
        d=ImageDraw.Draw(im)
        d.line((449,116,449,872),fill=PALE,width=1)
        d.text((58,55),'me',font=font(39,True),fill=INK)
        connected=t<110.8
        circle(d,365,77,5,RED if connected else MUTED)
        d.text((384,60),'you' if connected else '—',font=font(24),fill=INK if connected else MUTED)
        face='serious' if t<15.35 else 'starry' if t<44.412 else 'confused' if t<55.084 else 'shy' if t<73.926 else 'cheerful' if t<88.54 else 'exasperated' if t<103.522 else 'starry' if t<110.405 else 'frightened' if t<118.236 else 'shy' if t<125.582 else 'angry' if t<177.442 else 'shy' if t<188.294 else 'serious'
        avatar=self.faces[face]
        opacity=.24+.76*smooth(t/5.8)
        if name in ('twelve_cuts','execute_all'):opacity=.84
        if opacity<1:avatar=avatar.copy();avatar.putalpha(avatar.getchannel('A').point(lambda a:round(a*opacity)))
        breath=2*math.sin(t*1.8)
        im.paste(avatar,(83,int(131+breath)),avatar)
        d=ImageDraw.Draw(im)
        d.text((61,469),'whale / a conversation',font=font(16),fill=MUTED)
        d.line((59,501,416,501),fill=PALE)
        visible=[msg for msg in self.messages if msg[0]<=t][-3:]
        y=537
        for onset,who,text in visible:
            c=INK if who=='me' else RED
            d.text((60,y),who,font=font(18,True),fill=c)
            count=max(0,min(len(text),int((t-onset)*32)))
            words=text[:count].split();rows=[];current=''
            for word in words:
                test=(current+' '+word).strip()
                if d.textlength(test,font=font(22))>350 and current:rows.append(current);current=word
                else:current=test
            if current:rows.append(current)
            for j,row in enumerate(rows[:2]):d.text((60,y+27+j*28),row,font=font(22),fill=c)
            y+=100
        if t>110.8:
            d.text((60,870),'awaiting a reply',font=font(17),fill=MUTED)
    def captions(self,d,t):
        ln=next((ln for ln in self.words if ln['start']<=t<ln['hold_until']),None)
        d.line((60,938,1860,938),fill=PALE,width=1)
        if ln is None:return
        size=44
        while size>26 and d.textlength(ln['text'],font=font(size,True))>1750:size-=1
        widths=[d.textlength(w['text'],font=font(size,True)) for w in ln['words']]
        space=d.textlength(' ',font=font(size));total=sum(widths)+space*(len(widths)-1);x=(W-total)/2
        fade=1-smooth((t-ln['end']-.25)/.4)
        for w,width in zip(ln['words'],widths):
            active=w['start']<=t<w['end'];future=t<w['start']
            c=RED if active else MUTED if future else INK
            d.text((x,977),w['text'],font=font(size,active),fill=color(c,fade*(.52 if future else 1)))
            if active:d.line((x,1036,x+width,1036),fill=color(RED,fade),width=3)
            x+=width+space
    def render(self,i):
        t=i/FPS-self.offset;idx=max(0,min(self.track.n-1,i));e=float(self.track.energy[idx])
        im=self.paper.copy();stage,name=self.scene(t,e)
        im.paste(stage,(491,114));d=ImageDraw.Draw(im)
        d.text((491,49),'world.execute(me);',font=font(24,True),fill=INK)
        d.text((1585,57),'MILI / FAN VISUAL',font=font(16),fill=MUTED)
        self.sidebar(im,t,name);d=ImageDraw.Draw(im);self.captions(d,t)
        d.text((60,1057),'AI-assisted code / contains AI character artwork',font=font(12),fill=MUTED)
        d.text((1433,1057),'Art credits & licenses: NOTICE.md',font=font(12),fill=MUTED)
        remaining=self.track.duration-i/FPS
        if remaining<.9:
            u=smooth(remaining/.9);im=im.point(lambda a:round(a*u))
        return im
