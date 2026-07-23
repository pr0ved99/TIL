# Chassis Source Drawing

## Status

`SOURCE PRESERVED / UNMODIFIED`

이 폴더는 어댑터 플레이트의 기준으로 사용한 궤도 셰시 원본 홀 패턴 도면을 보존한다. 제조용 Rev A
파일과 구분하며, 원본 파일은 직접 편집하지 않는다.

## File Record

| 항목 | 값 |
| --- | --- |
| 파일 | [`R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg`](R3_High_Config_Version_Tracked_Vehicle_Hole_Pattern_Drawing.dwg) |
| 역할 | 궤도 셰시 홀 패턴 입력 도면 |
| 이전 위치 | `C:\Users\eyh12\Desktop` |
| 저장일 | 2026-07-24 |
| 파일 크기 | 170,279 bytes |
| DWG header | `AC1027` - AutoCAD 2013 형식 |
| SHA-256 | `E127671CF934FACB2B9E578599633E0C576756167181B3ABE6191C16774DCC5F` |

Rev A 어댑터 플레이트는 이 도면을 Onshape로 가져온 뒤 작성했다. 실제 Rev A 제조 정본은
[`../../releases/revA/README.md`](../../releases/revA/README.md)에서 관리한다.

## Rules

- 원본 DWG는 binary로 보존하고 줄바꿈 변환이나 포맷 변환을 적용하지 않는다.
- 새로운 셰시 도면을 받으면 기존 파일을 덮어쓰지 않고 별도 revision과 SHA-256을 기록한다.
- Rev B에서 홀 패턴을 변경할 때는 원본 DWG, Onshape 형상과 실물 셰시를 함께 대조한다.
- 제조 업체에 전달할 파일은 이 원본이 아니라 해당 adapter-plate release 정본을 사용한다.
