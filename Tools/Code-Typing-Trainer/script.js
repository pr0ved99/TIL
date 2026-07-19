"use strict";

const STORAGE_KEY = "codeTypingTrainer.v1";
const STORAGE_VERSION = 1;
const HISTORY_LIMIT = 200;
const CUSTOM_CODE_LIMIT = 10000;
const CUSTOM_SNIPPET_LIMIT = 100;
const TAB_SIZE = 4;

const CATEGORY_META = Object.freeze({
  "embedded-c": { label: "Embedded C", fileName: "main.c" },
  cpp: { label: "C++", fileName: "trainer.cpp" },
  python: { label: "Python", fileName: "trainer.py" },
  ros2: { label: "ROS 2", fileName: "robot_node.py" },
});

const DIFFICULTY_LABELS = Object.freeze({
  easy: "초급",
  medium: "중급",
  hard: "고급",
  custom: "사용자",
});

const BUILT_IN_SNIPPETS = Object.freeze([
  {
    id: "ec-gpio-write",
    category: "embedded-c",
    title: "GPIO 출력 제어",
    difficulty: "easy",
    fileName: "gpio_control.c",
    code: `static void led_set(bool enabled)
{
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                      enabled ? GPIO_PIN_SET : GPIO_PIN_RESET);
}`,
  },
  {
    id: "ec-pwm-clamp",
    category: "embedded-c",
    title: "PWM 명령 제한",
    difficulty: "medium",
    fileName: "motor_control.c",
    code: `static uint16_t clamp_pwm(int32_t command)
{
    if (command < 0) {
        return 0U;
    }
    if (command > 999) {
        return 999U;
    }
    return (uint16_t)command;
}`,
  },
  {
    id: "ec-uart-callback",
    category: "embedded-c",
    title: "UART 인터럽트 수신",
    difficulty: "hard",
    fileName: "uart_bridge.c",
    code: `void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        rx_buffer[rx_head] = rx_byte;
        rx_head = (rx_head + 1U) % RX_BUFFER_SIZE;
        HAL_UART_Receive_IT(huart, &rx_byte, 1U);
    }
}`,
  },
  {
    id: "cpp-velocity-limit",
    category: "cpp",
    title: "속도 명령 제한",
    difficulty: "easy",
    fileName: "velocity_limiter.cpp",
    code: `#include <algorithm>

double limitVelocity(double command, double maximum)
{
    return std::clamp(command, -maximum, maximum);
}`,
  },
  {
    id: "cpp-low-pass-filter",
    category: "cpp",
    title: "저역 통과 필터",
    difficulty: "medium",
    fileName: "low_pass_filter.cpp",
    code: `class LowPassFilter {
public:
    explicit LowPassFilter(float alpha) : alpha_(alpha) {}

    float update(float sample)
    {
        state_ += alpha_ * (sample - state_);
        return state_;
    }

private:
    float alpha_;
    float state_{0.0F};
};`,
  },
  {
    id: "cpp-sensor-mean",
    category: "cpp",
    title: "센서 평균 계산",
    difficulty: "medium",
    fileName: "sensor_mean.cpp",
    code: `#include <array>
#include <numeric>

float mean(const std::array<float, 3>& values)
{
    const float sum = std::accumulate(values.begin(), values.end(), 0.0F);
    return sum / static_cast<float>(values.size());
}`,
  },
  {
    id: "py-encoder-parser",
    category: "python",
    title: "엔코더 패킷 파싱",
    difficulty: "easy",
    fileName: "encoder_parser.py",
    code: `def parse_encoder(line: str) -> tuple[int, int]:
    left_text, right_text = line.strip().split(",")
    return int(left_text), int(right_text)`,
  },
  {
    id: "py-moving-average",
    category: "python",
    title: "이동 평균 필터",
    difficulty: "medium",
    fileName: "moving_average.py",
    code: `from collections import deque

samples = deque(maxlen=10)

def moving_average(value: float) -> float:
    samples.append(value)
    return sum(samples) / len(samples)`,
  },
  {
    id: "py-async-sensor",
    category: "python",
    title: "비동기 센서 폴링",
    difficulty: "hard",
    fileName: "sensor_stream.py",
    code: `async def poll_sensor(reader):
    while True:
        packet = await reader.readexactly(8)
        yield int.from_bytes(packet, byteorder="little", signed=False)`,
  },
  {
    id: "ros2-battery-publisher",
    category: "ros2",
    title: "rclpy 배터리 발행",
    difficulty: "medium",
    fileName: "battery_publisher.py",
    code: `class BatteryPublisher(Node):
    def __init__(self):
        super().__init__("battery_publisher")
        self.publisher = self.create_publisher(Float32, "battery_voltage", 10)
        self.timer = self.create_timer(1.0, self.publish_voltage)

    def publish_voltage(self):
        msg = Float32()
        msg.data = 12.4
        self.publisher.publish(msg)`,
  },
  {
    id: "ros2-sensor-qos",
    category: "ros2",
    title: "센서 QoS 구독",
    difficulty: "hard",
    fileName: "safety_node.cpp",
    code: `auto qos = rclcpp::SensorDataQoS().keep_last(5);
scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
    "scan", qos,
    std::bind(&SafetyNode::scanCallback, this, std::placeholders::_1));`,
  },
  {
    id: "ros2-launch-node",
    category: "ros2",
    title: "ROS 2 launch 구성",
    difficulty: "hard",
    fileName: "monitor.launch.py",
    code: `from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="robot_monitor",
            executable="battery_node",
            name="battery_monitor",
            parameters=[{"warning_voltage": 11.0}],
            output="screen",
        )
    ])`,
  },
]);

const elements = {
  storageStatus: document.querySelector("#storageStatus"),
  storageStatusText: document.querySelector("#storageStatusText"),
  categorySelect: document.querySelector("#categorySelect"),
  customCategorySelect: document.querySelector("#customCategorySelect"),
  categoryEyebrow: document.querySelector("#categoryEyebrow"),
  snippetTitle: document.querySelector("#snippetTitle"),
  difficultyBadge: document.querySelector("#difficultyBadge"),
  sourceBadge: document.querySelector("#sourceBadge"),
  snippetCounter: document.querySelector("#snippetCounter"),
  fileNameLabel: document.querySelector("#fileNameLabel"),
  inputState: document.querySelector("#inputState"),
  inputStateText: document.querySelector("#inputStateText"),
  typingStage: document.querySelector("#typingStage"),
  typingInput: document.querySelector("#typingInput"),
  codeDisplay: document.querySelector("#codeDisplay"),
  typingFeedback: document.querySelector("#typingFeedback"),
  typingFeedbackText: document.querySelector("#typingFeedbackText"),
  timerValue: document.querySelector("#timerValue"),
  accuracyValue: document.querySelector("#accuracyValue"),
  cpmValue: document.querySelector("#cpmValue"),
  wpmValue: document.querySelector("#wpmValue"),
  errorValue: document.querySelector("#errorValue"),
  progressValue: document.querySelector("#progressValue"),
  progressPercent: document.querySelector("#progressPercent"),
  progressBar: document.querySelector("#progressBar"),
  restartButton: document.querySelector("#restartButton"),
  nextButton: document.querySelector("#nextButton"),
  completionNextButton: document.querySelector("#completionNextButton"),
  completionCard: document.querySelector("#completionCard"),
  completionSummary: document.querySelector("#completionSummary"),
  manageSnippetsButton: document.querySelector("#manageSnippetsButton"),
  customDialog: document.querySelector("#customDialog"),
  closeDialogButton: document.querySelector("#closeDialogButton"),
  cancelDialogButton: document.querySelector("#cancelDialogButton"),
  customSnippetForm: document.querySelector("#customSnippetForm"),
  customTitleInput: document.querySelector("#customTitleInput"),
  customCodeInput: document.querySelector("#customCodeInput"),
  customCodeCount: document.querySelector("#customCodeCount"),
  customFormFeedback: document.querySelector("#customFormFeedback"),
  customSnippetCount: document.querySelector("#customSnippetCount"),
  customSnippetList: document.querySelector("#customSnippetList"),
  totalSessionsValue: document.querySelector("#totalSessionsValue"),
  bestAccuracyValue: document.querySelector("#bestAccuracyValue"),
  bestWpmValue: document.querySelector("#bestWpmValue"),
  totalPracticeValue: document.querySelector("#totalPracticeValue"),
  historyCountLabel: document.querySelector("#historyCountLabel"),
  historyTableBody: document.querySelector("#historyTableBody"),
  clearHistoryButton: document.querySelector("#clearHistoryButton"),
  announcement: document.querySelector("#announcement"),
};

let storageAvailable = true;
let storageWarning = "";
let persistedData = loadPersistedData();

const session = {
  category: isKnownCategory(persistedData.settings.category)
    ? persistedData.settings.category
    : "embedded-c",
  snippetIndex: 0,
  currentSnippet: null,
  targetChars: [],
  typedChars: [],
  characterElements: [],
  status: "idle",
  startedAt: 0,
  elapsedMs: 0,
  correctAttempts: 0,
  incorrectAttempts: 0,
  backspaceCount: 0,
  timerId: null,
  isComposing: false,
  saved: false,
};

initialize();

function initialize() {
  bindEvents();
  elements.categorySelect.value = session.category;
  elements.customCategorySelect.value = session.category;
  updateStorageStatus();
  renderHistory();
  renderCustomSnippetList();
  loadSnippet(0);
}

function bindEvents() {
  elements.categorySelect.addEventListener("change", handleCategoryChange);
  elements.restartButton.addEventListener("click", restartCurrentSnippet);
  elements.nextButton.addEventListener("click", goToNextSnippet);
  elements.completionNextButton.addEventListener("click", goToNextSnippet);

  elements.typingStage.addEventListener("click", focusTypingInput);
  elements.typingInput.addEventListener("input", handleTypingInput);
  elements.typingInput.addEventListener("keydown", handleTypingKeyDown);
  elements.typingInput.addEventListener("beforeinput", handleBeforeInput);
  elements.typingInput.addEventListener("compositionstart", () => {
    session.isComposing = true;
  });
  elements.typingInput.addEventListener("compositionend", () => {
    session.isComposing = false;
    syncTypedValue();
  });
  elements.typingInput.addEventListener("paste", blockPracticePaste);
  elements.typingInput.addEventListener("drop", blockPracticePaste);
  elements.typingInput.addEventListener("select", keepCaretAtEnd);

  elements.manageSnippetsButton.addEventListener("click", openCustomDialog);
  elements.closeDialogButton.addEventListener("click", closeCustomDialog);
  elements.cancelDialogButton.addEventListener("click", closeCustomDialog);
  elements.customDialog.addEventListener("click", handleDialogBackdropClick);
  elements.customSnippetForm.addEventListener("submit", saveCustomSnippet);
  elements.customCodeInput.addEventListener("input", updateCustomCodeCount);
  elements.customCodeInput.addEventListener("keydown", insertTabInCustomEditor);
  elements.customSnippetList.addEventListener("click", deleteCustomSnippet);

  elements.clearHistoryButton.addEventListener("click", clearHistory);
  window.addEventListener("storage", syncPersistedDataFromOtherTab);
  window.addEventListener("beforeunload", stopTimer);
}

function getSnippetsForCategory(category) {
  const builtIn = BUILT_IN_SNIPPETS.filter((snippet) => snippet.category === category);
  const custom = persistedData.customSnippets
    .filter((snippet) => snippet.category === category)
    .map((snippet) => ({ ...snippet, difficulty: "custom", isCustom: true }));

  return [...builtIn, ...custom];
}

function loadSnippet(reference = 0) {
  const snippets = getSnippetsForCategory(session.category);
  if (snippets.length === 0) {
    return;
  }

  let nextIndex;
  if (typeof reference === "string") {
    const foundIndex = snippets.findIndex((snippet) => snippet.id === reference);
    nextIndex = foundIndex >= 0 ? foundIndex : 0;
  } else {
    nextIndex = ((reference % snippets.length) + snippets.length) % snippets.length;
  }

  stopTimer();
  session.snippetIndex = nextIndex;
  session.currentSnippet = snippets[nextIndex];
  session.targetChars = Array.from(normalizeCode(session.currentSnippet.code));
  session.typedChars = [];
  session.characterElements = [];
  session.status = "idle";
  session.startedAt = 0;
  session.elapsedMs = 0;
  session.correctAttempts = 0;
  session.incorrectAttempts = 0;
  session.backspaceCount = 0;
  session.isComposing = false;
  session.saved = false;

  elements.typingInput.disabled = false;
  elements.typingInput.value = "";
  elements.typingStage.dataset.complete = "false";
  elements.typingStage.scrollTop = 0;
  elements.typingStage.scrollLeft = 0;
  elements.completionCard.hidden = true;

  renderSnippetHeader(snippets.length);
  renderCodeCharacters();
  renderMetrics();
  setInputState("ready", "입력 대기");
  setFeedback("neutral", "첫 글자를 입력하면 타이머가 시작됩니다.", "⌨");
  announce(`${CATEGORY_META[session.category].label}, ${session.currentSnippet.title} 문제를 불러왔습니다.`);
}

function renderSnippetHeader(totalSnippets) {
  const snippet = session.currentSnippet;
  const category = CATEGORY_META[session.category];
  const level = snippet.difficulty || "custom";

  elements.categoryEyebrow.textContent = `${category.label.toUpperCase()} · TARGET`;
  elements.snippetTitle.textContent = snippet.title;
  elements.difficultyBadge.textContent = DIFFICULTY_LABELS[level] || "사용자";
  elements.difficultyBadge.dataset.level = level;
  elements.sourceBadge.textContent = snippet.isCustom ? "내 코드" : "기본 문제";
  elements.snippetCounter.textContent = `${session.snippetIndex + 1} / ${totalSnippets}`;
  elements.fileNameLabel.textContent = snippet.fileName || category.fileName;
}

function renderCodeCharacters() {
  const fragment = document.createDocumentFragment();

  session.targetChars.forEach((character, index) => {
    const span = document.createElement("span");
    span.className = "code-character pending";
    span.textContent = character;
    span.dataset.index = String(index);

    if (character === " ") {
      span.classList.add("space");
    } else if (character === "\n") {
      span.classList.add("newline");
    }

    session.characterElements.push(span);
    fragment.append(span);
  });

  elements.codeDisplay.replaceChildren(fragment);
  updateCharacterState(0);
  updateTypingInputLabel();
}

function updateCharacterState(index) {
  const characterElement = session.characterElements[index];
  if (!characterElement) {
    return;
  }

  characterElement.classList.remove("correct", "incorrect", "pending", "current");
  characterElement.removeAttribute("title");

  if (index < session.typedChars.length) {
    const isCorrect = session.typedChars[index] === session.targetChars[index];
    characterElement.classList.add(isCorrect ? "correct" : "incorrect");

    if (!isCorrect) {
      characterElement.title = `예상: ${describeCharacter(session.targetChars[index])} / 입력: ${describeCharacter(session.typedChars[index])}`;
    }
  } else {
    characterElement.classList.add("pending");
  }

  if (
    session.status !== "completed"
    && index === session.typedChars.length
    && index < session.targetChars.length
  ) {
    characterElement.classList.add("current");
  }
}

function syncCharacterDisplay(previousChars, nextChars) {
  let firstDifference = 0;
  const sharedLength = Math.min(previousChars.length, nextChars.length);

  while (
    firstDifference < sharedLength
    && previousChars[firstDifference] === nextChars[firstDifference]
  ) {
    firstDifference += 1;
  }

  const changedEnd = Math.max(previousChars.length, nextChars.length);
  for (let index = firstDifference; index < changedEnd; index += 1) {
    updateCharacterState(index);
  }

  updateCharacterState(previousChars.length);
  updateCharacterState(nextChars.length);
  updateTypingInputLabel();
  scrollCurrentCharacterIntoView();
}

function handleCategoryChange(event) {
  session.category = isKnownCategory(event.target.value)
    ? event.target.value
    : "embedded-c";
  persistedData.settings.category = session.category;
  savePersistedData();
  elements.customCategorySelect.value = session.category;
  loadSnippet(0);
}

function restartCurrentSnippet() {
  const currentId = session.currentSnippet?.id;
  loadSnippet(currentId || session.snippetIndex);
  focusTypingInput();
}

function goToNextSnippet() {
  const snippets = getSnippetsForCategory(session.category);
  loadSnippet((session.snippetIndex + 1) % snippets.length);
  focusTypingInput();
}

function focusTypingInput() {
  if (session.status === "completed") {
    return;
  }

  elements.typingInput.focus({ preventScroll: true });
  moveCaretToEnd();
}

function handleTypingInput() {
  if (session.isComposing || session.status === "completed") {
    return;
  }

  syncTypedValue();
}

function handleBeforeInput(event) {
  if (event.inputType === "insertFromPaste" || event.inputType === "insertFromDrop") {
    blockPracticePaste(event);
    return;
  }

  if (session.isComposing) {
    return;
  }

  const atEnd = elements.typingInput.selectionStart === elements.typingInput.value.length
    && elements.typingInput.selectionEnd === elements.typingInput.value.length;

  if (!atEnd) {
    event.preventDefault();
    moveCaretToEnd();
  }
}

function handleTypingKeyDown(event) {
  if (event.key === "Escape") {
    event.preventDefault();
    elements.typingInput.blur();
    announce("코드 입력 포커스를 해제했습니다.");
    return;
  }

  if (event.key === "Tab" && !event.shiftKey) {
    event.preventDefault();
    insertPracticeTab();
    return;
  }

  if (event.key === "Tab" && event.shiftKey) {
    return;
  }

  if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "Delete", "PageUp", "PageDown"].includes(event.key)) {
    event.preventDefault();
    moveCaretToEnd();
  }
}

function insertPracticeTab() {
  if (session.status === "completed") {
    return;
  }

  if (session.typedChars.length >= session.targetChars.length) {
    showFullTargetMessage();
    return;
  }

  const targetPrefix = session.targetChars.slice(0, session.typedChars.length);
  const currentColumn = getCurrentColumn(targetPrefix);
  const spacesToInsert = TAB_SIZE - (currentColumn % TAB_SIZE);
  const remainingSlots = session.targetChars.length - session.typedChars.length;
  const spaces = " ".repeat(Math.min(spacesToInsert, remainingSlots));

  elements.typingInput.value = session.typedChars.join("") + spaces;
  syncTypedValue();
  moveCaretToEnd();
}

function syncTypedValue() {
  if (session.status === "completed") {
    return;
  }

  const previousChars = session.typedChars.slice();
  let nextChars = Array.from(elements.typingInput.value.replace(/\r\n?/g, "\n"));

  if (nextChars.length > session.targetChars.length) {
    nextChars = nextChars.slice(0, session.targetChars.length);
    elements.typingInput.value = nextChars.join("");
  }

  const sharedPrefixLength = getSharedPrefixLength(previousChars, nextChars);
  const isAppend = sharedPrefixLength === previousChars.length && nextChars.length >= previousChars.length;
  const isDelete = sharedPrefixLength === nextChars.length && nextChars.length < previousChars.length;
  const isNoChange = previousChars.length === nextChars.length
    && sharedPrefixLength === previousChars.length;

  if (!isAppend && !isDelete && !isNoChange) {
    elements.typingInput.value = previousChars.join("");
    moveCaretToEnd();
    return;
  }

  if (isNoChange) {
    moveCaretToEnd();
    return;
  }

  if (isAppend && nextChars.length > previousChars.length) {
    startTimer();

    for (let index = previousChars.length; index < nextChars.length; index += 1) {
      if (nextChars[index] === session.targetChars[index]) {
        session.correctAttempts += 1;
      } else {
        session.incorrectAttempts += 1;
      }
    }
  }

  if (isDelete) {
    session.backspaceCount += previousChars.length - nextChars.length;
  }

  session.typedChars = nextChars;
  syncCharacterDisplay(previousChars, nextChars);
  updateTypingFeedback(previousChars, nextChars);
  renderMetrics();
  checkForCompletion();
  moveCaretToEnd();
}

function updateTypingFeedback(previousChars, nextChars) {
  if (nextChars.length === 0) {
    const message = session.status === "running"
      ? "입력을 모두 지웠습니다. 타이머는 계속 측정됩니다."
      : "첫 글자를 입력하면 타이머가 시작됩니다.";
    setFeedback("neutral", message, session.status === "running" ? "↶" : "⌨");
    return;
  }

  if (nextChars.length < previousChars.length) {
    setFeedback("neutral", "마지막 입력을 지웠습니다. 현재 강조된 위치부터 다시 입력하세요.", "↶");
    return;
  }

  const latestIndex = nextChars.length - 1;
  const expected = session.targetChars[latestIndex];
  const typed = nextChars[latestIndex];

  if (typed !== expected) {
    const position = getLineAndColumn(latestIndex);
    const errorMessage = `오타 · ${position} · 예상 ${describeCharacter(expected)}, 입력 ${describeCharacter(typed)}`;
    setFeedback(
      "error",
      errorMessage,
      "!",
    );
    announce(errorMessage);
    return;
  }

  if (nextChars.length === session.targetChars.length) {
    setFeedback("success", "마지막 글자까지 정확하게 입력했습니다.", "✓");
  } else {
    setFeedback("neutral", "좋습니다. 현재 강조된 글자를 이어서 입력하세요.", "⌨");
  }
}

function checkForCompletion() {
  if (session.typedChars.length !== session.targetChars.length) {
    return;
  }

  const allCorrect = session.typedChars.every(
    (character, index) => character === session.targetChars[index],
  );

  if (!allCorrect) {
    showFullTargetMessage();
    return;
  }

  completeSession();
}

function showFullTargetMessage() {
  const firstErrorIndex = session.typedChars.findIndex(
    (character, index) => character !== session.targetChars[index],
  );

  if (firstErrorIndex >= 0) {
    const errorMessage = `${getLineAndColumn(firstErrorIndex)}에 오타가 남아 있습니다. Backspace로 해당 위치까지 돌아가세요.`;
    setFeedback(
      "error",
      errorMessage,
      "!",
    );
    announce(errorMessage);
  }
}

function startTimer() {
  if (session.status !== "idle") {
    return;
  }

  session.status = "running";
  session.startedAt = performance.now();
  setInputState("running", "입력 중");
  session.timerId = window.setInterval(renderMetrics, 100);
}

function stopTimer() {
  if (session.timerId !== null) {
    window.clearInterval(session.timerId);
    session.timerId = null;
  }
}

function completeSession() {
  if (session.status === "completed" || session.saved) {
    return;
  }

  session.elapsedMs = Math.max(0, performance.now() - session.startedAt);
  session.status = "completed";
  session.saved = true;
  stopTimer();
  elements.typingInput.disabled = true;
  elements.typingStage.dataset.complete = "true";
  setInputState("complete", "완료");

  const stats = calculateMetrics();
  const record = {
    id: createId("record"),
    snippetId: session.currentSnippet.id,
    title: session.currentSnippet.title,
    category: session.category,
    completedAt: new Date().toISOString(),
    durationMs: Math.round(session.elapsedMs),
    totalChars: session.targetChars.length,
    correctAttempts: session.correctAttempts,
    incorrectAttempts: session.incorrectAttempts,
    backspaceCount: session.backspaceCount,
    accuracy: roundTo(stats.accuracy, 1),
    cpm: Math.round(stats.cpm),
    wpm: Math.round(stats.wpm),
  };

  persistedData.history.unshift(record);
  persistedData.history = persistedData.history.slice(0, HISTORY_LIMIT);
  const savedToStorage = savePersistedData();
  renderMetrics();
  renderHistory();

  elements.completionSummary.textContent = `${formatElapsed(session.elapsedMs)} · 정확도 ${record.accuracy.toFixed(1)}% · ${record.wpm} WPM`;
  elements.completionCard.hidden = false;
  if (savedToStorage) {
    setFeedback("success", "완료 기록을 이 브라우저에 저장했습니다.", "✓");
  } else {
    setFeedback("error", "문제는 완료했지만 로컬 저장소에 기록하지 못했습니다.", "!");
  }
  announce(
    savedToStorage
      ? `${session.currentSnippet.title} 완료. 정확도 ${record.accuracy.toFixed(1)}퍼센트, ${record.wpm} WPM이며 기록을 저장했습니다.`
      : `${session.currentSnippet.title} 완료. 기록은 로컬 저장소에 저장하지 못했습니다.`,
  );
  elements.completionCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  window.requestAnimationFrame(() => {
    elements.completionNextButton.focus({ preventScroll: true });
  });
}

function renderMetrics() {
  if (session.status === "running") {
    session.elapsedMs = Math.max(0, performance.now() - session.startedAt);
  }

  const metrics = calculateMetrics();
  const typedCount = session.typedChars.length;
  const totalCount = session.targetChars.length;
  const progress = totalCount > 0 ? (typedCount / totalCount) * 100 : 0;

  elements.timerValue.textContent = formatElapsed(session.elapsedMs);
  elements.accuracyValue.textContent = `${metrics.accuracy.toFixed(1)}%`;
  elements.cpmValue.textContent = String(Math.round(metrics.cpm));
  elements.wpmValue.textContent = String(Math.round(metrics.wpm));
  elements.errorValue.textContent = String(session.incorrectAttempts);
  elements.progressValue.textContent = `${typedCount} / ${totalCount}`;
  elements.progressPercent.textContent = `${Math.floor(progress)}% 완료`;
  elements.progressBar.style.width = `${Math.min(100, progress)}%`;
}

function calculateMetrics() {
  const attempts = session.correctAttempts + session.incorrectAttempts;
  const accuracy = attempts > 0 ? (session.correctAttempts / attempts) * 100 : 100;
  const correctPositions = session.typedChars.reduce(
    (count, character, index) => count + (character === session.targetChars[index] ? 1 : 0),
    0,
  );
  const elapsedMinutes = session.elapsedMs / 60000;
  const cpm = elapsedMinutes > 0
    ? correctPositions / elapsedMinutes
    : 0;

  return {
    accuracy,
    cpm,
    wpm: cpm / 5,
    correctPositions,
  };
}

function setInputState(state, label) {
  elements.inputState.dataset.state = state;
  elements.inputStateText.textContent = label;
}

function updateTypingInputLabel() {
  if (session.status === "completed" || session.typedChars.length >= session.targetChars.length) {
    elements.typingInput.setAttribute("aria-label", "코드 입력, 마지막 위치");
    return;
  }

  const index = session.typedChars.length;
  elements.typingInput.setAttribute(
    "aria-label",
    `코드 입력, ${getLineAndColumn(index)}, 예상 ${describeCharacter(session.targetChars[index])}`,
  );
}

function setFeedback(state, message, icon) {
  elements.typingFeedback.dataset.state = state;
  elements.typingFeedbackText.textContent = message;
  elements.typingFeedback.querySelector(".feedback-icon").textContent = icon;
}

function blockPracticePaste(event) {
  event.preventDefault();
  setFeedback("error", "연습 입력에는 붙여넣기를 사용할 수 없습니다. 한 글자씩 입력해 주세요.", "!");
  announce("연습 입력에서는 붙여넣기를 사용할 수 없습니다.");
}

function keepCaretAtEnd() {
  if (document.activeElement !== elements.typingInput || session.isComposing) {
    return;
  }

  window.requestAnimationFrame(moveCaretToEnd);
}

function moveCaretToEnd() {
  const end = elements.typingInput.value.length;
  try {
    elements.typingInput.setSelectionRange(end, end);
  } catch {
    // 비활성화된 입력창에서는 selection API가 실패할 수 있다.
  }
}

function scrollCurrentCharacterIntoView() {
  const current = session.characterElements[session.typedChars.length];
  if (!current) {
    return;
  }

  window.requestAnimationFrame(() => {
    current.scrollIntoView({ block: "nearest", inline: "nearest" });
  });
}

function openCustomDialog() {
  elements.customCategorySelect.value = session.category;
  elements.customFormFeedback.textContent = "";
  updateCustomCodeCount();
  renderCustomSnippetList();

  if (typeof elements.customDialog.showModal === "function") {
    elements.customDialog.showModal();
  } else {
    elements.customDialog.setAttribute("open", "");
  }

  window.requestAnimationFrame(() => elements.customTitleInput.focus());
}

function closeCustomDialog() {
  if (typeof elements.customDialog.close === "function") {
    elements.customDialog.close();
  } else {
    elements.customDialog.removeAttribute("open");
  }
}

function handleDialogBackdropClick(event) {
  if (event.target !== elements.customDialog) {
    return;
  }

  const bounds = elements.customDialog.getBoundingClientRect();
  const clickedInside = event.clientX >= bounds.left
    && event.clientX <= bounds.right
    && event.clientY >= bounds.top
    && event.clientY <= bounds.bottom;

  if (!clickedInside) {
    closeCustomDialog();
  }
}

function updateCustomCodeCount() {
  elements.customCodeCount.textContent = String(Array.from(elements.customCodeInput.value).length);
}

function insertTabInCustomEditor(event) {
  if (event.key !== "Tab" || event.shiftKey) {
    return;
  }

  event.preventDefault();
  const textarea = elements.customCodeInput;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const valueBeforeCaret = textarea.value.slice(0, start);
  const currentLine = valueBeforeCaret.slice(valueBeforeCaret.lastIndexOf("\n") + 1);
  const spaces = " ".repeat(TAB_SIZE - (Array.from(currentLine).length % TAB_SIZE));

  textarea.setRangeText(spaces, start, end, "end");
  updateCustomCodeCount();
}

function saveCustomSnippet(event) {
  event.preventDefault();
  const title = elements.customTitleInput.value.trim();
  const rawCode = elements.customCodeInput.value.replace(/\r\n?/g, "\n");
  const category = isKnownCategory(elements.customCategorySelect.value)
    ? elements.customCategorySelect.value
    : "embedded-c";

  if (!title) {
    elements.customFormFeedback.textContent = "문제 제목을 입력해 주세요.";
    elements.customTitleInput.focus();
    return;
  }

  if (rawCode.trim().length === 0) {
    elements.customFormFeedback.textContent = "연습할 코드를 한 글자 이상 입력해 주세요.";
    elements.customCodeInput.focus();
    return;
  }

  if (persistedData.customSnippets.length >= CUSTOM_SNIPPET_LIMIT) {
    elements.customFormFeedback.textContent = `사용자 코드는 최대 ${CUSTOM_SNIPPET_LIMIT}개까지 저장할 수 있습니다. 기존 문제를 삭제한 뒤 다시 시도해 주세요.`;
    return;
  }

  const normalizedCode = normalizeCode(rawCode);
  if (Array.from(normalizedCode).length > CUSTOM_CODE_LIMIT) {
    elements.customFormFeedback.textContent = "코드는 10,000자 이하로 입력해 주세요.";
    elements.customCodeInput.focus();
    return;
  }

  const snippet = {
    id: createId("custom"),
    category,
    title,
    code: normalizedCode,
    fileName: CATEGORY_META[category].fileName,
    createdAt: new Date().toISOString(),
  };

  persistedData.customSnippets.unshift(snippet);
  persistedData.settings.category = category;
  session.category = category;
  elements.categorySelect.value = category;
  const savedToStorage = savePersistedData();
  renderCustomSnippetList();
  elements.customSnippetForm.reset();
  elements.customCodeCount.textContent = "0";
  elements.customFormFeedback.textContent = "";
  closeCustomDialog();
  loadSnippet(snippet.id);
  if (!savedToStorage) {
    setFeedback("error", "내 코드는 이번 탭에서만 사용할 수 있으며 새로고침하면 사라집니다.", "!");
  }
  focusTypingInput();
  announce(
    savedToStorage
      ? `${title} 사용자 문제를 저장하고 연습 화면에 불러왔습니다.`
      : `${title} 사용자 문제를 현재 세션에 불러왔지만 로컬 저장소에는 저장하지 못했습니다.`,
  );
}

function renderCustomSnippetList() {
  elements.customSnippetCount.textContent = `${persistedData.customSnippets.length}개`;
  elements.customSnippetList.replaceChildren();

  if (persistedData.customSnippets.length === 0) {
    const emptyItem = document.createElement("li");
    emptyItem.className = "empty-custom-list";
    emptyItem.textContent = "아직 저장한 코드가 없습니다.";
    elements.customSnippetList.append(emptyItem);
    return;
  }

  const fragment = document.createDocumentFragment();
  persistedData.customSnippets.forEach((snippet) => {
    const item = document.createElement("li");
    const copy = document.createElement("span");
    const title = document.createElement("strong");
    const meta = document.createElement("small");
    const deleteButton = document.createElement("button");

    title.textContent = snippet.title;
    meta.textContent = `${CATEGORY_META[snippet.category].label} · ${Array.from(snippet.code).length}자`;
    copy.append(title, meta);

    deleteButton.type = "button";
    deleteButton.className = "delete-snippet-button";
    deleteButton.dataset.deleteSnippet = snippet.id;
    deleteButton.textContent = "삭제";
    deleteButton.setAttribute("aria-label", `${snippet.title} 코드 삭제`);

    item.append(copy, deleteButton);
    fragment.append(item);
  });

  elements.customSnippetList.append(fragment);
}

function deleteCustomSnippet(event) {
  const button = event.target.closest("[data-delete-snippet]");
  if (!button) {
    return;
  }

  const snippetId = button.dataset.deleteSnippet;
  const snippet = persistedData.customSnippets.find((item) => item.id === snippetId);
  if (!snippet) {
    return;
  }

  if (!window.confirm(`“${snippet.title}” 문제를 삭제할까요? 완료 기록은 유지됩니다.`)) {
    return;
  }

  const previousSnippets = persistedData.customSnippets;
  persistedData.customSnippets = previousSnippets.filter((item) => item.id !== snippetId);
  if (!savePersistedData()) {
    persistedData.customSnippets = previousSnippets;
    renderCustomSnippetList();
    announce(`${snippet.title} 문제를 삭제하지 못했습니다. 로컬 저장소 상태를 확인해 주세요.`);
    return;
  }
  renderCustomSnippetList();

  const remainingSnippets = getSnippetsForCategory(session.category);
  const currentIndex = remainingSnippets.findIndex(
    (item) => item.id === session.currentSnippet?.id,
  );

  if (currentIndex < 0) {
    loadSnippet(0);
  } else {
    session.snippetIndex = currentIndex;
    renderSnippetHeader(remainingSnippets.length);
  }

  announce(`${snippet.title} 사용자 문제를 삭제했습니다.`);
}

function renderHistory() {
  const history = persistedData.history;
  const totalDuration = history.reduce((sum, record) => sum + record.durationMs, 0);
  const bestAccuracy = history.length > 0
    ? Math.max(...history.map((record) => record.accuracy))
    : null;
  const bestWpm = history.length > 0
    ? Math.max(...history.map((record) => record.wpm))
    : null;

  elements.totalSessionsValue.textContent = String(history.length);
  elements.bestAccuracyValue.textContent = bestAccuracy === null ? "—" : `${bestAccuracy.toFixed(1)}%`;
  elements.bestWpmValue.textContent = bestWpm === null ? "—" : String(Math.round(bestWpm));
  elements.totalPracticeValue.textContent = formatTotalPractice(totalDuration);
  elements.historyCountLabel.textContent = `최근 ${Math.min(history.length, 10)}개`;
  elements.clearHistoryButton.disabled = history.length === 0;

  elements.historyTableBody.replaceChildren();
  if (history.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.className = "empty-history";
    cell.colSpan = 5;
    cell.textContent = "완료한 연습 기록이 아직 없습니다.";
    row.append(cell);
    elements.historyTableBody.append(row);
    return;
  }

  const fragment = document.createDocumentFragment();
  history.slice(0, 10).forEach((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCompletedAt(record.completedAt),
      record.title,
      CATEGORY_META[record.category]?.label || record.category,
      `${record.accuracy.toFixed(1)}% · ${record.wpm} WPM`,
      formatElapsed(record.durationMs),
    ];

    values.forEach((value, index) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (index === 3) {
        cell.className = "result-cell";
      }
      row.append(cell);
    });

    fragment.append(row);
  });

  elements.historyTableBody.append(fragment);
}

function clearHistory() {
  if (persistedData.history.length === 0) {
    return;
  }

  if (!window.confirm("저장된 모든 완료 기록을 삭제할까요? 사용자 코드는 유지됩니다.")) {
    return;
  }

  const previousHistory = persistedData.history;
  persistedData.history = [];
  if (!savePersistedData()) {
    persistedData.history = previousHistory;
    renderHistory();
    announce("완료 기록을 삭제하지 못했습니다. 로컬 저장소 상태를 확인해 주세요.");
    return;
  }
  renderHistory();
  announce("모든 완료 기록을 삭제했습니다.");
}

function loadPersistedData() {
  const defaultData = createDefaultPersistedData();

  try {
    const probeKey = `${STORAGE_KEY}.probe`;
    window.localStorage.setItem(probeKey, "1");
    window.localStorage.removeItem(probeKey);

    const rawData = window.localStorage.getItem(STORAGE_KEY);
    if (!rawData) {
      return defaultData;
    }

    return sanitizePersistedData(JSON.parse(rawData));
  } catch (error) {
    storageAvailable = false;
    storageWarning = error instanceof SyntaxError
      ? "저장 데이터를 읽지 못해 새 기록으로 시작"
      : "로컬 저장소를 사용할 수 없음";
    return defaultData;
  }
}

function createDefaultPersistedData() {
  return {
    version: STORAGE_VERSION,
    settings: { category: "embedded-c", tabSize: TAB_SIZE },
    customSnippets: [],
    history: [],
  };
}

function sanitizePersistedData(data) {
  if (!data || typeof data !== "object") {
    throw new SyntaxError("Invalid saved data");
  }

  const safeData = createDefaultPersistedData();
  safeData.settings.category = isKnownCategory(data.settings?.category)
    ? data.settings.category
    : "embedded-c";

  if (Array.isArray(data.customSnippets)) {
    safeData.customSnippets = data.customSnippets
      .filter(isValidCustomSnippet)
      .slice(0, CUSTOM_SNIPPET_LIMIT)
      .map((snippet) => ({
        id: String(snippet.id),
        category: snippet.category,
        title: String(snippet.title).slice(0, 60),
        code: normalizeCode(String(snippet.code)).slice(0, CUSTOM_CODE_LIMIT),
        fileName: typeof snippet.fileName === "string"
          ? snippet.fileName.slice(0, 80)
          : CATEGORY_META[snippet.category].fileName,
        createdAt: isValidDate(snippet.createdAt) ? snippet.createdAt : new Date().toISOString(),
      }));
  }

  if (Array.isArray(data.history)) {
    safeData.history = data.history
      .filter(isValidHistoryRecord)
      .slice(0, HISTORY_LIMIT)
      .map((record) => ({
        id: String(record.id),
        snippetId: String(record.snippetId),
        title: String(record.title).slice(0, 100),
        category: record.category,
        completedAt: record.completedAt,
        durationMs: Math.max(0, Number(record.durationMs)),
        totalChars: Math.max(0, Number(record.totalChars)),
        correctAttempts: Math.max(0, Number(record.correctAttempts)),
        incorrectAttempts: Math.max(0, Number(record.incorrectAttempts)),
        backspaceCount: Math.max(0, Number(record.backspaceCount)),
        accuracy: clamp(Number(record.accuracy), 0, 100),
        cpm: Math.max(0, Number(record.cpm)),
        wpm: Math.max(0, Number(record.wpm)),
      }));
  }

  return safeData;
}

function savePersistedData() {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(persistedData));
    storageAvailable = true;
    storageWarning = "";
  } catch {
    storageAvailable = false;
    storageWarning = "현재 세션의 변경 사항을 저장하지 못함";
  }

  updateStorageStatus();
  return storageAvailable;
}

function syncPersistedDataFromOtherTab(event) {
  if (event.key !== STORAGE_KEY) {
    return;
  }

  try {
    persistedData = event.newValue
      ? sanitizePersistedData(JSON.parse(event.newValue))
      : createDefaultPersistedData();
    storageAvailable = true;
    storageWarning = "";
    updateStorageStatus();
    renderHistory();
    renderCustomSnippetList();

    const snippets = getSnippetsForCategory(session.category);
    const currentIndex = snippets.findIndex(
      (snippet) => snippet.id === session.currentSnippet?.id,
    );
    if (currentIndex >= 0) {
      session.snippetIndex = currentIndex;
      renderSnippetHeader(snippets.length);
    }
  } catch {
    storageWarning = "다른 탭의 저장 데이터를 동기화하지 못함";
    updateStorageStatus();
  }
}

function updateStorageStatus() {
  if (storageAvailable && !storageWarning) {
    elements.storageStatus.dataset.state = "ok";
    elements.storageStatusText.textContent = "이 브라우저에 자동 저장";
    return;
  }

  elements.storageStatus.dataset.state = "warning";
  elements.storageStatusText.textContent = storageWarning || "로컬 저장소 확인 필요";
}

function isValidCustomSnippet(snippet) {
  return Boolean(
    snippet
    && typeof snippet.id === "string"
    && typeof snippet.title === "string"
    && snippet.title.trim().length > 0
    && typeof snippet.code === "string"
    && snippet.code.trim().length > 0
    && isKnownCategory(snippet.category),
  );
}

function isValidHistoryRecord(record) {
  return Boolean(
    record
    && typeof record.id === "string"
    && typeof record.snippetId === "string"
    && typeof record.title === "string"
    && isKnownCategory(record.category)
    && isValidDate(record.completedAt)
    && Number.isFinite(Number(record.durationMs))
    && Number.isFinite(Number(record.accuracy))
    && Number.isFinite(Number(record.wpm)),
  );
}

function normalizeCode(code) {
  const normalizedLines = String(code).replace(/\r\n?/g, "\n");
  let result = "";
  let column = 0;

  for (const character of Array.from(normalizedLines)) {
    if (character === "\t") {
      const spaces = TAB_SIZE - (column % TAB_SIZE);
      result += " ".repeat(spaces);
      column += spaces;
    } else {
      result += character;
      column = character === "\n" ? 0 : column + 1;
    }
  }

  return result;
}

function getSharedPrefixLength(first, second) {
  const limit = Math.min(first.length, second.length);
  let index = 0;
  while (index < limit && first[index] === second[index]) {
    index += 1;
  }
  return index;
}

function getCurrentColumn(characters) {
  const lastNewlineIndex = characters.lastIndexOf("\n");
  return characters.length - lastNewlineIndex - 1;
}

function getLineAndColumn(index) {
  let line = 1;
  let column = 1;

  for (let cursor = 0; cursor < index; cursor += 1) {
    if (session.targetChars[cursor] === "\n") {
      line += 1;
      column = 1;
    } else {
      column += 1;
    }
  }

  return `${line}행 ${column}열`;
}

function describeCharacter(character) {
  if (character === "\n") {
    return "줄바꿈(Enter)";
  }
  if (character === " ") {
    return "공백(Space)";
  }
  if (character === undefined) {
    return "없음";
  }
  return `“${character}”`;
}

function formatElapsed(milliseconds) {
  const safeMilliseconds = Math.max(0, Number(milliseconds) || 0);
  const totalTenths = Math.floor(safeMilliseconds / 100);
  const tenths = totalTenths % 10;
  const totalSeconds = Math.floor(totalTenths / 10);
  const seconds = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);

  if (hours > 0) {
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
}

function formatTotalPractice(milliseconds) {
  if (milliseconds <= 0) {
    return "0분";
  }

  const minutes = Math.floor(milliseconds / 60000);
  if (minutes < 1) {
    return "<1분";
  }
  if (minutes < 60) {
    return `${minutes}분`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}시간 ${remainingMinutes}분` : `${hours}시간`;
}

function formatCompletedAt(dateString) {
  try {
    return new Intl.DateTimeFormat("ko-KR", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(new Date(dateString));
  } catch {
    return dateString;
  }
}

function createId(prefix) {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return `${prefix}-${window.crypto.randomUUID()}`;
  }

  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function isKnownCategory(category) {
  return Object.prototype.hasOwnProperty.call(CATEGORY_META, category);
}

function isValidDate(value) {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

function roundTo(value, digits) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function announce(message) {
  elements.announcement.textContent = "";
  window.setTimeout(() => {
    elements.announcement.textContent = message;
  }, 20);
}
