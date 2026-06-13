# ROS 2 Executor와 Callback Group

## 분야

- ROS 2
- 로봇 미들웨어
- 동시성 제어

## 관련 면접 질문

- ROS에도 mutex나 semaphore와 비슷한 개념이 있는가?
- ROS 2에서 callback은 어떻게 실행되는가?
- multi-threaded executor를 쓰면 어떤 문제가 생길 수 있는가?

## 선수지식

- ROS 2 node
- topic publish/subscribe
- callback 함수
- thread
- mutex

## 핵심 개념

ROS 2에서는 node가 topic, service, action, timer 등을 통해 callback을 실행합니다. 이 callback을 실제로 실행해 주는 주체가 executor입니다.

```text
Node
  Subscription Callback
  Timer Callback
  Service Callback

Executor
  -> 준비된 callback을 실행
```

## Single-threaded Executor

Single-threaded executor는 callback을 한 번에 하나씩 실행합니다.

장점:

- 동시성 문제가 적습니다.
- 구조가 단순합니다.

단점:

- 오래 걸리는 callback이 있으면 다른 callback이 밀립니다.

## Multi-threaded Executor

Multi-threaded executor는 여러 callback을 병렬로 실행할 수 있습니다.

장점:

- 여러 작업을 병렬 처리할 수 있습니다.
- 센서 처리, 제어, 통신이 많은 시스템에서 응답성이 좋아질 수 있습니다.

단점:

- shared data에 동시에 접근하면 race condition이 생길 수 있습니다.
- mutex나 callback group 설계가 필요합니다.

## Callback Group

ROS 2의 callback group은 callback들이 동시에 실행될 수 있는지 제어하는 단위입니다.

대표적으로 두 종류가 있습니다.

- Mutually Exclusive Callback Group: 같은 group 안의 callback은 동시에 실행되지 않음
- Reentrant Callback Group: 같은 group 안의 callback도 동시에 실행될 수 있음

## ROS 2에서 Mutex가 필요한 예

센서 callback이 최신 센서 값을 갱신하고, timer callback이 그 값을 읽어 제어 명령을 만든다고 가정합니다.

```text
Sensor Callback -> latest_scan 갱신
Timer Callback  -> latest_scan 읽고 제어 명령 계산
```

multi-threaded executor에서는 두 callback이 동시에 실행될 수 있습니다. 이때 `latest_scan` 접근을 mutex로 보호하지 않으면 중간 상태를 읽을 수 있습니다.

## RTOS와의 차이

ROS 2는 로봇 미들웨어이지 RTOS가 아닙니다. 따라서 hard real-time을 직접 보장하는 구조는 아닙니다. 하지만 executor, callback, thread, mutex 같은 동시성 문제는 충분히 발생합니다.

면접에서는 "ROS는 RTOS처럼 task priority를 다루는 시스템은 아니지만, node 내부 callback 병렬 실행에서는 mutex나 callback group을 고려해야 한다"고 말하면 좋습니다.

## 면접 답변으로 연결

### 30초 답변

> ROS 2는 RTOS처럼 semaphore나 mutex를 전면에 내세우는 구조는 아니지만, multi-threaded executor에서 여러 callback이 병렬로 실행되면 shared data 문제가 생길 수 있습니다. 예를 들어 센서 callback이 값을 갱신하고 timer callback이 그 값을 읽는다면 mutex로 보호하거나 callback group을 mutually exclusive로 설정해 race condition을 막을 수 있습니다.

## 내 프로젝트로 연결하는 문장

> ROS 2 Navigation 구조를 다룰 때도 topic 흐름만 보는 것이 아니라 callback 실행 방식과 shared state 접근까지 확인해야 안정적인 node를 만들 수 있다고 연결할 수 있습니다.

