# 주문서 - 스택 3개

이 파일은 `rack.py`가 배치에서 직접 세어서 만든다. 손으로 고치지 말 것.

## 1. 레이저 커팅 (아크릴)

- 재질: **투명 캐스트 아크릴 3 mm**, 양면 보호필름 붙은 채로
- 판: **250 × 180 mm**, 모서리 R6. 도면은 DXF(mm, R12), 레이어 `CUT`만 있다
- 구멍 공차: 지름 +0.1 / -0 (M3 → Ø3.4, M2.5 → Ø2.9)
- 보낼 파일: `order-dxf.zip` 하나

| 도면 | 수량 | 구멍 |
|---|---:|---:|
| `dxf/A-base.dxf` | 3 | 12 |
| `dxf/B-ecu.dxf` | 3 | 25 |
| `dxf/C-can.dxf` | 6 | 12 |
| `dxf/D-top.dxf` | 3 | 4 |
| **합계** | **15** | |

## 2. 하드웨어

| 구분 | 품목 | 규격 | 수량 | 메모 |
|---|---|---|---:|---|
| column | hex standoff M/F | M3 x 50, male 6 mm | 24 | male end up; the stud crosses the plate above into the next standoff |
| column | hex standoff M/F | M3 x 60, male 6 mm | 24 | male end up; the stud crosses the plate above into the next standoff |
| column | screw, pan head | M3 x 8 | 12 | up through plate A into the first column standoff |
| column | nut | M3 | 12 | on the four studs above the top plate |
| column | rubber foot | self-adhesive, ~10 mm | 12 | under plate A |
| boards | hex standoff F/F | M3 x 10 | 24 | LAN9692 (board drill Ø3.048 - try an M3 by hand, use M2.5 if it binds) |
| boards | screw, pan head | M3 x 6 | 84 | down through the board |
| boards | screw, pan head | M3 x 8 | 84 | up through the plate |
| boards | washer, nylon | M3 | 84 | under every screw head that lands on acrylic |
| boards | hex standoff F/F | M3 x 8 | 24 | TC397, ESP32-S31 |
| boards | hex standoff F/F | M2.5 x 20 | 12 | FIM-RJ45v2 |
| boards | screw, pan head | M2.5 x 6 | 24 | down through the board |
| boards | screw, pan head | M2.5 x 8 | 24 | up through the plate |
| boards | washer, nylon | M2.5 | 24 | under every screw head that lands on acrylic |
| boards | hex standoff F/F | M2.5 x 10 | 12 | T1-Gender |
| boards | hex standoff F/F | M3 x 35 | 36 | KA7-UNO |
| fan | fan | 40 x 40 x 10 mm, 12 V | 3 | Noctua NF-A4x10 FLX; 32 mm hole pitch |
| fan | screw, pan head | M3 x 20 | 12 | down through the fan and plate B |
| fan | nut, nyloc | M3 | 12 | the fan is the one part that vibrates |
| power | DC adapter | 12 V 5 A, 5.5 x 2.5 mm, centre + | 3 | Mean Well GST60A12-P1M (P1M = 2.5 mm; P1J is 2.1 and contacts badly) |
| power | DC splitter | 1 female -> 2 male, 5.5 x 2.5 mm | 3 | NOT 5.5 x 2.1 |
| power | barrel socket to leads | female 5.5 x 2.5, 18 AWG | 3 | Tensility 10-02879 - the fan joins here. Meter which lead is the centre pin |

여분: 나사·너트·와셔는 10 % 더 사는 게 좋다. M3 x 60 스탠드오프가 없으면 30 + 30으로 이어도 된다.

## 3. 이미 있는 것 (주문 안 함)

- CAN 보드 방열판 20 mm (이미 붙어 있음)
- 보드 자체: LAN9692 EVB, TC397, ESP32-S31, CAN 보드, 인젝션 모듈 v2, T1 커넥터 젠더
