# SPDX-License-Identifier: MIT
"""Check the Git index for local copyrighted inputs before publishing."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.mp4','.mov','.m4a','.mp3','.wav','.flac','.aac','.lrc','.srt'}

def check():
    proc=subprocess.run(['git','ls-files','-z'],cwd=ROOT,stdout=subprocess.PIPE,check=True)
    files=[Path(p.decode('utf-8')) for p in proc.stdout.split(b'\0') if p]
    errors=[]
    for p in files:
        if p.suffix.lower() in FORBIDDEN or p.parts[0] in ('local','out','film') or (p.parts[0]=='input' and p.name!='README.md'):
            errors.append(f'Local music, lyrics or rendered output is tracked: {p}')
        if p.name=='word_timeline_notext.json':
            data=json.loads((ROOT/p).read_text())['skeleton']
            if any(row.get('text') is not None for row in data['lines']+data['words']):
                errors.append(f'Timing metadata contains lyric text: {p}')
    required={'LICENSE','NOTICE.md','LICENSES/reference-MIT.txt','LICENSES/CC-BY-NC-SA-4.0.txt','LICENSES/OFL_spacemono.txt'}
    missing=required-{p.as_posix() for p in files}
    errors.extend(f'Missing published license/notice: {p}' for p in sorted(missing))
    if errors:sys.exit('\n'.join(errors))
    print(f'Public-file check passed: {len(files)} tracked files; no music or lyric text files.')
if __name__=='__main__':check()
