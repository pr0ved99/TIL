# R03 Task Priority, Stack, Heap

## 목표

Task priority, stack size, heap 사용량을 조정하고 문제 증상을 이해한다.

## 실습 항목

1. priority가 다른 task 2개를 만든다.
2. 높은 priority task가 delay 없이 busy loop를 돌 때 낮은 task가 굶는지 확인한다.
3. 각 task에 적절한 delay/blocking을 넣는다.
4. stack size를 너무 작게 잡았을 때 증상을 확인한다.

## 확인할 함수 후보

```c
uxTaskGetStackHighWaterMark(NULL);
xPortGetFreeHeapSize();
```

## 확인 기준

- 높은 priority task가 CPU를 독점할 수 있음을 이해한다.
- task는 delay 또는 blocking wait로 CPU를 양보해야 함을 확인한다.
- stack 부족 증상을 기록한다.

## 프로젝트 연결

`safety_task`와 `motor_control_task`는 높은 priority지만, 짧게 실행하고 즉시 delay/blocking 상태로 돌아가야 한다.
