"""Local sample review of user supplied carpet/S0 videos. No audio review."""
from pathlib import Path
import subprocess, re, hashlib, json, math, argparse
from PIL import Image, ImageDraw, ImageFont

BASE=Path(__file__).resolve().parent
FFMPEG=Path('C:/Users/eyh12/AppData/Local/Temp/codex-video-merge-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
INPUTS={k:Path('C:/Users/eyh12/Desktop')/(k+'.mp4') for k in ['mvp_long_01','mvp_cam_long_01']}
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',19)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def sheet(images,path,cols=4,width=480):
    height=round(width*9/16)+28
    out=Image.new('RGB',(cols*width,math.ceil(len(images)/cols)*height),'#eef3f8'); d=ImageDraw.Draw(out)
    for i,(label,p) in enumerate(images):
        x=(i%cols)*width;y=(i//cols)*height
        d.text((x+6,y+3),label,font=font,fill='#10283c')
        out.paste(Image.open(p).resize((width,height-28)),(x,y+28))
    out.save(path,quality=90)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--detail',choices=list(INPUTS)); ap.add_argument('--times'); args=ap.parse_args()
    if args.detail:
        times=[float(t) for t in args.times.split(',')]; dst=BASE/(args.detail+'_detail'); dst.mkdir(exist_ok=True)
        for t in times:
            subprocess.run([str(FFMPEG),'-hide_banner','-loglevel','error','-nostdin','-ss',str(t),'-i',str(INPUTS[args.detail]),
                '-frames:v','1','-update','1','-q:v','2','-y',str(dst/f'{t:08.3f}.jpg')],check=True)
        print('Detail samples:',args.detail,times); return
    manifest={'date':'2026-10-24','audio_reviewed':False,'review_method':'Every 60th video frame at nominal 30fps (2s samples), not continuous visual inspection. No sync offset assumed.','videos':[]}
    for name,p in INPUTS.items():
        probe=subprocess.run([str(FFMPEG),'-hide_banner','-i',str(p)],capture_output=True,text=True,encoding='utf8',errors='replace')
        (BASE/(name+'_streams.txt')).write_text(probe.stderr,encoding='utf8')
        m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',probe.stderr); duration=int(m[1])*3600+int(m[2])*60+float(m[3])
        dst=BASE/(name+'_samples'); dst.mkdir(exist_ok=True)
        cmd=[str(FFMPEG),'-hide_banner','-loglevel','error','-nostdin','-i',str(p),'-vf','select=not(mod(n\\,60)),scale=1280:-2',
             '-fps_mode','vfr','-an','-q:v','3','-start_number','0','-y',str(dst/'%04d.jpg')]
        subprocess.run(cmd,check=True)
        frames=sorted(dst.glob('*.jpg'))
        sheet([(f'{int(f.stem)*2:.0f}s',f) for f in frames[::3]],BASE/(name+'_overview.jpg'))
        manifest['videos'].append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'duration_seconds_rounded':duration,
            'samples':len(frames),'sample_seconds':[int(f.stem)*2 for f in frames],'command':cmd})
    (BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
