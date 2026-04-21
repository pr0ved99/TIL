#!/usr/bin/env bash

set -euo pipefail

BUSES=(0 1 2 4 5 7 9)

echo "== Jetson BNO08x Bus Scan =="
echo "Expected I2C address: 0x4a or 0x4b"
echo

for bus in "${BUSES[@]}"; do
  echo "[i2c bus ${bus}]"
  if i2cdetect -y "${bus}" >/tmp/bno08x_i2c_scan_${bus}.txt 2>/dev/null; then
    cat /tmp/bno08x_i2c_scan_${bus}.txt
  else
    echo "scan failed on bus ${bus}"
  fi
  echo "---"
done

rm -f /tmp/bno08x_i2c_scan_*.txt

echo
echo "[serial candidates]"
ls -1 /dev/ttyACM* /dev/ttyUSB* /dev/ttyTHS* 2>/dev/null || true
