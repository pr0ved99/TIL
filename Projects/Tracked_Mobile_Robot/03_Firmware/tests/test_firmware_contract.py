"""Static safety contracts shared by the STM32 and ESP32 firmware.

These tests intentionally use only the Python standard library.  They are a
source preflight check, not a replacement for firmware builds or measurements
on the target hardware.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


FIRMWARE_ROOT = Path(__file__).resolve().parent.parent
STM32_ROOT = FIRMWARE_ROOT / "stm32_uart_mvp"
ESP32_ROOT = FIRMWARE_ROOT / "esp32_uart_bridge"


def read_text(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required firmware file is missing: {path}")
    return path.read_text(encoding="utf-8")


def strip_c_comments(source: str) -> str:
    """Remove C comments while preserving quoted strings and line structure."""
    output: list[str] = []
    index = 0
    state = "normal"

    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""

        if state == "normal":
            if char == "/" and next_char == "/":
                state = "line_comment"
                output.extend((" ", " "))
                index += 2
                continue
            if char == "/" and next_char == "*":
                state = "block_comment"
                output.extend((" ", " "))
                index += 2
                continue
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
            output.append(char)
            index += 1
            continue

        if state == "line_comment":
            if char in "\r\n":
                state = "normal"
                output.append(char)
            else:
                output.append(" ")
            index += 1
            continue

        if state == "block_comment":
            if char == "*" and next_char == "/":
                output.extend((" ", " "))
                state = "normal"
                index += 2
                continue
            output.append(char if char in "\r\n" else " ")
            index += 1
            continue

        output.append(char)
        if char == "\\" and index + 1 < len(source):
            output.append(source[index + 1])
            index += 2
            continue
        if state == "string" and char == '"':
            state = "normal"
        elif state == "character" and char == "'":
            state = "normal"
        index += 1

    return "".join(output)


def compact_c(source: str) -> str:
    return re.sub(r"\s+", "", strip_c_comments(source))


def parse_ioc(source: str) -> tuple[dict[str, str], set[str]]:
    values: dict[str, str] = {}
    duplicates: set[str] = set()

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in values:
            duplicates.add(key)
        values[key] = value.strip()

    return values, duplicates


DEFINE_PATTERN = re.compile(
    r"^\s*#\s*define[ \t]+([A-Za-z_]\w*)[ \t]+([^\r\n]+?)\s*$",
    re.MULTILINE,
)


def parse_defines(source: str) -> dict[str, list[str]]:
    definitions: dict[str, list[str]] = {}
    for match in DEFINE_PATTERN.finditer(strip_c_comments(source)):
        definitions.setdefault(match.group(1), []).append(match.group(2).strip())
    return definitions


INTEGER_LITERAL_PATTERN = re.compile(
    r"^\s*\(?\s*([+-]?(?:0[xX][0-9A-Fa-f]+|\d+))\s*[uUlL]*\s*\)?\s*$"
)


def single_define(definitions: dict[str, list[str]], name: str) -> str:
    values = definitions.get(name, [])
    if len(values) != 1:
        raise AssertionError(
            f"expected exactly one definition for {name}, found {len(values)}"
        )
    return values[0]


def integer_define(definitions: dict[str, list[str]], name: str) -> int:
    raw_value = single_define(definitions, name)
    match = INTEGER_LITERAL_PATTERN.fullmatch(raw_value)
    if match is None:
        raise AssertionError(f"{name} is not a simple integer literal: {raw_value!r}")
    return int(match.group(1), 0)


def extract_function(source: str, name: str) -> str:
    """Extract a C function body with brace matching rather than line matching."""
    clean = strip_c_comments(source)
    signature = re.compile(
        rf"\b{re.escape(name)}\s*\([^;{{}}]*\)\s*\{{",
        re.MULTILINE,
    )
    matches = list(signature.finditer(clean))
    if len(matches) != 1:
        raise AssertionError(
            f"expected one definition for function {name}, found {len(matches)}"
        )

    opening = clean.find("{", matches[0].start())
    depth = 0
    state = "normal"
    index = opening

    while index < len(clean):
        char = clean[index]
        if state == "normal":
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return clean[opening + 1 : index]
        else:
            if char == "\\":
                index += 2
                continue
            if state == "string" and char == '"':
                state = "normal"
            elif state == "character" and char == "'":
                state = "normal"
        index += 1

    raise AssertionError(f"unterminated function body for {name}")


class FirmwareContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = {
            "ioc": STM32_ROOT / "stm32_uart_mvp.ioc",
            "main_h": STM32_ROOT / "Core" / "Inc" / "main.h",
            "main_c": STM32_ROOT / "Core" / "Src" / "main.c",
            "gpio_c": STM32_ROOT / "Core" / "Src" / "gpio.c",
            "tim_c": STM32_ROOT / "Core" / "Src" / "tim.c",
            "usart_c": STM32_ROOT / "Core" / "Src" / "usart.c",
            "motor_output_h": STM32_ROOT / "Core" / "Inc" / "motor_output.h",
            "motor_output_c": STM32_ROOT / "Core" / "Src" / "motor_output.c",
            "mapper_h": STM32_ROOT / "Core" / "Inc" / "drive_command_mapper.h",
            "mapper_c": STM32_ROOT / "Core" / "Src" / "drive_command_mapper.c",
            "parser_h": STM32_ROOT / "Core" / "Inc" / "uart_frame_parser.h",
            "parser_c": STM32_ROOT / "Core" / "Src" / "uart_frame_parser.c",
            "protocol_c": STM32_ROOT / "Core" / "Src" / "uart_mvp_protocol.c",
            "esp_c": ESP32_ROOT / "main" / "hello_world_main.c",
        }
        cls.source = {name: read_text(path) for name, path in cls.paths.items()}
        cls.ioc, cls.ioc_duplicates = parse_ioc(cls.source["ioc"])

    def assert_assignment(self, body: str, left: str, right: str) -> None:
        self.assertIn(
            compact_c(f"{left} = {right};"),
            compact_c(body),
            f"missing assignment: {left} = {right}",
        )

    def assert_tokens_in_order(self, body: str, *tokens: str) -> None:
        compact_body = compact_c(body)
        offset = 0
        for token in tokens:
            compact_token = compact_c(token)
            found = compact_body.find(compact_token, offset)
            self.assertNotEqual(found, -1, f"missing or out-of-order token: {token}")
            offset = found + len(compact_token)

    def test_ioc_target_and_required_initializers(self) -> None:
        self.assertFalse(self.ioc_duplicates, f"duplicate .ioc keys: {self.ioc_duplicates}")
        self.assertEqual(self.ioc["Mcu.CPN"], "STM32F446RET6")

        initializer_text = self.ioc["ProjectManager.functionlistsort"]
        initializers = set(
            re.findall(r"(?:^|,)\d+-([A-Za-z_]\w*)-", initializer_text)
        )
        required = {
            "SystemClock_Config",
            "MX_GPIO_Init",
            "MX_USART1_UART_Init",
            "MX_USART2_UART_Init",
            "MX_TIM3_Init",
            "MX_TIM4_Init",
            "MX_TIM5_Init",
        }
        self.assertTrue(
            required.issubset(initializers),
            f"missing CubeMX initializers: {sorted(required - initializers)}",
        )

    def test_ioc_pin_contract(self) -> None:
        expected = {
            "PA9.Signal": "USART1_TX",
            "PA10.Signal": "USART1_RX",
            "PB4.Signal": "S_TIM3_CH1",
            "PB5.Signal": "S_TIM3_CH2",
            "PA0-WKUP.Signal": "S_TIM5_CH1",
            "PA1.Signal": "S_TIM5_CH2",
            "PB6.Signal": "S_TIM4_CH1",
            "PB6.GPIO_Label": "MOTOR_LEFT_PWM",
            "PB7.Signal": "S_TIM4_CH2",
            "PB7.GPIO_Label": "MOTOR_RIGHT_PWM",
            "PC7.Signal": "GPIO_Input",
            "PC7.GPIO_Label": "ESTOP_SENSE",
            "PC7.GPIO_PuPd": "GPIO_PULLUP",
            "PC8.Signal": "GPIO_Output",
            "PC8.GPIO_Label": "MOTOR_LEFT_DIR",
            "PC9.Signal": "GPIO_Output",
            "PC9.GPIO_Label": "MOTOR_RIGHT_DIR",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(self.ioc.get(key), value)

    def test_ioc_timer_and_uart_contract(self) -> None:
        expected = {
            "TIM3.EncoderMode": "TIM_ENCODERMODE_TI12",
            "TIM5.EncoderMode": "TIM_ENCODERMODE_TI12",
            "TIM4.Channel-PWM\\ Generation1\\ CH1": "TIM_CHANNEL_1",
            "TIM4.Channel-PWM\\ Generation2\\ CH2": "TIM_CHANNEL_2",
            "TIM4.Period": "4420",
            "RCC.APB1TimFreq_Value": "84000000",
            "USART1.VirtualMode": "VM_ASYNC",
            "USART2.VirtualMode": "VM_ASYNC",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(self.ioc.get(key), value)

        self.assertTrue(self.ioc["NVIC.USART1_IRQn"].startswith("true\\:"))
        self.assertTrue(self.ioc["NVIC.USART2_IRQn"].startswith("true\\:"))

        timer_clock_hz = int(self.ioc["RCC.APB1TimFreq_Value"])
        period_counts = int(self.ioc["TIM4.Period"]) + 1
        self.assertEqual(timer_clock_hz // period_counts, 19_000)

    def test_generated_pin_aliases_match_contract(self) -> None:
        definitions = parse_defines(self.source["main_h"])
        expected = {
            "ESTOP_SENSE_Pin": "GPIO_PIN_7",
            "ESTOP_SENSE_GPIO_Port": "GPIOC",
            "MOTOR_LEFT_DIR_Pin": "GPIO_PIN_8",
            "MOTOR_LEFT_DIR_GPIO_Port": "GPIOC",
            "MOTOR_RIGHT_DIR_Pin": "GPIO_PIN_9",
            "MOTOR_RIGHT_DIR_GPIO_Port": "GPIOC",
            "MOTOR_LEFT_PWM_Pin": "GPIO_PIN_6",
            "MOTOR_LEFT_PWM_GPIO_Port": "GPIOB",
            "MOTOR_RIGHT_PWM_Pin": "GPIO_PIN_7",
            "MOTOR_RIGHT_PWM_GPIO_Port": "GPIOB",
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(single_define(definitions, name), value)
    def test_generated_estop_input_contract(self) -> None:
        gpio = compact_c(
            extract_function(self.source["gpio_c"], "MX_GPIO_Init")
        )
        self.assertIn(
            "GPIO_InitStruct.Pin=ESTOP_SENSE_Pin;"
            "GPIO_InitStruct.Mode=GPIO_MODE_INPUT;"
            "GPIO_InitStruct.Pull=GPIO_PULLUP;"
            "HAL_GPIO_Init(ESTOP_SENSE_GPIO_Port,&GPIO_InitStruct);",
            gpio,
        )

    def test_generated_timer_contract(self) -> None:
        tim3 = extract_function(self.source["tim_c"], "MX_TIM3_Init")
        tim4 = extract_function(self.source["tim_c"], "MX_TIM4_Init")
        tim5 = extract_function(self.source["tim_c"], "MX_TIM5_Init")

        for body, handle, period in (
            (tim3, "htim3", "65535"),
            (tim4, "htim4", "4420"),
            (tim5, "htim5", "4294967295"),
        ):
            self.assert_assignment(body, f"{handle}.Init.Prescaler", "0")
            self.assert_assignment(body, f"{handle}.Init.Period", period)

        for body in (tim3, tim5):
            self.assert_assignment(body, "sConfig.EncoderMode", "TIM_ENCODERMODE_TI12")
            self.assert_assignment(body, "sConfig.IC1Polarity", "TIM_ICPOLARITY_RISING")
            self.assert_assignment(body, "sConfig.IC2Polarity", "TIM_ICPOLARITY_RISING")
            self.assert_assignment(body, "sConfig.IC1Prescaler", "TIM_ICPSC_DIV1")
            self.assert_assignment(body, "sConfig.IC2Prescaler", "TIM_ICPSC_DIV1")

        self.assert_assignment(tim4, "sConfigOC.OCMode", "TIM_OCMODE_PWM1")
        self.assert_assignment(tim4, "sConfigOC.Pulse", "0")
        self.assert_assignment(tim4, "sConfigOC.OCPolarity", "TIM_OCPOLARITY_HIGH")
        compact_tim4 = compact_c(tim4)
        self.assertIn(
            "HAL_TIM_PWM_ConfigChannel(&htim4,&sConfigOC,TIM_CHANNEL_1)",
            compact_tim4,
        )
        self.assertIn(
            "HAL_TIM_PWM_ConfigChannel(&htim4,&sConfigOC,TIM_CHANNEL_2)",
            compact_tim4,
        )

        compact_source = compact_c(self.source["tim_c"])
        for token in (
            "GPIO_InitStruct.Pin=GPIO_PIN_4|GPIO_PIN_5;",
            "GPIO_InitStruct.Alternate=GPIO_AF2_TIM3;",
            "GPIO_InitStruct.Pin=GPIO_PIN_0|GPIO_PIN_1;",
            "GPIO_InitStruct.Alternate=GPIO_AF2_TIM5;",
            "GPIO_InitStruct.Pin=MOTOR_LEFT_PWM_Pin|MOTOR_RIGHT_PWM_Pin;",
            "GPIO_InitStruct.Alternate=GPIO_AF2_TIM4;",
        ):
            self.assertIn(token, compact_source)

    def test_drive_command_mapper_source_contract(self) -> None:
        definitions = parse_defines(self.source["mapper_c"])
        expected = {
            "DRIVE_COMMAND_NORMALIZED_SCALE": 1000,
            "DRIVE_COMMAND_VX_MIN_MMPS": -100,
            "DRIVE_COMMAND_VX_MAX_MMPS": 100,
            "DRIVE_COMMAND_W_MIN_MRADPS": -500,
            "DRIVE_COMMAND_W_MAX_MRADPS": 500,
            "DRIVE_COMMAND_MAX_DUTY_PERMILLE": 100,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(integer_define(definitions, name), value)

        compact_header = compact_c(self.source["mapper_h"])
        self.assertIn(
            "typedefstruct{"
            "int16_tleft_signed_permille;"
            "int16_tright_signed_permille;"
            "}drive_command_request_t;",
            compact_header,
        )
        self.assertIn(
            "booldrive_command_map("
            "int32_tvx_mmps,"
            "int32_tw_mradps,"
            "uint16_tduty_cap_permille,"
            "drive_command_request_t*request"
            ");",
            compact_header,
        )

        mapper_source = strip_c_comments(
            self.source["mapper_h"] + "\n" + self.source["mapper_c"]
        )
        self.assertIsNone(
            re.search(r"\b(?:HAL_|GPIO_|TIM_)", mapper_source),
            "pure mapper must not depend on HAL, GPIO or timer symbols",
        )

        body = extract_function(self.source["mapper_c"], "drive_command_map")
        compact_body = compact_c(body)
        range_guard = (
            "if(vx_mmps < DRIVE_COMMAND_VX_MIN_MMPS || "
            "vx_mmps > DRIVE_COMMAND_VX_MAX_MMPS || "
            "w_mradps < DRIVE_COMMAND_W_MIN_MRADPS || "
            "w_mradps > DRIVE_COMMAND_W_MAX_MRADPS || "
            "duty_cap_permille > DRIVE_COMMAND_MAX_DUTY_PERMILLE) "
            "{ return false; }"
        )
        self.assertIn(
            compact_c(range_guard),
            compact_body,
        )
        self.assert_tokens_in_order(
            body,
            "if(request == NULL) { return false; }",
            "request->left_signed_permille = 0;",
            "request->right_signed_permille = 0;",
            range_guard,
            "linear = (vx_mmps * DRIVE_COMMAND_NORMALIZED_SCALE) / DRIVE_COMMAND_VX_MAX_MMPS;",
            "yaw = (w_mradps * DRIVE_COMMAND_NORMALIZED_SCALE) / DRIVE_COMMAND_W_MAX_MRADPS;",
            "raw_left = linear - yaw;",
            "raw_right = linear + yaw;",
            "left_abs = (raw_left < 0) ? -raw_left : raw_left;",
            "right_abs = (raw_right < 0) ? -raw_right : raw_right;",
            "peak = DRIVE_COMMAND_NORMALIZED_SCALE;",
            "if(left_abs > peak)",
            "peak = left_abs;",
            "if(right_abs > peak)",
            "peak = right_abs;",
            "request->left_signed_permille =",
            "request->right_signed_permille =",
            "return true;",
        )

    def test_generated_uart_contract(self) -> None:
        for number in (1, 2):
            body = extract_function(self.source["usart_c"], f"MX_USART{number}_UART_Init")
            handle = f"huart{number}"
            expected = {
                f"{handle}.Instance": f"USART{number}",
                f"{handle}.Init.BaudRate": "115200",
                f"{handle}.Init.WordLength": "UART_WORDLENGTH_8B",
                f"{handle}.Init.StopBits": "UART_STOPBITS_1",
                f"{handle}.Init.Parity": "UART_PARITY_NONE",
                f"{handle}.Init.Mode": "UART_MODE_TX_RX",
                f"{handle}.Init.HwFlowCtl": "UART_HWCONTROL_NONE",
            }
            for left, right in expected.items():
                with self.subTest(usart=number, field=left):
                    self.assert_assignment(body, left, right)

        compact_source = compact_c(self.source["usart_c"])
        for token in (
            "GPIO_InitStruct.Pin=GPIO_PIN_9|GPIO_PIN_10;",
            "GPIO_InitStruct.Alternate=GPIO_AF7_USART1;",
            "GPIO_InitStruct.Alternate=GPIO_AF7_USART2;",
        ):
            self.assertIn(token, compact_source)

    def test_all_bench_hooks_are_present_and_disabled(self) -> None:
        source_names = ("main_c", "protocol_c", "esp_c")
        hooks: dict[str, int] = {}

        for source_name in source_names:
            definitions = parse_defines(self.source[source_name])
            for name in definitions:
                if not name.endswith("_TEST_ENABLED"):
                    continue
                self.assertNotIn(name, hooks, f"duplicate test hook: {name}")
                hooks[name] = integer_define(definitions, name)

        required = {
            "MOTOR_OUTPUT_PIN_TEST_ENABLED",
            "MOTOR_FAULT_INJECTION_TEST_ENABLED",
            "UART_MVP_OUTPUT_TEST_ENABLED",
            "UART_MVP_WRONG_DISARM_ACK_TYPE_ONCE_TEST_ENABLED",
            "BRIDGE_SCRIPTED_TEST_ENABLED",
        }
        self.assertTrue(
            required.issubset(hooks),
            f"missing test-hook guards: {sorted(required - hooks.keys())}",
        )
        for name, value in hooks.items():
            with self.subTest(name=name):
                self.assertEqual(value, 0, f"bench-only hook must be disabled: {name}")

    def test_boot_outputs_start_in_safe_state(self) -> None:
        gpio = extract_function(self.source["gpio_c"], "MX_GPIO_Init")
        compact_gpio = compact_c(gpio)
        reset = (
            "HAL_GPIO_WritePin(GPIOC,MOTOR_LEFT_DIR_Pin|"
            "MOTOR_RIGHT_DIR_Pin,GPIO_PIN_RESET);"
        )
        configure = "HAL_GPIO_Init(GPIOC,&GPIO_InitStruct);"
        self.assertIn(reset, compact_gpio)
        self.assertIn(configure, compact_gpio)
        self.assertLess(compact_gpio.index(reset), compact_gpio.index(configure))

        main = extract_function(self.source["main_c"], "main")
        compact_main = compact_c(main)
        for initializer in (
            "MX_GPIO_Init();",
            "MX_TIM3_Init();",
            "MX_TIM4_Init();",
            "MX_TIM5_Init();",
        ):
            self.assertIn(initializer, compact_main)
            self.assertLess(
                compact_main.index(initializer),
                compact_main.index("motor_output_init(&htim4)"),
            )

        motor_init = extract_function(self.source["motor_output_c"], "motor_output_init")
        self.assert_tokens_in_order(
            motor_init,
            "motor_output_stop_all();",
            "HAL_TIM_PWM_Start(motor_timer, TIM_CHANNEL_1);",
            "HAL_TIM_PWM_Start(motor_timer, TIM_CHANNEL_2);",
        )

    def test_encoder_initialization_and_vehicle_sign_contract(self) -> None:
        definitions = parse_defines(self.source["main_c"])
        self.assertEqual(integer_define(definitions, "ENCODER_COUNTS_PER_OUTPUT_REV"), 1560)
        self.assertEqual(integer_define(definitions, "ENCODER_SPEED_SAMPLE_PERIOD_MS"), 100)

        main = extract_function(self.source["main_c"], "main")
        compact_main = compact_c(main)
        for token in (
            "__HAL_TIM_SET_COUNTER(&htim3,32768U);",
            "__HAL_TIM_SET_COUNTER(&htim5,0x80000000U);",
            "HAL_TIM_Encoder_Start(&htim3,TIM_CHANNEL_ALL)",
            "HAL_TIM_Encoder_Start(&htim5,TIM_CHANNEL_ALL)",
            "&s_encoder_tim3,ENCODER_COUNTER_WIDTH_16",
            "&s_encoder_tim5,ENCODER_COUNTER_WIDTH_32",
        ):
            self.assertIn(token, compact_main)

        log_process = extract_function(
            self.source["main_c"], "encoder_speed_log_process"
        )
        expected_mapping = (
            "uart_mvp_set_encoder_cps("
            "encoder_cps_to_i32(-s_encoder_tim3.counts_per_second),"
            "encoder_cps_to_i32(s_encoder_tim5.counts_per_second));"
        )
        self.assertIn(expected_mapping, compact_c(log_process))

    def test_motor_output_limits_and_fail_safe_order(self) -> None:
        definitions = parse_defines(self.source["motor_output_c"])
        expected = {
            "MOTOR_OUTPUT_DUTY_SCALE_PERMILLE": 1000,
            "MOTOR_OUTPUT_MAX_DUTY_PERMILLE": 100,
            "MOTOR_OUTPUT_PWM_ZERO_SETTLE_MS": 1,
            "MOTOR_OUTPUT_DIR_SETTLE_MS": 1,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(integer_define(definitions, name), value)

        stop = extract_function(self.source["motor_output_c"], "motor_output_stop_all")
        compact_stop = compact_c(stop)
        for token in (
            "__HAL_TIM_SET_COMPARE(motor_timer,TIM_CHANNEL_1,0U);",
            "__HAL_TIM_SET_COMPARE(motor_timer,TIM_CHANNEL_2,0U);",
            "HAL_GPIO_WritePin(MOTOR_LEFT_DIR_GPIO_Port,MOTOR_LEFT_DIR_Pin,GPIO_PIN_RESET);",
            "HAL_GPIO_WritePin(MOTOR_RIGHT_DIR_GPIO_Port,MOTOR_RIGHT_DIR_Pin,GPIO_PIN_RESET);",
        ):
            self.assertIn(token, compact_stop)

        set_raw = extract_function(self.source["motor_output_c"], "motor_output_set_raw")
        compact_set = compact_c(set_raw)
        self.assertGreaterEqual(compact_set.count("motor_output_stop_all();"), 2)
        self.assert_tokens_in_order(
            set_raw,
            "__HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_1, 0U);",
            "__HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_2, 0U);",
            "HAL_Delay(MOTOR_OUTPUT_PWM_ZERO_SETTLE_MS);",
            "HAL_GPIO_WritePin(MOTOR_LEFT_DIR_GPIO_Port, MOTOR_LEFT_DIR_Pin, left_dir_level);",
            "HAL_GPIO_WritePin(MOTOR_RIGHT_DIR_GPIO_Port, MOTOR_RIGHT_DIR_Pin, right_dir_level);",
            "HAL_Delay(MOTOR_OUTPUT_DIR_SETTLE_MS);",
            "__HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_1, left_compare);",
            "__HAL_TIM_SET_COMPARE(motor_timer, TIM_CHANNEL_2, right_compare);",
        )

        motor_init = extract_function(self.source["motor_output_c"], "motor_output_init")
        compact_init = compact_c(motor_init)
        self.assertIn("htim->Instance!=TIM4", compact_init)

        error_handler = extract_function(self.source["main_c"], "Error_Handler")
        self.assert_tokens_in_order(
            error_handler,
            "motor_output_stop_all();",
            "__disable_irq();",
            "while (1)",
        )

    def test_applied_output_telemetry_contract(self) -> None:
        header = compact_c(self.source["motor_output_h"])

        self.assertIn(
            "typedefstruct{" \
            "int16_tleft_signed_permille;" \
            "int16_tright_signed_permille;" \
            "}motor_output_applied_t;",
            header,
        )
        self.assertIn(
            "motor_output_applied_tmotor_output_get_applied(void);",
            header,
        )

        stop = extract_function(
            self.source["motor_output_c"],
            "motor_output_stop_all",
        )
        self.assert_tokens_in_order(
            stop,
            "motor_left_duty_permille = 0U;",
            "motor_right_duty_permille = 0U;",
        )

        getter = extract_function(
            self.source["motor_output_c"],
            "motor_output_get_applied",
        )
        self.assert_tokens_in_order(
            getter,
            "motor_output_applied_t applied = {0};",
            "if(motor_left_duty_permille != 0U)",
            "MOTOR_OUTPUT_LEFT_REVERSE_DIR_LEVEL",
            "if(motor_right_duty_permille != 0U)",
            "MOTOR_OUTPUT_RIGHT_REVERSE_DIR_LEVEL",
            "return applied",
        )

        send_tel = extract_function(
            self.source["protocol_c"],
            "send_tel",
        )
        compact_tel = compact_c(send_tel)

        self.assertNotIn(
            '"left_pwm=0,right_pwm=0,"',
            compact_tel,
        )
        self.assert_tokens_in_order(
            send_tel,
            "motor_output_applied_t applied =",
            "motor_output_get_applied();",
            '"left_pwm=%ld,right_pwm=%ld,"',
            "(long)applied.left_signed_permille",
            "(long)applied.right_signed_permille",
        )

        esp_source = self.source["esp_c"]
        self.assert_tokens_in_order(
            esp_source,
            "int32_t left_pwm;",
            "int32_t right_pwm;",
            'parse_i32_field(line, "left_pwm=", &parsed.left_pwm)',
            'parse_i32_field(line, "right_pwm=", &parsed.right_pwm)',
            '" left_pwm=%" PRIi32',
            '" right_pwm=%" PRIi32',
            "s_telemetry.left_pwm",
            "s_telemetry.right_pwm",
        )

    def test_signed_motor_output_adapter_contract(self) -> None:
        header = compact_c(self.source["motor_output_h"])
        self.assertIn(
            "HAL_StatusTypeDefmotor_output_set_signed("
            "int16_tleft_signed_permille,"
            "int16_tright_signed_permille);",
            header,
        )

        definitions = parse_defines(self.source["motor_output_c"])
        expected_levels = {
            "MOTOR_OUTPUT_LEFT_FORWARD_DIR_LEVEL": "GPIO_PIN_RESET",
            "MOTOR_OUTPUT_LEFT_REVERSE_DIR_LEVEL": "GPIO_PIN_SET",
            "MOTOR_OUTPUT_RIGHT_FORWARD_DIR_LEVEL": "GPIO_PIN_RESET",
            "MOTOR_OUTPUT_RIGHT_REVERSE_DIR_LEVEL": "GPIO_PIN_SET",
        }
        for name, value in expected_levels.items():
            with self.subTest(name=name):
                self.assertEqual(single_define(definitions, name), value)

        body = extract_function(
            self.source["motor_output_c"],
            "motor_output_set_signed",
        )
        compact_body = compact_c(body)
        self.assertEqual(compact_body.count("motor_output_set_raw("), 1)

        self.assertIn(
            compact_c(
                "status = motor_output_set_raw("
                "left_duty_permille,"
                "left_dir_level,"
                "right_duty_permille,"
                "right_dir_level"
                ");"
            ),
            compact_body,
        )

        self.assertGreaterEqual(
            compact_body.count("motor_output_stop_all();"),
            2,
        )
        self.assert_tokens_in_order(
            body,
            "left_signed_permille < -(int32_t)MOTOR_OUTPUT_MAX_DUTY_PERMILLE",
            "left_signed_permille > (int32_t)MOTOR_OUTPUT_MAX_DUTY_PERMILLE",
            "right_signed_permille < -(int32_t)MOTOR_OUTPUT_MAX_DUTY_PERMILLE",
            "right_signed_permille > (int32_t)MOTOR_OUTPUT_MAX_DUTY_PERMILLE",
            "motor_output_stop_all();",
            "return HAL_ERROR;",
            "if (left_signed_permille < 0)",
            "left_duty_permille = (uint16_t)(-left_signed_permille);",
            "left_dir_level = MOTOR_OUTPUT_LEFT_REVERSE_DIR_LEVEL;",
            "left_duty_permille = (uint16_t)left_signed_permille;",
            "left_dir_level = MOTOR_OUTPUT_LEFT_FORWARD_DIR_LEVEL;",
            "if (right_signed_permille < 0)",
            "right_duty_permille = (uint16_t)(-right_signed_permille);",
            "right_dir_level = MOTOR_OUTPUT_RIGHT_REVERSE_DIR_LEVEL;",
            "right_duty_permille = (uint16_t)right_signed_permille;",
            "right_dir_level = MOTOR_OUTPUT_RIGHT_FORWARD_DIR_LEVEL;",
            "status = motor_output_set_raw(",
            "if (status != HAL_OK)",
            "motor_output_stop_all();",
            "return status;",
        )

    def test_production_cmd_output_integration_contract(self) -> None:
        protocol_source = self.source["protocol_c"]
        compact_protocol = compact_c(protocol_source)

        self.assertEqual(
            compact_protocol.count('#include"drive_command_mapper.h"'),
            1,
        )

        definitions = parse_defines(protocol_source)
        self.assertEqual(
            integer_define(
                definitions,
                "CMD_OUTPUT_DUTY_CAP_PERMILLE",
            ),
            100,
        )

        body = extract_function(protocol_source, "handle_cmd")
        compact_body = compact_c(body)

        self.assertIn(
            "drive_command_request_trequest;",
            compact_body,
        )
        self.assertEqual(compact_body.count("drive_command_map("), 1)
        self.assertEqual(
            compact_body.count("motor_output_set_signed("),
            1,
        )
        mapper_failure = compact_c(
            "if(!drive_command_map("
            "frame->vx_mmps,"
            "frame->w_mradps,"
            "CMD_OUTPUT_DUTY_CAP_PERMILLE,"
            "&request"
            ")){"
            "motor_output_stop_all();"
            "s_vx_mmps = 0;"
            "s_w_mradps = 0;"
            'send_err(frame->seq, "CMD", "MAPPER_FAILED");'
            "return;"
            "}"
        )
        self.assertIn(mapper_failure, compact_body)
        output_failure = (
            "motor_output_stop_all();"
            "s_vx_mmps = 0;"
            "s_w_mradps = 0;"
            'send_err(frame->seq, "CMD", "MOTOR_OUTPUT_FAILED");'
            "return;"
        )

        production_output = compact_c(
            "else if(motor_output_set_signed("
            "request.left_signed_permille,"
            "request.right_signed_permille"
            ") != HAL_OK){"
            + output_failure
            + "}"
        )
        self.assertIn(production_output, compact_body)

        controlled_output_failure = compact_c(
            "if(motor_output_set_raw("
            "UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,"
            "GPIO_PIN_RESET,"
            "UART_MVP_OUTPUT_TEST_DUTY_PERMILLE,"
            "GPIO_PIN_RESET"
            ") != HAL_OK){"
            + output_failure
            + "}"
        )
        self.assertIn(controlled_output_failure, compact_body)

        estop_guard = compact_c(
            "if(estop_enforce_latch() != 0U){"
            'send_err(frame->seq, "CMD", "ESTOP_LATCHED");'
            "return;"
            "}"
        )
        self.assertEqual(compact_body.count(estop_guard), 3)

        success_tokens = (
            "s_last_seq = frame->seq;",
            "s_vx_mmps = frame->vx_mmps;",
            "s_w_mradps = frame->w_mradps;",
            "s_cmd_timeout_ms = frame->timeout_ms;",
            "s_last_cmd_ms = HAL_GetTick();",
            'send_ack(frame->seq, "CMD");',
        )

        for token in success_tokens:
            self.assertEqual(
                compact_body.count(compact_c(token)),
                1,
            )

        success_commit = compact_c(
            estop_guard + "".join(success_tokens)
        )
        self.assertIn(success_commit, compact_body)

        self.assert_tokens_in_order(
            body,
            "if(frame->vx_mmps < VX_MIN_MMPS",
            "if(frame->timeout_ms < CMD_TIMEOUT_MIN_MS",
            "if(s_state != ROBOT_ARMED)",
            estop_guard,
            mapper_failure,
            estop_guard,
            "if(UART_MVP_OUTPUT_TEST_ENABLED != 0U)",
            controlled_output_failure,
            production_output,
            success_commit,
        )

    def test_estop_reset_parser_contract(self) -> None:
        parser_header = compact_c(self.source["parser_h"])
        self.assertIn(
            "UART_FRAME_TYPE_CMD,UART_FRAME_TYPE_ESTOP_RESET",
            parser_header,
        )

        parse_type = compact_c(
            extract_function(self.source["parser_c"], "parse_type")
        )
        self.assertIn(
            'if(token_equals(line,token_len,"ESTOP_RESET"))'
            "{returnUART_FRAME_TYPE_ESTOP_RESET;}",
            parse_type,
        )

        type_name = compact_c(
            extract_function(self.source["parser_c"], "uart_frame_type_name")
        )
        self.assertIn(
            'caseUART_FRAME_TYPE_ESTOP_RESET:return"ESTOP_RESET";',
            type_name,
        )

    def test_estop_latch_forces_safe_state(self) -> None:
        force_safe = extract_function(
            self.source["protocol_c"], "estop_latch_and_force_safe"
        )
        self.assert_tokens_in_order(
            force_safe,
            "motor_output_stop_all();",
            "s_vx_mmps = 0;",
            "s_w_mradps = 0;",
            "s_estop_latched = 1U;",
            "s_state = ROBOT_FAULT;",
        )

        enforce_latch_contract = compact_c(
            "static uint8_t estop_enforce_latch(void) {"
            "if ((estop_input_active() != 0U) ||"
            "(s_estop_latched != 0U)) {"
            "estop_latch_and_force_safe();"
            "return 1U;"
            "}"
            "return 0U;"
            "}"
        )
        self.assertIn(
            enforce_latch_contract,
            compact_c(self.source["protocol_c"]),
        )

    def test_estop_blocks_arm_and_cmd_contract(self) -> None:
        handle_line = compact_c(
            extract_function(self.source["protocol_c"], "handle_line")
        )
        arm_cmd_guard = compact_c(
            "if (((frame.type == UART_FRAME_TYPE_ARM) ||"
            "(frame.type == UART_FRAME_TYPE_CMD)) &&"
            "(estop_enforce_latch() != 0U)) {"
            "send_err("
            "frame.seq,"
            "uart_frame_type_name(frame.type),"
            '"ESTOP_LATCHED"'
            ");"
            "return;"
            "}"
        )

        self.assertIn(arm_cmd_guard, handle_line)
        self.assertLess(
            handle_line.index(arm_cmd_guard),
            handle_line.index("switch(frame.type){"),
        )

    def test_estop_disarm_reset_and_polling_contract(self) -> None:
        protocol_source = self.source["protocol_c"]
        compact_protocol = compact_c(protocol_source)

        input_high_contract = compact_c(
            "static uint8_t estop_input_active(void) {"
            "return (HAL_GPIO_ReadPin("
            "ESTOP_SENSE_GPIO_Port,"
            "ESTOP_SENSE_Pin"
            ") == GPIO_PIN_SET) ? 1U : 0U;"
            "}"
        )
        self.assertIn(input_high_contract, compact_protocol)

        handle_line = compact_c(
            extract_function(protocol_source, "handle_line")
        )

        disarm_start = handle_line.index(
            "caseUART_FRAME_TYPE_DISARM:"
        )
        disarm_end = handle_line.index(
            "caseUART_FRAME_TYPE_ARM:",
            disarm_start,
        )
        disarm_case = handle_line[disarm_start:disarm_end]

        self.assertIn(
            compact_c(
                "if (estop_enforce_latch() == 0U) {"
                "s_state = ROBOT_DISARMED;"
                "}"
            ),
            disarm_case,
        )
        self.assertNotIn("s_estop_latched=0U;", disarm_case)

        reset_start = handle_line.index(
            "caseUART_FRAME_TYPE_ESTOP_RESET:"
        )
        reset_end = handle_line.index(
            "caseUART_FRAME_TYPE_CMD:",
            reset_start,
        )
        reset_case = handle_line[reset_start:reset_end]

        active_reject = compact_c(
            "if (estop_input_active() != 0U) {"
            "estop_latch_and_force_safe();"
            'send_err(frame.seq, "ESTOP_RESET", "ESTOP_ACTIVE");'
            "return;"
            "}"
        )
        clear_to_disarmed = compact_c(
            "s_estop_latched = 0U;"
            "s_state = ROBOT_DISARMED;"
            "s_last_seq = frame.seq;"
            'send_ack(frame.seq, "ESTOP_RESET");'
            "return;"
        )

        self.assertIn(active_reject, reset_case)
        self.assertIn(clear_to_disarmed, reset_case)
        self.assertLess(
            reset_case.index(active_reject),
            reset_case.index(clear_to_disarmed),
        )

        protocol_init = compact_c(
            extract_function(protocol_source, "uart_mvp_init")
        )
        clear_latch = "s_estop_latched=0U;"
        enforce_latch = "(void)estop_enforce_latch();"
        self.assertIn(clear_latch, protocol_init)
        self.assertIn(enforce_latch, protocol_init)
        self.assertLess(
            protocol_init.index(clear_latch),
            protocol_init.index(enforce_latch),
        )

        process = compact_c(
            extract_function(protocol_source, "uart_mvp_process")
        )
        self.assertIn(
            "for(;;){(void)estop_enforce_latch();",
            process,
        )

    def test_protocol_limits_and_stop_paths(self) -> None:
        definitions = parse_defines(self.source["protocol_c"])
        expected = {
            "CMD_TIMEOUT_DEFAULT_MS": 300,
            "CMD_TIMEOUT_MIN_MS": 50,
            "CMD_TIMEOUT_MAX_MS": 500,
            "VX_MIN_MMPS": -100,
            "VX_MAX_MMPS": 100,
            "W_MIN_MRADPS": -500,
            "W_MAX_MRADPS": 500,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(integer_define(definitions, name), value)

        handle_cmd = compact_c(
            extract_function(self.source["protocol_c"], "handle_cmd")
        )
        not_armed = "if(s_state!=ROBOT_ARMED){"
        output_hook = "if(UART_MVP_OUTPUT_TEST_ENABLED!=0U){"
        self.assertIn(not_armed, handle_cmd)
        self.assertIn(output_hook, handle_cmd)
        self.assertLess(handle_cmd.index(not_armed), handle_cmd.index(output_hook))

        handle_line = compact_c(
            extract_function(self.source["protocol_c"], "handle_line")
        )
        self.assertIn(
            "parse_result=uart_frame_parse(line,line_len,&frame);",
            handle_line,
        )
        self.assertIn(
            "if(parse_result!=UART_FRAME_PARSE_OK){"
            "send_err(frame.seq,uart_frame_type_name(frame.type),"
            "parse_error_code(parse_result));return;}",
            handle_line,
        )

        disarm_case_start = handle_line.index("caseUART_FRAME_TYPE_DISARM:")
        disarm_case_end = handle_line.index(
            "caseUART_FRAME_TYPE_ARM:", disarm_case_start
        )
        disarm_case = handle_line[disarm_case_start:disarm_case_end]

        self.assert_tokens_in_order(
            disarm_case,
            "case UART_FRAME_TYPE_DISARM:",
            "motor_output_stop_all();",
            "s_vx_mmps = 0;",
            "s_w_mradps = 0;",
            "s_state = ROBOT_DISARMED;",
            "s_last_seq = frame.seq;",
            "if(s_wrong_disarm_ack_type_sent == 0u)",
            "s_wrong_disarm_ack_type_sent = 1u;",
            'send_ack(frame.seq, "ARM");',
            "return;",
            'send_ack(frame.seq, "DISARM");',
            "return;",
        )

        self.assertIn(
            "caseUART_FRAME_TYPE_ARM:motor_output_stop_all();"
            "s_vx_mmps=0;s_w_mradps=0;"
            "s_cmd_timeout_ms=CMD_TIMEOUT_DEFAULT_MS;"
            "s_last_cmd_ms=HAL_GetTick();"
            "s_state=ROBOT_ARMED;s_last_seq=frame.seq;"
            "send_ack(frame.seq,\"ARM\");return;",
            handle_line,
        )

        protocol_source = self.source["protocol_c"]
        parser_source = self.source["parser_c"]
        for forbidden in ("strtol", "strtoul", "strstr", "strncmp", "sscanf"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, protocol_source)
                self.assertNotIn(forbidden, parser_source)

        compact_parser = compact_c(parser_source)
        parser_literals = (
            'consume_literal(&cursor,",seq=")',
            'consume_literal(&cursor,",vx_mmps=")',
            'consume_literal(&cursor,",w_mradps=")',
            'consume_literal(&cursor,",timeout_ms=")',
        )
        parser_offsets = [compact_parser.index(token) for token in parser_literals]
        self.assertEqual(parser_offsets, sorted(parser_offsets))
        for token in (
            "parsed>(UINT32_MAX-digit)/10u",
            "limit=2147483648u",
            "if(magnitude==2147483648u)",
            "if(cursor.position!=cursor.length){"
            "returnUART_FRAME_PARSE_EXTRA_DATA;}",
        ):
            self.assertIn(token, compact_parser)

        compact_protocol = compact_c(protocol_source)
        self.assertIn("staticuint32_ts_last_seq;", compact_protocol)

        process = compact_c(
            extract_function(self.source["protocol_c"], "uart_mvp_process")
        )
        self.assertIn(
            "if(s_line_len>0u&&s_line[s_line_len-1u]=='\\r'){s_line_len--;}",
            process,
        )
        self.assertNotIn("if(byte=='\\r'){continue;}", process)
        self.assertIn(
            "for(;;){(void)estop_enforce_latch();"
            "command_timeout_enforce();",
            process,
        )

        protocol_init = compact_c(
            extract_function(self.source["protocol_c"], "uart_mvp_init")
        )
        self.assertIn("s_state=ROBOT_DISARMED;", protocol_init)
        self.assertIn(
            "s_wrong_disarm_ack_type_sent=0u;",
            protocol_init,
        )
        self.assertIn("s_cmd_timeout_ms=CMD_TIMEOUT_DEFAULT_MS;", protocol_init)

    def test_command_timeout_forces_disarmed_contract(self) -> None:
        timeout_body = extract_function(
            self.source["protocol_c"],
            "command_timeout_enforce",
        )
        compact_timeout = compact_c(timeout_body)

        self.assert_tokens_in_order(
            timeout_body,
            "if(s_state != ROBOT_ARMED)",
            "return;",
            "if((HAL_GetTick() - s_last_cmd_ms) < s_cmd_timeout_ms)",
            "return;",
            "motor_output_stop_all();",
            "s_vx_mmps = 0;",
            "s_w_mradps = 0;",
            "s_state = ROBOT_DISARMED;",
        )

        for forbidden in (
            "send_err(",
            "send_ack(",
            "s_error_count",
            "s_last_seq",
        ):
            self.assertNotIn(
                compact_c(forbidden),
                compact_timeout,
            )

    def test_esp32_uart_and_script_guard_contract(self) -> None:
        definitions = parse_defines(self.source["esp_c"])
        expected_defines = {
            "BRIDGE_UART_NUM": "UART_NUM_1",
            "BRIDGE_UART_TX_GPIO": "GPIO_NUM_17",
            "BRIDGE_UART_RX_GPIO": "GPIO_NUM_18",
        }
        for name, value in expected_defines.items():
            with self.subTest(name=name):
                self.assertEqual(single_define(definitions, name), value)
        self.assertEqual(integer_define(definitions, "BRIDGE_UART_BAUD"), 115200)
        self.assertEqual(integer_define(definitions, "BRIDGE_SCRIPTED_TEST_ENABLED"), 0)

        expected_startup_defines = {
            "STARTUP_SETTLE_MS": 500,
            "STARTUP_SYNC_WAIT_MS": 100,
            "STARTUP_RESPONSE_TIMEOUT_MS": 500,
            "STARTUP_MAX_ATTEMPTS": 3,
        }
        for name, value in expected_startup_defines.items():
            with self.subTest(name=name):
                self.assertEqual(integer_define(definitions, name), value)

        init = compact_c(extract_function(self.source["esp_c"], "bridge_uart_init"))
        for token in (
            ".baud_rate=BRIDGE_UART_BAUD,",
            ".data_bits=UART_DATA_8_BITS,",
            ".parity=UART_PARITY_DISABLE,",
            ".stop_bits=UART_STOP_BITS_1,",
            ".flow_ctrl=UART_HW_FLOWCTRL_DISABLE,",
            "uart_param_config(BRIDGE_UART_NUM,&uart_config)",
            "uart_set_pin(BRIDGE_UART_NUM,BRIDGE_UART_TX_GPIO,"
            "BRIDGE_UART_RX_GPIO,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE)",
        ):
            self.assertIn(token, init)

        rx_handler = compact_c(
            extract_function(self.source["esp_c"], "bridge_uart_handle_rx_line")
        )
        for token in (
            'if(strncmp(line,"PONG,",5)==0)',
            "s_last_pong_seq=seq;",
            "s_last_pong_valid=true;",
            "s_startup_state==BRIDGE_STARTUP_WAIT_PONG",
            "seq==s_startup_ping_seq",
            'if(strncmp(line,"TEL,",4)==0)',
            'if(strncmp(line,"ACK,",4)==0)',
            'parse_u32_field(line,"seq=",&seq)',
            'parse_string_field(line,"type=",type,sizeof(type))',
            "s_last_ack_seq=seq;",
            'snprintf(s_last_ack_type,sizeof(s_last_ack_type),"%s",type);',
            "s_last_ack_valid=true;",
            "s_startup_state==BRIDGE_STARTUP_WAIT_DISARM_ACK",
            "seq==s_startup_disarm_seq",
            'strcmp(type,"DISARM")==0',
            'if(strncmp(line,"ERR,",4)==0)',
        ):
            self.assertIn(token, rx_handler)

        startup = compact_c(
            extract_function(self.source["esp_c"], "bridge_uart_startup_step")
        )
        for token in (
            "caseBRIDGE_STARTUP_SETTLE:",
            "pdMS_TO_TICKS(STARTUP_SETTLE_MS)",
            'uart_write_bytes(BRIDGE_UART_NUM,"\\n",1)',
            "caseBRIDGE_STARTUP_SYNC_WAIT:",
            "pdMS_TO_TICKS(STARTUP_SYNC_WAIT_MS)",
            "uart_flush_input(BRIDGE_UART_NUM)",
            "if(!bridge_uart_send_disarm(s_startup_disarm_seq))",
            "caseBRIDGE_STARTUP_WAIT_DISARM_ACK:",
            "s_last_ack_seq==s_startup_disarm_seq",
            'strcmp(s_last_ack_type,"DISARM")==0',
            "if(!bridge_uart_send_ping(s_startup_ping_seq))",
            "caseBRIDGE_STARTUP_WAIT_PONG:",
            "s_last_pong_seq==s_startup_ping_seq",
            "s_startup_attempt_count<STARTUP_MAX_ATTEMPTS",
            "s_startup_state=BRIDGE_STARTUP_READY;",
            "s_startup_state=BRIDGE_STARTUP_FAILED;",
        ):
            self.assertIn(token, startup)
        self.assertIn(
            "if(s_last_ack_valid&&"
            "s_last_ack_seq==s_startup_disarm_seq&&"
            'strcmp(s_last_ack_type,"DISARM")==0)',
            startup,
        )
        self.assertIn(
            "if(s_last_pong_valid&&s_last_pong_seq==s_startup_ping_seq)",
            startup,
        )
        self.assertEqual(
            startup.count("pdMS_TO_TICKS(STARTUP_RESPONSE_TIMEOUT_MS)"),
            2,
        )
        self.assertEqual(
            startup.count("if(s_startup_attempt_count<STARTUP_MAX_ATTEMPTS)"),
            2,
        )
        self.assertEqual(startup.count("s_startup_attempt_count++;"), 2)
        self.assertEqual(
            startup.count("bridge_uart_send_disarm(s_startup_disarm_seq)"),
            2,
        )
        self.assertEqual(
            startup.count("bridge_uart_send_ping(s_startup_ping_seq)"),
            2,
        )
        self.assertGreaterEqual(
            startup.count("s_startup_state=BRIDGE_STARTUP_FAILED;"),
            6,
        )
        self.assertEqual(
            startup.count("s_startup_state=BRIDGE_STARTUP_READY;"),
            1,
        )
        self.assertNotIn("bridge_uart_send_arm(", startup)
        self.assertNotIn("bridge_uart_send_cmd(", startup)
        self.assertNotIn("bridge_uart_run_test_step(", startup)

        app_main = compact_c(extract_function(self.source["esp_c"], "app_main"))
        for token in (
            "s_startup_disarm_seq=esp_random();",
            "s_startup_ping_seq=s_startup_disarm_seq+1U;",
            "uint32_ttest_seq=s_startup_ping_seq+1U;",
            "s_startup_state=BRIDGE_STARTUP_SETTLE;",
            "s_startup_state_tick=xTaskGetTickCount();",
            "s_startup_attempt_count=0U;",
            "boolstartup_ready_seen=false;",
            "startup_ready_seen=true;",
            "last_test_tick=now;",
        ):
            self.assertIn(token, app_main)
        self.assertEqual(app_main.count("bridge_uart_startup_step(now);"), 1)
        self.assertIn(
            "if(BRIDGE_SCRIPTED_TEST_ENABLED!=0U&&"
            "s_startup_state==BRIDGE_STARTUP_READY&&"
            "test_step!=BRIDGE_TEST_DONE&&",
            app_main,
        )
        self.assertNotIn("vTaskDelay(", app_main)
        self.assertNotIn('uart_write_bytes(BRIDGE_UART_NUM,"\\n",1)', app_main)
        self.assertEqual(app_main.count("bridge_uart_run_test_step("), 1)
        self.assertNotIn("bridge_uart_send_arm(", app_main)
        self.assertNotIn("bridge_uart_send_cmd(", app_main)

    def test_esp32_field_parser_requires_exact_field_boundaries(self) -> None:
        esp_source = compact_c(self.source["esp_c"])
        self.assertNotIn("strstr(", esp_source)
        for token in (
            "constchar*field=line;",
            "constchar*value=NULL;",
            "if(strncmp(field,key,key_len)==0)",
            "if(value!=NULL){returnNULL;}",
            "value=field+key_len;",
            "constchar*comma=strchr(field,',');",
            "field=comma+1;",
            "returnvalue;",
        ):
            self.assertIn(token, esp_source)

        self.assertGreaterEqual(esp_source.count("find_field_value(line,key)"), 3)
        self.assertEqual(esp_source.count("if(pos[0]!=','&&pos[0]!='\\0')"), 2)
        self.assertIn("value>(UINT32_MAX-digit)/10U", esp_source)
        self.assertIn("magnitude>(limit-digit)/10U", esp_source)

        rx_bytes = compact_c(
            extract_function(self.source["esp_c"], "bridge_uart_handle_rx_byte")
        )
        for token in (
            "if(s_rx_discard_until_lf)",
            "s_rx_discard_until_lf=false;",
            "s_rx_discard_until_lf=true;",
            "s_rx_line_buf[s_rx_line_len-1U]=='\\r'",
            "s_rx_line_len--;",
            "RXembeddedCRrejected",
            "RXcontrolbyterejected",
            "RXlineoverflow",
            "s_parse_error_count++;",
        ):
            self.assertIn(token, rx_bytes)
        self.assertNotIn("if(byte=='\\r'){return;}", rx_bytes)


if __name__ == "__main__":
    unittest.main()
