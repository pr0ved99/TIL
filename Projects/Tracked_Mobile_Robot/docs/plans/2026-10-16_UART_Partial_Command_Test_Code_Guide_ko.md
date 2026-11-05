# UR-02: 부분 명령 수동 주입 코드 입력 가이드

작성: 2026-10-16. **오늘은 기본 비활성 코드 입력 → 실제 저장본 PC 검사까지 진행한다.** 시험용 빌드·플래시·주입은 이후 보드 조건을 확인하고 별도로 수행한다.

## 1. 왜 만드는가

새벽의 두 단절 캡처에서는 명령 전체가 유실됐다. CAN+LF를 붙인 첫 DISARM의 정상 재연결 복구는 확인했지만, **STM에 남은 미완성 명령을 실제로 폐기하는 조건**은 아직 확인하지 못했다. 별도 USB–UART 없이 ESP가 정해진 부분 문자열을 보내 이 조건을 만든다.

```mermaid
flowchart LR
    A[수동 시험 요청] --> B[READY·IDLE·새 TEL·속도와 PWM 0 확인]
    B --> C[LF 없는 고정 문자열 한 번 송신]
    C --> D[약 100ms 동안 수신과 상태 검사]
    D --> E[기존 CAN+LF와 DISARM 송신]
    E --> F[일치 ACK와 이후 새 정지 TEL]
    F --> G[IDLE 확인과 캡처 판독]
```

- `CMD,seq=`는 seq 값도 완성되지 않은 명령 조각이다.
- `ARM,seq=번호`는 내용이 완성됐지만 종결 LF가 없어 아직 실행하면 안 되는 명령이다.
- CAN은 ASCII 취소 문자 `0x18`이며 CAN 버스가 아니다. STM은 CAN부터 다음 LF까지 줄을 버리고, 뒤의 DISARM으로 정지를 처리한다.
- LF만 덧붙이면 남은 ARM이 실행될 수 있다. **마지막 화면이 DISARMED라도 중간 ARM 실행을 놓칠 수 있으므로 ACK와 파형을 함께 확인한다.**

## 2. 역할과 상태 흐름

| 담당 | 역할 |
| --- | --- |
| HTTP handler | 현재 boot_id와 시작 조건을 확인하고 요청 상태만 저장. UART 송신 없음 |
| 기존 `stm_uart_rx_task` | 시험 prefix와 제어 송신을 같은 태스크에서 직렬 실행 |
| 시험 상태 | UNUSED → QUEUED → HOLD → STOPPING → DONE. 송신 전 취소·만료는 ABORTED |
| 기존 executor | CAN+LF/DISARM, 정확한 seq의 ACK, ACK 이후 새 정지 TEL, 실패 시 BLOCKED |
| STM | 기존 CAN 줄 폐기와 명령 파싱. 이번 추가 작업에서는 소스 수정 없음 |

설정 `WIFI_UART_PARTIAL_TEST_MODE`는 **0=정상, 1=부분 CMD, 2=LF 없는 ARM**이다. 아래는 0U로 입력한다. 1/2 시험 이미지는 부팅 전체에서 일반 PING/ARM/CMD를 BUSY로 거부하고 제어 ticket을 발급하지 않는다. 수동 DISARM과 부팅용 DISARM/PING은 유지한다. 화면에 시험 이미지 표시가 나온다. PING 버튼이 보여도 일반 PING 요청은 거부된다.

한 번 접수한 뒤 같은 부팅에서 재주입하지 않는다. 수동 POST 전 자동 주입, 임의 문자열, nonzero 명령은 없다. POST 본문은 현재 boot_id의 십진수 문자열만 허용한다. **202는 접수일 뿐 전달·성공 증거가 아니다.** 응답을 잃어도 자동 재시도하지 않는다.

## 3. 실패와 경합 처리

| 상황 | 처리 |
| --- | --- |
| 접수 조건 미충족 | 409, 주입 없음. 조건을 정리한 뒤 수동 재요청 가능 |
| 접수 후 50ms 이상 대기 / 상태 변화 | ABORTED, 주입 없음. 이번 부팅의 시도는 소비됨 |
| prefix 전에 수동 DISARM / 통신 해제 | 대기 주입 취소. 수동 정지는 기존 경로로 처리 |
| 송신 확정 직후 수동 DISARM | 확정한 바이트는 회수 불가. 100ms 대기를 취소하고 뒤에 priority DISARM |
| prefix 짧은 쓰기 | prefix 재전송 없이 정지 경로로 전환. `prefix_full=0`은 시험 입력 미완료 |
| 대기 중 TEL stale / FAULT / 출력 변화 | 대기를 취소하고 기존 정지 경로로 전환 |
| 정지 ACK / 새 정지 TEL 누락 | 기존 기한에 BLOCKED. 자동 재시도 없음. 수동 DISARM 복구는 가능 |
| UART 번호 소진 | prefix와 뒤의 DISARM 번호가 남아 있지 않으면 주입하지 않음 |

공유 상태는 `s_stm_lock`으로 보호한다. UART 송신과 HTTP 응답 동안에는 이 잠금을 잡지 않는다. `uart_write_bytes` 반환 길이는 드라이버에 넘긴 길이이며 STM 수신 확인이 아니다. 100ms는 ESP 타이머의 대기 기준이며 실제 선로 간격은 LA에서 측정한다.

## 4. 입력 범위 — 한 묶음으로 저장

입력 대상은 **`03_Firmware/esp32_wifi_link/main/wifi_link_main.c` 한 파일**이다. 지금 열려 있는 `wifi_control_executor.c`, STM 파일, CMake, 개인 Wi-Fi 설정은 이번에 수정하지 않는다.

아래 8개 블록을 한 묶음으로 입력하고 저장한다. 함수는 선언부터 닫는 중괄호까지 통째로 교체한다. 줄 번호는 삽입하면서 바뀌므로 함수명과 앵커를 기준으로 한다. 중간 상태로 빌드·플래시하지 않는다.


### 4-1. 설정과 함수 선언

`#define STATUS_JSON_SIZE` 바로 앞에 추가한다. **0U를 유지한다.**

```c
/* 0: normal image; 1: partial CMD; 2: ARM without LF.
 * Test images reject normal PING/ARM/CMD for the entire boot.
 * One manual POST per boot; never inject automatically at startup. */
#define WIFI_UART_PARTIAL_TEST_MODE 0U
#if WIFI_UART_PARTIAL_TEST_MODE > 2U
#error "WIFI_UART_PARTIAL_TEST_MODE must be 0, 1 or 2"
#endif
#if WIFI_UART_PARTIAL_TEST_MODE != 0U
#define WIFI_UART_PARTIAL_TEST_BANNER \
    "<p><strong>UART 부분 명령 시험 이미지</strong> · 일반 PING/ARM/CMD 비활성 · 수동 DISARM 가능</p>"
#else
#define WIFI_UART_PARTIAL_TEST_BANNER ""
#endif

static esp_err_t wifi_uart_test_post(httpd_req_t *req);
static void wifi_uart_test_cancel_locked(void);
```


### 4-2. PAGE 전체 블록 교체 — 10/16 저장본 검토 후 범위 명확화

**`static const char PAGE[] =`부터 `static int status_json(...)` 바로 앞까지 전부 선택하고 아래 블록 하나로 교체한다.** 주석으로 보관한 이전 PAGE 선언·HTML·JavaScript도 이 범위에 포함한다. `status_json` 함수는 선택하지 않는다.

처음 안내는 HTML 머리만 교체하고 기존 JavaScript를 이어 붙이는 방식이었다. 복사 과정에서 전체 기존 PAGE가 주석 처리되는 일을 막기 위해, 아래에는 **JavaScript와 끝의 세미콜론까지 포함한 완전한 PAGE**를 제공한다. 다른 7개 블록은 다시 입력할 필요가 없다.

```c
static const char PAGE[] =
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>ESP Wi-Fi Link</title></head><body><h1>로봇 상태</h1>"
    WIFI_UART_PARTIAL_TEST_BANNER
    "<p>STM32 UART → ESP32 Wi-Fi → 브라우저</p><p id='link'>연결 확인 중</p><p id='stm'>STM TEL 수신 대기</p><p id='startup'>부팅 응답 새 상태 확인 대기</p><p>READY는 이번 ESP 부팅 때 응답 확인을 마쳤다는 뜻입니다. 현재 통신 상태는 TEL 표시에서 확인하세요.</p><p><button id='ping' type='button' disabled>PING</button> <button id='arm' type='button' disabled>ARM · 속도 0</button> <button id='disarm' type='button' disabled>DISARM</button></p><p id='control'>제어 상태 수신 대기</p><p id='command_notice'>명령 송신 대기</p><p id='command_result'>명령 결과 수신 대기</p><pre id='data'></pre><script>\n"
    "const byId=id=>document.getElementById(id);\n"
    "const link=byId('link'), stm=byId('stm'), startup=byId('startup'), data=byId('data');\n"
    "const notice=byId('command_notice'), result=byId('command_result'), control=byId('control');\n"
    "const ping=byId('ping'), disarm=byId('disarm'), arm=byId('arm');\n"
    "let socket=null, retry=null, watchdog=null, buttonTimer=null, commandTimer=null, controlTimer=null;\n"
    "let boot=null, session=null, startupFinished=false, nextId=1, ignoredThrough=0, pending=null, nextPingAt=0;\n"
    "let offer=null, offerAt=0, ticketDeadline=0, usedTicket=0, intent=false, controlId=0, nextCmdAt=0;\n"
    "let armWait=null;\n"
    "// Best-effort transit budget; ESP still enforces its own 150 ms expiry.\n"
    "const TICKET_SEND_MARGIN_MS=50;\n"
    "const ARM_WAIT_MS=200;\n"
    "const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;\n"
    "const cmds=['PING','DISARM','ARM','CMD'];\n"
    "const resultLabels={OK:'응답 확인',TIMEOUT:'응답 시간 초과',STM_ERROR:'STM 명령 거부',\n"
    " TX_ERROR:'UART 송신 실패',RX_ERROR:'UART 수신 실패',QUEUE_EXPIRED:'대기 시간 초과',\n"
    " BOOT_MISMATCH:'ESP 부팅 식별값 불일치',UNSUPPORTED:'미지원 명령',SEQ_EXHAUSTED:'UART 번호 소진',\n"
    " FORMAT_ERROR:'송신 형식 오류',CONNECTION_CLOSED:'요청 연결 종료',CANCELLED:'취소됨',STOP_UNCONFIRMED:'정지 확인 실패'};\n"
    "const noticeLabels={QUEUED:'ESP 접수 · STM 응답 확인 중',BAD_FORMAT:'명령 형식 오류',BOOT_MISMATCH:'ESP 부팅 식별값 불일치',\n"
    " STARTUP_PENDING:'부팅 확인 진행 중',DUPLICATE:'이미 접수한 요청 번호',RATE_LIMIT:'요청 간격이 너무 짧음',\n"
    " BUSY:'다른 요청 처리 중',QUEUE_FULL:'요청 큐 사용 불가',TICKET_REJECTED:'ticket 불일치 또는 만료',NOT_READY:'ARM 조건 미충족',BAD_INPUT:'허용하지 않는 입력'};\n"
    "function ownKey(obj,key){return Object.prototype.hasOwnProperty.call(obj,key);}\n"
    "function focused(){return !document.hidden&&document.hasFocus();}\n"
    "function connected(){return socket!==null&&socket.readyState===WebSocket.OPEN&&boot!==null&&startupFinished;}\n"
    "function ticketFor(purpose){return offer!==null&&offer.purpose===purpose&&offer.ticket>0&&offer.ticket!==usedTicket&&\n"
    " performance.now()<ticketDeadline&&performance.now()-offerAt<200;}\n"
    "function armReady(){return connected()&&nextId<=4294967295&&pending===null&&!intent&&focused()&&\n"
    " offer!==null&&offer.phase==='IDLE'&&offer.purpose==='ARM'&&offer.ticket>0&&performance.now()-offerAt<200;}\n"
    "function cancelArmWait(message){\n"
    " if(armWait===null)return;clearTimeout(armWait.timer);armWait=null;\n"
    " if(message)notice.textContent=message;\n"
    "}\n"
    "function requestArm(){\n"
    " if(armWait!==null||!armReady())return;\n"
    " if(ticketFor('ARM')){sendCommand('ARM');return;}\n"
    " // One bounded manual click, cancelled before any eventual send. Never a retry.\n"
    " const wait={ws:socket,boot,session,until:performance.now()+ARM_WAIT_MS,timer:null};armWait=wait;\n"
    " notice.textContent='ARM 준비 확인 중';\n"
    " wait.timer=setTimeout(()=>{\n"
    "  if(armWait!==wait)return;cancelArmWait('ARM 준비 시간 초과 · 다시 눌러주세요');updateButtons();\n"
    " },ARM_WAIT_MS);updateButtons();\n"
    "}\n"
    "function tryWaitingArm(){\n"
    " const wait=armWait;if(wait===null)return;\n"
    " if(socket!==wait.ws||boot!==wait.boot||session!==wait.session||performance.now()>=wait.until||!armReady()){\n"
    "  cancelArmWait('ARM 준비 대기 취소 · 다시 눌러주세요');return;\n"
    " }\n"
    " if(ticketFor('ARM')){cancelArmWait();sendCommand('ARM');}\n"
    "}\n"
    "function updateButtons(){\n"
    " clearTimeout(buttonTimer);buttonTimer=null;\n"
    " const ready=connected()&&nextId<=4294967295;\n"
    " ping.disabled=!ready||pending!==null||armWait!==null||intent||(offer!==null&&!['IDLE','BLOCKED'].includes(offer.phase))||performance.now()<nextPingAt;\n"
    " disarm.disabled=!ready||(pending!==null&&pending.cmd==='DISARM');\n"
    " arm.disabled=armWait!==null||!armReady();\n"
    " let refreshAt=Infinity;\n"
    " if(ready&&pending===null&&performance.now()<nextPingAt)refreshAt=nextPingAt;\n"
    " if(!arm.disabled)refreshAt=Math.min(refreshAt,offerAt+200);\n"
    " if(Number.isFinite(refreshAt))buttonTimer=setTimeout(updateButtons,Math.max(1,Math.ceil(refreshAt-performance.now())));\n"
    "}\n"
    "function clearPending(){clearTimeout(commandTimer);commandTimer=null;pending=null;}\n"
    "function resetControl(){\n"
    " cancelArmWait();\n"
    " intent=false;controlId=0;offer=null;usedTicket=0;ticketDeadline=0;\n"
    " clearTimeout(controlTimer);controlTimer=null;\n"
    "}\n"
    "function stopLocal(sendStop){\n"
    " cancelArmWait('ARM 준비 대기 취소 · 수동 ARM 필요');\n"
    " const wasIntent=intent;intent=false;controlId=0;clearTimeout(controlTimer);controlTimer=null;\n"
    " if(wasIntent&&sendStop&&connected())sendCommand('DISARM');\n"
    " updateButtons();\n"
    "}\n"
    "function sendCommand(cmd){\n"
    " if(!cmds.includes(cmd))return;\n"
    " updateButtons();\n"
    " if(cmd==='PING'&&ping.disabled)return;\n"
    " if(cmd==='ARM'&&(arm.disabled||!ticketFor('ARM')))return;\n"
    " if(cmd==='DISARM'&&disarm.disabled)return;\n"
    " if(cmd==='CMD'&&(!connected()||!intent||pending!==null||!focused()||!ticketFor('CMD')||\n"
    "   !offer||offer.owner_session!==session||offer.control_id!==controlId||controlId===0||nextId>4294967295))return;\n"
    " if(cmd==='DISARM'){\n"
    "  cancelArmWait();\n"
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
    "  if(cmd==='CMD'){text+=',vx_mmps=0,w_mradps=0';nextCmdAt=performance.now()+100;}\n"
    "  else{intent=true;controlId=0;nextCmdAt=0;}\n"
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
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    " updateButtons();\n"
    "}\n"
    "function controlTick(){\n"
    " controlTimer=null;\n"
    " if(!intent)return;\n"
    " if(!focused()){stopLocal(true);return;}\n"
    " if(!offer||performance.now()-offerAt>=200){disconnect(socket,'제어 상태 수신 시간 초과');return;}\n"
    " if(offer.owner_session===session&&['ZERO_PENDING','ACTIVE'].includes(offer.phase)&&\n"
    "    controlId>0&&performance.now()>=nextCmdAt)sendCommand('CMD');\n"
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    "}\n"
    "function validControl(r){\n"
    " if(!r||r.kind!=='control_state'||!u32(r.boot_id)||!u32(r.session_id)||r.session_id===0||\n"
    " !u32(r.owner_session)||!u32(r.control_id)||!u32(r.ticket)||!u32(r.ttl_ms)||r.zero_only!==true||\n"
    " !['IDLE','ARM_PENDING','ZERO_PENDING','ACTIVE','STOPPING','BLOCKED'].includes(r.phase)||\n"
    " !['NONE','ARM','CMD'].includes(r.purpose))return false;\n"
    " if((r.owner_session===0)!==(r.control_id===0))return false;\n"
    " if(['IDLE','STOPPING','BLOCKED'].includes(r.phase)&&r.owner_session!==0)return false;\n"
    " if(['ARM_PENDING','ZERO_PENDING','ACTIVE'].includes(r.phase)&&r.owner_session===0)return false;\n"
    " if(r.purpose==='NONE')return r.ticket===0&&r.ttl_ms===0;\n"
    " if(r.ticket===0||r.ttl_ms===0||r.ttl_ms>150)return false;\n"
    " return r.purpose==='ARM'?r.phase==='IDLE':\n"
    "  ['ZERO_PENDING','ACTIVE'].includes(r.phase)&&r.owner_session===r.session_id;\n"
    "}\n"
    "function handleControl(r){\n"
    " if(boot===null||r.boot_id!==boot||(session!==null&&r.session_id!==session))return;\n"
    " if(armWait!==null&&performance.now()-offerAt>=200)cancelArmWait('제어 상태 수신 지연 · 수동 ARM 필요');\n"
    " session=r.session_id;\n"
    " const deadline=performance.now()+Math.max(0,r.ttl_ms-TICKET_SEND_MARGIN_MS);\n"
    " ticketDeadline=offer&&offer.ticket===r.ticket?Math.min(ticketDeadline,deadline):deadline;\n"
    " offer=r;offerAt=performance.now();\n"
    " control.textContent='제어 상태 · '+r.phase+' · 속도 0 전용';\n"
    " if(intent&&(['STOPPING','BLOCKED'].includes(r.phase)||(r.phase==='IDLE'&&controlId>0)))stopLocal(false);\n"
    " tryWaitingArm();\n"
    " updateButtons();\n"
    "}\n"
    "function validNotice(r){\n"
    " if(!r||r.kind!=='command_notice'||!u32(r.boot_id)||!u32(r.session_id)||!ownKey(noticeLabels,r.reason))return false;\n"
    " const identified=u32(r.request_id)&&r.request_id>0&&cmds.includes(r.cmd);\n"
    " if(r.stage==='ACCEPTED')return identified&&r.session_id>0&&r.reason==='QUEUED';\n"
    " return r.stage==='REJECTED'&&r.reason!=='QUEUED'&&(r.reason==='BAD_FORMAT'?r.request_id===null&&r.cmd===null:identified);\n"
    "}\n"
    "function handleNotice(r){\n"
    " if(boot===null||r.boot_id!==boot||(session!==null&&r.session_id!==session))return;\n"
    " if(r.stage==='ACCEPTED'&&r.request_id<=ignoredThrough)return;\n"
    " if(r.request_id!==null)nextId=Math.max(nextId,r.request_id+1);\n"
    " notice.textContent=(r.cmd===null?'명령':r.cmd+' 요청 '+r.request_id)+': '+\n"
    "  (r.stage==='ACCEPTED'?'접수됨 · ':'거부됨 · ')+noticeLabels[r.reason]+' ('+r.reason+')';\n"
    " if(pending&&r.request_id===pending.id&&r.cmd===pending.cmd){\n"
    "  if(r.stage==='ACCEPTED'){pending.accepted=true;pending.session=r.session_id;}\n"
    "  else if(!pending.accepted){\n"
    "   const wasControl=['ARM','CMD'].includes(pending.cmd);\n"
    "   ignoredThrough=Math.max(ignoredThrough,pending.id);clearPending();\n"
    "   if(wasControl)stopLocal(true);\n"
    "  }\n"
    " }\n"
    " updateButtons();\n"
    "}\n"
    "function validResult(r){\n"
    " return r&&r.kind==='command_result'&&u32(r.boot_id)&&u32(r.session_id)&&r.session_id>0&&\n"
    " u32(r.request_id)&&r.request_id>0&&u32(r.seq)&&u32(r.control_id)&&cmds.includes(r.cmd)&&ownKey(resultLabels,r.status)&&\n"
    " (!['ARM','CMD'].includes(r.cmd)||r.control_id>0);\n"
    "}\n"
    "function handleResult(r){\n"
    " if(boot===null||r.boot_id!==boot||r.request_id<=ignoredThrough||(session!==null&&r.session_id!==session))return;\n"
    " if(pending&&(r.request_id!==pending.id||r.cmd!==pending.cmd||\n"
    " (pending.session!==null&&r.session_id!==pending.session)||\n"
    " (r.cmd==='CMD'&&r.control_id!==pending.controlId)))return;\n"
    " const expected=pending!==null;\n"
    " clearPending();ignoredThrough=r.request_id;nextId=Math.max(nextId,r.request_id+1);\n"
    " notice.textContent='ESP 명령 처리 결과 수신';\n"
    " result.textContent='마지막 명령 결과 · '+r.cmd+' 요청 '+r.request_id+': '+resultLabels[r.status]+' ('+r.status+')';\n"
    " if(['ARM','CMD'].includes(r.cmd)){\n"
    "  if(r.status!=='OK')stopLocal(true);\n"
    "  else if(r.cmd==='ARM'&&intent&&expected)controlId=r.control_id;\n"
    " }\n"
    " updateButtons();\n"
    "}\n"
    "function validStatus(s){ const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295; const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647; const ms=v=>Number.isSafeInteger(v)&&v>=0; if(!s||typeof s!=='object'||Array.isArray(s)||    !['ESP_ONLY','STM_UART'].includes(s.source)||    !['AP','STA'].includes(s.mode)||    !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK',      'WAIT_PONG','READY','FAILED'].includes(s.startup_state)||    !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||    !u32(s.tel_count)||!u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||    typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||    s.batt_mv!==null||s.battery_available!==false)return false; if(s.source==='ESP_ONLY'){  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&   s.tel_count===0&&['stm_t_ms','state','reason','command_age_ms',   'last_seq','vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps','drop','err'].every(k=>s[k]===null); } return ms(s.stm_age_ms)&&  s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&  ['DISARMED','ARMED','FAULT'].includes(s.state)&&  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&  ['vx_mmps','w_mradps','left_pwm','right_pwm',   'left_cps','right_cps'].every(k=>i32(s[k]))&&  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000;}\n"
    "function scheduleReconnect(){if(retry===null)retry=setTimeout(()=>{retry=null;connect();},1000);}\n"
    "function disconnect(ws,reason){\n"
    " if(socket!==ws||ws===null)return;\n"
    " socket=null;boot=null;session=null;startupFinished=false;\n"
    " clearTimeout(watchdog);watchdog=null;resetControl();\n"
    " const p=pending;clearPending();\n"
    " result.textContent=p?p.cmd+' 요청 '+p.id+': 결과 확인 불가 · '+reason:reason+' · 새 명령 결과 수신 대기';\n"
    " notice.textContent='연결 끊김 · 명령 송신 대기';control.textContent='제어 연결 끊김 · 수동 ARM 필요';\n"
    " link.textContent=reason+' · 아래 값은 마지막 수신 데이터';stm.textContent='STM 상태 확인 불가 · 마지막 수신 데이터';\n"
    " startup.textContent='부팅 응답 확인 불가';updateButtons();ws.close();scheduleReconnect();\n"
    "}\n"
    "function armWatchdog(ws){clearTimeout(watchdog);watchdog=setTimeout(()=>disconnect(ws,'상태 수신 시간 초과'),4000);}\n"
    "function connect(){\n"
    " if(socket!==null)return;\n"
    " clearPending();resetControl();boot=null;session=null;startupFinished=false;nextId=1;ignoredThrough=0;nextPingAt=0;\n"
    " notice.textContent='새 연결 · 명령 송신 대기';result.textContent='새 연결 · 명령 결과 수신 대기';\n"
    " const ws=new WebSocket('ws://'+location.host+'/ws');socket=ws;armWatchdog(ws);updateButtons();\n"
    " ws.onopen=()=>{\n"
    "  if(socket!==ws)return;\n"
    "  link.textContent='연결됨 · 새 상태 수신 대기';\n"
    "  try{ws.send('HELLO');}catch(error){disconnect(ws,'연결 등록 실패');return;}\n"
    "  armWatchdog(ws);updateButtons();\n"
    " };\n"
    " ws.onmessage=event=>{\n"
    "  if(socket!==ws)return;\n"
    "  try{\n"
    "   const r=JSON.parse(event.data);\n"
    "   if(r&&r.kind==='control_state'){if(!validControl(r))throw Error('control');handleControl(r);return;}\n"
    "   if(r&&r.kind==='command_notice'){if(!validNotice(r))throw Error('notice');handleNotice(r);return;}\n"
    "   if(r&&r.kind==='command_result'){if(!validResult(r))throw Error('result');handleResult(r);return;}\n"
    "   if(!validStatus(r))throw Error('status');\n"
    "   if(boot!==r.boot_id){\n"
    "    if(boot!==null){disconnect(ws,'ESP 부팅 변경');return;}\n"
    "    boot=r.boot_id;result.textContent='이번 ESP 부팅의 명령 결과 수신 대기';\n"
    "   }\n"
    "   startupFinished=['READY','FAILED'].includes(r.startup_state);\n"
    "   if(armWait!==null&&(r.startup_state!=='READY'||r.source!=='STM_UART'||!r.stm_connected||\n"
    "      r.state!=='DISARMED'||r.vx_mmps!==0||r.w_mradps!==0||r.left_pwm!==0||r.right_pwm!==0))\n"
    "    cancelArmWait('STM ARM 조건 변경 · 수동 ARM 필요');\n"
    "   data.textContent=JSON.stringify(r,null,2);link.textContent='WebSocket 수신 정상 · '+new Date().toLocaleTimeString();\n"
    "   startup.textContent='이번 ESP 부팅의 응답 확인: '+r.startup_state;\n"
    "   stm.textContent=r.source==='ESP_ONLY'?'STM TEL 아직 수신 없음':r.stm_stale?\n"
    "    'STM TEL 수신 중단 · '+r.stm_age_ms+' ms · 아래 STM 값은 마지막 정상 TEL':'STM TEL 수신 정상 · '+r.state+' / '+r.reason;\n"
    "   armWatchdog(ws);updateButtons();\n"
    "  }catch(error){disconnect(ws,'잘못된 상태 응답');}\n"
    " };\n"
    " ws.onerror=()=>disconnect(ws,'WebSocket 오류');ws.onclose=()=>disconnect(ws,'연결 끊김');\n"
    "}\n"
    "ping.onclick=()=>sendCommand('PING');disarm.onclick=()=>sendCommand('DISARM');arm.onclick=requestArm;\n"
    "window.addEventListener('blur',()=>stopLocal(true));\n"
    "document.addEventListener('visibilitychange',()=>{if(document.hidden)stopLocal(true);});\n"
    "window.addEventListener('offline',()=>{if(socket!==null)disconnect(socket,'네트워크 연결 끊김');});\n"
    "window.addEventListener('online',()=>{clearTimeout(retry);retry=null;connect();});\n"
    "connect();\n"
    "\n"
    "</script></body></html>\n";
```

### 4-3. 통신 해제 시 주입 취소

`wifi_control_transport_lost` 함수 전체를 교체한다.

```c
static void wifi_control_transport_lost(void)
{
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    wifi_uart_test_cancel_locked();
    /* An unrelated read-only tab must not stop a different owner. This helper
     * is for loss of the whole transport; per-session loss uses closed(id). */
    if (s_control.state.owner.ws_session_id != 0U) {
        wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_OWNER_CLOSED, wifi_control_now());
    }
    s_wifi_command_owner_session_id = 0U;
    (void)xQueueReset(s_wifi_command_queue);
    wifi_control_cleanup_locked();
    xSemaphoreGive(s_stm_lock);
}
```


### 4-4. 명령 접수와 수동 정지 우선권

`wifi_command_admit_locked` 함수 전체를 교체한다.

```c
static const char *wifi_command_admit_locked(
    wifi_ws_session_t *session, wifi_command_request_t *request)
{
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (request->expected_boot_id != s_boot_id) return "BOOT_MISMATCH";
    if (request->request_id <= session->last_request_id) return "DUPLICATE";
    if (!wifi_control_ready_locked() && strcmp(s_stm_startup_status, "FAILED") != 0)
        return "STARTUP_PENDING";
    if (WIFI_UART_PARTIAL_TEST_MODE != 0U && request->type != WIFI_COMMAND_DISARM)
        return "BUSY"; /* Bench image: normal control stays disabled. */
    request->ws_session_id = session->id;
    request->accepted_ms = now;
    if (request->type == WIFI_COMMAND_DISARM) {
        /* Stop bypasses normal command rate/busy gates. One stop result slot. */
        if (s_manual_stop_pending) return "BUSY";
        wifi_uart_test_cancel_locked();
        s_manual_stop_request = *request;
        s_manual_stop_seq = 0U;
        s_manual_stop_pending = true;
        if (s_control.state.phase != WIFI_CONTROL_STOPPING) {
            wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP, now);
        } else if (s_control.state.pending == WIFI_CONTROL_OP_DISARM) {
            s_manual_stop_seq = s_control.state.pending_seq;
        } else if (s_control.state.stop_ack) {
            s_manual_stop_seq = s_control.state.confirm_seq;
        }
        wifi_control_cleanup_locked();
    } else if (request->type == WIFI_COMMAND_PING) {
        if (session->last_request_id != 0U && now - session->last_accepted_ms < WIFI_COMMAND_MIN_INTERVAL_MS)
            return "RATE_LIMIT";
        if (s_manual_stop_pending || s_wifi_command_owner_session_id != 0U ||
            !wifi_control_executor_allows_ping(&s_control)) return "BUSY";
        if (xQueueSend(s_wifi_command_queue, request, 0) != pdPASS) return "QUEUE_FULL";
        s_wifi_command_owner_session_id = session->id;
    } else if (request->type == WIFI_COMMAND_ARM || request->type == WIFI_COMMAND_CMD) {
        if (request->type == WIFI_COMMAND_CMD && session->have_cmd && now - session->last_cmd_ms < 50U)
            return "RATE_LIMIT";
        if (s_manual_stop_pending || s_wifi_command_owner_session_id != 0U) return "BUSY";
        request->control.ws_session_id = session->id;
        const wifi_control_submit_status_t status = wifi_control_executor_submit(
            &s_control, &request->control, &session->ticket,
            wifi_control_ready_locked(), true, now);
        wifi_control_cleanup_locked();
        switch (status) {
        case WIFI_EXEC_ACCEPTED: break;
        case WIFI_EXEC_BOOT_MISMATCH: return "BOOT_MISMATCH";
        case WIFI_EXEC_TICKET_REJECTED: return "TICKET_REJECTED";
        case WIFI_EXEC_NOT_READY: return "NOT_READY";
        case WIFI_EXEC_BUSY: case WIFI_EXEC_OUTPUT_PENDING: return "BUSY";
        default: return "BAD_INPUT";
        }
        if (request->type == WIFI_COMMAND_CMD) {
            session->have_cmd = true;
            session->last_cmd_ms = now;
        }
    } else return "BAD_INPUT";
    session->last_request_id = request->request_id;
    session->last_accepted_ms = now;
    return NULL;
}
```


### 4-5. 시험 이미지의 제어 ticket 차단

`wifi_control_snapshot` 함수 전체를 교체한다.

```c
static int wifi_control_snapshot(wifi_ws_session_t *session, char *json, size_t capacity)
{
    static const char *const phases[] = {"IDLE", "ARM_PENDING", "ZERO_PENDING", "ACTIVE", "STOPPING", "BLOCKED"};
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    const wifi_control_state_t *state = &s_control.state;
    const bool available = WIFI_UART_PARTIAL_TEST_MODE == 0U && !s_manual_stop_pending && s_wifi_command_owner_session_id == 0U &&
        !s_control.queued && !s_control.waiting && !s_control.prepared && !s_control.have_result;
    const bool fresh = state->have_tel && now >= state->tel_received_ms &&
        now - state->tel_received_ms < WIFI_CONTROL_TEL_MS;
    const bool zero = fresh && state->tel.vx_mmps == 0 && state->tel.w_mradps == 0 &&
        state->tel.left_pwm == 0 && state->tel.right_pwm == 0;
    const bool arm = available && wifi_control_ready_locked() && state->phase == WIFI_CONTROL_IDLE &&
        zero && state->tel.state == WIFI_CONTROL_STM_DISARMED;
    const bool cmd = available && (state->phase == WIFI_CONTROL_ZERO_PENDING || state->phase == WIFI_CONTROL_ACTIVE) &&
        state->owner.ws_session_id == session->id;
    if (!arm && !cmd) {
        wifi_control_ticket_invalidate(&session->ticket);
    } else {
        const wifi_control_type_t purpose = arm ? WIFI_CONTROL_ARM : WIFI_CONTROL_CMD;
        const uint32_t control_id = arm ? 0U : state->owner.control_id;
        if (session->ticket.purpose != purpose || session->ticket.control_id != control_id)
            wifi_control_ticket_invalidate(&session->ticket);
        (void)wifi_control_ticket_issue(&s_ticket_pool, &session->ticket, session->id, purpose, control_id, now);
    }
    const bool valid = session->ticket.valid && now < session->ticket.expires_ms;
    const uint32_t ttl = valid ? (uint32_t)(session->ticket.expires_ms - now) : 0U;
    const int length = snprintf(json, capacity,
        "{\"kind\":\"control_state\",\"boot_id\":%" PRIu32 ",\"session_id\":%" PRIu32
        ",\"phase\":\"%s\",\"owner_session\":%" PRIu32 ",\"control_id\":%" PRIu32
        ",\"ticket\":%" PRIu32 ",\"purpose\":\"%s\",\"ttl_ms\":%" PRIu32 ",\"zero_only\":true}",
        s_boot_id, session->id, phases[state->phase], state->owner.ws_session_id, state->owner.control_id,
        valid ? session->ticket.id : 0U, valid ? (arm ? "ARM" : "CMD") : "NONE", ttl);
    xSemaphoreGive(s_stm_lock);
    return length >= 0 && (size_t)length < capacity ? length : -1;
}
```


### 4-6. 수동 시험 HTTP 경로 등록

`server_start` 함수 전체를 교체한다.

```c
static void server_start(void)
{
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    if (s_server != NULL) {
        xSemaphoreGive(s_server_lock);
        return;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    config.max_open_sockets = WS_MAX_CLIENTS;
    config.lru_purge_enable = true;
    config.recv_wait_timeout = 2;
    config.send_wait_timeout = 2;
    ESP_ERROR_CHECK(httpd_start(&s_server, &config));

    const httpd_uri_t page_uri = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = page_get
    };

    const httpd_uri_t status_uri = {
        .uri = "/api/status",
        .method = HTTP_GET,
        .handler = status_get
    };

    const httpd_uri_t ws_uri = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = ws_receive,
        .is_websocket = true,
        .handle_ws_control_frames = false
    };

    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &page_uri));
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &status_uri));
    ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &ws_uri));
    if (WIFI_UART_PARTIAL_TEST_MODE != 0U) {
        const httpd_uri_t test_uri = {
            .uri = "/api/uart-partial-test", .method = HTTP_POST,
            .handler = wifi_uart_test_post
        };
        ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &test_uri));
        ESP_LOGW(TAG, "UART TEST IMAGE mode=%u: normal PING/ARM/CMD disabled",
                 (unsigned)WIFI_UART_PARTIAL_TEST_MODE);
    }
    atomic_store(&s_ws_work_pending, false);
    xSemaphoreGive(s_server_lock);

    esp_netif_ip_info_t info;
    ESP_ERROR_CHECK(esp_netif_get_ip_info(s_netif, &info));
    ESP_LOGI(TAG, "Open http://" IPSTR "/", IP2STR(&info.ip));
    ESP_LOGI(TAG, "WebSocket status: /ws, period=%u ms", WS_PERIOD_MS);
}
```


### 4-7. 시험 상태·입력·UART 단계

`static void wifi_control_step(void)` 바로 앞에 아래 블록 전체를 추가한다. 기존 `wifi_control_step` 내용은 유지한다. `UART_PARTIAL_TEST_BEGIN/END` 주석도 포함한다.

```c
/* UART_PARTIAL_TEST_BEGIN: all state is protected by s_stm_lock. */
typedef enum {
    UART_TEST_UNUSED, UART_TEST_QUEUED, UART_TEST_HOLD,
    UART_TEST_STOPPING, UART_TEST_DONE, UART_TEST_ABORTED
} uart_partial_test_phase_t;

static uart_partial_test_phase_t s_uart_test_phase;
static uint64_t s_uart_test_at_ms;
static bool s_uart_test_prefix_full;

static bool wifi_uart_test_ready_locked(uint64_t now)
{
    const wifi_control_state_t *s = &s_control.state;
    return wifi_control_ready_locked() && s->phase == WIFI_CONTROL_IDLE &&
        !s_manual_stop_pending && s_wifi_command_owner_session_id == 0U &&
        !s_control.queued && !s_control.waiting && !s_control.prepared &&
        !s_control.have_result && s->have_tel && now >= s->tel_received_ms &&
        now - s->tel_received_ms < WIFI_CONTROL_TEL_MS &&
        s->tel.state == WIFI_CONTROL_STM_DISARMED &&
        s->tel.vx_mmps == 0 && s->tel.w_mradps == 0 &&
        s->tel.left_pwm == 0 && s->tel.right_pwm == 0;
}

/* Reserve the prefix identity and ensure the next allocator call can still
 * provide a DISARM identity, including skipped startup-reserved values. */
static bool wifi_uart_test_sequence_locked(uint32_t *seq)
{
    if (!wifi_uart_allocate_seq(seq)) return false;
    while (s_wifi_uart_next_seq <= UINT32_MAX &&
        (s_wifi_uart_next_seq == s_stm_startup.disarm_seq ||
         s_wifi_uart_next_seq == s_stm_startup.ping_seq)) {
        ++s_wifi_uart_next_seq;
    }
    return s_wifi_uart_next_seq <= UINT32_MAX;
}

/* Manual stop / transport loss cancels a queued injection. A committed prefix
 * cannot be recalled; request the existing priority DISARM immediately. */
static void wifi_uart_test_cancel_locked(void)
{
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        s_uart_test_phase = UART_TEST_ABORTED;
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        s_uart_test_phase = UART_TEST_STOPPING;
        wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP,
                                   wifi_control_now());
        wifi_control_cleanup_locked();
    }
}

/* Body: decimal current boot_id only. HTTP queues; it never writes UART.
 * The 202 response means accepted, not prefix delivery or test success. */
static esp_err_t wifi_uart_test_post(httpd_req_t *req)
{
    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) {
        httpd_resp_set_status(req, "404 Not Found");
        return httpd_resp_sendstr(req, "DISABLED");
    }
    char body[11];
    if (req->content_len <= 0 || req->content_len >= sizeof(body)) {
        httpd_resp_set_status(req, "400 Bad Request");
        return httpd_resp_sendstr(req, "BAD_INPUT");
    }
    size_t used = 0U;
    while (used < req->content_len) {
        const int got = httpd_req_recv(req, body + used, req->content_len - used);
        if (got <= 0) return ESP_FAIL; /* No retry, no queued side effect. */
        used += (size_t)got;
    }
    body[used] = '\0';
    uint32_t boot = 0U;
    const char *cursor = body;
    if (memchr(body, '\0', used) != NULL ||
        !wifi_command_parse_u32(&cursor, &boot) || *cursor != '\0') {
        httpd_resp_set_status(req, "400 Bad Request");
        return httpd_resp_sendstr(req, "BAD_INPUT");
    }
    const char *error = NULL;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (boot != s_boot_id) error = "BOOT_MISMATCH";
    else if (s_uart_test_phase != UART_TEST_UNUSED) error = "ALREADY_USED";
    else if (!wifi_uart_test_ready_locked(now)) error = "NOT_READY";
    else {
        s_uart_test_phase = UART_TEST_QUEUED;
        s_uart_test_at_ms = now;
    }
    xSemaphoreGive(s_stm_lock);
    httpd_resp_set_status(req, error != NULL ? "409 Conflict" : "202 Accepted");
    return httpd_resp_sendstr(req, error != NULL ? error : "QUEUED; check UART log and capture");
}

/* Called only by stm_uart_rx_task, before normal control/command dispatch.
 * Fixed prefix -> 100 ms receive/poll interval -> existing CAN+LF DISARM.
 * No raw input, no LF-only flush, no retry, no new UART writer task. */
static void wifi_uart_test_step(void)
{
    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) return;
    char prefix[32];
    int length = 0;
    uint32_t seq = 0U;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        if (now < s_uart_test_at_ms || now - s_uart_test_at_ms >= WIFI_CONTROL_QUEUE_MS ||
            !wifi_uart_test_ready_locked(now) || !wifi_uart_test_sequence_locked(&seq)) {
            s_uart_test_phase = UART_TEST_ABORTED;
            ESP_LOGW(TAG, "UART TEST: not sent (expired/not ready/sequence exhausted)");
        } else {
            length = WIFI_UART_PARTIAL_TEST_MODE == 1U ?
                snprintf(prefix, sizeof(prefix), "CMD,seq=") :
                snprintf(prefix, sizeof(prefix), "ARM,seq=%" PRIu32, seq);
            /* The fixed strings plus uint32_t always fit prefix[32]. */
            s_uart_test_phase = UART_TEST_HOLD;
            s_uart_test_at_ms = now;
        }
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        if (!wifi_uart_test_ready_locked(now) || now < s_uart_test_at_ms ||
            now - s_uart_test_at_ms >= 100U) {
            s_uart_test_phase = UART_TEST_STOPPING;
            wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP, now);
            wifi_control_cleanup_locked();
        }
    } else if (s_uart_test_phase == UART_TEST_STOPPING) {
        if (s_control.state.phase == WIFI_CONTROL_IDLE ||
            s_control.state.phase == WIFI_CONTROL_BLOCKED) {
            s_uart_test_phase = UART_TEST_DONE;
            ESP_LOGI(TAG, "UART TEST: end prefix_full=%u stop_confirmed=%u; capture review required",
                     s_uart_test_prefix_full ? 1U : 0U,
                     s_control.state.phase == WIFI_CONTROL_IDLE ? 1U : 0U);
        }
    }
    xSemaphoreGive(s_stm_lock);
    if (length <= 0) return;

    /* Commit point is above, under the lock, just like executor take_tx.
     * A concurrent DISARM may cancel the hold, but cannot retract these bytes. */
    const int written = uart_write_bytes(STM_UART_PORT, prefix, (size_t)length);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_uart_test_prefix_full = written == length;
    if (s_uart_test_phase == UART_TEST_HOLD) {
        s_uart_test_at_ms = wifi_control_now();
        if (!s_uart_test_prefix_full) wifi_uart_test_cancel_locked();
    }
    xSemaphoreGive(s_stm_lock);
    ESP_LOGI(TAG, "UART TEST: mode=%u reserved_seq=%" PRIu32 " prefix=%s written=%d/%d NO_LF",
             (unsigned)WIFI_UART_PARTIAL_TEST_MODE, seq, prefix, written, length);
}
/* UART_PARTIAL_TEST_END */
```


### 4-8. 기존 UART 태스크에 연결

`static void stm_uart_rx_task(void *arg)` 함수 전체를 교체한다. 별도 태스크를 만들지 않는다.

```c
static void stm_uart_rx_task(void *arg)
{
    (void)arg;
    uint8_t bytes[64];

    stm_startup_begin();
    stm_startup_publish_status();

    /* 사용자 요청 seq는 부팅용 PING 다음 값부터 시작한다. */
    s_wifi_uart_next_seq = (uint32_t)(s_stm_startup.ping_seq + 1U);

    for(;;) {
        stm_startup_step((uint64_t)esp_timer_get_time() / 1000U);
        wifi_uart_test_step();
        wifi_control_step();
        wifi_command_step();

        const int count = uart_read_bytes(
            STM_UART_PORT, bytes, sizeof(bytes),
            pdMS_TO_TICKS(20)
        );

        if (count < 0) {
            wifi_control_transport_lost();
            wifi_command_finish("RX_ERROR");
            stm_startup_fail("UART read failed");
            stm_startup_publish_status();
            s_stm_rx_length = 0U;
            s_stm_discard_until_lf = true;
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        for (int i = 0; i < count; ++i) {
            stm_uart_handle_byte(bytes[i]);
        }

        stm_startup_step((uint64_t)esp_timer_get_time() / 1000U);
        stm_startup_publish_status();
        wifi_uart_test_step();
        wifi_control_step();
        wifi_command_step();
    }
}
```


## 5. 입력 후 확인과 완료 상태

**10/16 후속 완료:** 최초 PAGE 누락은 사용자 직접 수정 위임으로 Codex가 4-2 전체 블록을 복원했다. 실제 저장본 PAGE C/HTML mode0·1·2와 제어/주입 PC 검사를 통과했고, 사용자 mode1/2 실물 시험 및 mode0 일반 이미지 복원까지 완료했다. [보고서36](../verification/36_UART_Line_Cancel_Recovery_2026-10-16_ko.md), [복원 관측](../../assets/logs/wifi_link/2026-10-16_uart_partial_normal_restore/observations.json).

현재 기본값은0U다. 이미 복원된 PAGE나 시험 블록을 다시 입력하지 않는다. 아래 절차·코드는 재현용 이력이며 지금 반복 실행할 지시가 아니다. SDK 전체 빌드·실제 UART 관측은 PC 검사와 구분한다.

입력 전 후보 검사 근거:

- [PC 검사 출력](../../assets/logs/wifi_link/2026-10-16_uart_partial_candidate/pc_results.txt): 기본 비활성 경로·기존 W5/main 42개, mode1/2 실제 STM 파서 연결, 입력 거부·기한·정지 경합·실패 경로.
- [소스 manifest](../../assets/logs/wifi_link/2026-10-16_uart_partial_candidate/source_manifest.json): 검사 기준과 해시.
- [검토 후보 전체 C](../../assets/logs/wifi_link/2026-10-16_uart_partial_candidate/wifi_link_main.c): 비교용. 실제 펌웨어에는 자동 적용하지 않았다.

LF-only로 바꿔 보내는 PC 반례에서는 오래된 ARM ACK가 나오는 것도 확인했다. 이로써 마지막 정지만 보는 검사로는 누락되는 실행을 구분한다. PC 검사는 SDK 전체 빌드, FreeRTOS 실스케줄링, 실제 UART 신호와 전기 출력을 증명하지 않는다.

## 6. 실물 시험 절차 — mode1/2 및 mode0 복원 완료

저장본 검사와 사용자 빌드가 끝난 뒤 배선·전원 변경 여부부터 확인한다. 전제는 드라이버 B+ 분리·절연, #1 두 보드 전원 플러그 분리, 기존 정상 E-stop 감지 조건, 보드 USB 공급과 UART 공통 GND, D0~D3 양끝 측정이다. 마지막 전원 기록을 현재 상태로 추정하지 않고 사용자 확인 후 한 시험씩 진행한다.

1. **부분 CMD:** mode1 사용자 빌드·플래시 → 새 boot/시험 이미지 표시 및 READY/IDLE·fresh DISARMED/zero 확인 → LA 캡처 시작 → 수동 POST 한 번 → 원본 저장.
2. **LF 없는 ARM:** 첫 결과를 검토한 뒤 mode2 사용자 빌드·플래시와 새 boot 확인 → 같은 방식의 한 번 주입 → 별도 저장.
3. 마감 때 **mode0 정상 이미지로 사용자 빌드·플래시하고 복원 확인**한다. 시험 이미지에서는 일반 무선 제어를 재개하지 않는다.

아래는 해당 시험 시작을 안내받은 뒤 브라우저 콘솔에서 실행할 수동 요청이다.

```javascript
(async () => {
  const status = await fetch('/api/status', {cache: 'no-store'});
  if (!status.ok) throw new Error('상태 조회 실패');
  const robot = await status.json();
  const response = await fetch('/api/uart-partial-test', {
    method: 'POST',
    headers: {'Content-Type': 'text/plain'},
    body: String(robot.boot_id)
  });
  console.log(response.status, await response.text());
})();
```

실물 PASS는 다음을 함께 확인한다.

- D3/D1의 prefix가 의도대로 같고 끝 LF가 없다. 이어서 `18 0A`와 첫 DISARM의 완전한 seq/LF가 일치한다.
- D0/D2에 남은 ARM/CMD의 ACK·실행 흔적과 추가 ERR가 없다. 마지막 정지 화면으로 이 조건을 대체하지 않는다.
- 첫 새 DISARM의 정확한 ACK와 이후 같은 seq의 새 정지 TEL이 도착하며 자동 ARM/CMD 재전송이 없다.
- `UART TEST: end prefix_full=1 stop_confirmed=1`과 IDLE을 확인한다. 이 로그는 송신 반환 길이와 executor 정지 확인이며, 캡처 검토를 대신하는 시험 전체 PASS가 아니다.
- 추가 오류·예상 밖 ARMED/출력·BLOCKED가 나오면 원본부터 보존하고 반복 주입하지 않는다. 수동 정지 복구는 별도 안내한다.

이번 범위는 UART 명령 폐기와 정지 확인이다. 실제 PWM/PC7, 모터 전력 차단·정지 거리, 전체 AC-S는 별도다. 합성 시험으로 원래 실패 당시의 미확보 잔여 바이트를 소급 확정하지 않는다.
