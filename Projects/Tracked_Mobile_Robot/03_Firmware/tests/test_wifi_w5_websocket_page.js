// Usage: node test_wifi_w5_websocket_page.js <wifi_link_main.c or code-guide.md>
// Runs only the embedded browser script. Does not build or flash ESP firmware.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

if (!process.argv[2]) {
    throw new Error('Supply the C source or the Markdown code guide to check.');
}
let source = fs.readFileSync(process.argv[2], 'utf8');
if (process.argv[2].endsWith('.md')) {
    source = source.match(/```c\r?\n([\s\S]*?)\r?\n```/)?.[1];
}
assert.ok(source, 'C source block is present');
const page = source.match(/static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic /)?.[1];
assert.ok(page, 'PAGE string is present');
const html = [...page.matchAll(/"(?:\\.|[^"\\])*"/g)]
    .map(match => JSON.parse(match[0])).join('');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'Browser script is present');
const w4Page = html.includes("id='stm'");
const startupPage = html.includes("id='startup'");
const commandResultPage = html.includes("id='command_result'");
assert.ok(commandResultPage, 'New command-result display is present');

function harness() {
    const elements = {
        link: {textContent: ''}, stm: {textContent: ''},
        startup: {textContent: ''}, data: {textContent: ''}, command_result: {textContent: ''},
        command_notice: {textContent: ''}, ping: {disabled: true}, disarm: {disabled: true}
    };
    const sockets = [];
    const timers = new Map();
    const listeners = {};
    let now = 0;
    let timerId = 0;
    class FakeWebSocket {
        static OPEN = 1;
        constructor(url) {
            this.url = url;
            this.closeCount = 0;
            this.readyState = 0;
            this.sent = [];
            this.failSend = false;
            sockets.push(this);
        }
        close() {
            this.closeCount += 1;
            this.readyState = 3;
            // Deliver immediately to exercise re-entrant close/error handling.
            this.onclose?.({});
        }
        open() { this.readyState = 1; this.onopen?.({}); }
        send(value) { if (this.failSend) throw new Error("send failed"); this.sent.push(value); }
        receive(value) { this.onmessage?.({data: JSON.stringify(value)}); }
    }
    const context = vm.createContext({
        document: {getElementById: id => elements[id]},
        location: {host: '192.0.2.20:8080'},
        window: {addEventListener: (name, handler) => { listeners[name] = handler; }},
        WebSocket: FakeWebSocket,
        performance: {now: () => now},
        setTimeout: (fn, delay) => {
            const id = ++timerId;
            timers.set(id, {fn, at: now + delay});
            return id;
        },
        clearTimeout: id => timers.delete(id),
        fetch: () => { throw new Error('Status page must not HTTP-poll'); }
    });
    vm.runInContext(script, context, {timeout: 1000});
    function advance(ms) {
        const target = now + ms;
        let steps = 0;
        for (;;) {
            const entry = [...timers.entries()]
                .filter(([, timer]) => timer.at <= target)
                .sort((a, b) => a[1].at - b[1].at)[0];
            if (!entry) break;
            assert.ok(++steps < 100, 'Timers do not spin without delay');
            now = entry[1].at;
            timers.delete(entry[0]);
            entry[1].fn();
        }
        now = target;
    }
    return {elements, sockets, listeners, advance};
}

function status(bootId = 123, uptime = 1000) {
    const value = {
        source: 'ESP_ONLY', mode: 'STA', boot_id: bootId, uptime_ms: uptime,
        free_heap_bytes: 200000, stm_connected: false,
        state: null, reason: null, left_pwm: null, right_pwm: null,
        left_cps: null, right_cps: null
    };
    if (w4Page) {
        Object.assign(value, {
            stm_stale: false, stm_age_ms: null, stm_age_limit_ms: 500,
            tel_count: 0, stm_t_ms: null, command_age_ms: null, last_seq: null,
            vx_mmps: null, w_mradps: null, batt_mv: null,
            battery_available: false, drop: null, err: null
        });
    }
    if (startupPage) {
        value.startup_state = 'SETTLE';
    }
    return value;
}

function stmStatus(age = 50) {
    return {
        ...status(), source: 'STM_UART',
        stm_connected: age <= 500, stm_stale: age > 500, stm_age_ms: age,
        stm_age_limit_ms: 500, tel_count: 100, stm_t_ms: 1470300,
        state: 'FAULT', reason: 'ESTOP_ACTIVE',
        command_age_ms: 4294967295, last_seq: 0,
        vx_mmps: 0, w_mradps: 0, left_pwm: 0, right_pwm: 0,
        left_cps: 0, right_cps: 0, batt_mv: null,
        battery_available: false, drop: 0, err: 7
    };
}

let passed = 0;
function test(name, fn) {
    fn();
    passed += 1;
    console.log('PASS ' + name);
}

test('Connects to /ws on the same host, waits for real data', () => {
    const h = harness();
    assert.equal(h.sockets.length, 1);
    assert.equal(h.sockets[0].url, 'ws://192.0.2.20:8080/ws');
    h.sockets[0].open();
    assert.equal(h.elements.data.textContent, '');
    assert.match(h.elements.link.textContent, /수신 대기/);
});

test('Displays real status and keeps unconnected STM fields null', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status());
    assert.deepEqual(JSON.parse(h.elements.data.textContent), status());
    assert.match(h.elements.link.textContent, /WebSocket 수신 정상/);
});

test('Silent connection times out and preserves last data', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status());
    h.advance(3999);
    assert.equal(h.sockets[0].closeCount, 0);
    h.advance(1);
    assert.match(h.elements.link.textContent, /시간 초과/);
    assert.deepEqual(JSON.parse(h.elements.data.textContent), status());
    assert.equal(h.sockets[0].closeCount, 1);
    h.advance(1000);
    assert.equal(h.sockets.length, 2);
    h.sockets[1].open();
    assert.match(h.elements.link.textContent, /수신 대기/);
    h.sockets[1].receive(status(123, 6000));
    assert.equal(JSON.parse(h.elements.data.textContent).boot_id, 123);
    assert.match(h.elements.link.textContent, /수신 정상/);
});

test('Late events from the old socket cannot overwrite the new connection', () => {
    const h = harness();
    const old = h.sockets[0];
    old.open();
    old.receive(status());
    old.onerror({});
    h.advance(1000);
    const current = h.sockets[1];
    current.open();
    current.receive(status(123, 3000));
    old.receive(status(999, 1));
    old.onerror({});
    old.onclose({});
    assert.equal(JSON.parse(h.elements.data.textContent).uptime_ms, 3000);
    assert.match(h.elements.link.textContent, /수신 정상/);
    assert.equal(current.closeCount, 0);
    h.advance(1000);
    assert.equal(h.sockets.length, 2);
});

test('Error plus close schedules only one reconnect', () => {
    const h = harness();
    h.sockets[0].onerror({});
    h.sockets[0].onclose({});
    h.sockets[0].onerror({});
    h.advance(1000);
    assert.equal(h.sockets.length, 2);
});

test('Bad JSON preserves the previous valid display', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status());
    h.sockets[0].onmessage({data: '{broken'});
    assert.deepEqual(JSON.parse(h.elements.data.textContent), status());
    assert.match(h.elements.link.textContent, /잘못된 상태/);
});

test('Invalid status shapes are rejected without showing fake fresh data', () => {
    for (const value of [null, [], {}, {...status(), source: 'FAKE'},
        {...status(), uptime_ms: -1}, {...status(), boot_id: -1},
        {...status(), boot_id: 4294967296}]) {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(status());
        h.sockets[0].receive(value);
        assert.deepEqual(JSON.parse(h.elements.data.textContent), status());
        assert.match(h.elements.link.textContent, /잘못된 상태/);
    }
});

test('Each valid sample renews the inactivity deadline', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status());
    h.advance(3000);
    h.sockets[0].receive(status(123, 4000));
    h.advance(3000);
    assert.equal(h.sockets[0].closeCount, 0);
    h.advance(1000);
    assert.equal(h.sockets[0].closeCount, 1);
});

test('Offline and repeated online events do not create duplicate sockets', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status());
    h.listeners.offline();
    assert.match(h.elements.link.textContent, /네트워크 연결 끊김/);
    h.listeners.online();
    h.listeners.online();
    assert.equal(h.sockets.length, 2);
    h.advance(1000);
    assert.equal(h.sockets.length, 2);
});

test('A rebooted ESP may send a new boot ID and smaller uptime', () => {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(status(123, 100000));
    h.sockets[0].onclose({});
    h.advance(1000);
    h.sockets[1].open();
    h.sockets[1].receive(status(456, 1000));
    assert.equal(JSON.parse(h.elements.data.textContent).boot_id, 456);
    assert.equal(JSON.parse(h.elements.data.textContent).uptime_ms, 1000);
});

if (w4Page) {
    test('W4 separates healthy WebSocket from no STM telemetry yet', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(status());
        assert.match(h.elements.link.textContent, /WebSocket 수신 정상/);
        assert.match(h.elements.stm.textContent, /아직 수신 없음/);
        assert.equal(JSON.parse(h.elements.data.textContent).stm_age_ms, null);
    });

    test('W4 shows real UART state including FAULT and the no-CMD sentinel', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(stmStatus());
        assert.deepEqual(JSON.parse(h.elements.data.textContent), stmStatus());
        assert.match(h.elements.stm.textContent, /수신 정상.*FAULT.*ESTOP_ACTIVE/);
        assert.equal(h.sockets[0].closeCount, 0);
    });

    test('W4 accepts signed motion values without inventing battery voltage', () => {
        const h = harness();
        const value = {
            ...stmStatus(), state: 'ARMED', reason: 'NONE',
            vx_mmps: -100, w_mradps: 200, left_pwm: -100, right_pwm: 100,
            left_cps: -2147483648, right_cps: 2147483647
        };
        h.sockets[0].receive(value);
        const displayed = JSON.parse(h.elements.data.textContent);
        assert.deepEqual(displayed, value);
        assert.equal(displayed.batt_mv, null);
        assert.equal(displayed.battery_available, false);
    });

    test('W4 becomes stale above 500ms, preserves STM values, and recovers', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(stmStatus(500));
        assert.match(h.elements.stm.textContent, /수신 정상/);
        h.sockets[0].receive(stmStatus(501));
        assert.match(h.elements.link.textContent, /WebSocket 수신 정상/);
        assert.match(h.elements.stm.textContent, /수신 중단.*501.*마지막 정상 TEL/);
        assert.deepEqual(JSON.parse(h.elements.data.textContent), stmStatus(501));
        assert.equal(h.sockets[0].closeCount, 0);
        h.sockets[0].receive({...stmStatus(0), tel_count: 101, stm_t_ms: 1470400});
        assert.match(h.elements.stm.textContent, /수신 정상/);
        assert.equal(JSON.parse(h.elements.data.textContent).tel_count, 101);
    });

    test('W4 stale UART updates keep WebSocket healthy beyond its watchdog', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(stmStatus());
        for (let second = 1; second <= 8; ++second) {
            h.advance(1000);
            h.sockets[0].receive({
                ...stmStatus(second * 1000), uptime_ms: 1000 + second * 1000
            });
        }
        assert.equal(h.sockets[0].closeCount, 0);
        assert.equal(h.sockets.length, 1);
        assert.match(h.elements.stm.textContent, /수신 중단/);
        assert.equal(JSON.parse(h.elements.data.textContent).tel_count, 100);
    });

    test('W4 rejects inconsistent health flags, broken TEL fields and fake battery data', () => {
        const invalid = [
            {...stmStatus(501), stm_connected: true},
            {...stmStatus(), stm_stale: true},
            {...stmStatus(), stm_age_ms: -1},
            {...stmStatus(), stm_age_ms: Number.MAX_SAFE_INTEGER + 1},
            {...stmStatus(), stm_age_limit_ms: 0},
            {...stmStatus(), state: 'UNKNOWN'},
            {...stmStatus(), reason: '<script>'},
            {...stmStatus(), left_pwm: 1001},
            {...stmStatus(), right_cps: 2147483648},
            {...stmStatus(), command_age_ms: -1},
            {...stmStatus(), drop: 4294967296},
            {...stmStatus(), left_cps: null},
            {...stmStatus(), batt_mv: 0},
            {...stmStatus(), battery_available: true},
            {...status(), stm_t_ms: 123},
            {...status(), stm_connected: true}
        ];
        for (const value of invalid) {
            const h = harness();
            h.sockets[0].open();
            h.sockets[0].receive(stmStatus());
            h.sockets[0].receive(value);
            assert.deepEqual(JSON.parse(h.elements.data.textContent), stmStatus());
            assert.match(h.elements.link.textContent, /잘못된 상태/);
            assert.match(h.elements.stm.textContent, /확인 불가/);
            assert.equal(h.sockets[0].closeCount, 1);
        }
    });

    test('W4 quiet WebSocket marks STM freshness unknown and preserves the snapshot', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive(stmStatus());
        h.advance(4000);
        assert.match(h.elements.link.textContent, /시간 초과/);
        assert.match(h.elements.stm.textContent, /확인 불가/);
        assert.deepEqual(JSON.parse(h.elements.data.textContent), stmStatus());
        assert.equal(h.sockets[0].closeCount, 1);
    });

    test('W4 reconnect ignores stale socket TEL events and accepts a new ESP boot', () => {
        const h = harness();
        const old = h.sockets[0];
        old.open();
        old.receive(stmStatus());
        old.onclose({});
        h.advance(1000);
        const current = h.sockets[1];
        current.open();
        current.receive({...stmStatus(), boot_id: 456, uptime_ms: 100});
        const before = h.elements.stm.textContent;
        old.receive(stmStatus(5000));
        old.onclose({});
        assert.equal(h.elements.stm.textContent, before);
        assert.equal(JSON.parse(h.elements.data.textContent).boot_id, 456);
        assert.equal(current.closeCount, 0);
    });
}

if (startupPage) {
    test('Fresh TEL remains visible when boot response confirmation failed', () => {
        const h = harness();
        h.sockets[0].open();
        h.sockets[0].receive({...stmStatus(), startup_state: 'FAILED'});
        assert.match(h.elements.link.textContent, /WebSocket 수신 정상/);
        assert.match(h.elements.stm.textContent, /TEL 수신 정상/);
        assert.match(h.elements.startup.textContent, /이번 ESP 부팅.*실패.*FAILED/);
        assert.equal(h.sockets[0].closeCount, 0);
    });

    test('READY records boot confirmation without hiding stale STM telemetry', () => {
        const h = harness();
        h.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
        h.sockets[0].receive({...stmStatus(501), startup_state: 'READY'});
        assert.match(h.elements.startup.textContent, /이번 ESP 부팅.*완료.*READY/);
        assert.match(h.elements.stm.textContent, /수신 중단.*501/);
        assert.equal(JSON.parse(h.elements.data.textContent).stm_connected, false);
        assert.equal(h.sockets[0].closeCount, 0);
    });

    test('Pending boot phases never display completed confirmation', () => {
        const phases = [
            ['SETTLE', /초기 안정 대기/],
            ['SYNC_WAIT', /줄 동기화 대기/],
            ['WAIT_DISARM_ACK', /DISARM 응답 대기/],
            ['WAIT_PONG', /PING 응답 대기/]
        ];
        const h = harness();
        for (const [phase, text] of phases) {
            h.sockets[0].receive({...status(), startup_state: phase});
            assert.match(h.elements.startup.textContent, text);
            assert.doesNotMatch(h.elements.startup.textContent, /완료|READY/);
            assert.match(h.elements.stm.textContent, /아직 수신 없음/);
        }
        h.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
        assert.match(h.elements.startup.textContent, /완료.*READY/);
    });

    test('Invalid boot status hides current readiness and preserves the last snapshot', () => {
        for (const phase of [undefined, null, 1, {}, [], 'UNKNOWN', 'ready', 'toString']) {
            const h = harness();
            const good = {...stmStatus(), startup_state: 'READY'};
            h.sockets[0].receive(good);
            h.sockets[0].receive({...stmStatus(), startup_state: phase});
            assert.match(h.elements.link.textContent, /잘못된 상태/);
            assert.match(h.elements.startup.textContent, /확인 불가/);
            assert.doesNotMatch(h.elements.startup.textContent, /완료|READY/);
            assert.deepEqual(JSON.parse(h.elements.data.textContent), good);
            assert.equal(h.sockets[0].closeCount, 1);
        }
    });

    test('Lost WebSocket marks boot status unknown until a new valid sample', () => {
        for (const loss of ['watchdog', 'close', 'error', 'offline']) {
            const h = harness();
            h.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
            if (loss === 'watchdog') h.advance(4000);
            if (loss === 'close') h.sockets[0].onclose({});
            if (loss === 'error') h.sockets[0].onerror({});
            if (loss === 'offline') h.listeners.offline();
            assert.match(h.elements.startup.textContent, /확인 불가/);
            assert.doesNotMatch(h.elements.startup.textContent, /완료|READY/);
            h.advance(1000);
            h.sockets[1].open();
            assert.match(h.elements.startup.textContent, /새 상태.*대기/);
            assert.doesNotMatch(h.elements.startup.textContent, /완료|READY/);
            h.sockets[1].receive({...stmStatus(), startup_state: 'FAILED'});
            assert.match(h.elements.startup.textContent, /실패.*FAILED/);
        }
    });

    test('A new ESP boot replaces READY and old socket events cannot restore it', () => {
        const h = harness();
        const old = h.sockets[0];
        old.receive({...stmStatus(), startup_state: 'READY'});
        old.onclose({});
        h.advance(1000);
        const current = h.sockets[1];
        current.open();
        current.receive({...status(456, 100), startup_state: 'SETTLE'});
        assert.match(h.elements.startup.textContent, /초기 안정 대기/);
        assert.equal(JSON.parse(h.elements.data.textContent).boot_id, 456);
        current.receive({...stmStatus(), boot_id: 456, startup_state: 'FAILED'});
        old.receive({...stmStatus(), startup_state: 'READY'});
        old.onclose({});
        assert.match(h.elements.startup.textContent, /실패.*FAILED/);
        assert.equal(JSON.parse(h.elements.data.textContent).boot_id, 456);
        assert.equal(current.closeCount, 0);
    });
}

test('A connection that never opens is retried after its deadline', () => {
    const h = harness();
    h.advance(4000);
    assert.equal(h.sockets[0].closeCount, 1);
    h.advance(1000);
    assert.equal(h.sockets.length, 2);
});


function commandResult(overrides = {}) {
    return {
        kind: 'command_result', boot_id: 123, request_id: 12,
        session_id: 3, cmd: 'PING', seq: 3993059321, status: 'OK',
        ...overrides
    };
}

test('W5 PING result displays matching request without replacing telemetry', () => {
    const h = harness();
    h.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
    const telemetry = h.elements.data.textContent;
    const startup = h.elements.startup.textContent;
    h.sockets[0].receive(commandResult());
    assert.match(h.elements.command_result.textContent, /PING 요청 12: 응답 확인 \(OK\)/);
    assert.equal(h.elements.data.textContent, telemetry);
    assert.equal(h.elements.startup.textContent, startup);
    assert.equal(h.sockets[0].closeCount, 0);
});

test('W5 DISARM ACK display does not clear the reported ESTOP fault', () => {
    const h = harness();
    h.sockets[0].receive(stmStatus());
    h.sockets[0].receive(commandResult({cmd: 'DISARM'}));
    assert.match(h.elements.command_result.textContent, /DISARM 요청 12.*응답 확인/);
    assert.match(h.elements.stm.textContent, /FAULT \/ ESTOP_ACTIVE/);
    assert.equal(JSON.parse(h.elements.data.textContent).state, 'FAULT');
});

test('W5 TIMEOUT remains a failure alongside historical READY and stale TEL', () => {
    const h = harness();
    h.sockets[0].receive({...stmStatus(2000), startup_state: 'READY'});
    h.sockets[0].receive(commandResult({status: 'TIMEOUT'}));
    assert.match(h.elements.command_result.textContent, /응답 시간 초과 \(TIMEOUT\)/);
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    assert.match(h.elements.startup.textContent, /READY/);
    assert.match(h.elements.stm.textContent, /수신 중단/);
    assert.equal(h.sockets[0].closeCount, 0);
});

test('W5 continued TEL does not erase the last command result', () => {
    const h = harness();
    h.sockets[0].receive(stmStatus());
    h.sockets[0].receive(commandResult());
    const result = h.elements.command_result.textContent;
    h.sockets[0].receive({...stmStatus(), tel_count: 101, uptime_ms: 1100});
    assert.equal(h.elements.command_result.textContent, result);
    assert.equal(JSON.parse(h.elements.data.textContent).tel_count, 101);
});

test('W5 command results cannot keep silent telemetry falsely fresh', () => {
    const h = harness();
    h.sockets[0].receive(stmStatus());
    h.advance(3000);
    h.sockets[0].receive(commandResult());
    h.advance(999);
    assert.equal(h.sockets[0].closeCount, 0);
    h.advance(1);
    assert.equal(h.sockets[0].closeCount, 1);
    assert.match(h.elements.link.textContent, /시간 초과/);
});

test('W5 results for an older ESP boot are ignored', () => {
    const h = harness();
    h.sockets[0].receive(status(456));
    const before = h.elements.command_result.textContent;
    h.sockets[0].receive(commandResult());
    assert.equal(h.elements.command_result.textContent, before);
    assert.equal(h.sockets[0].closeCount, 0);
});

test('W5 delayed events from an old WebSocket cannot overwrite current results', () => {
    const h = harness();
    const old = h.sockets[0];
    old.receive(stmStatus());
    old.receive(commandResult());
    old.onclose({});
    h.advance(1000);
    const current = h.sockets[1];
    current.receive(stmStatus());
    current.receive(commandResult({request_id: 1, session_id: 4, status: 'TIMEOUT'}));
    const before = h.elements.command_result.textContent;
    old.receive(commandResult({request_id: 13}));
    assert.equal(h.elements.command_result.textContent, before);
    assert.equal(current.closeCount, 0);
});

test('W5 requires a current status boot ID before displaying a result', () => {
    const h = harness();
    const before = h.elements.command_result.textContent;
    h.sockets[0].receive(commandResult());
    assert.equal(h.elements.command_result.textContent, before);
    assert.equal(h.sockets[0].closeCount, 0);
});

test('W5 malformed result fields cannot display success or replace telemetry', () => {
    for (const override of [
        {boot_id: 4294967296}, {request_id: 0}, {session_id: 0}, {seq: -1},
        {cmd: 'ARM'}, {status: 'toString'}, {status: 'constructor'}, {status: {}},
    ]) {
        const h = harness();
        h.sockets[0].receive(stmStatus());
        h.sockets[0].receive(commandResult(override));
        assert.equal(h.sockets[0].closeCount, 1);
        assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
        assert.deepEqual(JSON.parse(h.elements.data.textContent), stmStatus());
    }
});

test('W5 an ESP boot change clears the preceding boot result', () => {
    const h = harness();
    h.sockets[0].receive(stmStatus());
    h.sockets[0].receive(commandResult());
    h.sockets[0].receive(status(456));
    assert.doesNotMatch(h.elements.command_result.textContent, /PING 요청 12/);
    assert.match(h.elements.command_result.textContent, /이번 ESP 부팅/);
});

test('W5 reconnect requires a new result instead of restoring old success', () => {
    const h = harness();
    h.sockets[0].receive(stmStatus());
    h.sockets[0].receive(commandResult());
    h.sockets[0].onclose({});
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    h.advance(1000);
    h.sockets[1].receive(stmStatus());
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    assert.equal(h.sockets[1].closeCount, 0);
});


function notice(overrides = {}) {
    return {
        kind: 'command_notice', boot_id: 123, session_id: 9,
        request_id: 1, cmd: 'PING', stage: 'ACCEPTED', reason: 'QUEUED',
        ...overrides
    };
}

function readyHarness(value = {...stmStatus(), startup_state: 'READY'}) {
    const h = harness();
    h.sockets[0].open();
    h.sockets[0].receive(value);
    return h;
}

test('UI waits for an open socket and completed startup before enabling buttons', () => {
    const h = harness();
    assert.equal(h.elements.ping.disabled, true);
    h.sockets[0].open();
    assert.equal(h.elements.ping.disabled, true);
    h.sockets[0].receive({...status(), startup_state: 'WAIT_PONG'});
    assert.equal(h.elements.ping.disabled, true);
    h.sockets[0].receive({...status(), startup_state: 'READY'});
    assert.equal(h.elements.ping.disabled, false);
    assert.equal(h.elements.disarm.disabled, false);
});

test('UI permits diagnostic commands after FAILED even if TEL is stale', () => {
    const h = readyHarness({...stmStatus(2000), startup_state: 'FAILED'});
    assert.equal(h.elements.ping.disabled, false);
    h.elements.ping.onclick();
    assert.deepEqual(h.sockets[0].sent, ['PING,boot_id=123,request_id=1']);
});

test('UI PING click sends one request and blocks another click while pending', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.elements.ping.onclick();
    h.elements.disarm.onclick();
    assert.deepEqual(h.sockets[0].sent, ['PING,boot_id=123,request_id=1']);
    assert.equal(h.elements.ping.disabled, true);
    assert.equal(h.elements.disarm.disabled, true);
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
});

test('UI ACCEPTED is not success and does not release the pending request', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    assert.match(h.elements.command_notice.textContent, /접수됨.*STM 응답 확인 중/);
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인|\(OK\)/);
    assert.equal(h.elements.ping.disabled, true);
    assert.equal(h.sockets[0].closeCount, 0);
});

test('UI matching completion releases pending but preserves the 500ms interval', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.match(h.elements.command_result.textContent, /PING 요청 1: 응답 확인 \(OK\)/);
    assert.equal(h.elements.ping.disabled, true);
    h.advance(499);
    assert.equal(h.elements.ping.disabled, true);
    h.advance(1);
    assert.equal(h.elements.ping.disabled, false);
    h.elements.disarm.onclick();
    assert.equal(h.sockets[0].sent[1], 'DISARM,boot_id=123,request_id=2');
});

test('UI ignores a result for another request, command, session, or boot', () => {
    for (const fields of [
        {request_id: 2}, {cmd: 'DISARM'}, {session_id: 10}, {boot_id: 456}
    ]) {
        const h = readyHarness();
        h.elements.ping.onclick();
        h.sockets[0].receive(notice());
        const before = h.elements.command_result.textContent;
        h.sockets[0].receive(commandResult({request_id: 1, session_id: 9, ...fields}));
        assert.equal(h.elements.command_result.textContent, before);
        assert.equal(h.elements.ping.disabled, true);
        assert.equal(h.sockets[0].closeCount, 0);
    }
});

test('UI BUSY or RATE_LIMIT rejection ends the matching request without success', () => {
    for (const reason of ['BUSY', 'RATE_LIMIT', 'STARTUP_PENDING', 'QUEUE_FULL', 'BOOT_MISMATCH']) {
        const h = readyHarness();
        h.elements.ping.onclick();
        h.sockets[0].receive(notice({stage: 'REJECTED', reason}));
        assert.match(h.elements.command_notice.textContent, new RegExp('거부됨.*'+reason));
        assert.match(h.elements.command_result.textContent, new RegExp('요청 거부.*'+reason));
        assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인|\(OK\)/);
        h.advance(500);
        assert.equal(h.elements.ping.disabled, false);
        assert.equal(h.sockets[0].sent.length, 1);
    }
});

test('UI duplicate rejection of a second copy cannot terminate an accepted original', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.sockets[0].receive(notice({stage: 'REJECTED', reason: 'DUPLICATE'}));
    assert.equal(h.elements.ping.disabled, true);
    assert.match(h.elements.command_notice.textContent, /DUPLICATE/);
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.match(h.elements.command_result.textContent, /응답 확인 \(OK\)/);
});

test('UI rejection for an unrelated request does not end the current request', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.sockets[0].receive(notice({request_id: 2, stage: 'REJECTED', reason: 'RATE_LIMIT'}));
    assert.equal(h.elements.ping.disabled, true);
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    h.advance(500);
    h.elements.ping.onclick();
    assert.equal(h.sockets[0].sent[1], 'PING,boot_id=123,request_id=3');
});

test('UI malformed-input notice without identifiers is shown without fake success', () => {
    const h = readyHarness();
    h.sockets[0].receive(notice({request_id: null, cmd: null, stage: 'REJECTED', reason: 'BAD_FORMAT'}));
    assert.match(h.elements.command_notice.textContent, /거부됨.*명령 형식 오류.*BAD_FORMAT/);
    assert.equal(h.sockets[0].closeCount, 0);
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인|\(OK\)/);
});

test('UI lost completion is unknown after 3s rather than STM TIMEOUT or success', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.advance(2500);
    h.sockets[0].receive({...stmStatus(), startup_state: 'READY', uptime_ms: 3500});
    h.advance(500);
    assert.match(h.elements.command_result.textContent, /결과 확인 불가.*브라우저 대기 시간 초과/);
    assert.doesNotMatch(h.elements.command_result.textContent, /TIMEOUT|\(OK\)/);
    assert.equal(h.elements.command_notice.textContent, '명령 결과 전달 확인 불가');
    assert.equal(h.sockets[0].sent.length, 1);
    assert.equal(h.elements.ping.disabled, false);
});

test('UI late success after browser expiry cannot replace the unknown outcome', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.advance(2500);
    h.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
    h.advance(500);
    const before = h.elements.command_result.textContent;
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.equal(h.elements.command_result.textContent, before);
    h.elements.ping.onclick();
    h.sockets[0].receive(notice({request_id: 2}));
    const pending = h.elements.command_result.textContent;
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.equal(h.elements.command_result.textContent, pending);
    assert.equal(h.elements.ping.disabled, true);
});

test('UI late acceptance cannot revive an expired or completed request notice', () => {
    const expired = readyHarness();
    expired.elements.ping.onclick();
    expired.advance(2500);
    expired.sockets[0].receive({...stmStatus(), startup_state: 'READY'});
    expired.advance(500);
    const unknown = expired.elements.command_notice.textContent;
    expired.sockets[0].receive(notice());
    assert.equal(expired.elements.command_notice.textContent, unknown);
    assert.equal(expired.elements.ping.disabled, false);

    const completed = readyHarness();
    completed.elements.ping.onclick();
    completed.sockets[0].receive(notice());
    completed.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.equal(completed.elements.command_notice.textContent, 'ESP 명령 처리 결과 수신');
    completed.sockets[0].receive(notice());
    assert.equal(completed.elements.command_notice.textContent, 'ESP 명령 처리 결과 수신');
});

test('UI pending connection loss stays unknown and reconnect never resends', () => {
    const h = readyHarness();
    const old = h.sockets[0];
    h.elements.ping.onclick();
    old.receive(notice());
    old.onclose({});
    assert.match(h.elements.command_result.textContent, /PING 요청 1: 결과 확인 불가/);
    assert.equal(h.elements.ping.disabled, true);
    h.advance(1000);
    const current = h.sockets[1];
    current.open();
    current.receive({...stmStatus(), startup_state: 'READY'});
    assert.equal(current.sent.length, 0);
    assert.equal(h.elements.ping.disabled, false);
    old.receive(commandResult({request_id: 1, session_id: 9}));
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    h.elements.ping.onclick();
    assert.deepEqual(current.sent, ['PING,boot_id=123,request_id=1']);
});

test('UI ESP boot change invalidates a pending command without resending', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    h.sockets[0].receive(notice());
    h.sockets[0].receive({...status(456), startup_state: 'SETTLE'});
    assert.match(h.elements.command_result.textContent, /결과 확인 불가.*ESP 부팅 변경/);
    assert.equal(h.elements.ping.disabled, true);
    h.sockets[0].receive(commandResult({request_id: 1, session_id: 9}));
    assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    assert.equal(h.sockets[0].sent.length, 1);
});

test('UI failed WebSocket send is unknown and does not trigger a retry', () => {
    const h = readyHarness();
    h.sockets[0].failSend = true;
    h.elements.ping.onclick();
    assert.match(h.elements.command_result.textContent, /결과 확인 불가.*명령 송신 실패/);
    h.advance(1000);
    assert.equal(h.sockets[1].sent.length, 0);
});

test('UI old command result cannot overwrite a newer completed request', () => {
    const h = readyHarness();
    h.sockets[0].receive(commandResult({request_id: 12}));
    const before = h.elements.command_result.textContent;
    h.sockets[0].receive(commandResult({request_id: 11, status: 'TIMEOUT'}));
    assert.equal(h.elements.command_result.textContent, before);
});

test('UI receipt and rejection notices cannot renew silent status watchdog', () => {
    const h = readyHarness();
    h.advance(3000);
    h.sockets[0].receive(notice({stage: 'REJECTED', reason: 'BUSY'}));
    h.advance(999);
    assert.equal(h.sockets[0].closeCount, 0);
    h.advance(1);
    assert.equal(h.sockets[0].closeCount, 1);
});

test('UI malformed notice is rejected instead of impersonating acceptance', () => {
    for (const fields of [
        {reason: 'toString'}, {request_id: 0}, {cmd: 'ARM'}, {session_id: 0},
        {stage: 'OK'}, {reason: 'BUSY'}, {boot_id: -1},
    ]) {
        const h = readyHarness();
        h.sockets[0].receive(notice(fields));
        assert.equal(h.sockets[0].closeCount, 1);
        assert.doesNotMatch(h.elements.command_result.textContent, /응답 확인/);
    }
});

test('UI wrong-boot notices do not alter the current request or enable buttons', () => {
    const h = readyHarness();
    h.elements.ping.onclick();
    const before = h.elements.command_notice.textContent;
    h.sockets[0].receive(notice({boot_id: 456, stage: 'REJECTED', reason: 'BUSY'}));
    assert.equal(h.elements.command_notice.textContent, before);
    assert.equal(h.elements.ping.disabled, true);
});

test('UI request ID exhaustion disables buttons without wrapping to 1', () => {
    const h = readyHarness();
    h.sockets[0].receive(notice({request_id: 4294967295, stage: 'REJECTED', reason: 'DUPLICATE'}));
    assert.equal(h.elements.ping.disabled, true);
    h.elements.ping.onclick();
    assert.equal(h.sockets[0].sent.length, 0);
});

console.log(`${passed} browser simulation checks passed; no ESP runtime or C build checked.`);
