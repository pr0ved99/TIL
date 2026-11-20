# 부품 데이터시트와 계측기 설명서

**자주 쓰는 수치와 원문 페이지:** [전류·온도 계측/센서 사양 빠른 참조](QUICK_REFERENCE_ko.md). 매번 원본 전체를 읽기보다 해당 절을 먼저 참조한다.

2026-10-22 사용자 요청으로 바탕화면 `datasheets` 폴더의 PDF8개·PNG3개를 이동했다. 파일명만 정리했고 원본 내용은 변경하지 않았다. [이동 명세·원래 파일명·SHA-256](import_manifest_2026-10-22.json)에11개 파일의 이동 전후 일치를 기록했다. 다운로드 경로가 확인되지 않은 파일의 실제 취득 URL은 추정하지 않는다.

## 자료 목록

| 자료 | 로컬 파일 | 참고 |
| --- | --- | --- |
| Cytron MDD10A | [매뉴얼](Cytron_MDD10A_User_Manual.pdf) | V2.0, June2017,11쪽 |
| XL4015 | [데이터시트](XL4015_Datasheet.pdf) | Rev2.0,10쪽. IC 자료이며 완제품 모듈 전체의 정격 보증과 구분 |
| UNI-T UT210E | [설명서](UNI-T_UT210E_User_Manual.pdf) | MAY2018 REV2,2쪽. 이미지 중심 PDF |
| BENETECH GM1312 | [기준 설명서](BENETECH_GM1312_User_Manual.pdf) | GM1312-EN-01,6면이 PDF1쪽에 배치된 이미지 자료 |
| BENETECH GM1312 | [다른 스캔본](BENETECH_GM1312_User_Manual_Alternate_Scan.pdf) | 같은 판본으로 확인. 사용자 원본 보존용, 기준 파일은 위 자료 |
| SEMITEC103JT | [데이터시트](SEMITEC_103JT_Thermistor_Datasheet.pdf) |103JT-025를 포함한 JT 시리즈,1쪽 |
| Allegro ACS71240 | [데이터시트](Allegro_ACS71240_Datasheet.pdf) | Rev16,34쪽. 구매 carrier의 IC 사양 |
| Pololu#5241 | [제품 페이지](Pololu_5241_Product_Page.pdf) |7쪽.2쪽 기능 목록 우측 일부 잘림을 아래 PNG로 보완 |
| Pololu#5241 | [Overview 전체 캡처](Pololu_5241_Overview_Unclipped.png) | 기능 설명 문장 끝까지 시각 확인 |
| Pololu 전류센서 비교표 | [왼쪽](Pololu_Current_Sensor_Comparison_Left.png) · [오른쪽](Pololu_Current_Sensor_Comparison_Right.png) | 가로 스크롤 표를 나눈 보조 자료. ACS71240 열은 왼쪽에 있음 |

## 2026-11-04 추가 — 보드·ADC 참고 자료

사용자가 프로젝트와 바탕화면 NotebookLM 자료집에 저장한 다음4개 PDF를 확인했다. PDF 열림/전체 페이지 텍스트 읽기와 각 위치의 SHA256 일치를 확인했다. 바탕화면 UM1724의 `(1)` 접미사는 내용 차이를 뜻하지 않는다. [확인 기록](../logs/pcb_design/2026-11-04_notebooklm_source_packet/user_pdf_check.json).

| 문서 | 로컬 파일 | 확인한 판본·분량 | 사용할 범위 |
| --- | --- | --- | --- |
| NUCLEO-64 사용 설명서 | [UM1724](um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf) | Rev17,2025-09,91쪽 | 보드 전원·점퍼·헤더 |
| NUCLEO 보드 회로도 | [MB1136](mb1136-default-c04_schematic.pdf) | C04,2022-08-17,5쪽 | Sheet2/3/5의 전원·MCU·확장 접점; 실제 보드 변형은 별도 대조 |
| GPIO 하드웨어 지침 | [AN4899](an4899-guidelines-for-gpio-hardware-settings-and-lowpower-consumption-on-stm32-mcus-stmicroelectronics.pdf) | Rev4,2026-05,33쪽 | GPIO/아날로그 입력 모드·전원 조건 |
| ADC 정확도 지침 | [AN2834](cd00211314-how-to-optimize-the-adc-accuracy-in-the-stm32-mcus-stmicroelectronics.pdf) | Rev10,2024-10,현 보유 PDF | ADC 오차·외부 회로·취득 조건. 사용자가 갱신한 판본을 사용하며 STM32F446 개별 수치는 DS10693 해당 판본으로 확인 |

기존 [STM32F446 PDF](../stm32f446mc.pdf)는 DS10693 Rev10이다. 별도 웹 판본은 이번 설명 자료의 필수 보충 대상에서 제외했다. 위4개는 이제 로컬 PDF가 있으므로 초기 다운로드 timeout 기록을 현재 미확보 상태로 읽지 않는다. 이번 확인은 자료 확보/동일성 확인이며 새로운 회로·실물 검증이 아니다.

## 공개 참조 위치

아래는 대조에 사용한 공개 참조이며 사용자 파일별 실제 다운로드 출처를 보증하는 기록은 아니다.

- [Cytron 공식 제품·매뉴얼 연결](https://my.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels)
- [XL4015 제조사 PDF](https://www.xlsemi.com/datasheet/XL4015-EN.pdf)
- [UNI-T 공식 UT210E 설명서](https://meters.uni-trend.com/download/ut210e-user-manual/)
- [GM1312 원본 설명서 유통사 보관본](https://www.onetemp.com.au/wp-content/uploads/2024/01/Benetech-GM1312-Thermocouple-Thermometer-Instruction-Manual.pdf)
- [SEMITEC JT 제조사 PDF](https://www.semitec-global.com/uploads/2022/01/P9-JT-Thermistor.pdf)
- [Allegro ACS71240 제조사 PDF](https://www.allegromicro.com/-/media/files/datasheets/acs71240-datasheet.pdf)
- [Pololu#5241 제품 페이지](https://www.pololu.com/product/5241)

## 남은 근거와 사용 범위

MG540P30_12V 모터의 케이스 허용 온도·연속 운전 조건을 명시한 자료는 이번 묶음에 없다. [기존 제조사 회신](../vendor/wheeltec/2026-08-17_mg540p30_12v_support_reply_ko.md)을 보존하며 미확보 온도 사양을 추정하지 않는다. 실제 수령 프로브·고정재의 사양과 전기적 절연도 별도 확인 대상이다.

문서 확보·파일 보존 확인은 온도/전류 실측이나 MVP 검증 완료가 아니다. [외부 온도 관측 계획](../../docs/plans/2026-10-20_External_Temperature_Test_Plan_ko.md)의 수치 중단/판정 기준은 아직 미확정이다.

11/5 마감 점검: AN2834의 이전 Rev2 파일명 링크를 실제 보유 Rev10 파일명으로 정정했다. 과거 복제 영수증은 생성 당시 판본/해시 이력으로 보존한다.
