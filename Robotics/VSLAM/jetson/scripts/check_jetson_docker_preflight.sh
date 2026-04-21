#!/usr/bin/env bash

set -euo pipefail

echo "== Jetson Docker Preflight =="
echo

echo "[System]"
uname -m
cat /etc/nv_tegra_release
echo

echo "[Docker Versions]"
docker --version
docker compose version
echo

echo "[User Groups]"
id -nG
echo

echo "[Socket]"
ls -l /var/run/docker.sock
echo

echo "[Daemon Runtime Config]"
if [[ -f /etc/docker/daemon.json ]]; then
  cat /etc/docker/daemon.json
else
  echo "missing: /etc/docker/daemon.json"
fi
echo

echo "[Access Check]"
if docker info >/tmp/jetson_docker_info.txt 2>/tmp/jetson_docker_info.err; then
  echo "docker daemon access: OK"
  grep -i "Runtimes\\|Default Runtime\\|nvidia" /tmp/jetson_docker_info.txt || true
else
  echo "docker daemon access: FAILED"
  cat /tmp/jetson_docker_info.err
  echo
  echo "hint: add the current user to the docker group, then open a new terminal."
fi

rm -f /tmp/jetson_docker_info.txt /tmp/jetson_docker_info.err
