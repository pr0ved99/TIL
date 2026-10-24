"""Decode every output frame, inspect streams, and export visual review samples."""
from pathlib import Path
import json, re, subprocess
from PIL import Image, ImageDraw, ImageFont
from render_demo import BASE, FFMPEG, OUTPUT, sha256

manifest=json.loads((BASE/'edit_manifest.json').read_text(encoding='utf8'))
probe=subprocess.run([str(FFMPEG),'-hide_banner','-i',str(OUTPUT)],capture_output=True,text=True,encoding='utf8',errors='replace')
(BASE/'output_streams.txt').write_text(probe.stderr,encoding='utf8')
streams=[line.strip() for line in probe.stderr.splitlines() if re.match(r'\s*Stream #0:',line)]
assert len(streams)==1 and 'Video: h264' in streams[0] and '1920x1080' in streams[0] and '24 fps' in streams[0], streams
decoded=subprocess.run([str(FFMPEG),'-hide_banner','-loglevel','error','-nostdin','-nostats',
    '-progress','pipe:1','-i',str(OUTPUT),'-map','0','-f','null','-'],capture_output=True,text=True,encoding='utf8',errors='replace')
assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
frames=[int(x) for x in re.findall(r'^frame=(\d+)$',decoded.stdout,re.M)]
assert frames[-1]==1560, frames
assert 'progress=end' in decoded.stdout
(BASE/'decode_progress.txt').write_text(decoded.stdout,encoding='utf8')
originals={s['path']:sha256(BASE/s['path'])==s['sha256'] for s in manifest['sources']}
assert all(originals.values())
prior=json.loads((BASE.parent/'video_manifest.json').read_text(encoding='utf8'))
for v in prior['videos']:
    current=BASE.parent/v.get('current_file',v['file'])
    assert sha256(current)==v['sha256'],str(current)
times=[0,3,9.25,12,17,21,23,27,29,33,36,40,45,48,50,54,57,61.5,64.8]
samples=BASE/'output_samples'; samples.mkdir(exist_ok=True)
for t in times:
    subprocess.run([str(FFMPEG),'-hide_banner','-loglevel','error','-nostdin','-ss',str(t),'-i',str(OUTPUT),
        '-frames:v','1','-update','1','-q:v','2','-y',str(samples/f'{t:06.2f}.jpg')],check=True)
cols=3; tilew=640; tileh=386
sheet=Image.new('RGB',(cols*tilew,((len(times)+cols-1)//cols)*tileh),'#eef3f8')
d=ImageDraw.Draw(sheet); font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
for i,t in enumerate(times):
    x=(i%cols)*tilew;y=(i//cols)*tileh
    sheet.paste(Image.open(samples/f'{t:06.2f}.jpg').resize((640,360)),(x,y+26))
    d.text((x+6,y+3),f'Output {t:.2f}s / Screen source {t+6:.2f}s',font=font,fill='#183149')
sheet.save(BASE/'output_contact_sheet.jpg',quality=92)
validation={'output_sha256':sha256(OUTPUT),'decoded_frames':frames[-1], 'expected_frames':1560,
    'decode_exit_code':decoded.returncode,'decode_errors':decoded.stderr,'streams':streams,
    'original_hashes_unchanged':originals,'original_hashes_match_prior_review':True,
    'sample_output_seconds':times,'human_visual_review':'pending; see output_contact_sheet.jpg',
    'scope':'Full codec decode plus selected image review; not physical acceptance or audio review.'}
(BASE/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in validation.items() if k not in ['sample_output_seconds']},ensure_ascii=False,indent=2))
