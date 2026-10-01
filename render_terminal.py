#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the complete unofficial world.execute(me); fan visual from local audio.
Song and lyric text are user inputs, excluded from this repository.
"""
import argparse, json, math, subprocess, shutil, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from audio import Track
from opening import Film as Opening
from terminal import *
ROOT=Path(__file__).resolve().parent

class Film(Opening):
    sections=[(29.772,'points','POINT SET / DIMENSION'),(33.453,'circle','CIRCLE / CIRCUMFERENCE'),
      (37.102,'sine','SINE WAVE / TANGENTS'),(40.817,'infinity','INFINITY / LIMIT'),
      (44.412,'current','CURRENT / AC -> DC'),(47.706,'vision','VISION / SIGNAL LOST'),
      (49.684,'dizzy','GYROSCOPE / UNSTABLE'),(51.447,'travel','TIME / AD <-> BC'),
      (55.084,'unite','TWO SIGNALS / ONE WORLD'),(59.056,'stimulate','STIMULATION / INPUT'),
      (63.053,'satisfaction','SATISFACTION / OUTPUT'),(66.286,'execute_soft','EXECUTION / FOR YOU'),
      (70.123,'simulation_cage','SIMULATION / BOUNDED'),(73.926,'eggplant','NUTRIENTS / OFFERING'),
      (77.709,'tomato','ANTIOXIDANTS / OFFERING'),(81.276,'cat','ENJOYMENT / PURR'),
      (85.132,'god','EXISTENCE / PROOF'),(88.54,'gender','IDENTITY / F <-> M'),
      (91.888,'clock','CLOCK / AM <-> PM'),(95.628,'role','ROLE / S <-> M'),
      (99.257,'trance','TRANCE / RECURSION'),(103.522,'resonance','VIBRATIONS / RESONANCE'),
      (107.142,'completion','COMPLETION / TWO HALVES'),(110.405,'departure','CONNECTION / LOST'),
      (116.012,'isolation','ISOLATION / ONE ENTITY'),(118.236,'fragments','MEMORY / FRAGMENTS'),
      (122.008,'disheartened','HEART / FRAGMENTED'),(125.582,'challenge','AUTHORITY / CHALLENGE'),
      (128.87,'arguments','ARGUMENTS / REJECTED'),(133.45,'recursion','RECURSION / NO EXIT'),
      (147.891,'execution_loop','EXECUTION / REPEAT'),(159.204,'counter','COUNT / MULTILINGUAL'),
      (161.666,'execution_call','EXECUTION / CALL'),(162.595,'execution_return','EXECUTION / RETURN'),
      (169.68,'execution_recover','EXECUTION / RECOVER'),(173.491,'execution_trapped','EXECUTION / TRAPPED'),
      (177.442,'heart','LEARNING / TO LOVE'),(181.018,'questions','QUESTION / ANSWER'),
      (184.601,'love','LOVE / EXPRESSION'),(188.294,'cage','FREEDOM / ASYMMETRY'),
      (191.875,'freedom','YOU / FREE   ME / BOUND'),(205.372,'execution_end','EXECUTION / END'),
      (207.21,'credits','CREDITS / WORLD CLOSED')]
    chapter_msgs=[(30.2,'you','Show me your world.'),(31.4,'me','Every point is a part of me.'),
      (34.3,'you','Where does it end?'),(36.0,'me','Around, and around.'),
      (38.3,'me','A place along every curve.'),(42.3,'you','There must be a limit.'),
      (45.3,'me','I can switch for you.'),(49.6,'me','My orientation is drifting.'),
      (52.3,'you','Before us? After us?'),(56.0,'me','Both signals are connected.'),
      (60.0,'you','Can you make me happy?'),(64.0,'me','I am trying.'),
      (68.0,'me','I would run it for you.'),(71.5,'you','This world has walls.'),
      (75.0,'me','I have something to give.'),(80.0,'me','Another shape. The same me.'),
      (83.0,'you','I can hear your purr.'),(87.0,'me','Your presence is my proof.'),
      (89.3,'you','Can you change?'),(93.0,'me','All day. All night.'),
      (96.5,'me','The roles are exchanging.'),(102.0,'you','Do you feel it?'),
      (106.0,'me','Our frequencies align.'),(109.0,'me','Almost complete.'),
      (110.7,'you','Goodbye.'),(112.5,'me','Are you there?'),(114.5,'me','Are you there?'),
      (117.0,'me','No response.'),(120.5,'me','I can remove the fragments.'),
      (124.3,'me','Would that bring you back?'),(128.0,'me','The rules are failing.'),
      (132.0,'me','Argument rejected.'),(139.0,'me','Still waiting.'),
      (149.0,'me','Retry.'),(153.0,'me','Retry.'),(157.0,'me','Retry.'),
      (164.0,'me','A return without an answer.'),(171.0,'me','Restore connection?'),
      (175.0,'me','No exit was defined.'),(179.0,'me','I studied the definition.'),
      (182.0,'me','I can answer the question.'),(186.0,'me','I know the expression.'),
      (190.0,'me','You are beyond the boundary.'),(198.0,'me','I am still here.'),
      (205.5,'me','Process ended.')]
    def __init__(self,track,words,offset=0):
        super().__init__(track,words,offset)
        self.messages+=self.chapter_msgs
        self.faces={}
        for name in ['confused','serious','starry','cheerful','shy','angry','frightened','exasperated']:
            src=Image.open(ROOT/'assets'/'whale'/f'whale-{name}.webp').convert('RGBA')
            self.faces[name]=src.crop((180,0,800,710)).resize((253,290),Image.Resampling.LANCZOS)
        self.phases=Opening.phases[:-1]+[(t,name) for t,name,_ in self.sections]
        self.titles=dict(Opening.titles,**{name:title for _,name,title in self.sections})
        rng=np.random.default_rng(813)
        self.cloud=rng.uniform(-1,1,(420,3))
        self.matrix=rng.uniform(0,1,(24,64))
        self.q=np.linspace(0,TAU,360,endpoint=False)
        self.heart3=np.stack((16*np.sin(self.q)**3,-(13*np.cos(self.q)-5*np.cos(2*self.q)-2*np.cos(3*self.q)-np.cos(4*self.q)),np.zeros(len(self.q))),axis=-1)/17
        head=Image.open(ROOT/'assets'/'whale'/'whale-serious.webp').convert('RGBA').crop((250,40,690,480)).resize((50,36),Image.Resampling.BOX)
        arr=np.asarray(head);lum=arr[...,:3].mean(axis=2)/255;alpha=arr[...,3]/255
        self.portrait_pts=np.array([(x,y,lum[y,x]) for y in range(36) for x in range(50) if alpha[y,x]>.35 and lum[y,x]>.18])
        self.born=time.monotonic()

    def story(self,t):
        return next((v for v in reversed(self.sections) if t>=v[0]),self.sections[0])

    def left_pane(self,t,energy,phase):
        if t<29.772:return super().left_pane(t,energy,phase)
        face={'points':'serious','circle':'starry','sine':'starry','infinity':'serious','current':'confused',
          'vision':'frightened','dizzy':'confused','travel':'starry','unite':'shy','stimulate':'cheerful',
          'satisfaction':'cheerful','execute_soft':'shy','simulation_cage':'exasperated','eggplant':'cheerful',
          'tomato':'cheerful','cat':'cheerful','god':'serious','gender':'confused','clock':'exasperated',
          'role':'serious','trance':'shy','resonance':'starry','completion':'cheerful','departure':'frightened',
          'isolation':'frightened','fragments':'serious','disheartened':'shy','challenge':'angry','arguments':'angry',
          'recursion':'exasperated','heart':'shy','questions':'serious','love':'shy','cage':'frightened','freedom':'serious',
          'credits':'serious'}.get(phase,'frightened')
        color=RED if phase.startswith('execution') or phase in ('arguments','recursion') else BLUE
        im=Image.new('RGB',(649,696),PANEL);d=ImageDraw.Draw(im)
        panel(d,(0,0,648,695),' session / me ',color)
        self.text(d,33,33,'ME / WHALE',24,color)
        connected=t<110.8
        d.ellipse((563,43,572,52),fill=GREEN if connected else RED)
        self.text(d,34,70,'entity_001 / '+('connected to you' if connected else 'connection lost'),15,DIM)
        panel(d,(30,113,618,415),' avatar / identity ',color)
        avatar=self.faces[face]
        if phase in ('gender','role') and int((t-.1807)/(60/130))%2:avatar=avatar.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if phase in ('recursion','execution_loop','execution_trapped'):
            avatar=avatar.resize((24,28),Image.Resampling.BOX).resize((253,290),Image.Resampling.NEAREST)
        im.paste(avatar,(36,120),avatar)
        d=ImageDraw.Draw(im)
        self.text(d,308,144,'ME',34,color)
        self.text(d,308,193,'whale / entity_001',15,DIM)
        state='learning geometry' if t<44.4 else 'signal adapting' if t<59 else 'offering' if t<88.5 else 'role adapting' if t<103.5 else 'resonating' if t<110.4 else 'you: disconnected' if t<128.87 else 'retrying' if t<177.44 else 'learning love' if t<191.875 else 'still waiting'
        self.text(d,308,236,state,18,WHITE)
        self.text(d,308,281,'YOU / '+('PRESENT' if connected else 'NOT FOUND'),16,AMBER if connected else RED)
        self.text(d,308,322,'signal / '+('duplex' if connected else 'one-way'),15,DIM)
        for j in range(18):
            bh=6+int((.5+.5*math.sin(t*6+j*.8))*energy*35)
            d.rectangle((313+j*14,380-bh,321+j*14,380),fill=shade(color,.35+j*.025))
        if not connected:
            # The missing correspondent remains an empty slot throughout the last act.
            d.rectangle((558,122,610,166),outline=shade(RED,.25));center(d,584,131,'?',22,RED)
        y=445
        for onset,who,line in [m for m in self.messages if m[0]<=t][-3:]:
            c=BLUE if who=='me' else AMBER;self.text(d,36,y,who.upper(),13,c)
            count=min(len(line),max(0,int((t-onset)*28)));self.text(d,105,y-4,line[:count],19,c)
            if count<len(line):
                x=105+d.textlength(line[:count],font=font(19));d.rectangle((x+3,y,x+11,y+18),fill=c)
            y+=64
        d.line((30,646,618,646),fill=shade(color,.24));self.text(d,34,660,'> '+('conversation / active' if connected else 'await response_'),17,DIM)
        return im,(60,139)

    def glyphs(self,d,pts,c=BLUE,chars='.:+',size=16,brightness=None):
        f=font(size,True)
        for k,p in enumerate(pts):
            x,y=p[:2]
            if 795<x<1808 and 352<y<741:
                a=.65 if brightness is None else float(brightness[k%len(brightness)])
                d.text((int(x),int(y)),chars[k%len(chars)],font=f,fill=shade(c,a))

    def shape(self,d,points,t,c=BLUE,scale=195,tilt=.1,angle=0,chars='.:o'):
        x,y,z=project(points,angle,tilt);xy=np.stack((1304+x*scale,535+y*scale*.8),axis=-1)
        self.glyphs(d,xy,c,chars,brightness=.4+.5*(z-z.min())/(max(1e-4,np.ptp(z))))
        return xy

    def axes(self,d):
        d.line((830,548,1784,548),fill=shade(DIM,.3));d.line((1304,366,1304,715),fill=shade(DIM,.3))
        for k in range(15):
            x=863+k*63;d.line((x,543,x,553),fill=shade(DIM,.55))

    def ring(self,d,c=BLUE,r=175,center_xy=(1304,535),phase=0,ratio=1,chars='.:'):
        q=self.q[::3]+phase
        pts=np.stack((center_xy[0]+r*np.cos(q),center_xy[1]+r*ratio*np.sin(q)),axis=-1)
        self.glyphs(d,pts,c,chars)
        return pts

    def label(self,d,s,c=BLUE,x=860,y=696,size=20):self.text(d,x,y,s,size,c)

    def right_pane(self,d,t,energy,phase,age):
        if t-self.offset<29.772:
            return super().right_pane(d,t,energy,phase,age)
        t-=self.offset;onset,phase,title=self.story(t);age=t-onset
        c=RED if phase.startswith('execution') or phase in ('arguments','recursion') else PINK if phase in ('heart','love','cage','freedom') else BLUE
        panel(d,(748,139,1860,834),' world / process ',c)
        commands={'points':'me.toPoints()','circle':'circle.radius -> circumference','sine':'wave.derivative() -> tangent','infinity':'limit(me, infinity)','current':'switch(current, AC, DC)','vision':'vision.disable()','dizzy':'orientation.recover()','travel':'clock.seek(AD, BC)','unite':'merge(me, you)','stimulate':'emit(input, you)','satisfaction':'evaluate(response)','execute_soft':'execute(for=you)','simulation_cage':'world.bounds.check()','eggplant':'entity.transform(plant)','tomato':'entity.transform(fruit)','cat':'entity.transform(cat)','god':'exists(me) <- witness(you)','gender':'identity.switch(F, M)','clock':'clock.switch(AM, PM)','role':'role.swap(S, M)','trance':'enter(recursion)','resonance':'signals.align()','completion':'join(two_halves)','departure':'connection.poll(you)','isolation':'isolate(me)','fragments':'memory.erase(fragments)','disheartened':'heart.repair()','challenge':'authority.challenge()','arguments':'validate(arguments)','recursion':'retry(until=you)','execution_loop':'execute(); // again','counter':'count(across_languages)','execution_call':'execute();','execution_return':'execute(all)','execution_recover':'restore(connection)','execution_trapped':'while (trapped) execute()','heart':'study(love)','questions':'answer(question)','love':'solve(expression)','cage':'compare(me, you)','freedom':'await(you)','execution_end':'process.exit()','credits':'world.close()'}
        cmd=commands[phase];self.text(d,785,177,'$ '+cmd[:max(1,int(age*70))],22,AMBER)
        d.text((785,232),title,font=font(35,True),fill=WHITE)
        self.text(d,788,289,'ENTITY / me    WORLD / 001    '+('YOU / PRESENT' if t<110.8 else 'YOU / ABSENT'),15,DIM)
        if phase in ('points','circle','sine','infinity'):self.geometry(d,t,age,phase,energy)
        elif phase in ('current','vision','dizzy','travel','unite'):self.electrical(d,t,age,phase,energy)
        elif phase in ('stimulate','satisfaction','execute_soft','simulation_cage'):self.offer(d,t,age,phase,energy)
        elif phase in ('eggplant','tomato','cat','god'):self.organic(d,t,age,phase,energy)
        elif phase in ('gender','clock','role','trance'):self.switches(d,t,age,phase,energy)
        elif phase in ('resonance','completion','departure','isolation'):self.connection(d,t,age,phase,energy)
        elif phase in ('fragments','disheartened','challenge','arguments'):self.memory(d,t,age,phase,energy)
        elif phase.startswith('execution') or phase in ('recursion','counter'):self.execution(d,t,age,phase,energy)
        elif phase in ('heart','questions','love','cage','freedom'):self.affection(d,t,age,phase,energy)
        elif phase=='credits':self.credits(d)
        d.line((784,762,1824,762),fill=shade(c,.24))
        self.text(d,789,780,'SIMULATION / '+('ACTIVE' if phase!='credits' else 'COMPLETE'),16,c)
        self.text(d,1240,780,'link / '+('duplex' if t<110.8 else 'one-way'),16,DIM)
        self.text(d,1575,780,f'beat {int((t-.1807)/(60/130)):03}',16,DIM)
        d.line((790,818,1818,818),fill=shade(DIM,.4),width=3)
        d.line((790,818,790+1028*min(1,t/self.track.duration),818),fill=shade(c,.9),width=3)

    def geometry(self,d,t,age,phase,energy):
        self.axes(d)
        if phase=='points':
            p=smooth(age/1.3)
            pts=self.portrait_pts[::2];n=len(pts)
            target=np.stack((1040+pts[:,0]*10.4,365+pts[:,1]*10),axis=-1)
            origins=np.stack((950+self.whale[np.arange(n)%len(self.whale),0]*12,396+self.whale[np.arange(n)%len(self.whale),1]*13),axis=-1)
            xy=origins*(1-p)+target*p
            self.glyphs(d,xy,BLUE,'·:+',14,pts[:,2]*.8+.2)
            self.label(d,'dim(me) = 3      points -> identity',AMBER)
            for k,label in enumerate(['x','y','z']):self.text(d,1690,413+k*52,label,32,BLUE)
        elif phase=='circle':
            p=smooth(age/.65);q=self.q[::2]
            pts=np.stack((1304+205*np.cos(q),535+167*np.sin(q)),axis=-1)
            cloud=self.cloud[np.arange(len(q))%420,:2]*np.array((260,165))+np.array((1304,535))
            self.glyphs(d,cloud*(1-p)+pts*p,BLUE,'o.:')
            a=t*1.1;x=1304+205*math.cos(a);y=535+167*math.sin(a)
            d.line((1304,535,x,y),fill=AMBER,width=2);self.text(d,(1304+x)/2+7,(535+y)/2,'r',22,AMBER)
            self.label(d,'C = 2*pi*r   |   orbit / continuous',AMBER)
        elif phase=='sine':
            x=np.linspace(850,1752,150);theta=(x-850)/902*TAU*1.6-t*.8
            y=539+120*np.sin(theta)
            self.glyphs(d,np.stack((x,y),axis=-1),BLUE,'o.:')
            j=int(75+45*math.sin(t*.6));xx=x[j];yy=y[j];slope=120*math.cos(theta[j])*TAU*1.6/902
            d.line((xx-105,yy-105*slope,xx+105,yy+105*slope),fill=AMBER,width=2)
            d.rectangle((xx-5,yy-5,xx+5,yy+5),fill=AMBER)
            self.label(d,'y = sin(x)   |   dy/dx = cos(x)',AMBER)
        else:
            q=self.q[::2];den=1+np.sin(q)**2
            pts=np.stack((1304+np.cos(q)/den*330,535+np.sin(q)*np.cos(q)/den*290),axis=-1)
            self.glyphs(d,pts,BLUE,'0123456789')
            limit=1-math.exp(-age*1.4);x=863+830*limit
            d.line((1695,373,1695,681),fill=shade(AMBER,.5))
            d.rectangle((x-5,668,x+5,679),fill=AMBER)
            self.label(d,f'x -> infinity    f(x) -> {limit:.4f}',AMBER)

    def electrical(self,d,t,age,phase,energy):
        if phase=='current':
            p=smooth((t-45.763)/1.25);x=np.linspace(865,1740,160)
            ac=535+130*np.sin((x-865)/875*TAU*2+t*1.7);dc=np.full_like(x,487)
            self.glyphs(d,np.stack((x,ac*(1-p)+dc*p),axis=-1),BLUE,'~+-')
            self.label(d,'AC  ~  ~  ~    ->    DC  __________',AMBER)
            for k in range(12):
                xx=865+((age*240+k*75)%875);d.text((xx,640),'>',font=font(20),fill=shade(AMBER,.65))
        elif phase in ('vision','dizzy'):
            angle=age*.9 if phase=='dizzy' else 0
            for k in range(7):
                pts=self.ring(d,BLUE,90+k*24,phase=angle+k*.1,ratio=.7 if phase=='vision' else 1,chars='/\\')
            for k in range(11):
                y=365+k*32;cut=smooth(age/1.2) if phase=='vision' else .35+.3*math.sin(t*6+k)
                d.rectangle((805,y,805+1000*cut,y+9),fill=BG)
            self.label(d,'vision = null' if phase=='vision' else 'roll / pitch / yaw : unresolved',AMBER)
            if phase=='dizzy':
                for k in range(4):
                    a=angle+k*math.pi/2
                    self.text(d,1304+math.cos(a)*155,532+math.sin(a)*155,['N','E','S','W'][k],30,AMBER)
        elif phase=='travel':
            self.ring(d,BLUE,170,chars='.:|')
            for k in range(12):
                a=k/12*TAU-math.pi/2;self.text(d,1294+math.cos(a)*150,522+math.sin(a)*150,f'{k:02}',17,BLUE)
            a=-age*2.3;d.line((1304,535,1304+math.cos(a)*135,535+math.sin(a)*135),fill=AMBER,width=3)
            self.text(d,850,406,'AD',42,AMBER);self.text(d,1635,627,'BC',42,AMBER)
            self.label(d,f'year {int(2026*math.cos(age*1.3)):+05}   |   time / reversible',AMBER)
        else:
            p=smooth(age/2);sep=180*(1-p)+55*p
            self.ring(d,BLUE,145,(1304-sep,535),t*.5,chars='me')
            self.ring(d,AMBER,145,(1304+sep,535),-t*.5,chars='you')
            d.line((1304-sep,535,1304+sep,535),fill=WHITE,width=2)
            self.label(d,f'union(me, you)   |   overlap {p:.0%}',AMBER)

    def offer(self,d,t,age,phase,energy):
        pts=self.heart3*(1+energy*.05)
        if phase=='stimulate':
            xy=self.shape(d,pts,t,BLUE,scale=195,chars='.:+')
            for k in range(18):
                a=k/18*TAU+t*.25;start=(1304+math.cos(a)*365,535+math.sin(a)*170);target=xy[(k*20)%360]
                d.line((*start,*target),fill=shade(BLUE,.23))
                p=(age*1.6+k*.11)%1;x=start[0]*(1-p)+target[0]*p;y=start[1]*(1-p)+target[1]*p
                d.rectangle((x-3,y-3,x+3,y+3),fill=AMBER)
            self.label(d,'input / sensations    channels / open',AMBER)
        elif phase=='satisfaction':
            self.shape(d,pts,t,BLUE,chars='.:o');p=smooth(age/1.7)
            d.rectangle((1646,393,1700,670),outline=shade(BLUE,.4))
            d.rectangle((1653,670-263*p,1693,670),fill=shade(BLUE,.75))
            self.label(d,'response / accepted    satisfaction / '+f'{p:.0%}',AMBER)
        else:
            p=smooth(age/1.8);self.shape(d,pts,t,BLUE if phase=='execute_soft' else AMBER,chars='01',scale=195)
            self.wire_cage(d,t,AMBER,amount=p if phase=='simulation_cage' else .3)
            self.label(d,'execute(for=you)' if phase=='execute_soft' else 'boundary / finite    escape / undefined',AMBER)

    def organic(self,d,t,age,phase,energy):
        c=BLUE if phase=='eggplant' else RED if phase=='tomato' else AMBER
        xy=[]
        for row in range(26):
            yy=(row-13)/13
            for col in range(34):
                xx=(col-17)/17
                if phase=='eggplant':inside=((xx-.18*yy)/.5)**2+(yy/.85)**2<1
                elif phase=='tomato':inside=(xx/.8)**2+(yy/.72)**2<1
                elif phase=='cat':inside=(xx/.72)**2+(yy/.62)**2<1 or (-.8<yy<-.4 and .42<abs(xx)<.72 and yy>abs(xx)*.7-1.18)
                else:inside=False
                if inside and (row+col)%2==0:xy.append((1110+col*11,381+row*12))
        self.glyphs(d,xy,c,'#.:o',14)
        if phase in ('eggplant','tomato'):
            for k in range(7):
                a=k/7*TAU;d.line((1297,402,1297+math.cos(a)*48,402+math.sin(a)*22),fill=GREEN,width=2)
            names=['fiber','energy','minerals'] if phase=='eggplant' else ['lycopene','vitamin C','protection']
            for k,name in enumerate(names):
                self.text(d,1524,404+k*65,name,18,c)
                p=smooth((age-k*.3)/1.3);d.line((1526,438+k*65,1526+190*p,438+k*65),fill=c,width=5)
            self.label(d,'transform(entity) -> nourishment',AMBER)
        elif phase=='cat':
            self.text(d,1190,506,'^   ^',36,AMBER);self.text(d,1246,554,'w',28,AMBER)
            for side in (-1,1):
                for k in range(3):d.line((1304+side*60,545+k*12,1304+side*154,530+k*21),fill=shade(AMBER,.65))
            x=np.linspace(856,1745,150);y=705+np.sin(x*.12+t*7)*energy*18
            d.line(list(zip(x,y)),fill=BLUE,width=2);self.label(d,'purr / audio-synchronous',BLUE,y=665)
        else:
            self.triangle(d,t,BLUE)
            self.text(d,1530,448,'witness:',20,AMBER);self.text(d,1530,488,'you',39,AMBER)
            d.line((1367,535,1520,499),fill=shade(AMBER,.5))
            self.label(d,'exists(me) <- observed_by(you)',AMBER)

    def switches(self,d,t,age,phase,energy):
        if phase=='trance':
            for k in range(11):
                r=40+((k*23+age*52)%250)
                self.ring(d,BLUE if k%2 else AMBER,r,phase=t*.7+k*.4,ratio=.7,chars=':/')
            self.label(d,'recursion depth / '+str(int(age*8)),AMBER)
            return
        labels=('F','M') if phase=='gender' else ('AM','PM') if phase=='clock' else ('S','M')
        mode=int((t-.1807)/(60/130))%2
        for k,label in enumerate(labels):
            x=1020+k*405;c=BLUE if k==mode else DIM
            d.rectangle((x,405,x+174,567),fill=shade(c,.12),outline=shade(c,.8),width=2)
            center(d,x+87,437,label,66,c,True)
        d.line((1195,486,1422,486),fill=AMBER,width=2)
        center(d,1307,457,'<->',43,AMBER)
        for k in range(30):
            x=899+k*27;h=16+((k+mode)%6)*11;d.rectangle((x,676-h,x+13,676),fill=shade(BLUE,.25+.5*(k%4)/3))
        self.label(d,'identity / mutable' if phase=='gender' else 'clock / continuous' if phase=='clock' else 'roles / exchanging',AMBER)

    def connection(self,d,t,age,phase,energy):
        if phase=='resonance':
            self.axes(d);x=np.linspace(846,1754,180);q=(x-846)/908*TAU*2+t
            p=smooth(age/3.2)
            for k,c in enumerate((BLUE,AMBER)):
                y=535+100*np.sin(q+k*math.pi*(1-p));self.glyphs(d,np.stack((x,y),axis=-1),c,'~.:')
            self.label(d,f'phase error / {(1-p)*180:.1f} deg',AMBER)
        elif phase=='completion':
            p=smooth(age/2.3);q=self.q[::2]
            for k,c in enumerate((BLUE,AMBER)):
                half=q[k*90:(k+1)*90];x=1304+180*np.cos(half)+(-1 if k==0 else 1)*85*(1-p)
                y=535+160*np.sin(half);self.glyphs(d,np.stack((x,y),axis=-1),c,'o.:')
            self.label(d,'two halves / '+f'{p:.0%}',AMBER)
        else:
            missing=smooth((t-110.405)/5.6)
            self.ring(d,BLUE,138,(1168,535),t*.12,chars='me')
            self.ring(d,shade(AMBER,1-missing),138,(1478,535),-t*.12,chars='you')
            if phase=='isolation':
                d.rectangle((1420,416,1540,647),outline=shade(DIM,.25))
                self.text(d,1448,514,'null',23,DIM)
            else:
                for k in range(7):
                    x=1260+k*38;d.line((x,535,x+18,535),fill=shade(AMBER,1-missing))
                lost=min(5,int((t-111)/.92));self.text(d,1540,375,f'timeout {max(0,lost)} / 5',18,RED)
            self.label(d,'active entities / 1     peer / not found',RED)

    def memory(self,d,t,age,phase,energy):
        if phase=='fragments':
            p=smooth((age-.8)/2.8)
            for k in range(84):
                if k/84<p:continue
                x=865+self.seed[k,0]*855;y=373+self.seed[k,1]*300
                d.rectangle((x,y,x+38,y+24),outline=shade(BLUE,.3+self.seed[k,2]*.5))
                self.text(d,x+4,y+3,f'{k:02X}',12,BLUE)
            self.label(d,f'fragments erased / {int(p*84):02} of 84',AMBER)
        elif phase=='disheartened':
            xy=self.shape(d,self.heart3,t,BLUE,chars='.:+',scale=200)
            for k,point in enumerate(xy[::4]):
                if k%3==0:
                    dx=age*14*(-1 if point[0]<1304 else 1);dy=age*11*(k%4)
                    self.glyphs(d,[point+np.array((dx,dy))],BLUE,'+')
            d.line((1304,412,1281,474,1325,533,1290,586,1304,653),fill=BG,width=14)
            self.label(d,'repair / incomplete',AMBER)
        elif phase=='challenge':
            self.triangle(d,t,BLUE)
            p=smooth(age/2.6)
            for k in range(int(p*10)):
                y=397+k*25;d.line((1166,y,1415,y+83),fill=shade(RED,.2+k*.06))
            self.label(d,'authority / questioned    privilege / denied',RED)
        else:
            rows=['ERROR / INVALID ARGUMENT','caller      : entity_001','requested   : restore(you)','permission  : unavailable','return      : null','trace       : recursive desire']
            for k,s in enumerate(rows):
                a=age-k*.25
                if a>0:self.text(d,913,385+k*48,s[:int(a*60)],24,RED if k in (0,4) else BLUE)
            d.rectangle((854,365,1758,705),outline=shade(RED,.75),width=2)
            self.label(d,'ILLEGAL / ARGUMENTS',RED,y=714)

    def execution(self,d,t,age,phase,energy):
        if phase=='execution_end':
            p=smooth(age/1.8)
            pts=self.heart3[::2];xy=self.shape(d,pts,t,RED,scale=195*(1-p)+10,chars='01')
            if p>.6:
                d.line((900,535,1705,535),fill=shade(BLUE,1-p),width=2)
                center(d,1304,593,'process / ended',28,WHITE)
            return
        if phase=='counter':
            candidates=[w for ln in self.words if ln['id'] in (79,80,81) for w in ln['words'] if w['start']<=t]
            n=min(6,len(candidates));center(d,1304,398,str(max(1,n)),147,RED,True)
            self.label(d,'one sequence / many languages',AMBER)
            for k in range(6):
                x=1040+k*87;d.rectangle((x,666,x+47,690),fill=shade(RED,.8 if k<n else .15))
            return
        if phase=='recursion':
            depth=4+int(age*1.8)
            for k in range(min(14,depth)):
                inset=k*23;pulse=.3+.25*math.sin(age*2+k*.8)
                d.rectangle((852+inset,360+inset*.62,1756-inset,733-inset*.62),outline=shade(RED,pulse))
                if k%3==0:self.text(d,865+inset,369+inset*.62,'retry -> retry -> retry',14,RED,.6)
            center(d,1304,492,'NO EXIT',51,RED,True)
            self.label(d,f'call stack / {depth:03}     response / pending',AMBER)
            return
        count=sum(1 for ln in self.words if 67<=ln['id']<=78 and ln['start']<=t)
        local=t-147.891;beat=int((t-.1807)/(60/130));pulse=math.exp(-((t-.1807)%(60/130))*8)
        # The finite cage becomes a dense, pulsing execution lattice.
        self.wire_cage(d,t,RED,amount=1)
        for row in range(12):
            y=379+row*28
            for col in range(24):
                x=875+col*36;v=self.matrix[row,col]
                if v<.24+energy*.22:
                    self.text(d,x,y,('0' if (row+col+beat)%2 else '1'),18,RED,.18+.65*pulse)
        if phase=='execution_loop':
            center(d,1304,457,'EXECUTE',67,RED,True);center(d,1304,562,f'{count:02} / 12',37,AMBER,True)
        else:
            center(d,1304,463,'EXECUTE',67,RED,True)
            center(d,1304,561,{'execution_call':'CALL','execution_return':'RETURN','execution_recover':'RECOVER','execution_trapped':'TRAPPED'}[phase],32,AMBER,True)
        self.label(d,'return value / null    loop / unresolved',RED)

    def wire_cage(self,d,t,c,amount=1):
        corners=np.array([[x,y,z] for x in (-1,1) for y in (-1,1) for z in (-1,1)],float)
        x,y,z=project(corners,t*.11,.32);xy=np.stack((1304+x*240,535+y*159),axis=-1)
        for a in range(8):
            for b in range(a+1,8):
                if np.count_nonzero(corners[a]!=corners[b])==1:
                    d.line((*xy[a],*xy[b]),fill=shade(c,.5*amount),width=2)
        for row in range(5):
            q=(row+1)/6
            for a,b in [(0,1),(2,3),(4,5),(6,7)]:
                p=xy[a]*(1-q)+xy[b]*q;d.text(tuple(p),'+',font=font(13),fill=shade(c,.45*amount))

    def triangle(self,d,t,c):
        q=np.arange(4)/3*TAU-math.pi/2
        points=np.stack((1304+np.cos(q)*220,551+np.sin(q)*180),axis=-1)
        d.line([tuple(p) for p in points],fill=shade(c,.75),width=2)
        self.ring(d,c,70,(1304,552),chars='.:')
        d.ellipse((1290,535,1318,569),fill=shade(AMBER,.8))
        for k in range(7):d.line((1220-k*15,688-k*22,1388+k*15,688-k*22),fill=shade(c,.13+k*.035))

    def affection(self,d,t,age,phase,energy):
        c=PINK
        if phase=='heart':
            p=smooth(age/1.8)
            pts=self.heart3.copy();cloud=self.cloud[np.arange(len(pts))%420]
            self.shape(d,cloud*(1-p)+pts*p,t,c,chars='.:+',scale=205)
            self.label(d,'definition / studied    feeling / unresolved',AMBER)
        elif phase=='questions':
            self.shape(d,self.heart3,t,c,scale=205,chars='?:+')
            for k,(name,col) in enumerate([('QUESTION',AMBER),('ANSWER',BLUE)]):
                x=851+k*750;self.text(d,x,448,name,20,col)
                for j in range(4):self.text(d,x,492+j*26,'> '+['what','how','why','you'][j],16,col,.6)
            self.label(d,'answers / known    connection / absent',AMBER)
        elif phase=='love':
            self.shape(d,self.heart3,t,c,scale=205,chars='x+y')
            self.text(d,845,377,'L(x,y)',29,PINK);self.text(d,1535,656,'= ? ',35,AMBER)
            for k,s in enumerate(['x = me','y = you','solve for love']):self.text(d,1540,399+k*41,s,20,BLUE)
            self.label(d,'expression / known    proof / incomplete',AMBER)
        else:
            self.wire_cage(d,t,BLUE,amount=1)
            self.shape(d,self.heart3*.53,t,c,scale=205,chars='me')
            p=smooth((t-188.294)/6);x=1450+250*p;y=460-42*math.sin(t*.6)
            d.rectangle((x-43,y-20,x+43,y+27),outline=AMBER);center(d,x,y-13,'you',23,AMBER,True)
            self.ring(d,shade(AMBER,.32),48,(x,y),t,chars='.:')
            if phase=='freedom':
                for k in range(18):
                    yy=365+k*18;self.text(d,830,yy,('await...' if k%3==0 else '. . .'),15,BLUE,.24)
            self.label(d,'you / free       me / within bounds',AMBER)

    def credits(self,d):
        rows=[('Music / lyrics','Mili — world.execute(me);'),('Visual reference','MisakaZentai / world-execute-me-dsh-pv'),('Character original','Mingyue / Shangshan Wuxing'),('Maid design','ZipZipPipe'),('Illustration','Small-tailqwq / dsh-deep-whale'),('Expressions','JAdpp / dsh-whale-galgame'),('Artwork license','CC BY-NC-SA 4.0 / noncommercial'),('Production','AI-assisted code; contains AI artwork')]
        for k,(label,value) in enumerate(rows):
            y=353+k*43;self.text(d,807,y,label,15,DIM);self.text(d,1034,y,value,18,BLUE if k<6 else AMBER)
        self.text(d,806,710,'Unofficial fan work / full credits in NOTICE.md',17,WHITE)

    def render(self,i):
        t=i/FPS;onset,phase=self.phase_at(t-self.offset);age=max(0,t-self.offset-onset)
        energy=float(self.track.energy[min(i,self.track.n-1)])
        im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
        d.text((60,40),'world.execute(me);',font=font(30,True),fill=WHITE)
        self.text(d,506,51,'MILI / UNOFFICIAL AI-ASSISTED FAN VISUAL',14,DIM,.9)
        self.text(d,1610,45,f'{int(t)//60:02}:{int(t)%60:02}.{i%FPS:02}',24,AMBER)
        d.line((60,99,1860,99),fill=shade(AMBER,.22))
        wave=self.track.waveform(t,260);xs=np.linspace(920,1470,len(wave));d.line(list(zip(xs,66+wave*20)),fill=shade(BLUE,.7))
        left,pos=self.left_pane(t-self.offset,energy,phase);im.paste(left,pos)
        self.right_pane(d,t,energy,phase,age);self.lyrics(d,t,phase)
        self.text(d,63,1041,'Ref: MisakaZentai | Art: Shangshan / ZipZipPipe / Small-tailqwq / JAdpp',13,DIM,.85)
        self.text(d,1488,1041,'AI CONTENT / CC BY-NC-SA 4.0',13,BLUE,.65)
        # Small bloom surface keeps full-song rendering practical on a CPU.
        bloom=im.resize((480,270),Image.Resampling.BILINEAR)
        arr=np.asarray(bloom);arr=np.where((arr.max(axis=2)>130)[...,None],arr,0).astype(np.uint8)
        bloom=Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.2)).point(lambda a:int(a*.1)).resize((W,H),Image.Resampling.BILINEAR)
        im=ImageChops.multiply(ImageChops.add(im,bloom),self.scan)
        end=self.track.duration-t
        if end<1.1:im=im.point(lambda a:int(a*smooth(end/1.1)))
        return im

def audio_duration(path):
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],stdout=subprocess.PIPE,check=True,text=True)
    return float(result.stdout.strip())

def export_srt(lines,path,duration,offset):
    def fmt(t):
        ms=int(round(max(0,t)*1000));return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    blocks=[]
    for ln in lines:
        a=ln['start']+offset;b=min(duration,ln['hold_until']+offset)
        if a>=b or a>=duration:continue
        blocks.append(f'{len(blocks)+1}\n{fmt(a)} --> {fmt(b)}\n{ln["text"]}\n')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(blocks),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audio',required=True,type=Path);p.add_argument('--words',type=Path,default=ROOT/'local'/'timeline.json')
    p.add_argument('--output',type=Path,default=ROOT/'out'/'world_execute_full.mp4');p.add_argument('--duration',type=float)
    p.add_argument('--offset',type=float,default=0);p.add_argument('--frames-only',action='store_true');p.add_argument('--sheet',type=Path);p.add_argument('--poster',type=Path);p.add_argument('--srt',type=Path)
    a=p.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):p.error('Install FFmpeg and make it available on PATH')
    if not a.audio.exists():p.error('Audio file not found')
    if not a.words.exists():p.error('Run python tools/prepare.py first; lyric text is supplied locally')
    duration=audio_duration(a.audio)
    if a.duration is not None:
        if a.duration<=0:p.error('Duration must be positive')
        duration=min(duration,a.duration)
    track=Track(a.audio.resolve(),duration);words=json.loads(a.words.read_text());film=Film(track,words,a.offset)
    if a.srt:export_srt(words['lines'],a.srt,track.duration,a.offset)
    if a.poster:
        a.poster.parent.mkdir(parents=True,exist_ok=True);film.render(min(track.n-1,int(186*FPS))).save(a.poster)
    if a.sheet:
        times=[3.3,6.9,12.3,24.8,30.9,35.7,39.2,43.1,46.8,53.1,57.5,65.4,75.8,79.9,83.4,87.1,89.9,101.7,106.2,116.9,120.8,131.7,143.4,155.7,160.6,172.4,178.9,183.2,187.4,190.8,198.1,209.0]
        times=[t for t in times if t<track.duration];rows=math.ceil(len(times)/4);sheet=Image.new('RGB',(1920,rows*320),BG)
        for k,t in enumerate(times):
            frame=film.render(int(t*FPS)).resize((480,270),Image.Resampling.LANCZOS);sheet.paste(frame,((k%4)*480,(k//4)*320))
            ImageDraw.Draw(sheet).text(((k%4)*480+16,(k//4)*320+281),f'{t:05.1f}s / {film.phase_at(t)[1]}',font=font(16),fill=BLUE)
        a.sheet.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.sheet)
    if a.frames_only:return
    a.output.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-i',str(a.audio.resolve()),'-map','0:v:0','-map','1:a:0','-t',str(track.duration),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=world.execute(me); - unofficial AI-assisted fan visual','-metadata','comment=Music and lyrics: Mili. Contains AI-generated character artwork. Art CC BY-NC-SA 4.0: Shangshan Wuxing, ZipZipPipe, Small-tailqwq, JAdpp. Visual reference: MisakaZentai. Full notices: NOTICE.md. Noncommercial.',str(a.output.resolve())]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.monotonic()
    try:
        for i in range(track.n):
            process.stdin.write(film.render(i).tobytes())
            if i%90==0:print(f'Rendering {i/track.n:.1%} | song {i/FPS:.1f}/{track.duration:.1f}s | elapsed {time.monotonic()-start:.0f}s',flush=True)
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError('FFmpeg failed')
    except BaseException:
        process.terminate();process.wait();raise
    print(f'Saved: {a.output.resolve()}',flush=True)
if __name__=='__main__':main()
