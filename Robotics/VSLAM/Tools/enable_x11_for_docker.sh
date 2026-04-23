#!/usr/bin/env bash

set -euo pipefail

display_value="${DISPLAY:-:0}"

export DISPLAY="${display_value}"

xhost +si:localuser:root

echo "[OK] Docker root container is allowed to use X11 on DISPLAY=${DISPLAY}"
echo "Next:"
echo "  bash Tools/run_ros2_d435i_container.sh"
