# SPDX-License-Identifier: MIT
"""Reconstruct a local lyric timeline from a supplied LRC and text-free timing."""
import argparse, json, sys
from pathlib import Path
from reference_lyrics import read_lrc, match, apply_patch, sha
ROOT=Path(__file__).resolve().parents[1]

def prepare(lrc, output):
    data=ROOT/'data'/'timing'
    lines=json.loads((data/'lyrics_synced_notext.json').read_text())['lines']
    metadata=json.loads((data/'word_timeline_notext.json').read_text())
    found,problems,_,_=match(lines,read_lrc(lrc))
    if problems:raise ValueError('LRC does not match reference timing:\n'+'\n'.join(problems))
    patches={p['line_id']:p['ops'] for p in metadata['patches']}
    by_id={}
    for item in metadata['lines']:
        i=item['id'];text=found[i]
        if i in patches:text=apply_patch(text,patches[i])
        if sha(text)!=item['sha256']:raise ValueError(f'Word alignment mismatch at line {i}')
        by_id[i]=(text,item['spans'])
    skeleton=metadata['skeleton'];result=[]
    for row in skeleton['lines']:
        i=row['id'];text,spans=by_id[i]
        words=[]
        for w in skeleton['words']:
            if w['line_id']!=i:continue
            a,b=spans[w['word_index']];word=text[a:b]
            # User-supplied wording corrections; timestamps remain the same.
            if i==9 and word.lower()=='point':word='points'
            if i==26 and word.lower()=='simulations':word='STIMULATIONS'
            words.append({'text':word,'start':w['start'],'end':w['end']})
        result.append({'id':i,'start':row['start'],'end':row['end'],'text':' '.join(w['text'] for w in words),'words':words})
    for k,row in enumerate(result):
        next_start=result[k+1]['start'] if k+1<len(result) else row['end']+.7
        row['hold_until']=min(next_start,row['end']+.65)
    obj={'timing_source':'MisakaZentai/world-execute-me-dsh-pv','lyrics_source':'Locally supplied LRC; never included in the repository','lines':result}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(f'Prepared {len(result)} lines / {sum(len(r["words"]) for r in result)} words -> {output.name}')
    return obj

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lrc',type=Path,default=ROOT/'input'/'lyrics.lrc');p.add_argument('--output',type=Path,default=ROOT/'local'/'timeline.json')
    a=p.parse_args()
    if not a.lrc.exists():p.error('Supply an LRC or run python tools/reference_lyrics.py fetch first')
    try:prepare(a.lrc,a.output)
    except ValueError as e:sys.exit(str(e))
if __name__=='__main__':main()
