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
