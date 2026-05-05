#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash $0" >&2
  exit 1
fi

CONF="/boot/extlinux/extlinux.conf"

if [[ ! -f "${CONF}" ]]; then
  echo "Missing extlinux config: ${CONF}" >&2
  exit 1
fi

cp -a "${CONF}" "${CONF}.restore-jetsonio-$(date +%Y%m%d-%H%M%S)"

if grep -q '^LABEL JetsonIO$' "${CONF}"; then
  sed -i 's/^DEFAULT .*/DEFAULT JetsonIO/' "${CONF}"
  echo "DEFAULT restored to JetsonIO"
else
  echo "LABEL JetsonIO was not found. Please inspect ${CONF}" >&2
  exit 1
fi

grep -nE 'DEFAULT|LABEL JetsonIO$|LABEL JetsonIO-UARTA-PIO|FDT .*uarta-pio|OVERLAYS' "${CONF}"
