#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original abstract geometry film; retained whale chat, local song and lyrics."""
import argparse, json, math, shutil, subprocess, time
from pathlib import Path
from PIL import Image, ImageDraw
from audio import Track
from devotion import Film, FPS, W, H, PAPER, INK, font
ROOT=Path(__file__).resolve().parent

def audio_duration(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())
def export_srt(lines,path,duration,offset,start=0):
    def fmt(t):
        ms=round(max(0,t)*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    blocks=[]
    for ln in lines:
        a=max(0,ln['start']+offset-start);b=min(duration,ln['hold_until']+offset-start)
        if b<=a or a>=duration:continue
        blocks.append(f'{len(blocks)+1}\n{fmt(a)} --> {fmt(b)}\n{ln["text"]}\n')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(blocks),encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audio',required=True,type=Path);ap.add_argument('--words',type=Path,default=ROOT/'local/timeline.json')
    ap.add_argument('--output',type=Path,default=ROOT/'out/world_execute_devotion.mp4');ap.add_argument('--duration',type=float)
    ap.add_argument('--start',type=float,default=0,help='preview an excerpt while retaining global lyric/scene time')
    ap.add_argument('--offset',type=float,default=0);ap.add_argument('--frames-only',action='store_true')
    ap.add_argument('--sheet',type=Path);ap.add_argument('--poster',type=Path);ap.add_argument('--srt',type=Path)
    a=ap.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):ap.error('FFmpeg and ffprobe must be on PATH')
    if not a.audio.exists() or not a.words.exists():ap.error('Provide audio and run tools/prepare.py to build the local lyric timeline')
    full=audio_duration(a.audio)
    if a.start<0 or a.start>=full:ap.error('Start must be within the audio')
    duration=full-a.start if a.duration is None else min(a.duration,full-a.start)
    if duration<=0:ap.error('Duration must be positive')
    track=Track(a.audio.resolve(),full);data=json.loads(a.words.read_text());film=Film(track,data,a.offset)
    if a.srt:export_srt(data['lines'],a.srt,duration,a.offset,a.start)
    if a.poster:
        a.poster.parent.mkdir(parents=True,exist_ok=True);film.render(int(117.1*FPS)).save(a.poster)
    if a.sheet:
        times=[.8,3.3,6.9,12.7,19.0,27.2,31.8,35.9,39.2,43.0,46.8,49.1,53.5,57.8,61.7,69.0,75.8,79.6,83.4,87.2,90.0,94.5,98.0,106.3,109.5,113.8,117.2,121.1,132.0,142.4,150.3,158.2,160.7,171.5,179.7,186.7,193.0,200.5,206.4,209.2]
        rows=math.ceil(len(times)/4);sheet=Image.new('RGB',(1920,rows*308),PAPER)
        for k,t in enumerate(times):
            fr=film.render(min(track.n-1,int(t*FPS))).resize((480,270),Image.Resampling.LANCZOS)
            sheet.paste(fr,((k%4)*480,(k//4)*308))
            ImageDraw.Draw(sheet).text(((k%4)*480+12,(k//4)*308+279),f'{t:05.1f}s / {film.phase_at(t)[1]}',font=font(16),fill=INK)
        a.sheet.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.sheet)
    if a.frames_only:return
    a.output.parent.mkdir(parents=True,exist_ok=True)
    count=math.ceil(duration*FPS);first=round(a.start*FPS)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0','-ss',str(a.start),'-i',str(a.audio.resolve()),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=world.execute(me); - A Geometry of Devotion','-metadata','comment=Original geometric choreography, AI-assisted code. Retained whale artwork contains AI art, CC BY-NC-SA 4.0: Shangshan Wuxing, ZipZipPipe, Small-tailqwq, JAdpp. Song and lyrics: Mili. Timing/helper: MisakaZentai, MIT. Unofficial noncommercial fan work. Full credits: NOTICE.md.',str(a.output.resolve())]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);begin=time.monotonic()
    try:
        for k in range(count):
            proc.stdin.write(film.render(min(track.n-1,first+k)).tobytes())
            if k%150==0:print(f'Rendering {k/count:.1%} | song {(first+k)/FPS:.1f}s | elapsed {time.monotonic()-begin:.0f}s',flush=True)
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('FFmpeg failed')
    except BaseException:
        proc.terminate();proc.wait();raise
    print(f'Saved: {a.output.resolve()}',flush=True)
if __name__=='__main__':main()
