"""Reproducible local, silent review edit. Originals are read-only inputs.

Usage: python render_demo.py [--preview]
Requires Pillow and the FFmpeg executable below (or FFMPEG environment variable).
No robot connection, video upload, firmware build or flash is performed.
"""
from pathlib import Path
import os, json, statistics, subprocess, hashlib, argparse
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
FFMPEG = Path(os.environ.get('FFMPEG', 'C:/Users/eyh12/AppData/Local/Temp/codex-video-merge-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'))
CAMERA = Path('C:/Users/eyh12/Desktop/mvp_cam_01.mp4')
SCREEN = Path('C:/Users/eyh12/Desktop/mvp_01.mp4')
OUTPUT = BASE / 'TMR_MVP_Demo_2026-10-24_review.mp4'
FPS, START, END = 24, 6.0, 71.0
OFFSET = 13/24  # screen source time = camera source time + this offset
FONT = Path('C:/Windows/Fonts/malgun.ttf')
BOLD = Path('C:/Windows/Fonts/malgunbd.ttf')

def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def alignment_record():
    data=json.loads((BASE/'visual_button_signals.json').read_text(encoding='utf8'))
    spans={}
    for name,buttons in data['values'].items():
        spans[name]={}
        for button,values in buttons.items():
            ranges=[]; active=False
            for i,value in enumerate(values+[0]):
                now=value > (23 if name=='camera' else 20)
                if now and not active: start=i/FPS
                if active and not now: ranges.append([start,i/FPS])
                active=now
            spans[name][button]=ranges
    anchors=[]
    for button,screen_ranges in spans['screen'].items():
        camera_ranges=spans['camera'][button]
        assert len(screen_ranges)==len(camera_ranges)
        for n,(s,c) in enumerate(zip(screen_ranges,camera_ranges),1):
            for j,label in enumerate(['highlight_on','highlight_off']):
                delta=s[j]-c[j]
                anchors.append({'button':button,'occurrence':n,'edge':label,
                    'screen_seconds':s[j],'camera_seconds':c[j],
                    'offset_seconds':delta,'residual_seconds':delta-OFFSET})
    assert len(anchors)==12
    assert max(abs(a['residual_seconds']) for a in anchors)<1/FPS+1e-8
    result={'method':'Match the same UI button highlight in the direct screen recording and filmed monitor; RGB samples resampled to 24 fps.',
        'equation':'screen_source_seconds = camera_source_seconds + offset_seconds',
        'offset_seconds':OFFSET,'anchors':anchors,
        'median_offset_seconds':statistics.median(a['offset_seconds'] for a in anchors),
        'max_abs_anchor_residual_seconds':max(abs(a['residual_seconds']) for a in anchors),
        'limitations':'Editing alignment only. Frame quantization, display refresh/capture delay and visual classification remain. Not network, ACK or physical stop latency. No speed correction/time warp.',
        'audio_alignment':'Not used: the decoded screen audio is silent.', 'button_spans':spans}
    (BASE/'alignment.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

def make_background():
    im=Image.new('RGB',(1920,1080),'#eef3f8'); d=ImageDraw.Draw(im)
    def txt(x,y,s,size=24,color='#183149',bold=False):
        d.text((x,y),s,font=ImageFont.truetype(str(BOLD if bold else FONT),size),fill=color)
    d.rectangle((0,0,1920,112),fill='#10283c')
    txt(40,13,'TRACKED MOBILE ROBOT',18,'#80d6cb',True)
    txt(40,40,'브라우저로 제어하는 궤도형 로봇',38,'white',True)
    txt(1260,30,'브라우저  →  ESP32  →  STM32',25,'#e3edf5',True)
    txt(1260,69,'무선 수동 제어 · PWM / 엔코더 피드백',19,'#b8c9d8')
    txt(40,130,'실제 로봇',26,bold=True)
    txt(940,136,'배속 없는 탁상 시연',18,'#526779')
    txt(1180,130,'STM32 실시간 피드백',26,bold=True)
    d.rectangle((38,178,1142,696),fill='#bccbd8')
    d.rectangle((1178,178,1882,701),fill='#bccbd8')
    txt(40,716,'브라우저 입력',26,bold=True)
    d.rounded_rectangle((40,762,560,1032),radius=12,fill='white',outline='#d5e0ea',width=1)
    d.rounded_rectangle((580,738,1880,1032),radius=16,fill='#10283c')
    txt(40,1045,'2026.10.24  ·  탁상 수동 주행  ·  무음 검토본',19,'#526779')
    txt(1180,1045,'요청값은 실측 차체 속도가 아닙니다.',19,'#526779')
    im.save(BASE/'layout.png')
    mask=Image.new('L',(280,124),0)
    ImageDraw.Draw(mask).polygon([(0,0),(279,0),(279,70),(0,123)],fill=255)
    mask.save(BASE/'background_monitor_mask.png')

def ass_time(t):
    n=round(t*100); h,n=divmod(n,360000); m,n=divmod(n,6000); s,cs=divmod(n,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'

def make_captions(alignment):
    # Chapter labels describe the recorded sequence; no fabricated live values.
    motions=[]
    names={'forward':('03 / 08','짧은 전진','좌·우 궤도를 같은 방향으로 구동'),
           'reverse':('04 / 08','짧은 후진','좌·우 PWM과 엔코더 부호가 함께 반전'),
           'left':('05 / 08','짧은 좌회전','좌·우 궤도를 서로 반대 방향으로 구동'),
           'right':('06 / 08','짧은 우회전','좌회전과 반대인 PWM·엔코더 부호')}
    for button,ranges in alignment['button_spans']['screen'].items():
        for i,(a,b) in enumerate(ranges):
            chapter,title,detail=names[button]
            if i:
                chapter='07 / 08' if button=='left' else '08 / 08'
                title='긴 좌회전' if button=='left' else '긴 우회전'
                detail='버튼을 누르는 동안 방향 입력 유지'
            motions.append((a,b,chapter,title,detail))
    motions.sort()
    items=[(START,14.75,'01 / 08 · 시작','DISARM','조작 전 제어 해제'),
           (14.75,motions[0][0],'02 / 08 · 준비','ARM','속도0으로 제어 준비')]
    for n,(a,b,chapter,title,detail) in enumerate(motions):
        items.append((a,b,chapter+' · 방향 입력',title,detail))
        next_start=motions[n+1][0] if n+1<len(motions) else 67.2
        items.append((b,next_start,chapter+' · 입력 해제','버튼 해제','속도0 요청 · 다음 조작 대기'))
    items.extend([(67.2,67.35,'마지막 조작','DISARM 요청','제어 해제 확인 중'),
                  (67.35,END,'시연 종료','DISARMED','PWM / CPS 0 · 최종 누적 count 3886 / −564')])
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Chapter,Malgun Gothic,24,&H00CBD680,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Action,Malgun Gothic,46,&H00FFFFFF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Detail,Malgun Gothic,27,&H00E8D8C8,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Note,Malgun Gothic,20,&H00B6A28F,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    lines=[]
    for a,b,chapter,title,detail in items:
        for style,y,value in [('Chapter',774,chapter),('Action',817,title),('Detail',892,detail)]:
            lines.append(f'Dialogue: 0,{ass_time(a-START)},{ass_time(b-START)},{style},,0,0,0,,{{\\pos(620,{y})}}{value}')
    lines.append(f'Dialogue: 0,0:00:00.00,{ass_time(END-START)},Note,,0,0,0,,{{\\pos(620,980)}}같은 회차의 카메라와 화면 녹화를 정렬했습니다. 정지 지연 계측 자료는 아닙니다.')
    (BASE/'captions.ass').write_text(header+'\n'.join(lines)+'\n',encoding='utf8')
    (BASE/'captions.json').write_text(json.dumps({'source_clock':'mvp_01.mp4 seconds','items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); args=ap.parse_args()
    alignment=alignment_record(); make_background(); make_captions(alignment)
    # Crop out the upper monitors. Blur the remaining lower edge of the left
    # monitor only; the robot stays below/right of that small background region.
    graph='''[0:v]setpts=PTS-STARTPTS,fps=24,crop=900:420:250:300,split[cb][cm];
[cm]crop=280:124:0:0,boxblur=14:3[blur];
[3:v]format=gray[mask];
[blur][mask]alphamerge[maskedblur];
[cb][maskedblur]overlay=0:0,scale=1100:514:flags=lanczos,setsar=1[cam];
[1:v]setpts=PTS-STARTPTS,fps=24,split[fb][ctrl];
[fb]crop=758:562:842:170,scale=700:520:flags=lanczos,setsar=1[feedback];
[ctrl]crop=480:258:332:270,setsar=1[controls];
[2:v]format=yuv420p[bg];
[bg][cam]overlay=40:180:shortest=1[v1];
[v1][feedback]overlay=1180:180:shortest=1[v2];
[v2][controls]overlay=60:770:shortest=1[v3];
[v3]ass=captions.ass,format=yuv420p[out]
'''
    if args.preview:
        graph=graph.replace('[out]',"[composed];[composed]select='eq(n,288)'[out]")
    (BASE/'filtergraph.txt').write_text(graph,encoding='utf8')
    cmd=[str(FFMPEG),'-hide_banner','-nostdin','-y','-ss',f'{START-OFFSET:.9f}','-i',str(CAMERA),
         '-ss',str(START),'-i',str(SCREEN),'-loop','1','-framerate',str(FPS),'-i','layout.png',
         '-loop','1','-framerate',str(FPS),'-i','background_monitor_mask.png',
         '-filter_complex_threads','2','-filter_complex_script','filtergraph.txt','-map','[out]','-an']
    if args.preview:
        cmd+=['-frames:v','1','-update','1','preview.png']
    else:
        cmd+=['-t',str(END-START),'-r',str(FPS),'-c:v','libx264','-preset','medium','-crf','19',
              '-pix_fmt','yuv420p','-movflags','+faststart','-map_metadata','-1','-metadata',
              'title=Tracked Mobile Robot - Manual Control Demo - Review',str(OUTPUT)]
    with (BASE/('preview_render.log' if args.preview else 'render.log')).open('w',encoding='utf8') as log:
        subprocess.run(cmd,cwd=BASE,stdout=log,stderr=subprocess.STDOUT,check=True)
    if not args.preview:
        manifest={'date':'2026-10-24','output':str(OUTPUT),'output_sha256':sha256(OUTPUT),'output_bytes':OUTPUT.stat().st_size,
            'resolution':[1920,1080],'fps':FPS,'duration_seconds':END-START,'audio_tracks':0,
            'sources':[{'path':str(p),'sha256':sha256(p)} for p in [CAMERA,SCREEN]],
            'screen_interval_seconds':[START,END],'camera_interval_seconds':[START-OFFSET,END-OFFSET],
            'camera_crop_xywh':[250,300,900,420],'blur_in_camera_crop_xywh':[0,0,280,124],
            'blur_mask_polygon_in_region':[[0,0],[279,0],[279,70],[0,123]],
            'feedback_crop_xywh':[842,170,758,562],'controls_crop_xywh':[332,270,480,258],
            'alignment_offset_seconds':OFFSET,'playback_speed':1,'internal_cuts':0,
            'originals_modified':False,'published':False,'audio_reviewed_by_listening':False,
            'ffmpeg_command':cmd,'validation_status':'pending decode and visual review'}
        (BASE/'edit_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(str(BASE/('preview.png' if args.preview else OUTPUT.name)))

if __name__=='__main__': main()
