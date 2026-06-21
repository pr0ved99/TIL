"use strict";

const MAX_LOG_LINES = 500;
const TEL_STALE_MS = 1500;
const SCRIPTED_DELAY_MS = 500;

const state = {
  port: null,
  reader: null,
  writer: null,
  keepReading: false,
  rxBuffer: "",
  connected: false,
  fakeTimer: null,
  keepaliveTimer: null,
  seq: 1,
  lastTelAt: 0,
  ackCount: 0,
  errCount: 0,
  parseErrorCount: 0,
  logs: [],
  csvRows: [],
  telemetry: {
    t_ms: "0",
    state: "UNKNOWN",
    batt_mv: "0",
    left_cps: "0",
    right_cps: "0",
    left_pwm: "0",
    right_pwm: "0",
    fault: "0",
  },
};

const el = {};

document.addEventListener("DOMContentLoaded", () => {
  bindElements();
  bindEvents();
  updateSupport();
  renderAll();
  setInterval(updateAge, 200);
});

function bindElements() {
  for (const id of [
    "supportText",
    "baudRate",
    "connectBtn",
    "disconnectBtn",
    "connectionState",
    "robotState",
    "lastTelAge",
    "lastSeq",
    "ackCount",
    "errCount",
    "parseErrorCount",
    "telTime",
    "telBattery",
    "telLeftCps",
    "telRightCps",
    "telLeftPwm",
    "telRightPwm",
    "telFault",
    "lastCode",
    "fakeToggleBtn",
    "clearLogBtn",
    "downloadCsvBtn",
    "autoSeq",
    "seqInput",
    "vxInput",
    "wInput",
    "timeoutInput",
    "pingBtn",
    "armBtn",
    "disarmBtn",
    "cmdBtn",
    "stopBtn",
    "forwardBtn",
    "turnBtn",
    "badRangeBtn",
    "keepaliveBtn",
    "scriptedBtn",
    "rawInput",
    "sendRawBtn",
    "parseRawBtn",
    "lastTx",
    "lastRx",
    "lastAck",
    "lastErr",
    "rawLog",
    "logCount",
  ]) {
    el[id] = document.getElementById(id);
  }
}

function bindEvents() {
  el.connectBtn.addEventListener("click", connectSerial);
  el.disconnectBtn.addEventListener("click", disconnectSerial);
  el.fakeToggleBtn.addEventListener("click", toggleFakeTelemetry);
  el.clearLogBtn.addEventListener("click", clearLogs);
  el.downloadCsvBtn.addEventListener("click", downloadCsv);
  el.pingBtn.addEventListener("click", () => sendFrame(makeSimpleFrame("PING")));
  el.armBtn.addEventListener("click", () => sendFrame(makeSimpleFrame("ARM")));
  el.disarmBtn.addEventListener("click", () => sendFrame(makeSimpleFrame("DISARM")));
  el.cmdBtn.addEventListener("click", () => sendFrame(makeCmdFrame(readCommandInputs())));
  el.stopBtn.addEventListener("click", () => sendFrame(makeCmdFrame({ vx: 0, w: 0, timeout: readTimeout() })));
  el.forwardBtn.addEventListener("click", () => sendFrame(makeCmdFrame({ vx: 50, w: 0, timeout: readTimeout() })));
  el.turnBtn.addEventListener("click", () => sendFrame(makeCmdFrame({ vx: 0, w: 300, timeout: readTimeout() })));
  el.badRangeBtn.addEventListener("click", () => sendFrame(makeRawFrame(`CMD,seq=${nextSeq()},vx_mmps=9999,w_mradps=0,timeout_ms=300`)));
  el.keepaliveBtn.addEventListener("click", toggleKeepalive);
  el.scriptedBtn.addEventListener("click", runScriptedTest);
  el.sendRawBtn.addEventListener("click", () => sendFrame(makeRawFrame(el.rawInput.value)));
  el.parseRawBtn.addEventListener("click", () => handleLine(el.rawInput.value, "RX"));
}

function updateSupport() {
  const hasSerial = "serial" in navigator;
  const isSecure = window.isSecureContext;
  if (hasSerial && isSecure) {
    el.supportText.textContent = "Web Serial ready on this browser";
    return;
  }
  if (!isSecure) {
    el.supportText.textContent = "Open through localhost to use Web Serial";
    el.connectBtn.disabled = true;
    return;
  }
  el.supportText.textContent = "Web Serial is not supported by this browser";
  el.connectBtn.disabled = true;
}

async function connectSerial() {
  if (!("serial" in navigator)) {
    appendLog("SYS", "Web Serial API unavailable");
    return;
  }
  try {
    const baudRate = Number(el.baudRate.value);
    state.port = await navigator.serial.requestPort();
    await state.port.open({ baudRate });
    state.writer = state.port.writable.getWriter();
    state.keepReading = true;
    state.connected = true;
    appendLog("SYS", `CONNECTED,baud=${baudRate}`);
    renderConnection();
    readLoop();
  } catch (error) {
    appendLog("SYS", `CONNECT_ERROR,${error.message}`);
  }
}

async function disconnectSerial() {
  stopKeepalive();
  state.keepReading = false;
  try {
    if (state.reader) {
      await state.reader.cancel();
      state.reader.releaseLock();
      state.reader = null;
    }
    if (state.writer) {
      state.writer.releaseLock();
      state.writer = null;
    }
    if (state.port) {
      await state.port.close();
      state.port = null;
    }
  } catch (error) {
    appendLog("SYS", `DISCONNECT_ERROR,${error.message}`);
  } finally {
    state.connected = false;
    appendLog("SYS", "DISCONNECTED");
    renderConnection();
  }
}

async function readLoop() {
  const decoder = new TextDecoder();
  while (state.port && state.port.readable && state.keepReading) {
    state.reader = state.port.readable.getReader();
    try {
      while (state.keepReading) {
        const { value, done } = await state.reader.read();
        if (done) break;
        if (value) consumeText(decoder.decode(value, { stream: true }));
      }
    } catch (error) {
      if (state.keepReading) appendLog("SYS", `READ_ERROR,${error.message}`);
    } finally {
      if (state.reader) {
        state.reader.releaseLock();
        state.reader = null;
      }
    }
  }
}

function consumeText(text) {
  state.rxBuffer += text;
  let lineEnd = state.rxBuffer.indexOf("\n");
  while (lineEnd >= 0) {
    const line = state.rxBuffer.slice(0, lineEnd).replace(/\r$/, "");
    state.rxBuffer = state.rxBuffer.slice(lineEnd + 1);
    handleLine(line, "RX");
    lineEnd = state.rxBuffer.indexOf("\n");
  }
}

async function sendFrame(frame) {
  const line = normalizeLine(frame);
  appendLog("TX", line);
  el.lastTx.textContent = line;
  if (!state.writer) {
    appendLog("SYS", "TX_DRY_RUN,no_serial_connection");
    renderLogs();
    return;
  }
  try {
    const encoder = new TextEncoder();
    await state.writer.write(encoder.encode(`${line}\n`));
  } catch (error) {
    appendLog("SYS", `WRITE_ERROR,${error.message}`);
  }
}

function handleLine(line, direction) {
  const normalized = normalizeLine(line);
  appendLog(direction, normalized);
  if (direction === "RX") el.lastRx.textContent = normalized;

  const parsed = parseFrame(normalized);
  if (!parsed) {
    state.parseErrorCount += 1;
    renderAll();
    return;
  }

  if (parsed.type === "TEL") {
    state.telemetry = { ...state.telemetry, ...parsed.fields };
    state.lastTelAt = performance.now();
  } else if (parsed.type === "ACK") {
    state.ackCount += 1;
    el.lastAck.textContent = normalized;
  } else if (parsed.type === "ERR") {
    state.errCount += 1;
    el.lastErr.textContent = normalized;
    el.lastCode.textContent = parsed.fields.code || "-";
  } else if (parsed.type === "PONG") {
    el.lastAck.textContent = normalized;
  }

  renderAll();
}

function parseFrame(line) {
  if (!line || !line.trim()) return null;
  const tokens = line.split(",");
  const type = tokens[0].trim().toUpperCase();
  if (!type) return null;
  const fields = {};
  for (const token of tokens.slice(1)) {
    if (!token) continue;
    const idx = token.indexOf("=");
    if (idx < 0) {
      fields[token.trim()] = "";
      continue;
    }
    const key = token.slice(0, idx).trim();
    const value = token.slice(idx + 1).trim();
    fields[key] = value;
  }
  return { type, fields, raw: line };
}

function normalizeLine(line) {
  return String(line ?? "").trim().replace(/\r?\n/g, "");
}

function nextSeq() {
  if (!el.autoSeq.checked) return Number(el.seqInput.value || 0);
  const seq = state.seq;
  state.seq += 1;
  el.seqInput.value = state.seq;
  return seq;
}

function makeSimpleFrame(type) {
  return `${type},seq=${nextSeq()}`;
}

function readCommandInputs() {
  return {
    vx: Number(el.vxInput.value || 0),
    w: Number(el.wInput.value || 0),
    timeout: readTimeout(),
  };
}

function readTimeout() {
  return Number(el.timeoutInput.value || 300);
}

function makeCmdFrame({ vx, w, timeout }) {
  return `CMD,seq=${nextSeq()},vx_mmps=${vx},w_mradps=${w},timeout_ms=${timeout}`;
}

function makeRawFrame(raw) {
  return normalizeLine(raw);
}

function toggleKeepalive() {
  if (state.keepaliveTimer) {
    stopKeepalive();
    return;
  }
  el.keepaliveBtn.classList.add("primary");
  state.keepaliveTimer = setInterval(() => {
    sendFrame(makeCmdFrame({ vx: 0, w: 0, timeout: readTimeout() }));
  }, 50);
}

function stopKeepalive() {
  if (state.keepaliveTimer) {
    clearInterval(state.keepaliveTimer);
    state.keepaliveTimer = null;
  }
  el.keepaliveBtn.classList.remove("primary");
}

async function runScriptedTest() {
  const frames = [
    "PING,seq=1",
    "CMD,seq=2,vx_mmps=80,w_mradps=0,timeout_ms=300",
    "ARM,seq=3",
    "CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300",
    "CMD,seq=5,vx_mmps=80,timeout_ms=300",
    "CMD,seq=6,vx_mmps=9999,w_mradps=0,timeout_ms=300",
    "CMD,seq=7,vx_mmps=0,w_mradps=0,timeout_ms=300",
    "DISARM,seq=8",
  ];
  el.scriptedBtn.disabled = true;
  try {
    for (const frame of frames) {
      await sendFrame(frame);
      await delay(SCRIPTED_DELAY_MS);
    }
    state.seq = 9;
    el.seqInput.value = "9";
  } finally {
    el.scriptedBtn.disabled = false;
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function toggleFakeTelemetry() {
  if (state.fakeTimer) {
    clearInterval(state.fakeTimer);
    state.fakeTimer = null;
    el.fakeToggleBtn.classList.remove("primary");
    appendLog("SYS", "FAKE_TEL_STOP");
    return;
  }
  el.fakeToggleBtn.classList.add("primary");
  appendLog("SYS", "FAKE_TEL_START");
  const start = performance.now();
  state.fakeTimer = setInterval(() => {
    const t = Math.floor(performance.now() - start);
    const phase = Math.sin(t / 900);
    const tel = [
      "TEL",
      `t_ms=${t}`,
      `state=${phase > -0.6 ? "ARMED" : "DISARMED"}`,
      `batt_mv=${11800 + Math.floor(phase * 40)}`,
      `left_cps=${Math.floor(120 + phase * 25)}`,
      `right_cps=${Math.floor(118 - phase * 18)}`,
      `left_pwm=${Math.floor(410 + phase * 30)}`,
      `right_pwm=${Math.floor(405 - phase * 20)}`,
      "fault=0",
    ].join(",");
    handleLine(tel, "RX");
  }, 100);
}

function appendLog(direction, line) {
  const entry = {
    time: new Date().toISOString(),
    direction,
    line: normalizeLine(line),
  };
  state.logs.push(entry);
  if (state.logs.length > MAX_LOG_LINES) state.logs.shift();
  state.csvRows.push(entry);
  renderLogs();
}

function clearLogs() {
  state.logs = [];
  state.csvRows = [];
  renderLogs();
}

function downloadCsv() {
  const rows = [["timestamp", "direction", "frame_type", "seq", "state", "code", "raw"]];
  for (const entry of state.csvRows) {
    const parsed = parseFrame(entry.line);
    rows.push([
      entry.time,
      entry.direction,
      parsed?.type || "",
      parsed?.fields.seq || "",
      parsed?.fields.state || "",
      parsed?.fields.code || "",
      entry.line,
    ]);
  }
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `uart_mvp_${new Date().toISOString().replace(/[:.]/g, "-")}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function renderAll() {
  renderConnection();
  renderTelemetry();
  renderCounters();
  renderLogs();
}

function renderConnection() {
  el.connectionState.textContent = state.connected ? "CONNECTED" : "DISCONNECTED";
  el.connectionState.className = state.connected ? "state-armed" : "state-disconnected";
  el.connectBtn.disabled = state.connected || !("serial" in navigator) || !window.isSecureContext;
  el.disconnectBtn.disabled = !state.connected;
}

function renderTelemetry() {
  const tel = state.telemetry;
  el.robotState.textContent = tel.state || "UNKNOWN";
  el.robotState.className = stateClass(tel.state);
  el.telTime.textContent = tel.t_ms || "0";
  el.telBattery.textContent = tel.batt_mv || "0";
  el.telLeftCps.textContent = tel.left_cps || "0";
  el.telRightCps.textContent = tel.right_cps || "0";
  el.telLeftPwm.textContent = tel.left_pwm || "0";
  el.telRightPwm.textContent = tel.right_pwm || "0";
  el.telFault.textContent = tel.fault || "0";
}

function stateClass(robotState) {
  const value = String(robotState || "").toUpperCase();
  if (value === "ARMED") return "state-armed";
  if (value === "DISARMED") return "state-disarmed";
  if (value === "FAULT") return "state-fault";
  return "";
}

function renderCounters() {
  el.lastSeq.textContent = String(state.seq - 1);
  el.ackCount.textContent = String(state.ackCount);
  el.errCount.textContent = String(state.errCount);
  el.parseErrorCount.textContent = String(state.parseErrorCount);
}

function updateAge() {
  if (!state.lastTelAt) {
    el.lastTelAge.textContent = "-";
    return;
  }
  const age = Math.floor(performance.now() - state.lastTelAt);
  el.lastTelAge.textContent = `${age} ms`;
  el.lastTelAge.className = age > TEL_STALE_MS ? "state-disarmed" : "state-armed";
}

function renderLogs() {
  el.rawLog.textContent = state.logs
    .map((entry) => `${entry.time} ${entry.direction.padEnd(3, " ")} ${entry.line}`)
    .join("\n");
  el.logCount.textContent = `${state.logs.length} lines`;
  el.rawLog.scrollTop = el.rawLog.scrollHeight;
}
