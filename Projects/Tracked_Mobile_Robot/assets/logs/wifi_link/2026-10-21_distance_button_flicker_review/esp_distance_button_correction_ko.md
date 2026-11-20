# 거리 실행 버튼 깜박임 — 준비 상태와 송신 시점 분리

## 원인과 교정 범위

사용자가 ARM 후 공중 궤도 거리 실행 버튼이 빠르게 활성/비활성으로 바뀐다고 보고했다. 실제 저장본으로 정지 상태에서 다음 zero CMD를 보내는 시점을 검사해 재현했다. 기존 `distanceReady()`가 `pending===null`과 사용 가능한 ticket을 요구해, 약80ms마다 ACK 대기·ticket 소진 중 버튼과 준비 문구가 바뀌었다. count가 움직인 것으로 확정한 것이 아니다. 이전16개 거리 검사는 송신 사이 준비 시점만 확인해 이 구간을 놓쳤다.

실제 입력 대상은 `03_Firmware/esp32_wifi_link/main/wifi_link_main.c`의 **PAGE 안5개 함수**다. PAGE 전체를 다시 입력하지 않는다. 아래5개 전체 교체 블록을 함께 적용한다. 로그 사본·candidate 파일은 입력 대상이 아니다. 사용자 입력 전에 생산 소스는 수정하지 않았다.

## 새 흐름과 정지 조건

- 준비 표시는 같은 ARM의 fresh count/CPS·요청/PWM 정지100ms, ACTIVE·owner·포커스 조건으로 결정한다. 단순 ACK 대기나 ticket 교체로 버튼을 끄지 않는다. TEL/제어 상태가 오래되거나 정지가 풀리면 비활성화/중단하는 조건은 유지한다.
- trusted 포인터를 누르면 목표를 고정한다. zero CMD 응답이나 새 ticket을 기다리는 동안에도 포인터를 유지해야 한다. 실제 `sendCommand()`는 기존 pending·ticket·80ms 간격 검증을 그대로 거친다. 새 ticket이 왔다는 이유만으로 실행하지 않는다.
- 첫 거리 CMD 전송까지 최대200ms 기다린다. 기한이 끝나면 `START_WAIT_TIMEOUT`과 DISARM이며, 늦은 ACK·ticket이 도착해도 재실행하지 않는다. 송신 함수와 반복 타이머 양쪽에서 기한을 검사한다. 기한을 반복 갱신하지 않는다.
- 첫 거리 CMD를 보내기 전에 관측 count가 기준에서 바뀌거나 요청/PWM/CPS가0이 아니면 `START_NOT_STILL`로 중단한다. 같은 포인터의 release/cancel·blur·stale·DISARM도 기존처럼 취소한다. 대기 중에 손을 놓으면 뒤늦게 거리 명령이 나가지 않는다.
- 목표가 담긴 WebSocket `send()`가 성공한 시각을 `first_goal_sent_ms`에 기록한다. 이는 브라우저 송신 시각이며 STM 접수·실제 구동 시작 시각이 아니다. 이후300ms CMD timeout·거리 목표/무진행/전체 기한·좌우 차단·E-stop은 기존 STM 책임이다.

안전 한계·freshness·ticket TTL·PWM cap/gain·STM 코드는 변경하지 않는다. 버튼을 단순히 항상 켜 두거나 제한 시간을 늘리는 방식은 사용하지 않는다. 기존 방향 입력·거리 cutoff/final 로그도 유지한다.

## 검증과 다음 순서

기존 main/브라우저 회귀에 정지 버튼의 pending zero ACK·ticket 소진/갱신 구간, 대기 중 trusted hold→늦은 ACK/ticket 송신, release·200ms 만료·대기 중 count 변경 취소를 추가한다. 현재 저장본은 새 깜박임 회귀에서 FAIL이며 교정 후보 PC PASS와 구분한다. PC 검사는 실제 브라우저 체감·보드 타이밍 검증이 아니다.

먼저 DISARM 상태로 두고 아래5개 함수를 교체·저장한다. 저장본 검사가 통과한 뒤 사용자 ESP만 build/flash하고, ARM 후 정지 상태에서 버튼이 안정적으로 유지되는지 먼저 확인한다. STM 재입력/재flash나 거리 구동을 먼저 하지 않는다.

## 1. `distanceReady()` 전체 교체

PAGE 문자열에서 `"function distanceReady(`로 시작하는 줄부터 해당 함수 끝의 `"}\n"` 줄까지 교체한다. 다음 함수는 유지한다.
새 `distanceStartExpired()`는 이 블록에 포함되어 있으므로 따로 중복 추가하지 않는다.

```c
    "function distanceReady(){\n"
    " const now=performance.now();\n"
    " return distanceTrial===null&&motionReady()&&!releaseZero&&\n"
    "  distanceSample(latestTel)&&distanceZero(latestTel)&&distanceStill!==null&&distanceStill.span>=100&&\n"
    "  now-distanceStill.rx+latestTel.stm_age_ms<250;\n"
    "}\n"
    "function distanceStartExpired(){\n"
    " return distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&distanceTrial.first_goal_sent_ms===null&&\n"
    "  performance.now()-distanceTrial.started_ms>=200;\n"
    "}\n"
```

## 2. `distanceStart()` 전체 교체

PAGE 문자열에서 `"function distanceStart(`로 시작하는 줄부터 해당 함수 끝의 `"}\n"` 줄까지 교체한다. 다음 함수는 유지한다.

```c
    "function distanceStart(){\n"
    " distanceTrial={goal_mm:distanceGoal,boot_id:boot,control_id:controlId,arm_seq:distanceArmSeq,\n"
    "  phase:'RUNNING',started_ms:performance.now(),first_goal_sent_ms:null,baseline:distancePoint(latestTel),\n"
    "  accepted_seqs:[],samples:[],samples_dropped:0,cutoff:null,final:null};\n"
    " distanceRuns.push(distanceTrial);if(distanceRuns.length>16){distanceRuns.shift();++distanceRunsDropped;}\n"
    "}\n"
```

## 3. `distanceObserve()` 전체 교체

PAGE 문자열에서 `"function distanceObserve(`로 시작하는 줄부터 해당 함수 끝의 `"}\n"` 줄까지 교체한다. 다음 함수는 유지한다.

```c
    "function distanceObserve(r){\n"
    " if(!distanceSample(r)){\n"
    "  distanceStill=null;\n"
    "  if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
    "   distanceInterrupt('ENCODER_OR_ARM_INVALID');stopLocal(true);\n"
    "  }\n"
    "  return;\n"
    " }\n"
    " if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&distanceTrial.first_goal_sent_ms===null&&\n"
    "    (!distanceZero(r)||r.left_count!==distanceTrial.baseline.left_count||r.right_count!==distanceTrial.baseline.right_count)){\n"
    "  distanceInterrupt('START_NOT_STILL');stopLocal(true);return;\n"
    " }\n"
    " const now=performance.now(),old=distanceStill;\n"
    " const generation=old===null?1:(r.tel_count-old.tel_count)>>>0;\n"
    " if(old===null||generation!==0){\n"
    "  const step=old===null?0:(r.encoder_t_ms-old.encoder_t_ms)>>>0;\n"
    "  const stmStep=old===null?0:(r.stm_t_ms-old.stm_t_ms)>>>0;\n"
    "  const continuous=old!==null&&generation<2147483648&&step>0&&step<=500&&stmStep>0&&stmStep<=500&&now-old.rx<250;\n"
    "  const same=continuous&&distanceZero(r)&&old.zero&&r.left_count===old.left&&r.right_count===old.right;\n"
    "  distanceStill={tel_count:r.tel_count,encoder_t_ms:r.encoder_t_ms,stm_t_ms:r.stm_t_ms,rx:now,\n"
    "   left:r.left_count,right:r.right_count,zero:distanceZero(r),span:same?old.span+step:0};\n"
    "  if(old!==null&&!continuous&&distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
    "   distanceInterrupt('ENCODER_OR_TEL_DISCONTINUITY');stopLocal(true);return;\n"
    "  }\n"
    "  if(distanceTrial!==null){\n"
    "   distanceTrial.samples.push(distancePoint(r));\n"
    "   if(distanceTrial.samples.length>240){distanceTrial.samples.shift();++distanceTrial.samples_dropped;}\n"
    "   if(distanceTrial.phase!=='RUNNING'&&distanceTrial.phase!=='STILL_OBSERVED')distanceTrial.final=distancePoint(r);\n"
    "   if(distanceTrial.phase==='STILL_OBSERVED'&&\n"
    "      (r.left_count!==distanceTrial.final.left_count||r.right_count!==distanceTrial.final.right_count))\n"
    "    distanceTrial.post_still_count_changed=true;\n"
    "  }\n"
    " }\n"
    " // ACK may arrive after its TEL. Recheck the latest TEL when its seq becomes known.\n"
    " if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&r.reason==='DISTANCE_REACHED'&&\n"
    "    r.state==='ARMED'&&r.vx_mmps===0&&r.w_mradps===0&&r.left_pwm===0&&r.right_pwm===0&&\n"
    "    distanceTrial.accepted_seqs.includes(r.last_seq)){\n"
    "  distanceTrial.phase='CUTOFF';distanceTrial.cutoff=distancePoint(r);\n"
    "  distanceTrial.stop_reason='DISTANCE_REACHED';distanceTrial.final=distancePoint(r);\n"
    "  stopLocal(true);\n"
    " }\n"
    " if(distanceTrial!==null&&distanceTrial.phase==='CUTOFF'&&distanceStill!==null&&distanceStill.span>=200){\n"
    "  distanceTrial.phase='STILL_OBSERVED';distanceTrial.final=distancePoint(r);\n"
    " }\n"
    "}\n"
```

## 4. `sendCommand()` 전체 교체

PAGE 문자열에서 `"function sendCommand(`로 시작하는 줄부터 해당 함수 끝의 `"}\n"` 줄까지 교체한다. 다음 함수는 유지한다.

```c
    "function sendCommand(cmd){\n"
    " if(!cmds.includes(cmd))return;\n"
    " updateButtons();\n"
    " if(cmd==='PING'&&ping.disabled)return;\n"
    " if(cmd==='ARM'&&(arm.disabled||!ticketFor('ARM')))return;\n"
    " if(cmd==='DISARM'&&disarm.disabled)return;\n"
    " if(cmd==='CMD'&&distanceStartExpired()){distanceInterrupt('START_WAIT_TIMEOUT');stopLocal(true);return;}\n"
    " if(cmd==='CMD'&&(!connected()||!intent||pending!==null||!focused()||!ticketFor('CMD')||\n"
    "   performance.now()<nextCmdAt||!offer||!['ZERO_PENDING','ACTIVE'].includes(offer.phase)||offer.owner_session!==session||offer.control_id!==controlId||controlId===0||nextId>4294967295))return;\n"
    " if(cmd==='DISARM'){\n"
    "  distanceInterrupt('DISARM');cancelArmWait();clearMotion();\n"
    "  intent=false;controlId=0;clearTimeout(controlTimer);controlTimer=null;\n"
    "  if(pending)ignoredThrough=Math.max(ignoredThrough,pending.id);\n"
    "  clearPending();\n"
    " }\n"
    " const ws=socket;\n"
    " const p={id:nextId++,cmd,boot,session,controlId:cmd==='CMD'?controlId:0};\n"
    " let text=cmd+',boot_id='+boot+',request_id='+p.id;\n"
    " if(cmd==='ARM'||cmd==='CMD'){\n"
    "  if(cmd==='CMD')text+=',control_id='+controlId;\n"
    "  text+=',ticket='+offer.ticket;usedTicket=offer.ticket;\n"
    "  if(cmd==='CMD'){\n"
    "   if(motion!==null&&!motionReady()){stopLocal(true);return;}\n"
    "   const move=motion!==null&&!releaseZero&&motionReady();\n"
    "   const vx=move?motion.vx:0,w=move?motion.w:0;\n"
    "   p.releaseZero=releaseZero;p.distance_mm=move?(motion.distance_mm||0):0;\n"
    "   text+=',vx_mmps='+vx+',w_mradps='+w;\n"
    "   if(p.distance_mm>0)text+=',distance_mm='+p.distance_mm;\n"
    "   nextCmdAt=performance.now()+80;\n"
    "  }else{distanceReset();clearMotion();intent=true;controlId=0;nextCmdAt=0;}\n"
    " }\n"
    " pending=p;nextPingAt=performance.now()+500;\n"
    " notice.textContent='브라우저 송신 · ESP 접수 확인 전';result.textContent=cmd+' 요청 '+p.id+': 결과 대기';\n"
    " commandTimer=setTimeout(()=>{\n"
    "  if(socket!==ws||pending!==p)return;\n"
    "  ignoredThrough=Math.max(ignoredThrough,p.id);clearPending();\n"
    "  result.textContent=cmd+' 요청 '+p.id+': 결과 확인 불가 · 브라우저 대기 시간 초과';\n"
    "  if(cmd==='ARM'||cmd==='CMD')stopLocal(true);\n"
    "  updateButtons();\n"
    " },cmd==='ARM'||cmd==='CMD'?400:3000);\n"
    " try{ws.send(text);}catch(error){disconnect(ws,'명령 송신 실패');return;}\n"
    " if(p.distance_mm>0&&distanceTrial!==null&&distanceTrial.first_goal_sent_ms===null)\n"
    "  distanceTrial.first_goal_sent_ms=performance.now();\n"
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    " updateButtons();\n"
    "}\n"
```

## 5. `controlTick()` 전체 교체

PAGE 문자열에서 `"function controlTick(`로 시작하는 줄부터 해당 함수 끝의 `"}\n"` 줄까지 교체한다. 다음 함수는 유지한다.

```c
    "function controlTick(){\n"
    " controlTimer=null;\n"
    " if(!intent)return;\n"
    " if(distanceStartExpired()){distanceInterrupt('START_WAIT_TIMEOUT');stopLocal(true);return;}\n"
    " if(!focused()||(motion!==null&&!motionReady())){stopLocal(true);return;}\n"
    " if(!offer||performance.now()-offerAt>=200){disconnect(socket,'제어 상태 수신 시간 초과');return;}\n"
    " if(offer.owner_session===session&&['ZERO_PENDING','ACTIVE'].includes(offer.phase)&&\n"
    "    controlId>0&&performance.now()>=nextCmdAt)sendCommand('CMD');\n"
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    "}\n"
```
