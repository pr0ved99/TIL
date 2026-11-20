"""Prepare one complete PAGE replacement, retaining all production C outside it."""
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
MAIN=HERE.parent/'esp32_wifi_link/main/wifi_link_main.c'


def page_range(source):
    match=re.search(r'static const char PAGE\[\] =([\s\S]*?);\n\nstatic ',source)
    assert match
    return match.start(),match.end()-len('\n\nstatic '),match.group(1)


def prepare():
    source=MAIN.read_text(encoding='utf-8')
    a,z,literals=page_range(source)
    html=''.join(json.loads(m[0]) for m in re.finditer(r'"(?:\\.|[^"\\])*"',literals))
    assert 'g6DistanceObserve' not in html, 'Already entered; use --saved'
    before,script=html.split('<script>\n',1)
    script,after=script.split('</script>',1)
    controls="""<fieldset><legend>공중 궤도 거리 시험</legend>
<p>양쪽 궤도를 띄운 상태에서 사용하세요. 거리는 ARM 전에 선택하며, 실행 후 다음 시험은 새 ARM이 필요합니다.</p>
<p><button id='distance_50' type='button' disabled>5 cm</button> <button id='distance_100' type='button' disabled>10 cm</button> <button id='distance_150' type='button' disabled>15 cm</button> <button id='distance_200' type='button' disabled>20 cm</button></p>
<p><button id='distance_move' type='button' style='touch-action:none;user-select:none;min-height:48px' disabled>선택 거리 전진 · 누르는 동안</button></p>
<p id='distance_hint'>거리 시험 준비 대기</p>
<button id='distance_report' type='button' disabled>거리 기록 복사</button>
<p id='distance_copy_status' role='status' aria-live='polite'></p>
<textarea id='distance_data' aria-label='거리 기록 JSON' readonly hidden rows='6' style='width:100%;box-sizing:border-box'></textarea></fieldset>
"""
    before=before.replace("<pre id='data'>",controls+"<pre id='data'>",1)
    before=before.replace('놓으면 속도 0, DISARM은 무장 해제입니다.',
                          '방향 버튼을 놓으면 속도 0, 거리 버튼을 놓으면 DISARM으로 중단합니다.')

    def replace(old,new):
        nonlocal script
        assert script.count(old)==1, old
        script=script.replace(old,new,1)

    replace("function motionReady(){",(HERE/'wifi_distance_page.js').read_text(encoding='utf-8')+'\nfunction motionReady(){')
    replace("const motionButtons=['forward','reverse','left','right'].map(byId);",
            "const motionButtons=['forward','reverse','left','right'].map(byId);\n"
            "const pointerButtons=motionButtons.concat(byId('distance_move'));")
    replace("const motionValues={forward:[100,0],reverse:[-100,0],left:[0,500],right:[0,-500]};",
            "const motionValues={forward:[100,0],reverse:[-100,0],left:[0,500],right:[0,-500],distance_move:[100,0]};")
    replace(" event.preventDefault();\n const button=byId(name),values=motionValues[name];",
            " const distance=name==='distance_move';\n"
            " if(distance?!distanceReady():distanceTrial!==null)return;\n"
            " event.preventDefault();\n const button=byId(name),values=motionValues[name];")
    replace(" motion={button,pointer:event.pointerId,vx:values[0],w:values[1]};",
            " motion={button,pointer:event.pointerId,vx:values[0],w:values[1],distance_mm:distance?distanceGoal:0};")
    replace(" sendCommand('CMD');updateButtons();\n}\nfunction endMotion(event){",
            " if(distance)distanceStart();\n sendCommand('CMD');updateButtons();\n}\nfunction endMotion(event){")
    replace(" if(motion===null||event.pointerId!==motion.pointer)return;\n clearMotion();releaseZero=true;",
            " if(motion===null||event.pointerId!==motion.pointer)return;\n"
            " if(motion.distance_mm>0){distanceInterrupt('BUTTON_RELEASE');stopLocal(true);return;}\n"
            " clearMotion();releaseZero=true;")
    replace(" const canMove=motionReady()&&!releaseZero;",
            " distanceUpdate();\n const canMove=motionReady()&&!releaseZero&&distanceTrial===null;")
    replace(" cancelArmWait();clearMotion();latestTel=null;latestTelAt=0;",
            " distanceReset();cancelArmWait();clearMotion();latestTel=null;latestTelAt=0;")
    replace("function stopLocal(sendStop){\n",
            "function stopLocal(sendStop){\n distanceInterrupt('CONTROL_STOP');\n")
    replace(" if(cmd==='DISARM'){\n  cancelArmWait();clearMotion();",
            " if(cmd==='DISARM'){\n  distanceInterrupt('DISARM');cancelArmWait();clearMotion();")
    replace("   p.releaseZero=releaseZero;",
            "   p.releaseZero=releaseZero;p.distance_mm=move?(motion.distance_mm||0):0;")
    replace("   text+=',vx_mmps='+vx+',w_mradps='+w;nextCmdAt=performance.now()+80;",
            "   text+=',vx_mmps='+vx+',w_mradps='+w;\n"
            "   if(p.distance_mm>0)text+=',distance_mm='+p.distance_mm;\n"
            "   nextCmdAt=performance.now()+80;")
    replace("  }else{clearMotion();intent=true;controlId=0;nextCmdAt=0;}",
            "  }else{distanceReset();clearMotion();intent=true;controlId=0;nextCmdAt=0;}")
    replace("  else if(r.cmd==='ARM'&&intent&&expected)controlId=r.control_id;",
            "  else if(r.cmd==='ARM'&&intent&&expected){controlId=r.control_id;distanceArmSeq=r.seq;distanceStill=null;}\n"
            "  else if(r.cmd==='CMD'&&completed&&completed.distance_mm>0&&distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
            "   distanceTrial.accepted_seqs.push(r.seq);distanceObserve(latestTel);\n  }")
    replace("   latestTel=r;latestTelAt=performance.now();",
            "   latestTel=r;latestTelAt=performance.now();distanceObserve(r);")
    replace("for(const button of motionButtons){\n button.onpointerdown=event=>beginMotion(event,button.id);",
            "for(const button of pointerButtons){\n button.onpointerdown=event=>beginMotion(event,button.id);")
    # Helper initialization runs after all base control globals, before connect().
    html=before+'<script>\n'+script+'</script>'+after
    head,rest=html.split('</h1>',1);head+='</h1>'
    def literals(text):
        return '\n'.join('    '+json.dumps(line,ensure_ascii=False)
                         for line in text.splitlines(keepends=True))
    # Split HTML tags for readable C literals without changing HTML/script bytes.
    rest=rest.replace('<script>\n','<script>\n',1)
    prefix,js=rest.split('<script>\n',1)
    prefix_parts=re.split(r'(?=<[A-Za-z/!])',prefix)
    page='static const char PAGE[] =\n'+literals(head)+'\n    WIFI_UART_PARTIAL_TEST_BANNER\n'
    page+='\n'.join(literals(part) for part in prefix_parts if part)
    page+='\n'+literals('<script>\n'+js)+';'
    return source[:a]+page+source[z:],page
