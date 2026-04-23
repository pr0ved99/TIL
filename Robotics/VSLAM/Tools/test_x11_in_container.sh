#!/usr/bin/env bash

set -euo pipefail

docker exec -it ros2-d435i bash -lc \
  "echo DISPLAY=\$DISPLAY && xeyes"
