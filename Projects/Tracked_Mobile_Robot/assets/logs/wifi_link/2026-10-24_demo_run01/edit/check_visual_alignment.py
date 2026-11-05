"""Match visible button highlight transitions, not motion or network latency."""
from pathlib import Path
import subprocess, json, statistics

BASE = Path(__file__).resolve().parent
RAW = BASE.parents[3]/'videos/wifi_mvp/2026-10-24/raw'
FFMPEG = Path('C:/Users/eyh12/AppData/Local/Temp/codex-video-merge-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
FPS = 24
SETUPS = {
 'camera': ('mvp_cam_01', (560,70,125,105), {'forward':(616,122),'reverse':(616,149),'left':(591,135),'right':(647,135)}),
 'screen': ('mvp_01', (380,340,350,160), {'forward':(540,352),'reverse':(540,478),'left':(410,414),'right':(665,414)})
}

def get_values(setup):
    stem,(x,y,w,h),points=setup
    raw = subprocess.check_output([str(FFMPEG),'-hide_banner','-loglevel','error','-nostdin','-i',str(RAW/(stem+'.mp4')),
        '-vf',f'fps={FPS},format=rgb24,crop={w}:{h}:{x}:{y}','-an','-f','rawvideo','pipe:1'])
    stride=w*h*3
    assert len(raw) % stride == 0
    out={k:[] for k in points}
    for i in range(len(raw)//stride):
        for k,(px,py) in points.items():
            offsets=[i*stride+((py-y+dy)*w+px-x+dx)*3 for dx in range(-1,2) for dy in range(-1,2)]
            out[k].append(sum(raw[o+2]-raw[o] for o in offsets)/len(offsets))
    return out

all_values={k:get_values(v) for k,v in SETUPS.items()}
for k,vs in all_values.items():
    print(k, {b:[round(vs[b][int(t*FPS)],1) for t in [0,15,18,23,27,29,33,35,39,42,51,54,60,63,67]] for b in vs})
(BASE/'visual_button_signals.json').write_text(json.dumps({'fps':FPS,'values':all_values},indent=2)+'\n',encoding='utf8')
