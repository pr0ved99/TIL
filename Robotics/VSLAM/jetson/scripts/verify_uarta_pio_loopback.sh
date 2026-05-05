#!/usr/bin/env bash
set -euo pipefail

OUTDIR="/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/logs/2026-05-06_uart_pio"
mkdir -p "${OUTDIR}"

echo "=== boot entry ==="
grep -nE 'DEFAULT|LABEL JetsonIO-UARTA-PIO|FDT .*uarta-pio|OVERLAYS' /boot/extlinux/extlinux.conf || true
echo

echo "=== running serial@3100000 properties ==="
NODE="/proc/device-tree/bus@0/serial@3100000"
echo -n "status: "
tr -d '\0' < "${NODE}/status" 2>/dev/null || true
echo
echo -n "compatible: "
tr -d '\0' < "${NODE}/compatible" 2>/dev/null || true
echo
echo -n "dma-names: "
if [[ -f "${NODE}/dma-names" ]]; then
  tr -d '\0' < "${NODE}/dma-names"
else
  echo "<missing>"
fi
echo -n "dmas: "
if [[ -f "${NODE}/dmas" ]]; then
  wc -c < "${NODE}/dmas"
else
  echo "<missing>"
fi
echo

echo "=== loopback test: connect Jetson pin 8 <-> pin 10 before running ==="
PORT=/dev/ttyTHS1

stty -F "${PORT}" 9600 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo

rm -f /tmp/uart_loopback.txt
timeout 5 cat "${PORT}" > /tmp/uart_loopback.txt &
READER=$!

sleep 1
printf 'hello-gps-test\r\n' > "${PORT}"

wait "${READER}" || true

echo "=== received cat -v ==="
cat -v /tmp/uart_loopback.txt | tee "${OUTDIR}/loopback_after_pio_cat_v.txt"
echo

echo "=== recent UART/SMMU kernel log ==="
sudo dmesg -T | grep -iE 'serial|uart|dma|smmu|fault|tegra' | tail -n 120 | tee "${OUTDIR}/dmesg_after_pio_loopback.txt" || true
