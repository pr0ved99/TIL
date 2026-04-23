#!/usr/bin/env bash

set -euo pipefail

docker exec -it ros2-d435i bash -lc \
  "set +u && \
   source /opt/ros/humble/setup.bash && \
   set -u && \
   ros2 daemon stop || true && \
   ros2 daemon start && \
   sleep 2 && \
   echo '==== nodes ====' && \
   ros2 node list && \
   echo '==== topics ====' && \
   ros2 topic list"
