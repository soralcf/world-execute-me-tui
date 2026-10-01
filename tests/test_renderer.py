# SPDX-License-Identifier: MIT
"""Pure-time rendering and local subtitle regressions; no song/lyric fixture."""
import sys, unittest, tempfile, math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from render import Film, export_srt
from devotion import FPS

class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.track=SimpleNamespace(duration=212.288,n=6369,energy=np.full(6369,.6))
        cls.film=Film(cls.track,{'lines':[]})
    def test_every_scene_and_handoff_renders(self):
        phases=self.film.phases
        for k,(onset,name) in enumerate(phases):
            end=phases[k+1][0] if k+1<len(phases) else self.track.duration
            for t in (onset+.01,(onset+end)/2,end-.04):
                with self.subTest(scene=name,time=t):
                    im=self.film.render(min(self.track.n-1,max(math.ceil(onset*FPS),int(t*FPS))))
                    self.assertEqual(im.size,(1920,1080));self.assertEqual(im.mode,'RGB')
                    if t<self.track.duration-.9 and name!='last_switch':
                        # A visible subject must remain, rather than merely paper.
                        self.assertGreater((np.asarray(im)[150:850,500:1850,0]<145).sum(),200)
    def test_seeking_is_deterministic(self):
        a=np.asarray(self.film.render(4900));self.film.render(2800);b=np.asarray(self.film.render(4900))
        self.assertTrue(np.array_equal(a,b))
    def test_final_frame_fades_to_black(self):
        self.assertLess(np.asarray(self.film.render(self.track.n-1)).max(),5)
    def test_srt_clips_to_selected_audio(self):
        rows=[{'start':1,'hold_until':3,'text':'alpha beta'},{'start':4,'hold_until':6,'text':'gamma'}]
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'captions.srt';export_srt(rows,p,2,0)
            self.assertIn('00:00:01,000 --> 00:00:02,000',p.read_text());self.assertNotIn('gamma',p.read_text())
    def test_excerpt_subtitles_use_local_time(self):
        rows=[{'start':8,'hold_until':12,'text':'alpha beta'}]
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'captions.srt';export_srt(rows,p,2,0,start=10)
            self.assertIn('00:00:00,000 --> 00:00:02,000',p.read_text())
if __name__=='__main__':unittest.main()
