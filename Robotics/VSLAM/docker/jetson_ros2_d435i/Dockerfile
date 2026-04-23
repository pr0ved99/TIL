FROM arm64v8/ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    usbutils \
    v4l-utils \
    x11-apps \
    mesa-utils \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-description \
    ros-humble-rtabmap \
    ros-humble-rtabmap-ros \
    ros-humble-rtabmap-launch \
    ros-humble-rtabmap-viz \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-lc"]

CMD ["bash"]
