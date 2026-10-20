#include <stdlib.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "driver/uart.h"

#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "nvs_flash.h"

#include "wifi_link_config.h"
#include "wifi_control_executor.h"

#if WIFI_LINK_USE_AP != 0 && WIFI_LINK_USE_AP != 1
#error "WIFI_LINK_USE_AP must be 0 or 1"
#endif

#if !CONFIG_HTTPD_WS_SUPPORT
#error "Enable HTTPD_WS_SUPPORT in menuconfig"
#endif

#if WIFI_LINK_USE_AP
#define WIFI_LINK_MODE_NAME "AP"
#else
#define WIFI_LINK_MODE_NAME "STA"
static unsigned s_retry_count;
#endif

#define STATUS_JSON_SIZE 1024U
/* 0: normal image; 1: partial CMD; 2: ARM without LF; 3: CMD_TIMEOUT / NOT_ARMED.
 * Test images reject normal PING/ARM/CMD for the entire boot.
 * One manual POST per boot; never inject automatically at startup. */
#define WIFI_UART_PARTIAL_TEST_MODE 0U
#if WIFI_UART_PARTIAL_TEST_MODE > 3U
#error "WIFI_UART_PARTIAL_TEST_MODE must be 0, 1, 2 or 3"
#endif
#if WIFI_UART_PARTIAL_TEST_MODE == 3U
#define WIFI_UART_PARTIAL_TEST_BANNER \
    "<p><strong>AC-S06 시간초과 시험 이미지</strong> · 제어 IDLE과 별도로 시험 UART 동작 · 일반 PING/ARM/CMD 비활성 · 수동 DISARM 가능</p>"
#elif WIFI_UART_PARTIAL_TEST_MODE != 0U
#define WIFI_UART_PARTIAL_TEST_BANNER \
    "<p><strong>UART 부분 명령 시험 이미지</strong> · 일반 PING/ARM/CMD 비활성 · 수동 DISARM 가능</p>"
#else
#define WIFI_UART_PARTIAL_TEST_BANNER ""
#endif

static esp_err_t wifi_uart_test_post(httpd_req_t *req);
static void wifi_uart_test_cancel_locked(void);

#define WS_MAX_CLIENTS 4U
#define WS_PERIOD_MS 50U
#define CONTROL_PUMP_MS 20U
#define STM_TEL_STALE_MS 500U

static const char *TAG = "wifi_link";
static httpd_handle_t s_server;
static esp_netif_t *s_netif;
static uint32_t s_boot_id;
static SemaphoreHandle_t s_server_lock;
static atomic_bool s_ws_work_pending = ATOMIC_VAR_INIT(false);

typedef struct {
    uint32_t t_ms;
    char state[16];
    char reason[32];
    uint32_t command_age_ms;
    uint32_t last_seq;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
    int32_t left_cps;
    int32_t right_cps;
    bool encoder_valid;
    uint32_t encoder_t_ms;
    int64_t left_count;
    int64_t right_count;
    bool encoder_arm_valid;
    uint32_t encoder_arm_seq;
    uint32_t batt_mv;
    uint32_t drop;
    uint32_t err;

    uint64_t rx_ms;
    bool valid;
} stm_telemetry_t;

static SemaphoreHandle_t s_stm_lock;
static stm_telemetry_t s_stm_telemetry;
static uint32_t s_stm_tel_count;
/* RX task publishes a static string; s_stm_lock protects the pointer. */
static const char *s_stm_startup_status = "SETTLE";

/* WS 사용자 요청의 제한값 */
#define WIFI_COMMAND_QUEUE_LENGTH 1U
#define WIFI_COMMAND_MAX_FRAME_SIZE 128U
#define WIFI_COMMAND_RESPONSE_MS 500U
#define WIFI_COMMAND_MIN_INTERVAL_MS 500U
#define WIFI_COMMAND_RESULT_QUEUE_LENGTH WS_MAX_CLIENTS

typedef enum {
    WIFI_COMMAND_PING,
    WIFI_COMMAND_DISARM,
    WIFI_COMMAND_ARM,
    WIFI_COMMAND_CMD
} wifi_command_type_t;

typedef struct {
    wifi_command_type_t type;

    /* 브라우저 요청과 결과를 연결하는 번호. UART seq와 다르다. */
    uint32_t request_id;

    /* 브라우저가 마지막으로 확인한 ESP 부팅 식별값. */
    uint32_t expected_boot_id;

    /* 요청한 WebSocket 연결의 식별값. */
    uint32_t ws_session_id;

    /* 오래된 대기 요청을 실행하기 않기 위한 ESP 접수 시각. */
    uint64_t accepted_ms;
    wifi_control_request_t control;
} wifi_command_request_t;

/* HTTP 태스크가 넣고 UART 태스크가 꺼낸다. */
static QueueHandle_t s_wifi_command_queue;

/* UART 태스크가 넣고 HTTP 태스크가 꺼내는 완료 결과. */
typedef struct {
    wifi_command_request_t request;
    uint32_t seq;
    uint32_t control_id;
    char status[24];
} wifi_command_result_t;

static QueueHandle_t s_wifi_command_result_queue;

/* 숫자를 읽고 cursor를 숫자 바로 다음 위치로 이동한다. */
static bool wifi_command_parse_u32(const char **cursor, uint32_t *out)
{
    const char *pos = *cursor;

    if (*pos < '0' || *pos > '9') {
        return false;
    }

    uint32_t value = 0U;

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');

        if (value > (UINT32_MAX - digit) / 10U) {
            return false;
        }

        value = value * 10U + digit;
        ++pos;
    }

    *cursor = pos;
    *out = value;
    return true;
}

/* 허용한 명령과 정확한 필드 형식만 요청 구조체로 변환한다. */
static bool wifi_command_parse(
    const char *text, size_t length,
    wifi_command_request_t *out)
{
    if (text == NULL || out == NULL || length == 0U ||
        length > WIFI_COMMAND_MAX_FRAME_SIZE) {
        return false;
    }

    /* 공백, 줄바꿈, 중간 NUL, 비ASCII 문자를 거부한다. */
    for (size_t i = 0U; i < length; ++i) {
        const uint8_t byte = (uint8_t)text[i];

        if (byte < 0x21U || byte > 0x7eU) {
            return false;
        }
    }

    char buffer[WIFI_COMMAND_MAX_FRAME_SIZE + 1U];
    memcpy(buffer, text, length);
    buffer[length] = '\0';

    wifi_command_request_t parsed = {0};
    const char *cursor = buffer;

    if (strncmp(cursor, "PING,", 5U) == 0) {
        parsed.type = WIFI_COMMAND_PING;
        cursor += 5U;
    } else if (strncmp(cursor, "DISARM,", 7U) == 0) {
        parsed.type = WIFI_COMMAND_DISARM;
        cursor += 7U;
    } else {
        return false;
    }

    if (strncmp(cursor, "boot_id=", 8U) != 0) {
        return false;
    }
    cursor += 8U;

    if (!wifi_command_parse_u32(&cursor, &parsed.expected_boot_id)) {
        return false;
    }

    if (strncmp(cursor, ",request_id=", 12U) != 0) {
        return false;
    }
    cursor += 12U;

    if (!wifi_command_parse_u32(&cursor, &parsed.request_id) ||
        parsed.request_id == 0U || *cursor != '\0') {
        return false;
    }

    *out = parsed;
    return true;
}

static const char PAGE[] =
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>ESP Wi-Fi Link</title></head><body><h1>로봇 상태</h1>"
    WIFI_UART_PARTIAL_TEST_BANNER
    "<p>STM32 UART → ESP32 Wi-Fi → 브라우저"
    "</p>"
    "<p id='link'>연결 확인 중"
    "</p>"
    "<p id='stm'>STM TEL 수신 대기"
    "</p>"
    "<p id='startup'>부팅 응답 새 상태 확인 대기"
    "</p>"
    "<p>READY는 이번 ESP 부팅 때 응답 확인을 마쳤다는 뜻입니다. 현재 통신 상태는 TEL 표시에서 확인하세요."
    "</p>"
    "<p>"
    "<button id='ping' type='button' disabled>PING"
    "</button> "
    "<button id='arm' type='button' disabled>ARM · 속도 0"
    "</button> "
    "<button id='disarm' type='button' disabled>DISARM"
    "</button>"
    "</p>"
    "<p>마우스/터치로 누르는 동안만 방향 명령을 보냅니다. 방향 버튼을 놓으면 속도 0, 거리 버튼을 놓으면 DISARM으로 중단합니다."
    "</p>"
    "<p>명령값: 전진 +100 / 후진 -100 mm/s · 회전 ±500 mrad/s (실측 속도 아님)"
    "</p>"
    "<p>"
    "<button id='forward' type='button' style='touch-action:none;user-select:none;min-width:72px;min-height:48px' disabled>전진"
    "</button> "
    "<button id='reverse' type='button' style='touch-action:none;user-select:none;min-width:72px;min-height:48px' disabled>후진"
    "</button> "
    "<button id='left' type='button' style='touch-action:none;user-select:none;min-width:72px;min-height:48px' disabled>좌회전"
    "</button> "
    "<button id='right' type='button' style='touch-action:none;user-select:none;min-width:72px;min-height:48px' disabled>우회전"
    "</button> "
    "</p>"
    "<p id='motion_hint'>방향 입력 대기"
    "</p>"
    "<p id='control'>제어 상태 수신 대기"
    "</p>"
    "<p id='command_notice'>명령 송신 대기"
    "</p>"
    "<p id='command_result'>명령 결과 수신 대기"
    "</p>"
    "<fieldset>"
    "<legend>공중 궤도 거리 시험"
    "</legend>\n"
    "<p>양쪽 궤도를 띄운 상태에서 사용하세요. 거리는 ARM 전에 선택하며, 실행 후 다음 시험은 새 ARM이 필요합니다."
    "</p>\n"
    "<p>"
    "<button id='distance_50' type='button' disabled>5 cm"
    "</button> "
    "<button id='distance_100' type='button' disabled>10 cm"
    "</button> "
    "<button id='distance_150' type='button' disabled>15 cm"
    "</button> "
    "<button id='distance_200' type='button' disabled>20 cm"
    "</button>"
    "</p>\n"
    "<p>"
    "<button id='distance_move' type='button' style='touch-action:none;user-select:none;min-height:48px' disabled>선택 거리 전진 · 누르는 동안"
    "</button>"
    "</p>\n"
    "<p id='distance_hint'>거리 시험 준비 대기"
    "</p>\n"
    "<button id='distance_report' type='button' disabled>거리 기록 보기"
    "</button>"
    "<pre id='distance_data'>"
    "</pre>"
    "</fieldset>\n"
    "<pre id='data'>"
    "</pre>"
    "<script>\n"
    "const byId=id=>document.getElementById(id);\n"
    "const link=byId('link'), stm=byId('stm'), startup=byId('startup'), data=byId('data');\n"
    "const notice=byId('command_notice'), result=byId('command_result'), control=byId('control');\n"
    "const ping=byId('ping'), disarm=byId('disarm'), arm=byId('arm');\n"
    "let socket=null, retry=null, watchdog=null, buttonTimer=null, commandTimer=null, controlTimer=null;\n"
    "let boot=null, session=null, startupFinished=false, nextId=1, ignoredThrough=0, pending=null, nextPingAt=0;\n"
    "let offer=null, offerAt=0, ticketDeadline=0, usedTicket=0, intent=false, controlId=0, nextCmdAt=0;\n"
    "let armWait=null;\n"
    "let motion=null, releaseZero=false, latestTel=null, latestTelAt=0;\n"
    "const motionButtons=['forward','reverse','left','right'].map(byId);\n"
    "const pointerButtons=motionButtons.concat(byId('distance_move'));\n"
    "const motionHint=byId('motion_hint');\n"
    "// Fixed open-loop requests, not calibrated vehicle speeds.\n"
    "const motionValues={forward:[100,0],reverse:[-100,0],left:[0,500],right:[0,-500],distance_move:[100,0]};\n"
    "// Inserted into the embedded PAGE; no direct hardware or network access here.\n"
    "const distanceButtons=[50,100,150,200].map(mm=>byId('distance_'+mm));\n"
    "const distanceButton=byId('distance_move'),distanceHint=byId('distance_hint');\n"
    "let distanceGoal=50,distanceArmSeq=null,distanceStill=null,distanceTrial=null,distanceRunsDropped=0;\n"
    "const distanceRuns=[];\n"
    "function distanceZero(r){\n"
    " return r.vx_mmps===0&&r.w_mradps===0&&r.left_pwm===0&&r.right_pwm===0&&r.left_cps===0&&r.right_cps===0;\n"
    "}\n"
    "function distanceSample(r){\n"
    " return r!==null&&r.source==='STM_UART'&&r.startup_state==='READY'&&r.stm_connected&&!r.stm_stale&&\n"
    "  r.stm_age_ms<250&&r.encoder_valid&&r.encoder_arm_valid&&distanceArmSeq!==null&&r.encoder_arm_seq===distanceArmSeq;\n"
    "}\n"
    "function distancePoint(r){\n"
    " return {ms:performance.now(),tel_count:r.tel_count,stm_t_ms:r.stm_t_ms,encoder_t_ms:r.encoder_t_ms,\n"
    "  encoder_arm_seq:r.encoder_arm_seq,last_seq:r.last_seq,state:r.state,reason:r.reason,\n"
    "  command:[r.vx_mmps,r.w_mradps],pwm:[r.left_pwm,r.right_pwm],cps:[r.left_cps,r.right_cps],\n"
    "  left_count:r.left_count,right_count:r.right_count,stm_age_ms:r.stm_age_ms,drop:r.drop,err:r.err};\n"
    "}\n"
    "function distanceInterrupt(reason){\n"
    " if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
    "  distanceTrial.phase='ABORTED';distanceTrial.stop_reason=reason;distanceTrial.stop_ms=performance.now();\n"
    " }\n"
    "}\n"
    "function distanceReset(){\n"
    " distanceInterrupt('CONTROL_RESET');distanceArmSeq=null;distanceStill=null;distanceTrial=null;\n"
    "}\n"
    "function distanceReady(){\n"
    " const now=performance.now();\n"
    " return distanceTrial===null&&motionReady()&&pending===null&&!releaseZero&&ticketFor('CMD')&&\n"
    "  distanceSample(latestTel)&&distanceZero(latestTel)&&distanceStill!==null&&distanceStill.span>=100&&\n"
    "  now-distanceStill.rx+latestTel.stm_age_ms<250;\n"
    "}\n"
    "function distanceStart(){\n"
    " distanceTrial={goal_mm:distanceGoal,boot_id:boot,control_id:controlId,arm_seq:distanceArmSeq,\n"
    "  phase:'RUNNING',started_ms:performance.now(),baseline:distancePoint(latestTel),\n"
    "  accepted_seqs:[],samples:[],samples_dropped:0,cutoff:null,final:null};\n"
    " distanceRuns.push(distanceTrial);if(distanceRuns.length>16){distanceRuns.shift();++distanceRunsDropped;}\n"
    "}\n"
    "function distanceObserve(r){\n"
    " if(!distanceSample(r)){\n"
    "  distanceStill=null;\n"
    "  if(distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
    "   distanceInterrupt('ENCODER_OR_ARM_INVALID');stopLocal(true);\n"
    "  }\n"
    "  return;\n"
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
    "function distanceUpdate(){\n"
    " const choose=connected()&&!intent&&pending===null&&offer!==null&&offer.phase==='IDLE';\n"
    " for(const button of distanceButtons){\n"
    "  button.disabled=!choose;\n"
    "  button.textContent=(Number(button.id.slice(9))===distanceGoal?'● ':'')+(Number(button.id.slice(9))/10)+' cm';\n"
    " }\n"
    " const held=motion!==null&&motion.distance_mm>0;\n"
    " distanceButton.disabled=!held&&!distanceReady();\n"
    " byId('distance_report').disabled=intent||distanceRuns.length===0;\n"
    " distanceHint.textContent=distanceTrial===null?\n"
    "  (distanceReady()?'거리 '+distanceGoal/10+' cm · 누르는 동안 실행':'거리 '+distanceGoal/10+' cm · ARM 후 정지 상태 확인 대기'):\n"
    "  distanceTrial.phase==='RUNNING'?'거리 '+distanceTrial.goal_mm/10+' cm 실행 중 · 놓으면 중단':\n"
    "  distanceTrial.phase==='CUTOFF'?'목표 count 도달·출력 차단 · 정지 관측 중 · 다음 시험은 새 ARM':\n"
    "  distanceTrial.phase==='STILL_OBSERVED'?(distanceTrial.post_still_count_changed?\n"
    "   '정지 관측 뒤 count 변경 · 기록과 실측 구간 확인 필요':'정지 TEL 관측 · 좌우 링크 실측 필요 · 다음 시험은 새 ARM'):\n"
    "  '거리 시험 중단 ('+distanceTrial.stop_reason+') · 다음 시험은 새 ARM';\n"
    "}\n"
    "function distanceReport(){\n"
    " return {version:1,kind:'airborne_distance_trials',coefficient_mm_per_count:'1687/19500',\n"
    "  note:'TEL baseline/cutoff/final observations; measure actual left/right link travel separately',runs_dropped:distanceRunsDropped,runs:distanceRuns};\n"
    "}\n"
    "window.g6DistanceObserve={report:()=>JSON.stringify(distanceReport(),null,2)};\n"
    "byId('distance_report').onclick=()=>{byId('distance_data').textContent=window.g6DistanceObserve.report();};\n"
    "for(const button of distanceButtons)button.onclick=()=>{\n"
    " if(button.disabled)return;distanceGoal=Number(button.id.slice(9));updateButtons();\n"
    "};\n"
    "\n"
    "function motionReady(){\n"
    " const age=performance.now()-latestTelAt;\n"
    " return connected()&&intent&&focused()&&controlId>0&&nextId<=4294967295&&\n"
    "  offer!==null&&offer.zero_only===false&&offer.phase==='ACTIVE'&&\n"
    "  offer.owner_session===session&&offer.control_id===controlId&&performance.now()-offerAt<200&&\n"
    "  latestTel!==null&&latestTel.source==='STM_UART'&&latestTel.startup_state==='READY'&&\n"
    "  latestTel.stm_connected&&!latestTel.stm_stale&&latestTel.stm_age_ms+age<250&&\n"
    "  latestTel.state==='ARMED'&&latestTel.command_age_ms+age<300&&\n"
    "  Math.abs(latestTel.vx_mmps)<=100&&Math.abs(latestTel.w_mradps)<=500&&\n"
    "  Math.abs(latestTel.left_pwm)<=200&&Math.abs(latestTel.right_pwm)<=200;\n"
    "}\n"
    "function clearMotion(){\n"
    " const old=motion;motion=null;releaseZero=false;\n"
    " if(old){try{old.button.releasePointerCapture(old.pointer);}catch(error){/* already released */}}\n"
    "}\n"
    "function beginMotion(event,name){\n"
    " if(!event.isTrusted||event.button!==0||event.isPrimary===false||motion!==null||releaseZero||!motionReady())return;\n"
    " const distance=name==='distance_move';\n"
    " if(distance?!distanceReady():distanceTrial!==null)return;\n"
    " event.preventDefault();\n"
    " const button=byId(name),values=motionValues[name];\n"
    " motion={button,pointer:event.pointerId,vx:values[0],w:values[1],distance_mm:distance?distanceGoal:0};\n"
    " try{button.setPointerCapture(event.pointerId);}catch(error){stopLocal(true);return;}\n"
    " if(distance)distanceStart();\n"
    " sendCommand('CMD');updateButtons();\n"
    "}\n"
    "function endMotion(event){\n"
    " if(motion===null||event.pointerId!==motion.pointer)return;\n"
    " if(motion.distance_mm>0){distanceInterrupt('BUTTON_RELEASE');stopLocal(true);return;}\n"
    " clearMotion();releaseZero=true;\n"
    " // If a CMD is pending, retain zero intent until its ACK and a fresh ticket.\n"
    " sendCommand('CMD');updateButtons();\n"
    "}\n"
    "function cancelMotion(event){\n"
    " if(motion!==null&&event.pointerId===motion.pointer)stopLocal(true);\n"
    "}\n"
    "function moveMotion(event){\n"
    " if(motion===null||event.pointerId!==motion.pointer)return;\n"
    " const r=motion.button.getBoundingClientRect();\n"
    " if((event.pointerType==='mouse'&&(event.buttons&1)===0)||\n"
    "    event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)endMotion(event);\n"
    "}\n"
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
    " distanceUpdate();\n"
    " const canMove=motionReady()&&!releaseZero&&distanceTrial===null;\n"
    " for(const button of motionButtons)button.disabled=!canMove||(motion!==null&&motion.button!==button);\n"
    " motionHint.textContent=offer&&offer.zero_only?'속도 0 전용 · 방향 입력 비활성':\n"
    "  releaseZero?'속도 0 응답 대기':motion?'누르는 동안 명령 전송 · 놓으면 속도 0':\n"
    "  canMove?'방향 버튼을 누르는 동안 명령 전송':'ARM 후 ACTIVE에서 방향 입력 가능';\n"
    " let refreshAt=Infinity;\n"
    " if(ready&&pending===null&&performance.now()<nextPingAt)refreshAt=nextPingAt;\n"
    " if(!arm.disabled)refreshAt=Math.min(refreshAt,offerAt+200);\n"
    " if(Number.isFinite(refreshAt))buttonTimer=setTimeout(updateButtons,Math.max(1,Math.ceil(refreshAt-performance.now())));\n"
    "}\n"
    "function clearPending(){clearTimeout(commandTimer);commandTimer=null;pending=null;}\n"
    "function resetControl(){\n"
    " distanceReset();cancelArmWait();clearMotion();latestTel=null;latestTelAt=0;\n"
    " intent=false;controlId=0;offer=null;usedTicket=0;ticketDeadline=0;\n"
    " clearTimeout(controlTimer);controlTimer=null;\n"
    "}\n"
    "function stopLocal(sendStop){\n"
    " distanceInterrupt('CONTROL_STOP');\n"
    " cancelArmWait('ARM 준비 대기 취소 · 수동 ARM 필요');\n"
    " const wasIntent=intent;intent=false;clearMotion();controlId=0;clearTimeout(controlTimer);controlTimer=null;\n"
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
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    " updateButtons();\n"
    "}\n"
    "function controlTick(){\n"
    " controlTimer=null;\n"
    " if(!intent)return;\n"
    " if(!focused()||(motion!==null&&!motionReady())){stopLocal(true);return;}\n"
    " if(!offer||performance.now()-offerAt>=200){disconnect(socket,'제어 상태 수신 시간 초과');return;}\n"
    " if(offer.owner_session===session&&['ZERO_PENDING','ACTIVE'].includes(offer.phase)&&\n"
    "    controlId>0&&performance.now()>=nextCmdAt)sendCommand('CMD');\n"
    " if(intent&&controlTimer===null)controlTimer=setTimeout(controlTick,20);\n"
    "}\n"
    "function validControl(r){\n"
    " if(!r||r.kind!=='control_state'||!u32(r.boot_id)||!u32(r.session_id)||r.session_id===0||\n"
    " !u32(r.owner_session)||!u32(r.control_id)||!u32(r.ticket)||!u32(r.ttl_ms)||typeof r.zero_only!=='boolean'||\n"
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
    " if(offer!==null&&offer.zero_only!==r.zero_only){disconnect(socket,'제어 mode 변경 · 새 연결 필요');return;}\n"
    " session=r.session_id;\n"
    " const deadline=performance.now()+Math.max(0,r.ttl_ms-TICKET_SEND_MARGIN_MS);\n"
    " ticketDeadline=offer&&offer.ticket===r.ticket?Math.min(ticketDeadline,deadline):deadline;\n"
    " offer=r;offerAt=performance.now();\n"
    " control.textContent='제어 상태 · '+r.phase+(r.zero_only?' · 속도 0 전용':' · 방향 입력 모드');\n"
    " if(intent&&(['STOPPING','BLOCKED'].includes(r.phase)||(r.phase==='IDLE'&&controlId>0)))stopLocal(false);\n"
    " if(intent&&controlId>0&&(r.owner_session!==session||r.control_id!==controlId))stopLocal(true);\n"
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
    " const completed=pending,expected=pending!==null;\n"
    " clearPending();ignoredThrough=r.request_id;nextId=Math.max(nextId,r.request_id+1);\n"
    " notice.textContent='ESP 명령 처리 결과 수신';\n"
    " result.textContent='마지막 명령 결과 · '+r.cmd+' 요청 '+r.request_id+': '+resultLabels[r.status]+' ('+r.status+')';\n"
    " if(['ARM','CMD'].includes(r.cmd)){\n"
    "  if(r.status!=='OK')stopLocal(true);\n"
    "  else if(r.cmd==='ARM'&&intent&&expected){controlId=r.control_id;distanceArmSeq=r.seq;distanceStill=null;}\n"
    "  else if(r.cmd==='CMD'&&completed&&completed.distance_mm>0&&distanceTrial!==null&&distanceTrial.phase==='RUNNING'){\n"
    "   distanceTrial.accepted_seqs.push(r.seq);distanceObserve(latestTel);\n"
    "  }\n"
    "  else if(r.cmd==='CMD'&&completed&&completed.releaseZero)releaseZero=false;\n"
    " }\n"
    " updateButtons();\n"
    "}\n"
    "function validStatus(s){\n"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;\n"
    " const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647;\n"
    " const ms=v=>Number.isSafeInteger(v)&&v>=0;\n"
    " const i64text=v=>{\n"
    "  if(typeof v!=='string'||! /^-?(0|[1-9][0-9]{0,18})$/.test(v)||v==='-0')return false;\n"
    "  const negative=v[0]==='-', digits=negative?v.slice(1):v;\n"
    "  const limit=negative?'9223372036854775808':'9223372036854775807';\n"
    "  return digits.length<limit.length||(digits.length===limit.length&&digits<=limit);\n"
    " };\n"
    " if(!s||typeof s!=='object'||Array.isArray(s)||\n"
    "  !['ESP_ONLY','STM_UART'].includes(s.source)||!['AP','STA'].includes(s.mode)||\n"
    "  !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK','WAIT_PONG','READY','FAILED'].includes(s.startup_state)||\n"
    "  !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||!u32(s.tel_count)||\n"
    "  !u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||\n"
    "  typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||\n"
    "  s.batt_mv!==null||s.battery_available!==false)return false;\n"
    " if(s.source==='ESP_ONLY'){\n"
    "  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&s.tel_count===0&&\n"
    "   ['stm_t_ms','state','reason','command_age_ms','last_seq','vx_mmps','w_mradps',\n"
    "    'left_pwm','right_pwm','left_cps','right_cps','drop','err',\n"
    "    'encoder_valid','encoder_t_ms','left_count','right_count',\n"
    "    'encoder_arm_valid','encoder_arm_seq'].every(k=>s[k]===null);\n"
    " }\n"
    " return ms(s.stm_age_ms)&&s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&\n"
    "  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&\n"
    "  ['DISARMED','ARMED','FAULT'].includes(s.state)&&\n"
    "  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&\n"
    "  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&\n"
    "  ['vx_mmps','w_mradps','left_pwm','right_pwm','left_cps','right_cps'].every(k=>i32(s[k]))&&\n"
    "  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000&&\n"
    "  typeof s.encoder_valid==='boolean'&&typeof s.encoder_arm_valid==='boolean'&&\n"
    "  u32(s.encoder_t_ms)&&u32(s.encoder_arm_seq)&&i64text(s.left_count)&&i64text(s.right_count);\n"
    "}\n"
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
    "   latestTel=r;latestTelAt=performance.now();distanceObserve(r);\n"
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
    "for(const button of pointerButtons){\n"
    " button.onpointerdown=event=>beginMotion(event,button.id);\n"
    " button.onpointerup=endMotion;button.onpointercancel=cancelMotion;\n"
    " button.onlostpointercapture=cancelMotion;\n"
    " button.oncontextmenu=event=>event.preventDefault();\n"
    "}\n"
    "window.addEventListener('pointerup',endMotion);\n"
    "window.addEventListener('pointercancel',cancelMotion);\n"
    "window.addEventListener('pointermove',moveMotion);\n"
    "window.addEventListener('blur',()=>stopLocal(true));\n"
    "document.addEventListener('visibilitychange',()=>{if(document.hidden)stopLocal(true);});\n"
    "window.addEventListener('offline',()=>{if(socket!==null)disconnect(socket,'네트워크 연결 끊김');});\n"
    "window.addEventListener('online',()=>{clearTimeout(retry);retry=null;connect();});\n"
    "connect();\n"
    "\n"
    "</script></body></html>\n";

static int status_json(char *json, size_t capacity)
{
    stm_telemetry_t tel;
    uint32_t tel_count;
    const char *startup_state;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    tel = s_stm_telemetry;
    tel_count = s_stm_tel_count;
    startup_state = s_stm_startup_status;
    xSemaphoreGive(s_stm_lock);

    /* Snapshot을 복사한 뒤 시각을 읽어 rx_ms보다 앞서지 않게 한다. */
    const uint64_t uptime_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const uint64_t age_ms = tel.valid ? uptime_ms - tel.rx_ms : 0U;
    const bool fresh = tel.valid && age_ms <= STM_TEL_STALE_MS;
    int length;

    if (!tel.valid) {
        length = snprintf(
            json, capacity,
            "{\"source\":\"ESP_ONLY\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":false,\"stm_stale\":false,"
            "\"stm_age_ms\":null,\"stm_age_limit_ms\":%u,"
            "\"tel_count\":0,\"stm_t_ms\":null,"
            "\"state\":null,\"reason\":null,"
            "\"command_age_ms\":null,\"last_seq\":null,"
            "\"vx_mmps\":null,\"w_mradps\":null,"
            "\"left_pwm\":null,\"right_pwm\":null,"
            "\"left_cps\":null,\"right_cps\":null,"
            "\"encoder_valid\":null,\"encoder_t_ms\":null,"
            "\"left_count\":null,\"right_count\":null,"
            "\"encoder_arm_valid\":null,\"encoder_arm_seq\":null,"
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":null,\"err\":null}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state, STM_TEL_STALE_MS);
    } else {
        length = snprintf(
            json, capacity,
            "{\"source\":\"STM_UART\",\"mode\":\"%s\","
            "\"boot_id\":%" PRIu32 ",\"uptime_ms\":%" PRIu64 ","
            "\"free_heap_bytes\":%" PRIu32 ","
            "\"startup_state\":\"%s\","
            "\"stm_connected\":%s,\"stm_stale\":%s,"
            "\"stm_age_ms\":%" PRIu64 ",\"stm_age_limit_ms\":%u,"
            "\"tel_count\":%" PRIu32 ",\"stm_t_ms\":%" PRIu32 ","
            "\"state\":\"%s\",\"reason\":\"%s\","
            "\"command_age_ms\":%" PRIu32 ",\"last_seq\":%" PRIu32 ","
            "\"vx_mmps\":%" PRIi32 ",\"w_mradps\":%" PRIi32 ","
            "\"left_pwm\":%" PRIi32 ",\"right_pwm\":%" PRIi32 ","
            "\"left_cps\":%" PRIi32 ",\"right_cps\":%" PRIi32 ","
            "\"encoder_valid\":%s,\"encoder_t_ms\":%" PRIu32 ","
            "\"left_count\":\"%" PRId64 "\",\"right_count\":\"%" PRId64 "\","
            "\"encoder_arm_valid\":%s,\"encoder_arm_seq\":%" PRIu32 ","
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":%" PRIu32 ",\"err\":%" PRIu32 "}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state,
            fresh ? "true" : "false", fresh ? "false" : "true",
            age_ms, STM_TEL_STALE_MS, tel_count, tel.t_ms,
            tel.state, tel.reason, tel.command_age_ms, tel.last_seq,
            tel.vx_mmps, tel.w_mradps, tel.left_pwm, tel.right_pwm,
            tel.left_cps, tel.right_cps,
            tel.encoder_valid ? "true" : "false", tel.encoder_t_ms,
            tel.left_count, tel.right_count,
            tel.encoder_arm_valid ? "true" : "false", tel.encoder_arm_seq,
            tel.drop, tel.err);
    }

    if (length < 0 || (size_t)length >= capacity) {
        return -1;
    }
    return length;
}

static esp_err_t page_get(httpd_req_t *req)
{
    ESP_ERROR_CHECK(httpd_resp_set_type(req, "text/html; charset=utf-8"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, PAGE, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t status_get(httpd_req_t *req)
{
    char json[STATUS_JSON_SIZE];
    const int length = status_json(json, sizeof(json));
    if (length < 0) {
        return httpd_resp_send_err(
            req, HTTPD_500_INTERNAL_SERVER_ERROR, "Status buffer error");
    }

    ESP_ERROR_CHECK(httpd_resp_set_type(req, "application/json"));
    ESP_ERROR_CHECK(httpd_resp_set_hdr(req, "Cache-Control", "no-store"));
    return httpd_resp_send(req, json, length);
}

/* HTTP and UART serialize executor/ticket/session access with s_stm_lock.
 * Never hold this lock across UART/network I/O. Only UART task writes UART1. */
typedef struct {
    uint32_t id;
    uint32_t last_request_id;
    uint64_t last_accepted_ms;
    uint64_t last_cmd_ms;
    bool have_cmd;
    wifi_control_ticket_t ticket;
} wifi_ws_session_t;

static uint32_t s_wifi_ws_next_session_id;
static uint32_t s_wifi_command_owner_session_id;
static wifi_ws_session_t *s_sessions[WS_MAX_CLIENTS];
static wifi_control_executor_t s_control;
static wifi_control_ticket_pool_t s_ticket_pool;
static bool s_manual_stop_pending;
static wifi_command_request_t s_manual_stop_request;
static uint32_t s_manual_stop_seq;

static uint64_t wifi_control_now(void)
{
    return (uint64_t)esp_timer_get_time() / 1000U;
}

static const char *wifi_command_name(wifi_command_type_t type)
{
    switch (type) {
    case WIFI_COMMAND_PING: return "PING";
    case WIFI_COMMAND_DISARM: return "DISARM";
    case WIFI_COMMAND_ARM: return "ARM";
    case WIFI_COMMAND_CMD: return "CMD";
    default: return "UNKNOWN";
    }
}

static bool wifi_control_ready_locked(void)
{
    return strcmp(s_stm_startup_status, "READY") == 0;
}

static void wifi_control_cleanup_locked(void)
{
    if (!wifi_control_executor_needs_invalidation(&s_control)) return;
    for (size_t i = 0U; i < WS_MAX_CLIENTS; ++i) {
        if (s_sessions[i] != NULL) wifi_control_ticket_invalidate(&s_sessions[i]->ticket);
    }
    (void)xQueueReset(s_wifi_command_queue);
    s_wifi_command_owner_session_id = 0U;
    wifi_control_executor_inputs_cleared(&s_control);
}

static void wifi_control_closed(uint32_t id)
{
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    wifi_control_executor_owner_closed(&s_control, id, wifi_control_now());
    if (s_wifi_command_owner_session_id == id) {
        s_wifi_command_owner_session_id = 0U;
        (void)xQueueReset(s_wifi_command_queue);
    }
    wifi_control_cleanup_locked();
    xSemaphoreGive(s_stm_lock);
}

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

static void wifi_ws_session_free(void *context)
{
    wifi_ws_session_t *session = context;
    if (session == NULL) return;
    wifi_control_closed(session->id);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    wifi_control_ticket_invalidate(&session->ticket);
    for (size_t i = 0U; i < WS_MAX_CLIENTS; ++i) {
        if (s_sessions[i] == session) s_sessions[i] = NULL;
    }
    xSemaphoreGive(s_stm_lock);
    free(session);
}

static wifi_ws_session_t *wifi_ws_session_get(httpd_req_t *req)
{
    if (req->sess_ctx != NULL) return req->sess_ctx;
    wifi_ws_session_t *session = calloc(1U, sizeof(*session));
    if (session == NULL) return NULL;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    size_t slot = 0U;
    while (slot < WS_MAX_CLIENTS && s_sessions[slot] != NULL) ++slot;
    if (slot == WS_MAX_CLIENTS || s_wifi_ws_next_session_id == UINT32_MAX) {
        xSemaphoreGive(s_stm_lock);
        free(session);
        return NULL;
    }
    session->id = ++s_wifi_ws_next_session_id;
    s_sessions[slot] = session;
    xSemaphoreGive(s_stm_lock);
    req->sess_ctx = session;
    req->free_ctx = wifi_ws_session_free;
    return session;
}

/* Called with s_stm_lock held. A NULL result means accepted, not STM success. */
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
        ",\"ticket\":%" PRIu32 ",\"purpose\":\"%s\",\"ttl_ms\":%" PRIu32
        ",\"zero_only\":%s,\"control_reason\":%u}",
        s_boot_id, session->id, phases[state->phase],
        state->owner.ws_session_id, state->owner.control_id,
        valid ? session->ticket.id : 0U,
        valid ? (arm ? "ARM" : "CMD") : "NONE", ttl,
        WIFI_CONTROL_ZERO_ONLY ? "true" : "false",
        (unsigned)state->reason);
    xSemaphoreGive(s_stm_lock);
    return length >= 0 && (size_t)length < capacity ? length : -1;
}

/* HTTP 핸들러에서 접수/거부만 즉시 알린다. STM 응답을 기다리지 않는다. */
static esp_err_t wifi_ws_send_notice(
    httpd_req_t *req, const wifi_command_request_t *request,
    const char *stage, const char *reason)
{
    char request_id[16] = "null";
    char command[12] = "null";

    if (request != NULL) {
        (void)snprintf(request_id, sizeof(request_id), "%" PRIu32, request->request_id);
        (void)snprintf(
            command, sizeof(command), "\"%s\"",
            wifi_command_name(request->type));
    }

    const wifi_ws_session_t *session = req->sess_ctx;
    const uint32_t session_id = session == NULL ? 0U : session->id;
    char json[256];
    const int length = snprintf(
        json, sizeof(json),
        "{\"kind\":\"command_notice\",\"boot_id\":%" PRIu32
        ",\"session_id\":%" PRIu32 ",\"request_id\":%s,\"cmd\":%s"
        ",\"stage\":\"%s\",\"reason\":\"%s\"}",
        s_boot_id, session_id, request_id, command, stage, reason);

    if (length < 0 || (size_t)length >= sizeof(json)) {
        ESP_LOGE(TAG, "W5 notice JSON buffer error");
        return ESP_FAIL;
    }

    httpd_ws_frame_t frame = {
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)json,
        .len = (size_t)length
    };
    const esp_err_t result = httpd_ws_send_frame(req, &frame);

    if (result != ESP_OK) {
        ESP_LOGW(TAG, "W5 notice send failed; closing connection");
    }
    return result;
}

static esp_err_t ws_receive(httpd_req_t *req)
{
    httpd_ws_frame_t frame = {0};
    esp_err_t result = httpd_ws_recv_frame(req, &frame, 0);
    if (result != ESP_OK) return result;
    const bool pong = frame.type == HTTPD_WS_TYPE_PONG;
    if (!frame.final || (frame.type != HTTPD_WS_TYPE_TEXT && !pong) ||
        frame.len > WIFI_COMMAND_MAX_FRAME_SIZE || (pong && frame.len > 125U)) return ESP_FAIL;
    uint8_t payload[WIFI_COMMAND_MAX_FRAME_SIZE];
    frame.payload = payload;
    if (frame.len > 0U) {
        result = httpd_ws_recv_frame(req, &frame, sizeof(payload));
        if (result != ESP_OK) return result;
    }
    if (pong) return ESP_OK;
    wifi_ws_session_t *session = wifi_ws_session_get(req);
    if (session == NULL) return ESP_FAIL;
    /* HELLO only registers the live connection. It never queues a UART command. */
    if (frame.len == 5U && memcmp(payload, "HELLO", 5U) == 0) return ESP_OK;
    wifi_command_request_t request = {0};
    if (!wifi_command_parse((const char *)payload, frame.len, &request)) {
        if (wifi_control_parse((const char *)payload, frame.len, &request.control) != WIFI_CONTROL_PARSE_OK) {
            wifi_control_closed(session->id);
            return wifi_ws_send_notice(req, NULL, "REJECTED", "BAD_FORMAT");
        }
        request.type = request.control.type == WIFI_CONTROL_ARM ? WIFI_COMMAND_ARM : WIFI_COMMAND_CMD;
        request.request_id = request.control.request_id;
        request.expected_boot_id = request.control.expected_boot_id;
    }
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const wifi_control_ticket_t ticket_before = session->ticket;
    const uint64_t check_begin_ms = wifi_control_now();
    const char *rejection = wifi_command_admit_locked(session, &request);
    const uint64_t check_end_ms = wifi_control_now();
    const bool ticket_valid_after = session->ticket.valid;
    xSemaphoreGive(s_stm_lock);
    if (rejection != NULL) {
        ESP_LOGW(TAG, "WS rejected: %s request=%" PRIu32, rejection, request.request_id);
        if (strcmp(rejection, "TICKET_REJECTED") == 0) {
            /* Capture under the lock; print only after releasing it. */
            ESP_LOGW(TAG,
                "TICKET DEBUG: cmd=%s request=%" PRIu32
                " got=%" PRIu32 " expected=%" PRIu32 " valid=%u/%u"
                " check_ms=%" PRIu64 "..%" PRIu64
                " issued_ms=%" PRIu64 " expires_ms=%" PRIu64
                " boot=%" PRIu32 "/%" PRIu32
                " session=%" PRIu32 "/%" PRIu32
                " control=%" PRIu32 "/%" PRIu32 " purpose=%u/%u",
                wifi_command_name(request.type), request.request_id,
                request.control.ticket, ticket_before.id,
                (unsigned)ticket_before.valid, (unsigned)ticket_valid_after,
                check_begin_ms, check_end_ms,
                ticket_before.issued_ms, ticket_before.expires_ms,
                request.control.expected_boot_id, ticket_before.boot_id,
                request.control.ws_session_id, ticket_before.ws_session_id,
                request.control.control_id, ticket_before.control_id,
                (unsigned)request.control.type, (unsigned)ticket_before.purpose);
        }
    } else {
        ESP_LOGI(TAG, "WS QUEUED: %s request=%" PRIu32 " session=%" PRIu32,
            wifi_command_name(request.type), request.request_id, request.ws_session_id);
    }
    result = wifi_ws_send_notice(req, &request, rejection == NULL ? "ACCEPTED" : "REJECTED",
        rejection == NULL ? "QUEUED" : rejection);
    if (result != ESP_OK) wifi_control_closed(session->id);
    return result;
}

/* HTTP 태스크에서만 실행: 결과를 요청했던 연결 하나에 전달한다. */
static void ws_command_results(httpd_handle_t server)
{
    wifi_command_result_t result;
    for (size_t n = 0U; n < WIFI_COMMAND_RESULT_QUEUE_LENGTH; ++n) {
        if (xQueueReceive(s_wifi_command_result_queue, &result, 0) != pdPASS) break;
        if (result.request.expected_boot_id != s_boot_id) continue;
        int clients[WS_MAX_CLIENTS];
        size_t count = WS_MAX_CLIENTS;
        if (httpd_get_client_list(server, &count, clients) != ESP_OK) {
            wifi_control_transport_lost();
            return;
        }
        char json[320];
        const int length = snprintf(json, sizeof(json),
            "{\"kind\":\"command_result\",\"boot_id\":%" PRIu32 ",\"session_id\":%" PRIu32
            ",\"request_id\":%" PRIu32 ",\"cmd\":\"%s\",\"seq\":%" PRIu32
            ",\"control_id\":%" PRIu32 ",\"status\":\"%s\"}",
            s_boot_id, result.request.ws_session_id, result.request.request_id,
            wifi_command_name(result.request.type), result.seq, result.control_id, result.status);
        if (length < 0 || (size_t)length >= sizeof(json)) {
            wifi_control_closed(result.request.ws_session_id);
            continue;
        }
        for (size_t i = 0U; i < count; ++i) {
            if (httpd_ws_get_fd_info(server, clients[i]) != HTTPD_WS_CLIENT_WEBSOCKET) continue;
            const wifi_ws_session_t *session = httpd_sess_get_ctx(server, clients[i]);
            if (session == NULL || session->id != result.request.ws_session_id) continue;
            httpd_ws_frame_t frame = {.type = HTTPD_WS_TYPE_TEXT, .payload = (uint8_t *)json, .len = (size_t)length};
            if (httpd_ws_send_frame_async(server, clients[i], &frame) != ESP_OK) {
                wifi_control_closed(session->id);
                (void)httpd_sess_trigger_close(server, clients[i]);
            }
            break;
        }
    }
}

static void ws_broadcast(void *arg)
{
    const httpd_handle_t server = (httpd_handle_t)arg;
    static uint64_t last_status_ms;
    ws_command_results(server);
    const uint64_t now = wifi_control_now();
    const bool send_status = now - last_status_ms >= WS_PERIOD_MS;
    char status[STATUS_JSON_SIZE];
    const int status_length = send_status ? status_json(status, sizeof(status)) : -1;
    if (send_status) last_status_ms = now;
    int clients[WS_MAX_CLIENTS];
    size_t count = WS_MAX_CLIENTS;
    if (httpd_get_client_list(server, &count, clients) != ESP_OK) {
        wifi_control_transport_lost();
    } else for (size_t i = 0U; i < count; ++i) {
        if (httpd_ws_get_fd_info(server, clients[i]) != HTTPD_WS_CLIENT_WEBSOCKET) continue;
        wifi_ws_session_t *session = httpd_sess_get_ctx(server, clients[i]);
        esp_err_t result = ESP_OK;
        if (status_length >= 0) {
            httpd_ws_frame_t frame = {.type = HTTPD_WS_TYPE_TEXT, .payload = (uint8_t *)status, .len = (size_t)status_length};
            result = httpd_ws_send_frame_async(server, clients[i], &frame);
        }
        if (result == ESP_OK && session != NULL) {
            char control[320];
            const int length = wifi_control_snapshot(session, control, sizeof(control));
            if (length < 0) result = ESP_FAIL;
            else {
                httpd_ws_frame_t frame = {.type = HTTPD_WS_TYPE_TEXT, .payload = (uint8_t *)control, .len = (size_t)length};
                result = httpd_ws_send_frame_async(server, clients[i], &frame);
            }
        }
        if (result != ESP_OK) {
            if (session != NULL) wifi_control_closed(session->id);
            (void)httpd_sess_trigger_close(server, clients[i]);
        }
    }
    atomic_store(&s_ws_work_pending, false);
}

static void ws_schedule(void)
{
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    if (s_server != NULL && !atomic_load(&s_ws_work_pending)) {
        atomic_store(&s_ws_work_pending, true);
        if (httpd_queue_work(s_server, ws_broadcast, s_server) != ESP_OK) {
            atomic_store(&s_ws_work_pending, false);
            ESP_LOGW(TAG, "WS work queue failed");
        }
    }
    xSemaphoreGive(s_server_lock);
}

static void server_stop(void)
{
    wifi_control_transport_lost();
    xSemaphoreTake(s_server_lock, portMAX_DELAY);
    const httpd_handle_t server = s_server;
    s_server = NULL;
    xSemaphoreGive(s_server_lock);

    if (server != NULL) {
        ESP_ERROR_CHECK(httpd_stop(server));
        ESP_LOGI(TAG, "HTTP/WS server stopped");
    }
}

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

#define STM_UART_PORT UART_NUM_1
#define STM_UART_TX_PIN 17
#define STM_UART_RX_PIN 18
#define STM_UART_RX_BUFFER_SIZE 1024
#define STM_UART_LINE_SIZE 512U

/* 이 수신 상태는 stm_uart_rx_task만 사용한다. */
static char s_stm_rx_line[STM_UART_LINE_SIZE];
static size_t s_stm_rx_length;

/* 수신 시작 시 이미 전송 중인 첫 줄은 버린다. */
static bool s_stm_discard_until_lf = true;

static void stm_uart_init(void)
{
    const uart_config_t config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT
    };

    ESP_ERROR_CHECK(uart_driver_install(
        STM_UART_PORT, STM_UART_RX_BUFFER_SIZE,
        0, 0, NULL, 0));
    
    ESP_ERROR_CHECK(uart_param_config(STM_UART_PORT, &config));

    ESP_ERROR_CHECK(uart_set_pin(
        STM_UART_PORT,
        STM_UART_TX_PIN, STM_UART_RX_PIN,
        UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));

    ESP_LOGI(TAG, "STM UART RX ready: TX=GPIO17 RX=GPIO18 115200/8N1");
}

static const char *stm_find_field_value(
    const char *line, const char *key)
{
    const size_t key_length = strlen(key);
    const char *field = line;
    const char *value = NULL;

    while (*field != '\0') {
        if (strncmp(field, key, key_length) == 0) {
            if (value != NULL) {
                return NULL;
            }
            value = field + key_length;
        }

        const char *comma = strchr(field, ',');
        if (comma == NULL) {
            break;
        }
        field = comma + 1;
    }

    return value;
}

static bool stm_parse_u32_field(
    const char *line, const char *key, uint32_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL || *pos < '0' || *pos > '9') {
        return false;
    }

    uint32_t value = 0U;

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');
        if (value > (UINT32_MAX - digit) / 10U) {
            return false;
        }
        value = value * 10U + digit;
        ++pos;
    }

    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    *out = value;
    return true;
}

static bool stm_parse_i32_field(
    const char *line, const char *key, int32_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const bool negative = *pos == '-';
    if (negative) {
        ++pos;
    }
    if (*pos < '0' || *pos > '9') {
        return false;
    }

    const uint32_t limit =
        negative ? 2147483648U : 2147483647U;
    uint32_t magnitude = 0U;

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');
        if (magnitude > (limit - digit) / 10U) {
            return false;
        }
        magnitude = magnitude * 10U + digit;
        ++pos;
    }

    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    if (negative) {
        *out = magnitude == 2147483648U
            ? INT32_MIN : -(int32_t)magnitude;
    } else {
        *out = (int32_t)magnitude;
    }

    return true;
}

static bool stm_parse_i64_field(
    const char *line, const char *key, int64_t *out)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const bool negative = *pos == '-';
    if (negative) {
        ++pos;
    }
    if (*pos < '0' || *pos > '9') {
        return false;
    }

    const uint64_t limit = negative
        ? (uint64_t)INT64_MAX + 1U : (uint64_t)INT64_MAX;
    uint64_t magnitude = 0U;
    while (*pos >= '0' && *pos <= '9') {
        const uint64_t digit = (uint64_t)(*pos - '0');
        if (magnitude > (limit - digit) / 10U) {
            return false;
        }
        magnitude = magnitude * 10U + digit;
        ++pos;
    }
    if (*pos != ',' && *pos != '\0') {
        return false;
    }

    *out = negative
        ? (magnitude == (uint64_t)INT64_MAX + 1U
            ? INT64_MIN : -(int64_t)magnitude)
        : (int64_t)magnitude;
    return true;
}

static bool stm_parse_text_field(
    const char *line, const char *key,
    char *out, size_t capacity)
{
    const char *pos = stm_find_field_value(line, key);
    if (pos == NULL) {
        return false;
    }

    const size_t length = strcspn(pos, ",");
    if (length == 0U || length >= capacity) {
        return false;
    }

    for (size_t i = 0U; i < length; ++i) {
        const char c = pos[i];
        if (!((c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '_')) {
            return false;
        }
    }

    memcpy(out, pos, length);
    out[length] = '\0';
    return true;
}

static bool stm_parse_tel(
    const char *line, stm_telemetry_t *out)
{
    if (line == NULL || out == NULL ||
        strncmp(line, "TEL,", 4) != 0) {
        return false;
    }

    const size_t length = strlen(line);
    if (line[length - 1U] == ',' ||
        strstr(line, ",,") != NULL) {
        return false;
    }

    /* 확장 TEL 계약은 20개 필드다. */
    size_t field_count = 0U;
    for (const char *pos = line; *pos != '\0'; ++pos) {
        if (*pos == ',') {
            ++field_count;
        }
    }
    if (field_count != 20U) {
        return false;
    }

    uint32_t encoder_valid;
    uint32_t encoder_arm_valid;
    const bool fields_ok =
        stm_parse_u32_field(line, "t_ms=", &out->t_ms) &&
        stm_parse_text_field(
            line, "state=", out->state, sizeof(out->state)) &&
        stm_parse_text_field(
            line, "reason=", out->reason, sizeof(out->reason)) &&
        stm_parse_u32_field(
            line, "command_age_ms=", &out->command_age_ms) &&
        stm_parse_u32_field(line, "last_seq=", &out->last_seq) &&
        stm_parse_i32_field(line, "vx_mmps=", &out->vx_mmps) &&
        stm_parse_i32_field(line, "w_mradps=", &out->w_mradps) &&
        stm_parse_i32_field(line, "left_pwm=", &out->left_pwm) &&
        stm_parse_i32_field(line, "right_pwm=", &out->right_pwm) &&
        stm_parse_i32_field(line, "left_cps=", &out->left_cps) &&
        stm_parse_i32_field(line, "right_cps=", &out->right_cps) &&
        stm_parse_u32_field(line, "encoder_valid=", &encoder_valid) &&
        stm_parse_u32_field(line, "encoder_t_ms=", &out->encoder_t_ms) &&
        stm_parse_i64_field(line, "left_count=", &out->left_count) &&
        stm_parse_i64_field(line, "right_count=", &out->right_count) &&
        stm_parse_u32_field(line, "encoder_arm_valid=", &encoder_arm_valid) &&
        stm_parse_u32_field(line, "encoder_arm_seq=", &out->encoder_arm_seq) &&
        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&
        stm_parse_u32_field(line, "drop=", &out->drop) &&
        stm_parse_u32_field(line, "err=", &out->err);

    if (!fields_ok || encoder_valid > 1U || encoder_arm_valid > 1U) {
        return false;
    }

    out->encoder_valid = encoder_valid != 0U;
    out->encoder_arm_valid = encoder_arm_valid != 0U;

    const bool state_ok =
        strcmp(out->state, "DISARMED") == 0 ||
        strcmp(out->state, "ARMED") == 0 ||
        strcmp(out->state, "FAULT") == 0;

    return state_ok &&
        out->left_pwm >= -1000 && out->left_pwm <= 1000 &&
        out->right_pwm >= -1000 && out->right_pwm <= 1000;
}

#define STM_STARTUP_SETTLE_MS 500U
#define STM_STARTUP_SYNC_WAIT_MS 100U
#define STM_STARTUP_RESPONSE_MS 500U
#define STM_STARTUP_MAX_ATTEMPTS 3U

typedef enum {
    STM_STARTUP_SETTLE,
    STM_STARTUP_SYNC_WAIT,
    STM_STARTUP_WAIT_DISARM_ACK,
    STM_STARTUP_WAIT_PONG,
    STM_STARTUP_READY,
    STM_STARTUP_FAILED
} stm_startup_state_t;

/* 아래 상태는 stm_uart_rx_task만 읽고 변경한다. */
typedef struct {
    stm_startup_state_t state;
    uint64_t phase_ms;
    uint32_t disarm_seq;
    uint32_t ping_seq;
    unsigned attempts;
    bool disarm_ack;
    bool pong;
} stm_startup_t;

static stm_startup_t s_stm_startup;

static void stm_startup_fail(const char *reason)
{
    if (s_stm_startup.state == STM_STARTUP_FAILED) {
        return;
    }

    s_stm_startup.state = STM_STARTUP_FAILED;
    ESP_LOGE(TAG, "STARTUP FAILED: %s", reason);
}

static void stm_startup_begin(void)
{
    const uint32_t seq = esp_random();

    s_stm_startup = (stm_startup_t) {
        .state = STM_STARTUP_SETTLE,
        .phase_ms = (uint64_t)esp_timer_get_time() / 1000U,
        .disarm_seq = seq,
        .ping_seq = seq + 1U
    };

    ESP_LOGI(
        TAG,
        "STARTUP: settle; DISARM seq=%" PRIu32
        " PING seq=%" PRIu32,
        s_stm_startup.disarm_seq,
        s_stm_startup.ping_seq);
}

static void stm_startup_send_request(bool ping, uint64_t now_ms)
{
    const char *command = ping ? "PING" : "DISARM";
    const uint32_t seq = ping
        ? s_stm_startup.ping_seq
        : s_stm_startup.disarm_seq;

    char frame[48];
    const int length = snprintf(
        frame, sizeof(frame),
        "%s%s,seq=%" PRIu32 "\n",
        ping ? "" : WIFI_CONTROL_UART_CANCEL, command, seq);

    if (length <= 0 || (size_t)length >= sizeof(frame)) {
        stm_startup_fail("request formatting failed");
        return;
    }

    if (uart_write_bytes(
            STM_UART_PORT, frame, (size_t)length) != length) {
        stm_startup_fail("request TX failed");
        return;
    }

    s_stm_startup.state = ping
        ? STM_STARTUP_WAIT_PONG
        : STM_STARTUP_WAIT_DISARM_ACK;
    s_stm_startup.phase_ms = now_ms;
    s_stm_startup.disarm_ack = false;
    s_stm_startup.pong = false;

    ESP_LOGI(
        TAG,
        "TX UART1: %s,seq=%" PRIu32 " attempt=%u",
        command, seq, s_stm_startup.attempts);
}

static void stm_startup_retry(bool ping, uint64_t now_ms)
{
    if (now_ms - s_stm_startup.phase_ms <
        STM_STARTUP_RESPONSE_MS) {
        return;
    }

    if (s_stm_startup.attempts >= STM_STARTUP_MAX_ATTEMPTS) {
        stm_startup_fail(
            ping ? "no matching PONG" : "no matching DISARM ACK");
        return;
    }

    ++s_stm_startup.attempts;

    ESP_LOGW(
        TAG, "STARTUP: retry %s attempt=%u",
        ping ? "PING" : "DISARM",
        s_stm_startup.attempts);

    stm_startup_send_request(ping, now_ms);
}

static void stm_startup_step(uint64_t now_ms)
{
    switch (s_stm_startup.state) {
    case STM_STARTUP_SETTLE:
        if (now_ms - s_stm_startup.phase_ms <
            STM_STARTUP_SETTLE_MS) {
            break;
        }

        if (uart_write_bytes(STM_UART_PORT, WIFI_CONTROL_UART_CANCEL, 2) != 2) {
            stm_startup_fail("line cancel TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line cancel sent");
        s_stm_startup.state = STM_STARTUP_SYNC_WAIT;
        s_stm_startup.phase_ms = now_ms;
        break;

    case STM_STARTUP_SYNC_WAIT:
        if (now_ms - s_stm_startup.phase_ms <
            STM_STARTUP_SYNC_WAIT_MS) {
            break;
        }

        if (uart_flush_input(STM_UART_PORT) != ESP_OK) {
            stm_startup_fail("RX flush failed");
            break;
        }

        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = false;
        s_stm_startup.attempts = 1U;
        stm_startup_send_request(false, now_ms);
        break;

    case STM_STARTUP_WAIT_DISARM_ACK:
        if (s_stm_startup.disarm_ack) {
            ESP_LOGI(TAG, "STARTUP: DISARM acknowledged");
            s_stm_startup.attempts = 1U;
            stm_startup_send_request(true, now_ms);
        } else {
            stm_startup_retry(false, now_ms);
        }
        break;

    case STM_STARTUP_WAIT_PONG:
        if (s_stm_startup.pong) {
            s_stm_startup.state = STM_STARTUP_READY;
            ESP_LOGI(
                TAG,
                "STARTUP READY: DISARM ACK and PONG verified");
        } else {
            stm_startup_retry(true, now_ms);
        }
        break;

    case STM_STARTUP_READY:
    case STM_STARTUP_FAILED:
    default:
        break;
    }
}

/* 아래 대기 정보와 seq는 UART 태스크만 사용한다. */
typedef struct {
    bool active;
    wifi_command_request_t request;
    uint32_t seq;
    uint64_t sent_ms;
} wifi_uart_pending_t;

static wifi_uart_pending_t s_wifi_uart_pending;
static uint64_t s_wifi_uart_next_seq;

/* One allocator for startup-reserved seq, W5 diagnostics and control frames. */
static bool wifi_uart_allocate_seq(uint32_t *out)
{
    while (s_wifi_uart_next_seq <= UINT32_MAX &&
        (s_wifi_uart_next_seq == s_stm_startup.disarm_seq || s_wifi_uart_next_seq == s_stm_startup.ping_seq)) {
        ++s_wifi_uart_next_seq;
    }
    if (s_wifi_uart_next_seq > UINT32_MAX) return false;
    *out = (uint32_t)s_wifi_uart_next_seq++;
    return true;
}

static void wifi_control_results_locked(void)
{
    wifi_control_executor_result_t value;
    if (wifi_control_executor_take_result(&s_control, &value)) {
        wifi_command_result_t result = {
            .request = {
                .type = value.request.type == WIFI_CONTROL_ARM ? WIFI_COMMAND_ARM : WIFI_COMMAND_CMD,
                .request_id = value.request.request_id,
                .expected_boot_id = value.request.expected_boot_id,
                .ws_session_id = value.request.ws_session_id
            },
            .seq = value.seq, .control_id = value.request.control_id
        };
        (void)snprintf(result.status, sizeof(result.status), "%s", value.status);
        if (xQueueSend(s_wifi_command_result_queue, &result, 0) != pdPASS) {
            wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_OWNER_CLOSED, wifi_control_now());
        }
    }
    if (s_manual_stop_pending && (s_control.state.phase == WIFI_CONTROL_IDLE || s_control.state.phase == WIFI_CONTROL_BLOCKED)) {
        wifi_command_result_t result = {.request = s_manual_stop_request, .seq = s_manual_stop_seq};
        (void)snprintf(result.status, sizeof(result.status), "%s",
            s_control.state.phase == WIFI_CONTROL_IDLE ? "OK" : "STOP_UNCONFIRMED");
        (void)xQueueSend(s_wifi_command_result_queue, &result, 0);
        s_manual_stop_pending = false;
    }
    wifi_control_cleanup_locked();
}

/* UART_PARTIAL_TEST_BEGIN: all state is protected by s_stm_lock. */
typedef enum {
    UART_TEST_UNUSED, UART_TEST_QUEUED, UART_TEST_HOLD,
    UART_TEST_STOPPING, UART_TEST_DONE, UART_TEST_ABORTED
} uart_partial_test_phase_t;

static uart_partial_test_phase_t s_uart_test_phase;
static uint64_t s_uart_test_at_ms;
static bool s_uart_test_prefix_full;

/* Inserted inside UART_PARTIAL_TEST_BEGIN. Native tests compile these exact functions. */
typedef enum { WD_ARM, WD_ZERO, WD_TIMEOUT, WD_PROBE, WD_OBSERVE } uart_watchdog_phase_t;
static struct {
    uart_watchdog_phase_t phase;
    uint32_t seq[3], baseline_seq, drop, err, last_t_ms, ack_t_ms, cmd_t_ms, tel_floor;
    uint64_t started_ms, sent_ms, observed_ms;
    bool replied, proof, stop_confirmed;
    const char *problem;
} s_watchdog;

static bool wifi_watchdog_zero_locked(uint64_t now)
{
    const stm_telemetry_t *t = &s_stm_telemetry;
    return t->valid && now >= t->rx_ms && now - t->rx_ms < WIFI_CONTROL_TEL_MS &&
        (strcmp(t->state, "DISARMED") == 0 || strcmp(t->state, "ARMED") == 0) &&
        t->vx_mmps == 0 && t->w_mradps == 0 && t->left_pwm == 0 && t->right_pwm == 0 &&
        t->left_cps == 0 && t->right_cps == 0;
}

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
        s->tel.left_pwm == 0 && s->tel.right_pwm == 0 &&
        (WIFI_UART_PARTIAL_TEST_MODE != 3U || wifi_watchdog_zero_locked(now));
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
        if (WIFI_UART_PARTIAL_TEST_MODE == 3U && s_watchdog.problem == NULL)
            s_watchdog.problem = "CANCELLED";
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

static void wifi_watchdog_stop_locked(const char *problem, uint64_t now)
{
    if (problem != NULL && s_watchdog.problem == NULL) s_watchdog.problem = problem;
    s_uart_test_phase = UART_TEST_STOPPING;
    wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_MANUAL_STOP, now);
    wifi_control_cleanup_locked();
    ESP_LOGI(TAG, "AC-S06: cleanup proof=%u problem=%s", s_watchdog.proof ? 1U : 0U,
             s_watchdog.problem != NULL ? s_watchdog.problem : "NONE");
}

static bool wifi_watchdog_reply_locked(wifi_control_op_t op, uint32_t seq,
    bool ack, const char *code, uint32_t t_ms, uint64_t now)
{
    if (WIFI_UART_PARTIAL_TEST_MODE != 3U || s_uart_test_phase != UART_TEST_HOLD ||
        (s_watchdog.phase != WD_ARM && s_watchdog.phase != WD_ZERO &&
         s_watchdog.phase != WD_PROBE)) return false;
    const unsigned index = s_watchdog.phase == WD_ARM ? 0U :
                           s_watchdog.phase == WD_ZERO ? 1U : 2U;
    if (seq != s_watchdog.seq[index]) return false;
    const bool expected = op == (index == 0U ? WIFI_CONTROL_OP_ARM : WIFI_CONTROL_OP_CMD) &&
        (index < 2U ? ack : (!ack && code != NULL && strcmp(code, "NOT_ARMED") == 0));
    if (!expected || s_watchdog.replied || now < s_watchdog.sent_ms ||
        now - s_watchdog.sent_ms >= WIFI_CONTROL_ACK_MS || t_ms < s_watchdog.last_t_ms) {
        wifi_watchdog_stop_locked("BAD_OR_LATE_REPLY", now);
    } else {
        s_watchdog.replied = true;
        s_watchdog.ack_t_ms = t_ms;
        if (index == 1U) s_watchdog.cmd_t_ms = t_ms;
        ESP_LOGI(TAG, "AC-S06: reply step=%u seq=%" PRIu32 " %s t_ms=%" PRIu32,
                 index, seq, ack ? "ACK" : "NOT_ARMED", t_ms);
    }
    return true;
}

/* Same UART task as production, fixed zero frames only, no retries or auto re-arm.
 * The production owner remains IDLE: its early source-loss DISARM would otherwise
 * preempt the STM's 300 ms watchdog. Normal ingress/tickets stay disabled in mode 3. */
static void wifi_watchdog_step(void)
{
    char frame[WIFI_CONTROL_UART_FRAME_SIZE];
    int length = 0, index = -1;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const uint64_t now = wifi_control_now();
    const stm_telemetry_t *t = &s_stm_telemetry;
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), now);
    wifi_control_cleanup_locked();
    if (s_uart_test_phase == UART_TEST_QUEUED) {
        if (now < s_uart_test_at_ms || now - s_uart_test_at_ms >= WIFI_CONTROL_QUEUE_MS ||
            !wifi_uart_test_ready_locked(now) || strcmp(t->state, "DISARMED") != 0 ||
            t->err == UINT32_MAX || t->t_ms > UINT32_MAX - 2000U) {
            s_uart_test_phase = UART_TEST_ABORTED;
            ESP_LOGW(TAG, "AC-S06: not sent (expired/not ready/counter boundary)");
        } else {
            memset(&s_watchdog, 0, sizeof(s_watchdog));
            bool allocated = true;
            for (unsigned i = 0U; i < 3U && allocated; ++i)
                allocated = wifi_uart_test_sequence_locked(&s_watchdog.seq[i]);
            if (!allocated) {
                s_uart_test_phase = UART_TEST_ABORTED;
                ESP_LOGW(TAG, "AC-S06: not sent (sequence exhausted)");
            } else {
                s_watchdog.started_ms = now;
                s_watchdog.baseline_seq = t->last_seq;
                s_watchdog.drop = t->drop; s_watchdog.err = t->err;
                s_watchdog.last_t_ms = t->t_ms;
                s_uart_test_phase = UART_TEST_HOLD;
                index = 0;
            }
        }
    } else if (s_uart_test_phase == UART_TEST_HOLD) {
        const bool armed = strcmp(t->state, "ARMED") == 0;
        const bool timed_out = strcmp(t->state, "DISARMED") == 0 &&
            strcmp(t->reason, "CMD_TIMEOUT") == 0 && t->last_seq == s_watchdog.seq[1] &&
            t->t_ms >= s_watchdog.cmd_t_ms &&
            t->command_age_ms >= 300U && t->command_age_ms != UINT32_MAX;
        /* command_age_ms is measured from CMD acceptance. ACK t_ms can be a
         * later HAL tick; subtracting it would falsely reject the 300 ms edge. */
        const bool probing = s_watchdog.phase == WD_PROBE || s_watchdog.phase == WD_OBSERVE;
        if (!wifi_control_ready_locked() || s_control.state.phase != WIFI_CONTROL_IDLE ||
            s_manual_stop_pending || s_wifi_command_owner_session_id != 0U ||
            s_control.queued || s_control.waiting || s_control.prepared || s_control.have_result ||
            !wifi_watchdog_zero_locked(now) || now < s_watchdog.started_ms ||
            now - s_watchdog.started_ms >= 2000U || t->t_ms < s_watchdog.last_t_ms ||
            t->drop != s_watchdog.drop ||
            (t->err != s_watchdog.err && (!probing || t->err != s_watchdog.err + 1U))) {
            wifi_watchdog_stop_locked("STATE_FRESHNESS_OUTPUT_OR_COUNTER", now);
        } else {
            s_watchdog.last_t_ms = t->t_ms;
            const bool tel_after_tx = s_stm_tel_count != s_watchdog.tel_floor &&
                t->rx_ms >= s_watchdog.sent_ms && t->t_ms >= s_watchdog.ack_t_ms;
            if ((s_watchdog.phase == WD_ARM || s_watchdog.phase == WD_ZERO ||
                 s_watchdog.phase == WD_PROBE) && !s_watchdog.replied &&
                now - s_watchdog.sent_ms >= WIFI_CONTROL_ACK_MS) {
                wifi_watchdog_stop_locked("REPLY_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_ARM) {
                if ((armed && (t->last_seq != s_watchdog.seq[0] || strcmp(t->reason, "NONE") != 0)) ||
                    (!armed && t->last_seq != s_watchdog.baseline_seq))
                    wifi_watchdog_stop_locked("ARM_STATE_MISMATCH", now);
                else if (s_watchdog.replied && tel_after_tx && armed) index = 1;
                else if (now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("ARM_TEL_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_ZERO) {
                if (!armed || strcmp(t->reason, "NONE") != 0 ||
                    (t->last_seq != s_watchdog.seq[0] && t->last_seq != s_watchdog.seq[1]))
                    wifi_watchdog_stop_locked("ZERO_STATE_MISMATCH", now);
                else if (s_watchdog.replied && tel_after_tx && t->last_seq == s_watchdog.seq[1] &&
                         t->command_age_ms < 300U) {
                    s_watchdog.phase = WD_TIMEOUT;
                    ESP_LOGI(TAG, "AC-S06: zero accepted; waiting CMD_TIMEOUT seq=%" PRIu32, t->last_seq);
                } else if (now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("ZERO_TEL_TIMEOUT", now);
            } else if (s_watchdog.phase == WD_TIMEOUT) {
                if (timed_out) {
                    ESP_LOGI(TAG, "AC-S06: CMD_TIMEOUT seq=%" PRIu32 " age=%" PRIu32,
                             t->last_seq, t->command_age_ms);
                    index = 2;
                } else if (!armed || t->last_seq != s_watchdog.seq[1] ||
                           strcmp(t->reason, "NONE") != 0 || t->command_age_ms >= 300U ||
                           now - s_watchdog.sent_ms >= 700U)
                    wifi_watchdog_stop_locked("EXPECTED_CMD_TIMEOUT_MISSING", now);
            } else if (probing) {
                if (!timed_out) wifi_watchdog_stop_locked("CMD_REARMED_OR_STATE_CHANGED", now);
                else if (s_watchdog.phase == WD_PROBE && s_watchdog.replied && tel_after_tx &&
                         t->err == s_watchdog.err + 1U) {
                    s_watchdog.phase = WD_OBSERVE;
                    s_watchdog.observed_ms = now;
                    s_watchdog.tel_floor = s_stm_tel_count;
                } else if (s_watchdog.phase == WD_PROBE && now - s_watchdog.sent_ms >= 250U)
                    wifi_watchdog_stop_locked("REJECTION_TEL_TIMEOUT", now);
                else if (s_watchdog.phase == WD_OBSERVE && t->err != s_watchdog.err + 1U)
                    wifi_watchdog_stop_locked("ERROR_COUNTER_CHANGED", now);
                else if (s_watchdog.phase == WD_OBSERVE && now - s_watchdog.observed_ms >= 200U &&
                         s_stm_tel_count - s_watchdog.tel_floor >= 2U) {
                    s_watchdog.proof = true;
                    wifi_watchdog_stop_locked(NULL, now);
                }
            }
        }
    } else if (s_uart_test_phase == UART_TEST_STOPPING &&
               (s_control.state.phase == WIFI_CONTROL_IDLE || s_control.state.phase == WIFI_CONTROL_BLOCKED)) {
        const bool stopped = s_control.state.phase == WIFI_CONTROL_IDLE &&
            wifi_watchdog_zero_locked(now) && strcmp(t->state, "DISARMED") == 0 &&
            strcmp(t->reason, "DISARM") == 0 && t->last_seq == s_control.state.confirm_seq &&
            t->t_ms >= s_watchdog.last_t_ms && t->drop == s_watchdog.drop &&
            t->err == s_watchdog.err + 1U;
        s_watchdog.stop_confirmed = stopped;
        if (!stopped && s_watchdog.problem == NULL) s_watchdog.problem = "CLEANUP_UNCONFIRMED";
        s_uart_test_phase = UART_TEST_DONE;
        ESP_LOGI(TAG, "AC-S06: end checks_ok=%u stop_confirmed=%u problem=%s; capture and manual re-arm review required",
            s_watchdog.proof && s_watchdog.problem == NULL && stopped ? 1U : 0U,
            stopped ? 1U : 0U, s_watchdog.problem != NULL ? s_watchdog.problem : "NONE");
    }
    if (index >= 0 && s_uart_test_phase == UART_TEST_HOLD) {
        s_watchdog.phase = index == 0 ? WD_ARM : index == 1 ? WD_ZERO : WD_PROBE;
        s_watchdog.replied = false; s_watchdog.ack_t_ms = 0U;
        s_watchdog.sent_ms = now; s_watchdog.tel_floor = s_stm_tel_count;
        length = index == 0 ? snprintf(frame, sizeof(frame), "ARM,seq=%" PRIu32 "\n", s_watchdog.seq[index]) :
            snprintf(frame, sizeof(frame), "CMD,seq=%" PRIu32 ",vx_mmps=0,w_mradps=0,timeout_ms=300\n", s_watchdog.seq[index]);
        if (length <= 0 || (size_t)length >= sizeof(frame)) {
            length = 0; wifi_watchdog_stop_locked("FORMAT_FAILED", now);
        }
    }
    xSemaphoreGive(s_stm_lock);
    if (length <= 0) return;
    /* A concurrent manual stop cannot retract this committed frame. The existing
     * priority CAN+LF/DISARM follows; no subsequent test frame is committed. */
    const int written = uart_write_bytes(STM_UART_PORT, frame, (size_t)length);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    if (written != length && s_uart_test_phase == UART_TEST_HOLD)
        wifi_watchdog_stop_locked("SHORT_WRITE", wifi_control_now());
    xSemaphoreGive(s_stm_lock);
    ESP_LOGI(TAG, "AC-S06: TX step=%d seq=%" PRIu32 " written=%d/%d", index,
             s_watchdog.seq[index], written, length);
}

/* Called only by stm_uart_rx_task, before normal control/command dispatch.
 * Fixed prefix -> 100 ms receive/poll interval -> existing CAN+LF DISARM.
 * No raw input, no LF-only flush, no retry, no new UART writer task. */
static void wifi_uart_test_step(void)
{
    if (WIFI_UART_PARTIAL_TEST_MODE == 0U) return;
    if (WIFI_UART_PARTIAL_TEST_MODE == 3U) { wifi_watchdog_step(); return; }
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

/* Nonblocking state progress. Physical writes occur only here or W5/startup. */
static void wifi_control_step(void)
{
    wifi_control_tx_t tx;
    bool have_tx = false;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    wifi_control_executor_poll(&s_control, wifi_control_ready_locked(), wifi_control_now());
    wifi_control_cleanup_locked();
    wifi_control_results_locked();
    if (!s_control.prepared && (s_control.queued || s_control.state.need_disarm)) {
        uint32_t seq;
        if (wifi_uart_allocate_seq(&seq)) {
            have_tx = wifi_control_executor_take_tx(&s_control, seq, wifi_control_now(), &tx);
            if (have_tx && tx.op == WIFI_CONTROL_OP_DISARM && s_manual_stop_pending) s_manual_stop_seq = seq;
        } else {
            wifi_control_executor_stop(&s_control, WIFI_CONTROL_REASON_TX_FAILED, wifi_control_now());
            wifi_control_cleanup_locked();
        }
    }
    xSemaphoreGive(s_stm_lock);
    if (!have_tx) return;
    /* take_tx commits this frame. A concurrent close may cancel future input,
     * but cannot retract this committed/in-flight UART write. DISARM follows. */
    const int written = uart_write_bytes(STM_UART_PORT, tx.bytes, tx.length);
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    (void)wifi_control_executor_tx_complete(&s_control, written, wifi_control_now());
    wifi_control_results_locked();
    xSemaphoreGive(s_stm_lock);
    ESP_LOGI(TAG, "CONTROL TX: op=%u seq=%" PRIu32 " written=%d/%u",
        (unsigned)tx.op, tx.seq, written, (unsigned)tx.length);
}

static bool wifi_control_handle_response(const char *line)
{
    const bool ack = strncmp(line, "ACK,", 4U) == 0;
    const bool error = strncmp(line, "ERR,", 4U) == 0;
    if (!ack && !error) return false;
    const size_t length = strlen(line);
    unsigned commas = 0U;
    for (const char *p = line; *p != '\0'; ++p) if (*p == ',') ++commas;
    uint32_t seq, t_ms;
    char type[16], code[32];
    if (length == 0U || line[length - 1U] == ',' || strstr(line, ",,") != NULL ||
        commas != (ack ? 3U : 4U) || !stm_parse_u32_field(line, "seq=", &seq) ||
        !stm_parse_u32_field(line, "t_ms=", &t_ms) ||
        !stm_parse_text_field(line, "type=", type, sizeof(type)) ||
        (error && !stm_parse_text_field(line, "code=", code, sizeof(code)))) return false;
    wifi_control_op_t op;
    if (strcmp(type, "ARM") == 0) op = WIFI_CONTROL_OP_ARM;
    else if (strcmp(type, "CMD") == 0) op = WIFI_CONTROL_OP_CMD;
    else if (strcmp(type, "DISARM") == 0) op = WIFI_CONTROL_OP_DISARM;
    else return false;
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const bool test_matched = wifi_watchdog_reply_locked(op, seq, ack,
        ack ? NULL : code, t_ms, wifi_control_now());
    const bool matched = test_matched ||
        wifi_control_executor_reply(&s_control, op, seq, ack, t_ms, wifi_control_now());
    wifi_control_results_locked();
    xSemaphoreGive(s_stm_lock);
    if (matched) ESP_LOGI(TAG, "CONTROL RX MATCH: %s seq=%" PRIu32, type, seq);
    return matched;
}


/* 요청을 끝내고, 살아 있는 소유 연결의 결과만 큐에 복사한다. */
static void wifi_command_finish(const char *status)
{
    if (!s_wifi_uart_pending.active) {
        return;
    }

    const wifi_command_request_t request = s_wifi_uart_pending.request;
    wifi_command_result_t result = {
        .request = request,
        .seq = s_wifi_uart_pending.seq
    };
    const int length = snprintf(result.status, sizeof(result.status), "%s", status);

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const bool owned = s_wifi_command_owner_session_id == request.ws_session_id;
    bool result_queued = false;

    if (owned) {
        /* 기다리지 않고 값만 복사한다. 네트워크 송신은 HTTP 태스크의 역할이다. */
        if (length >= 0 && (size_t)length < sizeof(result.status)) {
            result_queued = xQueueSend(s_wifi_command_result_queue, &result, 0) == pdPASS;
        }
        s_wifi_command_owner_session_id = 0U;
    }
    xSemaphoreGive(s_stm_lock);

    s_wifi_uart_pending.active = false;

    ESP_LOGI(
        TAG,
        "W5 RESULT: request=%" PRIu32 " session=%" PRIu32
        " seq=%" PRIu32 " status=%s",
        request.request_id, request.ws_session_id,
        result.seq, owned ? status : "CONNECTION_CLOSED");

    if (owned && !result_queued) {
        ESP_LOGW(TAG, "W5 result queue unavailable; request=%" PRIu32, request.request_id);
    }
}

/* 기다리며 멈추는 함수가 아니라, 대기 요청이 유효한지 확인한다. */
static bool wifi_command_pending_valid(void)
{
    if (!s_wifi_uart_pending.active) {
        return false;
    }

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const bool owned =
        s_wifi_command_owner_session_id ==
            s_wifi_uart_pending.request.ws_session_id;
    xSemaphoreGive(s_stm_lock);

    if (!owned) {
        wifi_command_finish("CONNECTION_CLOSED");
        return false;
    }

    const uint64_t now_ms =
        (uint64_t)esp_timer_get_time() / 1000U;
    
    if (now_ms - s_wifi_uart_pending.sent_ms >=
        WIFI_COMMAND_RESPONSE_MS) {
        wifi_command_finish("TIMEOUT");
        return false;
    }

    return true;
}

/* UART 수신 루프에서 호출: 대기 요청 점검 또는 새 요청 한 개 송신. */
static void wifi_command_step(void)
{
    if (s_wifi_uart_pending.active) {
        (void)wifi_command_pending_valid();
        return;
    }

    if (s_stm_startup.state != STM_STARTUP_READY &&
        s_stm_startup.state != STM_STARTUP_FAILED) {
        return;
    }

    wifi_command_request_t request = {0};

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const BaseType_t received = xQueueReceive(
        s_wifi_command_queue, &request, 0);
    const bool owned =
        received == pdPASS && request.ws_session_id != 0U &&
        s_wifi_command_owner_session_id == request.ws_session_id;
    xSemaphoreGive(s_stm_lock);

    if (received != pdPASS || !owned) {
        return;
    }

    s_wifi_uart_pending = (wifi_uart_pending_t) {
        .active = true,
        .request = request
    };

    if (request.expected_boot_id != s_boot_id) {
        wifi_command_finish("BOOT_MISMATCH");
        return;
    }

    if (request.type != WIFI_COMMAND_PING &&
        request.type != WIFI_COMMAND_DISARM) {
        wifi_command_finish("UNSUPPORTED");
        return;
    }

    if (!wifi_uart_allocate_seq(&s_wifi_uart_pending.seq)) {
        wifi_command_finish("SEQ_EXHAUSTED");
        return;
    }

    const char *command =
        wifi_command_name(request.type);
    char line[48];
    const int length = snprintf(
        line, sizeof(line),
        "%s%s,seq=%" PRIu32 "\n",
        request.type == WIFI_COMMAND_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
        command, s_wifi_uart_pending.seq);

    if (length <= 0 || (size_t)length >= sizeof(line)) {
        wifi_command_finish("FORMAT_ERROR");
        return;
    }

    /* 송신 직전에 연결 소유권과 요청 나이를 다시 확인한다. */
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const bool still_owned = s_wifi_command_owner_session_id == request.ws_session_id;
    const uint64_t now_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const bool expired = now_ms - request.accepted_ms >= WIFI_COMMAND_RESPONSE_MS;
    xSemaphoreGive(s_stm_lock);
    int written = -1;
    if (still_owned && !expired) {
        s_wifi_uart_pending.sent_ms = now_ms;
        written = uart_write_bytes(STM_UART_PORT, line, (size_t)length);
    }

    if (!still_owned) {
        wifi_command_finish("CONNECTION_CLOSED");
    } else if (expired) {
        wifi_command_finish("QUEUE_EXPIRED");
    } else if (written != length) {
        wifi_command_finish("TX_ERROR");
    } else {
        ESP_LOGI(TAG, "W5 TX UART1: %s,seq=%" PRIu32 " request=%" PRIu32 " session=%" PRIu32,
            command, s_wifi_uart_pending.seq, request.request_id, request.ws_session_id);
    }
}

/* 사용자 요청의 ACK/PONG/ERR만 처리한다. TEL은 기존 경로로 보낸다. */
static bool wifi_command_handle_response(const char *line)
{
    const bool pong = strncmp(line, "PONG,", 5U) == 0;
    const bool ack = strncmp(line, "ACK,", 4U) == 0;
    const bool error = strncmp(line, "ERR,", 4U) == 0;

    if (!s_wifi_uart_pending.active || (!pong && !ack && !error)) {
        return false;
    }

    /* 이미 제한 시간이 지난 응답은 성공으로 인정하지 않는다. */
    if (!wifi_command_pending_valid()) {
        return true;
    }

    unsigned commas = 0U;
    for (const char *pos = line; *pos != '\0'; ++pos) {
        if (*pos == ',') {
            ++commas;
        }
    }

    const unsigned expected_commas = pong ? 2U : (ack ? 3U : 4U);
    const size_t length = strlen(line);
    uint32_t seq;
    uint32_t stm_time_ms;
    char type[16];
    char code[32];

    if (line[length - 1U] == ',' || strstr(line, ",,") != NULL ||
        commas != expected_commas ||
        !stm_parse_u32_field(line, "seq=", &seq) ||
        !stm_parse_u32_field(line, "t_ms=", &stm_time_ms) ||
        ((ack || error) && !stm_parse_text_field(line, "type=", type, sizeof(type))) ||
        (error && !stm_parse_text_field(line, "code=", code, sizeof(code)))) {
        ESP_LOGW(TAG, "W5 ignored: malformed UART response");
        return true;
    }

    if (seq != s_wifi_uart_pending.seq) {
        ESP_LOGW(TAG, "W5 ignored: non-matching seq=%" PRIu32, seq);
        return true;
    }

    const bool ping_request = s_wifi_uart_pending.request.type == WIFI_COMMAND_PING;
    const char *expected_type = ping_request ? "PING" : "DISARM";

    if (error && strcmp(type, expected_type) == 0) {
        ESP_LOGW(TAG, "W5 STM ERR: seq=%" PRIu32 " code=%s", seq, code);
        wifi_command_finish("STM_ERROR");
    } else if ((pong && ping_request) ||
               (ack && !ping_request && strcmp(type, "DISARM") == 0)) {
        ESP_LOGI(TAG, "W5 RX MATCH: seq=%" PRIu32 " t_ms=%" PRIu32, seq, stm_time_ms);
        wifi_command_finish("OK");
    } else {
        ESP_LOGW(TAG, "W5 ignored: response type does not match request");
    }

    return true;
}

/* ACK/PONG이면 처리 후 true, 다른 프레임이면 false를 반환한다. */
static bool stm_startup_handle_response(const char *line)
{
    const bool ack = strncmp(line, "ACK,", 4) == 0;
    const bool pong = strncmp(line, "PONG,", 5) == 0;

    if (!ack && !pong) {
        return false;
    }

    const size_t length = strlen(line);
    if (line[length - 1U] == ',' ||
        strstr(line, ",,") != NULL) {
        ESP_LOGW(TAG, "STARTUP: malformed response: %s", line);
        return true;
    }

    uint32_t seq;
    char type[16];

    if (!stm_parse_u32_field(line, "seq=", &seq) ||
        (ack && !stm_parse_text_field(
            line, "type=", type, sizeof(type)))) {
        ESP_LOGW(TAG, "STARTUP: response parse rejected: %s", line);
        return true;
    }

    if (ack) {
        ESP_LOGI(
            TAG, "RX ACK: seq=%" PRIu32 " type=%s",
            seq, type);

        if (s_stm_startup.state == STM_STARTUP_WAIT_DISARM_ACK &&
            seq == s_stm_startup.disarm_seq &&
            strcmp(type, "DISARM") == 0) {
            s_stm_startup.disarm_ack = true;
        } else {
            ESP_LOGW(TAG, "STARTUP: ignored non-matching ACK");
        }
    } else {
        ESP_LOGI(TAG, "RX PONG: seq=%" PRIu32, seq);

        if (s_stm_startup.state == STM_STARTUP_WAIT_PONG &&
            seq == s_stm_startup.ping_seq) {
            s_stm_startup.pong = true;
        } else {
            ESP_LOGW(TAG, "STARTUP: ignored non-matching PONG");
        }
    }

    return true;
}

static void stm_uart_handle_line(const char *line)
{
    if (wifi_control_handle_response(line)) {
        return;
    }

    if (wifi_command_handle_response(line)) {
        return;
    }

    if (stm_startup_handle_response(line)) {
        return;
    }

    if (strncmp(line, "TEL,", 4) != 0) {
        ESP_LOGI(TAG, "STM RX: %s", line);
        return;
    }

    stm_telemetry_t parsed = {0};

    if (!stm_parse_tel(line, &parsed)) {
        ESP_LOGW(TAG, "STM TEL rejected: %s", line);
        return;
    }

    parsed.rx_ms = (uint64_t)esp_timer_get_time() / 1000U;
    parsed.valid = true;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_stm_telemetry = parsed;
    const wifi_control_tel_t tel = {
        .state = strcmp(parsed.state, "ARMED") == 0 ? WIFI_CONTROL_STM_ARMED :
                 strcmp(parsed.state, "DISARMED") == 0 ? WIFI_CONTROL_STM_DISARMED : WIFI_CONTROL_STM_FAULT,
        .t_ms = parsed.t_ms, .last_seq = parsed.last_seq,
        .command_age_ms = parsed.command_age_ms,
        .vx_mmps = parsed.vx_mmps, .w_mradps = parsed.w_mradps,
        .left_pwm = parsed.left_pwm, .right_pwm = parsed.right_pwm
    };
    wifi_control_executor_tel(&s_control, &tel, wifi_control_now());
    wifi_control_cleanup_locked();
    const uint32_t count = ++s_stm_tel_count;
    xSemaphoreGive(s_stm_lock);

    ESP_LOGI(TAG,
        "STM TEL #%" PRIu32 " t_ms=%" PRIu32
        " state=%s reason=%s"
        " pwm=%" PRIi32 "/%" PRIi32
        " cps=%" PRIi32 "/%" PRIi32
        " drop=%" PRIu32 " err=%" PRIu32,
        count, parsed.t_ms, parsed.state, parsed.reason,
        parsed.left_pwm, parsed.right_pwm,
        parsed.left_cps, parsed.right_cps,
        parsed.drop, parsed.err);
}

static void stm_uart_handle_byte(uint8_t byte)
{
    if (byte == '\n') {
        if (s_stm_discard_until_lf) {
            s_stm_discard_until_lf = false;
            s_stm_rx_length = 0U;
            return;
        }

        /* CRLF 형식이면 마지막 CR을 제거한다. */
        if (s_stm_rx_length > 0U &&
            s_stm_rx_line[s_stm_rx_length - 1U] == '\r') {
            --s_stm_rx_length;
        }

        s_stm_rx_line[s_stm_rx_length] = '\0';

        if (s_stm_rx_length > 0U) {
            stm_uart_handle_line(s_stm_rx_line);
        }

        s_stm_rx_length = 0U;
        return;
    }

    if (s_stm_discard_until_lf) {
        return;
    }

    const bool embedded_cr =
        s_stm_rx_length > 0U &&
        s_stm_rx_line[s_stm_rx_length - 1U] == '\r';
    
    const bool invalid_byte =
        (byte < 0x20U && byte != '\r') || byte > 0x7eU;

    if (embedded_cr || invalid_byte) {
        ESP_LOGW(TAG, "STM RX invalid line; discard until LF");
        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = true;
        return;
    }

    if (s_stm_rx_length >= sizeof(s_stm_rx_line) - 1U) {
        ESP_LOGW(TAG, "STM RX line overflow; discard until LF");
        s_stm_rx_length = 0U;
        s_stm_discard_until_lf = true;
        return;
    }

    s_stm_rx_line[s_stm_rx_length++] = (char)byte;
}

static void stm_startup_publish_status(void)
{
    const char *status = "FAILED";

    switch (s_stm_startup.state) {
    case STM_STARTUP_SETTLE:
        status = "SETTLE";
        break;
    case STM_STARTUP_SYNC_WAIT:
        status = "SYNC_WAIT";
        break;
    case STM_STARTUP_WAIT_DISARM_ACK:
        status = "WAIT_DISARM_ACK";
        break;
    case STM_STARTUP_WAIT_PONG:
        status = "WAIT_PONG";
        break;
    case STM_STARTUP_READY:
        status = "READY";
        break;
    case STM_STARTUP_FAILED:
    default:
        break;
    }

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    s_stm_startup_status = status;
    xSemaphoreGive(s_stm_lock);
}

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

static void wifi_event(
    void *arg, esp_event_base_t base, int32_t id, void *event_data)
{
    (void)arg;
    (void)event_data;

#if WIFI_LINK_USE_AP
    if (base == WIFI_EVENT && id == WIFI_EVENT_AP_START) {
        server_start();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STOP) {
        server_stop();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STACONNECTED) {
        ESP_LOGI(TAG, "AP client connected");
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STADISCONNECTED) {
        ESP_LOGI(TAG, "AP client disconnected");
    }
#else
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        ESP_ERROR_CHECK(esp_wifi_connect());
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        server_stop();
        if (s_retry_count < 5U) {
            ++s_retry_count;
            ESP_LOGW(TAG, "STA reconnect attempt %u/5", s_retry_count);
            ESP_ERROR_CHECK(esp_wifi_connect());
        } else {
            ESP_LOGE(TAG, "STA retry limit reached; reboot to retry");
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        s_retry_count = 0U;
        server_start();
    }
#endif
}

void app_main(void)
{
    const size_t ssid_length = strlen(WIFI_LINK_SSID);
    const size_t password_length = strlen(WIFI_LINK_PASSWORD);

    if (ssid_length == 0U || ssid_length > 32U ||
        password_length < 8U || password_length > 63U ||
        strcmp(WIFI_LINK_PASSWORD, "CHANGE_ME") == 0) {
        ESP_LOGE(TAG, "Set a valid private SSID/password in wifi_link_config.h");
        return;
    }

    s_server_lock = xSemaphoreCreateMutex();
    s_stm_lock = xSemaphoreCreateMutex();
    s_wifi_command_queue = xQueueCreate(
        WIFI_COMMAND_QUEUE_LENGTH,
        sizeof(wifi_command_request_t));
    s_wifi_command_result_queue = xQueueCreate(
        WIFI_COMMAND_RESULT_QUEUE_LENGTH,
        sizeof(wifi_command_result_t));

    if (s_server_lock == NULL || s_stm_lock == NULL ||
        s_wifi_command_queue == NULL || s_wifi_command_result_queue == NULL) {
        ESP_LOGE(TAG, "Mutex/command/result queue allocation failed");
        return;
    }

    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES ||
        result == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);

    s_boot_id = esp_random();
    wifi_control_executor_init(&s_control, s_boot_id);
    wifi_control_ticket_pool_init(&s_ticket_pool, s_boot_id);
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

#if WIFI_LINK_USE_AP
    s_netif = esp_netif_create_default_wifi_ap();
#else
    s_netif = esp_netif_create_default_wifi_sta();
#endif
    if (s_netif == NULL) {
        ESP_LOGE(TAG, "Network interface allocation failed");
        return;
    }

    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_event_handler_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL));

    wifi_config_t wifi = {0};
#if WIFI_LINK_USE_AP
    memcpy(wifi.ap.ssid, WIFI_LINK_SSID, ssid_length);
    memcpy(wifi.ap.password, WIFI_LINK_PASSWORD, password_length);
    wifi.ap.ssid_len = (uint8_t)ssid_length;
    wifi.ap.channel = 6;
    wifi.ap.max_connection = 2;
    wifi.ap.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi));
#else
    memcpy(wifi.sta.ssid, WIFI_LINK_SSID, ssid_length);
    memcpy(wifi.sta.password, WIFI_LINK_PASSWORD, password_length);
    wifi.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_event_handler_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi));
#endif
    
    stm_uart_init();

    if (xTaskCreate(
            stm_uart_rx_task, "stm_uart_rx",
            6144, NULL, 5, NULL) != pdPASS) {
        ESP_LOGE(TAG, "STM UART RX task allocation failed");
        return;
    }

    ESP_LOGI(TAG, "Wi-Fi + STM UART RX: mode=%s boot_id=%" PRIu32,
             WIFI_LINK_MODE_NAME, s_boot_id);
#if !WIFI_LINK_USE_AP
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
    ESP_LOGI(TAG, "Wi-Fi power save disabled for control latency");
#endif
    ESP_ERROR_CHECK(esp_wifi_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(CONTROL_PUMP_MS));
        ws_schedule();
    }
}
