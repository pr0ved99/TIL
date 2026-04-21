#!/usr/bin/env bash

set -euo pipefail

echo "== D435i IMU Kernel Support Check =="
echo "kernel: $(uname -r)"
echo

echo "== 1. Kernel config =="
if [[ -r /proc/config.gz ]]; then
  zgrep -E 'CONFIG_HIDRAW|CONFIG_HID_SENSOR_HUB|CONFIG_IIO|CONFIG_USB_HID' /proc/config.gz || true
else
  echo "/proc/config.gz is not readable"
fi
echo

echo "== 2. Relevant modules on disk =="
find "/lib/modules/$(uname -r)" -type f 2>/dev/null | \
  grep -E 'hid_sensor|industrialio|iio.*hid|accel_3d|gyro_3d|triggered_buffer' || true
echo

echo "== 3. Currently loaded modules =="
lsmod | grep -E 'hid_sensor|industrialio|iio|hid_generic|usbhid' || true
echo

echo "== 4. RealSense HID device =="
lsusb | grep -i 'RealSense\\|Intel' || true
ls -l /dev/hidraw* 2>/dev/null || true
echo

echo "== 5. IIO devices =="
find /sys/bus/iio/devices -maxdepth 2 -type f \( -name name -o -name label \) \
  -print -exec sh -c 'printf "  "; cat "$1"' _ {} \; 2>/dev/null || true
echo

echo "== 6. Quick interpretation =="
if [[ -r /proc/config.gz ]] && zgrep -q '^# CONFIG_HID_SENSOR_HUB is not set' /proc/config.gz; then
  echo "[BLOCKER] CONFIG_HID_SENSOR_HUB is not set in the current Jetson kernel."
  echo "[BLOCKER] In this state, D435i HID IMU support is unlikely to work on Jetson."
fi

if ! find "/lib/modules/$(uname -r)" -type f 2>/dev/null | grep -q 'hid_sensor_hub'; then
  echo "[BLOCKER] hid_sensor_hub-related kernel modules are not present under /lib/modules."
fi

if [[ -d /sys/bus/iio/devices ]] && ! find /sys/bus/iio/devices -maxdepth 1 -type d -name 'iio:device*' | grep -q .; then
  echo "[OBSERVE] /sys/bus/iio/devices is currently empty."
fi

echo
echo "If D435i IMU works on a laptop but not on this Jetson, the current top suspect is Jetson kernel/HID/IIO support."
