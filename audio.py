# SPDX-License-Identifier: MIT
"""Local FFmpeg audio decoding and frame-aligned spectral analysis."""
import subprocess, math
import numpy as np
FPS=30

class Track:
    def __init__(self,filename,duration,start=0):
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',str(filename),
             '-t',str(duration),'-vn','-ac','2','-ar','44100','-f','s16le','pipe:1']
        data=subprocess.run(cmd,stdout=subprocess.PIPE,check=True).stdout
        stereo=np.frombuffer(data,dtype='<i2').reshape(-1,2).astype(np.float32)/32768
        self.samples=stereo.mean(axis=1)
        self.duration=min(duration,len(self.samples)/44100)
        if self.duration<=0:
            raise ValueError('Audio contains no samples in the selected interval')
        self.n=math.ceil(self.duration*FPS)
        bins=np.geomspace(2,1024,65).astype(int)
        for k in range(1,len(bins)):
            bins[k]=max(bins[k],bins[k-1]+1)
        window=np.hanning(2048)
        padded=np.pad(self.samples,(1024,3072))
        spec=[];energy=[]
        for i in range(self.n):
            p=int(i*44100/FPS)
            segment=padded[p:p+2048]
            fft=np.abs(np.fft.rfft(segment*window))
            spec.append([np.sqrt(np.mean(fft[a:b]**2)) for a,b in zip(bins[:-1],bins[1:])])
            energy.append(float(np.sqrt(np.mean(segment**2))))
        spec=np.asarray(spec)
        self.spec=np.clip(np.log1p(spec)/np.log1p(max(1e-5,np.percentile(spec,98))),0,1.2)
        energy=np.asarray(energy)
        self.energy=np.clip(energy/max(1e-5,np.percentile(energy,95)),0,1.2)
        for i in range(1,self.n):
            self.spec[i]=self.spec[i]*.48+self.spec[i-1]*.52

    def waveform(self,t,count=300):
        k=int(t*44100)
        segment=self.samples[k:k+2048]
        if not len(segment):
            return np.zeros(count)
        return np.interp(np.linspace(0,len(segment)-1,count),np.arange(len(segment)),segment)
