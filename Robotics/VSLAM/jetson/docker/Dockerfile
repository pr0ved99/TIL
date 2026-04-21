FROM ros:humble-ros-base-jammy

ARG USER_NAME=jetson
ARG UID=1000
ARG GID=1000

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash-completion \
    build-essential \
    git \
    i2c-tools \
    iputils-ping \
    less \
    libgl1-mesa-glx \
    libglib2.0-0 \
    nano \
    python3-colcon-common-extensions \
    python3-dev \
    python3-pip \
    python3-smbus \
    ros-humble-image-tools \
    ros-humble-realsense2-camera \
    ros-humble-rqt-image-view \
    ros-humble-rtabmap-ros \
    ros-humble-rviz2 \
    usbutils \
    vim \
    x11-apps \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir \
    adafruit-blinka \
    adafruit-circuitpython-bno08x \
    adafruit-extended-bus \
    pyserial \
    smbus2

RUN if getent group "${GID}" >/dev/null 2>&1; then \
      existing_group="$(getent group "${GID}" | cut -d: -f1)"; \
      if [ "${existing_group}" != "${USER_NAME}" ]; then \
        groupmod -n "${USER_NAME}" "${existing_group}"; \
      fi; \
    elif getent group "${USER_NAME}" >/dev/null 2>&1; then \
      groupmod -o -g "${GID}" "${USER_NAME}"; \
    else \
      groupadd --gid "${GID}" "${USER_NAME}"; \
    fi \
 && if id -u "${USER_NAME}" >/dev/null 2>&1; then \
      usermod -o -u "${UID}" -g "${GID}" "${USER_NAME}"; \
    else \
      useradd --uid "${UID}" --gid "${GID}" -m -s /bin/bash "${USER_NAME}"; \
    fi \
 && mkdir -p /workspace \
 && chown -R "${UID}:${GID}" /workspace /home/"${USER_NAME}"

RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USER_NAME}/.bashrc

USER ${USER_NAME}
WORKDIR /workspace/TIL
CMD ["bash"]
