"""Check visible button/movement transitions in the encoded deliverable itself.

This is an editing check, not a robot response-time or clock-synchronization test.
"""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageChops
from render_final import B, FF, OUT, sha
from review_alignment import spans, FPS


def extract(start, duration, camera):
    if camera:
        filt='crop=1100:618:40:170,fps=15,scale=320:180:flags=area,format=gray'
        fmt='gray';flag='-vf'
    else:
        filt=('fps=15,format=rgb24,split=4[a][b][c][d];'
              '[a]crop=4:4:1478:827[aa];[b]crop=4:4:1478:955[bb];'
              '[c]crop=4:4:1358:891[cc];[d]crop=4:4:1613:891[dd];'
              '[aa][bb][cc][dd]hstack=inputs=4')
        fmt='rgb24';flag='-filter_complex'
    return subprocess.check_output([FF,'-v','error','-nostdin','-ss',str(start),'-i',str(OUT),
        '-t',str(duration),flag,filt,'-an','-pix_fmt',fmt,'-f','rawvideo','pipe:1'])


def check(start,duration):
    with ThreadPoolExecutor(max_workers=2) as pool:
        cam_task=pool.submit(extract,start,duration,True)
        ui_task=pool.submit(extract,start,duration,False)
        cam=cam_task.result();ui=ui_task.result()
    stride=320*180;energy=[0]
    previous=Image.frombytes('L',(320,180),cam[:stride]).crop((40,35,285,165))
    for i in range(1,len(cam)//stride):
        current=Image.frombytes('L',(320,180),cam[i*stride:(i+1)*stride]).crop((40,35,285,165))
        hist=ImageChops.difference(current,previous).histogram()
        energy.append(sum(n*h for n,h in enumerate(hist) if n>=10)/(245*130))
        previous=current
    ui_stride=16*4*3;active=[]
    for i in range(len(ui)//ui_stride):
        colors=[]
        for k in range(4):
            ix=[i*ui_stride+(y*16+k*4+x)*3 for y in range(4) for x in range(4)]
            colors.append(sum(ui[j+2]-ui[j] for j in ix)/16)
        active.append(int(max(colors)>20))
    camera_spans=spans(energy,.5);button_spans=spans(active,.5);pairs=[]
    for a,b in button_spans:
        if a<.5 or b>duration-.5:continue  # Exclude intervals cut by chapter boundaries.
        matches=[(x,y) for x,y in camera_spans if abs(x-a)<.3 and abs(y-b)<.3]
        assert len(matches)==1,(start,a,b,camera_spans)
        x,y=matches[0]
        pairs.append({'button_output_seconds':[start+a,start+b],
                      'camera_movement_output_seconds':[start+x,start+y],
                      'edge_difference_seconds':[a-x,b-y]})
    return {'output_window_seconds':[start,start+duration],'pairs':pairs}


def main():
    windows=[check(70,27),check(125,16)]
    pairs=[p for w in windows for p in w['pairs']]
    assert len(pairs)==5,len(pairs)
    result={'output_sha256':sha(OUT),'fps_sampled':FPS,'motion_threshold':.5,
            'windows':windows,'complete_spans_checked':len(pairs),
            'max_abs_edge_difference_seconds':max(abs(t) for p in pairs for t in p['edge_difference_seconds']),
            'editing_check':'PASS: all 10 sampled button/movement edges agree within 0.3 seconds',
            'limitation':'Visible response and encoded images only. Threshold, frame sampling, actuator/UI latency are included; not common-clock sync or safety latency measurement.'}
    (B/'render_alignment_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
