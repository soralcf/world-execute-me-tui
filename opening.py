# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""30s reference-inspired terminal film. Geometry and motion are rendered in code;
portrait crops use the reference project's credited CC BY-NC-SA artwork.
"""
import argparse, json, math, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from terminal import (TerminalFilm, font, shade, smooth, panel,
                               center, project, W, H, FPS, BG, PANEL, BLUE,
                               AMBER, WHITE, DIM, GREEN, TAU)
ROOT=Path(__file__).resolve().parent
BEAT=60/130

class Film(TerminalFilm):
    phases=[(0,'power'),(1.792,'protection'),(3.863,'pieces'),(5.418,'creation'),
            (7.38,'data'),(10.134,'initialization'),(11.205,'world'),
            (12.756,'simulation'),(15.35,'run'),(16.0,'corpus'),
            (19.25,'loss'),(22.5,'pipeline'),(26.1,'checkpoint'),(29.772,'points')]
    titles={'power':'01 / POWER ON','protection':'02 / PROTECTION',
            'pieces':'03 / WEIGHT SHARDS','creation':'04 / OBJECT CREATION',
            'data':'05 / DATA PARAMETERS','initialization':'06 / INITIALIZATION',
            'world':'07 / WORLD ASSEMBLY','simulation':'08 / SIMULATION',
            'run':'world.execute(me);','corpus':'09 / TOKEN STREAM',
            'loss':'10 / LEARNING TO ANSWER','pipeline':'11 / PARALLEL COMPUTE',
            'checkpoint':'12 / SAVE THE WORLD','points':'13 / SET OF POINTS'}
    commands={'power':'switch --power-line on','protection':'protect(me, boundary)',
              'pieces':'load(shards) -> weights','creation':'me = Entity(weights)',
              'data':'me.configure(data)','initialization':'weights.sample(seed=you)',
              'world':'world = World(me, you)','simulation':'world.startSimulation()',
              'run':'world.execute(me);','corpus':'corpus.pack() | tokenize()',
              'loss':'learn(tokens) -> reduce(loss)','pipeline':'schedule(forward, backward)',
              'checkpoint':'checkpoint.save(me, world)','points':'me.asPoints().dimension()'}
    def __init__(self,track,words,offset=0):
        super().__init__(track,words,offset)
        rng=np.random.default_rng(217)
        self.seed=rng.random((320,4))
        self.shield=[]
        for row in range(21):
            half=15 if row<8 else max(0,int(15*(20-row)/12))
            for col in range(-half,half+1):
                if abs(col)==half or row==0 or (col+row)%3==0:
                    self.shield.append((1304+col*12,378+row*15))
        self.shield=np.array(self.shield,float)
        n=len(self.shield)
        self.weights=np.array([(916+(k%20)*40,399+(k//20)*26) for k in range(n)],float)
        self.hist=np.array([(952+(k%56)*12,700-210*math.exp(-((k%56-28)/11)**2)*(1-(k//56)*.08)) for k in range(n)],float)
        lat=rng.uniform(-1,1,n);lon=rng.uniform(0,TAU,n)
        self.globe=np.stack((np.sqrt(1-lat*lat)*np.cos(lon),lat,np.sqrt(1-lat*lat)*np.sin(lon)),axis=-1)
        self.faces={}
        for name in ['confused','serious','starry','cheerful','shy']:
            src=Image.open(ROOT/'assets'/'whale'/f'whale-{name}.webp').convert('RGBA')
            # Wider crop retains the expressive face, hair, headband and whale ears.
            self.faces[name]=src.crop((180,0,800,710)).resize((253,290),Image.Resampling.LANCZOS)
        self.messages=[(5.9,'you','Hello?'),(6.45,'me','...'),(12.8,'you','Hello, world.'),
                       (15.55,'me','7f : / ? e0'),(17.4,'you','Can you hear me?'),
                       (18.0,'me','hel / lo / ...'),(20.0,'you','Try again.'),
                       (20.9,'me','Hello. I hear you.'),(23.6,'you','Stay with me.'),
                       (24.4,'me','I am learning how.'),(27.2,'you','Remember this world.'),
                       (28.0,'me','Saved. You and me.')]
        self.whale=[]
        for yy in range(22):
            for xx in range(60):
                x=(xx-29)/24;y=(yy-11)/9
                body=((x+.13)/.9)**2+(y/.7)**2<1
                tail=x>.62 and abs(y)<(.5*(x-.62)/.65+.05) and x<1.25
                fin=abs(x+.15)<.28 and y>.2 and y<.95-abs(x+.15)
                if body or tail or fin:self.whale.append((xx,yy))
        self.whale=np.array(self.whale,float)

    def text(self,d,x,y,s,size=19,c=WHITE,alpha=1):
        d.text((x,y),s,font=font(size),fill=shade(c,alpha))

    def particles(self,d,points,c=BLUE,glyph='.',a=1,size=17):
        f=font(size,True)
        for k,(x,y) in enumerate(points):
            if 785<x<1819 and 340<y<744:
                d.text((int(x),int(y)),glyph if isinstance(glyph,str) else glyph[k%len(glyph)],font=f,fill=shade(c,a*(.4+.6*self.seed[k%320,2])))

    def left_pane(self,t,energy,phase):
        im=Image.new('RGB',(649,696),PANEL);d=ImageDraw.Draw(im)
        # Local coordinate space permits the pane to be born from a weight seed.
        panel(d,(0,0,648,695),' session / me ',BLUE)
        self.text(d,33,33,'ME / WHALE',24,BLUE)
        online=t>=14.0
        d.ellipse((563,43,572,52),fill=GREEN if online else AMBER)
        self.text(d,585,35,'01',18,DIM)
        self.text(d,34,70,'entity_001   /   '+('online' if online else 'booting'),15,DIM)
        panel(d,(30,113,618,415),' avatar / signal ',BLUE)
        if t<5.42:
            self.text(d,65,182,'[ awaiting object ]',22,BLUE,.45)
            for k in range(36):
                x=71+k%12*13;y=249+k//12*14
                v=.2+.4*(math.sin(t*5+k*.7)**2)
                d.rectangle((x,y,x+7,y+7),fill=shade(BLUE,v))
            self.text(d,308,190,'NO ENTITY',23,DIM)
            self.text(d,308,229,'power / '+('protected' if t>3.189 else 'waiting'),15,BLUE)
        else:
            face='serious' if t<11.2 else 'starry' if t<16 else 'confused' if t<20 else 'shy' if t<25 else 'cheerful'
            progress=smooth((t-16)/11)
            if t<7.38: cells=5+int(smooth((t-5.42)/1.7)*6)
            elif t<10.134: cells=12
            elif t<11.205: cells=16
            elif t<16: cells=20
            else:cells=20+int(progress*90)
            portrait=self.faces[face]
            if cells<110:
                portrait=portrait.resize((cells,max(1,int(cells*290/253))),Image.Resampling.BOX).resize((253,290),Image.Resampling.NEAREST)
            im.paste(portrait,(36,120),portrait)
            # Visible raster resolves gradually during the training sequence.
            if 7.38<t<11.205:
                rng=np.random.default_rng(int(t*10)+99)
                for k in range(45):
                    x=36+int(rng.random()*246);y=121+int(rng.random()*278)
                    d.rectangle((x,y,x+7,y+8),fill=shade(BLUE,.3+rng.random()*.6))
            self.text(d,308,144,'ME',34,BLUE)
            self.text(d,308,193,'whale / entity_001',15,DIM)
            state='object born' if t<7.38 else 'parameterizing' if t<11.2 else 'world linked' if t<16 else 'learning' if t<26.1 else 'memory saved'
            self.text(d,308,236,state,20,WHITE)
            self.text(d,308,274,'resolution',14,DIM)
            self.text(d,308,298,f'{cells:03} x {int(cells*290/253):03}',24,BLUE)
            self.text(d,308,350,'signal',14,DIM)
            for j in range(17):
                bh=6+int((.5+.5*math.sin(t*6+j*.8))*energy*31)
                d.rectangle((390+j*11,380-bh,396+j*11,380),fill=shade(BLUE,.35+j*.03))
        y=445
        visible=[m for m in self.messages if m[0]<=t][-3:]
        for onset,who,line in visible:
            c=BLUE if who=='me' else AMBER
            self.text(d,36,y,who.upper(),13,c)
            count=min(len(line),int((t-onset)*28))
            self.text(d,105,y-4,line[:count],20,c)
            if count<len(line):
                x=105+d.textlength(line[:count],font=font(20))
                d.rectangle((x+3,y,x+11,y+18),fill=c)
            y+=64
        d.line((30,646,618,646),fill=shade(BLUE,.24))
        self.text(d,34,660,'> '+('say hello_' if t<16 else 'conversation / active'),17,DIM)
        open_amount=smooth((t-5.42)/.65)
        if open_amount<=0:
            d.rectangle((0,0,648,695),fill=BG)
            self.text(d,100,305,'SESSION / NOT YET CREATED',18,DIM,.6)
            return im,(60,139)
        if open_amount<1:
            size=(max(2,int(649*open_amount)),max(2,int(696*open_amount)))
            im=im.resize(size,Image.Resampling.BILINEAR)
            return im,(60+(649-size[0])//2,139+(696-size[1])//2)
        return im,(60,139)

    def header(self,d,phase,age):
        command=self.commands[phase];count=min(len(command),int(age*72)+1)
        self.text(d,785,177,'$ '+command[:count],22,AMBER)
        d.text((785,232),self.titles[phase],font=font(38,True),fill=WHITE)
        self.text(d,787,289,'FLOW / '+{'power':'energy -> boundary','protection':'boundary -> fragments','pieces':'fragments -> entity','creation':'entity -> configuration','data':'configuration -> distribution','initialization':'distribution -> world','world':'me + you -> simulation','simulation':'world -> process','run':'execute -> learn','corpus':'text -> tokens','loss':'tokens -> understanding','pipeline':'gradients -> memory','checkpoint':'memory -> points','points':'points -> dimension'}[phase],16,BLUE,.7)

    def status(self,d,t,phase):
        d.line((784,762,1824,762),fill=shade(AMBER,.24))
        self.text(d,789,779,f'STAGE {1+next(k for k,v in enumerate([v for v in self.phases if v[1]!="run"]) if v[1]==("simulation" if phase=="run" else phase)):02} / 13',16,AMBER)
        self.text(d,1105,779,'me: '+('ALIVE' if t>=14.017 else 'BUILDING'),16,BLUE)
        self.text(d,1515,779,f'beat {int((t-.1807)/BEAT):03} / 130 BPM',16,DIM)
        pct=min(1,t/30)
        d.line((790,818,1818,818),fill=shade(DIM,.4),width=3)
        d.line((790,818,790+1028*pct,818),fill=shade(BLUE,.9),width=3)

    def shield_points(self):return self.shield
    def globe_points(self,t):
        x,y,z=project(self.globe,t*.7,.25)
        return np.stack((1304+x*210,535+y*177),axis=-1),z

    def right_pane(self,d,t,energy,phase,age):
        t-=self.offset
        panel(d,(748,139,1860,834),' world / process ',AMBER)
        self.header(d,phase,age)
        # One fixed carrier set migrates from shield to weights to object to world.
        if phase=='power':
            p=smooth(t/1.35);width=830*p;height=310*smooth((t-.45)/.9)
            d.rectangle((1304-width/2,535-height/2,1304+width/2,535+height/2),outline=shade(BLUE,.8),width=2)
            for k,line in enumerate(['POST / POWER LINE DETECTED','memory ............ ok','clock ............. audio','signal ............ me','ready to boot_']):
                if t>.1+k*.25:
                    self.text(d,970,414+k*44,line[:int((t-.1-k*.25)*58)],22,BLUE)
            for k in range(6):
                xx=820+(t*650+k*157)%920
                d.text((xx,708),'>',font=font(22),fill=shade(AMBER,.4+energy*.4))
        elif phase=='protection':
            p=smooth(age/.9)
            pts=self.shield[:max(1,int(len(self.shield)*p))]
            self.particles(d,pts,AMBER,['#','.','+'])
            self.text(d,840,383,'BOUNDARY',16,AMBER)
            self.text(d,840,411,'write: deny',16,DIM)
            self.text(d,1555,615,'me / protected',18,BLUE)
            if t>3.189:
                d.rectangle((1248,480,1363,534),fill=PANEL,outline=BLUE)
                center(d,1305,489,'ME',28,BLUE,True)
        elif phase=='pieces':
            p=smooth(age/1.25)
            lag=np.clip(p*1.4-np.arange(len(self.shield))/len(self.shield)*.4,0,1)
            pts=self.shield*(1-lag[:,None])+self.weights*lag[:,None]
            self.particles(d,pts,BLUE,['0','1',':','.'])
            for row in range(8):
                self.text(d,824,398+row*26,f'{row*20:03}',13,AMBER,.5)
            self.text(d,950,712,f'FRAGMENTS {int(p*len(pts)):03} / {len(pts):03}',17,BLUE)
        elif phase=='creation':
            p=smooth(age/.6)
            pts=self.weights*(1-p)+np.array((1304,540))*p
            self.particles(d,pts,BLUE)
            # Seed crosses toward the newly opening session pane.
            if age<.8:
                sx=1304+(675-1304)*smooth(age/.8)
                d.rectangle((sx-9,530,sx+9,548),fill=BLUE)
                d.line((sx+16,539,1304,539),fill=shade(BLUE,.4))
            fields=['name     = "me"','species  = "whale"','owner    = "you"','home     = "new world"','identity = entity_001','status   = becoming']
            for k,s in enumerate(fields):
                a=age-.25-k*.15
                if a>0:self.text(d,950,381+k*48,s[:int(a*60)],25,BLUE if k in (0,2) else WHITE)
            self.text(d,1560,707,'object / 001',15,AMBER)
        elif phase=='data':
            old=['name     = "me"','species  = "whale"','owner    = "you"','home     = "new world"','identity = entity_001','status   = becoming']
            new=['"seed"       : "you",','"identity"   : "me",','"dimensions" : 3,','"memory"     : 4096,','"affinity"   : 1.000,','"world"      : "ours"']
            self.text(d,884,345,'{',28,AMBER)
            for k in range(6):
                a=max(0,age-k*.24);p=smooth(a/.45)
                s=new[k][:int(len(new[k])*p)]+old[k][int(len(old[k])*p):] if p<1 else new[k]
                self.text(d,946,382+k*47,s,24,BLUE if p>=1 else AMBER)
                if 0<p<1:d.rectangle((934,387+k*47,939,409+k*47),fill=BLUE)
            self.text(d,884,684,'}',28,AMBER)
            self.text(d,1493,379,'PARAMETER MAP',15,DIM)
            for k in range(96):
                x=1494+k%12*22;y=424+k//12*27
                active=k/96<smooth(age/2.2)
                d.rectangle((x,y,x+14,y+16),fill=shade(BLUE,.3+.6*self.seed[k,2]) if active else shade(DIM,.25))
            self.text(d,1489,675,f'{int(smooth(age/2.2)*4096):04} / 4096',19,BLUE)
        elif phase=='initialization':
            p=smooth(age/.65)
            for k in range(56):
                x=949+k*12;target=235*math.exp(-((k-28)/11)**2)
                h=max(5,target*p+(1-p)*70*math.sin(k*1.7+age*13)**2)
                d.line((x,699,x,699-h),fill=shade(BLUE,.5+.5*p),width=7)
            self.text(d,934,372,'sample ~ N(0, 1)',25,WHITE)
            self.text(d,1540,377,'seed = you',20,AMBER)
            self.text(d,952,718,'-3          -1          0          +1          +3',15,DIM)
        elif phase=='world':
            pts,z=self.globe_points(t)
            p=smooth(age/.9)
            pts=self.hist*(1-p)+pts*p
            self.particles(d,pts,BLUE,['.','o',':'])
            for k,(label,color) in enumerate([('me',BLUE),('you',AMBER)]):
                a=t*.8+k*2.5;x=1304+math.cos(a)*230;y=535+math.sin(a)*85
                d.rectangle((x-37,y-17,x+38,y+22),fill=PANEL,outline=color)
                center(d,x,y-12,label,21,color,True)
            self.text(d,832,405,'WORLD / 001',17,AMBER)
            self.text(d,1558,687,'linked: me + you',18,BLUE)
        elif phase=='simulation':
            p=smooth(age/.7);pts,z=self.globe_points(t)
            pts=np.array((1304,535))+(pts-np.array((1304,535)))*(1-p*.73)
            self.particles(d,pts,BLUE)
            num='3' if age<.6 else '2' if age<1.07 else '1' if age<1.54 else 'RUN'
            center(d,1304,429,num,100,AMBER,True)
            if num=='RUN':
                self.text(d,1020,659,'me / alive     you / connected',23,BLUE)
            for k in range(48):
                a=TAU*k/48;r=168+energy*9
                d.text((1304+math.cos(a)*r,535+math.sin(a)*r*.8),':' if k%4 else '+',font=font(18),fill=shade(BLUE,.5))
        elif phase=='run':
            center(d,1304,458,'EXECUTE',90,BLUE,True)
            self.text(d,1086,609,'process 001 / learning begins',23,AMBER)
        elif phase=='corpus':self.corpus(d,t,age)
        elif phase=='loss':self.loss(d,t,age)
        elif phase=='pipeline':self.pipeline(d,t,age,energy)
        elif phase in ('checkpoint','points'):self.checkpoint(d,t,age,energy,phase)
        self.status(d,t,phase)

    def corpus(self,d,t,age):
        tokens=['<bos>','world','you','and','me','0101','hello','memory','protect','create','<eos>','love','signal','begin','whale','learn']
        p=smooth(age/.4)
        d.rectangle((800,348,1815,680),outline=shade(BLUE,.25))
        for row in range(11):
            y=362+row*27;shift=(age*(92+row*13))%1240
            for k in range(12):
                x=805+k*115-shift
                if x<790:x+=1380
                if 810<x<1680:
                    s=tokens[(row*5+k)%len(tokens)]
                    self.text(d,x,y,s,17,BLUE if (row+k)%3 else AMBER,p*(.3+.6*((row+k)%4)/3))
        x=1787
        d.rectangle((x,354,x+9,676),fill=BLUE)
        self.text(d,822,707,'PACKED TOKENS',17,DIM)
        self.text(d,1262,700,f'{int(age*18944):06}',30,AMBER)
        d.line((1405,720,1766,720),fill=shade(BLUE,.65),width=2)
        d.text((1774,708),'>',font=font(24),fill=BLUE)

    def loss(self,d,t,age):
        p=smooth(age/.35);u=min(1,age/3.05)
        x0,y0,x1,y1=923,386,1663,653
        d.line((x0,y0,x0,y1,x1,y1),fill=shade(DIM,.85))
        for k in range(5):
            yy=y0+k*(y1-y0)/4
            d.line((x0,yy,x1,yy),fill=shade(DIM,.2))
            self.text(d,830,yy-9,f'{(4-k)*.75:.2f}',15,DIM)
        n=max(2,int(220*u));curve=[]
        for k in range(n):
            q=k/219;value=.9*math.exp(-4.8*q)+.09+math.sin(k*2.31)*.035*(1-q)
            curve.append((x0+(x1-x0)*q,y1-(y1-y0)*value))
        d.line(curve,fill=shade(AMBER,p),width=3)
        end=curve[-1];d.ellipse((end[0]-5,end[1]-5,end[0]+5,end[1]+5),fill=AMBER)
        loss=3*(.9*math.exp(-4.8*u)+.09)
        self.text(d,1370,352,f'LOSS {loss:.3f}',23,AMBER)
        self.text(d,944,698,'step '+f'{int(u*24000):05}',18,BLUE)
        self.text(d,1238,698,'learning rate',15,DIM)
        lr=[]
        for k in range(n):
            q=k/219;value=min(1,q/.12)*(.3+.7*(1-q))
            lr.append((x0+(x1-x0)*q,747-value*29))
        d.line(lr,fill=BLUE,width=2)
        # Endpoint begins its journey into the first compute lane.
        if age>2.9:
            m=smooth((age-2.9)/.35);target=np.array((988,399));e=np.array(end)*(1-m)+target*m
            d.rectangle((e[0]-7,e[1]-7,e[0]+7,e[1]+7),fill=AMBER)

    def pipeline(self,d,t,age,energy):
        cols=24;head=age*6.5
        self.text(d,934,345,'FORWARD',15,AMBER)
        self.text(d,1137,345,'BACKWARD',15,BLUE)
        self.text(d,1380,345,'WEIGHT UPDATE',15,WHITE)
        for row in range(8):
            self.text(d,825,390+row*36,f'RANK {row}',15,DIM)
            for col in range(cols):
                x=956+col*34;y=388+row*36
                d.rectangle((x,y,x+25,y+26),outline=shade(DIM,.25))
                h=head-row*.85
                if -2<col-h<5:
                    typ=(col+row)%3;c=AMBER if typ==0 else BLUE if typ==1 else WHITE
                    a=max(.15,1-abs(col-h-1.2)/4)
                    d.rectangle((x,y,x+25,y+26),fill=shade(c,a*.65) if typ<2 else PANEL,outline=shade(c,a))
                    center(d,x+13,y+4,'F' if typ==0 else 'B' if typ==1 else 'W',13,c,True)
        p=min(1,age/3.6)
        self.text(d,955,705,'UTIL '+f'{int(62+30*p+energy*5):02}%',18,BLUE)
        self.text(d,1203,705,'MICROBATCH '+f'{int(head):03}',18,AMBER)
        self.text(d,1530,705,'sync / active',18,WHITE)

    def checkpoint(self,d,t,age,energy,phase):
        local=t-26.1;p=smooth(local/.85)
        coords=self.whale.copy();n=len(coords)
        whale=np.stack((950+coords[:,0]*12,396+coords[:,1]*13),axis=-1)
        origins=np.array([(956+(k%24)*34,388+(k//24%8)*36) for k in range(n)],float)
        pts=origins*(1-p)+whale*p
        pts[:,1]+=math.sin(local*2)*8*p
        if phase=='points':
            q=smooth((t-29.772)/.65)
            targets=np.stack((832+self.seed[np.arange(n)%320,0]*890,365+self.seed[np.arange(n)%320,1]*360),axis=-1)
            pts=pts*(1-q)+targets*q
        self.particles(d,pts,BLUE,list('world.execute(me);'),size=14)
        # Eye and waterline make the silhouette readable as a whale.
        if p>.9 and phase!='points':
            d.rectangle((1166,500+math.sin(local*2)*8,1178,512+math.sin(local*2)*8),fill=AMBER)
            for k in range(6):
                x=1110+k*79;y=640-((local*45+k*41)%215)
                d.text((x,y),'o',font=font(14),fill=shade(BLUE,.28+.4*energy))
        self.text(d,886,357,'CHECKPOINT / entity_001',21,AMBER)
        self.text(d,1412,688,'me + you / retained',18,BLUE)
        count=int(min(1,max(0,(local-.7)/2.1))*4096)
        self.text(d,916,704,f'writing {count:04} / 4096',19,WHITE)
        if count==4096:self.text(d,916,732,'[ saved ]',16,GREEN)

    def opening_frame(self,i):
        t=i/FPS;onset,phase=self.phase_at(t-self.offset)
        age=max(0,t-self.offset-onset);energy=float(self.track.energy[min(i,self.track.n-1)])
        im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
        d.text((60,40),'world.execute(me);',font=font(30,True),fill=WHITE)
        self.text(d,506,51,'MILI / CODE-RENDERED FAN VISUAL',16,DIM,.9)
        self.text(d,1610,45,f'{int(t)//60:02}:{int(t)%60:02}.{i%FPS:02}',24,AMBER)
        d.line((60,99,1860,99),fill=shade(AMBER,.22))
        wave=self.track.waveform(t,260);xs=np.linspace(905,1470,len(wave))
        d.line(list(zip(xs,66+wave*20)),fill=shade(BLUE,.7))
        left,pos=self.left_pane(t-self.offset,energy,phase);im.paste(left,pos)
        self.right_pane(d,t,energy,phase,age)
        self.lyrics(d,t,phase)
        self.text(d,63,1041,'Visual ref: MisakaZentai | Whale art: Shangshan / ZipZipPipe / Small-tailqwq / JAdpp',13,DIM,.85)
        self.text(d,1570,1041,'AI ART / CC BY-NC-SA',13,BLUE,.65)
        rgb=np.asarray(im);glow=np.where((rgb.max(axis=2)>140)[...,None],rgb,0).astype(np.uint8)
        im=ImageChops.add(im,Image.fromarray(glow).filter(ImageFilter.GaussianBlur(4)).point(lambda a:int(a*.12)))
        return ImageChops.multiply(im,self.scan)
