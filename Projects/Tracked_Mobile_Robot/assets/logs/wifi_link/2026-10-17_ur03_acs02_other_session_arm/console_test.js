// Normal firmware, READY / IDLE / DISARMED, motor power isolated.
// Install in ONE robot page. B is an internal WebSocket; installation sends HELLO.
// After READY and LA capture start, manually click page ARM once; keep focus.
// B attempts ARM once with its last IDLE ticket. Never retries ARM or sends CMD.
(() => {
  'use strict';
  if (window.ur03OtherArm) throw Error('이미 설치됨. 새 회차는 새로고침 후 준비하세요.');
  if (typeof connected !== 'function' || !connected() || !session || intent || pending ||
      !offer || offer.phase !== 'IDLE') throw Error('먼저 READY / IDLE을 확인하세요.');
  const initial = JSON.parse(data.textContent);
  const zero = r => r && r.source === 'STM_UART' && r.startup_state === 'READY' &&
    r.stm_connected === true && r.stm_stale === false && Number.isFinite(r.stm_age_ms) &&
    r.stm_age_ms >= 0 && ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k => r[k] === 0);
  if (!zero(initial) || initial.stm_age_ms >= 250 || initial.state !== 'DISARMED')
    throw Error('fresh DISARMED / 출력 0이 필요합니다.');
  const a = socket, expectedBoot = boot, aSession = session;
  const b = new WebSocket('ws://' + location.host + '/ws');
  const started = performance.now(), events = [], timers = new Set(), beforeCmd = new Set(), afterCmd = new Set();
  let stage = 'waiting', done = false, problem = null, readyLogged = false;
  let bSession = null, aOffer = offer, aAt = started, bOffer = null, bAt = -Infinity, savedArmTicket = null;
  let latest = initial, telAt = started, ownerControl = null, armOk = false, target = null;
  let rejected = false, activeAfter = false, proofScheduled = false, replyTimer = null, runTimer = null;
  let stopId = null, stopSeq = null, stopAccepted = false, stopIdle = false, proofComplete = false;
  const phaseKeys = {A:null,B:null};
  const pageSame = () => socket === a && boot === expectedBoot && session === aSession && connected();
  const fresh = () => zero(latest) && latest.stm_age_ms + performance.now() - telAt < 250;
  const peers = () => pageSame() && b.readyState === WebSocket.OPEN && bSession && bSession !== aSession &&
    performance.now() - aAt < 250 && performance.now() - bAt < 250;
  const idle = r => r && r.phase === 'IDLE' && r.owner_session === 0 && r.control_id === 0;
  const owns = r => r && r.phase === 'ACTIVE' && r.owner_session === aSession && r.control_id === ownerControl;
  function log(event, details = {}) {
    const entry = {ms:+(performance.now()-started).toFixed(3),event,...details}; events.push(entry);
    if (event !== 'TEL') console.log('AC-S02 OTHER ARM ' + event, JSON.stringify(entry));
  }
  function later(fn,ms) {
    const id=setTimeout(()=>{timers.delete(id);if(!done)fn();},ms);timers.add(id);return id;
  }
  function cancel(id) { clearTimeout(id);timers.delete(id); }
  function finish(stopConfirmed) {
    if(done)return;done=true;for(const id of timers)clearTimeout(id);timers.clear();
    a.removeEventListener('message',onA);a.removeEventListener('close',onAClose);
    b.onopen=b.onmessage=b.onclose=b.onerror=null;b.close();
    const ok=!problem && rejected && activeAfter && afterCmd.size>=2 && proofComplete && stopConfirmed;
    stage=ok?'APP_CHECKS_OK_CAPTURE_REQUIRED':'INCOMPLETE';
    log(stage,{problem,rejected,activeAfter,post_rejection_cmd_seqs:[...afterCmd],proofComplete,stopConfirmed,stopSeq});
    console.log('결과 복사: copy(ur03OtherArm.report())');
  }
  function stop(reason) {
    if(done || stage==='stopping')return;
    stage='stopping';cancel(replyTimer);cancel(runTimer);
    log('A_DISARM_REQUEST',{reason});later(()=>finish(false),3500);
    try {
      if(pageSame()) { sendCommand('DISARM');stopId=pending && pending.cmd==='DISARM'?pending.id:null; }
      else if(b.readyState===WebSocket.OPEN) b.send('DISARM,boot_id='+expectedBoot+',request_id=2');
    } catch { log('STOP_SEND_FAILED'); }
  }
  function abort(reason) {
    if(done)return;problem=problem||reason;log('ABORT',{reason});
    if(stage==='waiting' && !intent && latest.state==='DISARMED')finish(false);else stop(reason);
  }
  function begin() {
    if(stage!=='waiting')return;stage='running';log('A_MANUAL_ARM_OBSERVED',{session:aSession});
    if(!readyLogged || !peers()) { abort('B 준비 전 ARM 또는 연결 이탈');return; }
    runTimer=later(()=>abort('6초 내 거부 및 A 유지 증거 미확보'),6000);
  }
  function verify() {
    if(done || stage==='waiting' || stage==='stopping')return;
    if(!peers() || !fresh() || !focused() || latest.state==='FAULT' ||
        latest.stm_t_ms<initial.stm_t_ms || latest.drop!==initial.drop || latest.err!==initial.err) {
      abort('연결/포커스/fresh TEL/출력/STM 부팅/오류 조건 이탈');return;
    }
    if(target && (!owns(aOffer) || !owns(bOffer) || !intent || controlId!==ownerControl || latest.state!=='ARMED'))
      abort('B ARM 시험 중 A 소유권 또는 ARMED 유지 실패');
  }
  function probe() {
    if(stage!=='running' || !armOk || beforeCmd.size<2 || !savedArmTicket || !peers() || !fresh() ||
        !focused() || !intent || pending || latest.state!=='ARMED' || !owns(aOffer) || !owns(bOffer) ||
        controlId!==ownerControl || bOffer.purpose!=='NONE' || bOffer.ticket!==0)return;
    target={request:1,ticket:savedArmTicket.ticket,control_id:ownerControl,
      ticket_captured_ms:savedArmTicket.ms,ticket_age_ms:performance.now()-started-savedArmTicket.ms,
      advertised_ttl_ms:savedArmTicket.ttl_ms,last_a_cmd_seq:[...beforeCmd].at(-1)};
    stage='probing';
    const text='ARM,boot_id='+expectedBoot+',request_id=1,ticket='+target.ticket;
    log('B_ARM_TX',{A:aSession,B:bSession,target,text,a_offer:aOffer,b_offer:bOffer,latest});
    replyTimer=later(()=>abort('B ARM 거부 응답 1500ms 초과'),1500);
    try { b.send(text); } catch { abort('B ARM 송신 실패'); }
  }
  function checkProof() {
    if(stage==='stopping') {
      if(stopAccepted && stopSeq!==null && stopIdle && pageSame() && fresh() && latest.state==='DISARMED' &&
          latest.reason==='DISARM' && latest.last_seq===stopSeq && !intent && controlId===0)finish(true);
      return;
    }
    if(stage!=='observing' || !rejected || !activeAfter || afterCmd.size<2 || !afterCmd.has(latest.last_seq) ||
        !peers() || !fresh() || !owns(aOffer) || !owns(bOffer) || latest.state!=='ARMED' || proofScheduled)return;
    proofScheduled=true;log('A_STILL_ACTIVE',{session:aSession,control_id:ownerControl,cmd_seqs:[...afterCmd],latest});
    later(()=>{verify();if(stage==='observing' && !problem){proofComplete=true;stop('시험 종료');}},1000);
  }
  function controlLog(who,r) {
    const key=[r.phase,r.owner_session,r.control_id].join(':');
    if(phaseKeys[who]!==key){phaseKeys[who]=key;log(who+'_CONTROL_STATE',{data:r});}
  }
  function onA(event) {
    if(done)return;let r;try{r=JSON.parse(event.data);}catch{abort('A JSON 오류');return;}
    if(!pageSame() || r.boot_id!==expectedBoot || (r.session_id!==undefined && r.session_id!==aSession)) {
      abort('A 식별 변경');return;
    }
    if(r.kind==='control_state') {
      aOffer=r;aAt=performance.now();controlLog('A',r);
      if(['ARM_PENDING','ZERO_PENDING','ACTIVE'].includes(r.phase) && r.owner_session===aSession)begin();
      if(stage==='stopping')stopIdle=idle(r);
      else if(stage!=='waiting' && ['STOPPING','BLOCKED','IDLE'].includes(r.phase)) {
        const preArm=r.phase==='IDLE' && !armOk && intent && controlId===0 && pending && pending.cmd==='ARM';
        if(!preArm){abort('예정 정리 전 A 제어 종료: '+r.phase);return;}
      }
      if(rejected && owns(r))activeAfter=true;
    } else if(r.source==='STM_UART') { latest=r;telAt=performance.now();log('TEL',{data:r}); }
    else if(r.kind==='command_notice' || r.kind==='command_result') {
      log('A_'+r.kind.toUpperCase(),{data:r});
      if(r.cmd==='ARM' && r.kind==='command_notice' && r.stage==='ACCEPTED')begin();
      if(stage==='stopping') {
        if(r.cmd==='DISARM' && r.request_id===stopId) {
          if(r.kind==='command_notice') {
            if(r.stage!=='ACCEPTED' || r.reason!=='QUEUED'){problem=problem||'정리 DISARM 거부';finish(false);return;}
            stopAccepted=true;
          } else {
            if(r.status!=='OK' || !Number.isInteger(r.seq) || r.seq<=0 || r.seq>4294967295 || r.control_id!==0) {
              problem=problem||'정리 DISARM 실패';finish(false);return;
            }
            stopSeq=r.seq;
          }
        }
      } else if(stage!=='waiting') {
        if(r.cmd==='DISARM' || (r.kind==='command_notice' && r.stage==='REJECTED')) { abort('관측 완료 전 A 명령 거부/정지');return; }
        if(r.kind==='command_result' && ['ARM','CMD'].includes(r.cmd)) {
          if(r.status!=='OK'){abort('A 제어 명령 실패: '+r.status);return;}
          if(r.cmd==='ARM') {
            if(armOk){abort('A ARM 반복');return;}armOk=true;ownerControl=r.control_id;
          } else if(armOk && r.control_id===ownerControl) {
            if(rejected)afterCmd.add(r.seq);else beforeCmd.add(r.seq);
          } else {abort('A CMD control_id 불일치');return;}
        }
      }
    }
    verify();probe();checkProof();
  }
  function onB(event) {
    if(done)return;let r;try{r=JSON.parse(event.data);}catch{abort('B JSON 오류');return;}
    if(r.boot_id!==expectedBoot){abort('B boot 변경');return;}
    if(r.kind==='control_state') {
      if(!bSession)bSession=r.session_id;
      if(!bSession || bSession===aSession || r.session_id!==bSession){abort('B session 변경');return;}
      bOffer=r;bAt=performance.now();controlLog('B',r);
      if(stage==='waiting' && idle(r) && r.purpose==='ARM' && Number.isInteger(r.ticket) && r.ticket>0)
        savedArmTicket={ticket:r.ticket,ttl_ms:r.ttl_ms,ms:performance.now()-started};
    } else if(r.kind==='command_notice' || r.kind==='command_result') {
      log('B_'+r.kind.toUpperCase(),{data:r});
      if(stage==='stopping')return;
      if(stage!=='probing' || !target || r.session_id!==bSession || r.request_id!==1 || r.cmd!=='ARM' ||
          r.kind!=='command_notice' || r.stage!=='REJECTED' || r.reason!=='TICKET_REJECTED') {
        abort(r.reason==='BUSY'?'B ARM은 BUSY로 거부됨: ticket/owner 거부 증거는 미확보':'B ARM이 예상한 ticket 거부와 다름');return;
      }
      rejected=true;cancel(replyTimer);stage='observing';log('B_ARM_REJECTED',{ticket:target.ticket});
    }
    if(!readyLogged && stage==='waiting' && peers() && fresh() && idle(aOffer) && idle(bOffer) &&
        latest.state==='DISARMED' && savedArmTicket && !intent && !pending) {
      readyLogged=true;log('READY',{boot:expectedBoot,A:aSession,B:bSession});
      console.log('캡처 시작 후 페이지 ARM을 한 번 누르고 그대로 기다리세요. 별도 탭 불필요.');
    }
    verify();probe();checkProof();
  }
  function onAClose(){abort('A 연결 종료');}
  function watch(){verify();probe();checkProof();if(!done)later(watch,50);}
  a.addEventListener('message',onA);a.addEventListener('close',onAClose);
  b.onopen=()=>{try{b.send('HELLO');}catch{abort('B 등록 실패');}};
  b.onmessage=onB;b.onclose=()=>abort('B 연결 종료');b.onerror=()=>abort('B 연결 오류');
  window.ur03OtherArm={cancel:()=>abort('사용자 취소'),report:()=>JSON.stringify({
    test:'UR03_ACS02_NON_OWNER_ARM_REJECTION',stage,boot:expectedBoot,A:aSession,B:bSession,
    owner_control_id:ownerControl,target,problem,initial,events
  },null,2)};
  later(()=>{if(stage==='waiting')abort('ARM 대기 120초 종료');},120000);
  watch();log('INSTALLED',{message:'자동 A ARM 없음. B READY 대기 중.'});
})();
