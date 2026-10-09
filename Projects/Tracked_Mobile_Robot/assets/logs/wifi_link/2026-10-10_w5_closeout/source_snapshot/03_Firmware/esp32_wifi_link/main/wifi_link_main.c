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
#define WS_MAX_CLIENTS 4U
#define WS_PERIOD_MS 100U
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
    WIFI_COMMAND_DISARM
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
} wifi_command_request_t;

/* HTTP 태스크가 넣고 UART 태스크가 꺼낸다. */
static QueueHandle_t s_wifi_command_queue;

/* UART 태스크가 넣고 HTTP 태스크가 꺼내는 완료 결과. */
typedef struct {
    wifi_command_request_t request;
    uint32_t seq;
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
    "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP Wi-Fi Link</title></head><body>"
    "<h1>로봇 상태</h1><p>STM32 UART → ESP32 Wi-Fi → 브라우저</p>"
    "<p id='link'>연결 확인 중</p>"
    "<p id='stm'>STM TEL 수신 대기</p>"
    "<p id='startup'>부팅 응답 새 상태 확인 대기</p>"
    "<p>READY는 이번 ESP 부팅 때 응답 확인을 마쳤다는 뜻입니다. "
    "현재 통신 상태는 TEL 표시에서 확인하세요.</p>"
    "<p><button id='ping' type='button' disabled>PING</button> "
    "<button id='disarm' type='button' disabled>DISARM</button></p>"
    "<p id='command_notice'>명령 송신 대기</p>"
    "<p id='command_result'>명령 결과 수신 대기</p>"
    "<pre id='data'></pre><script>"
    "const link=document.getElementById('link');"
    "const stm=document.getElementById('stm');"
    "const startup=document.getElementById('startup');"
    "const data=document.getElementById('data');"
    "const commandResult=document.getElementById('command_result');"
    "const pingButton=document.getElementById('ping');"
    "const disarmButton=document.getElementById('disarm');"
    "const commandNotice=document.getElementById('command_notice');"
    "let currentBootId=null;"
    "let startupFinished=false;"
    "let nextRequestId=1;"
    "let ignoredThroughId=0;"
    "let pendingCommand=null;"
    "let commandTimer=null;"
    "let cooldownTimer=null;"
    "let nextSendAt=0;"
    "let socket=null;"
    "let retryTimer=null;"
    "let watchdog=null;"
    "const startupLabels={"
    " SETTLE:'초기 안정 대기',SYNC_WAIT:'UART 줄 동기화 대기',"
    " WAIT_DISARM_ACK:'DISARM 응답 대기',WAIT_PONG:'PING 응답 대기',"
    " READY:'완료 (READY)',FAILED:'실패 (FAILED)'"
    "};"
    "const resultLabels={"
    " OK:'응답 확인',TIMEOUT:'응답 시간 초과',"
    " STM_ERROR:'STM 명령 거부',TX_ERROR:'UART 송신 실패',"
    " RX_ERROR:'UART 수신 실패',QUEUE_EXPIRED:'대기 시간 초과',"
    " BOOT_MISMATCH:'ESP 부팅 식별값 불일치',UNSUPPORTED:'미지원 명령',"
    " SEQ_EXHAUSTED:'UART 번호 소진',FORMAT_ERROR:'송신 형식 오류',"
    " CONNECTION_CLOSED:'요청 연결 종료'"
    "};"
    "function validCommandResult(r){"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;"
    " return r&&typeof r==='object'&&!Array.isArray(r)&&"
    "  r.kind==='command_result'&&u32(r.boot_id)&&"
    "  u32(r.request_id)&&r.request_id>0&&"
    "  u32(r.session_id)&&r.session_id>0&&u32(r.seq)&&"
    "  ['PING','DISARM'].includes(r.cmd)&&"
    "  ['OK','TIMEOUT','STM_ERROR','TX_ERROR','RX_ERROR',"
    "   'QUEUE_EXPIRED','BOOT_MISMATCH','UNSUPPORTED',"
    "   'SEQ_EXHAUSTED','FORMAT_ERROR','CONNECTION_CLOSED'].includes(r.status);"
    "}"
    "const noticeLabels={"
    " QUEUED:'ESP 접수 · STM 응답 확인 중',BAD_FORMAT:'명령 형식 오류',"
    " BOOT_MISMATCH:'ESP 부팅 식별값 불일치',STARTUP_PENDING:'부팅 확인 진행 중',"
    " DUPLICATE:'이미 접수한 요청 번호',RATE_LIMIT:'요청 간격이 너무 짧음',"
    " BUSY:'다른 요청 처리 중',QUEUE_FULL:'요청 큐 사용 불가'"
    "};"
    "function validCommandNotice(r){"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;"
    " if(!r||typeof r!=='object'||Array.isArray(r)||"
    "    r.kind!=='command_notice'||!u32(r.boot_id)||!u32(r.session_id))return false;"
    " const identified=u32(r.request_id)&&r.request_id>0&&"
    "  ['PING','DISARM'].includes(r.cmd);"
    " if(r.stage==='ACCEPTED')return identified&&r.session_id>0&&r.reason==='QUEUED';"
    " return r.stage==='REJECTED'&&"
    "  ['BAD_FORMAT','BOOT_MISMATCH','STARTUP_PENDING','DUPLICATE',"
    "   'RATE_LIMIT','BUSY','QUEUE_FULL'].includes(r.reason)&&"
    "  (r.reason==='BAD_FORMAT'?r.request_id===null&&r.cmd===null:identified);"
    "}"
    "function updateButtons(){"
    " clearTimeout(cooldownTimer);cooldownTimer=null;"
    " const wait=nextSendAt-performance.now();"
    " const ready=socket!==null&&socket.readyState===WebSocket.OPEN&&"
    "  currentBootId!==null&&startupFinished;"
    " const blocked=!ready||pendingCommand!==null||nextRequestId>4294967295||wait>0;"
    " pingButton.disabled=blocked;disarmButton.disabled=blocked;"
    " if(ready&&pendingCommand===null&&wait>0){"
    "  cooldownTimer=setTimeout(updateButtons,Math.ceil(wait));"
    " }"
    "}"
    "function clearPending(){"
    " clearTimeout(commandTimer);commandTimer=null;pendingCommand=null;"
    "}"
    "function cancelCommand(reason){"
    " const pending=pendingCommand;clearPending();"
    " commandResult.textContent=pending?pending.cmd+' 요청 '+pending.id+"
    "  ': 결과 확인 불가 · '+reason:reason+' · 새 명령 결과 수신 대기';"
    "}"
    "function sendCommand(cmd){"
    " if(!['PING','DISARM'].includes(cmd))return;"
    " updateButtons();"
    " if(pingButton.disabled){"
    "  commandNotice.textContent='지금은 새 요청을 보낼 수 없습니다.';return;"
    " }"
    " const ws=socket;"
    " const pending={id:nextRequestId++,cmd,boot:currentBootId,session:null,accepted:false};"
    " pendingCommand=pending;nextSendAt=performance.now()+500;"
    " commandNotice.textContent='브라우저 송신 · ESP 접수 확인 전';"
    " commandResult.textContent=cmd+' 요청 '+pending.id+': 결과 대기';"
    " updateButtons();"
    " commandTimer=setTimeout(()=>{"
    "  if(socket!==ws||pendingCommand!==pending)return;"
    "  ignoredThroughId=Math.max(ignoredThroughId,pending.id);clearPending();"
    "  commandNotice.textContent='명령 결과 전달 확인 불가';"
    "  commandResult.textContent=cmd+' 요청 '+pending.id+"
    "   ': 결과 확인 불가 · 브라우저 대기 시간 초과';"
    "  updateButtons();"
    " },3000);"
    " try{ws.send(cmd+',boot_id='+pending.boot+',request_id='+pending.id);}"
    " catch(error){disconnect(ws,'명령 송신 실패');}"
    "}"
    "pingButton.onclick=()=>sendCommand('PING');"
    "disarmButton.onclick=()=>sendCommand('DISARM');"
    "function handleCommandNotice(r){"
    " if(currentBootId===null||r.boot_id!==currentBootId)return;"
    " if(r.stage==='ACCEPTED'&&r.request_id<=ignoredThroughId)return;"
    " if(r.request_id!==null)nextRequestId=Math.max(nextRequestId,r.request_id+1);"
    " const prefix=r.cmd===null?'명령':r.cmd+' 요청 '+r.request_id;"
    " commandNotice.textContent=prefix+': '+"
    "  (r.stage==='ACCEPTED'?'접수됨 · ':'거부됨 · ')+noticeLabels[r.reason]+"
    "  ' ('+r.reason+')';"
    " const pending=pendingCommand;"
    " if(pending&&r.request_id===pending.id&&r.cmd===pending.cmd){"
    "  if(r.stage==='ACCEPTED'){"
    "   pending.accepted=true;pending.session=r.session_id;"
    "  }else if(!pending.accepted){"
    "   ignoredThroughId=Math.max(ignoredThroughId,pending.id);clearPending();"
    "   commandResult.textContent=prefix+': 요청 거부 ('+r.reason+')';"
    "  }"
    " }"
    " updateButtons();"
    "}"
    "function handleCommandResult(r){"
    " if(currentBootId===null||r.boot_id!==currentBootId||"
    "    r.request_id<=ignoredThroughId)return;"
    " const pending=pendingCommand;"
    " if(pending&&(r.request_id!==pending.id||r.cmd!==pending.cmd||"
    "    (pending.session!==null&&r.session_id!==pending.session)))return;"
    " clearPending();ignoredThroughId=r.request_id;"
    " nextRequestId=Math.max(nextRequestId,r.request_id+1);"
    " commandNotice.textContent='ESP 명령 처리 결과 수신';"
    " commandResult.textContent='마지막 명령 결과 · '+r.cmd+"
    "  ' 요청 '+r.request_id+': '+resultLabels[r.status]+' ('+r.status+')';"
    " updateButtons();"
    "}"
    "function validStatus(s){"
    " const u32=v=>Number.isInteger(v)&&v>=0&&v<=4294967295;"
    " const i32=v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647;"
    " const ms=v=>Number.isSafeInteger(v)&&v>=0;"
    " if(!s||typeof s!=='object'||Array.isArray(s)||"
    "    !['ESP_ONLY','STM_UART'].includes(s.source)||"
    "    !['AP','STA'].includes(s.mode)||"
    "    !['SETTLE','SYNC_WAIT','WAIT_DISARM_ACK',"
    "      'WAIT_PONG','READY','FAILED'].includes(s.startup_state)||"
    "    !u32(s.boot_id)||!ms(s.uptime_ms)||!u32(s.free_heap_bytes)||"
    "    !u32(s.tel_count)||!u32(s.stm_age_limit_ms)||s.stm_age_limit_ms===0||"
    "    typeof s.stm_connected!=='boolean'||typeof s.stm_stale!=='boolean'||"
    "    s.batt_mv!==null||s.battery_available!==false)return false;"
    " if(s.source==='ESP_ONLY'){"
    "  return !s.stm_connected&&!s.stm_stale&&s.stm_age_ms===null&&"
    "   s.tel_count===0&&['stm_t_ms','state','reason','command_age_ms',"
    "   'last_seq','vx_mmps','w_mradps','left_pwm','right_pwm',"
    "   'left_cps','right_cps','drop','err'].every(k=>s[k]===null);"
    " }"
    " return ms(s.stm_age_ms)&&"
    "  s.stm_connected===(s.stm_age_ms<=s.stm_age_limit_ms)&&"
    "  s.stm_stale===!s.stm_connected&&u32(s.stm_t_ms)&&"
    "  ['DISARMED','ARMED','FAULT'].includes(s.state)&&"
    "  typeof s.reason==='string'&&/^[A-Z0-9_]{1,31}$/.test(s.reason)&&"
    "  ['command_age_ms','last_seq','drop','err'].every(k=>u32(s[k]))&&"
    "  ['vx_mmps','w_mradps','left_pwm','right_pwm',"
    "   'left_cps','right_cps'].every(k=>i32(s[k]))&&"
    "  Math.abs(s.left_pwm)<=1000&&Math.abs(s.right_pwm)<=1000;"
    "}"
    "function scheduleReconnect(){"
    " if(retryTimer!==null)return;"
    " retryTimer=setTimeout(()=>{retryTimer=null;connect();},1000);"
    "}"
    "function disconnect(ws,reason){"
    " if(socket!==ws)return;"
    " socket=null;currentBootId=null;clearTimeout(watchdog);watchdog=null;"
    " startupFinished=false;cancelCommand(reason);"
    " commandNotice.textContent='연결 끊김 · 명령 송신 대기';updateButtons();"
    " link.textContent=reason+' · 아래 값은 마지막 수신 데이터';"
    " stm.textContent='STM 상태 확인 불가 · 아래 STM 값은 마지막 수신 데이터';"
    " startup.textContent='부팅 응답 확인 불가 · 아래 값은 마지막 수신 데이터';"
    " ws.close();scheduleReconnect();"
    "}"
    "function armWatchdog(ws){"
    " clearTimeout(watchdog);"
    " watchdog=setTimeout(()=>disconnect(ws,'상태 수신 시간 초과'),4000);"
    "}"
    "function connect(){"
    " if(socket!==null)return;"
    " link.textContent='연결 중 · 기존 표시값은 마지막 수신 데이터';"
    " stm.textContent='STM 새 상태 확인 대기 · 기존 값은 마지막 수신 데이터';"
    " startup.textContent='부팅 응답 새 상태 확인 대기 · 기존 값은 마지막 수신 데이터';"
    " clearPending();nextRequestId=1;ignoredThroughId=0;nextSendAt=0;"
    " startupFinished=false;currentBootId=null;"
    " commandNotice.textContent='새 연결 · 명령 송신 대기';"
    " commandResult.textContent='새 연결 · 명령 결과 수신 대기';"
    " const ws=new WebSocket('ws://'+location.host+'/ws');"
    " socket=ws;armWatchdog(ws);updateButtons();"
    " ws.onopen=()=>{"
    "  if(socket!==ws)return;"
    "  link.textContent='연결됨 · 새 상태 수신 대기';armWatchdog(ws);updateButtons();"
    " };"
    " ws.onmessage=(event)=>{"
    "  if(socket!==ws)return;"
    "  try{"
    "   const status=JSON.parse(event.data);"
    "   if(status&&status.kind==='command_result'){"
    "    if(!validCommandResult(status))throw new Error('invalid result');"
    "    handleCommandResult(status);return;"
    "   }"
    "   if(status&&status.kind==='command_notice'){"
    "    if(!validCommandNotice(status))throw new Error('invalid notice');"
    "    handleCommandNotice(status);return;"
    "   }"
    "   if(!validStatus(status))throw new Error('invalid status');"
    "   if(currentBootId!==status.boot_id){"
    "    if(pendingCommand!==null)cancelCommand('ESP 부팅 변경');"
    "    else commandResult.textContent='이번 ESP 부팅의 명령 결과 수신 대기';"
    "    currentBootId=status.boot_id;ignoredThroughId=0;"
    "    commandNotice.textContent='이번 ESP 부팅의 명령 송신 대기';"
    "   }"
    "   startupFinished=['READY','FAILED'].includes(status.startup_state);"
    "   updateButtons();"
    "   data.textContent=JSON.stringify(status,null,2);"
    "   link.textContent='WebSocket 수신 정상 · '+new Date().toLocaleTimeString();"
    "   startup.textContent='이번 ESP 부팅의 응답 확인: '+startupLabels[status.startup_state];"
    "   if(status.source==='ESP_ONLY'){"
    "    stm.textContent='STM TEL 아직 수신 없음';"
    "   }else if(status.stm_stale){"
    "    stm.textContent='STM TEL 수신 중단 · '+status.stm_age_ms+"
    "     ' ms · 아래 STM 값은 마지막 정상 TEL';"
    "   }else{"
    "    stm.textContent='STM TEL 수신 정상 · '+status.state+' / '+status.reason;"
    "   }"
    "   armWatchdog(ws);"
    "  }catch(error){disconnect(ws,'잘못된 상태 응답');}"
    " };"
    " ws.onerror=()=>disconnect(ws,'WebSocket 오류');"
    " ws.onclose=()=>disconnect(ws,'연결 끊김');"
    "}"
    "window.addEventListener('offline',()=>{"
    " if(socket!==null)disconnect(socket,'네트워크 연결 끊김');"
    "});"
    "window.addEventListener('online',()=>{"
    " clearTimeout(retryTimer);retryTimer=null;connect();"
    "});"
    "connect();</script></body></html>";

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
            "\"batt_mv\":null,\"battery_available\":false,"
            "\"drop\":%" PRIu32 ",\"err\":%" PRIu32 "}",
            WIFI_LINK_MODE_NAME, s_boot_id, uptime_ms,
            esp_get_free_heap_size(), startup_state,
            fresh ? "true" : "false", fresh ? "false" : "true",
            age_ms, STM_TEL_STALE_MS, tel_count, tel.t_ms,
            tel.state, tel.reason, tel.command_age_ms, tel.last_seq,
            tel.vx_mmps, tel.w_mradps, tel.left_pwm, tel.right_pwm,
            tel.left_cps, tel.right_cps, tel.drop, tel.err);
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

/* 각 WebSocket 연결에 따로 보관하는 정보. */
typedef struct {
    uint32_t id;
    uint32_t last_request_id;
    uint64_t last_accepted_ms;
} wifi_ws_session_t;

/* 아래 공유 값은 s_stm_lock으로 보호한다. */
static uint32_t s_wifi_ws_next_session_id;
static uint32_t s_wifi_command_owner_session_id;

/* HTTP 서버가 연결을 닫을 때 호출한다. */
static void wifi_ws_session_free(void *context)
{
    wifi_ws_session_t *session = context;

    if (session == NULL) {
        return;
    }

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);

    if (s_wifi_command_owner_session_id == session->id) {
        s_wifi_command_owner_session_id = 0U;

        /* 아직 큐에 남은 해당 연결의 요청을 버린다. */
        (void)xQueueReset(s_wifi_command_queue);
    }

    xSemaphoreGive(s_stm_lock);
    free(session);
}

/* 첫 정상 요청 때 연결 식별값을 만들고 이후에는 재사용한다. */
static wifi_ws_session_t *wifi_ws_session_get(httpd_req_t *req)
{
    wifi_ws_session_t *session = req->sess_ctx;

    if (session != NULL) {
        return session;
    }

    session = calloc(1U, sizeof(*session));

    if (session == NULL) {
        return NULL;
    }

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);

    /* 같은 ESP 부팅 안에서 연결 식별값을 재사용하지 않는다. */
    if (s_wifi_ws_next_session_id == UINT32_MAX) {
        xSemaphoreGive(s_stm_lock);
        free(session);
        return NULL;
    }

    session->id = ++s_wifi_ws_next_session_id;

    xSemaphoreGive(s_stm_lock);

    req->sess_ctx = session;
    req->free_ctx = wifi_ws_session_free;
    return session;
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
            request->type == WIFI_COMMAND_PING ? "PING" : "DISARM");
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
    /* ESP-IDF 6.0.2가 handshake, 제어 PING/CLOSE를 처리한다. */
    httpd_ws_frame_t frame = {0};
    esp_err_t result = httpd_ws_recv_frame(req, &frame, 0);

    if (result != ESP_OK) {
        return result;
    }

    const bool control_pong =
        frame.type == HTTPD_WS_TYPE_PONG;
    
    /*
     * 이번 명령은 완전한 TEXT 프레임 하나로만 받는다.
     * 읽지 않은 큰 payload가 남으면 연결을 닫는다.
    */
    if (!frame.final ||
        (frame.type != HTTPD_WS_TYPE_TEXT && !control_pong) ||
        frame.len > WIFI_COMMAND_MAX_FRAME_SIZE ||
        (control_pong && frame.len > 125)) {
        ESP_LOGW(TAG, "WS unsupported frame; closing connection");
        return ESP_FAIL;
    }

    uint8_t payload[WIFI_COMMAND_MAX_FRAME_SIZE];
    frame.payload = payload;

    if (frame.len > 0U) {
        result = httpd_ws_recv_frame(
            req, &frame, sizeof(payload));

        if (result != ESP_OK) {
            return result;
        }
    }

    /* WebSocket 제어 PONG은 STM 명령 응답과 별개다. */
    if (control_pong) {
        return ESP_OK;
    }

    wifi_command_request_t request = {0};

    if (!wifi_command_parse(
            (const char *)payload, frame.len, &request)) {
        ESP_LOGW(TAG, "W5 rejected: BAD_FORMAT");
        return wifi_ws_send_notice(req, NULL, "REJECTED", "BAD_FORMAT");
    }

    if (request.expected_boot_id != s_boot_id) {
        ESP_LOGW(
            TAG, "W5 rejected: BOOT_MISMATCH request=%" PRIu32,
            request.request_id);
        return wifi_ws_send_notice(req, &request, "REJECTED", "BOOT_MISMATCH");
    }

    wifi_ws_session_t *session = wifi_ws_session_get(req);

    if (session == NULL) {
        ESP_LOGE(TAG, "W5 session unavailable");
        return ESP_FAIL;
    }

    const char *rejection = NULL;

    xSemaphoreTake(s_stm_lock, portMAX_DELAY);

    const uint64_t now_ms =
        (uint64_t)esp_timer_get_time() / 1000U;
    
    const bool startup_finished =
        strcmp(s_stm_startup_status, "READY") == 0 ||
        strcmp(s_stm_startup_status, "FAILED") == 0;
    
    if (!startup_finished) {
        rejection = "STARTUP_PENDING";
    } else if (request.request_id <= session->last_request_id) {
        rejection = "DUPLICATE";
    } else if (session->last_request_id != 0U &&
               now_ms - session->last_accepted_ms <
                   WIFI_COMMAND_MIN_INTERVAL_MS) {
        rejection = "RATE_LIMIT";
    } else if (s_wifi_command_owner_session_id != 0U) {
        rejection = "BUSY";
    } else {
        request.ws_session_id = session->id;
        request.accepted_ms = now_ms;

        /* 대기하지 않고 요청 구조체 전체를 큐에 복사한다. */
        if (xQueueSend(
                s_wifi_command_queue, &request, 0) != pdPASS) {
            rejection = "QUEUE_FULL";
        } else {
            s_wifi_command_owner_session_id = session->id;
            session->last_request_id = request.request_id;
            session->last_accepted_ms = now_ms;
        }
    }

    xSemaphoreGive(s_stm_lock);

    if (rejection != NULL) {
        ESP_LOGW(
            TAG,
            "WS rejected: %s request=%" PRIu32,
            rejection, request.request_id);
        return wifi_ws_send_notice(req, &request, "REJECTED", rejection);
    }

    ESP_LOGI(
        TAG,
        "W5 QUEUED: %s request=%" PRIu32 " session=%" PRIu32,
        request.type == WIFI_COMMAND_PING ? "PING" : "DISARM",
        request.request_id, request.ws_session_id);
    
    return wifi_ws_send_notice(req, &request, "ACCEPTED", "QUEUED");
}

/* HTTP 태스크에서만 실행: 결과를 요청했던 연결 하나에 전달한다. */
static void ws_command_results(httpd_handle_t server)
{
    wifi_command_result_t result;

    /* 한 번의 작업에서 처리할 수를 제한해 상태 송신도 계속한다. */
    for (size_t n = 0U; n < WIFI_COMMAND_RESULT_QUEUE_LENGTH; ++n) {
        if (xQueueReceive(s_wifi_command_result_queue, &result, 0) != pdPASS) {
            break;
        }

        if (result.request.expected_boot_id != s_boot_id) {
            continue;
        }

        int clients[WS_MAX_CLIENTS];
        size_t count = WS_MAX_CLIENTS;

        if (httpd_get_client_list(server, &count, clients) != ESP_OK) {
            ESP_LOGW(TAG, "W5 result client list unavailable");
            continue;
        }

        char json[256];
        const int length = snprintf(
            json, sizeof(json),
            "{\"kind\":\"command_result\",\"boot_id\":%" PRIu32
            ",\"request_id\":%" PRIu32 ",\"session_id\":%" PRIu32
            ",\"cmd\":\"%s\",\"seq\":%" PRIu32 ",\"status\":\"%s\"}",
            result.request.expected_boot_id, result.request.request_id,
            result.request.ws_session_id,
            result.request.type == WIFI_COMMAND_PING ? "PING" : "DISARM",
            result.seq, result.status);

        if (length < 0 || (size_t)length >= sizeof(json)) {
            ESP_LOGE(TAG, "W5 result JSON buffer error");
            continue;
        }

        bool found = false;

        for (size_t i = 0U; i < count; ++i) {
            if (httpd_ws_get_fd_info(server, clients[i]) !=
                HTTPD_WS_CLIENT_WEBSOCKET) {
                continue;
            }

            const wifi_ws_session_t *session =
                httpd_sess_get_ctx(server, clients[i]);

            /* fd를 재사용하더라도 연결 식별값은 달라야 한다. */
            if (session == NULL || session->id != result.request.ws_session_id) {
                continue;
            }

            found = true;
            httpd_ws_frame_t frame = {
                .type = HTTPD_WS_TYPE_TEXT,
                .payload = (uint8_t *)json,
                .len = (size_t)length
            };

            if (httpd_ws_send_frame_async(server, clients[i], &frame) != ESP_OK) {
                ESP_LOGW(TAG, "W5 result send failed; closing fd=%d", clients[i]);
                (void)httpd_sess_trigger_close(server, clients[i]);
            }
            break;
        }

        if (!found) {
            ESP_LOGI(
                TAG, "W5 result target closed; discard request=%" PRIu32,
                result.request.request_id);
        }
    }
}

static void ws_broadcast(void *arg)
{
    const httpd_handle_t server = (httpd_handle_t)arg;

    /* 완료 결과는 특정 연결에, TEL 상태는 모든 연결에 보낸다. */
    ws_command_results(server);

    char json[STATUS_JSON_SIZE];
    const int length = status_json(json, sizeof(json));
    int clients[WS_MAX_CLIENTS];
    size_t count = WS_MAX_CLIENTS;

    if (length >= 0 && httpd_get_client_list(server, &count, clients) == ESP_OK) {
        httpd_ws_frame_t frame = {
            .type = HTTPD_WS_TYPE_TEXT,
            .payload = (uint8_t *)json,
            .len = (size_t)length
        };

        for (size_t i = 0U; i < count; ++i) {
            if (httpd_ws_get_fd_info(server, clients[i]) != HTTPD_WS_CLIENT_WEBSOCKET) {
                continue;
            }

            if (httpd_ws_send_frame_async(server, clients[i], &frame) != ESP_OK) {
                ESP_LOGW(TAG, "WS send failed; closing fd=%d", clients[i]);
                (void)httpd_sess_trigger_close(server, clients[i]);
            }
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
#define STM_UART_LINE_SIZE 384U

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

    /* 현재 TEL 계약은 14개 필드다. */
    size_t field_count = 0U;
    for (const char *pos = line; *pos != '\0'; ++pos) {
        if (*pos == ',') {
            ++field_count;
        }
    }
    if (field_count != 14U) {
        return false;
    }

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
        stm_parse_u32_field(line, "batt_mv=", &out->batt_mv) &&
        stm_parse_u32_field(line, "drop=", &out->drop) &&
        stm_parse_u32_field(line, "err=", &out->err);

    if (!fields_ok) {
        return false;
    }

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
        "%s,seq=%" PRIu32 "\n", command, seq);

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

        if (uart_write_bytes(STM_UART_PORT, "\n", 1) != 1) {
            stm_startup_fail("line sync TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line sync sent");
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

    /* 부팅용 seq를 건너뛰고 같은 부팅 안에서 seq를 재사용하지 않는다. */
    while (s_wifi_uart_next_seq <= UINT32_MAX &&
           (s_wifi_uart_next_seq == s_stm_startup.disarm_seq ||
            s_wifi_uart_next_seq == s_stm_startup.ping_seq)) {
        ++s_wifi_uart_next_seq;
    }

    if (s_wifi_uart_next_seq > UINT32_MAX) {
        wifi_command_finish("SEQ_EXHAUSTED");
        return;
    }

    s_wifi_uart_pending.seq = (uint32_t)s_wifi_uart_next_seq++;

    const char *command =
        request.type == WIFI_COMMAND_PING ? "PING" : "DISARM";
    char line[48];
    const int length = snprintf(
        line, sizeof(line),
        "%s,seq=%" PRIu32 "\n", command, s_wifi_uart_pending.seq);

    if (length <= 0 || (size_t)length >= sizeof(line)) {
        wifi_command_finish("FORMAT_ERROR");
        return;
    }

    /* 송신 직전에 연결 소유권과 요청 나이를 다시 확인한다. */
    xSemaphoreTake(s_stm_lock, portMAX_DELAY);
    const bool still_owned = s_wifi_command_owner_session_id == request.ws_session_id;
    const uint64_t now_ms = (uint64_t)esp_timer_get_time() / 1000U;
    const bool expired = now_ms - request.accepted_ms >= WIFI_COMMAND_RESPONSE_MS;
    int written = -1;

    if (still_owned && !expired) {
        /* 짧은 수신 호출만 보호한다. 응답 대기는 잠금 밖에서 진행한다. */
        written = uart_write_bytes(STM_UART_PORT, line, (size_t)length);
        s_wifi_uart_pending.sent_ms = (uint64_t)esp_timer_get_time() / 1000U;
    }
    xSemaphoreGive(s_stm_lock);

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
        wifi_command_step();

        const int count = uart_read_bytes(
            STM_UART_PORT, bytes, sizeof(bytes),
            pdMS_TO_TICKS(20)
        );

        if (count < 0) {
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
            4096, NULL, 5, NULL) != pdPASS) {
        ESP_LOGE(TAG, "STM UART RX task allocation failed");
        return;
    }

    ESP_LOGI(TAG, "Wi-Fi + STM UART RX: mode=%s boot_id=%" PRIu32,
             WIFI_LINK_MODE_NAME, s_boot_id);
    ESP_ERROR_CHECK(esp_wifi_start());

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(WS_PERIOD_MS));
        ws_schedule();
    }
}