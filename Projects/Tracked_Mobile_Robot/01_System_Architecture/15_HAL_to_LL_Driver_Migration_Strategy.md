# HAL to LL Driver Migration Strategy

## Purpose

This document defines how the STM32 firmware can migrate selected paths from
HAL to LL Driver after the drivetrain is already working.

LL migration is a required engineering-depth goal, but it is not the first
bring-up step. The first firmware should use CubeMX and HAL to reduce wiring,
clock, timer, and peripheral configuration risk. LL is introduced later only
where it improves timing clarity, register-level understanding, or control-loop
determinism.

This document answers:

- Why the project starts with HAL
- Which code paths are good LL migration targets
- Which code paths should stay HAL at first
- How to avoid breaking a working motor controller
- What evidence proves that LL migration was useful

## Architecture Decision

Start with HAL, then migrate timing-critical paths to LL behind stable project
interfaces.

Migration direction:

```text
HAL bare-metal MVP
    -> HAL + FreeRTOS baseline
    -> LL for selected GPIO/PWM/encoder/timer paths
    -> optional LL for ADC and CAN paths
```

Core decision:

```text
HAL is used for bring-up reliability.
LL is used later for timing-critical and safety-relevant paths.
```

The project should not rewrite everything into LL.

## 1. HAL and LL Terms

| Term | Meaning in this project |
| --- | --- |
| HAL | STM32 high-level driver layer generated and used easily with CubeMX |
| LL Driver | Lower-level STM32 driver layer closer to peripheral registers |
| Register | MCU hardware configuration or data field mapped into memory |
| Migration | Replacing a working HAL path with an LL path while keeping behavior equivalent |
| Baseline | Known-good HAL behavior used for comparison |
| Regression | A behavior that worked before but breaks after migration |
| Jitter | Variation in loop period or signal timing |

## 2. Why Start With HAL

HAL is the correct first step for this project.

Reasons:

- CubeMX reduces pin, clock, and alternate-function setup mistakes.
- HAL examples are easier to search, debug, and modify.
- UART, ADC, I2C, CAN, and timer bring-up are faster with HAL.
- Early problems are more likely to be wiring, power, pin, or driver issues
  than HAL overhead.
- A working HAL version gives a clear reference before LL changes.

Rule:

```text
Do not migrate a peripheral to LL before its HAL version has been validated.
```

## 3. Why Migrate Some Paths to LL

LL is useful when the project needs:

- More direct understanding of timer and GPIO behavior
- Lower overhead for repeated high-rate operations
- Clearer control of interrupt timing
- Easier timing inspection
- Stronger embedded portfolio evidence

Good LL migration is not about making every line faster. It is about proving
that the developer understands which parts of the firmware are timing-critical
and can validate the change.

## 4. Entry Criteria

Start LL migration only after:

- One motor can run forward and reverse under HAL control.
- Left and right BTS7960 PWM outputs are validated at low duty.
- Encoder counting works in HAL configuration.
- Command timeout stops motor output.
- Safety gate sets PWM zero and disables driver enable.
- A known-good HAL firmware commit or branch exists.
- Basic telemetry can show loop timing, command age, PWM, and encoder values.

If these are not true, LL migration will make debugging harder instead of more
professional.

## 5. Migration Principles

Use these rules:

1. Keep high-level application logic unchanged.
2. Wrap peripheral access behind project-local functions.
3. Migrate one peripheral path at a time.
4. Keep the HAL version available for comparison.
5. Measure or log behavior before and after migration.
6. Run a regression checklist after every migration.
7. Never migrate safety-critical output without a safe default test.

Project-local wrapper examples:

```c
void motor_pwm_set_left(int16_t duty);
void motor_pwm_set_right(int16_t duty);
int32_t encoder_get_left_count(void);
int32_t encoder_get_right_count(void);
void driver_enable_set(bool enabled);
uint16_t battery_adc_read_raw(void);
```

Application code should call these wrappers, not HAL or LL directly.

## 6. Recommended Migration Targets

| Target | Initial HAL path | LL migration reason | Priority |
| --- | --- | --- | --- |
| BTS7960 enable GPIO | `HAL_GPIO_WritePin()` | Simple first LL migration, safety output clarity | High |
| PWM compare update | `__HAL_TIM_SET_COMPARE()` or HAL PWM helpers | High-rate motor duty update path | High |
| Encoder count read | `__HAL_TIM_GET_COUNTER()` | Frequent control-loop read path | High |
| Control-loop timer interrupt | HAL timer callback | Loop timing and ISR ownership clarity | Medium |
| ADC raw read | HAL ADC polling or interrupt | Battery monitor path after it is stable | Medium |
| CAN RX/TX | HAL CAN callbacks | Optional after CAN baseline works | Low to medium |

## 7. Paths Not Recommended for First LL Migration

Avoid migrating these first:

| Path | Reason |
| --- | --- |
| UART command text parsing | Parsing logic dominates, LL gives little benefit |
| Debug `printf` path | Debug convenience is more important than optimization |
| BNO08x I2C bring-up | Sensor protocol debugging is already complex |
| ESP32 Wi-Fi or dashboard logic | Not STM32 timing-critical |
| Full CAN protocol stack | Validate HAL CAN first, then decide |
| FreeRTOS kernel internals | Not a project migration target |

Rule:

```text
Migrate peripheral access, not the whole application architecture.
```

## 8. Layering Model

Recommended firmware layering:

```text
Application / control logic
        |
        v
Project driver interface
        |
        v
HAL implementation or LL implementation
        |
        v
STM32 peripheral registers
```

Example:

```text
motor_control_task
        |
        v
motor_pwm_set_left()
        |
        +-- HAL implementation in baseline
        |
        +-- LL implementation after migration
```

This keeps the control loop independent from the driver layer.

## 9. Migration Plan

### Step 0: Preserve the HAL Baseline

Before changing code:

- Commit or tag the HAL baseline.
- Record PWM frequency, control-loop rate, encoder behavior, and safety tests.
- Save a small test log.

Exit criteria:

- The HAL version can be rebuilt and reflashed.

### Step 1: Create Driver Wrappers

Move direct HAL calls behind project-local functions.

Examples:

- `motor_pwm_set_*()`
- `encoder_get_*()`
- `driver_enable_set()`
- `battery_adc_read_raw()`

Exit criteria:

- Firmware behavior is unchanged, but HAL calls are localized.

### Step 2: Migrate Driver Enable GPIO

Migrate enable GPIO write first because it is small and easy to test.

Validation:

- Boot leaves enable disabled.
- Disarm disables driver.
- E-stop disables driver.
- Arm enables driver only if safety state allows it.

### Step 3: Migrate PWM Compare Update

Replace the PWM compare update path with LL.

Validation:

- PWM duty zero at boot.
- Forward command activates only one BTS7960 PWM input per motor.
- Reverse command activates the opposite PWM input.
- `RPWM` and `LPWM` are never active together.
- Duty clamp still works.

### Step 4: Migrate Encoder Count Read

Replace encoder counter read and optional reset path with LL.

Validation:

- Counts increase in the expected direction.
- Left and right encoder signs match motor command signs.
- Speed estimate matches the HAL baseline within acceptable tolerance.

### Step 5: Migrate Control-Loop Timer Path

Only after motor and encoder paths are stable, migrate the loop timer or ISR
path if it improves timing control.

Validation:

- Motor loop period remains near target.
- Worst-case loop delay is recorded.
- No blocking work is added inside ISR.

### Step 6: Optional ADC or CAN LL Migration

ADC or CAN LL migration should happen only after the feature works with HAL.

ADC validation:

- Raw ADC counts match measured voltage divider output.
- Pack voltage estimate is stable enough for safety thresholds.

CAN validation:

- Loopback still works.
- USB-CAN still observes telemetry.
- Heartbeat timeout still stops motor output.

## 10. Measurement Plan

Record before and after values.

| Measurement | Purpose |
| --- | --- |
| Motor loop period average | Confirms expected control frequency |
| Motor loop max period | Detects jitter or blocking |
| PWM output frequency | Confirms timer setup did not change unexpectedly |
| PWM duty command vs output | Confirms compare update correctness |
| Encoder count direction | Confirms timer mode and sign |
| Command timeout behavior | Confirms safety behavior did not regress |
| Boot output state | Confirms motors stay disabled on reset |

Useful debug fields:

```text
loop_count
loop_dt_us
loop_dt_max_us
left_pwm_cmd
right_pwm_cmd
left_encoder_count
right_encoder_count
safety_state
fault_code
```

## 11. Regression Checklist

Run this after every LL migration:

- Firmware builds cleanly.
- Board flashes successfully.
- Boot state keeps PWM zero.
- Driver enable remains disabled until arm condition is met.
- Stop command forces PWM zero.
- Command timeout forces PWM zero.
- Low-voltage simulated condition blocks motor output.
- Encoder count direction is unchanged.
- Telemetry still reports safety state and motor data.
- UART or CAN command path still cannot bypass safety gate.

## 12. Risks

| Risk | Mitigation |
| --- | --- |
| LL code bypasses CubeMX assumptions | Keep generated init code, migrate only access functions first |
| Register mistake drives motor unexpectedly | Test with motor power disconnected or tracks lifted |
| HAL and LL both touch same peripheral inconsistently | Centralize ownership in wrapper files |
| Timing improves but behavior regresses | Use regression checklist, not only timing numbers |
| Debugging becomes harder | Keep HAL baseline branch and document every migration |

## 13. Portfolio Evidence

LL migration should produce evidence, not just code.

Evidence targets:

- Before/after architecture note
- HAL baseline commit reference
- LL migration commit reference
- PWM or timing measurement screenshot
- Code diff showing wrapper isolation
- Regression checklist result
- Short explanation of why the selected path was migrated

Strong portfolio claim:

```text
Migrated timing-critical STM32 motor output paths from HAL to LL after a
validated HAL baseline, then confirmed that safety behavior and motor output
timing did not regress.
```

## Final Decision

The project will not start with LL Driver.

The project will first build a working HAL baseline, then migrate selected
paths to LL in this order:

```text
GPIO enable
-> PWM compare update
-> encoder count read
-> control-loop timer path
-> optional ADC/CAN path
```

Every LL migration must preserve the same safety behavior as the HAL baseline.
