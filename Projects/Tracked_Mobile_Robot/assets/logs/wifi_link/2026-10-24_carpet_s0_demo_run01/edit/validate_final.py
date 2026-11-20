"""Decode all frames, inspect stream metadata, extract critical-stage previews."""
import json, subprocess, re, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from render_final import B, FF, OUT, sha, CAM, SCR, OLD

def main():
    proc=subprocess.run([FF,'-hide_banner','-v','error','-i',str(OUT),'-map','0:v:0','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True)
    (B/'decode.log').write_text(proc.stdout+proc.stderr,encoding='utf8')
    assert proc.returncode==0 and not proc.stderr.strip(), proc.stderr
    frames=int(re.findall(r'^frame=(\d+)',proc.stdout,re.M)[-1]); assert frames==4470,frames
    meta=subprocess.run([FF,'-hide_banner','-i',str(OUT)],capture_output=True,text=True).stderr
    (B/'streams.txt').write_text(meta,encoding='utf8')
    assert '1920x1080' in meta and '30 fps' in meta and 'Audio:' not in meta
    assert 'Duration: 00:02:29.00' in meta
    manifest=json.loads((B/'edit_manifest.json').read_text(encoding='utf8'))
    for item in manifest['sources']: assert sha(B/item['path'])==item['sha256']
    assert sha(CAM)=='c20c0c02d323779e844d3fe3abdcf2250156ebf690bd4d3cfc757553e7d90702'
    assert sha(SCR)=='2a125c4e221c01ac2bca0ee397713be6a0cefbb96e149d863d076187caf9db30'
    assert sha(OLD)=='aa6f87968a8bec79b74affbd162ec0a37eed0c1dd964cdb7c46701fbc4f951fa'
    times=[1,10,40,66,69,72,80,94,98,101,106,109,114,118,122.5,123.8,127,135,143,146,148.5]
    sample=B/'output_samples';sample.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1280,7*390),'#eef3f8');d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
    # 3 columns, 7 rows; each frame at 426 x 240 with a concise time label.
    sheet=Image.new('RGB',(1278,7*270),'#eef3f8');d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        p=sample/f'{t:07.3f}.jpg'
        subprocess.run([FF,'-v','error','-nostdin','-y','-ss',str(t),'-i',str(OUT),'-frames:v','1','-q:v','2',str(p)],check=True)
        x=(i%3)*426;y=(i//3)*270
        sheet.paste(Image.open(p).resize((426,240)),(x,y));d.text((x+8,y+242),f'{t:.3f} s',fill='#183149',font=font)
    sheet.save(B/'output_contact_sheet.jpg',quality=92)
    result={'full_decode_exit':proc.returncode,'decode_errors':proc.stderr,'decoded_frames':frames,'duration_seconds':149,'width':1920,'height':1080,'fps':30,'audio_tracks':0,'sample_times_seconds':times,'source_hashes_unchanged':True,'output_sha256':sha(OUT),'visual_review':'pending'}
    (B/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
