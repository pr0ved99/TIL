"""Reproducible silent 149-second combined demo; source recordings stay read-only."""
from pathlib import Path
import subprocess, json, hashlib, os, sys
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent
FF = os.environ.get('FFMPEG', 'C:/Users/eyh12/AppData/Local/Temp/codex-video-merge-tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
CAM = Path('C:/Users/eyh12/Desktop/mvp_cam_long_01.mp4')
SCR = Path('C:/Users/eyh12/Desktop/mvp_long_01.mp4')
OLD = B.parents[1]/'2026-10-24_demo_run01/edit/TMR_MVP_Demo_2026-10-24_review.mp4'
OUT = B/'TMR_MVP_Final_2026-10-24.mp4'
OFFSET = 0.5  # Illustrative alignment only; NOT a measured common-clock offset.
FONT = 'C:/Windows/Fonts/malgun.ttf'
BOLD = 'C:/Windows/Fonts/malgunbd.ttf'
FPS = 30

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1048576), b''): h.update(c)
    return h.hexdigest()

def run(args, name):
    with open(B/(name+'.log'), 'w', encoding='utf8') as f:
        subprocess.run([FF, '-hide_banner', '-nostdin', '-y']+args, cwd=B, stdout=f, stderr=subprocess.STDOUT, check=True)

def text(d, xy, value, size=24, color='#183149', bold=False):
    d.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT,size),fill=color)

def base():
    im=Image.new('RGB',(1920,1080),'#eef3f8'); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,112),fill='#10283c')
    text(d,(40,13),'TRACKED MOBILE ROBOT',18,'#80d6cb',True)
    text(d,(40,40),'브라우저로 제어하는 궤도형 로봇',38,'white',True)
    text(d,(1260,30),'브라우저  →  ESP32  →  STM32',25,'#e3edf5',True)
    text(d,(1260,69),'무선 수동 제어 · PWM / 엔코더 피드백',19,'#b8c9d8')
    return im,d

def make_art():
    im,d=base()
    text(d,(40,130),'실제 로봇 · 카펫 지상 주행',26,bold=True)
    text(d,(1180,130),'STM32 실시간 피드백',26,bold=True)
    d.rectangle((38,168,1142,792),fill='#bccbd8')
    d.rounded_rectangle((40,816,1140,1032),radius=16,fill='#10283c')
    text(d,(1180,685),'브라우저 입력 · ARM 활성 여부',26,bold=True)
    d.rounded_rectangle((1180,730,1880,1032),radius=12,fill='white',outline='#d5e0ea')
    text(d,(40,1047),'2026.10.24  ·  원속도 · 무음  |  화면과 카메라는 시연용 근사 정렬',18,'#526779')
    text(d,(1180,1047),'요청값은 실측 차체 속도가 아닙니다.',18,'#526779')
    im.save(B/'layout.png')
    cards=[('intro','HARDWARE × FIRMWARE × WEB','궤도형 로봇 수동 제어 시연',
            '기본 조작 → 카펫 주행 → S0 정지와 복구','탁상과 지상 시연을 같은 흐름으로 연결했습니다.'),
           ('ground_card','02 / GROUND DRIVE','탁상에서 카펫으로',
            '연속 전진과 선회 · 100 × 150 cm 카펫','카펫 크기는 사용자 제공 · 거리 정밀도 측정 영상이 아닙니다.'),
           ('safety_card','03 / STOP & RECOVERY','주행 중 S0 · 래치 유지 · 복구',
            '이후의 두 번째 S0 시연 구간으로 이동합니다.','다음 45초는 원본 구간을 중간 편집 없이 재생합니다.')]
    for name,kicker,title,detail,note in cards:
        im,d=base();d.rounded_rectangle((100,250,1820,880),24,fill='#10283c')
        text(d,(160,315),kicker,25,'#80d6cb',True)
        text(d,(160,405),title,60,'white',True)
        text(d,(160,535),detail,34,'#d8e6f1')
        text(d,(160,740),note,25,'#b8c9d8')
        text(d,(100,1000),'2026.10.24 · NUCLEO-F446RE + ESP32-S3 · MDD10A',24,'#526779')
        im.save(B/(name+'.png'))
    im,d=base()
    text(d,(90,195),'시연 종료',25,'#526779',True)
    text(d,(90,260),'DISARMED · PWM / CPS 0',48,bold=True)
    text(d,(90,365),'S0 → 해제 후에도 FAULT 래치 유지',30)
    text(d,(90,425),'S2 이후에도 ARM 차단 → STM 리셋 후 새 ARM',30)
    text(d,(90,520),'카펫 주행 · 정지 · 복구 · 재주행을 영상으로 기록',27)
    text(d,(90,685),'오른쪽: 원본 화면 녹화 145.6초의 종료 상태',23,'#526779')
    text(d,(90,760),'영상 정렬은 근사값이며 정지 지연·거리 오차 계측이 아닙니다.',23,'#526779')
    text(d,(90,810),'S2는 전원 재인가이며 STM32의 FAULT 래치를 해제하지 않습니다.',23,'#526779')
    final=Image.open(B.parent/'mvp_long_01_detail/0145.600.jpg')
    final=final.crop((842,170,1600,732)).resize((758,562),Image.Resampling.LANCZOS)
    im.paste(final,(1090,245))
    text(d,(90,1000),'2026.10.24 · Tracked Mobile Robot · Lee Younghyun',24,'#526779')
    im.save(B/'outro.png')

def at(t):
    n=round(t*100);h,n=divmod(n,360000);m,n=divmod(n,6000);s,c=divmod(n,100)
    return f'{h}:{m:02}:{s:02}.{c:02}'

def ass(name, start, rows):
    h='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
    for n,size,col,b in [('Chapter',22,'&H00CBD680',0),('Action',36,'&H00FFFFFF',-1),('Detail',24,'&H00E8D8C8',0)]:
        h+=f'Style: {n},Malgun Gothic,{size},{col},&H00000000,&H00000000,&H00000000,{b},0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n'
    h+='\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    for a,b,ch,title,detail in rows:
        for style,y,v in [('Chapter',838,ch),('Action',881,title),('Detail',953,detail)]:
            h+=f'Dialogue: 0,{at(a-start)},{at(b-start)},{style},,0,0,0,,{{\\pos(72,{y})}}{v}\n'
    (B/(name+'.ass')).write_text(h,encoding='utf8')

ENC=['-an','-c:v','libx264','-preset','medium','-crf','19','-threads','4','-pix_fmt','yuv420p','-r','30','-video_track_timescale','15360','-movflags','+faststart','-map_metadata','-1']
def still(name,duration):
    run(['-loop','1','-framerate','30','-i',name+'.png','-t',str(duration)]+ENC+[name+'.mp4'],name)

def panel(name,start,duration,rows):
    ass(name,start,rows)
    graph=f'''[0:v]setpts=PTS-STARTPTS,fps=30,scale=1100:618:flags=lanczos,setsar=1[cam];
[1:v]setpts=PTS-STARTPTS,fps=30,split=3[fb][ctrl][state];
[fb]crop=720:442:860:225,scale=700:430:flags=lanczos,setsar=1[feedback];
[ctrl]crop=480:258:332:270,setsar=1[controls];
[state]crop=960:66:640:88,scale=700:48:flags=lanczos,setsar=1[states];
[2:v][cam]overlay=40:170:shortest=1[v1];
[v1][states]overlay=1180:170:shortest=1[v2];
[v2][feedback]overlay=1180:230:shortest=1[v3];
[v3][controls]overlay=1280:747:shortest=1[v4];
[v4]ass={name}.ass,format=yuv420p[out]'''
    (B/(name+'.filter')).write_text(graph,encoding='utf8')
    run(['-ss',str(start-OFFSET),'-i',str(CAM),'-ss',str(start),'-i',str(SCR),
         '-loop','1','-framerate','30','-i','layout.png','-filter_complex_threads','2',
         '-filter_complex_script',name+'.filter','-map','[out]','-t',str(duration)]+ENC+[name+'.mp4'],name)

def main():
    if '--recovery-only' not in sys.argv:
        make_art()
        still('intro',3)
        run(['-i',str(OLD),'-t','65','-vf','fps=30,setsar=1']+ENC+['tabletop.mp4'],'tabletop')
        still('ground_card',2)
        panel('ground',4,27,[(4,8,'02 / 카펫 주행','ARM · 정지 상태에서 시작','새 ARM 뒤 방향 버튼으로 주행을 시작합니다.'),
            (8,22,'02 / 카펫 주행','연속 전진','실제 궤도 움직임과 PWM / 엔코더 값을 함께 표시'),
            (22,31,'02 / 카펫 주행','선회와 방향 전환','카펫 위 이동을 원래 속도로 확인합니다.')])
        still('safety_card',2)
    panel('recovery',99,45,[(99,105,'03 / 정지와 복구','주행 중 S0 조작','실제 스위치 조작과 화면 상태를 함께 확인'),
        (105,111,'03 / S0 정지','FAULT · ARM 차단','화면의 FAULT · PWM / CPS 0 확인'),
        (111,115,'03 / 래치 유지','S0 해제 후에도 FAULT 유지','ESTOP_LATCHED · ARM 비활성 상태'),
        (115,122.4,'03 / 전원 재인가','S2 조작과 ARM 차단 확인','S2는 전원 재인가 · STM32 래치는 별도 유지'),
        (122.4,124,'03 / STM32 리셋','DISARMED / BOOT로 복귀','ARM 버튼이 다시 활성화됩니다.'),
        (124,127,'03 / 새 ARM','속도 0에서 다시 제어 준비','새 ARM 처리 뒤 ACTIVE 상태 확인'),
        (127,144,'04 / 복구 후 주행','재주행 · 선회 · DISARM','복구 후 움직임과 마지막 제어 해제를 확인합니다.')])
    still('outro',5)
    parts=[('intro',3),('tabletop',65),('ground_card',2),('ground',27),('safety_card',2),('recovery',45),('outro',5)]
    (B/'concat.txt').write_text(''.join(f"file '{n}.mp4'\n" for n,_ in parts),encoding='utf8')
    run(['-f','concat','-safe','0','-i','concat.txt','-map','0:v','-c','copy','-movflags','+faststart','-metadata','title=Tracked Mobile Robot - Manual Control, Ground Drive and S0 Recovery',str(OUT)],'concat')
    manifest={'output':OUT.name,'sha256':sha(OUT),'bytes':OUT.stat().st_size,'duration_seconds':149,'resolution':[1920,1080],'fps':30,'audio_tracks':0,
        'parts':parts,'sources':[{'path':str(p),'sha256':sha(p)} for p in [CAM,SCR,OLD]],
        'new_pair_alignment':{'equation':'screen time = camera time + 0.5 seconds','method':'Illustrative approximate pairing of switch/reset stages. No shared clock or common visible UI. Screen audio silent.','uncertainty':'Not quantified; no subsecond synchronization or latency claim.','anchors_reviewed':{'camera_s0_hand_contact_seconds':104,'screen_armed_seconds':104,'screen_fault_confirmed_seconds':108,'camera_reset_hand_seconds':122,'screen_disarmed_observed_seconds':122.4}},
        'ground_screen_seconds':[4,31],'recovery_screen_seconds':[99,144],'recovery_internal_cuts':0,'playback_speed':1,
        'outro_screen_still_seconds':145.6,'limitations':['carpet size and >1m travel are user reports; no distance-accuracy measurement','no raw telemetry in these recordings','no physical stop latency claim','S2/reset order records this demonstration, not a revised operating procedure','formal MVP acceptance is not upgraded by editing'],
        'validation_status':'pending'}
    (B/'edit_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(OUT,flush=True)

if __name__=='__main__': main()
