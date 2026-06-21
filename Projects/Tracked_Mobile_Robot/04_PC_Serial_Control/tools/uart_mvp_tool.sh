#!/usr/bin/env bash
set -euo pipefail

BAUDRATE=115200
PORT=""
LOG_DIR="logs"
NO_LOG=0
DRY_RUN=0
WAIT_S="1.0"
FRAME="PING"
SEQ=1
VX_MMPS=0
W_MRADPS=0
TIMEOUT_MS=300
RAW=""

RAW_LOG_PATH=""
CSV_LOG_PATH=""

usage() {
    cat <<'EOF'
UART MVP Linux tool

Usage:
  ./tools/uart_mvp_tool.sh list-ports
  ./tools/uart_mvp_tool.sh build FRAME [options]
  ./tools/uart_mvp_tool.sh send --port /dev/ttyACM0 FRAME [options]
  ./tools/uart_mvp_tool.sh monitor --port /dev/ttyACM0 [options]
  ./tools/uart_mvp_tool.sh scripted-test --port /dev/ttyACM0 [--dry-run]
  ./tools/uart_mvp_tool.sh interactive --port /dev/ttyACM0 [options]

Frames:
  PING, ARM, DISARM, CMD, RAW

Common options:
  --port DEV             Serial device, for example /dev/ttyACM0
  --baudrate N           Default 115200
  --log-dir DIR          Default logs
  --no-log               Disable raw/CSV log files
  --dry-run              Print frames without opening serial

Frame options:
  --seq N
  --vx-mmps N
  --w-mradps N
  --timeout-ms N
  --raw TEXT
  --wait-s N             Response monitor window for send mode
EOF
}

die() {
    echo "error: $*" >&2
    exit 1
}

to_upper() {
    printf '%s' "$1" | tr '[:lower:]' '[:upper:]'
}

require_port() {
    [[ -n "$PORT" ]] || die "--port is required"
    [[ -e "$PORT" ]] || die "serial device not found: $PORT"
}

csv_escape() {
    local text="${1-}"
    text="${text//\"/\"\"}"
    printf '"%s"' "$text"
}

timestamp() {
    date --iso-8601=milliseconds
}

trim_line() {
    local line="${1-}"
    line="${line%$'\r'}"
    line="${line%$'\n'}"
    printf '%s' "$line"
}

frame_field() {
    local raw="$1"
    local key="$2"
    local IFS=','
    local token
    read -ra tokens <<< "$raw"
    for token in "${tokens[@]:1}"; do
        if [[ "$token" == "$key="* ]]; then
            printf '%s' "${token#*=}"
            return
        fi
    done
}

frame_category() {
    case "$1" in
        ACK) printf 'accepted' ;;
        ERR) printf 'rejected' ;;
        TEL) printf 'telemetry' ;;
        PONG) printf 'pong' ;;
        STATE) printf 'state' ;;
        FAULT) printf 'fault' ;;
        "") printf 'unparsed' ;;
        *) printf 'other' ;;
    esac
}

init_log() {
    if [[ "$NO_LOG" -eq 1 ]]; then
        return
    fi

    mkdir -p "$LOG_DIR"
    local stamp
    stamp="$(date +%Y%m%d_%H%M%S)"
    RAW_LOG_PATH="$LOG_DIR/uart_mvp_${stamp}_raw.log"
    CSV_LOG_PATH="$LOG_DIR/uart_mvp_${stamp}_parsed.csv"
    printf 'timestamp,direction,frame_type,seq,state,code,category,raw\n' > "$CSV_LOG_PATH"
}

log_line() {
    local direction="$1"
    local line
    line="$(trim_line "${2-}")"
    local ts
    ts="$(timestamp)"

    printf '%s %-2s %s\n' "$ts" "$direction" "$line"

    if [[ "$NO_LOG" -eq 1 ]]; then
        return
    fi

    printf '%s %s %s\n' "$ts" "$direction" "$line" >> "$RAW_LOG_PATH"

    local type seq state code category
    type="$(printf '%s' "$line" | cut -d',' -f1 | tr '[:lower:]' '[:upper:]')"
    [[ "$type" == "$line" && "$line" != *","* ]] && type="$line"
    seq="$(frame_field "$line" "seq")"
    state="$(frame_field "$line" "state")"
    code="$(frame_field "$line" "code")"
    category="$(frame_category "$type")"

    {
        csv_escape "$ts"; printf ','
        csv_escape "$direction"; printf ','
        csv_escape "$type"; printf ','
        csv_escape "$seq"; printf ','
        csv_escape "$state"; printf ','
        csv_escape "$code"; printf ','
        csv_escape "$category"; printf ','
        csv_escape "$line"; printf '\n'
    } >> "$CSV_LOG_PATH"
}

validate_cmd_values() {
    [[ "$VX_MMPS" -ge -100 && "$VX_MMPS" -le 100 ]] || die "vx_mmps out of MVP range: $VX_MMPS"
    [[ "$W_MRADPS" -ge -500 && "$W_MRADPS" -le 500 ]] || die "w_mradps out of MVP range: $W_MRADPS"
    [[ "$TIMEOUT_MS" -ge 50 && "$TIMEOUT_MS" -le 500 ]] || die "timeout_ms out of MVP range: $TIMEOUT_MS"
}

make_frame() {
    local type
    type="$(to_upper "$FRAME")"
    case "$type" in
        PING)
            printf 'PING,seq=%s' "$SEQ"
            ;;
        ARM)
            printf 'ARM,seq=%s' "$SEQ"
            ;;
        DISARM)
            printf 'DISARM,seq=%s' "$SEQ"
            ;;
        CMD)
            validate_cmd_values
            printf 'CMD,seq=%s,vx_mmps=%s,w_mradps=%s,timeout_ms=%s' "$SEQ" "$VX_MMPS" "$W_MRADPS" "$TIMEOUT_MS"
            ;;
        RAW)
            printf '%s' "$RAW"
            ;;
        *)
            die "unsupported frame type: $FRAME"
            ;;
    esac
}

configure_serial() {
    require_port
    stty -F "$PORT" "$BAUDRATE" cs8 -cstopb -parenb -ixon -ixoff -crtscts -echo raw min 0 time 1
}

wait_ms_from_seconds() {
    awk -v s="$1" 'BEGIN { if (s < 0) s = 0; printf "%d", s * 1000 }'
}

read_for() {
    local seconds="$1"
    local wait_ms end_ms now_ms remaining_ms read_timeout
    wait_ms="$(wait_ms_from_seconds "$seconds")"
    end_ms=$(( $(date +%s%3N) + wait_ms ))

    while true; do
        now_ms="$(date +%s%3N)"
        remaining_ms=$(( end_ms - now_ms ))
        (( remaining_ms <= 0 )) && break

        read_timeout="$(awk -v ms="$remaining_ms" 'BEGIN { s=ms/1000; if (s > 0.2) s=0.2; if (s < 0.001) s=0.001; printf "%.3f", s }')"
        local line=""
        if IFS= read -r -t "$read_timeout" line <&3; then
            log_line "RX" "$line"
        fi
    done
}

send_frame_text() {
    local frame_text="$1"
    printf '%s\n' "$frame_text" >&3
    log_line "TX" "$frame_text"
}

list_ports() {
    local found=0
    local dev
    shopt -s nullglob
    for dev in /dev/ttyACM* /dev/ttyUSB*; do
        printf '%s\n' "$dev"
        found=1
    done

    if [[ -d /dev/serial/by-id ]]; then
        for dev in /dev/serial/by-id/*; do
            printf '%s -> %s\n' "$dev" "$(readlink -f "$dev")"
            found=1
        done
    fi
    shopt -u nullglob

    if [[ "$found" -eq 0 ]]; then
        echo "No /dev/ttyACM* or /dev/ttyUSB* serial devices found."
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --port)
                PORT="${2-}"; shift 2 ;;
            --baudrate)
                BAUDRATE="${2-}"; shift 2 ;;
            --log-dir)
                LOG_DIR="${2-}"; shift 2 ;;
            --no-log)
                NO_LOG=1; shift ;;
            --dry-run)
                DRY_RUN=1; shift ;;
            --wait-s)
                WAIT_S="${2-}"; shift 2 ;;
            --seq)
                SEQ="${2-}"; shift 2 ;;
            --vx-mmps)
                VX_MMPS="${2-}"; shift 2 ;;
            --w-mradps)
                W_MRADPS="${2-}"; shift 2 ;;
            --timeout-ms)
                TIMEOUT_MS="${2-}"; shift 2 ;;
            --raw)
                RAW="${2-}"; shift 2 ;;
            -h|--help)
                usage; exit 0 ;;
            PING|ARM|DISARM|CMD|RAW|ping|arm|disarm|cmd|raw)
                FRAME="$(to_upper "$1")"; shift ;;
            *)
                die "unknown argument: $1" ;;
        esac
    done
}

cmd_build() {
    local frame_text
    frame_text="$(make_frame)"
    printf '%s\n' "$frame_text"
}

cmd_send() {
    local frame_text
    frame_text="$(make_frame)"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        printf '%s\n' "$frame_text"
        return
    fi

    configure_serial
    init_log
    exec 3<>"$PORT"
    send_frame_text "$frame_text"
    read_for "$WAIT_S"
    exec 3>&-
}

cmd_monitor() {
    configure_serial
    init_log
    exec 3<>"$PORT"
    echo "Monitoring. Press Ctrl+C to stop."
    while true; do
        read_for 0.2
    done
}

scripted_send_or_print() {
    local frame_text="$1"
    local wait_s="$2"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        printf '%s\n' "$frame_text"
        printf '# wait %ss\n' "$wait_s"
    else
        send_frame_text "$frame_text"
        read_for "$wait_s"
    fi
}

cmd_scripted_test() {
    if [[ "$DRY_RUN" -eq 0 ]]; then
        configure_serial
        init_log
        exec 3<>"$PORT"
    fi

    scripted_send_or_print "PING,seq=1" "0.5"
    scripted_send_or_print "CMD,seq=2,vx_mmps=80,w_mradps=0,timeout_ms=300" "0.5"
    scripted_send_or_print "ARM,seq=3" "0.5"
    scripted_send_or_print "CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300" "0.5"
    scripted_send_or_print "CMD,seq=5,vx_mmps=80,timeout_ms=300" "0.5"
    scripted_send_or_print "CMD,seq=6,vx_mmps=9999,w_mradps=0,timeout_ms=300" "0.5"
    scripted_send_or_print "CMD,seq=7,vx_mmps=0,w_mradps=0,timeout_ms=300" "1.0"
    scripted_send_or_print "DISARM,seq=8" "0.5"

    if [[ "$DRY_RUN" -eq 0 ]]; then
        exec 3>&-
    fi
}

prompt_int() {
    local prompt="$1"
    local default="$2"
    local value
    read -r -p "$prompt [$default]: " value
    if [[ -z "$value" ]]; then
        printf '%s' "$default"
    else
        printf '%s' "$value"
    fi
}

cmd_interactive() {
    configure_serial
    init_log
    exec 3<>"$PORT"

    local next_seq="$SEQ"
    echo "Interactive UART MVP console. Keep motor power disconnected."
    while true; do
        cat <<'EOF'

1) PING
2) ARM
3) DISARM
4) CMD custom
5) CMD zero once
6) zero-CMD keepalive
7) raw frame
8) out-of-range CMD
9) monitor wait
q) quit
EOF
        local choice
        read -r -p "> " choice
        case "$choice" in
            q|Q)
                break
                ;;
            1)
                send_frame_text "PING,seq=$next_seq"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            2)
                send_frame_text "ARM,seq=$next_seq"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            3)
                send_frame_text "DISARM,seq=$next_seq"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            4)
                local vx w timeout
                vx="$(prompt_int "vx_mmps" "0")"
                w="$(prompt_int "w_mradps" "0")"
                timeout="$(prompt_int "timeout_ms" "300")"
                send_frame_text "CMD,seq=$next_seq,vx_mmps=$vx,w_mradps=$w,timeout_ms=$timeout"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            5)
                send_frame_text "CMD,seq=$next_seq,vx_mmps=0,w_mradps=0,timeout_ms=300"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            6)
                local duration_s duration_ms end_ms now_ms
                read -r -p "duration_s [3.0]: " duration_s
                [[ -z "$duration_s" ]] && duration_s="3.0"
                duration_ms="$(wait_ms_from_seconds "$duration_s")"
                end_ms=$(( $(date +%s%3N) + duration_ms ))
                while true; do
                    now_ms="$(date +%s%3N)"
                    (( now_ms >= end_ms )) && break
                    send_frame_text "CMD,seq=$next_seq,vx_mmps=0,w_mradps=0,timeout_ms=300"
                    next_seq=$(( next_seq + 1 ))
                    read_for 0.02
                    sleep 0.05
                done
                ;;
            7)
                local raw_frame
                read -r -p "raw frame without LF: " raw_frame
                send_frame_text "$raw_frame"
                read_for "$WAIT_S"
                ;;
            8)
                send_frame_text "CMD,seq=$next_seq,vx_mmps=9999,w_mradps=0,timeout_ms=300"
                next_seq=$(( next_seq + 1 ))
                read_for "$WAIT_S"
                ;;
            9)
                local wait_s
                read -r -p "wait_s [2.0]: " wait_s
                [[ -z "$wait_s" ]] && wait_s="2.0"
                read_for "$wait_s"
                ;;
            *)
                echo "Unknown menu option."
                ;;
        esac
    done

    exec 3>&-
}

main() {
    local cmd="${1-}"
    [[ -n "$cmd" ]] || { usage; exit 1; }
    shift || true

    case "$cmd" in
        list-ports)
            list_ports "$@"
            ;;
        build)
            parse_args "$@"
            cmd_build
            ;;
        send)
            parse_args "$@"
            cmd_send
            ;;
        monitor)
            parse_args "$@"
            cmd_monitor
            ;;
        scripted-test)
            parse_args "$@"
            cmd_scripted_test
            ;;
        interactive)
            parse_args "$@"
            cmd_interactive
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            usage
            die "unknown command: $cmd"
            ;;
    esac
}

main "$@"
