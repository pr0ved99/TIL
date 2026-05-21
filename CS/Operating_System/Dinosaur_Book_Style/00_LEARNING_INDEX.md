# Operating System Learning Index

## 결론

이 인덱스는 운영체제를 대단원/소단원 순서로 학습하기 위한 지도다.
파일명은 `대단원-소단원_주제.md` 형식으로 정리한다.

## 01. OS 기초

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 01-01 | [`01_OS_Foundation/01-01_What_Is_Operating_System.md`](./01_OS_Foundation/01-01_What_Is_Operating_System.md) | 운영체제의 역할을 잡는다. |
| 01-02 | [`01_OS_Foundation/01-02_Kernel_User_Mode_System_Call.md`](./01_OS_Foundation/01-02_Kernel_User_Mode_System_Call.md) | 커널 모드, 사용자 모드, 시스템 콜을 이해한다. |
| 01-03 | [`01_OS_Foundation/01-03_Interrupt_Trap_Boot.md`](./01_OS_Foundation/01-03_Interrupt_Trap_Boot.md) | 인터럽트, 트랩, 부팅 흐름을 이해한다. |
| 01-04 | [`01_OS_Foundation/01-04_OS_Structure.md`](./01_OS_Foundation/01-04_OS_Structure.md) | 운영체제 구조 설계 방식을 비교한다. |

## 02. 프로세스와 스레드

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 02-01 | [`02_Process_Thread/02-01_Process_and_PCB.md`](./02_Process_Thread/02-01_Process_and_PCB.md) | 프로세스와 PCB를 이해한다. |
| 02-02 | [`02_Process_Thread/02-02_Context_Switch.md`](./02_Process_Thread/02-02_Context_Switch.md) | context switch 비용과 흐름을 이해한다. |
| 02-03 | [`02_Process_Thread/02-03_IPC.md`](./02_Process_Thread/02-03_IPC.md) | 프로세스 간 통신 방식을 비교한다. |
| 02-04 | [`02_Process_Thread/02-04_Threads_and_Concurrency.md`](./02_Process_Thread/02-04_Threads_and_Concurrency.md) | 스레드와 동시성의 기본을 잡는다. |

## 03. CPU 스케줄링

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 03-01 | [`03_CPU_Scheduling/03-01_Scheduling_Goals_and_Metrics.md`](./03_CPU_Scheduling/03-01_Scheduling_Goals_and_Metrics.md) | 스케줄링 목표와 평가 지표를 이해한다. |
| 03-02 | [`03_CPU_Scheduling/03-02_Scheduling_Algorithms.md`](./03_CPU_Scheduling/03-02_Scheduling_Algorithms.md) | FCFS, SJF, RR, priority 계열을 비교한다. |
| 03-03 | [`03_CPU_Scheduling/03-03_Multicore_and_RealTime.md`](./03_CPU_Scheduling/03-03_Multicore_and_RealTime.md) | 멀티코어와 실시간 스케줄링 관점을 잡는다. |

## 04. 동기화와 데드락

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 04-01 | [`04_Synchronization_Deadlock/04-01_Race_Condition_Critical_Section.md`](./04_Synchronization_Deadlock/04-01_Race_Condition_Critical_Section.md) | race condition과 critical section을 이해한다. |
| 04-02 | [`04_Synchronization_Deadlock/04-02_Mutex_Semaphore_Monitor.md`](./04_Synchronization_Deadlock/04-02_Mutex_Semaphore_Monitor.md) | mutex, semaphore, monitor를 비교한다. |
| 04-03 | [`04_Synchronization_Deadlock/04-03_Classic_Synchronization_Problems.md`](./04_Synchronization_Deadlock/04-03_Classic_Synchronization_Problems.md) | 고전 동기화 문제를 패턴으로 이해한다. |
| 04-04 | [`04_Synchronization_Deadlock/04-04_Deadlock.md`](./04_Synchronization_Deadlock/04-04_Deadlock.md) | 데드락 조건과 처리 전략을 이해한다. |

## 05. 메모리 관리

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 05-01 | [`05_Memory_Management/05-01_Address_Binding_and_Address_Space.md`](./05_Memory_Management/05-01_Address_Binding_and_Address_Space.md) | 주소 공간과 주소 변환을 이해한다. |
| 05-02 | [`05_Memory_Management/05-02_Paging_and_Page_Table.md`](./05_Memory_Management/05-02_Paging_and_Page_Table.md) | paging과 page table을 이해한다. |
| 05-03 | [`05_Memory_Management/05-03_Virtual_Memory.md`](./05_Memory_Management/05-03_Virtual_Memory.md) | 가상 메모리와 demand paging을 이해한다. |
| 05-04 | [`05_Memory_Management/05-04_Page_Replacement.md`](./05_Memory_Management/05-04_Page_Replacement.md) | page replacement 알고리즘을 비교한다. |

## 06. 저장장치와 파일 시스템

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 06-01 | [`06_Storage_File_System/06-01_Storage_Stack.md`](./06_Storage_File_System/06-01_Storage_Stack.md) | 저장장치 계층을 이해한다. |
| 06-02 | [`06_Storage_File_System/06-02_File_Interface.md`](./06_Storage_File_System/06-02_File_Interface.md) | 파일 추상화와 파일 연산을 이해한다. |
| 06-03 | [`06_Storage_File_System/06-03_File_System_Implementation.md`](./06_Storage_File_System/06-03_File_System_Implementation.md) | 디렉터리, inode, block allocation을 이해한다. |
| 06-04 | [`06_Storage_File_System/06-04_Journaling_and_Reliability.md`](./06_Storage_File_System/06-04_Journaling_and_Reliability.md) | journaling과 crash recovery를 이해한다. |

## 07. I/O 시스템

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 07-01 | [`07_IO_System/07-01_IO_Hardware.md`](./07_IO_System/07-01_IO_Hardware.md) | I/O 하드웨어와 장치 모델을 이해한다. |
| 07-02 | [`07_IO_System/07-02_Interrupt_DMA_Driver.md`](./07_IO_System/07-02_Interrupt_DMA_Driver.md) | interrupt, DMA, driver 흐름을 이해한다. |
| 07-03 | [`07_IO_System/07-03_IO_Performance.md`](./07_IO_System/07-03_IO_Performance.md) | I/O 성능 병목을 판단한다. |

## 08. 보호와 보안

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 08-01 | [`08_Protection_Security/08-01_Protection_Model.md`](./08_Protection_Security/08-01_Protection_Model.md) | 보호 모델과 권한을 이해한다. |
| 08-02 | [`08_Protection_Security/08-02_Access_Control.md`](./08_Protection_Security/08-02_Access_Control.md) | 접근 제어 모델을 비교한다. |
| 08-03 | [`08_Protection_Security/08-03_Security_Threats.md`](./08_Protection_Security/08-03_Security_Threats.md) | OS 보안 위협과 방어 관점을 이해한다. |

## 09. 가상화와 분산

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 09-01 | [`09_Virtualization_Distributed/09-01_Virtual_Machines.md`](./09_Virtualization_Distributed/09-01_Virtual_Machines.md) | 가상 머신의 원리를 이해한다. |
| 09-02 | [`09_Virtualization_Distributed/09-02_Containers.md`](./09_Virtualization_Distributed/09-02_Containers.md) | 컨테이너가 OS 자원을 격리하는 방식을 이해한다. |
| 09-03 | [`09_Virtualization_Distributed/09-03_Distributed_OS_Basics.md`](./09_Virtualization_Distributed/09-03_Distributed_OS_Basics.md) | 분산 시스템에서 OS 개념이 확장되는 지점을 본다. |

## 10. 실습과 점검

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 10-01 | [`10_Practice_Labs/10-01_Linux_Process_Lab.md`](./10_Practice_Labs/10-01_Linux_Process_Lab.md) | Linux에서 process를 관찰한다. |
| 10-02 | [`10_Practice_Labs/10-02_Linux_Memory_Lab.md`](./10_Practice_Labs/10-02_Linux_Memory_Lab.md) | Linux에서 memory 상태를 관찰한다. |
| 10-03 | [`10_Practice_Labs/10-03_Linux_File_IO_Lab.md`](./10_Practice_Labs/10-03_Linux_File_IO_Lab.md) | Linux file I/O를 관찰한다. |
| 10-04 | [`10_Practice_Labs/10-04_Final_Checklist.md`](./10_Practice_Labs/10-04_Final_Checklist.md) | 운영체제 핵심 질문으로 전체를 점검한다. |

