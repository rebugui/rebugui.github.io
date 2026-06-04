---
title: "[2026 주요정보통신기반시설] N-13 N-13: 로깅 버퍼 크기 설정"
slug: "2026-주정통/N-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "버퍼메모리의크기를어느정도로설정하고있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-13: 로깅 버퍼 크기 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-13 |
| **점검내용** | 버퍼메모리의크기를어느정도로설정하고있는지점검 |
| **점검대상** | Cisco, Piolink등 |
| **판단기준** | 양호: 저장되는로그데이터보다버퍼용량이큰경우 |
| **판단기준** | 취약: 저장되는로그데이터보다버퍼용량이작은경우 |
| **조치방법** | 로그에대한정보를확인하여장비성능을고려한최대버퍼크기를설정 |

---
## 상세 설명

### 개요

로깅 버퍼 크기 설정 항목은 네트워크 장비의 로그를 저장하는 버퍼 메모리의 크기를 적절하게 설정하는 항목입니다. 버퍼가 너무 작으면 로그가 손실될 수 있고, 너무 크면 장비 성능에 영향을 줄 수 있으므로 적절한 크기로 설정해야 합니다.

### 필요성

**보안 위협**

버퍼 크기가 부적절할 경우 다음과 같은 문제가 발생할 수 있습니다.

1. **로그 손실**: 버퍼 용량을 초과하는 로그가 저장될 경우 오래된 로그부터 덮어쓰기되어 로그 정보를 잃게 됩니다.

2. **침입 흔적 소실**: 침해사고 발생 시 침입 흔적을 알 수 없게 되어 사고 조사가 불가능해집니다.

3. **법적 증거 부족**: 보안 사고 시 법적 대응을 위한 충분한 증거로 사용할 수 없습니다.

4. **성능 저하**: 버퍼 크기를 너무 크게 설정하면 패킷 전달이 안 되는 등 장비 성능에 영향을 줄 수 있습니다.

**버퍼 메모리란?**

일반적으로 주기억장치(RAM)와 중앙처리장치(CPU) 사이의 명령이나 데이터를 일시 유지하는데 사용되는 고속의 기억 장치입니다. 버퍼 메모리는 주기억 장치보다 용량은 적지만 고속의 기억 소자를 사용하여 정보의 흐름을 원활하게 합니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) 버퍼 메모리 설정 확인**

```
Router> enable
Router# show logging
```

출력 예시:
```
Syslog logging: enabled (0 messages dropped, 0 messages rate-limited,
                0 flushes, 0 overruns, xml disabled, filtering disabled)
    Console logging: level debugging, 453 messages logged, xml disabled,
                    filtering disabled
    Monitor logging: level debugging, 0 messages logged, xml disabled,
                    filtering disabled
    Buffer logging: level debugging, 453 messages logged
    Logging Exception size (4096 bytes)
```

`Buffer logging` 부분에서 버퍼 크기와 로그된 메시지 수를 확인합니다.

#### Piolink PLOS 장비

**Step 1) 로그 정보 확인**

```
# configure terminal
(config)# show logging
```

현재 로그 버퍼 설정과 로그 메시지를 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) 버퍼 메모리 설정**

```
Router# config terminal
```

1. **로깅 활성화**:

```
Router(config)# logging on
```

2. **버퍼 크기 설정**:

```
Router(config)# logging buffered 16000
```

- 16000 = 16KB 할당
- 일반적으로 16KB에서 32KB의 크기가 적당합니다

3. **Severity Level 설정**:

```
Router(config)# logging buffered informational
```

Severity Level:
- `debugging` (7): 모든 메시지
- `informational` (6): 정보성 메시지
- `notification` (5): 통지 필요
- `warning` (4): 경고
- `error` (3): 오류
- `critical` (2): 긴급
- `alert` (1): 즉시 조치 필요
- `emergency` (0): 시스템 사용 불가

**권장 설정**:

```
Router(config)# logging on
Router(config)# logging buffered 32768 informational
```

#### Piolink PLOS

**Step 2) 로그 버퍼 설정**

```
# configure terminal
(config)# logging buffer <size>
```

- 설정 범위: 1~1000KB
- 기본 설정: 100KB

**Severity Level 설정**:

```
(config)# logging priority <event> <level>
```

### 주의사항

1. **최대 버퍼 크기**: 최대 버퍼 크기는 65,500 bytes이며, 버퍼 용량을 높게 설정하면 패킷 전달이 안 되는 경우가 발생할 수 있습니다.

2. **적절한 크기**: 일반적으로 16KB에서 32KB의 크기가 적당하며, 최대 용량이 16KB에 못 미치는 장비의 경우 장비 성능을 고려하여 최대 용량에 가깝게 설정하는 것을 권고합니다.

3. **장비 성능 고려**: 버퍼 크기가 장비 성능에 비해 큰 경우 라우터의 성능에 영향을 줄 수 있습니다.

4. **RAM 제한**: 메모리(RAM)에 저장된 로그는 장비 재부팅 시 삭제되므로, 중요한 로그는 N-11(원격 로그 서버 사용)을 통해 별도 보관해야 합니다.

5. **로그 확인 명령**:
   - `show logging`: RAM에 저장된 로그 확인
   - `clear logging`: 로그 삭제

6. **장비별 차이**: 장비 모델과 RAM 용량에 따라 설정 가능한 버퍼 크기가 다르므로 장비 매뉴얼을 확인해야 합니다.

7. **모니터링**: 정기적으로 `show logging` 명령어로 버퍼 사용량을 모니터링하고 로그 손실이 발생하지 않는지 확인해야 합니다.

**권장 설정 값**:
- 최소: 16KB (16000 bytes)
- 권장: 32KB (32768 bytes)
- 최대: 장비 성능을 고려하여 최대 64KB (65536 bytes)
- Severity Level: `informational` 또는 `notification`
