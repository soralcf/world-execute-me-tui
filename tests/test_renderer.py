# SPDX-License-Identifier: MIT
"""Rendering regressions without distributing the song or any lyric text."""
import sys, unittest, tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from render import Film, export_srt
from terminal import FPS

class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.track=SimpleNamespace(duration=212.288,n=6369,energy=np.full(6369,.6),waveform=lambda t,n:np.zeros(n))
        cls.film=Film(cls.track,{'lines':[]})
    def test_every_scene_and_handoff_renders(self):
        starts=self.film.phases
        for k,(onset,name) in enumerate(starts):
            end=starts[k+1][0] if k+1<len(starts) else self.track.duration
            for t in (onset+.01,(onset+end)/2,end-.04):
                if t<0:continue
                with self.subTest(scene=name,time=t):
                    image=self.film.render(min(self.track.n-1,int(t*FPS)))
                    self.assertEqual(image.size,(1920,1080));self.assertEqual(image.mode,'RGB')
                    if t<self.track.duration-1.1:
                        self.assertGreater(np.asarray(image)[140:820,750:1850].max(),100)
    def test_final_frame_fades_to_black(self):
        image=self.film.render(self.track.n-1)
        self.assertLess(np.asarray(image).max(),5)
    def test_srt_clips_to_selected_audio(self):
        rows=[{'start':1,'hold_until':3,'text':'alpha beta'},{'start':4,'hold_until':6,'text':'gamma'}]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'captions.srt';export_srt(rows,path,2,0)
            text=path.read_text();self.assertIn('00:00:01,000 --> 00:00:02,000',text);self.assertNotIn('gamma',text)

if __name__=='__main__':unittest.main()
