#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  set +u
  source /opt/ros/humble/setup.bash
  set -u
fi

if [[ -f "${HOME}/venvs/bno08x/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${HOME}/venvs/bno08x/bin/activate"
else
  echo "[ERROR] ~/venvs/bno08x is not available."
  echo "[ERROR] run guides/11_Jetson_BNO08x_First_Value_Check_Guide.md first."
  exit 1
fi

echo "[INFO] Starting host BNO08x ROS 2 IMU publisher"
echo "[INFO] Default path: I2C bus=1 address=0x4b topic=/imu/data frame_id=imu_link rate=100Hz"
echo "[INFO] Override by passing custom python args, for example:"
echo "[INFO]   $0 --rate 50 --frame-id imu_link"

cd "${SCRIPT_DIR}/../../../.."
exec python ./Robotics/VSLAM/jetson/scripts/bno08x_ros2_imu_publisher.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --topic /imu/data \
  --mag-topic /imu/mag \
  --frame-id imu_link \
  --rate 100 \
  "$@"
