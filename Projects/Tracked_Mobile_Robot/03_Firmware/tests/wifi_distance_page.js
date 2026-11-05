// Inserted into the embedded PAGE; no direct hardware or network access here.
const distanceButtons=[50,100,150,200].map(mm=>byId('distance_'+mm));
const distanceButton=byId('distance_move'),distanceHint=byId('distance_hint');
let distanceGoal=50,distanceArmSeq=null,distanceStill=null,distanceTrial=null,distanceRunsDropped=0;
const distanceRuns=[];
function distanceZero(r){
 return r.vx_mmps===0&&r.w_mradps===0&&r.left_pwm===0&&r.right_pwm===0&&r.left_cps===0&&r.right_cps===0;
}
function distanceSample(r){
 return r!==null&&r.source==='STM_UART'&&r.startup_state==='READY'&&r.stm_connected&&!r.stm_stale&&
  r.stm_age_ms<250&&r.encoder_valid&&r.encoder_arm_valid&&distanceArmSeq!==null&&r.encoder_arm_seq===distanceArmSeq;
}
function distancePoint(r){
 return {ms:performance.now(),tel_count:r.tel_count,stm_t_ms:r.stm_t_ms,encoder_t_ms:r.encoder_t_ms,
  encoder_arm_seq:r.encoder_arm_seq,last_seq:r.last_seq,state:r.state,reason:r.reason,
  command:[r.vx_mmps,r.w_mradps],pwm:[r.left_pwm,r.right_pwm],cps:[r.left_cps,r.right_cps],
  left_count:r.left_count,right_count:r.right_count,stm_age_ms:r.stm_age_ms,drop:r.drop,err:r.err};
}
function distanceInterrupt(reason){
 if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'){
  distanceTrial.phase='ABORTED';distanceTrial.stop_reason=reason;distanceTrial.stop_ms=performance.now();
 }
}
function distanceReset(){
 distanceInterrupt('CONTROL_RESET');distanceArmSeq=null;distanceStill=null;distanceTrial=null;
}
function distanceReady(){
 const now=performance.now();
 return distanceTrial===null&&motionReady()&&!releaseZero&&
  distanceSample(latestTel)&&distanceZero(latestTel)&&distanceStill!==null&&distanceStill.span>=100&&
  now-distanceStill.rx+latestTel.stm_age_ms<250;
}
function distanceStartExpired(){
 return distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&distanceTrial.first_goal_sent_ms===null&&
  performance.now()-distanceTrial.started_ms>=200;
}
function distanceStart(){
 distanceTrial={goal_mm:distanceGoal,boot_id:boot,control_id:controlId,arm_seq:distanceArmSeq,
  phase:'RUNNING',started_ms:performance.now(),first_goal_sent_ms:null,baseline:distancePoint(latestTel),
  accepted_seqs:[],samples:[],samples_dropped:0,cutoff:null,final:null};
 distanceRuns.push(distanceTrial);if(distanceRuns.length>16){distanceRuns.shift();++distanceRunsDropped;}
}
function distanceObserve(r){
 if(!distanceSample(r)){
  distanceStill=null;
  if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'){
   distanceInterrupt('ENCODER_OR_ARM_INVALID');stopLocal(true);
  }
  return;
 }
 if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&distanceTrial.first_goal_sent_ms===null&&
    (!distanceZero(r)||r.left_count!==distanceTrial.baseline.left_count||r.right_count!==distanceTrial.baseline.right_count)){
  distanceInterrupt('START_NOT_STILL');stopLocal(true);return;
 }
 const now=performance.now(),old=distanceStill;
 const generation=old===null?1:(r.tel_count-old.tel_count)>>>0;
 if(old===null||generation!==0){
  const step=old===null?0:(r.encoder_t_ms-old.encoder_t_ms)>>>0;
  const stmStep=old===null?0:(r.stm_t_ms-old.stm_t_ms)>>>0;
  const continuous=old!==null&&generation<2147483648&&step>0&&step<=500&&stmStep>0&&stmStep<=500&&now-old.rx<250;
  const same=continuous&&distanceZero(r)&&old.zero&&r.left_count===old.left&&r.right_count===old.right;
  distanceStill={tel_count:r.tel_count,encoder_t_ms:r.encoder_t_ms,stm_t_ms:r.stm_t_ms,rx:now,
   left:r.left_count,right:r.right_count,zero:distanceZero(r),span:same?old.span+step:0};
  if(old!==null&&!continuous&&distanceTrial!==null&&distanceTrial.phase==='RUNNING'){
   distanceInterrupt('ENCODER_OR_TEL_DISCONTINUITY');stopLocal(true);return;
  }
  if(distanceTrial!==null){
   distanceTrial.samples.push(distancePoint(r));
   if(distanceTrial.samples.length>240){distanceTrial.samples.shift();++distanceTrial.samples_dropped;}
   if(distanceTrial.phase!=='RUNNING'&&distanceTrial.phase!=='STILL_OBSERVED')distanceTrial.final=distancePoint(r);
   if(distanceTrial.phase==='STILL_OBSERVED'&&
      (r.left_count!==distanceTrial.final.left_count||r.right_count!==distanceTrial.final.right_count))
    distanceTrial.post_still_count_changed=true;
  }
 }
 // ACK may arrive after its TEL. Recheck the latest TEL when its seq becomes known.
 if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'&&r.reason==='DISTANCE_REACHED'&&
    r.state==='ARMED'&&r.vx_mmps===0&&r.w_mradps===0&&r.left_pwm===0&&r.right_pwm===0&&
    distanceTrial.accepted_seqs.includes(r.last_seq)){
  distanceTrial.phase='CUTOFF';distanceTrial.cutoff=distancePoint(r);
  distanceTrial.stop_reason='DISTANCE_REACHED';distanceTrial.final=distancePoint(r);
  stopLocal(true);
 }
 if(distanceTrial!==null&&distanceTrial.phase==='CUTOFF'&&distanceStill!==null&&distanceStill.span>=200){
  distanceTrial.phase='STILL_OBSERVED';distanceTrial.final=distancePoint(r);
 }
}
function distanceUpdate(){
 const choose=connected()&&!intent&&pending===null&&offer!==null&&offer.phase==='IDLE';
 for(const button of distanceButtons){
  button.disabled=!choose;
  button.textContent=(Number(button.id.slice(9))===distanceGoal?'● ':'')+(Number(button.id.slice(9))/10)+' cm';
 }
 const held=motion!==null&&motion.distance_mm>0;
 distanceButton.disabled=!held&&!distanceReady();
 byId('distance_report').disabled=intent||distanceRuns.length===0;
 distanceHint.textContent=distanceTrial===null?
  (distanceReady()?'거리 '+distanceGoal/10+' cm · 누르는 동안 실행':'거리 '+distanceGoal/10+' cm · ARM 후 정지 상태 확인 대기'):
  distanceTrial.phase==='RUNNING'?'거리 '+distanceTrial.goal_mm/10+' cm 실행 중 · 놓으면 중단':
  distanceTrial.phase==='CUTOFF'?'목표 count 도달·출력 차단 · 정지 관측 중 · 다음 시험은 새 ARM':
  distanceTrial.phase==='STILL_OBSERVED'?(distanceTrial.post_still_count_changed?
   '정지 관측 뒤 count 변경 · 기록과 실측 구간 확인 필요':'정지 TEL 관측 · 좌우 링크 실측 필요 · 다음 시험은 새 ARM'):
  '거리 시험 중단 ('+distanceTrial.stop_reason+') · 다음 시험은 새 ARM';
}
function distanceReport(){
 return {version:1,kind:'airborne_distance_trials',coefficient_mm_per_count:'1687/19500',
  note:'TEL baseline/cutoff/final observations; measure actual left/right link travel separately',runs_dropped:distanceRunsDropped,runs:distanceRuns};
}
window.g6DistanceObserve={report:()=>JSON.stringify(distanceReport(),null,2)};
async function copyDistanceReport(){
 if(intent||distanceRuns.length===0)return;
 const text=window.g6DistanceObserve.report(),field=byId('distance_data'),status=byId('distance_copy_status');
 field.hidden=true;status.textContent='거리 기록 복사 중';
 if(window.isSecureContext&&navigator.clipboard&&typeof navigator.clipboard.writeText==='function'){
  try{
   await navigator.clipboard.writeText(text);
   status.textContent='거리 기록 복사 완료 · 채팅에 붙여넣으세요';return;
  }catch(error){/* HTTP or permission restrictions: try selected-text copy below. */}
 }
 // A delayed permission failure must not steal focus from a new motion session.
 if(intent){status.textContent='복사 실패 · 정지 후 다시 눌러주세요';return;}
 field.value=text;field.hidden=false;field.focus({preventScroll:true});field.select();
 field.setSelectionRange(0,text.length);
 let copied=false;
 // Compatibility path for the robot's plain HTTP page; browser support varies.
 try{copied=document.execCommand('copy');}catch(error){/* Leave all text selected. */}
 if(copied){
  field.hidden=true;byId('distance_report').focus({preventScroll:true});
  status.textContent='거리 기록 복사 완료 · 채팅에 붙여넣으세요';
 }else{
  status.textContent='자동 복사 실패 · 아래 전체 선택된 기록을 Ctrl+C 또는 복사 메뉴로 복사하세요';
 }
}
byId('distance_report').onclick=copyDistanceReport;
for(const button of distanceButtons)button.onclick=()=>{
 if(button.disabled)return;distanceGoal=Number(button.id.slice(9));updateButtons();
};
