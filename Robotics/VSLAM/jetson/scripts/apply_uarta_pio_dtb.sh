#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash $0" >&2
  exit 1
fi

SRC_DTB="/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/logs/2026-05-06_uart_pio/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb"
DST_DTB="/boot/dtb/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb"
CONF="/boot/extlinux/extlinux.conf"
STAMP="$(date +%Y%m%d-%H%M%S)"
CONF_BAK="/boot/extlinux/extlinux.conf.pre-uarta-pio-${STAMP}"

if [[ ! -f "${SRC_DTB}" ]]; then
  echo "Missing source DTB: ${SRC_DTB}" >&2
  exit 1
fi

if [[ ! -f "${CONF}" ]]; then
  echo "Missing extlinux config: ${CONF}" >&2
  exit 1
fi

cp -a "${CONF}" "${CONF_BAK}"
install -m 0644 "${SRC_DTB}" "${DST_DTB}"

if ! grep -q '^LABEL JetsonIO-UARTA-PIO$' "${CONF}"; then
  tmp_conf="$(mktemp)"
  cp "${CONF}" "${tmp_conf}"
  {
    printf '\n'
    printf 'LABEL JetsonIO-UARTA-PIO\n'
    printf '\tMENU LABEL Custom Header Config + UARTA PIO test\n'
    printf '\tLINUX /boot/Image\n'
    printf '\tFDT /boot/dtb/kernel_tegra234-p3768-0000+p3767-0005-nv-super-uarta-pio.dtb\n'
    printf '\tINITRD /boot/initrd\n'
    printf '\tAPPEND ${cbootargs} root=PARTUUID=8c1a99ff-1f41-4ccb-9f9c-273e58bec4ab rw rootwait rootfstype=ext4 mminit_loglevel=4 console=ttyTCU0,115200 firmware_class.path=/etc/firmware fbcon=map:0 video=efifb:off console=tty0 efi=runtime pci=pcie_bus_perf nvme.use_threaded_interrupts=1 nv-auto-config\n'
    printf '\tOVERLAYS /boot/jetson-io-hdr40-user-custom.dtbo\n'
  } >> "${tmp_conf}"
  install -m 0644 "${tmp_conf}" "${CONF}"
  rm -f "${tmp_conf}"
fi

sed -i 's/^DEFAULT .*/DEFAULT JetsonIO-UARTA-PIO/' "${CONF}"

echo "Installed: ${DST_DTB}"
echo "Backed up: ${CONF_BAK}"
echo
echo "Current extlinux UARTA PIO entry:"
grep -nE 'DEFAULT|LABEL JetsonIO-UARTA-PIO|MENU LABEL Custom Header Config \\+ UARTA PIO|FDT .*uarta-pio|OVERLAYS' "${CONF}"
echo
echo "Next:"
echo "  sudo reboot"
echo
echo "Fallback:"
echo "  At boot menu, select the previous JetsonIO entry if the PIO entry misbehaves."
