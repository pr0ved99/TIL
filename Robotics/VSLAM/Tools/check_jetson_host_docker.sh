#!/usr/bin/env bash

set -u

section() {
  printf "\n==== %s ====\n" "$1"
}

ok() {
  printf "[OK] %s\n" "$1"
}

warn() {
  printf "[WARN] %s\n" "$1"
}

show_cmd() {
  printf "\n$ %s\n" "$1"
}

run_optional() {
  local cmd="$1"
  show_cmd "$cmd"
  bash -lc "$cmd" 2>&1 || warn "명령 실행 실패: $cmd"
}

section "Jetson Host Docker Check"
printf "이 스크립트는 Jetson 호스트 상태를 점검합니다.\n"
printf "확인 대상: JetPack / Ubuntu / Docker / NVIDIA runtime / D435i 인식\n"

section "1. Architecture"
show_cmd "uname -m"
arch="$(uname -m 2>/dev/null || true)"
printf "%s\n" "$arch"
if [[ "$arch" == "aarch64" ]]; then
  ok "Jetson 계열에서 기대하는 aarch64 아키텍처입니다."
else
  warn "aarch64가 아닙니다. Jetson이 아닐 수 있습니다."
fi

section "2. JetPack / Ubuntu"
run_optional "cat /etc/nv_tegra_release"
run_optional "cat /etc/os-release | sed -n '1,8p'"

section "3. Docker"
if command -v docker >/dev/null 2>&1; then
  ok "docker 명령이 있습니다."
  run_optional "docker --version"
else
  warn "docker 명령이 없습니다."
fi

if command -v docker >/dev/null 2>&1; then
  run_optional "docker compose version"
  run_optional "systemctl is-active docker"
  run_optional "groups"
  run_optional "docker info --format '{{json .Runtimes}}'"
else
  warn "Docker 관련 추가 점검을 건너뜁니다."
fi

section "4. NVIDIA Container Toolkit"
run_optional "dpkg -l | grep -E 'nvidia-container|nvidia-ctk|nvidia-docker' || true"

section "5. D435i Device Visibility"
run_optional "lsusb"
run_optional "ls /dev/video*"

if command -v rs-enumerate-devices >/dev/null 2>&1; then
  run_optional "rs-enumerate-devices"
else
  warn "rs-enumerate-devices 명령이 없습니다. librealsense 도구가 아직 없을 수 있습니다."
fi

section "6. Quick Judgment"
printf -- "- aarch64 + R36.x + Ubuntu 22.04 + Docker 정상 + D435i 인식이면 다음 단계로 가도 됩니다.\n"
printf -- "- 여기서 막히면 ROS 2나 RTAB-Map으로 가지 말고 호스트 상태를 먼저 정리해야 합니다.\n"
