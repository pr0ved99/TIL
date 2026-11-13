"""Produce review-only PAGE/snapshot replacements; never edit firmware."""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[3]
MAIN = PROJECT / '03_Firmware/esp32_wifi_link/main/wifi_link_main.c'
raw = MAIN.read_bytes()
base_hash = hashlib.sha256(raw).hexdigest()
manifest = OUT / 'manifest.json'
if manifest.exists():
    assert json.loads(manifest.read_text(encoding='utf-8'))['base_sha256'] == base_hash, 'Production changed; review saved source instead of regenerating'
source = raw.decode('utf-8').replace('\r\n', '\n')
page_match = re.search(r'static const char PAGE\[\] =([\s\S]*?);\n\nstatic ', source)
assert page_match
old_page = page_match[0][:-len('\n\nstatic ')]
html = ''.join(json.loads(m[0]) for m in re.finditer(r'"(?:\\.|[^"\\])*"', page_match[1]))
js = re.search(r'<script>([\s\S]*?)</script>', html)[1]


def change(old, new):
    global js
    assert js.count(old) == 1, old
    js = js.replace(old, new)


change("let armWait=null;", """let armWait=null;
let motion=null, releaseZero=false, latestTel=null, latestTelAt=0;
const motionButtons=['forward','reverse','left','right'].map(byId);
const motionHint=byId('motion_hint');
// Fixed open-loop requests, not calibrated vehicle speeds.
const motionValues={forward:[50,0],reverse:[-50,0],left:[0,250],right:[0,-250]};
function motionReady(){
 const age=performance.now()-latestTelAt;
 return connected()&&intent&&focused()&&controlId>0&&nextId<=4294967295&&
  offer!==null&&offer.zero_only===false&&offer.phase==='ACTIVE'&&
  offer.owner_session===session&&offer.control_id===controlId&&performance.now()-offerAt<200&&
  latestTel!==null&&latestTel.source==='STM_UART'&&latestTel.startup_state==='READY'&&
  latestTel.stm_connected&&!latestTel.stm_stale&&latestTel.stm_age_ms+age<250&&
  latestTel.state==='ARMED'&&latestTel.command_age_ms+age<300&&
  Math.abs(latestTel.vx_mmps)<=100&&Math.abs(latestTel.w_mradps)<=500&&
  Math.abs(latestTel.left_pwm)<=100&&Math.abs(latestTel.right_pwm)<=100;
}
function clearMotion(){
 const old=motion;motion=null;releaseZero=false;
 if(old){try{old.button.releasePointerCapture(old.pointer);}catch(error){/* already released */}}
}
function beginMotion(event,name){
 if(!event.isTrusted||event.button!==0||event.isPrimary===false||motion!==null||releaseZero||!motionReady())return;
 event.preventDefault();
 const button=byId(name),values=motionValues[name];
 motion={button,pointer:event.pointerId,vx:values[0],w:values[1]};
 try{button.setPointerCapture(event.pointerId);}catch(error){stopLocal(true);return;}
 sendCommand('CMD');updateButtons();
}
function endMotion(event){
 if(motion===null||event.pointerId!==motion.pointer)return;
 clearMotion();releaseZero=true;
 // If a CMD is pending, retain zero intent until its ACK and a fresh ticket.
 sendCommand('CMD');updateButtons();
}
function cancelMotion(event){
 if(motion!==null&&event.pointerId===motion.pointer)stopLocal(true);
}
function moveMotion(event){
 if(motion===null||event.pointerId!==motion.pointer)return;
 const r=motion.button.getBoundingClientRect();
 if((event.pointerType==='mouse'&&(event.buttons&1)===0)||
    event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)endMotion(event);
}""")
change(" arm.disabled=armWait!==null||!armReady();", """ arm.disabled=armWait!==null||!armReady();
 const canMove=motionReady()&&!releaseZero;
 for(const button of motionButtons)button.disabled=!canMove||(motion!==null&&motion.button!==button);
 motionHint.textContent=offer&&offer.zero_only?'속도 0 전용 · 방향 입력 비활성':
  releaseZero?'속도 0 응답 대기':motion?'누르는 동안 명령 전송 · 놓으면 속도 0':
  canMove?'방향 버튼을 누르는 동안 명령 전송':'ARM 후 ACTIVE에서 방향 입력 가능';""")
change("function resetControl(){\n cancelArmWait();", "function resetControl(){\n cancelArmWait();clearMotion();latestTel=null;latestTelAt=0;")
change(" const wasIntent=intent;intent=false;controlId=0;", " const wasIntent=intent;intent=false;clearMotion();controlId=0;")
change("   !offer||offer.owner_session!==session", "   performance.now()<nextCmdAt||!offer||!['ZERO_PENDING','ACTIVE'].includes(offer.phase)||offer.owner_session!==session")
change(" if(cmd==='DISARM'){\n  cancelArmWait();", " if(cmd==='DISARM'){\n  cancelArmWait();clearMotion();")
change("  if(cmd==='CMD'){text+=',vx_mmps=0,w_mradps=0';nextCmdAt=performance.now()+100;}\n  else{intent=true;controlId=0;nextCmdAt=0;}", """  if(cmd==='CMD'){
   if(motion!==null&&!motionReady()){stopLocal(true);return;}
   const move=motion!==null&&!releaseZero&&motionReady();
   const vx=move?motion.vx:0,w=move?motion.w:0;
   p.releaseZero=releaseZero;
   text+=',vx_mmps='+vx+',w_mradps='+w;nextCmdAt=performance.now()+100;
  }else{clearMotion();intent=true;controlId=0;nextCmdAt=0;}""")
change(" if(!focused()){stopLocal(true);return;}", " if(!focused()||(motion!==null&&!motionReady())){stopLocal(true);return;}")
change("r.zero_only!==true", "typeof r.zero_only!=='boolean'")
change(" session=r.session_id;", """ if(offer!==null&&offer.zero_only!==r.zero_only){disconnect(socket,'제어 mode 변경 · 새 연결 필요');return;}
 session=r.session_id;""")
change(" control.textContent='제어 상태 · '+r.phase+' · 속도 0 전용';", " control.textContent='제어 상태 · '+r.phase+(r.zero_only?' · 속도 0 전용':' · 방향 입력 모드');")
change(" if(intent&&(['STOPPING','BLOCKED'].includes(r.phase)||(r.phase==='IDLE'&&controlId>0)))stopLocal(false);", """ if(intent&&(['STOPPING','BLOCKED'].includes(r.phase)||(r.phase==='IDLE'&&controlId>0)))stopLocal(false);
 if(intent&&controlId>0&&(r.owner_session!==session||r.control_id!==controlId))stopLocal(true);""")
change(" const expected=pending!==null;", " const completed=pending,expected=pending!==null;")
change("  else if(r.cmd==='ARM'&&intent&&expected)controlId=r.control_id;", """  else if(r.cmd==='ARM'&&intent&&expected)controlId=r.control_id;
  else if(r.cmd==='CMD'&&completed&&completed.releaseZero)releaseZero=false;""")
change("   data.textContent=JSON.stringify(r,null,2);", "   latestTel=r;latestTelAt=performance.now();\n   data.textContent=JSON.stringify(r,null,2);")
change("window.addEventListener('blur',()=>stopLocal(true));", """for(const button of motionButtons){
 button.onpointerdown=event=>beginMotion(event,button.id);
 button.onpointerup=endMotion;button.onpointercancel=cancelMotion;
 button.onlostpointercapture=cancelMotion;
 button.oncontextmenu=event=>event.preventDefault();
}
window.addEventListener('pointerup',endMotion);
window.addEventListener('pointercancel',cancelMotion);
window.addEventListener('pointermove',moveMotion);
window.addEventListener('blur',()=>stopLocal(true));""")
html = re.sub(r'<script>[\s\S]*?</script>', lambda _: '<script>'+js+'</script>', html)
buttons = "<p>마우스/터치로 누르는 동안만 방향 명령을 보냅니다. 놓으면 속도 0, DISARM은 무장 해제입니다.</p><p>명령값: 직진 ±50 mm/s · 회전 ±250 mrad/s (실측 속도 아님)</p><p>"
for name,label in [('forward','전진'),('reverse','후진'),('left','좌회전'),('right','우회전')]:
    buttons += f"<button id='{name}' type='button' style='touch-action:none;user-select:none;min-width:72px;min-height:48px' disabled>{label}</button> "
buttons += "</p><p id='motion_hint'>방향 입력 대기</p>"
html = html.replace("<p id='control'>", buttons+"<p id='control'>")
# Preserve the test-image banner macro; only PAGE and snapshot are replaced.
head, tail = html.split('</h1>', 1)
page = 'static const char PAGE[] =\n    '+json.dumps(head+'</h1>',ensure_ascii=False)+'\n    WIFI_UART_PARTIAL_TEST_BANNER\n'
page += '\n'.join('    '+json.dumps(line,ensure_ascii=False) for line in tail.splitlines(keepends=True))+';'
start = source.index('static int wifi_control_snapshot(')
end = source.index('\n\n/* HTTP 핸들러', start)
old_snapshot = source[start:end]
snapshot = old_snapshot.replace('\\"zero_only\\":true}', '\\"zero_only\\":%s}')
assert snapshot != old_snapshot
needle = 'valid ? (arm ? "ARM" : "CMD") : "NONE", ttl);'
assert snapshot.count(needle)==1
snapshot = snapshot.replace(needle, 'valid ? (arm ? "ARM" : "CMD") : "NONE", ttl,\n        WIFI_CONTROL_ZERO_ONLY ? "true" : "false");')
candidate = source.replace(old_page,page).replace(old_snapshot,snapshot)
(OUT/'source').mkdir(exist_ok=True)
for name,contents in [('source/wifi_link_main.c',candidate),('PAGE.c.txt',page+'\n'),('wifi_control_snapshot.c.txt',snapshot+'\n'),('page.js',js)]:
    (OUT/name).write_text(contents,encoding='utf-8')
manifest.write_text(json.dumps({'scope':'Review only; production unchanged; default mode 1 retained in saved core',
    'base_sha256':base_hash,'candidate_sha256':hashlib.sha256((OUT/'source/wifi_link_main.c').read_bytes()).hexdigest(),
    'replacements':['entire static const char PAGE[] declaration','entire wifi_control_snapshot function']},indent=2)+'\n',encoding='utf-8')
assert MAIN.read_bytes()==raw
print('Prepared PAGE and snapshot review blocks; production unchanged.')
