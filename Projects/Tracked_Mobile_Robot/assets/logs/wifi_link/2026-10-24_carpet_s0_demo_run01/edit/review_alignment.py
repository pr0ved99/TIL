"""Compare button activity with camera motion; editing alignment, not latency."""
from pathlib import Path
import subprocess, json, statistics, sys
from PIL import Image, ImageChops, ImageStat, ImageDraw, ImageFont
from render_final import FF, B, CAM, SCR

FPS=15
SELECTED_OFFSET=-23/30

def summarize(data):
    energy=data['camera_motion_energy'];active=data['screen_any_button']
    windows={'early':[3,51],'late':[125,141]}
    camera_spans=spans(energy,0.5)
    pairs=[]
    for name,ss in data['screen_button_spans'].items():
        for a,b in ss:
            window=next((k for k,(lo,hi) in windows.items() if lo<=a and b+1<hi),None)
            if not window:continue
            matches=[(x,y) for x,y in camera_spans if abs(x-a-.75)<.3 and abs(y-b-.75)<.3]
            assert len(matches)==1,(name,a,b,matches)
            x,y=matches[0]
            pairs.append({'window':window,'button':name,'screen_span':[a,b],'camera_motion_span':[x,y],
                          'screen_minus_camera_edges':[a-x,b-y],
                          'residual_after_edit_seconds':[a-(x+SELECTED_OFFSET),b-(y+SELECTED_OFFSET)]})
    pairs.sort(key=lambda p:p['screen_span'][0])
    window_scores={}
    for name,(lo,hi) in windows.items():
        scores=[]
        for shift in range(-30,31):
            ps=[(energy[i],active[i+shift]) for i in range(lo*FPS,hi*FPS) if 0<=i+shift<len(active)]
            contrast=statistics.mean(e for e,a in ps if a)-statistics.mean(e for e,a in ps if not a)
            scores.append({'offset_seconds':shift/FPS,'contrast':contrast})
        window_scores[name]=sorted(scores,key=lambda s:s['contrast'],reverse=True)[:3]
    data['recheck']={'old_offset_seconds':.5,'selected_offset_seconds':SELECTED_OFFSET,
        'screen_relative_delay_from_old_seconds':.5-SELECTED_OFFSET,
        'windows_camera_seconds':windows,'motion_threshold':.5,'paired_spans':pairs,
        'independent_window_best_candidates':window_scores,
        'max_abs_edge_residual_seconds':max(abs(r) for p in pairs for r in p['residual_after_edit_seconds']),
        'interpretation':'Editing alignment from visible response, not shared-clock accuracy. 15 fps sampling, chosen motion threshold, actuator and UI delays limit these residuals. No speed change or time-varying offset.'}
    (B/'alignment_recheck.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    im=Image.new('RGB',(1500,220+len(pairs)*115),'#eef3f8');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21)
    small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
    d.text((30,20),'카펫 영상 재정렬: 버튼 강조와 실제 움직임 9구간 대조',font=font,fill='#10283c')
    d.text((30,60),'각 행은 화면 버튼 시작 0초 기준. 빨강=기존 카메라 / 청록=수정 카메라 / 남색=화면 버튼',font=small,fill='#183149')
    d.text((30,95),'화면=카메라 - 0.7667초 / 기존 편집 대비 화면을 1.2667초 늦춤. 15fps 표본이며 지연 계측 아님.',font=small,fill='#183149')
    for i,p in enumerate(pairs):
        a,b=p['screen_span'];x,y=p['camera_motion_span'];top=150+i*115
        d.text((30,top),f'{p["button"]}  화면 {a:.2f}–{b:.2f}s',font=small,fill='#183149')
        # Local seconds at 70 px/sec; allow the longest 14 sec segment.
        for k,(u,v,col) in enumerate([(0,b-a,'#10283c'),(x+.5-a,y+.5-a,'#bb4054'),(x+SELECTED_OFFSET-a,y+SELECTED_OFFSET-a,'#188a78')]):
            d.rectangle((410+70*u,top+k*24,410+70*v,top+k*24+15),fill=col)
        d.line((410,top-4,410,top+78),fill='#526779',width=1)
        d.text((30,top+32),f'잔차 {p["residual_after_edit_seconds"][0]:+.3f} / {p["residual_after_edit_seconds"][1]:+.3f}s',font=small,fill='#526779')
    im.save(B/'alignment_comparison.png')
    print(json.dumps(data['recheck'],ensure_ascii=False,indent=2))
def raw(path, filt, fmt, complex=False):
    return subprocess.check_output([FF,'-v','error','-nostdin','-i',str(path),
        '-filter_complex' if complex else '-vf',filt,'-an','-pix_fmt',fmt,'-f','rawvideo','pipe:1'])

def spans(v,threshold):
    out=[];start=None
    for i,a in enumerate(v+[0]):
        if a>threshold and start is None:start=i/FPS
        if a<=threshold and start is not None:
            if i/FPS-start>.25:out.append([start,i/FPS])
            start=None
    return out

def main():
    if '--cached' in sys.argv:
        summarize(json.loads((B/'alignment_recheck.json').read_text(encoding='utf8')))
        return
    f='fps=15,format=rgb24,split=4[a][b][c][d];[a]crop=4:4:530:350[aa];[b]crop=4:4:530:478[bb];[c]crop=4:4:410:414[cc];[d]crop=4:4:665:414[dd];[aa][bb][cc][dd]hstack=inputs=4'
    buf=raw(SCR,f,'rgb24',True);stride=16*4*3
    values={k:[] for k in ['forward','reverse','left','right']}
    for i in range(len(buf)//stride):
        for k,name in enumerate(values):
            ix=[i*stride+(y*16+k*4+x)*3 for y in range(4) for x in range(4)]
            values[name].append(sum(buf[j+2]-buf[j] for j in ix)/16)
    active=[int(max(v[i] for v in values.values())>20) for i in range(len(buf)//stride)]
    buf=raw(CAM,'fps=15,scale=320:180:flags=area,format=gray','gray');stride=320*180
    energy=[0];prev=Image.frombytes('L',(320,180),buf[:stride]).crop((40,35,285,165))
    for i in range(1,len(buf)//stride):
        im=Image.frombytes('L',(320,180),buf[i*stride:(i+1)*stride]).crop((40,35,285,165))
        diff=ImageChops.difference(im,prev)
        # Ignore low amplitude codec noise; keep a movement energy series.
        hist=diff.histogram();energy.append(sum(n*h for n,h in enumerate(hist) if n>=10)/(245*130))
        prev=im
    results=[]
    # Camera interval 3-60 seconds avoids the operator's hands in S0 scenes.
    # For candidate D: screen event time = camera event time + D.
    for shift in range(-30,31):
        pairs=[(energy[i],active[i+shift]) for i in range(3*FPS,60*FPS) if 0<=i+shift<len(active)]
        on=[e for e,a in pairs if a];off=[e for e,a in pairs if not a]
        results.append({'offset_seconds':shift/FPS,'mean_motion_when_active':statistics.mean(on),
                        'mean_motion_when_inactive':statistics.mean(off),
                        'contrast':statistics.mean(on)-statistics.mean(off)})
    results.sort(key=lambda x:x['contrast'],reverse=True)
    data={'fps':FPS,'method':'camera frame-change energy vs recorded button highlight, camera3-60s; actuator/telemetry delays confounded; not common-clock synchronization',
          'screen_button_spans':{k:spans(v,20) for k,v in values.items()},'camera_motion_energy':energy,'screen_any_button':active,'candidate_scores':results}
    (B/'alignment_recheck.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    summarize(data)

if __name__=='__main__':main()
